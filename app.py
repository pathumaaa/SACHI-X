from flask import Flask, request, render_template, jsonify
import sqlite3
import json
import psutil
import requests
from datetime import datetime
import os  # For checking file paths

app = Flask(__name__)

db_path = "/etc/x-ui/x-ui.db"  # Adjust path if necessary

# SSL certificate base directory
ssl_cert_base_dir = "/root/cert/"

def convert_bytes(byte_size):
    """Convert bytes to a human-readable format (MB, GB, TB)."""
    if byte_size is None:
        return "0 Bytes"
    if byte_size < 1024:
        return f"{byte_size} Bytes"
    elif byte_size < 1024 * 1024:
        return f"{round(byte_size / 1024, 2)} KB"
    elif byte_size < 1024 * 1024 * 1024:
        return f"{round(byte_size / (1024 * 1024), 2)} MB"
    elif byte_size < 1024 * 1024 * 1024 * 1024:
        return f"{round(byte_size / (1024 * 1024 * 1024), 2)} GB"
    else:
        return f"{round(byte_size / (1024 * 1024 * 1024 * 1024), 2)} TB"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/usage', methods=['POST'])
def usage():
    user_input = request.form.get('user_input')  # Get input from the form

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to fetch client data
    query = '''SELECT email, up, down, total, expiry_time, inbound_id FROM client_traffics WHERE email = ? OR id = ?'''
    cursor.execute(query, (user_input, user_input))

    row = cursor.fetchone()

    if row:
        email, up, down, total, expiry_time, inbound_id = row

        # **Fixed expiry time handling**
        expiry_date = "Invalid Date"
        if expiry_time and isinstance(expiry_time, (int, float)):
            expiry_timestamp = expiry_time / 1000 if expiry_time > 9999999999 else expiry_time
            try:
                expiry_date = datetime.utcfromtimestamp(expiry_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, OSError):
                expiry_date = "Invalid Date"

        # Query to fetch totalGB and user-specific enable status
        inbound_query = '''SELECT settings FROM inbounds WHERE id = ?'''
        cursor.execute(inbound_query, (inbound_id,))
        inbound_row = cursor.fetchone()

        totalGB = "Not Available"
        user_status = "Disabled"  # Default to "Disabled" if user is not found

        if inbound_row:
            settings = inbound_row[0]
            try:
                inbound_data = json.loads(settings)
                for client in inbound_data.get('clients', []):
                    if client.get('email') == email:
                        totalGB = client.get('totalGB', "Not Available")
                        user_status = "Enabled" if client.get('enable', True) else "Disabled"  # ✅ RESTORED USER-SPECIFIC STATUS CHECK
                        break
            except json.JSONDecodeError:
                totalGB = "Invalid JSON Data"

        conn.close()

        # Convert to human-readable format
        up = convert_bytes(up)
        down = convert_bytes(down)
        total = convert_bytes(total)
        totalGB = convert_bytes(totalGB) if totalGB != "Not Available" else totalGB

        # Debugging: Print values being passed to the template
        print(f"Email: {email}")
        print(f"Uploaded: {up}")
        print(f"Downloaded: {down}")
        print(f"Total: {total}")
        print(f"Expiry Date: {expiry_date}")
        print(f"User Status: {user_status}")

        return render_template(
            'result.html',
            email=email,
            up=up,
            down=down,
            total=total,
            expiry_date=expiry_date,
            totalGB=totalGB,
            user_status=user_status  # Pass correct user status as a string
        )
    else:
        conn.close()
        return "No data found for this user."

@app.route('/update-status', methods=['POST'])
def update_status():
    data = request.get_json()
    new_status = data.get('status')  # True or False
    # Update the status in the database (implement this logic)
    print(f"Updating status to: {new_status}")
    return jsonify({"status": "success", "message": "Status updated"})

@app.route('/server-status')
def server_status():
    """Returns real-time CPU, RAM, and Disk usage."""
    try:
        status = {
            "cpu": psutil.cpu_percent(interval=1),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/server-location')
def server_location():
    """Fetches server location based on public IP."""
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        return jsonify({
            "country": data.get("country", "Unknown"),
            "city": data.get("city", "Unknown"),
            "ip": data.get("query", "Unknown")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ping')
def ping():
    """Endpoint for ping test."""
    return jsonify({"status": "success", "message": "Pong!"})

def find_ssl_certificates(domain):
    """Find SSL certificate and key files for a specific domain."""
    cert_path = os.path.join(ssl_cert_base_dir, domain, "fullchain.pem")
    key_path = os.path.join(ssl_cert_base_dir, domain, "privkey.pem")
    
    if os.path.exists(cert_path) and os.path.exists(key_path):
        return cert_path, key_path
    return None, None

if __name__ == '__main__':
    # Read domain and port from configuration file
    config_file = "/etc/x-ui/config.cfg"
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            for line in f:
                if line.startswith("DOMAIN="):
                    target_domain = line.strip().split("=")[1]
                elif line.startswith("PORT="):
                    port = int(line.strip().split("=")[1])
    else:
        target_domain = None
        port = 5000  # Default port

    # Use the domain to find SSL certificates
    if target_domain:
        ssl_cert_path, ssl_key_path = find_ssl_certificates(target_domain)
        if ssl_cert_path and ssl_key_path:
            print(f"SSL certificate found for {target_domain}. Starting Flask with HTTPS on port {port}...")
            app.run(host='0.0.0.0', port=port, debug=True, ssl_context=(ssl_cert_path, ssl_key_path))
        else:
            print(f"No SSL certificate found for {target_domain}. Starting Flask with HTTP on port {port}...")
            app.run(host='0.0.0.0', port=port, debug=True)
    else:
        print(f"No domain configured. Starting Flask with HTTP on port {port}...")
        app.run(host='0.0.0.0', port=port, debug=True)

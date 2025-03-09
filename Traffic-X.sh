#!/bin/bash

# Ask user for necessary information
echo "Enter your OS username (e.g., ubuntu):"
read USERNAME
echo "Enter your server IP or domain (e.g., 158.170.000.000 or your_domain.com):"
read SERVER_IP
echo "Enter the port (default: 5000):"
read PORT
PORT=${PORT:-5000}

# Install required dependencies
echo "Updating packages..."
sudo apt update

# Install Python3, pip, git, socat, and other required dependencies
echo "Installing required dependencies..."
sudo apt install -y python3-pip python3-venv git sqlite3 socat

# Clone your GitHub repository
echo "Cloning your repository from GitHub..."
cd /home/$USERNAME
if git clone https://github.com/MasterHide/Traffic-X.git; then
    echo "Repository cloned successfully."
else
    echo "Failed to clone repository. Exiting."
    exit 1
fi

# Go to the repo directory
cd Traffic-X

# Verify the templates directory exists
if [ -d "/home/$USERNAME/Traffic-X/templates" ]; then
    echo "Templates directory found."
else
    echo "Templates directory not found. Exiting."
    exit 1
fi

# Set up a virtual environment
echo "Setting up the Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Flask and any other required Python libraries
echo "Installing Flask and dependencies..."
pip install flask psutil requests

# Configure the Flask app to run on the specified port
echo "Configuring Flask app..."
cat > app.py <<EOL
from flask import Flask, request, render_template, jsonify
import sqlite3
import json
import psutil
import requests
from datetime import datetime

app = Flask(__name__)

db_path = "/etc/x-ui/x-ui.db"  # Adjust path if necessary

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=$PORT, debug=True)
EOL

# Set permissions for the database file
echo "Setting permissions for the database file..."
sudo chmod 644 /etc/x-ui/x-ui.db
sudo chown $USERNAME:$USERNAME /etc/x-ui/x-ui.db

# Install acme.sh
echo "Installing acme.sh..."
curl https://get.acme.sh | sh -s email=$USERNAME@$SERVER_IP
export DOMAIN=$SERVER_IP
mkdir -p /var/lib/marzban/certs

# Check if valid certificate already exists
if [ -f "/var/lib/marzban/certs/$DOMAIN.cer" ] && [ -f "/var/lib/marzban/certs/$DOMAIN.cer.key" ]; then
    echo "Valid SSL certificate already exists. Skipping certificate generation."
else
    echo "Generating SSL certificate..."
    ~/.acme.sh/acme.sh --issue --force --standalone -d "$DOMAIN" \
        --fullchain-file "/var/lib/marzban/certs/$DOMAIN.cer" \
        --key-file "/var/lib/marzban/certs/$DOMAIN.cer.key"
fi

# Check certificate expiration date
if [ -f "/var/lib/marzban/certs/$DOMAIN.cer" ]; then
    EXPIRY_DATE=$(openssl x509 -enddate -noout -in "/var/lib/marzban/certs/$DOMAIN.cer" | cut -d= -f2)
    EXPIRY_TIMESTAMP=$(date -d "$EXPIRY_DATE" +%s)
    CURRENT_TIMESTAMP=$(date +%s)
    DAYS_LEFT=$(( (EXPIRY_TIMESTAMP - CURRENT_TIMESTAMP) / 86400 ))

    if [ "$DAYS_LEFT" -lt 30 ]; then
        echo "Certificate is close to expiration (expires in $DAYS_LEFT days). Renewing certificate..."
        ~/.acme.sh/acme.sh --renew -d "$DOMAIN" --force
    else
        echo "Certificate is valid for $DAYS_LEFT days. Skipping renewal."
    fi
fi

# Stop any existing instance of the Flask app
if sudo systemctl is-active --quiet traffic-x; then
    echo "Stopping existing Traffic-X service..."
    sudo systemctl stop traffic-x
fi

# Configure Flask to use HTTPS
echo "Configuring Flask to use HTTPS..."
sed -i "s/app.run(host='0.0.0.0', port=$PORT, debug=True)/app.run(host='0.0.0.0', port=$PORT, ssl_context=('\/var\/lib\/marzban\/certs\/$DOMAIN.cer', '\/var\/lib\/marzban\/certs\/$DOMAIN.cer.key'), debug=True)/" app.py

# Create a systemd service to keep the Flask app running
echo "Setting up systemd service..."
cat > /etc/systemd/system/traffic-x.service <<EOL
[Unit]
Description=Traffic-X Web App
After=network.target

[Service]
User=$USERNAME
WorkingDirectory=/home/$USERNAME/Traffic-X
ExecStart=/home/$USERNAME/Traffic-X/venv/bin/python3 /home/$USERNAME/Traffic-X/app.py
Environment="DB_PATH=/etc/x-ui/x-ui.db"
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=traffic-x

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and enable the service
echo "Enabling the service to start on boot..."
sudo systemctl daemon-reload
sudo systemctl enable traffic-x
sudo systemctl start traffic-x

# Display success message
echo "Installation complete! Your server is running at https://$SERVER_IP:$PORT"
echo "The app will automatically restart if the server reboots."

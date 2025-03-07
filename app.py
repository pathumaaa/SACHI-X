from flask import Flask, request, render_template
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)

db_path = "/etc/x-ui/x-ui.db"  # Change this if your database is located elsewhere

def convert_bytes(size):
    """Convert bytes to human-readable format (MB, GB, TB)"""
    if size >= 1_099_511_627_776:  # 1 TB
        return f"{size / 1_099_511_627_776:.2f} TB"
    elif size >= 1_073_741_824:  # 1 GB
        return f"{size / 1_073_741_824:.2f} GB"
    elif size >= 1_048_576:  # 1 MB
        return f"{size / 1_048_576:.2f} MB"
    else:
        return f"{size} Bytes"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/usage', methods=['POST'])
def usage():
    user_input = request.form.get('user_input')  # Get input from the form

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to fetch client data from client_traffics
    query = '''SELECT email, up, down, total, expiry_time, inbound_id FROM client_traffics WHERE email = ? OR id = ?'''
    cursor.execute(query, (user_input, user_input))

    row = cursor.fetchone()

    if row:
        email = row[0]
        up = convert_bytes(row[1])  # Convert uploaded data
        down = convert_bytes(row[2])  # Convert downloaded data
        total = convert_bytes(row[3])  # Convert total usage
        expiry_time = row[4]
        inbound_id = row[5]  # Get the inbound_id to query the inbounds table

        # Convert expiry time to readable format
        try:
            expiry_time = int(expiry_time) / 1000 if expiry_time > 9999999999 else int(expiry_time)
            expiry_date = datetime.utcfromtimestamp(expiry_time).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            expiry_date = "Invalid Date"

        # Query to fetch total allocated data and config status from inbounds table
        inbound_query = '''SELECT settings, enable, total FROM inbounds WHERE id = ?'''
        cursor.execute(inbound_query, (inbound_id,))
        inbound_row = cursor.fetchone()

        total_allocated = "Not Available"
        config_status = "Unknown"

        if inbound_row:
            settings = inbound_row[0]
            enable_status = inbound_row[1]
            total_allocated_value = inbound_row[2]

            # Convert enable status (1 = Enabled, 0 = Disabled)
            config_status = "Enabled" if enable_status == 1 else "Disabled"

            # Convert total allocated value
            total_allocated = convert_bytes(total_allocated_value)

        conn.close()

        return render_template('result.html', email=email, up=up, down=down, total=total, expiry_date=expiry_date, total_allocated=total_allocated, config_status=config_status)
    else:
        conn.close()
        return "No data found for this user."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

#!/bin/bash

# Ask user for necessary information
echo "Enter your Os username (e.g., ubuntu):"
read USERNAME
echo "Enter your server IP or domain (e.g., 158.170.000.000 or your_domain.com):"
read SERVER_IP
echo "Enter the port type 5000 (default: 5000):"
read PORT
PORT=${PORT:-5000}

# Install required dependencies
echo "Updating packages..."
sudo apt update

# Install Python3, pip, git, and other required dependencies
echo "Installing required dependencies..."
sudo apt install -y python3-pip python3-venv git sqlite3

# Clone your GitHub repository
echo "Cloning your repository from GitHub..."
cd /home/$USERNAME
git clone https://github.com/MasterHide/Traffic-X.git

# Go to the repo directory
cd Traffic-X

# Set up a virtual environment
echo "Setting up the Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Flask and any other required Python libraries
echo "Installing Flask and dependencies..."
pip install flask

# Configure the Flask app to run on the specified port
echo "Configuring Flask app..."
cat > app.py <<EOL
from flask import Flask, request, render_template
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)

db_path = "/etc/x-ui/x-ui.db"  # Change this if your database is located elsewhere

def convert_bytes(byte_size):
    """Convert bytes to a human-readable format (MB, GB, TB)."""
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

    # Query to fetch client data from client_traffics
    query = '''SELECT email, up, down, total, expiry_time, inbound_id FROM client_traffics WHERE email = ? OR id = ?'''
    cursor.execute(query, (user_input, user_input))

    row = cursor.fetchone()

    if row:
        email = row[0]
        up = row[1]
        down = row[2]
        total = row[3]
        expiry_time = row[4]
        inbound_id = row[5]  # Get the inbound_id to query the inbounds table for totalGB and status

        # Check if expiry_time is a valid timestamp
        try:
            expiry_time = int(expiry_time) / 1000 if expiry_time > 9999999999 else int(expiry_time)
            expiry_date = datetime.utcfromtimestamp(expiry_time).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            expiry_date = "Invalid Date"

        # Query to fetch totalGB and user status from inbounds table based on inbound_id
        inbound_query = '''SELECT settings, enable FROM inbounds WHERE id = ?'''
        cursor.execute(inbound_query, (inbound_id,))
        inbound_row = cursor.fetchone()

        totalGB = "Not Available"
        user_status = "User Not Found in Inbound"

        if inbound_row:
            settings = inbound_row[0]
            try:
                inbound_data = json.loads(settings)
                for client in inbound_data.get('clients', []):
                    if client.get('email') == email:
                        totalGB = client.get('totalGB', "Not Available")
                        user_status = "Enabled" if client.get('enable', True) else "Disabled"
                        break
            except json.JSONDecodeError:
                totalGB = "Invalid JSON Data"

        conn.close()

        # Convert data to human-readable format
        up = convert_bytes(up)
        down = convert_bytes(down)
        total = convert_bytes(total)
        totalGB = convert_bytes(totalGB) if totalGB != "Not Available" else totalGB

        # Return results to the result page
        return render_template(
            'result.html',
            email=email,
            up=up,
            down=down,
            total=total,
            expiry_date=expiry_date,
            totalGB=totalGB,
            user_status=user_status  # Pass user-specific status to HTML
        )
    else:
        conn.close()
        return "No data found for this user."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
EOL

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
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and enable the service
echo "Enabling the service to start on boot..."
sudo systemctl daemon-reload
sudo systemctl enable traffic-x
sudo systemctl start traffic-x

# Display success message
echo "Installation complete! Your server is running at http://$SERVER_IP:$PORT"
echo "The app will automatically restart if the server reboots."

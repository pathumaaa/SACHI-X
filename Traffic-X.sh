#!/bin/bash

# Ask user for necessary information
echo "Enter your OS username (e.g., ubuntu):"
read USERNAME
echo "Enter your SSL ENABLED domain (e.g. domain.com):"
read SERVER_DOMAIN
echo "Enter the port (default: 5000):"
read PORT
PORT=${PORT:-5000}  # Default to 5000 if no input is provided

# Save the domain and port to a configuration file
echo "Saving domain and port to configuration file..."
echo "DOMAIN=$SERVER_DOMAIN" > /etc/x-ui/config.cfg
echo "PORT=$PORT" >> /etc/x-ui/config.cfg

# Install required dependencies
echo "Updating packages..."
sudo apt update

# Install Python3, pip, git, and other required dependencies
echo "Installing required dependencies..."
sudo apt install -y python3-pip python3-venv git sqlite3

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

# Set permissions for the database file
echo "Setting permissions for the database file..."
sudo chmod 644 /etc/x-ui/x-ui.db
sudo chown $USERNAME:$USERNAME /etc/x-ui/x-ui.db

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
echo "Installation complete! Your server is running at http://$SERVER_DOMAIN:$PORT"
echo "The app will automatically restart if the server reboots."

#!/bin/bash

# Update and install necessary dependencies
echo "Updating system..."
sudo apt-get update -y

# Install Python3, pip, and virtualenv if not installed
echo "Installing Python3 and dependencies..."
sudo apt-get install python3 python3-pip python3-venv -y

# Set up a virtual environment
python3 -m venv usage-env
source usage-env/bin/activate

# Install required Python packages
pip install -r requirements.txt

# Prompt for panel IP and port
read -p "Enter the Panel IP: " panel_ip
read -p "Enter the Panel Port: " panel_port

# Save the panel IP and port to a config file
echo "PANEL_IP='$panel_ip'" > config.py
echo "PANEL_PORT='$panel_port'" >> config.py

# Set up the Flask app
echo "Setting up Flask app..."
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the Flask application
echo "Running the Flask application..."
flask run --host=0.0.0.0 --port=5000

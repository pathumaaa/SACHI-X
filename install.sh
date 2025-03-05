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

# Check if config.py exists, if not, create it
if [ ! -f config.py ]; then
    # Prompt for panel IP and port if config file does not exist
    echo "Enter the Panel IP:"
    read panel_ip
    echo "Enter the Panel Port:"
    read panel_port

    # Save the panel IP and port to a config file
    echo "PANEL_IP='$panel_ip'" > config.py
    echo "PANEL_PORT='$panel_port'" >> config.py
else
    # If config file exists, just read the values
    source config.py
    echo "Using existing config: PANEL_IP='$PANEL_IP' and PANEL_PORT='$PANEL_PORT'"
fi

# Set up the Flask app
echo "Setting up Flask app..."
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the Flask application
echo "Running the Flask application..."
flask run --host=0.0.0.0 --port=5000

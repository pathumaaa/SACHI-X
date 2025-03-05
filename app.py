from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Load panel IP and port from config.py
try:
    # Import the config file where PANEL_IP and PANEL_PORT are stored
    from config import PANEL_IP, PANEL_PORT
except ImportError:
    PANEL_IP = "127.0.0.1"  # Default IP if the config is not found
    PANEL_PORT = "8000"  # Default port if the config is not found

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        response = get_client_data(email)
        return render_template('index.html', response=response)
    return render_template('index.html', response=None)

def get_client_data(email):
    url = f'http://{PANEL_IP}:{PANEL_PORT}/panel/api/inbounds/getClientTraffics/{email}'
    headers = {
        'Accept': 'application/json',
        # You may need to add authorization headers if required
    }
    try:
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else {"error": "Failed to fetch data"}
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {e}"}

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

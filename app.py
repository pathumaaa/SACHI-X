from flask import Flask, render_template
import requests
from config import get_x_ui_url

app = Flask(__name__)

# Fetch the X-UI URL from the config
X_UI_API_URL = get_x_ui_url()

@app.route('/usage/<uuid>')
def get_usage(uuid):
    try:
        # Fetch user data from X-UI API (Allow unverified HTTPS requests)
        response = requests.get(f"{X_UI_API_URL}/panel/api/inbounds/getClientTrafficsById/{uuid}", verify=False)

        if response.status_code == 200:
            data = response.json()

            # Ensure the necessary fields exist in the response
            if all(key in data for key in ['name', 'uuid', 'quota', 'remaining', 'expiration']):
                return render_template(
                    'usage.html',
                    name=data['name'],
                    uuid=data['uuid'],
                    quota=data['quota'],
                    remaining=data['remaining'],
                    expiration=data['expiration']
                )
            else:
                return "Error: Missing expected data fields", 500
        else:
            return f"Error fetching data from API. Status code: {response.status_code}", 500

    except Exception as e:
        return f"Error occurred: {str(e)}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

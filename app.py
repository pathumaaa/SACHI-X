from flask import Flask, render_template
import requests

app = Flask(__name__)

X_UI_API_URL = "http://your-x-ui-panel-url/panel/api/inbounds/getClientTrafficsById"

@app.route('/usage/<uuid>')
def get_usage(uuid):
    # Fetch user data from X-UI API
    response = requests.get(f"{X_UI_API_URL}/{uuid}")
    
    if response.status_code == 200:
        data = response.json()
        # Assuming the response includes name, uuid, quota, remaining data, and expiration
        name = data['name']
        uuid = data['uuid']
        quota = data['quota']
        remaining = data['remaining']
        expiration = data['expiration']
        return render_template('usage.html', name=name, uuid=uuid, quota=quota, remaining=remaining, expiration=expiration)
    else:
        return "Error fetching data", 500

if __name__ == "__main__":
    app.run(debug=True)

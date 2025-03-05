import os
import json

def set_x_ui_url(url):
    # Save the URL in an environment variable or a config file
    config = {'X_UI_URL': url}
    with open('config.json', 'w') as f:
        json.dump(config, f)

def get_x_ui_url():
    # Load the URL from the configuration file
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config.get('X_UI_URL', 'http://127.0.0.1')
    else:
        return 'http://127.0.0.1'

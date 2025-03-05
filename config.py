# config.py

X_UI_API_URL = None

def set_x_ui_url(url):
    global X_UI_API_URL
    X_UI_API_URL = url

def get_x_ui_url():
    return X_UI_API_URL

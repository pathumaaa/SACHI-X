import os

def get_x_ui_url():
    # Fetch the URL from environment variable or default to HTTP
    x_ui_protocol = os.getenv('X_UI_PROTOCOL', 'http')  # Default to 'http' if not set
    x_ui_host = os.getenv('X_UI_HOST', '127.0.0.1')    # Default to localhost if not set
    x_ui_port = os.getenv('X_UI_PORT', '80')           # Default to port 80 for HTTP
    
    # Construct the full URL with the protocol
    return f"{x_ui_protocol}://{x_ui_host}:{x_ui_port}"

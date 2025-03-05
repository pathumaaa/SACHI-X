import os
import subprocess
from config import set_x_ui_url

def ask_for_domain_or_ip():
    print("Please enter your X-UI Panel URL (IP address or domain). Example: https://yourdomain.com")
    x_ui_url = input("X-UI URL: ").strip()
    
    # Validate URL format
    if x_ui_url.startswith("http://") or x_ui_url.startswith("https://"):
        set_x_ui_url(x_ui_url)
        print(f"X-UI Panel URL set to: {x_ui_url}")
        # After setting the URL, start the Flask app (app.py)
        print("Starting the web application...")
        subprocess.run(["python3", "app.py"])  # This runs your Flask app
    else:
        print("Invalid URL. Please make sure to include http:// or https://")
        return ask_for_domain_or_ip()

if __name__ == "__main__":
    ask_for_domain_or_ip()

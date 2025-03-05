import sqlite3
import json

# Updated database path
DB_PATH = '/etc/x-sl/x-ui.db'

def fetch_user_data(username):
    # Connect to SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Query to fetch user data based on username
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()

    # Check if user data exists
    if user_data:
        # Example output (adjust based on your schema)
        user_info = {
            "id": user_data[0],
            "username": user_data[1],
            "password": user_data[2],
            "login_secret": user_data[3]
        }
    else:
        user_info = {"error": "User not found"}

    # Close the connection
    conn.close()

    # Return the data as JSON
    return json.dumps(user_info)

# Example usage: Fetch data by username
username = 'example_username'
data = fetch_user_data(username)
print(data)

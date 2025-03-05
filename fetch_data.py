import sqlite3
import json

# Updated database path
DB_PATH = '/etc/x-sl/x-ui.db'

def fetch_user_data(uuid):
    # Connect to SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Query to fetch user data based on UUID
    cursor.execute("SELECT * FROM users WHERE uuid = ?", (uuid,))
    user_data = cursor.fetchone()

    # Check if user data exists
    if user_data:
        # Example output (adjust based on your schema)
        user_info = {
            "uuid": user_data[0],
            "username": user_data[1],
            "email": user_data[2],  # Assuming you have an email field
            "expiry_date": user_data[3]  # Assuming you have an expiry_date field
        }
    else:
        user_info = {"error": "User not found"}

    # Close the connection
    conn.close()

    # Return the data as JSON
    return json.dumps(user_info)

# Example usage: Fetch data by UUID
uuid = 'example-uuid'
data = fetch_user_data(uuid)
print(data)

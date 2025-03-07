from flask import Flask, request, render_template
import sqlite3
from datetime import datetime

app = Flask(__name__)

db_path = "/etc/x-ui/x-ui.db"  # Change this if your database is located elsewhere

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/usage', methods=['POST'])
def usage():
    user_input = request.form.get('user_input')  # Get input from the form

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the input is an email or ID
    query = '''SELECT email, up, down, total, quota, expiry_time FROM client_traffics WHERE email = ? OR id = ?'''
    cursor.execute(query, (user_input, user_input))

    row = cursor.fetchone()
    conn.close()

    if row:
        email = row[0]
        up = row[1] / 1048576  # Convert bytes to MB
        down = row[2] / 1048576  # Convert bytes to MB
        total = row[3] / 1048576  # Convert bytes to MB
        quota = row[4] / 1048576  # Convert quota to MB (assuming it's stored in bytes)
        expiry_date = datetime.utcfromtimestamp(row[5]).strftime('%Y-%m-%d %H:%M:%S')

        # Calculate remaining data
        remaining_data = quota - total

        # Calculate remaining time (in days)
        expiry_timestamp = row[5]
        current_time = datetime.utcnow().timestamp()
        remaining_time_seconds = expiry_timestamp - current_time
        remaining_time_days = remaining_time_seconds / (60 * 60 * 24)  # Convert seconds to days

        return render_template('result.html', email=email, up=up, down=down, total=total, quota=quota, 
                               remaining_data=remaining_data, expiry_date=expiry_date, remaining_time_days=remaining_time_days)
    else:
        return "No data found for this user."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

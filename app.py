from flask import Flask, request, render_template
import sqlite3
from datetime import datetime

app = Flask(__name__)

db_path = "/etc/x-sl/x-ui.db"  # Change this if your database is located elsewhere

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/usage', methods=['POST'])
def usage():
    user_input = request.form.get('user_input')  # Get input from the form

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the input is an email or ID
    query = '''SELECT email, up, down, total, expiry_time FROM client_traffics WHERE email = ? OR id = ?'''
    cursor.execute(query, (user_input, user_input))

    row = cursor.fetchone()
    conn.close()

    if row:
        email = row[0]
        up = row[1]
        down = row[2]
        total = row[3]
        expiry_date = datetime.utcfromtimestamp(row[4]).strftime('%Y-%m-%d %H:%M:%S')

        return render_template('result.html', email=email, up=up, down=down, total=total, expiry_date=expiry_date)
    else:
        return "No data found for this user."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

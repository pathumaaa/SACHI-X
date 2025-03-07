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

    if not user_input:
        return "No user input provided", 400

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to fetch client data from client_traffics
    query = '''SELECT email, up, down, total, expiry_time, inbound_id FROM client_traffics WHERE email = ? OR id = ?'''
    cursor.execute(query, (user_input, user_input))

    row = cursor.fetchone()

    if row:
        email = row[0]
        up = row[1]  # in bytes
        down = row[2]  # in bytes
        total = row[3]  # in bytes
        expiry_time = row[4]
        inbound_id = row[5]

        # Convert expiry time to a human-readable format, handle invalid timestamps
        try:
            if expiry_time > 0:  # Ensure expiry_time is valid
                expiry_date = datetime.utcfromtimestamp(expiry_time).strftime('%Y-%m-%d %H:%M:%S')
            else:
                expiry_date = "Invalid Expiry Time"
        except Exception as e:
            expiry_date = "Error in Expiry Time"

        # Query to fetch totalGB from the inbounds table based on inbound_id
        inbound_query = '''SELECT totalGB FROM inbounds WHERE id = ?'''
        cursor.execute(inbound_query, (inbound_id,))
        inbound_row = cursor.fetchone()

        totalGB = inbound_row[0] if inbound_row else "Not Available"

        # Convert data usage to MB or GB (whichever is more appropriate)
        up_mb = up / (1024 * 1024)  # Convert bytes to MB
        down_mb = down / (1024 * 1024)  # Convert bytes to MB
        total_gb = total / (1024 * 1024 * 1024)  # Convert bytes to GB

        conn.close()

        # Render result template
        return render_template(
            'result.html',
            email=email,
            up=round(up_mb, 2),
            down=round(down_mb, 2),
            total=round(total_gb, 2),
            expiry_date=expiry_date,
            totalGB=totalGB
        )
    else:
        conn.close()
        return "No data found for this user.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

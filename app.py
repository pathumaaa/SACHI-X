from flask import Flask, request, render_template
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)

db_path = "/etc/x-ui/x-ui.db"  # Change if needed

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/usage', methods=['POST'])
def usage():
    user_input = request.form.get('user_input')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch client traffic data
    query = '''SELECT email, up, down, total, expiry_time, inbound_id FROM client_traffics WHERE email = ? OR id = ?'''
    cursor.execute(query, (user_input, user_input))
    row = cursor.fetchone()

    if row:
        email, up, down, total, expiry_time, inbound_id = row

        # Convert expiry time (handle milliseconds correctly)
        try:
            expiry_time = int(expiry_time) / 1000 if expiry_time > 9999999999 else int(expiry_time)
            expiry_date = datetime.utcfromtimestamp(expiry_time).strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            expiry_date = "Invalid Date"

        # Fetch total allocated GB and config status from inbounds table
        inbound_query = '''SELECT total, enable FROM inbounds WHERE id = ?'''
        cursor.execute(inbound_query, (inbound_id,))
        inbound_row = cursor.fetchone()

        total_allocated = "Not Available"
        config_status = "Unknown"

        if inbound_row:
            total_allocated, enable_status = inbound_row
            total_allocated = convert_units(total_allocated)  # Convert to GB/TB
            config_status = "Enabled" if enable_status == 1 else "Disabled"

        conn.close()

        return render_template('result.html', email=email, 
                               up=convert_units(up), 
                               down=convert_units(down), 
                               total=convert_units(total),
                               expiry_date=expiry_date, 
                               total_allocated=total_allocated,
                               config_status=config_status)
    else:
        conn.close()
        return "No data found for this user."

def convert_units(value):
    """ Convert bytes to MB, GB, or TB dynamically. """
    try:
        value = int(value)
        if value >= 1024**4:
            return f"{value / (1024**4):.2f} TB"
        elif value >= 1024**3:
            return f"{value / (1024**3):.2f} GB"
        elif value >= 1024**2:
            return f"{value / (1024**2):.2f} MB"
        else:
            return f"{value} Bytes"
    except (ValueError, TypeError):
        return "Invalid Data"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# from flask import Flask, request, render_template_string
# from ipwhois import IPWhois
# from datetime import datetime
# import sqlite3
# import os

# app = Flask(__name__)
# DB_PATH = 'visitor_log.db'

# def init_db():
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS visitors (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             ip TEXT,
#             isp TEXT,
#             country TEXT,
#             timestamp TEXT
#         )
#     ''')
#     conn.commit()
#     conn.close()

# init_db()

# def get_client_ip():
#     if request.environ.get('HTTP_X_FORWARDED_FOR'):
#         ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
#     else:
#         ip = request.remote_addr
#     return ip

# def log_visitor(ip, isp, country):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute('''
#         INSERT INTO visitors (ip, isp, country, timestamp)
#         VALUES (?, ?, ?, ?)
#     ''', (ip, isp, country, datetime.now().isoformat()))
#     conn.commit()
#     conn.close()

# @app.route('/')
# def home():
#     ip = get_client_ip()
#     isp = "Unknown"
#     country = "Unknown"
#     try:
#         obj = IPWhois(ip)
#         res = obj.lookup_rdap()
#         isp = res['network']['name'] or "Unknown"
#         country = res['network']['country'] or "Unknown"
#     except Exception as e:
#         print(f"Lookup failed: {e}")
#     log_visitor(ip, isp, country)
#     return render_template_string('''
#         <h2>Welcome to the Dashboard</h2>
#         <p><strong>Your IP:</strong> {{ ip }}</p>
#         <p><strong>ISP / Org:</strong> {{ isp }}</p>
#         <p><strong>Country:</strong> {{ country }}</p>
#         <a href="/visits">View all visitors</a>
#     ''', ip=ip, isp=isp, country=country)

# @app.route('/visits')
# def visits():
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("SELECT ip, isp, country, timestamp FROM visitors ORDER BY id DESC")
#     rows = c.fetchall()
#     conn.close()
#     return render_template_string('''
#         <h2>Visitor Log</h2>
#         <table border="1" cellpadding="8">
#             <tr><th>IP</th><th>ISP</th><th>Country</th><th>Time</th></tr>
#             {% for row in rows %}
#             <tr>
#                 <td>{{ row[0] }}</td>
#                 <td>{{ row[1] }}</td>
#                 <td>{{ row[2] }}</td>
#                 <td>{{ row[3] }}</td>
#             </tr>
#             {% endfor %}
#         </table>
#         <br><a href="/">Back to Dashboard</a>
#     ''', rows=rows)

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)


# from flask import Flask, request, render_template_string
# from ipwhois import IPWhois
# from datetime import datetime
# import geoip2.database
# import sqlite3
# import os
# import logging

# logging.basicConfig(level=logging.DEBUG)

# app = Flask(__name__)
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, 'visitor_log.db')
# GEOIP_DB = os.path.join(BASE_DIR, 'data', 'GeoLite2-City.mmdb')

# def init_db():
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS visitors (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             ip TEXT,
#             isp TEXT,
#             city TEXT,
#             state TEXT,
#             country TEXT,
#             timestamp TEXT,
            
#         )
#     ''')
#     conn.commit()
#     conn.close()

# init_db()

# def get_client_ip():
#     if request.environ.get('HTTP_X_FORWARDED_FOR'):
#         ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
#     else:
#         ip = request.remote_addr
#     return ip
# def get_location(ip):
#     if not os.path.exists(GEOIP_DB):
#         print(f"GeoIP database not found at {GEOIP_DB}")
#         return "Unknown", "Unknown", "Unknown"
    
#     try:
#         reader = geoip2.database.Reader(GEOIP_DB)
#         response = reader.city(ip)
#         city = response.city.name or "Unknown"
#         state = response.subdivisions.most_specific.name if response.subdivisions else "Unknown"
#         country = response.country.name or "Unknown"
#         reader.close()
#         return city, state, country
#     except Exception as e:
#         print(f"GeoIP error: {e}")
#         return "Unknown", "Unknown", "Unknown"

# def get_isp(ip):
#     try:
#         obj = IPWhois(ip)
#         res = obj.lookup_rdap()
#         return res['network']['name'] or "Unknown"
#     except Exception as e:
#         print(f"IPWhois error: {e}")
#         return "Unknown"

# def log_visitor(ip, isp, city, state, country):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute('''
#         INSERT INTO visitors (ip, isp, city, state, country, timestamp)
#         VALUES (?, ?, ?, ?, ?, ?)
#     ''', (ip, isp, city, state, country, datetime.now().isoformat()))
#     conn.commit()
#     conn.close()

# @app.route('/')
# def home():
#     try:
#         ip = get_client_ip()
#         isp = get_isp(ip)
#         city, state, country = get_location(ip)
#         log_visitor(ip, isp, city, state, country)

#         return render_template_string('''
#             <h2>Welcome to the Dashboard</h2>
#             <p><strong>Your IP:</strong> {{ ip }}</p>
#             <p><strong>ISP / Org:</strong> {{ isp }}</p>
#             <p><strong>City:</strong> {{ city }}</p>
#             <p><strong>State:</strong> {{ state }}</p>
#             <p><strong>Country:</strong> {{ country }}</p>
#             <a href="/visits">View all visitors</a>
#         ''', ip=ip, isp=isp, city=city, state=state, country=country)
#     except Exception as e:
#         logging.error(f"Error in home route: {str(e)}")
#         return f"An error occurred: {str(e)}", 500
# @app.route('/visits')
# def visits():
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("SELECT ip, isp, city, state, country, timestamp FROM visitors ORDER BY id DESC")
#     rows = c.fetchall()
#     conn.close()

#     return render_template_string('''
#         <h2>Visitor Log</h2>
#         <table border="1" cellpadding="8">
#             <tr><th>IP</th><th>ISP</th><th>City</th><th>State</th><th>Country</th><th>Time</th></tr>
#             {% for row in rows %}
#             <tr>
#                 <td>{{ row[0] }}</td>
#                 <td>{{ row[1] }}</td>
#                 <td>{{ row[2] }}</td>
#                 <td>{{ row[3] }}</td>
#                 <td>{{ row[4] }}</td>
#                 <td>{{ row[5] }}</td>
#             </tr>
#             {% endfor %}
#         </table>
#         <br><a href="/">Back to Dashboard</a>
#     ''', rows=rows)

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)




from flask import Flask, request, render_template_string
from ipwhois import IPWhois
from datetime import datetime
from pytz import timezone
import geoip2.database
import sqlite3
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Constants
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'visitor_log.db')
GEOIP_DB = os.path.join(BASE_DIR, 'data', 'GeoLite2-City.mmdb')
IST = timezone('Asia/Kolkata')

# Database initialization and migration
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create table if it does not exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            isp TEXT,
            city TEXT,
            state TEXT,
            country TEXT,
            latitude REAL DEFAULT 0.0,
            longitude REAL DEFAULT 0.0,
            timestamp TEXT,
            revisits INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Helper Functions
def get_client_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        ip = request.remote_addr
    return ip

def get_location(ip):
    if ip == "127.0.0.1":
        return "Localhost", "Local", "Local", 0.0, 0.0
    if not os.path.exists(GEOIP_DB):
        logging.error(f"GeoIP database not found at {GEOIP_DB}")
        return "Unknown", "Unknown", "Unknown", 0.0, 0.0

    try:
        reader = geoip2.database.Reader(GEOIP_DB)
        response = reader.city(ip)
        city = response.city.name or "Unknown"
        state = response.subdivisions.most_specific.name if response.subdivisions else "Unknown"
        country = response.country.name or "Unknown"
        latitude = response.location.latitude or 0.0
        longitude = response.location.longitude or 0.0
        reader.close()
        return city, state, country, latitude, longitude
    except Exception as e:
        logging.error(f"GeoIP error: {e}")
        return "Unknown", "Unknown", "Unknown", 0.0, 0.0

def get_isp(ip):
    if ip == "127.0.0.1":
        return "Localhost ISP"
    try:
        obj = IPWhois(ip)
        res = obj.lookup_rdap()
        return res['network']['name'] or "Unknown"
    except Exception as e:
        logging.error(f"IPWhois error: {e}")
        return "Unknown"

def log_visitor(ip, isp, city, state, country, latitude, longitude):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if the IP already exists
    c.execute('SELECT id, revisits FROM visitors WHERE ip = ?', (ip,))
    existing = c.fetchone()

    if existing:
        visitor_id, revisits = existing
        c.execute('''
            UPDATE visitors
            SET revisits = ?, timestamp = ?
            WHERE id = ?
        ''', (revisits + 1, datetime.now(IST).isoformat(), visitor_id))
        logging.info(f"Updated revisits for IP {ip}: {revisits + 1}")
    else:
        c.execute('''
            INSERT INTO visitors (ip, isp, city, state, country, latitude, longitude, timestamp, revisits)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', (ip, isp, city, state, country, latitude, longitude, datetime.now(IST).isoformat()))
        logging.info(f"New visitor logged: IP {ip}")

    conn.commit()
    conn.close()

# Routes
@app.route('/')
def home():
    try:
        ip = get_client_ip()
        isp = get_isp(ip)
        city, state, country, latitude, longitude = get_location(ip)
        log_visitor(ip, isp, city, state, country, latitude, longitude)

        return render_template_string('''
            <h2>Welcome to the Dashboard</h2>
            <p><strong>Your IP:</strong> {{ ip }}</p>
            <p><strong>ISP / Org:</strong> {{ isp }}</p>
            <p><strong>City:</strong> {{ city }}</p>
            <p><strong>State:</strong> {{ state }}</p>
            <p><strong>Country:</strong> {{ country }}</p>
            <p><strong>Latitude:</strong> {{ latitude }}</p>
            <p><strong>Longitude:</strong> {{ longitude }}</p>
            <a href="/visits">View all visitors</a>
        ''', ip=ip, isp=isp, city=city, state=state, country=country, latitude=latitude, longitude=longitude)

    except Exception as e:
        logging.error(f"Error in home route: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/visits')
def visits():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT ip, isp, city, state, country, latitude, longitude, timestamp, revisits
        FROM visitors
        ORDER BY id DESC
    ''')
    rows = c.fetchall()
    conn.close()

    return render_template_string('''
        <h2>Visitor Log</h2>
        <table border="1" cellpadding="8">
            <tr><th>IP</th><th>ISP</th><th>City</th><th>State</th><th>Country</th>
            <th>Latitude</th><th>Longitude</th><th>Time (IST)</th><th>Revisits</th></tr>
            {% for row in rows %}
            <tr>
                <td>{{ row[0] }}</td>
                <td>{{ row[1] }}</td>
                <td>{{ row[2] }}</td>
                <td>{{ row[3] }}</td>
                <td>{{ row[4] }}</td>
                <td>{{ row[5] }}</td>
                <td>{{ row[6] }}</td>
                <td>{{ row[7] }}</td>
                <td>{{ row[8] }}</td>
            </tr>
            {% endfor %}
        </table>
        <br><a href="/">Back to Dashboard</a>
    ''', rows=rows)

# Main
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7000))
    app.run(host='0.0.0.0', port=port)

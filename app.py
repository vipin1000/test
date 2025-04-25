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


from flask import Flask, request, render_template_string
from ipwhois import IPWhois
from datetime import datetime
import geoip2.database
import sqlite3
import os

app = Flask(__name__)
DB_PATH = 'visitor_log.db'
GEOIP_DB = 'data/GeoLite2-ASN.mmdb'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            isp TEXT,
            city TEXT,
            state TEXT,
            country TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_client_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        ip = request.remote_addr
    return ip

def get_location(ip):
    try:
        reader = geoip2.database.Reader(GEOIP_DB)
        response = reader.city(ip)
        city = response.city.name or "Unknown"
        state = response.subdivisions.most_specific.name or "Unknown"
        country = response.country.name or "Unknown"
        reader.close()
    except Exception as e:
        print(f"GeoIP error: {e}")
        city = state = country = "Unknown"
    return city, state, country

def get_isp(ip):
    try:
        obj = IPWhois(ip)
        res = obj.lookup_rdap()
        return res['network']['name'] or "Unknown"
    except Exception as e:
        print(f"IPWhois error: {e}")
        return "Unknown"

def log_visitor(ip, isp, city, state, country):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO visitors (ip, isp, city, state, country, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (ip, isp, city, state, country, datetime.now().isoformat()))
    conn.commit()
    conn.close()

@app.route('/')
def home():
    ip = get_client_ip()
    isp = get_isp(ip)
    city, state, country = get_location(ip)
    log_visitor(ip, isp, city, state, country)

    return render_template_string('''
        <h2>Welcome to the Dashboard</h2>
        <p><strong>Your IP:</strong> {{ ip }}</p>
        <p><strong>ISP / Org:</strong> {{ isp }}</p>
        <p><strong>City:</strong> {{ city }}</p>
        <p><strong>State:</strong> {{ state }}</p>
        <p><strong>Country:</strong> {{ country }}</p>
        <a href="/visits">View all visitors</a>
    ''', ip=ip, isp=isp, city=city, state=state, country=country)

@app.route('/visits')
def visits():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ip, isp, city, state, country, timestamp FROM visitors ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    return render_template_string('''
        <h2>Visitor Log</h2>
        <table border="1" cellpadding="8">
            <tr><th>IP</th><th>ISP</th><th>City</th><th>State</th><th>Country</th><th>Time</th></tr>
            {% for row in rows %}
            <tr>
                <td>{{ row[0] }}</td>
                <td>{{ row[1] }}</td>
                <td>{{ row[2] }}</td>
                <td>{{ row[3] }}</td>
                <td>{{ row[4] }}</td>
                <td>{{ row[5] }}</td>
            </tr>
            {% endfor %}
        </table>
        <br><a href="/">Back to Dashboard</a>
    ''', rows=rows)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
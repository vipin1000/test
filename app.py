from flask import Flask, request, render_template_string,render_template
from ipwhois import IPWhois
from datetime import datetime
import sqlite3

app = Flask(__name__)
DB_PATH = 'visitor_log.db'

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            isp TEXT,
            country TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Get IP (even behind proxy)
def get_client_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        ip = request.remote_addr
    return ip

# Log data
def log_visitor(ip, isp, country):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO visitors (ip, isp, country, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (ip, isp, country, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Home Route


@app.route('/')
def home():
    ip = get_client_ip()
    isp = "Unknown"
    country = "Unknown"

    try:
        obj = IPWhois(ip)
        res = obj.lookup_rdap()
        isp = res['network']['name'] or "Unknown"
        country = res['network']['country'] or "Unknown"
    except Exception as e:
        print(f"Lookup failed: {e}")

    log_visitor(ip, isp, country)

    return render_template('home.html', ip=ip, isp=isp, country=country)


# Route to view all visitor logs
@app.route('/visits')
def visits():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ip, isp, country, timestamp FROM visitors ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    return render_template_string('''
        <h2>Visitor Log</h2>
        <table border="1" cellpadding="8">
            <tr><th>IP</th><th>ISP</th><th>Country</th><th>Time</th></tr>
            {% for row in rows %}
            <tr>
                <td>{{ row[0] }}</td>
                <td>{{ row[1] }}</td>
                <td>{{ row[2] }}</td>
                <td>{{ row[3] }}</td>
            </tr>
            {% endfor %}
        </table>
        <br><a href="/">Back to Dashboard</a>
    ''', rows=rows)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify, render_template_string, Response
from flask_cors import CORS
import sqlite3
from functools import wraps
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

PORT = int(os.environ.get('PORT', 5000))
DATABASE = 'data.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mac_address TEXT NOT NULL,
            data_json TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    
def basic_auth(username, password):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth = request.authorization
            if not auth or auth.username != username or auth.password != password:
                return Response(
                    'Authentication required',
                    401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'}
                )
            return f(*args, **kwargs)
        return decorated_function
    return decorator

ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin1234')

@app.route('/admin/db', methods=['GET'])
@basic_auth(ADMIN_USER, ADMIN_PASSWORD)
def admin_db():
    # Get database statistics
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count entries and get other useful info
    cursor.execute("SELECT COUNT(*) FROM data_entries")
    count = cursor.fetchone()[0]
    
    # Get latest entries
    cursor.execute("SELECT * FROM data_entries ORDER BY id DESC LIMIT 10")
    latest = cursor.fetchall()
    
    conn.close()
    
    # Generate admin HTML
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Database Admin</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { text-align: left; padding: 12px 15px; border-bottom: 1px solid #ddd; }
            th { background-color: #f8f9fa; }
            tr:hover { background-color: #f5f5f5; }
            .actions { display: flex; gap: 10px; }
            .btn { padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
            .btn-primary { background-color: #0d6efd; color: white; }
            .btn-danger { background-color: #dc3545; color: white; }
            .stats { display: flex; gap: 20px; margin-bottom: 20px; }
            .stat-card { background-color: #f8f9fa; border-radius: 8px; padding: 20px; flex: 1; }
            .stat-value { font-size: 24px; font-weight: bold; margin: 10px 0; }
            pre { background: #f8f9fa; padding: 15px; border-radius: 4px; overflow: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Database Administration</h1>
            
            <div class="stats">
                <div class="stat-card">
                    <div>Total Entries</div>
                    <div class="stat-value">{{ count }}</div>
                </div>
            </div>
            
            <h2>Latest Entries</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>MAC Address</th>
                        <th>Timestamp</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in latest %}
                    <tr>
                        <td>{{ row.id }}</td>
                        <td>{{ row.mac_address }}</td>
                        <td>{{ row.timestamp }}</td>
                        <td class="actions">
                            <a href="/admin/entry/{{ row.id }}" class="btn btn-primary">View</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <h2>Database Schema</h2>
            <pre>
CREATE TABLE data_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mac_address TEXT NOT NULL,
    data_json TEXT NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
            </pre>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html, count=count, latest=latest)

@app.route('/admin/entry/<int:entry_id>', methods=['GET'])
@basic_auth(ADMIN_USER, ADMIN_PASSWORD)
def admin_view_entry(entry_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data_entries WHERE id = ?", (entry_id,))
    entry = cursor.fetchone()
    conn.close()
    
    if not entry:
        return "Entry not found", 404
    
    # Parse JSON data
    data = json.loads(entry['data_json'])
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Entry Details</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }
            .card { background: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
            .field { margin-bottom: 10px; }
            .label { font-weight: bold; display: inline-block; width: 120px; }
            pre { background: #f8f9fa; padding: 15px; border-radius: 4px; overflow: auto; }
            .back-link { display: inline-block; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Entry Details</h1>
            <div class="card">
                <div class="field">
                    <span class="label">ID:</span> {{ entry.id }}
                </div>
                <div class="field">
                    <span class="label">MAC Address:</span> {{ entry.mac_address }}
                </div>
                <div class="field">
                    <span class="label">Timestamp:</span> {{ entry.timestamp }}
                </div>
                
                <h3>JSON Data:</h3>
                <pre>{{ pretty_json }}</pre>
            </div>
            
            <a href="/admin/db" class="back-link">← Back to Database Admin</a>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(
        html, 
        entry=entry, 
        pretty_json=json.dumps(data, indent=4)
    )
    
@app.route('/api/admin/export', methods=['GET'])
@basic_auth(ADMIN_USER, ADMIN_PASSWORD)
def export_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all data
        cursor.execute("SELECT * FROM data_entries")
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        result = []
        for row in rows:
            item = dict(row)
            # Parse the JSON string into an object
            item['data'] = json.loads(item['data_json'])
            # Remove the raw JSON string
            del item['data_json']
            result.append(item)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/')
def home():
    return "Hello, Welcome to the Backend!"

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/data', methods=['GET'])
def get_data():
    mac = request.args.get('mac_address')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if mac:
        cursor.execute("SELECT * FROM data_entries WHERE LOWER(mac_address) = LOWER(?)", (mac,))
    else:
        cursor.execute("SELECT * FROM data_entries")
    
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        entry = {
            'id': row['id'],
            'mac_address': row['mac_address'],
            'timestamp': row['timestamp']
        }
        entry.update(json.loads(row['data_json']))
        result.append(entry)
        
    return jsonify(result)

@app.route('/api/insert_data', methods=['POST'])
def insert_data():
    data = request.get_json()
    
    mac_address = data.get('mac_address', '')
    
    data_json = json.dumps(data)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO data_entries (mac_address, data_json) VALUES (?, ?)",
        (mac_address, data_json)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'add successfully'}), 201



init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
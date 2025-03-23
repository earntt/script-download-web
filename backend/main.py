from flask import Flask, request, jsonify, render_template_string, Response, session
from flask_cors import CORS
import sqlite3
from functools import wraps
import json
import os
import shutil
from datetime import datetime
import secrets

app = Flask(__name__)
CORS(app)
# Add a secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

PORT = int(os.environ.get('PORT', 5000))
DATABASE = 'data.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
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
    # Generate a CSRF token for secure API calls
    csrf_token = secrets.token_hex(16)
    session['csrf_token'] = csrf_token
    
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
            .operations { margin: 20px 0; display: flex; gap: 10px; align-items: center; }
            #operation-status { margin-left: 10px; }
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
            
            <!-- Database operations -->
            <div class="operations">
                <button id="delete-all" class="btn btn-danger">Delete All Data</button>
                <a href="/api/admin/export" class="btn btn-primary">Export Data</a>
                <span id="operation-status"></span>
            </div>
            
            <h2>Latest Entries</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>IP Address</th>
                        <th>Timestamp</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in latest %}
                    <tr>
                        <td>{{ row.id }}</td>
                        <td>{{ row.ip_address }}</td>
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
    ip_address TEXT NOT NULL,
    data_json TEXT NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
            </pre>
        </div>
        
        <!-- Script for delete functionality -->
        <script>
            document.getElementById('delete-all').addEventListener('click', function() {
                if (confirm('WARNING: This will delete ALL data in the database. This cannot be undone. A backup will be created before deletion. Continue?')) {
                    const statusEl = document.getElementById('operation-status');
                    statusEl.textContent = 'Deleting...';
                    
                    fetch('/api/admin/delete_all', {
                        method: 'DELETE',
                        headers: {
                            'X-CSRF-Token': '{{ csrf_token }}',
                            'Content-Type': 'application/json'
                        },
                        credentials: 'same-origin'
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            statusEl.textContent = data.message;
                            setTimeout(() => {
                                window.location.reload();
                            }, 2000);
                        } else {
                            statusEl.textContent = 'Error: ' + data.message;
                        }
                    })
                    .catch(error => {
                        statusEl.textContent = 'Error: ' + error.message;
                    });
                }
            });
        </script>
    </body>
    </html>
    '''
    
    return render_template_string(html, count=count, latest=latest, csrf_token=csrf_token)

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
                    <span class="label">IP Address:</span> {{ entry.ip_address }}
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
    
@app.route('/api/get-ip', methods=['GET'])
def get_client_ip():
    client_ip = request.remote_addr
    forwarded_ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    real_ip = forwarded_ip or client_ip
    
    return jsonify({"ip": real_ip})

@app.route('/api/data', methods=['GET'])
def get_data():
    ip = request.args.get('ip_address')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if ip:
        cursor.execute("SELECT * FROM data_entries WHERE LOWER(ip_address) = LOWER(?)", (ip,))
    else:
        cursor.execute("SELECT * FROM data_entries")
    
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        entry = {
            'id': row['id'],
            'ip_address': row['ip_address'],
            'timestamp': row['timestamp']
        }
        entry.update(json.loads(row['data_json']))
        result.append(entry)
        
    return jsonify(result)

@app.route('/api/insert_data', methods=['POST'])
def insert_data():
    data = request.get_json()
    
    ip_address = data.get('ip_address', '')
    
    data_json = json.dumps(data)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO data_entries (ip_address, data_json) VALUES (?, ?)",
        (ip_address, data_json)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'add successfully'}), 201

@app.route('/api/admin/delete_all', methods=['DELETE'])
@basic_auth(ADMIN_USER, ADMIN_PASSWORD)
def delete_all_data():
    try:
        # Check CSRF token for security
        csrf_token = request.headers.get('X-CSRF-Token')
        if not csrf_token or csrf_token != session.get('csrf_token'):
            return jsonify({
                'status': 'error',
                'message': 'Invalid CSRF token'
            }), 403
            
        # Create a backup before deletion
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'backups'
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        backup_file = os.path.join(backup_dir, f'data_backup_before_delete_{timestamp}.db')
        
        # Connect directly to the file for backup
        shutil.copy2(DATABASE, backup_file)
        
        # Now delete all data
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM data_entries")
        deleted_count = conn.total_changes
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'All data deleted successfully. {deleted_count} records removed.',
            'backup_created': backup_file,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/admin/backup', methods=['POST'])
@basic_auth(ADMIN_USER, ADMIN_PASSWORD)
def backup_database():
    try:
        # Create backups folder if it doesn't exist
        if not os.path.exists('backups'):
            os.makedirs('backups')
            
        # Create backup with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'backups/data_backup_{timestamp}.db'
        
        # Copy database file
        shutil.copy2(DATABASE, backup_file)
        
        return jsonify({
            'status': 'success',
            'message': f'Backup created: {backup_file}',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
        
@app.route('/api/latest', methods=['GET'])
def get_latest_entry():
    """Get the latest entry from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the most recent entry ordered by ID (assuming higher ID = more recent)
        cursor.execute("SELECT * FROM data_entries ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                'status': 'error',
                'message': 'No entries found in database'
            }), 404
            
        # Convert row to dictionary
        entry = dict(row)
        
        # Parse the JSON string into an object
        data = json.loads(entry['data_json'])
        
        # Create the result object
        result = {
            'id': entry['id'],
            'ip_address': entry['ip_address'],
            'timestamp': entry['timestamp'],
            'data': data
        }
        
        return jsonify({
            'status': 'success',
            'entry': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
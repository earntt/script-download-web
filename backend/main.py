from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
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
    # Create the database and table if they don't exist
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
    
    # Convert rows to list of dictionaries
    result = []
    for row in rows:
        entry = {
            'id': row['id'],
            'mac_address': row['mac_address'],
            'timestamp': row['timestamp']
        }
        # Add the stored JSON data
        entry.update(json.loads(row['data_json']))
        result.append(entry)
        
    return jsonify(result)

@app.route('/api/insert_data', methods=['POST'])
def insert_data():
    data = request.get_json()
    
    # Extract the mac_address
    mac_address = data.get('mac_address', '')
    
    # Convert the entire data object to JSON string for storage
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

# Initialize the database on startup
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
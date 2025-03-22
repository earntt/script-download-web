from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

data_list = []

@app.route('/')
def home():
    return "Hello, Welcome to the Backend!"

@app.route('/api/data', methods=['GET'])
def get_data():
    mac = request.args.get('mac_address')
    filtered_data = data_list
    if mac:
        filtered_data = [item for item in filtered_data if item['mac_address'].lower() == mac.lower()]
    return jsonify(filtered_data)

@app.route('/api/insert_data', methods=['POST'])
def insert_data():
    data = request.get_json()
    data_list.append(data)
    return jsonify({'message':'add successfully'}),201



if __name__ == '__main__':
    app.run(debug=True)

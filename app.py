from flask import Flask, render_template, jsonify, request, send_from_directory
import requests

app = Flask(__name__)

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to serve the dataset
@app.route('/data')
def get_data():
    # URL to your dataset
    data_url = 'https://raw.githubusercontent.com/Ekanem-obo/Disease-Data-Management-and-Analysis/main/dataset/cleaned/cleaned_patients_data.json'
    # Fetch the dataset from GitHub
    response = requests.get(data_url)
    # Return the data as JSON
    return jsonify(response.json())

# Route for static files (handled by Flask automatically in production)
@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


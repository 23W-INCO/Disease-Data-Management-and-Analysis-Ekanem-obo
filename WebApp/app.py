from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load and process the dataset
file_path = './dataset/synthetic_chf_patient_ddata.json'
data_json = pd.read_json(file_path)
# Extracting nested data from 'entry' and 'resource' keys
extracted_data = [entry['resource'] for entry in data_json['entry']]
data = pd.DataFrame(extracted_data)

# Function to split blood pressure into systolic and diastolic
def split_blood_pressure(bp_str):
    systolic, diastolic = bp_str.split('/')
    return int(systolic), int(diastolic)

# Add systolic and diastolic columns to the DataFrame
data[['systolic_bp', 'diastolic_bp']] = data['bloodPressure'].apply(
    lambda x: pd.Series(split_blood_pressure(x))
)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/data', methods=['GET'])
def get_data():
    # Start with the full dataset
    filtered_data = data

    # Filter for exact matches (e.g., gender)
    for param in ['gender', 'ethnicity', 'smokingStatus', 'medication']:
        value = request.args.get(param)
        if value:
            filtered_data = filtered_data[filtered_data[param] == value]

    # Filter for ranges (e.g., age, BMI, bloodPressure, etc.)
    # ... [existing range filters here] ...

    # Blood pressure range filters
    systolic_min = request.args.get('systolic_min', type=int)
    systolic_max = request.args.get('systolic_max', type=int)
    diastolic_min = request.args.get('diastolic_min', type=int)
    diastolic_max = request.args.get('diastolic_max', type=int)

    if systolic_min is not None and systolic_max is not None:
        filtered_data = filtered_data[(filtered_data['systolic_bp'] >= systolic_min) &
                                      (filtered_data['systolic_bp'] <= systolic_max)]
    if diastolic_min is not None and diastolic_max is not None:
        filtered_data = filtered_data[(filtered_data['diastolic_bp'] >= diastolic_min) &
                                      (filtered_data['diastolic_bp'] <= diastolic_max)]

    # Return the filtered data
    return jsonify(filtered_data.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)

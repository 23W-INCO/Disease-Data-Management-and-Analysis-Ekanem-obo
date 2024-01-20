import json
import requests
from datetime import datetime

def clean_data_for_chart(bundle):
    cleaned_data = []

    # Extract resources from the bundle
    patients = {entry['resource']['id']: entry['resource'] for entry in bundle['entry'] if entry['resource']['resourceType'] == 'Patient'}
    observations = [entry['resource'] for entry in bundle['entry'] if entry['resource']['resourceType'] == 'Observation']
    medication_statements = [entry['resource'] for entry in bundle['entry'] if entry['resource']['resourceType'] == 'MedicationStatement']

    # Initialize patient_data to store medications by date
    patient_data = {patient_id: {'cholesterol': {}, 'blood_pressure': {}, 'BMI': {}, 'medication': {}} for patient_id in patients}

    # Map Observations to Patients
    for observation in observations:
        patient_id = observation['subject']['reference'].split('/')[-1]
        date = observation['effectiveDateTime'].split('T')[0]
        
        observation_display = observation['code']['coding'][0]['display'].lower()
        
        if 'cholesterol' in observation_display:
            cholesterol_value = observation.get('valueQuantity', {}).get('value', 'N/A')
            patient_data[patient_id]['cholesterol'][date] = cholesterol_value
        elif 'blood pressure' in observation_display:
            bp_values = {component['code']['coding'][0]['display']: component['valueQuantity']['value'] for component in observation.get('component', [])}
            patient_data[patient_id]['blood_pressure'][date] = bp_values
        elif 'bmi' in observation_display:
            bmi_value = observation.get('valueQuantity', {}).get('value', 'N/A')
            patient_data[patient_id]['BMI'][date] = bmi_value

    # Map Medications to Patients by Date
    for medication_statement in medication_statements:
        patient_id = medication_statement['subject']['reference'].split('/')[-1]
        med_date = medication_statement['effectiveDateTime'].split('T')[0]  # Extract the date from effectiveDateTime
        med_details = medication_statement['medicationCodeableConcept']['coding'][0]['display']
        
        # Initialize the list for the date if it doesn't exist
        if med_date not in patient_data[patient_id]['medication']:
            patient_data[patient_id]['medication'][med_date] = []
        
        # Append the medication details to the list for the specific date
        patient_data[patient_id]['medication'][med_date].append(med_details)

    # Combine the data for each patient
    for patient_id, patient in patients.items():
        birth_date = datetime.strptime(patient['birthDate'], "%Y-%m-%d")
        current_date = datetime.now()
        age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
        real_name = " ".join(patient['name'][0]['given']) + " " + patient['name'][0]['family']
        
        for date, bp_values in patient_data[patient_id]['blood_pressure'].items():
            cholesterol = patient_data[patient_id]['cholesterol'].get(date, 'N/A')
            bmi = patient_data[patient_id]['BMI'].get(date, 'N/A')
            
            # Get medications for the specific date
            medications = patient_data[patient_id]['medication'].get(date, [])
            
            bp_systolic = bp_values.get('Systolic blood pressure', 'N/A')
            bp_diastolic = bp_values.get('Diastolic blood pressure', 'N/A')
            
            cleaned_observation = {
                'date': date,
                'cholesterol': cholesterol,
                'name': real_name,
                'age': age,
                'BP': f"{bp_systolic}/{bp_diastolic}",
                'Med': medications,
                'BMI': bmi
            }
            cleaned_data.append(cleaned_observation)
            
    return cleaned_data

# Fetching the dataset
url = 'https://raw.githubusercontent.com/Ekanem-obo/Disease-Data-Management-and-Analysis/main/dataset/fhir_patients_data.json'
response = requests.get(url)
patients_data = response.json()

# Cleaning the dataset
cleaned_dataset = clean_data_for_chart(patients_data)

# Specifying the path where the cleaned data will be saved
cleaned_file_path = 'C:\\Users\\ekane\\Documents\\Visual Studio 2017\\My_Projects\\3rdSemester\\ICM\\webApp\\dataset\\cleaned\\cleaned_patients_data.json'

# Saving the cleaned data to the specified path
with open(cleaned_file_path, 'w', encoding='utf-8') as file:
    json.dump(cleaned_dataset, file, indent=4, ensure_ascii=False)

# Confirmation message
print(f"Cleaned data saved to {cleaned_file_path}")

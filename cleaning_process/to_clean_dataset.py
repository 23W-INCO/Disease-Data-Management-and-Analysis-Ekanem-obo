import json
import requests
from datetime import datetime

# Function to clean and reformat the patient data
def clean_patient_data(patients):
    cleaned_data = []
    for patient in patients:
        real_name = " ".join(patient['name'][0]['given']) + " " + patient['name'][0]['family']
        birth_date = datetime.strptime(patient['birthDate'], "%Y-%m-%d")
        current_date = datetime.now()
        age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
        medication = patient['medication'][0]['medicationCodeableConcept']['coding'][0]['display'] if patient['medication'] else "No medication"
        smoking_status = next((ext['valueString'] for ext in patient['extension'] if 'smokingStatus' in ext['url']), "Unknown")
        clinical_notes = next((ext['valueString'] for ext in patient['extension'] if 'clinicalNotes' in ext['url']), "No notes available")
        bmi_data = [{"date": obs['date'], "value": obs['BMI']} for obs in patient['observation']]
        blood_pressure_data = [{"date": obs['date'], "value": obs['bloodPressure']} for obs in patient['observation']]
        cholesterol_data = [{"date": obs['date'], "value": obs['cholesterol']} for obs in patient['observation']]
        cleaned_patient = {
            "name": real_name,
            "age": age,
            "gender": patient['gender'],
            "medication": medication,
            "smokingStatus": smoking_status,
            "clinicalNotes": clinical_notes,
            "BMI": bmi_data,
            "bloodPressure": blood_pressure_data,
            "cholesterol": cholesterol_data
        }
        cleaned_data.append(cleaned_patient)
    return cleaned_data

# URL of the dataset on GitHub
url = 'https://raw.githubusercontent.com/Ekanem-obo/Disease-Data-Management-and-Analysis/main/dataset/patients_data.json'

# Fetch the dataset
response = requests.get(url)
patients = response.json()

# Clean the dataset
cleaned_dataset = clean_patient_data(patients)

# Saving the cleaned dataset to my specified folder
cleaned_file_path = 'C:\\Users\\ekane\\Documents\\Visual Studio 2017\\My_Projects\\3rdSemester\\ICM\\webApp\\dataset\\cleaned\\cleaned_patients_data.json'
with open(cleaned_file_path, 'w', encoding='utf-8') as file:
    json.dump(cleaned_dataset, file, indent=4, ensure_ascii=False)

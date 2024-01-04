import json
import requests
from datetime import datetime

def clean_data_for_chart(patients):
    cleaned_data = []
    for patient in patients:
        birth_date = datetime.strptime(patient['birthDate'], "%Y-%m-%d")
        current_date = datetime.now()
        age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
        real_name = " ".join(patient['name'][0]['given']) + " " + patient['name'][0]['family']

        cholesterol_data = {item['date']: item['value'] for item in patient.get('cholesterolLevels', [])}

        for observation in patient.get('observation', []):
            bp_systolic, bp_diastolic = map(int, observation['bloodPressure'].split('/'))
            cholesterol = cholesterol_data.get(observation['date'], 'N/A')  # Default to 'N/A' if no cholesterol data for the date

            cleaned_observation = {
                'date': observation['date'],
                'cholesterol': cholesterol,
                'name': real_name,
                'age': age,
                'BP': f"{bp_systolic}/{bp_diastolic}",
                'Med': observation['medication'],
                'BMI': observation['BMI']
            }
            cleaned_data.append(cleaned_observation)
    return cleaned_data

url = 'https://github.com/Ekanem-obo/Disease-Data-Management-and-Analysis/blob/main/dataset/raw/patients_data.json'
response = requests.get(url)
patients_data = response.json()

cleaned_dataset = clean_data_for_chart(patients_data)

cleaned_file_path = 'C:\\Users\\ekane\\Documents\\Visual Studio 2017\\My_Projects\\3rdSemester\\ICM\\webApp\\dataset\\cleaned\\cleaned_patients_data.json'

with open(cleaned_file_path, 'w', encoding='utf-8') as file:
    json.dump(cleaned_dataset, file, indent=4, ensure_ascii=False)

print(f"Cleaned data saved to {cleaned_file_path}")

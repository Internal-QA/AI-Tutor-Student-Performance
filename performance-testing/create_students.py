import requests
import random
import csv
import json
import os
from datetime import datetime

def load_config():
    config = {}
    config_file = "test_config.properties"
    
    if not os.path.exists(config_file):
        print(f"Config file not found: {config_file}")
        exit(1)
    
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key] = value
    
    return config

def generate_email():
    random_num = random.randint(1000, 9999)
    timestamp = int(datetime.now().timestamp())
    return f"student{random_num}_{timestamp}@test.com"

def generate_name():
    first_names = ["John", "Jane", "Mike", "Sarah", "David", "Emily", "Chris", "Lisa", "Alex", "Maria", 
                   "James", "Anna", "Robert", "Emma", "William", "Olivia", "Daniel", "Sophia", "Matthew", "Isabella"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee"]
    
    first = random.choice(first_names)
    last = random.choice(last_names)
    return f"{first} {last}"

def create_student(api_url, student_data, session):
    try:
        response = session.post(api_url, json=student_data, timeout=30)
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return 0, str(e)

def main():
    # Load configuration
    config = load_config()
    
    api_url = config['API_BASE_URL'] + config['API_ENDPOINT']
    total_students = int(config['TOTAL_STUDENTS'])
    
    print(f"Creating {total_students} students...")
    print(f"API URL: {api_url}")
    

    
    # Files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/students_{timestamp}.log"
    credentials_file = "student_credentials.csv"
    
    success = 0
    failed = 0
    
    # Create credentials file with just email and password
    with open(credentials_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['email', 'password'])
    
    # Create session for connection reuse
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    
    # Create students
    for i in range(1, total_students + 1):
        email = generate_email()
        name = generate_name()
        
        print(f"[{i}/{total_students}] {name} ({email})")
        
        student_data = {
            "email": email,
            "full_name": name,
            "program_id": config['PROGRAM_ID'],
            "cohort_id": config['COHORT_ID'],
            "academic_year_id": config['ACADEMIC_YEAR_ID'],
            "password": config['DEFAULT_PASSWORD']
        }
        
        status_code, response_text = create_student(api_url, student_data, session)
        
        # Log to file
        with open(log_file, 'a') as f:
            f.write(f"[{i}] {datetime.now()} - {email} - {name} - HTTP:{status_code}\n")
            f.write(f"[{i}] Response: {response_text}\n")
        
        if 200 <= status_code < 300:
            print("  Created successfully")
            success += 1
            
            # Save credentials to file
            with open(credentials_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([email, config['DEFAULT_PASSWORD']])
        else:
            print(f"  Failed (HTTP {status_code})")
            failed += 1
    
    print(f"Completed: {success} created, {failed} failed")
    print(f"Log: {log_file}")
    print(f"Student credentials saved: {credentials_file}")

if __name__ == "__main__":
    main() 
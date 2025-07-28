#!/usr/bin/env python3

import csv
import os
import random

def load_student_credentials():
    """Load all student credentials from the saved file"""
    credentials_file = "student_credentials.csv"
    
    if not os.path.exists(credentials_file):
        print(f"Credentials file not found: {credentials_file}")
        print("Please run create_students.py first to create students")
        return []
    
    credentials = []
    with open(credentials_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            credentials.append({
                'email': row['email'],
                'password': row['password']
            })
    
    return credentials

def get_random_student():
    """Get a random student credential for testing"""
    credentials = load_student_credentials()
    if not credentials:
        return None
    return random.choice(credentials)

def get_student_batch(count=10):
    """Get a batch of student credentials for testing"""
    credentials = load_student_credentials()
    if not credentials:
        return []
    
    # Return up to 'count' credentials, or all if less available
    return credentials[:min(count, len(credentials))]

if __name__ == "__main__":
    # Example usage
    print("Loading student credentials...")
    
    credentials = load_student_credentials()
    print(f"Found {len(credentials)} student accounts")
    
    if credentials:
        print("\nExample credentials:")
        for i, cred in enumerate(credentials[:3], 1):
            print(f"  {i}. Email: {cred['email']}, Password: {cred['password']}")
        
        if len(credentials) > 3:
            print(f"  ... and {len(credentials) - 3} more")
        
        print(f"\nRandom student: {get_random_student()}") 
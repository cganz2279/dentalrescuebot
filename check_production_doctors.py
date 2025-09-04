#!/usr/bin/env python3
"""
Check what doctors/dentists exist in production via the old /practice/doctors endpoint
"""

import requests
import json

PRODUCTION_BASE_URL = "https://dentist-portal-3.emergent.host/api"
USER_EMAIL = "cganz2279@gmail.com"
USER_PASSWORD = "password123"

def get_jwt_token():
    """Get JWT token for authenticated requests"""
    try:
        login_data = {
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        }
        
        response = requests.post(
            f"{PRODUCTION_BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('token')
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def check_production_doctors():
    """Check what doctors exist in production"""
    jwt_token = get_jwt_token()
    if not jwt_token:
        print("❌ Failed to get JWT token")
        return
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Check old doctors endpoint
        response = requests.get(
            f"{PRODUCTION_BASE_URL}/practice/doctors",
            headers=headers,
            timeout=10
        )
        
        print("PRODUCTION DOCTORS CHECK")
        print("=" * 40)
        print(f"Endpoint: GET /practice/doctors")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            doctors = data.get('data', [])
            
            print(f"Found {len(doctors)} doctors in production:")
            for i, doctor in enumerate(doctors, 1):
                print(f"  {i}. {doctor}")
            
            # Check if John Smith exists
            john_smith_exists = any('John Smith' in str(doctor) for doctor in doctors)
            print(f"\nDr. John Smith exists: {john_smith_exists}")
            
            if not john_smith_exists:
                print("\n🔍 ISSUE IDENTIFIED:")
                print("Dr. John Smith is NOT in the production doctors list!")
                print("This explains why he doesn't appear in the frontend dropdown.")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error checking doctors: {e}")

if __name__ == "__main__":
    check_production_doctors()
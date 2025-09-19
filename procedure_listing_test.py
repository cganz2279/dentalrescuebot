#!/usr/bin/env python3
"""
Backend Test for Procedure Listing - Review Request
Testing GET /api/public/procedures endpoint to list all procedures
"""

import requests
import json
from typing import Dict, Any, List

# Backend URL from review request
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

# Test credentials from review request
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

def authenticate() -> str:
    """Authenticate and get JWT token"""
    print("🔐 Authenticating with backend...")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token") or data.get("token")
            if token:
                print("✅ Authentication successful")
                return token
            else:
                print("❌ No access token in response")
                print(f"Response: {data}")
                return None
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def test_public_procedures_endpoint(token: str = None) -> Dict[str, Any]:
    """Test GET /api/public/procedures endpoint"""
    print("\n📋 Testing GET /api/public/procedures endpoint...")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(f"{BACKEND_URL}/public/procedures", headers=headers)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Public procedures endpoint working")
            return data
        else:
            print(f"❌ Public procedures endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Public procedures endpoint error: {str(e)}")
        return None

def test_procedures_endpoint(token: str) -> Dict[str, Any]:
    """Test GET /api/procedures endpoint (authenticated)"""
    print("\n📋 Testing GET /api/procedures endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/procedures", headers=headers)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Procedures endpoint working")
            return data
        else:
            print(f"❌ Procedures endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Procedures endpoint error: {str(e)}")
        return None

def analyze_procedures_data(data: Dict[str, Any]) -> None:
    """Analyze and display procedures data"""
    if not data:
        print("❌ No data to analyze")
        return
    
    print("\n📊 PROCEDURE DATA ANALYSIS")
    print("=" * 50)
    
    # Check if data has success field and data array
    if isinstance(data, dict) and "data" in data:
        procedures = data["data"]
    elif isinstance(data, list):
        procedures = data
    else:
        print(f"❌ Unexpected data format: {type(data)}")
        return
    
    if not isinstance(procedures, list):
        print(f"❌ Procedures data is not a list: {type(procedures)}")
        return
    
    total_count = len(procedures)
    print(f"📈 TOTAL PROCEDURES COUNT: {total_count}")
    
    if total_count == 0:
        print("❌ No procedures found in database")
        return
    
    print(f"\n📋 FIRST 20 PROCEDURE NAMES AND IDs:")
    print("-" * 60)
    
    for i, procedure in enumerate(procedures[:20]):
        if isinstance(procedure, dict):
            proc_id = procedure.get("id", "N/A")
            proc_name = procedure.get("name", "N/A")
            specialty = procedure.get("specialtyName", procedure.get("specialty", "N/A"))
            print(f"{i+1:2d}. ID: {proc_id}")
            print(f"    Name: {proc_name}")
            print(f"    Specialty: {specialty}")
            print()
        else:
            print(f"{i+1:2d}. Invalid procedure format: {procedure}")
    
    if total_count > 20:
        print(f"... and {total_count - 20} more procedures")
    
    # Show specialty breakdown
    print(f"\n🏥 SPECIALTY BREAKDOWN:")
    print("-" * 30)
    specialty_counts = {}
    for procedure in procedures:
        if isinstance(procedure, dict):
            specialty = procedure.get("specialtyName", procedure.get("specialty", "Unknown"))
            specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1
    
    for specialty, count in sorted(specialty_counts.items()):
        print(f"{specialty}: {count} procedures")

def main():
    """Main test function"""
    print("🎯 BACKEND PROCEDURE LISTING TEST")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test credentials: {TEST_EMAIL}")
    print()
    
    # Step 1: Authenticate
    token = authenticate()
    
    # Step 2: Test public procedures endpoint (no auth required)
    print("\n" + "="*50)
    print("TESTING PUBLIC PROCEDURES ENDPOINT")
    print("="*50)
    
    public_data = test_public_procedures_endpoint()
    if public_data:
        print("\n✅ PUBLIC PROCEDURES ENDPOINT SUCCESS")
        analyze_procedures_data(public_data)
    else:
        print("\n❌ PUBLIC PROCEDURES ENDPOINT FAILED")
    
    # Step 3: Test authenticated procedures endpoint if we have token
    if token:
        print("\n" + "="*50)
        print("TESTING AUTHENTICATED PROCEDURES ENDPOINT")
        print("="*50)
        
        auth_data = test_procedures_endpoint(token)
        if auth_data:
            print("\n✅ AUTHENTICATED PROCEDURES ENDPOINT SUCCESS")
            analyze_procedures_data(auth_data)
        else:
            print("\n❌ AUTHENTICATED PROCEDURES ENDPOINT FAILED")
    else:
        print("\n⚠️ Skipping authenticated endpoint test (no token)")
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    if public_data or (token and auth_data):
        print("✅ PROCEDURE LISTING TEST COMPLETED SUCCESSFULLY")
        print("✅ Backend has procedures data available")
        if public_data:
            procedures = public_data.get("data", public_data) if isinstance(public_data, dict) else public_data
            if isinstance(procedures, list):
                print(f"✅ Total procedures found: {len(procedures)}")
        print("✅ User can now extract content from original PDFs and update procedures")
    else:
        print("❌ PROCEDURE LISTING TEST FAILED")
        print("❌ Unable to retrieve procedures list")
        print("❌ Check backend connectivity and authentication")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Search for any sedation-related procedures in the database
"""

import requests
import json

# Backend URL from review request
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

def authenticate():
    """Authenticate with the backend and return JWT token"""
    print("🔐 Authenticating with backend...")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ Authentication successful")
            return token
        else:
            print(f"❌ Authentication failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def search_sedation_procedures(token):
    """Search for sedation-related procedures"""
    print("\n🔍 Searching for sedation-related procedures...")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        # Search using the search endpoint
        response = requests.get(f"{BACKEND_URL}/procedures/search?q=sedation", headers=headers)
        print(f"Search API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                procedures = data.get('data', [])
                print(f"✅ Found {len(procedures)} procedures matching 'sedation'")
                
                for procedure in procedures:
                    print(f"   - {procedure.get('name')} (id: {procedure.get('id')}, specialty: {procedure.get('specialtyName')})")
                
                return procedures
            else:
                print(f"❌ Search returned success=false: {data}")
                return []
        else:
            print(f"❌ Search API error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error searching procedures: {str(e)}")
        return []

def get_all_procedures(token):
    """Get all procedures and search for sedation manually"""
    print("\n📋 Getting all procedures to search for sedation...")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        response = requests.get(f"{BACKEND_URL}/procedures", headers=headers)
        print(f"All procedures API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                procedures = data.get('data', [])
                print(f"✅ Found {len(procedures)} total procedures")
                
                # Search for sedation in names and overview
                sedation_procedures = []
                for procedure in procedures:
                    name = procedure.get('name', '').lower()
                    overview = procedure.get('overview', '').lower()
                    
                    if 'sedation' in name or 'sedation' in overview:
                        sedation_procedures.append(procedure)
                
                print(f"🔍 Found {len(sedation_procedures)} procedures containing 'sedation':")
                for procedure in sedation_procedures:
                    print(f"   - {procedure.get('name')} (id: {procedure.get('id')}, specialty: {procedure.get('specialtyName')})")
                    if 'sedation' in procedure.get('overview', '').lower():
                        print(f"     Overview mentions sedation: {procedure.get('overview', '')[:100]}...")
                
                return sedation_procedures
            else:
                print(f"❌ API returned success=false: {data}")
                return []
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting all procedures: {str(e)}")
        return []

def main():
    """Main test execution"""
    print("🔍 SEDATION PROCEDURE SEARCH TEST")
    print("=" * 40)
    
    # Authenticate
    token = authenticate()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Search using search endpoint
    search_results = search_sedation_procedures(token)
    
    # Search through all procedures
    all_results = get_all_procedures(token)
    
    print("\n" + "=" * 40)
    print("🎯 SUMMARY")
    print("=" * 40)
    print(f"Search endpoint results: {len(search_results)} procedures")
    print(f"Manual search results: {len(all_results)} procedures")
    
    if len(search_results) == 0 and len(all_results) == 0:
        print("❌ NO sedation-related procedures found in database")
        print("   This confirms IV Sedation was not successfully added")
    else:
        print("✅ Found sedation-related procedures")

if __name__ == "__main__":
    main()
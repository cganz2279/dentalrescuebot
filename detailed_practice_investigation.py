#!/usr/bin/env python3
"""
DETAILED PRACTICE DATA INVESTIGATION
Comprehensive check of all practice-related endpoints and raw database data
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend configuration
BACKEND_URL = "https://postop-care.preview.emergentagent.com/api"

def authenticate():
    """Get JWT token for authenticated requests"""
    session = requests.Session()
    
    response = session.post(
        f"{BACKEND_URL}/auth/login",
        json={
            "email": "cganz2279@gmail.com",
            "password": "password123"
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if "token" in data:
            jwt_token = data["token"]
            session.headers.update({
                "Authorization": f"Bearer {jwt_token}"
            })
            return session, data
    
    return None, None

def check_all_practice_endpoints():
    """Check all possible practice-related endpoints"""
    print("🔍 COMPREHENSIVE PRACTICE ENDPOINT INVESTIGATION")
    print("=" * 70)
    
    session, login_data = authenticate()
    if not session:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    print(f"   User: {login_data.get('user', {}).get('email')}")
    print(f"   Practice ID: {login_data.get('user', {}).get('practiceId')}")
    print()
    
    # List of endpoints to test
    endpoints_to_test = [
        "/practice/dashboard",
        "/practice",
        "/practice/settings", 
        "/practice/profile",
        "/practice/info",
        "/practice/details",
        "/practice/data",
        "/practice/config",
        "/practice/configuration"
    ]
    
    results = {}
    
    for endpoint in endpoints_to_test:
        print(f"🔍 Testing {endpoint}...")
        try:
            response = session.get(f"{BACKEND_URL}{endpoint}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract practice data
                if data.get("success"):
                    practice_data = data.get("data", {})
                    if "practice" in practice_data:
                        practice_obj = practice_data["practice"]
                    else:
                        practice_obj = practice_data
                else:
                    practice_obj = data
                
                # Check for office hours and emergency contact
                office_hours = practice_obj.get("officeHours") if isinstance(practice_obj, dict) else None
                emergency_contact = practice_obj.get("emergencyContact") if isinstance(practice_obj, dict) else None
                
                results[endpoint] = {
                    "status": "SUCCESS",
                    "status_code": 200,
                    "has_office_hours": office_hours is not None,
                    "has_emergency_contact": emergency_contact is not None,
                    "office_hours": office_hours,
                    "emergency_contact": emergency_contact,
                    "available_fields": list(practice_obj.keys()) if isinstance(practice_obj, dict) else "Not a dict"
                }
                
                print(f"   ✅ SUCCESS - Office Hours: {'✅' if office_hours else '❌'}, Emergency Contact: {'✅' if emergency_contact else '❌'}")
                if office_hours:
                    print(f"      Office Hours: '{office_hours}'")
                if emergency_contact:
                    print(f"      Emergency Contact: '{emergency_contact}'")
                
            elif response.status_code == 404:
                results[endpoint] = {
                    "status": "NOT_FOUND",
                    "status_code": 404
                }
                print(f"   ℹ️  NOT FOUND (404)")
                
            elif response.status_code == 403:
                results[endpoint] = {
                    "status": "FORBIDDEN",
                    "status_code": 403
                }
                print(f"   🚫 FORBIDDEN (403)")
                
            else:
                results[endpoint] = {
                    "status": "ERROR",
                    "status_code": response.status_code,
                    "error": response.text
                }
                print(f"   ❌ ERROR ({response.status_code})")
                
        except Exception as e:
            results[endpoint] = {
                "status": "EXCEPTION",
                "error": str(e)
            }
            print(f"   ❌ EXCEPTION: {str(e)}")
        
        print()
    
    # Summary
    print("=" * 70)
    print("📊 ENDPOINT INVESTIGATION SUMMARY")
    print("=" * 70)
    
    working_endpoints = []
    endpoints_with_data = []
    
    for endpoint, result in results.items():
        status_icon = "✅" if result["status"] == "SUCCESS" else "❌" if result["status"] == "ERROR" else "ℹ️"
        print(f"{status_icon} {endpoint}: {result['status']}")
        
        if result["status"] == "SUCCESS":
            working_endpoints.append(endpoint)
            if result.get("has_office_hours") and result.get("has_emergency_contact"):
                endpoints_with_data.append(endpoint)
                print(f"   📋 HAS COMPLETE PRACTICE DATA")
            elif result.get("has_office_hours") or result.get("has_emergency_contact"):
                print(f"   📋 HAS PARTIAL PRACTICE DATA")
            else:
                print(f"   📋 NO PRACTICE DATA")
    
    print()
    print("🎯 KEY FINDINGS:")
    print(f"   Working Endpoints: {len(working_endpoints)}")
    print(f"   Endpoints with Complete Data: {len(endpoints_with_data)}")
    
    if endpoints_with_data:
        print(f"   ✅ RECOMMENDED ENDPOINT: {endpoints_with_data[0]}")
        best_endpoint = endpoints_with_data[0]
        best_result = results[best_endpoint]
        print(f"      Office Hours: '{best_result['office_hours']}'")
        print(f"      Emergency Contact: '{best_result['emergency_contact']}'")
    else:
        print(f"   ❌ NO ENDPOINTS WITH COMPLETE PRACTICE DATA FOUND")
    
    return results

def check_raw_database_structure():
    """Check what the raw database structure looks like"""
    print("🗄️ RAW DATABASE STRUCTURE INVESTIGATION")
    print("=" * 70)
    
    session, login_data = authenticate()
    if not session:
        print("❌ Authentication failed")
        return
    
    # Get the most detailed response we can find
    response = session.get(f"{BACKEND_URL}/practice/dashboard")
    
    if response.status_code == 200:
        data = response.json()
        
        print("📋 COMPLETE DASHBOARD RESPONSE STRUCTURE:")
        print(json.dumps(data, indent=2))
        
        # Extract practice object
        practice_data = data.get("data", {}).get("practice", {})
        
        print("\n🔍 PRACTICE OBJECT FIELD ANALYSIS:")
        for field, value in practice_data.items():
            value_type = type(value).__name__
            is_null = value is None
            is_empty = value == "" if isinstance(value, str) else False
            
            status = "❌ NULL" if is_null else "⚠️ EMPTY" if is_empty else "✅ POPULATED"
            print(f"   {status} {field}: {value_type} = {repr(value)}")
        
        print(f"\n📊 FIELD STATISTICS:")
        total_fields = len(practice_data)
        null_fields = sum(1 for v in practice_data.values() if v is None)
        empty_fields = sum(1 for v in practice_data.values() if v == "")
        populated_fields = total_fields - null_fields - empty_fields
        
        print(f"   Total Fields: {total_fields}")
        print(f"   Populated Fields: {populated_fields}")
        print(f"   NULL Fields: {null_fields}")
        print(f"   Empty Fields: {empty_fields}")
        
        # Specific check for the fields we care about
        office_hours = practice_data.get("officeHours")
        emergency_contact = practice_data.get("emergencyContact")
        
        print(f"\n🎯 CRITICAL FIELDS STATUS:")
        print(f"   Office Hours: {'✅ POPULATED' if office_hours else '❌ NULL/EMPTY'}")
        print(f"   Emergency Contact: {'✅ POPULATED' if emergency_contact else '❌ NULL/EMPTY'}")
        
        if office_hours and emergency_contact:
            print(f"\n🎉 CONCLUSION: Practice data IS available in database!")
            print(f"   Office Hours: '{office_hours}'")
            print(f"   Emergency Contact: '{emergency_contact}'")
        else:
            print(f"\n❌ CONCLUSION: Practice data is NOT properly configured in database!")

if __name__ == "__main__":
    print("🚨 URGENT PRACTICE DATA INVESTIGATION")
    print("QUESTION: Are Office Hours and Emergency Contact fields populated in database?")
    print("USER REPORT: API returning NULL values despite Practice Settings configuration")
    print()
    
    # Part 1: Check all possible endpoints
    endpoint_results = check_all_practice_endpoints()
    
    print()
    
    # Part 2: Check raw database structure
    check_raw_database_structure()
    
    print("\n" + "=" * 70)
    print("🎯 FINAL ANSWER TO USER'S QUESTION")
    print("=" * 70)
    
    # Determine final answer based on investigation
    session, _ = authenticate()
    if session:
        response = session.get(f"{BACKEND_URL}/practice/dashboard")
        if response.status_code == 200:
            data = response.json()
            practice_data = data.get("data", {}).get("practice", {})
            office_hours = practice_data.get("officeHours")
            emergency_contact = practice_data.get("emergencyContact")
            
            if office_hours and emergency_contact:
                print("✅ FIELDS ARE POPULATED IN DATABASE:")
                print(f"   Office Hours: '{office_hours}'")
                print(f"   Emergency Contact: '{emergency_contact}'")
                print("\n🔧 ISSUE IS IN FRONTEND DATA FLOW:")
                print("   - Backend has the data")
                print("   - Frontend is not retrieving/using it properly")
                print("   - PDF generator needs to call /api/practice/dashboard")
            else:
                print("❌ FIELDS ARE NULL IN DATABASE:")
                print("   - User needs to configure these fields in Practice Settings")
                print("   - The Practice Settings page may not be saving data properly")
        else:
            print("❌ UNABLE TO DETERMINE - API call failed")
    else:
        print("❌ UNABLE TO DETERMINE - Authentication failed")
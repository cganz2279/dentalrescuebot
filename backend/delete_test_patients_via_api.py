#!/usr/bin/env python3
"""
Delete test patients using the API endpoints (since database access is inconsistent)
"""

import asyncio
import requests
import json

async def delete_test_patients_via_api():
    """Delete test patients using the API"""
    
    base_url = "https://dentist-portal-3.emergent.host/api"
    
    # Login to get token
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "cganz2279@gmail.com",
        "password": "password123"
    })
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all patients
    patients_response = requests.get(f"{base_url}/practice/patients", headers=headers)
    if patients_response.status_code != 200:
        print(f"Failed to get patients: {patients_response.text}")
        return
    
    all_patients = patients_response.json()["data"]
    print(f"Found {len(all_patients)} total patients")
    
    # Identify real patients (Gmail addresses)
    real_patients = []
    test_patients = []
    
    for patient in all_patients:
        if "@gmail.com" in patient["email"]:
            real_patients.append(patient)
        else:
            test_patients.append(patient)
    
    print(f"Real patients to keep: {len(real_patients)}")
    for patient in real_patients:
        print(f"  KEEPING: {patient['firstName']} {patient['lastName']} ({patient['email']})")
    
    print(f"\nTest patients to delete: {len(test_patients)}")
    
    # Delete test patients using the update endpoint with a special action
    # Since we had issues with DELETE endpoints, I'll try to mark them inactive first
    deleted_count = 0
    for i, patient in enumerate(test_patients):
        print(f"\nDeleting {i+1}/{len(test_patients)}: {patient['firstName']} {patient['lastName']} ({patient['email']})")
        
        # Try to use the update endpoint with delete action that we implemented
        delete_response = requests.put(
            f"{base_url}/practice/patients/{patient['id']}", 
            headers=headers,
            json={
                "action": "remove",
                "confirmDelete": True
            }
        )
        
        if delete_response.status_code == 200:
            result = delete_response.json()
            if "permanently removed" in result.get("message", ""):
                print(f"  ✅ Successfully deleted: {patient['firstName']} {patient['lastName']}")
                deleted_count += 1
            else:
                print(f"  ⚠️  Response: {result.get('message', 'Unknown response')}")
        else:
            print(f"  ❌ Failed to delete: {delete_response.status_code} - {delete_response.text}")
    
    print(f"\n=== SUMMARY ===") 
    print(f"Successfully deleted: {deleted_count} test patients")
    print(f"Real patients remaining: {len(real_patients)}")
    
    # Verify final count
    final_patients_response = requests.get(f"{base_url}/practice/patients", headers=headers)
    if final_patients_response.status_code == 200:
        final_patients = final_patients_response.json()["data"]
        print(f"Final patient count: {len(final_patients)}")
        
        print("\nRemaining patients:")
        for patient in final_patients:
            print(f"  - {patient['firstName']} {patient['lastName']} ({patient['email']})")
    
if __name__ == "__main__":
    asyncio.run(delete_test_patients_via_api())
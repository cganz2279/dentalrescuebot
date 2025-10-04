#!/usr/bin/env python3
"""
Quick test to check if patients exist for follow-up email testing
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
TEST_CREDENTIALS = {
    "email": "cganz2279@gmail.com",
    "password": "password123"
}

async def check_patients():
    async with aiohttp.ClientSession() as session:
        # Authenticate
        url = f"{BACKEND_URL}/api/auth/login"
        login_data = {
            "email": TEST_CREDENTIALS["email"],
            "password": TEST_CREDENTIALS["password"]
        }
        
        async with session.post(url, json=login_data) as response:
            if response.status == 200:
                response_data = await response.json()
                auth_token = response_data.get("access_token") or response_data.get("token")
                practice_id = response_data.get("user", {}).get("practiceId")
                
                if auth_token and practice_id:
                    print(f"✅ Authenticated successfully")
                    
                    # Check patients
                    url = f"{BACKEND_URL}/api/practice/patients"
                    headers = {"Authorization": f"Bearer {auth_token}"}
                    
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            patients_data = await response.json()
                            patients = patients_data.get("patients", [])
                            print(f"📊 Found {len(patients)} patients")
                            
                            for i, patient in enumerate(patients[:3]):  # Show first 3
                                print(f"   Patient {i+1}: {patient.get('firstName', 'N/A')} {patient.get('lastName', 'N/A')} ({patient.get('email', 'N/A')})")
                            
                            # Check procedures
                            url = f"{BACKEND_URL}/api/practice/procedures"
                            async with session.get(url, headers=headers) as response:
                                if response.status == 200:
                                    procedures_data = await response.json()
                                    recent_procedures = procedures_data.get("recentProcedures", [])
                                    print(f"📋 Found {len(recent_procedures)} recent procedures")
                                    
                                    status_counts = {}
                                    for proc in recent_procedures:
                                        status = proc.get("status", "unknown")
                                        status_counts[status] = status_counts.get(status, 0) + 1
                                    
                                    print("📈 Procedure status breakdown:")
                                    for status, count in status_counts.items():
                                        print(f"   {status}: {count}")
                                        
                                    # Show some examples
                                    delivered_procedures = [p for p in recent_procedures if p.get("status") == "delivered"]
                                    second_procedures = [p for p in recent_procedures if p.get("status") == "second"]
                                    
                                    if delivered_procedures:
                                        print(f"✅ Found {len(delivered_procedures)} delivered procedures (ready for follow-up)")
                                    if second_procedures:
                                        print(f"✅ Found {len(second_procedures)} second-status procedures (follow-up already sent)")
                                        
                                else:
                                    print(f"❌ Failed to get procedures: {response.status}")
                        else:
                            print(f"❌ Failed to get patients: {response.status}")
                else:
                    print("❌ Authentication failed")
            else:
                print(f"❌ Login failed: {response.status}")

if __name__ == "__main__":
    asyncio.run(check_patients())
#!/usr/bin/env python3
"""
MULTI-ENVIRONMENT SPECIALTY CORRUPTION CHECK
Testing both backend environments to identify discrepancies
"""

import requests
import json
from datetime import datetime

# Test both environments
ENVIRONMENTS = [
    {
        "name": "User Reported URL",
        "url": "https://dentist-portal-3.emergent.host/api"
    },
    {
        "name": "Frontend .env URL", 
        "url": "https://dentiportal.preview.emergentagent.com/api"
    }
]

TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

def test_environment(env_name, backend_url):
    """Test a specific environment for specialty corruption"""
    print(f"\n🌐 TESTING ENVIRONMENT: {env_name}")
    print(f"URL: {backend_url}")
    print("=" * 80)
    
    # Test authentication first
    print("🔐 Testing authentication...")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        auth_response = requests.post(f"{backend_url}/auth/login", json=login_data)
        print(f"Auth status: {auth_response.status_code}")
        
        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.text}")
            return None
        else:
            print("✅ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None
    
    # Test specialties
    print("\n📊 Testing specialties...")
    try:
        response = requests.get(f"{backend_url}/specialties")
        print(f"Specialties status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                specialties = data.get('data', [])
                print(f"Found {len(specialties)} specialties:")
                
                total_procedures = 0
                general_dentistry_count = 0
                
                for specialty in specialties:
                    name = specialty.get('name', 'Unknown')
                    count = specialty.get('procedureCount', 0)
                    print(f"  • {name}: {count} procedures")
                    total_procedures += count
                    
                    if name == "General Dentistry":
                        general_dentistry_count = count
                
                print(f"\nTOTAL: {total_procedures} procedures")
                print(f"GENERAL DENTISTRY: {general_dentistry_count} procedures")
                
                # Check corruption
                corruption_detected = general_dentistry_count >= 81
                if corruption_detected:
                    print("🚨 CORRUPTION DETECTED!")
                else:
                    print("✅ No corruption detected")
                
                return {
                    "total": total_procedures,
                    "general_dentistry": general_dentistry_count,
                    "corrupted": corruption_detected,
                    "specialties": specialties
                }
            else:
                print(f"❌ API error: {data}")
                return None
        else:
            print(f"❌ Failed to get specialties: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_specific_procedures(backend_url):
    """Test specific procedures in an environment"""
    print(f"\n🔍 Testing specific procedures...")
    
    procedures_to_test = [
        {"id": "root-canal-therapy", "expected": "Endodontics"},
        {"id": "dental-implant-placement", "expected": "Oral Surgery"},
        {"id": "tooth-extraction", "expected": "Oral Surgery"},
        {"id": "dental-crown-placement", "expected": "Prosthodontics"}
    ]
    
    results = []
    
    for proc in procedures_to_test:
        try:
            response = requests.get(f"{backend_url}/procedures/{proc['id']}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    procedure = data.get('data', {})
                    name = procedure.get('name', 'Unknown')
                    specialty_name = procedure.get('specialtyName', 'Unknown')
                    
                    is_correct = specialty_name == proc['expected']
                    status = "✅" if is_correct else "❌"
                    
                    print(f"  {status} {name}: {specialty_name} (expected: {proc['expected']})")
                    results.append({
                        "name": name,
                        "actual": specialty_name,
                        "expected": proc['expected'],
                        "correct": is_correct
                    })
                else:
                    print(f"  ❌ {proc['id']}: API error")
            else:
                print(f"  ❌ {proc['id']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {proc['id']}: Error - {str(e)}")
    
    return results

def main():
    """Main test execution"""
    print("🚨 MULTI-ENVIRONMENT SPECIALTY CORRUPTION CHECK")
    print("=" * 80)
    print(f"Timestamp: {datetime.now()}")
    print(f"Test Credentials: {TEST_EMAIL}")
    print("=" * 80)
    
    results = {}
    
    # Test each environment
    for env in ENVIRONMENTS:
        env_result = test_environment(env["name"], env["url"])
        if env_result:
            results[env["name"]] = env_result
            # Test specific procedures for this environment
            proc_results = test_specific_procedures(env["url"])
            results[env["name"]]["procedure_tests"] = proc_results
    
    # Summary comparison
    print("\n" + "=" * 80)
    print("🎯 ENVIRONMENT COMPARISON SUMMARY")
    print("=" * 80)
    
    if len(results) > 1:
        env_names = list(results.keys())
        env1, env2 = env_names[0], env_names[1]
        
        print(f"\n{env1}:")
        if env1 in results:
            r1 = results[env1]
            print(f"  Total procedures: {r1['total']}")
            print(f"  General Dentistry: {r1['general_dentistry']}")
            print(f"  Corrupted: {'YES' if r1['corrupted'] else 'NO'}")
        
        print(f"\n{env2}:")
        if env2 in results:
            r2 = results[env2]
            print(f"  Total procedures: {r2['total']}")
            print(f"  General Dentistry: {r2['general_dentistry']}")
            print(f"  Corrupted: {'YES' if r2['corrupted'] else 'NO'}")
        
        # Check for discrepancies
        if env1 in results and env2 in results:
            if results[env1]['corrupted'] != results[env2]['corrupted']:
                print(f"\n🚨 DISCREPANCY DETECTED!")
                print(f"Different corruption status between environments!")
            elif not results[env1]['corrupted'] and not results[env2]['corrupted']:
                print(f"\n✅ BOTH ENVIRONMENTS CLEAN")
                print(f"No corruption detected in either environment")
            else:
                print(f"\n🚨 BOTH ENVIRONMENTS CORRUPTED")
    
    # Final conclusion
    print("\n" + "=" * 80)
    print("🎯 FINAL CONCLUSION")
    print("=" * 80)
    
    any_corruption = any(r.get('corrupted', False) for r in results.values())
    
    if any_corruption:
        print("🚨 SPECIALTY CORRUPTION CONFIRMED")
        print("🚨 User's report is accurate - immediate action required")
    else:
        print("✅ NO SPECIALTY CORRUPTION FOUND")
        print("✅ User's report may be outdated or environment-specific")
        print("✅ All procedures appear to have correct specialty assignments")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
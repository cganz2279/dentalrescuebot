#!/usr/bin/env python3
"""
CRITICAL DATA CORRUPTION TEST - FOCUSED TEST
Testing the actual corrupted account: cganz2279@gmail.com

CONFIRMED CORRUPTION:
- Account: cganz2279@gmail.com / password123
- Practice Name: "Cary Ganz DDS PC" (WRONG - should be "The Dental Spa at Garden City")
- Practice ID: 0b08d321-ae1a-43d5-b69a-4850cfa3a9fc
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Corrupted account credentials
CORRUPTED_EMAIL = "cganz2279@gmail.com"
CORRUPTED_PASSWORD = "password123"
CORRECT_PRACTICE_NAME = "The Dental Spa at Garden City"
WRONG_PRACTICE_NAME = "Cary Ganz DDS PC"

def test_data_corruption():
    """Test and document the confirmed data corruption"""
    print("🚨 CRITICAL DATA CORRUPTION TEST")
    print("=" * 60)
    print(f"Testing Account: {CORRUPTED_EMAIL}")
    print(f"Expected Practice: {CORRECT_PRACTICE_NAME}")
    print(f"Current Wrong Practice: {WRONG_PRACTICE_NAME}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("=" * 60)
    print()
    
    try:
        # Test login with corrupted account
        print("🔍 Testing login with corrupted account...")
        login_response = requests.post(f"{API_BASE}/auth/login", json={
            "email": CORRUPTED_EMAIL,
            "password": CORRUPTED_PASSWORD
        }, timeout=30)
        
        if login_response.status_code == 200:
            print("✅ LOGIN SUCCESSFUL")
            login_data = login_response.json()
            user_data = login_data.get('user', {})
            practice_data = login_data.get('practice', {})
            
            print(f"\n📋 ACCOUNT DATA:")
            print(f"   User ID: {user_data.get('id', '')}")
            print(f"   User Name: {user_data.get('firstName', '')} {user_data.get('lastName', '')}")
            print(f"   User Email: {user_data.get('email', '')}")
            print(f"   Practice ID: {practice_data.get('id', '')}")
            print(f"   Practice Name: {practice_data.get('name', '')}")
            print(f"   Practice Owner: {practice_data.get('ownerName', '')}")
            print(f"   Practice Email: {practice_data.get('email', '')}")
            print(f"   Practice Phone: {practice_data.get('phone', '')}")
            
            # Analyze corruption
            current_name = f"{user_data.get('firstName', '')} {user_data.get('lastName', '')}".strip()
            current_practice = practice_data.get('name', '')
            
            print(f"\n🔍 CORRUPTION ANALYSIS:")
            corruption_found = False
            
            # Check name corruption
            if "Michael Brown" in current_name:
                print(f"   🚨 NAME CORRUPTION: '{current_name}' contains 'Michael Brown'")
                corruption_found = True
            else:
                print(f"   ✅ Name appears correct: '{current_name}'")
            
            # Check practice corruption
            if current_practice == WRONG_PRACTICE_NAME:
                print(f"   🚨 PRACTICE CORRUPTION CONFIRMED:")
                print(f"      Current: '{current_practice}'")
                print(f"      Should be: '{CORRECT_PRACTICE_NAME}'")
                corruption_found = True
            else:
                print(f"   ✅ Practice name: '{current_practice}'")
            
            # Summary
            print(f"\n📊 CORRUPTION SUMMARY:")
            if corruption_found:
                print("   🚨 DATA CORRUPTION CONFIRMED")
                print("   🎯 IMMEDIATE ACTION REQUIRED:")
                print(f"      1. Update practice name from '{WRONG_PRACTICE_NAME}' to '{CORRECT_PRACTICE_NAME}'")
                print(f"      2. Verify practice phone number is '516-236-1083'")
                print(f"      3. Test login returns correct data after fix")
                print(f"      4. Send password reset email to customer")
                return False
            else:
                print("   ✅ No corruption detected")
                return True
                
        else:
            print(f"❌ LOGIN FAILED: Status {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TEST ERROR: {str(e)}")
        return False

def test_password_reset():
    """Test password reset functionality"""
    print(f"\n🔍 Testing password reset for {CORRUPTED_EMAIL}...")
    try:
        response = requests.post(f"{API_BASE}/auth/forgot-password", json={
            "email": CORRUPTED_EMAIL,
            "recovery_method": "email"
        }, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Password reset available: {data.get('sent_methods', [])}")
            return True
        else:
            print(f"❌ Password reset failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Password reset error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting critical data corruption test...\n")
    
    # Run tests
    corruption_test_passed = test_data_corruption()
    password_reset_passed = test_password_reset()
    
    print("\n" + "=" * 60)
    print("🏁 FINAL RESULTS")
    print("=" * 60)
    
    if not corruption_test_passed:
        print("🚨 CRITICAL: Data corruption confirmed for cganz2279@gmail.com")
        print("   Practice name is wrong and needs immediate correction")
        print("   Customer has paid real money and deserves correct account data")
        sys.exit(1)
    else:
        print("✅ No data corruption detected")
        
    if password_reset_passed:
        print("✅ Password reset functionality working")
    else:
        print("❌ Password reset issues detected")
    
    print("\nTest completed.")
    sys.exit(0 if corruption_test_passed and password_reset_passed else 1)
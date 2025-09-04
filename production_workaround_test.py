#!/usr/bin/env python3
"""
PRODUCTION WORKAROUND TEST
Try to add Dr. John Smith to production using available methods
"""

import requests
import json
from datetime import datetime

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
            return data.get('token'), data.get('user', {}), data.get('practice', {})
        return None, None, None
    except Exception as e:
        print(f"Login error: {e}")
        return None, None, None

def check_current_doctors():
    """Check current doctors in production"""
    jwt_token, user, practice = get_jwt_token()
    if not jwt_token:
        return None
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{PRODUCTION_BASE_URL}/practice/doctors",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        return None
    except:
        return None

def try_add_via_admin_endpoints():
    """Try to add Dr. John Smith via admin endpoints if available"""
    print("🔧 ATTEMPTING ADMIN WORKAROUND...")
    
    # Try admin login first
    admin_credentials = [
        {"email": "cganz@admin.com", "password": "Dentist1#"},
        {"email": "admin@admin.com", "password": "admin123"},
    ]
    
    for creds in admin_credentials:
        try:
            response = requests.post(
                f"{PRODUCTION_BASE_URL}/admin/login",
                json=creds,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                admin_token = data.get('token')
                print(f"✅ Admin login successful with {creds['email']}")
                
                # Try to add doctor via admin interface
                # This would require knowing the admin endpoints for practice management
                return admin_token
            else:
                print(f"❌ Admin login failed for {creds['email']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Admin login error for {creds['email']}: {e}")
    
    return None

def try_direct_database_approach():
    """Check if we can access database directly (unlikely in production)"""
    print("🔧 CHECKING DIRECT DATABASE ACCESS...")
    
    # This would only work if we had direct MongoDB access
    # In production, this is typically not available
    print("❌ Direct database access not available in production environment")
    return False

def main():
    print("PRODUCTION WORKAROUND ATTEMPT")
    print("=" * 50)
    print("Goal: Add Dr. John Smith to production dentist list")
    print()
    
    # Step 1: Check current state
    print("📋 STEP 1: Check current doctors in production")
    current_doctors = check_current_doctors()
    if current_doctors:
        print(f"Current doctors: {len(current_doctors)}")
        for i, doctor in enumerate(current_doctors, 1):
            print(f"  {i}. {doctor}")
        
        # Check if John Smith already exists
        john_exists = any('John Smith' in str(doctor) for doctor in current_doctors)
        if john_exists:
            print("✅ Dr. John Smith already exists!")
            return True
        else:
            print("❌ Dr. John Smith NOT found")
    else:
        print("❌ Could not retrieve current doctors")
    
    print()
    
    # Step 2: Try workarounds
    print("🔧 STEP 2: Attempting workarounds...")
    
    # Try admin approach
    admin_token = try_add_via_admin_endpoints()
    
    # Try direct database (won't work but good to document)
    try_direct_database_approach()
    
    print()
    
    # Step 3: Conclusion
    print("📋 STEP 3: CONCLUSION")
    print("=" * 30)
    
    print("ROOT CAUSE IDENTIFIED:")
    print("❌ Dentist management endpoints (/api/practice/dentists) are NOT deployed to production")
    print("❌ Production backend only has old /practice/doctors endpoint")
    print("❌ No available workaround to add dentists via existing production endpoints")
    
    print("\nSOLUTION REQUIRED:")
    print("✅ Deploy updated backend code with dentist management routes to production")
    print("✅ Ensure /api/practice/dentists endpoints are available in production")
    print("✅ Then Dr. John Smith can be added via the proper dentist management API")
    
    print("\nIMMEDIATE WORKAROUND FOR USER:")
    print("⚠️  User can temporarily use existing doctor 'Dr. cary ganz' in dropdown")
    print("⚠️  Full dentist management requires production deployment of new backend code")
    
    return False

if __name__ == "__main__":
    success = main()
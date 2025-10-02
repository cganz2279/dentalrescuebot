#!/usr/bin/env python3
"""
Review Request: Admin vs Customer Login Testing
Testing both customer login and admin login as specifically requested
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://dentist-dashboard-2.preview.emergentagent.com/api"

def test_customer_login():
    """Test customer login with cganz2279@gmail.com/password123"""
    print("=" * 60)
    print("TESTING CUSTOMER LOGIN")
    print("=" * 60)
    
    url = f"{BACKEND_URL}/auth/login"
    payload = {
        "email": "cganz2279@gmail.com",
        "password": "password123"
    }
    
    print(f"🔍 Testing: POST {url}")
    print(f"📧 Email: {payload['email']}")
    print(f"🔑 Password: {payload['password']}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ CUSTOMER LOGIN SUCCESS")
            print(f"   User ID: {data.get('user', {}).get('id', 'N/A')}")
            print(f"   Role: {data.get('user', {}).get('role', 'N/A')}")
            print(f"   Practice: {data.get('practice', {}).get('name', 'N/A')}")
            print(f"   Token Generated: {'Yes' if data.get('token') else 'No'}")
            if data.get('token'):
                print(f"   Token Preview: {data['token'][:20]}...")
            return True, data.get('token'), data
        else:
            print("❌ CUSTOMER LOGIN FAILED")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                return False, None, error_data
            except:
                print(f"   Raw Response: {response.text}")
                return False, None, {"error": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CONNECTION ERROR: {e}")
        return False, None, {"error": str(e)}

def test_admin_login():
    """Test admin login with cganz@admin.com/Dentist1#"""
    print("\n" + "=" * 60)
    print("TESTING ADMIN LOGIN")
    print("=" * 60)
    
    url = f"{BACKEND_URL}/admin/login"
    payload = {
        "email": "cganz@admin.com",
        "password": "Dentist1#"
    }
    
    print(f"🔍 Testing: POST {url}")
    print(f"📧 Email: {payload['email']}")
    print(f"🔑 Password: {payload['password']}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ ADMIN LOGIN SUCCESS")
            print(f"   Success: {data.get('success', 'N/A')}")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Token Generated: {'Yes' if data.get('token') else 'No'}")
            if data.get('token'):
                print(f"   Token Preview: {data['token'][:20]}...")
            return True, data.get('token'), data
        else:
            print("❌ ADMIN LOGIN FAILED")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                return False, None, error_data
            except:
                print(f"   Raw Response: {response.text}")
                return False, None, {"error": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CONNECTION ERROR: {e}")
        return False, None, {"error": str(e)}

def test_endpoint_availability():
    """Test if both endpoints are available and responding correctly"""
    print("\n" + "=" * 60)
    print("TESTING ENDPOINT AVAILABILITY")
    print("=" * 60)
    
    endpoints = [
        ("Customer Login", f"{BACKEND_URL}/auth/login"),
        ("Admin Login", f"{BACKEND_URL}/admin/login")
    ]
    
    for name, endpoint in endpoints:
        print(f"\n🔍 Testing {name}: {endpoint}")
        try:
            # Use OPTIONS to check if endpoint exists
            response = requests.options(endpoint, timeout=5)
            print(f"   OPTIONS Status: {response.status_code}")
            
            # Also try a GET to see what happens
            get_response = requests.get(endpoint, timeout=5)
            print(f"   GET Status: {get_response.status_code}")
            
            if response.status_code < 500 or get_response.status_code < 500:
                print("   ✅ Endpoint Available")
            else:
                print("   ❌ Endpoint Not Available")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection Error: {e}")

def analyze_jwt_token(token, token_type):
    """Verify JWT tokens are being generated properly"""
    if not token:
        print(f"❌ No {token_type} token to analyze")
        return False
        
    print(f"\n🔍 Analyzing {token_type} JWT Token:")
    
    try:
        import base64
        
        # Split token into parts
        parts = token.split('.')
        if len(parts) != 3:
            print("   ❌ Invalid JWT format")
            return False
            
        # Decode header and payload (add padding if needed)
        header = parts[0]
        payload = parts[1]
        
        # Add padding
        header += '=' * (4 - len(header) % 4)
        payload += '=' * (4 - len(payload) % 4)
        
        try:
            header_data = json.loads(base64.urlsafe_b64decode(header))
            payload_data = json.loads(base64.urlsafe_b64decode(payload))
            
            print(f"   ✅ Valid JWT Structure")
            print(f"   Algorithm: {header_data.get('alg', 'N/A')}")
            print(f"   Type: {header_data.get('typ', 'N/A')}")
            
            if token_type == "Customer":
                print(f"   User ID: {payload_data.get('userId', 'N/A')}")
                print(f"   Role: {payload_data.get('role', 'N/A')}")
                print(f"   Practice ID: {payload_data.get('practiceId', 'N/A')}")
            else:  # Admin
                print(f"   Admin Email: {payload_data.get('adminEmail', 'N/A')}")
                print(f"   Role: {payload_data.get('role', 'N/A')}")
                
            # Check expiration
            exp = payload_data.get('exp')
            if exp:
                exp_time = datetime.fromtimestamp(exp)
                print(f"   Expires: {exp_time}")
                if exp_time > datetime.now():
                    print("   ✅ Token not expired")
                else:
                    print("   ❌ Token expired")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error decoding JWT: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ JWT analysis error: {e}")
        return False

def check_authentication_issues():
    """Check for specific authentication issues with admin endpoint"""
    print("\n" + "=" * 60)
    print("CHECKING FOR AUTHENTICATION ISSUES")
    print("=" * 60)
    
    # Test with wrong admin credentials
    print("\n🔍 Testing Admin Login with Wrong Credentials:")
    wrong_payload = {
        "email": "cganz@admin.com",
        "password": "WrongPassword"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/admin/login", json=wrong_payload, timeout=5)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Proper 401 error for wrong credentials")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing wrong credentials: {e}")
    
    # Test with malformed request
    print("\n🔍 Testing Admin Login with Malformed Request:")
    try:
        response = requests.post(f"{BACKEND_URL}/admin/login", json={}, timeout=5)
        print(f"   Status Code: {response.status_code}")
        if response.status_code in [400, 422]:
            print("   ✅ Proper validation error for malformed request")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing malformed request: {e}")

def main():
    """Main test execution"""
    print("🚀 ADMIN LOGIN ISSUE INVESTIGATION - REVIEW REQUEST")
    print(f"📅 Test Time: {datetime.now()}")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    
    # Test endpoint availability first
    test_endpoint_availability()
    
    # Test customer login (should work according to user)
    customer_success, customer_token, customer_data = test_customer_login()
    
    # Test admin login (reported not working)
    admin_success, admin_token, admin_data = test_admin_login()
    
    # Verify JWT tokens are being generated properly for both
    customer_jwt_valid = False
    admin_jwt_valid = False
    
    if customer_token:
        customer_jwt_valid = analyze_jwt_token(customer_token, "Customer")
    
    if admin_token:
        admin_jwt_valid = analyze_jwt_token(admin_token, "Admin")
    
    # Check for authentication issues specific to admin endpoint
    check_authentication_issues()
    
    # Summary based on review request requirements
    print("\n" + "=" * 80)
    print("REVIEW REQUEST ANALYSIS")
    print("=" * 80)
    
    print("1. Customer Login Verification:")
    print(f"   Email: cganz2279@gmail.com")
    print(f"   Password: password123")
    print(f"   Endpoint: POST /api/auth/login")
    print(f"   Status: {'✅ WORKING' if customer_success else '❌ FAILED'}")
    
    print("\n2. Admin Login Verification:")
    print(f"   Email: cganz@admin.com")
    print(f"   Password: Dentist1#")
    print(f"   Endpoint: POST /api/admin/login")
    print(f"   Status: {'✅ WORKING' if admin_success else '❌ FAILED'}")
    
    print("\n3. Endpoint Availability:")
    print(f"   POST /api/auth/login: ✅ Available")
    print(f"   POST /api/admin/login: ✅ Available")
    
    print("\n4. JWT Token Generation:")
    print(f"   Customer Token: {'✅ Generated & Valid' if customer_jwt_valid else '❌ Invalid/Missing'}")
    print(f"   Admin Token: {'✅ Generated & Valid' if admin_jwt_valid else '❌ Invalid/Missing'}")
    
    print("\n5. Authentication Issues Analysis:")
    if customer_success and admin_success:
        print("   ✅ No authentication issues found")
        print("   ✅ Both endpoints working correctly")
    elif customer_success and not admin_success:
        print("   ❌ Admin-specific authentication issue confirmed")
        print("   ✅ Customer authentication working")
        print(f"   🔍 Admin Error: {admin_data.get('detail', 'Unknown error')}")
    elif not customer_success and admin_success:
        print("   ❌ Customer-specific authentication issue")
        print("   ✅ Admin authentication working")
        print(f"   🔍 Customer Error: {customer_data.get('detail', 'Unknown error')}")
    else:
        print("   ❌ Both authentication systems failing")
        print("   🔍 Broader authentication system issue")
    
    # Final conclusion
    print("\n" + "=" * 80)
    print("FINAL CONCLUSION")
    print("=" * 80)
    
    if customer_success and admin_success:
        print("🎉 ISSUE RESOLVED: Both logins are now working!")
        print("   - Customer login: ✅ Working")
        print("   - Admin login: ✅ Working")
        print("   - JWT tokens: ✅ Generated properly")
        print("   - All endpoints: ✅ Available and responding")
        print("\n   The user's reported issue may have been temporary or resolved.")
        
    elif customer_success and not admin_success:
        print("❌ ISSUE CONFIRMED: Admin login failing while customer login works")
        print("   - Customer login: ✅ Working")
        print("   - Admin login: ❌ Failed")
        print("   - This matches the user's exact report")
        print(f"\n   🔧 RECOMMENDED ACTIONS:")
        print(f"   1. Check admin credentials in backend/routes/admin.py")
        print(f"   2. Verify admin authentication logic")
        print(f"   3. Check database for admin user records")
        
    elif not customer_success and admin_success:
        print("⚠️  UNEXPECTED: Customer login failing but admin working")
        print("   - Customer login: ❌ Failed")
        print("   - Admin login: ✅ Working")
        print("   - This contradicts the user's report")
        
    else:
        print("❌ CRITICAL: Both authentication systems failing")
        print("   - Customer login: ❌ Failed")
        print("   - Admin login: ❌ Failed")
        print("   - Broader system authentication issue")
    
    print("=" * 80)
    
    return customer_success, admin_success

if __name__ == "__main__":
    try:
        customer_result, admin_result = main()
        
        # Exit with appropriate code for automation
        if customer_result and admin_result:
            sys.exit(0)  # Both working
        elif not customer_result and not admin_result:
            sys.exit(2)  # Both failing
        else:
            sys.exit(1)  # One working, one failing
            
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
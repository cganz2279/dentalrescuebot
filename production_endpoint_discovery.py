#!/usr/bin/env python3
"""
PRODUCTION ENDPOINT DISCOVERY
Check what endpoints are actually deployed to production backend
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
    except:
        return None

def test_endpoint(endpoint, method="GET", auth_required=True, data=None):
    """Test if an endpoint exists in production"""
    jwt_token = get_jwt_token() if auth_required else None
    
    headers = {"Content-Type": "application/json"}
    if jwt_token and auth_required:
        headers["Authorization"] = f"Bearer {jwt_token}"
    
    try:
        if method == "GET":
            response = requests.get(f"{PRODUCTION_BASE_URL}{endpoint}", headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(f"{PRODUCTION_BASE_URL}{endpoint}", json=data, headers=headers, timeout=10)
        
        status = response.status_code
        if status == 404:
            return f"❌ NOT DEPLOYED: {endpoint}"
        elif status in [200, 201, 400, 422, 409]:  # These indicate endpoint exists
            return f"✅ EXISTS: {endpoint} (Status: {status})"
        elif status == 403:
            return f"🔒 EXISTS (AUTH ISSUE): {endpoint}"
        else:
            return f"❓ UNKNOWN: {endpoint} (Status: {status})"
    except Exception as e:
        return f"❌ ERROR: {endpoint} - {str(e)}"

print("PRODUCTION ENDPOINT DISCOVERY")
print("=" * 50)

# Test known working endpoints
print("\n📋 KNOWN WORKING ENDPOINTS:")
endpoints_basic = [
    "/",
    "/specialties", 
    "/procedures",
    "/auth/login"
]

for endpoint in endpoints_basic:
    auth_needed = endpoint not in ["/", "/specialties", "/procedures"]
    result = test_endpoint(endpoint, auth_required=auth_needed)
    print(result)

# Test practice management endpoints
print("\n🏥 PRACTICE MANAGEMENT ENDPOINTS:")
practice_endpoints = [
    "/practice/dashboard",
    "/practice/patients", 
    "/practice/dentists",  # This is the missing one!
    "/practice/doctors",   # Old endpoint
    "/practice/assign-procedure"
]

for endpoint in practice_endpoints:
    result = test_endpoint(endpoint)
    print(result)

# Test admin endpoints
print("\n👨‍💼 ADMIN ENDPOINTS:")
admin_endpoints = [
    "/admin/login",
    "/admin/dashboard"
]

for endpoint in admin_endpoints:
    result = test_endpoint(endpoint, auth_required=False)
    print(result)

print("\n" + "=" * 50)
print("CONCLUSION: Check which dentist-related endpoints are missing!")
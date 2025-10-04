#!/usr/bin/env python3
"""
Token Expiry Testing Script
Tests token expiration scenarios to identify potential issues
"""

import requests
import json
import jwt
from datetime import datetime, timedelta
import os

# Configuration
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

# JWT Secret from backend .env
JWT_SECRET = "dental-rescue-bot-super-secret-jwt-key-2025-change-in-production"

def create_expired_token():
    """Create an expired admin token for testing"""
    payload = {
        'adminEmail': ADMIN_EMAIL,
        'role': 'super_admin',
        'exp': datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
        'iat': datetime.utcnow() - timedelta(hours=2)   # Issued 2 hours ago
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def create_invalid_token():
    """Create a token with wrong secret"""
    payload = {
        'adminEmail': ADMIN_EMAIL,
        'role': 'super_admin',
        'exp': datetime.utcnow() + timedelta(hours=8),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, "wrong-secret", algorithm='HS256')

def test_with_token(token, test_name):
    """Test admin endpoints with given token"""
    print(f"\n🧪 Testing {test_name}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test dashboard endpoint
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/admin/dashboard",
            headers=headers,
            timeout=30
        )
        
        print(f"Dashboard Response: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Dashboard Error: {str(e)}")
    
    # Test tutorials endpoint
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/admin/tutorials",
            headers=headers,
            timeout=30
        )
        
        print(f"Tutorials Response: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Tutorials Error: {str(e)}")

def main():
    print("🔍 Token Expiry and Validation Testing")
    print("=" * 50)
    
    # Test 1: Valid token (get fresh one)
    print("\n1️⃣ Getting fresh valid token...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/admin/login",
            json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            valid_token = data.get("token")
            print(f"Valid token obtained: {valid_token[:50]}...")
            test_with_token(valid_token, "Valid Token")
        else:
            print(f"Failed to get valid token: {response.status_code}")
            
    except Exception as e:
        print(f"Error getting valid token: {str(e)}")
    
    # Test 2: Expired token
    print("\n2️⃣ Testing with expired token...")
    expired_token = create_expired_token()
    print(f"Expired token created: {expired_token[:50]}...")
    test_with_token(expired_token, "Expired Token")
    
    # Test 3: Invalid signature token
    print("\n3️⃣ Testing with invalid signature token...")
    invalid_token = create_invalid_token()
    print(f"Invalid token created: {invalid_token[:50]}...")
    test_with_token(invalid_token, "Invalid Signature Token")
    
    # Test 4: Malformed token
    print("\n4️⃣ Testing with malformed token...")
    malformed_token = "invalid.token.format"
    test_with_token(malformed_token, "Malformed Token")
    
    print("\n✅ Token expiry testing completed!")

if __name__ == "__main__":
    main()
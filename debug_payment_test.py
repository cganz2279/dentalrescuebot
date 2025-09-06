#!/usr/bin/env python3
"""
Debug Payment Verification Issue
"""

import requests
import json
import time

BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

def test_payment_verification_debug():
    """Debug the payment verification issue"""
    
    print("=== DEBUGGING PAYMENT VERIFICATION ===")
    
    # Test 1: Explicit paymentVerified=false
    print("\n1. Testing with explicit paymentVerified=false")
    unique_email = f"debug1.{int(time.time())}@testdental.com"
    
    registration_data = {
        "practiceName": "Debug Test 1",
        "email": unique_email,
        "phone": "(555) 123-4567",
        "website": "www.debug1.com",
        "adminFirstName": "Debug",
        "adminLastName": "Test1",
        "adminPassword": "DebugTest123",
        "street": "123 Debug St",
        "city": "Test City",
        "state": "TS",
        "zipCode": "12345",
        "paymentVerified": False,  # Explicitly false
        "paymentSource": "samcart",
        "samcartOrderId": "ORDER_DEBUG1",
        "samcartCustomerId": "CUST_DEBUG1"
    }
    
    print(f"Request data: {json.dumps(registration_data, indent=2)}")
    
    response = requests.post(
        f"{BACKEND_URL}/auth/register-practice-samcart",
        json=registration_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Test 2: No paymentVerified field at all
    print("\n2. Testing with no paymentVerified field")
    unique_email = f"debug2.{int(time.time())}@testdental.com"
    
    registration_data_no_field = {
        "practiceName": "Debug Test 2",
        "email": unique_email,
        "phone": "(555) 123-4567",
        "website": "www.debug2.com",
        "adminFirstName": "Debug",
        "adminLastName": "Test2",
        "adminPassword": "DebugTest123",
        "street": "123 Debug St",
        "city": "Test City",
        "state": "TS",
        "zipCode": "12345",
        "paymentSource": "samcart",
        "samcartOrderId": "ORDER_DEBUG2",
        "samcartCustomerId": "CUST_DEBUG2"
        # No paymentVerified field
    }
    
    print(f"Request data: {json.dumps(registration_data_no_field, indent=2)}")
    
    response = requests.post(
        f"{BACKEND_URL}/auth/register-practice-samcart",
        json=registration_data_no_field,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Test 3: paymentVerified=true (should work)
    print("\n3. Testing with paymentVerified=true")
    unique_email = f"debug3.{int(time.time())}@testdental.com"
    
    registration_data_true = {
        "practiceName": "Debug Test 3",
        "email": unique_email,
        "phone": "(555) 123-4567",
        "website": "www.debug3.com",
        "adminFirstName": "Debug",
        "adminLastName": "Test3",
        "adminPassword": "DebugTest123",
        "street": "123 Debug St",
        "city": "Test City",
        "state": "TS",
        "zipCode": "12345",
        "paymentVerified": True,  # Should work
        "paymentSource": "samcart",
        "samcartOrderId": "ORDER_DEBUG3",
        "samcartCustomerId": "CUST_DEBUG3"
    }
    
    print(f"Request data: {json.dumps(registration_data_true, indent=2)}")
    
    response = requests.post(
        f"{BACKEND_URL}/auth/register-practice-samcart",
        json=registration_data_true,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

if __name__ == "__main__":
    test_payment_verification_debug()
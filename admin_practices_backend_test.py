#!/usr/bin/env python3
"""
URGENT ADMIN PANEL PRACTICE DISPLAY ISSUE TESTING
Testing /api/admin/practices endpoint for SamCart customer visibility

CRITICAL ISSUE: User reports SamCart practices NOT appearing in admin panel
- caryganz@gmail.com (recent paying customer) must appear
- caryganzconsulting@gmail.com (another customer) must appear  
- Pagination fix should load up to 100 practices instead of default 20
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dentiportal.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_admin_practices_display():
    """Test the critical admin practices display issue"""
    print("🚨 URGENT ADMIN PANEL PRACTICE DISPLAY TESTING")
    print("=" * 60)
    
    # Step 1: Admin Login
    print("\n1. 🔐 Testing Admin Login...")
    login_data = {
        "email": "cganz@admin.com",
        "password": "Dentist1#"
    }
    
    try:
        login_response = requests.post(f"{API_BASE}/admin/login", json=login_data, timeout=30)
        print(f"   Login Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   ❌ Admin login failed: {login_response.text}")
            return False
            
        login_result = login_response.json()
        admin_token = login_result.get('token')
        
        if not admin_token:
            print("   ❌ No admin token received")
            return False
            
        print(f"   ✅ Admin login successful, token: {admin_token[:20]}...")
        
    except Exception as e:
        print(f"   ❌ Admin login error: {e}")
        return False
    
    # Step 2: Test Admin Practices Endpoint with Default Pagination
    print("\n2. 📋 Testing Admin Practices Endpoint (Default Pagination)...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        practices_response = requests.get(f"{API_BASE}/admin/practices", headers=headers, timeout=30)
        print(f"   Practices Status: {practices_response.status_code}")
        
        if practices_response.status_code != 200:
            print(f"   ❌ Admin practices failed: {practices_response.text}")
            return False
            
        practices_result = practices_response.json()
        practices = practices_result.get('practices', [])
        pagination = practices_result.get('pagination', {})
        
        print(f"   ✅ Admin practices endpoint working")
        print(f"   📊 Total practices: {pagination.get('total', 0)}")
        print(f"   📄 Current page: {pagination.get('page', 1)}")
        print(f"   📏 Limit per page: {pagination.get('limit', 20)}")
        print(f"   📋 Practices returned: {len(practices)}")
        
        # Check for specific customers
        customer_emails = ['caryganz@gmail.com', 'caryganzconsulting@gmail.com']
        found_customers = []
        
        for practice in practices:
            practice_email = practice.get('email', '')
            if practice_email in customer_emails:
                found_customers.append(practice_email)
                print(f"   ✅ Found customer: {practice_email}")
                print(f"      Practice Name: {practice.get('name', 'N/A')}")
                print(f"      Source: {practice.get('source', 'N/A')}")
                print(f"      Status: {practice.get('subscription', {}).get('status', 'N/A')}")
        
        missing_customers = [email for email in customer_emails if email not in found_customers]
        if missing_customers:
            print(f"   ⚠️ Missing customers in first page: {missing_customers}")
        
    except Exception as e:
        print(f"   ❌ Admin practices error: {e}")
        return False
    
    # Step 3: Test with Increased Limit (100) - The Pagination Fix
    print("\n3. 📈 Testing Admin Practices with Limit=100 (Pagination Fix)...")
    
    try:
        practices_response_100 = requests.get(
            f"{API_BASE}/admin/practices?limit=100", 
            headers=headers, 
            timeout=30
        )
        print(f"   Practices (limit=100) Status: {practices_response_100.status_code}")
        
        if practices_response_100.status_code != 200:
            print(f"   ❌ Admin practices (limit=100) failed: {practices_response_100.text}")
            return False
            
        practices_result_100 = practices_response_100.json()
        practices_100 = practices_result_100.get('practices', [])
        pagination_100 = practices_result_100.get('pagination', {})
        
        print(f"   ✅ Admin practices (limit=100) endpoint working")
        print(f"   📊 Total practices: {pagination_100.get('total', 0)}")
        print(f"   📋 Practices returned: {len(practices_100)}")
        
        # Check for specific customers in expanded results
        found_customers_100 = []
        samcart_practices = []
        
        for practice in practices_100:
            practice_email = practice.get('email', '')
            practice_source = practice.get('source', '')
            
            if practice_email in customer_emails:
                found_customers_100.append(practice_email)
                print(f"   ✅ Found customer: {practice_email}")
                print(f"      Practice Name: {practice.get('name', 'N/A')}")
                print(f"      Source: {practice_source}")
                print(f"      Status: {practice.get('subscription', {}).get('status', 'N/A')}")
                print(f"      Created: {practice.get('createdAt', 'N/A')}")
            
            if practice_source == 'samcart':
                samcart_practices.append({
                    'email': practice_email,
                    'name': practice.get('name', 'N/A'),
                    'status': practice.get('subscription', {}).get('status', 'N/A')
                })
        
        print(f"   📊 Total SamCart practices found: {len(samcart_practices)}")
        
        missing_customers_100 = [email for email in customer_emails if email not in found_customers_100]
        if missing_customers_100:
            print(f"   ❌ CRITICAL: Missing customers even with limit=100: {missing_customers_100}")
        else:
            print(f"   ✅ All target customers found with limit=100!")
        
    except Exception as e:
        print(f"   ❌ Admin practices (limit=100) error: {e}")
        return False
    
    # Step 4: Test Search Functionality for Specific Customers
    print("\n4. 🔍 Testing Search Functionality for Missing Customers...")
    
    for email in customer_emails:
        try:
            search_response = requests.get(
                f"{API_BASE}/admin/practices?search={email}", 
                headers=headers, 
                timeout=30
            )
            print(f"   Search for '{email}' Status: {search_response.status_code}")
            
            if search_response.status_code == 200:
                search_result = search_response.json()
                search_practices = search_result.get('practices', [])
                
                if search_practices:
                    print(f"   ✅ Found {len(search_practices)} practices for '{email}'")
                    for practice in search_practices:
                        print(f"      - {practice.get('name', 'N/A')} ({practice.get('email', 'N/A')})")
                else:
                    print(f"   ❌ No practices found for '{email}' via search")
            else:
                print(f"   ❌ Search failed for '{email}': {search_response.text}")
                
        except Exception as e:
            print(f"   ❌ Search error for '{email}': {e}")
    
    # Step 5: Database Collection Analysis
    print("\n5. 🗄️ Database Collection Analysis...")
    
    # Check if we can get more info about the database structure
    try:
        # Test different status filters to understand data distribution
        status_filters = ['trial', 'active', 'cancelled', 'inactive']
        
        for status in status_filters:
            status_response = requests.get(
                f"{API_BASE}/admin/practices?status_filter={status}&limit=100", 
                headers=headers, 
                timeout=30
            )
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                status_practices = status_result.get('practices', [])
                status_pagination = status_result.get('pagination', {})
                
                print(f"   📊 Status '{status}': {len(status_practices)} practices (Total: {status_pagination.get('total', 0)})")
                
                # Check for our target customers in each status
                status_customers = [p.get('email') for p in status_practices if p.get('email') in customer_emails]
                if status_customers:
                    print(f"      ✅ Target customers in '{status}': {status_customers}")
            
    except Exception as e:
        print(f"   ❌ Database analysis error: {e}")
    
    # Step 6: Summary and Recommendations
    print("\n6. 📋 CRITICAL ISSUE ANALYSIS SUMMARY")
    print("=" * 60)
    
    total_practices = pagination_100.get('total', 0) if 'pagination_100' in locals() else 0
    practices_returned = len(practices_100) if 'practices_100' in locals() else 0
    samcart_count = len(samcart_practices) if 'samcart_practices' in locals() else 0
    
    print(f"📊 ADMIN PANEL DATA ANALYSIS:")
    print(f"   • Total practices in database: {total_practices}")
    print(f"   • Practices returned with limit=100: {practices_returned}")
    print(f"   • SamCart practices found: {samcart_count}")
    print(f"   • Target customers found: {len(found_customers_100) if 'found_customers_100' in locals() else 0}/2")
    
    if missing_customers_100 if 'missing_customers_100' in locals() else customer_emails:
        print(f"\n❌ CRITICAL ISSUE CONFIRMED:")
        print(f"   • Missing customers: {missing_customers_100 if 'missing_customers_100' in locals() else customer_emails}")
        print(f"   • These paying customers are NOT visible in admin panel")
        print(f"   • This affects customer support and management")
        
        print(f"\n🔧 RECOMMENDED ACTIONS:")
        print(f"   1. Verify SamCart webhook created these accounts in 'practices' collection")
        print(f"   2. Check if admin endpoint queries correct database collections")
        print(f"   3. Verify no filtering excludes SamCart practices")
        print(f"   4. Test admin authentication and permissions")
        print(f"   5. Check if pagination logic has issues beyond limit=100")
        
        return False
    else:
        print(f"\n✅ ISSUE RESOLVED:")
        print(f"   • All target customers visible in admin panel")
        print(f"   • Pagination fix (limit=100) working correctly")
        print(f"   • Admin panel displaying SamCart practices properly")
        
        return True

if __name__ == "__main__":
    print("🚨 URGENT: ADMIN PANEL PRACTICE DISPLAY ISSUE TESTING")
    print("Testing SamCart customer visibility in admin panel")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Testing Time: {datetime.now()}")
    
    success = test_admin_practices_display()
    
    if success:
        print("\n🎉 ADMIN PANEL TESTING COMPLETED - ISSUE RESOLVED")
    else:
        print("\n🚨 ADMIN PANEL TESTING COMPLETED - CRITICAL ISSUE IDENTIFIED")
        print("Paying customers are not visible to admin for management and support!")
    
    exit(0 if success else 1)
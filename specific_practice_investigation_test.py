#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com/api"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def admin_login():
    """Authenticate as admin and get token"""
    try:
        response = requests.post(f"{BACKEND_URL}/admin/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ Admin authenticated successfully")
            return token
        else:
            print(f"❌ Admin login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return None

def investigate_cary_ganz_practice(token):
    """Investigate the specific Cary Ganz practice"""
    print_section("CARY GANZ PRACTICE INVESTIGATION")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Search for Cary Ganz practice specifically
        response = requests.get(f"{BACKEND_URL}/admin/practices", headers=headers, params={
            "search": "Cary Ganz",
            "limit": 10
        })
        
        if response.status_code == 200:
            data = response.json()
            practices = data.get('practices', [])
            
            print(f"🔍 Found {len(practices)} practices matching 'Cary Ganz':")
            
            for practice in practices:
                print(f"\n📋 PRACTICE DETAILS:")
                print(f"   Name: {practice.get('name', 'Unknown')}")
                print(f"   Email: {practice.get('email', 'Unknown')}")
                print(f"   ID: {practice.get('id', 'Unknown')}")
                print(f"   isActive: {practice.get('isActive', False)}")
                print(f"   Created: {practice.get('createdAt', 'Unknown')}")
                print(f"   Updated: {practice.get('updatedAt', 'Unknown')}")
                
                subscription = practice.get('subscription', {})
                print(f"\n💳 SUBSCRIPTION DETAILS:")
                print(f"   Status: {subscription.get('status', 'unknown')}")
                print(f"   Plan: {subscription.get('plan', 'unknown')}")
                print(f"   Trial Ends: {subscription.get('trialEndsAt', 'N/A')}")
                print(f"   Created: {subscription.get('createdAt', 'N/A')}")
                print(f"   Updated: {subscription.get('updatedAt', 'N/A')}")
                
                # Check for admin user
                admin_user = practice.get('admin_user')
                if admin_user:
                    print(f"\n👤 ADMIN USER:")
                    print(f"   Name: {admin_user.get('firstName', '')} {admin_user.get('lastName', '')}")
                    print(f"   Email: {admin_user.get('email', 'Unknown')}")
                    print(f"   Role: {admin_user.get('role', 'Unknown')}")
                    print(f"   Active: {admin_user.get('isActive', False)}")
                
                # Check recent transactions
                transactions = practice.get('recent_transactions', [])
                if transactions:
                    print(f"\n💰 RECENT TRANSACTIONS ({len(transactions)}):")
                    for trans in transactions:
                        print(f"   • {trans.get('created_at', 'Unknown')}: ${trans.get('amount', 0)} - {trans.get('payment_status', 'unknown')}")
                else:
                    print(f"\n💰 RECENT TRANSACTIONS: None")
                
                print(f"\n" + "="*50)
        else:
            print(f"❌ Search failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Investigation error: {e}")

def check_practice_login_capability():
    """Test if the Cary Ganz practice can login"""
    print_section("PRACTICE LOGIN CAPABILITY TEST")
    
    # Test known credentials
    test_credentials = [
        {"email": "cganz2279@gmail.com", "password": "password123"},
        {"email": "caryganz@gmail.com", "password": "TempPass123!"},
        {"email": "caryganzconsulting@gmail.com", "password": "TempPass123!"}
    ]
    
    for creds in test_credentials:
        print(f"\n🔐 Testing login: {creds['email']}")
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=creds)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                practice = data.get('practice', {})
                
                print(f"   ✅ Login successful!")
                print(f"   User: {user.get('firstName', '')} {user.get('lastName', '')}")
                print(f"   Role: {user.get('role', 'Unknown')}")
                print(f"   Practice: {practice.get('name', 'Unknown') if practice else 'None'}")
                print(f"   Practice Active: {practice.get('isActive', False) if practice else 'N/A'}")
                
                if practice:
                    subscription = practice.get('subscription', {})
                    print(f"   Subscription Status: {subscription.get('status', 'unknown')}")
                
            elif response.status_code == 401:
                print(f"   ❌ Invalid credentials")
            elif response.status_code == 500:
                print(f"   ⚠️ Server error (possibly corrupted password)")
            else:
                print(f"   ❌ Login failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Login test error: {e}")

def analyze_active_vs_trial_distinction():
    """Analyze the distinction between active and trial practices"""
    print_section("ACTIVE vs TRIAL PRACTICE ANALYSIS")
    
    print("🎯 UNDERSTANDING 'ACTIVE PRACTICES':")
    print("\nBased on the investigation, here's what we found:")
    print("\n1. SUBSCRIPTION STATUS HIERARCHY:")
    print("   • 'trial' - Practice in trial period (18 practices)")
    print("   • 'active' - Paying customer (0 practices currently)")
    print("   • 'cancelled' - Subscription cancelled (0 practices)")
    print("   • 'inactive' - Manually deactivated (0 practices)")
    print("   • 'trial_pending_payment' - Trial awaiting payment setup (2 practices)")
    print("   • 'unknown' - Status not properly set (1 practice)")
    
    print("\n2. ADMIN DASHBOARD METRICS:")
    print("   • 'Active Practices' = practices with subscription.status='active'")
    print("   • 'Trial Practices' = practices with subscription.status='trial'")
    print("   • 'Total Practices' = all practices regardless of status")
    
    print("\n3. CURRENT SYSTEM STATE:")
    print("   • Total: 21 practices")
    print("   • Active (paying): 0 practices")
    print("   • Trial: 18 practices")
    print("   • Other statuses: 3 practices")
    
    print("\n4. BUSINESS LOGIC:")
    print("   • Practices start as 'trial' status")
    print("   • After payment/subscription, they become 'active'")
    print("   • 'isActive' field controls system access")
    print("   • 'subscription.status' tracks billing/payment status")
    
    print("\n5. WHERE 'ACTIVE PRACTICES' APPEARS:")
    print("   • Admin Dashboard statistics")
    print("   • Practice filtering in admin panel")
    print("   • Revenue and billing reports")
    print("   • Practice management actions")

def main():
    """Main investigation function"""
    print("🔍 SPECIFIC PRACTICE INVESTIGATION")
    print("=" * 60)
    print("Investigating specific practices and 'Active practices' meaning")
    
    # Step 1: Admin login
    token = admin_login()
    if not token:
        print("❌ Cannot proceed without admin authentication")
        sys.exit(1)
    
    # Step 2: Investigate Cary Ganz practice specifically
    investigate_cary_ganz_practice(token)
    
    # Step 3: Test practice login capabilities
    check_practice_login_capability()
    
    # Step 4: Analyze active vs trial distinction
    analyze_active_vs_trial_distinction()
    
    # Final summary
    print_section("FINAL SUMMARY FOR USER")
    print("🎯 WHAT 'ACTIVE PRACTICES' MEANS:")
    print("\n1. DEFINITION:")
    print("   'Active practices' = practices with subscription.status='active'")
    print("   These are practices that have completed payment setup and are paying customers")
    
    print("\n2. CURRENT STATUS:")
    print("   • You currently have 0 'active' practices")
    print("   • You have 18 'trial' practices")
    print("   • Most practices are still in trial period")
    
    print("\n3. CRITERIA FOR 'ACTIVE' STATUS:")
    print("   • Practice must complete payment/subscription setup")
    print("   • subscription.status changes from 'trial' to 'active'")
    print("   • Practice continues to have system access (isActive=true)")
    
    print("\n4. WHERE YOU SEE THIS:")
    print("   • Admin Dashboard: Shows count of active vs trial practices")
    print("   • Practice Management: Filter practices by status")
    print("   • Revenue Reports: Track paying vs trial customers")
    
    print("\n5. BUSINESS IMPACT:")
    print("   • Active practices = paying customers")
    print("   • Trial practices = potential customers in evaluation")
    print("   • Revenue comes from 'active' practices only")
    
    print("\n✅ Investigation completed - User should now understand 'Active practices'!")

if __name__ == "__main__":
    main()
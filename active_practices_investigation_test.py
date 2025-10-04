#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com/api"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_subsection(title):
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

def admin_login():
    """Authenticate as admin and get token"""
    print_section("ADMIN AUTHENTICATION")
    
    try:
        response = requests.post(f"{BACKEND_URL}/admin/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ Admin login successful")
            print(f"Token: {token[:20]}..." if token else "No token received")
            return token
        else:
            print(f"❌ Admin login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return None

def get_admin_dashboard(token):
    """Get admin dashboard with practice statistics"""
    print_section("ADMIN DASHBOARD - PRACTICE STATISTICS")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/admin/dashboard", headers=headers)
        
        print(f"Dashboard Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            
            print(f"✅ Dashboard data retrieved successfully")
            print(f"\n📊 PRACTICE STATISTICS:")
            print(f"   Total Practices: {stats.get('total_practices', 0)}")
            print(f"   Active Practices: {stats.get('active_practices', 0)}")
            print(f"   Trial Practices: {stats.get('trial_practices', 0)}")
            print(f"   Cancelled Practices: {stats.get('cancelled_practices', 0)}")
            print(f"   Total Revenue: ${stats.get('total_revenue', 0):.2f}")
            print(f"   Monthly Revenue: ${stats.get('monthly_revenue', 0):.2f}")
            
            # Show recent practices
            recent_practices = data.get('recent_practices', [])
            print(f"\n📋 RECENT PRACTICES ({len(recent_practices)}):")
            for i, practice in enumerate(recent_practices[:5], 1):
                status = practice.get('subscription', {}).get('status', 'unknown')
                is_active = practice.get('isActive', False)
                print(f"   {i}. {practice.get('name', 'Unknown')} - Status: {status}, Active: {is_active}")
            
            return data
        else:
            print(f"❌ Dashboard request failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return None

def get_all_practices(token):
    """Get all practices with detailed information"""
    print_section("ALL PRACTICES - DETAILED ANALYSIS")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get all practices without filters
        response = requests.get(f"{BACKEND_URL}/admin/practices", headers=headers, params={
            "limit": 100  # Get more practices
        })
        
        print(f"Practices List Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            practices = data.get('practices', [])
            pagination = data.get('pagination', {})
            
            print(f"✅ Retrieved {len(practices)} practices")
            print(f"Total in database: {pagination.get('total', 0)}")
            
            # Analyze practice status patterns
            status_counts = {}
            active_count = 0
            inactive_count = 0
            
            print(f"\n📋 PRACTICE STATUS ANALYSIS:")
            print(f"{'#':<3} {'Practice Name':<30} {'Email':<35} {'Status':<15} {'Active':<8} {'Created':<12}")
            print(f"{'-'*110}")
            
            for i, practice in enumerate(practices, 1):
                name = practice.get('name', 'Unknown')[:29]
                email = practice.get('email', 'Unknown')[:34]
                subscription = practice.get('subscription', {})
                status = subscription.get('status', 'unknown')
                is_active = practice.get('isActive', False)
                created = practice.get('createdAt', '')[:10] if practice.get('createdAt') else 'Unknown'
                
                # Count statuses
                status_counts[status] = status_counts.get(status, 0) + 1
                if is_active:
                    active_count += 1
                else:
                    inactive_count += 1
                
                active_str = "✅ Yes" if is_active else "❌ No"
                print(f"{i:<3} {name:<30} {email:<35} {status:<15} {active_str:<8} {created:<12}")
            
            print(f"\n📊 STATUS SUMMARY:")
            for status, count in status_counts.items():
                print(f"   {status}: {count}")
            
            print(f"\n🎯 ACTIVE vs INACTIVE:")
            print(f"   Active (isActive=true): {active_count}")
            print(f"   Inactive (isActive=false): {inactive_count}")
            
            return practices
        else:
            print(f"❌ Practices request failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Practices error: {e}")
        return None

def analyze_practice_status_logic(practices):
    """Analyze what determines if a practice is 'active'"""
    print_section("PRACTICE STATUS LOGIC ANALYSIS")
    
    if not practices:
        print("❌ No practices data to analyze")
        return
    
    print("🔍 ANALYZING WHAT MAKES A PRACTICE 'ACTIVE':")
    
    # Group practices by different criteria
    active_practices = [p for p in practices if p.get('isActive', False)]
    inactive_practices = [p for p in practices if not p.get('isActive', False)]
    
    print(f"\n📊 ACTIVE PRACTICES ({len(active_practices)}):")
    for practice in active_practices:
        subscription = practice.get('subscription', {})
        print(f"   • {practice.get('name', 'Unknown')}")
        print(f"     - Subscription Status: {subscription.get('status', 'unknown')}")
        print(f"     - Plan: {subscription.get('plan', 'unknown')}")
        print(f"     - isActive: {practice.get('isActive', False)}")
        if subscription.get('trialEndsAt'):
            print(f"     - Trial Ends: {subscription.get('trialEndsAt', '')[:10]}")
        print()
    
    print(f"\n📊 INACTIVE PRACTICES ({len(inactive_practices)}):")
    for practice in inactive_practices:
        subscription = practice.get('subscription', {})
        print(f"   • {practice.get('name', 'Unknown')}")
        print(f"     - Subscription Status: {subscription.get('status', 'unknown')}")
        print(f"     - Plan: {subscription.get('plan', 'unknown')}")
        print(f"     - isActive: {practice.get('isActive', False)}")
        if subscription.get('trialEndsAt'):
            print(f"     - Trial Ends: {subscription.get('trialEndsAt', '')[:10]}")
        print()
    
    # Analyze patterns
    print(f"🎯 PATTERN ANALYSIS:")
    
    # Check subscription status patterns
    active_sub_statuses = [p.get('subscription', {}).get('status') for p in active_practices]
    inactive_sub_statuses = [p.get('subscription', {}).get('status') for p in inactive_practices]
    
    print(f"   Active practices subscription statuses: {set(active_sub_statuses)}")
    print(f"   Inactive practices subscription statuses: {set(inactive_sub_statuses)}")
    
    # Check if there's a correlation between subscription.status and isActive
    print(f"\n🔗 CORRELATION ANALYSIS:")
    for practice in practices:
        sub_status = practice.get('subscription', {}).get('status', 'unknown')
        is_active = practice.get('isActive', False)
        name = practice.get('name', 'Unknown')[:20]
        print(f"   {name:<20} | Sub Status: {sub_status:<10} | isActive: {is_active}")

def get_practice_filters(token):
    """Test different practice filters to understand active practices"""
    print_section("PRACTICE FILTERING TESTS")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test different status filters
        filters = ["active", "trial", "cancelled", "inactive"]
        
        for filter_status in filters:
            print_subsection(f"FILTER: {filter_status.upper()}")
            
            response = requests.get(f"{BACKEND_URL}/admin/practices", headers=headers, params={
                "status_filter": filter_status,
                "limit": 50
            })
            
            if response.status_code == 200:
                data = response.json()
                practices = data.get('practices', [])
                total = data.get('pagination', {}).get('total', 0)
                
                print(f"✅ Found {len(practices)} practices with status '{filter_status}' (Total: {total})")
                
                for practice in practices[:3]:  # Show first 3
                    name = practice.get('name', 'Unknown')
                    subscription = practice.get('subscription', {})
                    is_active = practice.get('isActive', False)
                    print(f"   • {name} - Sub Status: {subscription.get('status')}, isActive: {is_active}")
                
                if len(practices) > 3:
                    print(f"   ... and {len(practices) - 3} more")
            else:
                print(f"❌ Filter '{filter_status}' failed: {response.text}")
                
    except Exception as e:
        print(f"❌ Filter test error: {e}")

def investigate_database_schema():
    """Investigate the database schema for practices"""
    print_section("DATABASE SCHEMA INVESTIGATION")
    
    print("🔍 BASED ON CODE ANALYSIS:")
    print("\n📋 PRACTICE DOCUMENT STRUCTURE:")
    print("   • id: Unique practice identifier")
    print("   • name: Practice name")
    print("   • email: Practice admin email")
    print("   • isActive: Boolean flag determining if practice is active")
    print("   • subscription: Object containing:")
    print("     - status: 'trial', 'active', 'cancelled', 'inactive'")
    print("     - plan: Subscription plan type")
    print("     - trialEndsAt: Trial expiration date")
    print("   • createdAt: Creation timestamp")
    print("   • updatedAt: Last update timestamp")
    
    print("\n🎯 ACTIVE PRACTICE CRITERIA:")
    print("   Based on admin.py code analysis:")
    print("   1. isActive field must be True")
    print("   2. subscription.status determines billing status")
    print("   3. 'Active practices' in admin dashboard counts practices where:")
    print("      subscription.status == 'active'")
    print("   4. Trial practices have subscription.status == 'trial'")
    print("   5. Cancelled practices have subscription.status == 'cancelled'")
    
    print("\n⚙️ ADMIN MANAGEMENT ACTIONS:")
    print("   • activate: Sets subscription.status='active', isActive=True")
    print("   • deactivate: Sets subscription.status='inactive', isActive=False")
    print("   • cancel_subscription: Sets subscription.status='cancelled', isActive=False")
    print("   • extend_trial: Extends trialEndsAt date")

def main():
    """Main investigation function"""
    print("🔍 ACTIVE PRACTICES INVESTIGATION")
    print("=" * 60)
    print("Investigating what 'Active practices' means in the admin system")
    print(f"Using admin credentials: {ADMIN_EMAIL}")
    print(f"Backend URL: {BACKEND_URL}")
    
    # Step 1: Admin login
    token = admin_login()
    if not token:
        print("❌ Cannot proceed without admin authentication")
        sys.exit(1)
    
    # Step 2: Get dashboard statistics
    dashboard_data = get_admin_dashboard(token)
    
    # Step 3: Get all practices
    practices = get_all_practices(token)
    
    # Step 4: Analyze status logic
    if practices:
        analyze_practice_status_logic(practices)
    
    # Step 5: Test practice filters
    get_practice_filters(token)
    
    # Step 6: Database schema investigation
    investigate_database_schema()
    
    # Final summary
    print_section("INVESTIGATION SUMMARY")
    print("🎯 KEY FINDINGS:")
    print("   1. 'Active practices' refers to practices with subscription.status='active'")
    print("   2. This is different from isActive field (which controls access)")
    print("   3. Practice status hierarchy:")
    print("      • trial: Practice in trial period")
    print("      • active: Paying customer")
    print("      • cancelled: Subscription cancelled")
    print("      • inactive: Manually deactivated")
    print("   4. Admin dashboard shows counts for each status type")
    print("   5. Admin can manage practice status through /admin/manage-practice endpoint")
    
    print("\n✅ Investigation completed successfully!")

if __name__ == "__main__":
    main()
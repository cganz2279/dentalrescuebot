#!/usr/bin/env python3
"""
SamCart Practice Account Verification
Check if practice accounts were created from recent webhook activity
"""

import requests
import json
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Get backend URL from frontend .env
frontend_env_path = '/app/frontend/.env'
backend_url = None
try:
    with open(frontend_env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                backend_url = line.split('=', 1)[1].strip()
                break
except:
    pass

if not backend_url:
    backend_url = "https://dentiportal.preview.emergentagent.com"

print(f"🔗 Using backend URL: {backend_url}")

def check_samcart_practice_accounts():
    """Check for practice accounts created from SamCart webhooks"""
    
    print("\n" + "="*80)
    print("🏥 SAMCART PRACTICE ACCOUNT VERIFICATION")
    print("   Checking for practice accounts created from webhook activity")
    print("="*80)
    
    try:
        # First, get admin login to access practice data
        print("\n1️⃣ AUTHENTICATING AS ADMIN...")
        admin_login_url = f"{backend_url}/api/admin/login"
        
        admin_credentials = {
            "email": "cganz@admin.com",
            "password": "Dentist1#"
        }
        
        try:
            admin_response = requests.post(admin_login_url, json=admin_credentials, timeout=10)
            print(f"   📡 POST {admin_login_url}")
            print(f"   📊 Status: {admin_response.status_code}")
            
            if admin_response.status_code == 200:
                admin_data = admin_response.json()
                admin_token = admin_data.get('token')
                print(f"   ✅ Admin authentication successful")
                
                # 2. Get all practices to check for SamCart-created ones
                print("\n2️⃣ CHECKING FOR SAMCART PRACTICE ACCOUNTS...")
                practices_url = f"{backend_url}/api/admin/practices"
                
                headers = {"Authorization": f"Bearer {admin_token}"}
                practices_response = requests.get(practices_url, headers=headers, timeout=10)
                print(f"   📡 GET {practices_url}")
                print(f"   📊 Status: {practices_response.status_code}")
                
                if practices_response.status_code == 200:
                    practices_data = practices_response.json()
                    all_practices = practices_data.get('practices', [])
                    
                    print(f"   📋 Total practices found: {len(all_practices)}")
                    
                    # Filter for SamCart practices
                    samcart_practices = [p for p in all_practices if p.get('source') == 'samcart']
                    
                    if samcart_practices:
                        print(f"   ✅ Found {len(samcart_practices)} SamCart practice accounts!")
                        
                        # Show recent SamCart practices
                        target_time = datetime.now(timezone.utc).replace(hour=17, minute=55, second=0, microsecond=0)
                        if datetime.now(timezone.utc) < target_time:
                            target_time = target_time - timedelta(days=1)
                        
                        recent_practices = []
                        for practice in samcart_practices:
                            try:
                                created_at = practice.get('createdAt')
                                if isinstance(created_at, str):
                                    if created_at.endswith('Z'):
                                        practice_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                    else:
                                        practice_time = datetime.fromisoformat(created_at)
                                        if practice_time.tzinfo is None:
                                            practice_time = practice_time.replace(tzinfo=timezone.utc)
                                    
                                    if practice_time >= target_time:
                                        recent_practices.append(practice)
                            except Exception as e:
                                continue
                        
                        if recent_practices:
                            print(f"   🎯 {len(recent_practices)} practice accounts created since 5:55 PM today:")
                            
                            for i, practice in enumerate(recent_practices[:5], 1):  # Show first 5
                                try:
                                    created_at = practice.get('createdAt')
                                    if isinstance(created_at, str):
                                        if created_at.endswith('Z'):
                                            practice_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                        else:
                                            practice_time = datetime.fromisoformat(created_at)
                                            if practice_time.tzinfo is None:
                                                practice_time = practice_time.replace(tzinfo=timezone.utc)
                                    
                                    print(f"      {i}. {practice.get('name', 'Unknown Practice')}")
                                    print(f"         Email: {practice.get('email', 'N/A')}")
                                    print(f"         Owner: {practice.get('ownerName', 'N/A')}")
                                    print(f"         Created: {practice_time.strftime('%H:%M:%S')} UTC")
                                    print(f"         Status: {practice.get('subscription', {}).get('status', 'N/A')}")
                                    
                                    # Check SamCart data
                                    samcart_data = practice.get('samcartData', {})
                                    if samcart_data:
                                        print(f"         SamCart Order ID: {samcart_data.get('orderId', 'N/A')}")
                                    print()
                                except Exception as e:
                                    print(f"      {i}. Practice (timestamp parse error)")
                                    print(f"         Email: {practice.get('email', 'N/A')}")
                                    print()
                        else:
                            print(f"   ⚠️ No SamCart practice accounts created since 5:55 PM today")
                            
                            # Show most recent SamCart practice for context
                            if samcart_practices:
                                latest_practice = max(samcart_practices, key=lambda p: p.get('createdAt', ''))
                                try:
                                    created_at = latest_practice.get('createdAt')
                                    if isinstance(created_at, str):
                                        if created_at.endswith('Z'):
                                            latest_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                        else:
                                            latest_time = datetime.fromisoformat(created_at)
                                            if latest_time.tzinfo is None:
                                                latest_time = latest_time.replace(tzinfo=timezone.utc)
                                        
                                        print(f"   📝 Most recent SamCart practice: {latest_practice.get('name', 'Unknown')} at {latest_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
                                except Exception as e:
                                    print(f"   📝 Most recent SamCart practice: {latest_practice.get('name', 'Unknown')} (timestamp parse error)")
                        
                        # Show all SamCart practices summary
                        print(f"\n   📊 All SamCart Practice Accounts Summary:")
                        for i, practice in enumerate(samcart_practices, 1):
                            print(f"      {i}. {practice.get('name', 'Unknown')} ({practice.get('email', 'N/A')})")
                            subscription = practice.get('subscription', {})
                            print(f"         Status: {subscription.get('status', 'N/A')} | Trial End: {subscription.get('trialEndDate', 'N/A')}")
                    
                    else:
                        print(f"   ⚠️ No SamCart practice accounts found")
                        print(f"   📝 This could mean:")
                        print(f"      • Webhook events were test events, not real account creations")
                        print(f"      • Practice accounts were created but not marked with 'source': 'samcart'")
                        print(f"      • Database query issue")
                
                else:
                    print(f"   ❌ Failed to fetch practices: {practices_response.status_code}")
                    if practices_response.text:
                        print(f"   📄 Response: {practices_response.text[:200]}")
            
            else:
                print(f"   ❌ Admin authentication failed: {admin_response.status_code}")
                if admin_response.text:
                    print(f"   📄 Response: {admin_response.text[:200]}")
                    
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        
        print("\n" + "="*80)
        print("📋 PRACTICE ACCOUNT VERIFICATION COMPLETE")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Verification error: {e}")

if __name__ == "__main__":
    check_samcart_practice_accounts()
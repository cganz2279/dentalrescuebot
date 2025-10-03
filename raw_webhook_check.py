#!/usr/bin/env python3
"""
Raw webhook data check to see exactly what's in the logs
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"

def get_raw_webhook_data():
    """Get raw webhook data to understand the structure"""
    print("🔍 RAW WEBHOOK DATA ANALYSIS")
    print("="*60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/webhook/samcart/logs")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            raw_data = response.text
            print(f"Raw Response Length: {len(raw_data)} characters")
            print(f"Raw Response Type: {type(raw_data)}")
            
            try:
                logs = response.json()
                print(f"Parsed JSON Type: {type(logs)}")
                print(f"Number of items: {len(logs) if isinstance(logs, list) else 'Not a list'}")
                
                print("\n📋 RAW WEBHOOK LOGS:")
                print(json.dumps(logs, indent=2))
                
                # Check if it's a list or dict
                if isinstance(logs, list):
                    print(f"\n✅ Found {len(logs)} webhook log entries")
                    
                    for i, log in enumerate(logs):
                        print(f"\n--- LOG ENTRY #{i+1} ---")
                        print(f"Type: {type(log)}")
                        if isinstance(log, dict):
                            for key, value in log.items():
                                print(f"{key}: {value}")
                        else:
                            print(f"Content: {log}")
                            
                elif isinstance(logs, dict):
                    print("\n✅ Response is a dictionary:")
                    for key, value in logs.items():
                        print(f"{key}: {value}")
                        
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Raw response: {raw_data[:500]}...")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request error: {e}")

def check_webhook_stats_raw():
    """Get raw webhook stats"""
    print(f"\n🔍 RAW WEBHOOK STATS")
    print("="*60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/webhook/samcart/stats")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print("Raw Stats Data:")
            print(json.dumps(stats, indent=2))
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request error: {e}")

def main():
    print("🚨 RAW WEBHOOK DATA INVESTIGATION")
    print(f"Time: {datetime.utcnow().isoformat()}Z")
    
    get_raw_webhook_data()
    check_webhook_stats_raw()

if __name__ == "__main__":
    main()
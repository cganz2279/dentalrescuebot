#!/usr/bin/env python3
"""
Procedures Database Discrepancy Investigation Test
Testing /api/procedures endpoint to identify why only 86 procedures are returned when 97 should exist
"""

import requests
import json
import sys
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = "https://dentist-dashboard-2.preview.emergentagent.com"
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

def test_procedures_api():
    """Test the /api/procedures endpoint and analyze the response"""
    print("🔍 TESTING /api/procedures ENDPOINT")
    print("=" * 60)
    
    try:
        # Make API request
        url = f"{BACKEND_URL}/api/procedures"
        print(f"📡 Making GET request to: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"📊 Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response Structure: {list(data.keys())}")
            
            if 'data' in data:
                procedures = data['data']
                count = len(procedures)
                print(f"📈 PROCEDURES COUNT FROM API: {count}")
                
                # Check if count is also in response
                if 'count' in data:
                    api_count = data['count']
                    print(f"📈 COUNT FIELD IN RESPONSE: {api_count}")
                
                # Analyze procedures for missing ones
                analyze_procedures_for_missing_items(procedures)
                
                return procedures, count
            else:
                print("❌ No 'data' field in API response")
                print(f"Response: {data}")
                return [], 0
        else:
            print(f"❌ API Request Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return [], 0
            
    except Exception as e:
        print(f"❌ API Request Error: {str(e)}")
        return [], 0

def analyze_procedures_for_missing_items(procedures):
    """Analyze procedures to look for specific missing items"""
    print("\n🔍 ANALYZING PROCEDURES FOR MISSING ITEMS")
    print("=" * 60)
    
    # Target procedures to look for
    target_procedures = [
        "All On X Post Op Instructions",
        "Final Zirconia Implant Prosthesis Post Op Instructions"
    ]
    
    # Search terms
    search_terms = {
        "All On X": [],
        "Zirconia": [],
        "Zirconium": [],
        "Final": []
    }
    
    print(f"📋 Total procedures to analyze: {len(procedures)}")
    
    # Look for target procedures
    print(f"\n🎯 SEARCHING FOR SPECIFIC TARGET PROCEDURES:")
    for target in target_procedures:
        found = False
        for proc in procedures:
            if proc.get('name', '').strip() == target:
                print(f"✅ FOUND: {target}")
                found = True
                break
        if not found:
            print(f"❌ MISSING: {target}")
    
    # Search for procedures containing key terms
    print(f"\n🔍 SEARCHING FOR PROCEDURES CONTAINING KEY TERMS:")
    for term in search_terms:
        for proc in procedures:
            name = proc.get('name', '')
            if term.lower() in name.lower():
                search_terms[term].append(name)
    
    # Display results
    for term, matches in search_terms.items():
        print(f"🔍 '{term}' matches ({len(matches)}):")
        if matches:
            for match in matches:
                print(f"   ✅ {match}")
        else:
            print(f"   ❌ No procedures found containing '{term}'")
    
    # Show procedure specialties distribution
    print(f"\n📊 PROCEDURES BY SPECIALTY:")
    specialty_counts = {}
    for proc in procedures:
        specialty = proc.get('specialtyName', proc.get('specialty', 'Unknown'))
        specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1
    
    for specialty, count in sorted(specialty_counts.items()):
        print(f"   {specialty}: {count} procedures")

def test_database_direct():
    """Directly query MongoDB to get the actual count"""
    print("\n🗄️ TESTING DIRECT DATABASE ACCESS")
    print("=" * 60)
    
    try:
        # Connect to MongoDB
        print(f"🔌 Connecting to MongoDB: {MONGO_URL}")
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Get total count
        total_count = db.procedures.count_documents({})
        print(f"📊 TOTAL PROCEDURES IN DATABASE: {total_count}")
        
        # Get all procedures
        all_procedures = list(db.procedures.find({}, {"_id": 0}))
        actual_count = len(all_procedures)
        print(f"📊 ACTUAL PROCEDURES RETRIEVED: {actual_count}")
        
        # Look for specific missing procedures
        print(f"\n🎯 SEARCHING DATABASE FOR MISSING PROCEDURES:")
        target_procedures = [
            "All On X Post Op Instructions",
            "Final Zirconia Implant Prosthesis Post Op Instructions"
        ]
        
        for target in target_procedures:
            found_proc = db.procedures.find_one({"name": target})
            if found_proc:
                print(f"✅ FOUND IN DB: {target}")
                print(f"   ID: {found_proc.get('id', 'N/A')}")
                print(f"   Specialty: {found_proc.get('specialtyName', 'N/A')}")
            else:
                print(f"❌ NOT FOUND IN DB: {target}")
        
        # Search for procedures with key terms
        print(f"\n🔍 SEARCHING DATABASE FOR KEY TERMS:")
        search_terms = ["All On X", "Zirconia", "Zirconium", "Final"]
        
        for term in search_terms:
            # Case-insensitive search
            regex_pattern = {"$regex": term, "$options": "i"}
            matches = list(db.procedures.find({"name": regex_pattern}, {"name": 1, "id": 1, "_id": 0}))
            print(f"🔍 '{term}' matches in database ({len(matches)}):")
            if matches:
                for match in matches:
                    print(f"   ✅ {match.get('name')} (ID: {match.get('id')})")
            else:
                print(f"   ❌ No procedures found containing '{term}'")
        
        client.close()
        return total_count, actual_count, all_procedures
        
    except Exception as e:
        print(f"❌ Database Connection Error: {str(e)}")
        return 0, 0, []

def compare_api_vs_database(api_procedures, api_count, db_count, db_procedures):
    """Compare API results vs database results"""
    print("\n⚖️ COMPARING API VS DATABASE RESULTS")
    print("=" * 60)
    
    print(f"📊 API Count: {api_count}")
    print(f"📊 Database Count: {db_count}")
    print(f"📊 Discrepancy: {db_count - api_count} procedures missing from API")
    
    if db_count > api_count:
        print(f"❌ DISCREPANCY CONFIRMED: API is missing {db_count - api_count} procedures")
        
        # Find which procedures are missing from API
        api_ids = {proc.get('id') for proc in api_procedures}
        db_ids = {proc.get('id') for proc in db_procedures}
        
        missing_ids = db_ids - api_ids
        print(f"\n🔍 MISSING PROCEDURE IDs FROM API ({len(missing_ids)}):")
        
        missing_procedures = []
        for proc in db_procedures:
            if proc.get('id') in missing_ids:
                missing_procedures.append(proc)
                print(f"   ❌ {proc.get('name')} (ID: {proc.get('id')}, Specialty: {proc.get('specialtyName', 'N/A')})")
        
        # Check if missing procedures include our target ones
        print(f"\n🎯 CHECKING IF TARGET PROCEDURES ARE IN MISSING LIST:")
        target_procedures = [
            "All On X Post Op Instructions",
            "Final Zirconia Implant Prosthesis Post Op Instructions"
        ]
        
        for target in target_procedures:
            found_in_missing = any(proc.get('name') == target for proc in missing_procedures)
            if found_in_missing:
                print(f"✅ TARGET PROCEDURE FOUND IN MISSING LIST: {target}")
            else:
                print(f"❌ TARGET PROCEDURE NOT IN MISSING LIST: {target}")
        
    elif db_count == api_count:
        print(f"✅ NO DISCREPANCY: API and Database counts match")
    else:
        print(f"⚠️ UNEXPECTED: API count ({api_count}) is higher than database count ({db_count})")

def main():
    """Main test function"""
    print("🚀 PROCEDURES DATABASE DISCREPANCY INVESTIGATION")
    print("=" * 80)
    print("Goal: Identify why API returns 86 procedures when 97 should exist")
    print("Focus: Missing 'All On X' and 'Zirconia' procedures")
    print("=" * 80)
    
    # Test API
    api_procedures, api_count = test_procedures_api()
    
    # Test Database
    db_count, actual_db_count, db_procedures = test_database_direct()
    
    # Compare results
    if api_procedures and db_procedures:
        compare_api_vs_database(api_procedures, api_count, actual_db_count, db_procedures)
    
    # Final summary
    print("\n📋 INVESTIGATION SUMMARY")
    print("=" * 60)
    print(f"✅ API Endpoint Tested: /api/procedures")
    print(f"📊 API Returned: {api_count} procedures")
    print(f"📊 Database Contains: {actual_db_count} procedures")
    
    if actual_db_count > api_count:
        print(f"❌ CONFIRMED DISCREPANCY: {actual_db_count - api_count} procedures missing from API")
        print(f"🔍 Root Cause Investigation Required")
    else:
        print(f"✅ No discrepancy found - counts match")
    
    print("\n🎯 NEXT STEPS:")
    if actual_db_count > api_count:
        print("1. Check API query logic in backend/server.py line 211-230")
        print("2. Verify MongoDB query filters and limits")
        print("3. Check for data corruption or indexing issues")
        print("4. Investigate if procedures are being filtered out")
    else:
        print("1. Verify the expected count of 97 procedures")
        print("2. Check if specific procedures were recently added/removed")
        print("3. Confirm the source of the 97 procedure count expectation")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
CRITICAL DISCREPANCY INVESTIGATION: Active Procedures Count
User reports seeing only 6 active procedures, but backend API returns 11.
This test investigates the root cause of this 6 vs 11 discrepancy.
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

# Configuration
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "dentist_management"

class ActiveProceduresDiscrepancyTest:
    def __init__(self):
        self.session = None
        self.token = None
        self.practice_id = None
        self.mongo_client = None
        self.db = None

    async def setup(self):
        """Setup test environment"""
        self.session = aiohttp.ClientSession()
        
        # Setup MongoDB connection
        self.mongo_client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.mongo_client[DB_NAME]
        
        print("🔧 Test setup completed")

    async def cleanup(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()
        if self.mongo_client:
            self.mongo_client.close()

    async def authenticate(self):
        """Authenticate with practice credentials"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            async with self.session.post(f"{BACKEND_URL}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data["token"]
                    self.practice_id = data["user"]["practiceId"]
                    print(f"✅ Authentication successful")
                    print(f"   Practice ID: {self.practice_id}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False

    async def test_dashboard_api_response(self):
        """Test the dashboard API response to see what activeProcedures returns"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            async with self.session.get(f"{BACKEND_URL}/api/practice/dashboard", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    active_procedures = data["data"]["stats"]["activeProcedures"]
                    print(f"🔍 DASHBOARD API RESPONSE:")
                    print(f"   Active Procedures Count: {active_procedures}")
                    print(f"   Patient Count: {data['data']['stats']['patientCount']}")
                    print(f"   Recent Procedures Count: {len(data['data']['recentProcedures'])}")
                    
                    # Show recent procedures details
                    print(f"\n📋 RECENT PROCEDURES DETAILS:")
                    for i, proc in enumerate(data['data']['recentProcedures'][:10]):
                        print(f"   {i+1}. {proc['procedureName']} - Status: {proc['status']} - Patient: {proc.get('patientName', 'Unknown')}")
                    
                    return active_procedures
                else:
                    error_text = await response.text()
                    print(f"❌ Dashboard API failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            print(f"❌ Dashboard API error: {e}")
            return None

    async def test_direct_database_query(self):
        """Test the exact same database query that the dashboard API uses"""
        try:
            print(f"\n🔍 DIRECT DATABASE QUERY INVESTIGATION:")
            print(f"   Practice ID: {self.practice_id}")
            
            # Execute the exact same query as the dashboard API
            query = {
                "practiceId": self.practice_id,
                "status": "active"
            }
            
            print(f"   Query: {query}")
            
            # Count documents
            count = await self.db.patientprocedures.count_documents(query)
            print(f"   Direct DB Count: {count}")
            
            # Get all matching documents to analyze
            cursor = self.db.patientprocedures.find(query, {"_id": 0})
            procedures = await cursor.to_list(length=None)
            
            print(f"\n📊 DETAILED ANALYSIS OF {count} ACTIVE PROCEDURES:")
            for i, proc in enumerate(procedures, 1):
                patient_name = "Unknown"
                if proc.get("patientId"):
                    patient = await self.db.users.find_one(
                        {"id": proc["patientId"]}, 
                        {"firstName": 1, "lastName": 1, "_id": 0}
                    )
                    if patient:
                        patient_name = f"{patient['firstName']} {patient['lastName']}"
                
                print(f"   {i:2d}. {proc['procedureName']:25} | Patient: {patient_name:20} | Date: {proc.get('performedDate', 'N/A')}")
            
            return count, procedures
            
        except Exception as e:
            print(f"❌ Direct database query error: {e}")
            return None, None

    async def investigate_potential_filters(self):
        """Investigate potential filters that could reduce 11 to 6"""
        try:
            print(f"\n🔍 INVESTIGATING POTENTIAL FILTERS:")
            
            # Check for date-based filtering
            from datetime import datetime, timedelta
            
            # Recent procedures (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_query = {
                "practiceId": self.practice_id,
                "status": "active",
                "performedDate": {"$gte": thirty_days_ago}
            }
            recent_count = await self.db.patientprocedures.count_documents(recent_query)
            print(f"   Recent (30 days) Active Procedures: {recent_count}")
            
            # Very recent procedures (last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            very_recent_query = {
                "practiceId": self.practice_id,
                "status": "active",
                "performedDate": {"$gte": seven_days_ago}
            }
            very_recent_count = await self.db.patientprocedures.count_documents(very_recent_query)
            print(f"   Very Recent (7 days) Active Procedures: {very_recent_count}")
            
            # Check for limit-based filtering (top 6)
            cursor = self.db.patientprocedures.find(
                {"practiceId": self.practice_id, "status": "active"},
                {"_id": 0, "procedureName": 1, "performedDate": 1}
            ).sort("performedDate", -1).limit(6)
            top_6_procedures = await cursor.to_list(length=None)
            print(f"   Top 6 Most Recent Active Procedures:")
            for i, proc in enumerate(top_6_procedures, 1):
                print(f"      {i}. {proc['procedureName']} - {proc.get('performedDate', 'N/A')}")
            
            # Check for patient-based filtering (active patients only)
            active_patients = await self.db.users.find(
                {
                    "practiceId": self.practice_id,
                    "role": "patient",
                    "isActive": True
                },
                {"id": 1, "_id": 0}
            ).to_list(length=None)
            
            active_patient_ids = [p["id"] for p in active_patients]
            active_patient_procedures_query = {
                "practiceId": self.practice_id,
                "status": "active",
                "patientId": {"$in": active_patient_ids}
            }
            active_patient_procedures_count = await self.db.patientprocedures.count_documents(active_patient_procedures_query)
            print(f"   Active Procedures for Active Patients Only: {active_patient_procedures_count}")
            
            return {
                "recent_30_days": recent_count,
                "recent_7_days": very_recent_count,
                "top_6_most_recent": len(top_6_procedures),
                "active_patients_only": active_patient_procedures_count
            }
            
        except Exception as e:
            print(f"❌ Filter investigation error: {e}")
            return None

    async def check_frontend_data_flow(self):
        """Check if there might be frontend filtering happening"""
        try:
            print(f"\n🔍 FRONTEND DATA FLOW INVESTIGATION:")
            
            # Check if there are any other endpoints that might return different counts
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Check patients endpoint
            async with self.session.get(f"{BACKEND_URL}/api/practice/patients", headers=headers) as response:
                if response.status == 200:
                    patients_data = await response.json()
                    print(f"   Total Patients from /patients endpoint: {len(patients_data['data'])}")
                    
                    # Check procedure counts per patient
                    total_procedures = sum(p.get('procedureCount', 0) for p in patients_data['data'])
                    print(f"   Total Procedures across all patients: {total_procedures}")
            
            # Check export data endpoint
            async with self.session.get(f"{BACKEND_URL}/api/practice/export-data", headers=headers) as response:
                if response.status == 200:
                    export_data = await response.json()
                    patients_with_procedures = export_data['data']['patients']
                    
                    total_active_procedures = 0
                    for patient in patients_with_procedures:
                        active_procs = [p for p in patient.get('assignedProcedures', []) if p.get('status') == 'active']
                        total_active_procedures += len(active_procs)
                    
                    print(f"   Active Procedures from /export-data endpoint: {total_active_procedures}")
            
        except Exception as e:
            print(f"❌ Frontend data flow investigation error: {e}")

    async def run_comprehensive_investigation(self):
        """Run comprehensive investigation of the 6 vs 11 discrepancy"""
        print("🚨 CRITICAL DISCREPANCY INVESTIGATION: Active Procedures Count")
        print("=" * 70)
        print("User reports seeing only 6 active procedures, but backend API returns 11.")
        print("Investigating the root cause of this discrepancy...")
        print()
        
        # Setup
        await self.setup()
        
        # Authenticate
        if not await self.authenticate():
            return
        
        # Test dashboard API response
        api_count = await self.test_dashboard_api_response()
        
        # Test direct database query
        db_count, procedures = await self.test_direct_database_query()
        
        # Investigate potential filters
        filter_results = await self.investigate_potential_filters()
        
        # Check frontend data flow
        await self.check_frontend_data_flow()
        
        # Summary and analysis
        print(f"\n🎯 DISCREPANCY ANALYSIS SUMMARY:")
        print("=" * 50)
        print(f"Dashboard API Returns: {api_count}")
        print(f"Direct Database Query: {db_count}")
        print(f"User Reports Seeing: 6")
        print()
        
        if filter_results:
            print("🔍 POTENTIAL CAUSES OF 6 vs 11 DISCREPANCY:")
            if filter_results.get("top_6_most_recent") == 6:
                print("   ⚠️  LIKELY CAUSE: Frontend may be showing only the 6 most recent active procedures")
            if filter_results.get("recent_30_days") == 6:
                print("   ⚠️  POSSIBLE CAUSE: Frontend may be filtering to recent procedures (30 days)")
            if filter_results.get("recent_7_days") == 6:
                print("   ⚠️  POSSIBLE CAUSE: Frontend may be filtering to very recent procedures (7 days)")
            if filter_results.get("active_patients_only") != db_count:
                print("   ⚠️  POSSIBLE CAUSE: Some procedures may be for inactive patients")
        
        print()
        print("🎯 CONCLUSION:")
        if api_count == 11 and db_count == 11:
            print("   ✅ Backend is correctly returning 11 active procedures")
            print("   ❌ Issue is likely in FRONTEND DISPLAY or FILTERING")
            print("   🔧 RECOMMENDATION: Check frontend code for limits, pagination, or date filters")
        else:
            print("   ❌ Backend inconsistency detected")
            print("   🔧 RECOMMENDATION: Investigate backend query logic")
        
        # Cleanup
        await self.cleanup()

async def main():
    """Main test execution"""
    test = ActiveProceduresDiscrepancyTest()
    await test.run_comprehensive_investigation()

if __name__ == "__main__":
    asyncio.run(main())
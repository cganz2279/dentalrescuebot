#!/usr/bin/env python3
"""
DASHBOARD LIMIT INVESTIGATION: Recent Procedures vs Active Procedures
The backend dashboard API limits recent procedures to 10, but user sees only 6.
This test investigates the exact data flow.
"""

import asyncio
import aiohttp
import json
from motor.motor_asyncio import AsyncIOMotorClient

# Configuration
BACKEND_URL = "https://dentiportal.preview.emergentagent.com"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "dentist_management"

class DashboardLimitInvestigation:
    def __init__(self):
        self.session = None
        self.token = None
        self.practice_id = None
        self.mongo_client = None
        self.db = None

    async def setup(self):
        """Setup test environment"""
        self.session = aiohttp.ClientSession()
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

    async def investigate_dashboard_data_flow(self):
        """Investigate the exact data flow in dashboard API"""
        try:
            print(f"\n🔍 DASHBOARD DATA FLOW INVESTIGATION:")
            print("=" * 60)
            
            # 1. Test the exact query for activeProcedures count
            active_procedures_query = {
                "practiceId": self.practice_id,
                "status": "active"
            }
            active_count = await self.db.patientprocedures.count_documents(active_procedures_query)
            print(f"1. Active Procedures Count: {active_count}")
            
            # 2. Test the exact query for recent procedures (with limit 10)
            recent_procedures_query = {"practiceId": self.practice_id}
            cursor = self.db.patientprocedures.find(
                recent_procedures_query,
                {"_id": 0}
            ).sort("performedDate", -1).limit(10)
            recent_procedures = await cursor.to_list(length=None)
            print(f"2. Recent Procedures (limit 10): {len(recent_procedures)}")
            
            # 3. Count how many of the recent procedures are active
            active_recent_count = sum(1 for p in recent_procedures if p.get('status') == 'active')
            print(f"3. Active procedures in Recent Procedures: {active_recent_count}")
            
            # 4. Show the status breakdown of recent procedures
            status_breakdown = {}
            for proc in recent_procedures:
                status = proc.get('status', 'unknown')
                status_breakdown[status] = status_breakdown.get(status, 0) + 1
            
            print(f"4. Status breakdown of Recent Procedures:")
            for status, count in status_breakdown.items():
                print(f"   - {status}: {count}")
            
            # 5. Show detailed recent procedures
            print(f"\n📋 DETAILED RECENT PROCEDURES (limit 10):")
            for i, proc in enumerate(recent_procedures, 1):
                patient_name = "Unknown"
                if proc.get("patientId"):
                    patient = await self.db.users.find_one(
                        {"id": proc["patientId"]}, 
                        {"firstName": 1, "lastName": 1, "_id": 0}
                    )
                    if patient:
                        patient_name = f"{patient['firstName']} {patient['lastName']}"
                
                print(f"   {i:2d}. {proc['procedureName']:25} | Status: {proc.get('status', 'N/A'):8} | Patient: {patient_name:20} | Date: {proc.get('performedDate', 'N/A')}")
            
            # 6. Test dashboard API response
            headers = {"Authorization": f"Bearer {self.token}"}
            async with self.session.get(f"{BACKEND_URL}/api/practice/dashboard", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    api_active_procedures = data["data"]["stats"]["activeProcedures"]
                    api_recent_procedures = len(data["data"]["recentProcedures"])
                    
                    print(f"\n🌐 DASHBOARD API RESPONSE:")
                    print(f"   Active Procedures: {api_active_procedures}")
                    print(f"   Recent Procedures returned: {api_recent_procedures}")
                    
                    # Count active procedures in API response
                    api_active_in_recent = sum(1 for p in data["data"]["recentProcedures"] if p.get('status') == 'active')
                    print(f"   Active procedures in Recent Procedures: {api_active_in_recent}")
                    
                    # Show API recent procedures
                    print(f"\n📋 API RECENT PROCEDURES:")
                    for i, proc in enumerate(data["data"]["recentProcedures"], 1):
                        print(f"   {i:2d}. {proc['procedureName']:25} | Status: {proc.get('status', 'N/A'):8} | Patient: {proc.get('patientName', 'Unknown'):20}")
            
            return {
                "db_active_count": active_count,
                "db_recent_count": len(recent_procedures),
                "db_active_in_recent": active_recent_count,
                "api_active_count": api_active_procedures,
                "api_recent_count": api_recent_procedures,
                "api_active_in_recent": api_active_in_recent
            }
            
        except Exception as e:
            print(f"❌ Investigation error: {e}")
            return None

    async def run_investigation(self):
        """Run the complete investigation"""
        print("🚨 DASHBOARD LIMIT INVESTIGATION")
        print("=" * 50)
        print("Investigating why user sees 6 active procedures when backend returns 11")
        print()
        
        await self.setup()
        
        if not await self.authenticate():
            return
        
        results = await self.investigate_dashboard_data_flow()
        
        if results:
            print(f"\n🎯 ANALYSIS SUMMARY:")
            print("=" * 40)
            print(f"Database Active Procedures: {results['db_active_count']}")
            print(f"Database Recent Procedures (limit 10): {results['db_recent_count']}")
            print(f"Active procedures in Recent list: {results['db_active_in_recent']}")
            print(f"API Active Procedures: {results['api_active_count']}")
            print(f"API Recent Procedures: {results['api_recent_count']}")
            print(f"Active procedures in API Recent list: {results['api_active_in_recent']}")
            
            print(f"\n🔍 ROOT CAUSE ANALYSIS:")
            if results['api_active_in_recent'] == 6:
                print("   ✅ CONFIRMED: User sees 6 because only 6 of the 10 most recent procedures are 'active'")
                print("   📊 The dashboard shows 'Active Procedures: 11' (total active)")
                print("   📊 But 'Recent Procedures' section shows only 6 active procedures")
                print("   🎯 USER CONFUSION: User is looking at Recent Procedures section, not the stats card")
            else:
                print("   ❓ Need further investigation")
        
        await self.cleanup()

async def main():
    """Main test execution"""
    test = DashboardLimitInvestigation()
    await test.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
FRONTEND DISPLAY INVESTIGATION: Check for CSS/display issues
The backend returns 10 active procedures, but user sees only 6.
This suggests a frontend display issue.
"""

import asyncio
import aiohttp
import json

# Configuration
BACKEND_URL = "https://dentiportal.preview.emergentagent.com"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class FrontendDisplayInvestigation:
    def __init__(self):
        self.session = None
        self.token = None

    async def setup(self):
        """Setup test environment"""
        self.session = aiohttp.ClientSession()
        print("🔧 Test setup completed")

    async def cleanup(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()

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
                    print(f"✅ Authentication successful")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False

    async def test_dashboard_response_details(self):
        """Test dashboard response in detail to understand the data structure"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            async with self.session.get(f"{BACKEND_URL}/api/practice/dashboard", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    print(f"🔍 DETAILED DASHBOARD API ANALYSIS:")
                    print("=" * 60)
                    
                    # Stats section
                    stats = data["data"]["stats"]
                    print(f"📊 STATS SECTION:")
                    print(f"   - patientCount: {stats.get('patientCount', 'N/A')}")
                    print(f"   - activeProcedures: {stats.get('activeProcedures', 'N/A')}")
                    print(f"   - subscriptionStatus: {stats.get('subscriptionStatus', 'N/A')}")
                    
                    # Recent procedures section
                    recent_procedures = data["data"]["recentProcedures"]
                    print(f"\n📋 RECENT PROCEDURES SECTION:")
                    print(f"   - Total count: {len(recent_procedures)}")
                    
                    # Analyze each procedure in detail
                    active_count = 0
                    for i, proc in enumerate(recent_procedures, 1):
                        status = proc.get('status', 'N/A')
                        if status == 'active':
                            active_count += 1
                        
                        print(f"   {i:2d}. {proc.get('procedureName', 'N/A'):25} | Status: {status:8} | Patient: {proc.get('patientName', 'N/A'):20} | ID: {proc.get('id', 'N/A')}")
                    
                    print(f"\n🎯 ANALYSIS:")
                    print(f"   - Active procedures in stats: {stats.get('activeProcedures', 'N/A')}")
                    print(f"   - Active procedures in recent list: {active_count}")
                    print(f"   - Total procedures in recent list: {len(recent_procedures)}")
                    
                    # Check if there are any procedures with missing data
                    missing_data_count = 0
                    for proc in recent_procedures:
                        if not proc.get('patientName') or not proc.get('procedureName'):
                            missing_data_count += 1
                            print(f"   ⚠️  Procedure with missing data: {proc}")
                    
                    if missing_data_count > 0:
                        print(f"   - Procedures with missing data: {missing_data_count}")
                    
                    # Check for any filtering that might happen on frontend
                    print(f"\n🔍 POTENTIAL FRONTEND FILTERING ISSUES:")
                    
                    # Check if any procedures have null/undefined patient names
                    null_patient_count = sum(1 for p in recent_procedures if not p.get('patientName'))
                    if null_patient_count > 0:
                        print(f"   - Procedures with null/missing patientName: {null_patient_count}")
                        print("   - These might be filtered out by frontend")
                    
                    # Check if any procedures have invalid dates
                    invalid_date_count = 0
                    for proc in recent_procedures:
                        if not proc.get('performedDate'):
                            invalid_date_count += 1
                    
                    if invalid_date_count > 0:
                        print(f"   - Procedures with missing performedDate: {invalid_date_count}")
                    
                    # Check for duplicate procedure IDs
                    procedure_ids = [p.get('id') for p in recent_procedures if p.get('id')]
                    duplicate_ids = len(procedure_ids) - len(set(procedure_ids))
                    if duplicate_ids > 0:
                        print(f"   - Duplicate procedure IDs: {duplicate_ids}")
                    
                    return {
                        "stats_active": stats.get('activeProcedures', 0),
                        "recent_total": len(recent_procedures),
                        "recent_active": active_count,
                        "missing_data": missing_data_count,
                        "null_patients": null_patient_count,
                        "invalid_dates": invalid_date_count,
                        "duplicate_ids": duplicate_ids
                    }
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Dashboard API failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            print(f"❌ Dashboard API error: {e}")
            return None

    async def run_investigation(self):
        """Run the complete investigation"""
        print("🚨 FRONTEND DISPLAY INVESTIGATION")
        print("=" * 50)
        print("Investigating why user sees 6 active procedures when API returns 10")
        print()
        
        await self.setup()
        
        if not await self.authenticate():
            return
        
        results = await self.test_dashboard_response_details()
        
        if results:
            print(f"\n🎯 FINAL ANALYSIS:")
            print("=" * 40)
            print(f"Stats Active Procedures: {results['stats_active']}")
            print(f"Recent Procedures Total: {results['recent_total']}")
            print(f"Recent Procedures Active: {results['recent_active']}")
            
            if results['null_patients'] > 0:
                print(f"⚠️  POTENTIAL ISSUE: {results['null_patients']} procedures have missing patient names")
                print("   This could cause frontend filtering/display issues")
            
            if results['missing_data'] > 0:
                print(f"⚠️  POTENTIAL ISSUE: {results['missing_data']} procedures have missing data")
            
            if results['recent_active'] == 6:
                print("✅ CONFIRMED: Only 6 active procedures in recent list")
                print("🎯 ROOT CAUSE: User is looking at Recent Procedures section")
                print("   The 'Active Procedures: 11' stat is correct")
                print("   But Recent Procedures only shows 6 active ones")
            elif results['recent_active'] == 10:
                print("❓ MYSTERY: API returns 10 active in recent, but user sees 6")
                print("🔧 RECOMMENDATION: Check frontend CSS, scrolling, or display issues")
                print("   - Check if container height limits visible procedures")
                print("   - Check if there's pagination or 'show more' functionality")
                print("   - Check browser console for JavaScript errors")
        
        await self.cleanup()

async def main():
    """Main test execution"""
    test = FrontendDisplayInvestigation()
    await test.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())
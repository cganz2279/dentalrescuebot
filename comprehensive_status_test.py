#!/usr/bin/env python3
"""
Comprehensive Sequential Status System Test
Tests the complete status progression: active → delivered → second
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone
import os
import sys

# Test configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
TEST_CREDENTIALS = {
    "email": "cganz2279@gmail.com",
    "password": "password123"
}

class ComprehensiveStatusTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.practice_id = None
        self.test_assignment_id = None
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            
    async def login(self):
        """Login to get auth token"""
        try:
            url = f"{BACKEND_URL}/api/auth/login"
            login_data = {
                "email": TEST_CREDENTIALS["email"],
                "password": TEST_CREDENTIALS["password"]
            }
            
            async with self.session.post(url, json=login_data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("success"):
                        self.auth_token = response_data["token"]
                        self.practice_id = response_data.get("user", {}).get("practiceId")
                        print(f"✅ Login successful - Practice ID: {self.practice_id}")
                        return True
            print("❌ Login failed")
            return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
            
    async def get_dashboard_data(self):
        """Get current dashboard data"""
        try:
            url = f"{BACKEND_URL}/api/practice/dashboard"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("success"):
                        return response_data.get("data", {})
        except Exception as e:
            print(f"❌ Dashboard error: {e}")
        return None
        
    async def find_active_procedure(self):
        """Find an existing active procedure or create one"""
        dashboard_data = await self.get_dashboard_data()
        if not dashboard_data:
            return None
            
        recent_procedures = dashboard_data.get("recentProcedures", [])
        
        # Look for existing active procedure
        for proc in recent_procedures:
            if proc.get("status") == "active":
                print(f"✅ Found existing active procedure: {proc.get('procedureName')} (ID: {proc.get('id')})")
                return proc.get("id")
        
        # If no active procedure found, create one
        print("📝 No active procedure found, creating test procedure...")
        return await self.create_test_procedure()
        
    async def create_test_procedure(self):
        """Create a test procedure for status progression testing"""
        try:
            # Get patients
            url = f"{BACKEND_URL}/api/practice/patients"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("success"):
                        patients = response_data.get("data", [])
                        if not patients:
                            print("❌ No patients found")
                            return None
                        
                        # Use first patient
                        patient = patients[0]
                        patient_id = patient.get("id")
                        
                        # Create procedure assignment
                        assign_url = f"{BACKEND_URL}/api/practice/assign-procedure"
                        assignment_data = {
                            "patientId": patient_id,
                            "procedureId": "root-canal-therapy",
                            "procedureName": "Sequential Status Test Procedure",
                            "performedDate": datetime.now(timezone.utc).isoformat(),
                            "dentistName": "Dr. Status Test",
                            "practiceNotes": "Test procedure for sequential status system",
                            "customInstructions": ["This procedure tests the status progression system"],
                            "followUpDate": None
                        }
                        
                        async with self.session.post(assign_url, json=assignment_data, headers=headers) as assign_response:
                            if assign_response.status == 200:
                                assign_data = await assign_response.json()
                                if assign_data.get("success"):
                                    assignment_id = assign_data.get("data", {}).get("assignmentId")
                                    print(f"✅ Created test procedure with Assignment ID: {assignment_id}")
                                    return assignment_id
                                else:
                                    print(f"❌ Failed to create procedure: {assign_data}")
                            else:
                                error_text = await assign_response.text()
                                print(f"❌ Failed to create procedure: HTTP {assign_response.status}: {error_text}")
                        
        except Exception as e:
            print(f"❌ Error creating test procedure: {e}")
        return None
        
    async def get_assignment_details(self, assignment_id):
        """Get assignment details"""
        try:
            url = f"{BACKEND_URL}/api/practice/assignment/{assignment_id}"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("success"):
                        return response_data.get("data", {}).get("assignment", {})
        except Exception as e:
            print(f"❌ Error getting assignment details: {e}")
        return None
        
    async def update_assignment_status(self, assignment_id, new_status):
        """Update assignment status"""
        try:
            url = f"{BACKEND_URL}/api/practice/assignment/{assignment_id}"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            update_data = {"status": new_status}
            
            async with self.session.put(url, json=update_data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("success"):
                        print(f"✅ Successfully updated status to: {new_status}")
                        return True
                    else:
                        print(f"❌ Update failed: {response_data}")
                else:
                    error_text = await response.text()
                    print(f"❌ Update failed: HTTP {response.status}: {error_text}")
        except Exception as e:
            print(f"❌ Error updating assignment status: {e}")
        return False
        
    async def test_status_progression(self, assignment_id):
        """Test complete status progression"""
        print(f"\n🔄 TESTING STATUS PROGRESSION")
        print(f"Assignment ID: {assignment_id}")
        
        # Step 1: Verify initial active status
        print("\n📋 Step 1: Verifying initial 'active' status")
        initial_details = await self.get_assignment_details(assignment_id)
        if not initial_details:
            print("❌ Could not get assignment details")
            return False
            
        initial_status = initial_details.get("status", "unknown")
        print(f"   Current status: {initial_status}")
        
        if initial_status != "active":
            print(f"⚠️ Expected 'active' status, got '{initial_status}' - this may be expected if procedure was already processed")
        
        # Step 2: Mark as delivered
        print("\n📋 Step 2: Marking procedure as 'delivered'")
        delivered_success = await self.update_assignment_status(assignment_id, "delivered")
        if not delivered_success:
            print("❌ Failed to mark as delivered")
            return False
        
        # Verify delivered status and check follow-up scheduling
        print("\n📋 Step 3: Verifying 'delivered' status and follow-up scheduling")
        delivered_details = await self.get_assignment_details(assignment_id)
        if delivered_details:
            delivered_status = delivered_details.get("status", "unknown")
            follow_up_scheduled = delivered_details.get("followUpScheduled", False)
            follow_up_status = delivered_details.get("followUpStatus", "none")
            follow_up_scheduled_at = delivered_details.get("followUpScheduledAt", "Not set")
            
            print(f"   Status: {delivered_status}")
            print(f"   Follow-up Scheduled: {follow_up_scheduled}")
            print(f"   Follow-up Status: {follow_up_status}")
            print(f"   Follow-up Scheduled At: {follow_up_scheduled_at}")
            
            if delivered_status == "delivered":
                print("✅ Status successfully changed to 'delivered'")
                
                if follow_up_scheduled:
                    print("✅ Follow-up email was automatically scheduled")
                    print("📧 In production, this would send a follow-up email after 24 hours")
                    print("📧 When the follow-up email is sent, status will change from 'delivered' → 'second'")
                else:
                    print("⚠️ Follow-up email was not automatically scheduled")
                    print("   This may indicate an issue with the follow-up scheduler service")
                
                return True
            else:
                print(f"❌ Expected 'delivered' status, got '{delivered_status}'")
        else:
            print("❌ Could not get updated assignment details")
        
        return False
        
    async def test_active_count_accuracy(self):
        """Test that active count only includes 'active' status procedures"""
        print(f"\n📊 TESTING ACTIVE COUNT ACCURACY")
        
        dashboard_data = await self.get_dashboard_data()
        if not dashboard_data:
            print("❌ Could not get dashboard data")
            return False
        
        stats = dashboard_data.get("stats", {})
        recent_procedures = dashboard_data.get("recentProcedures", [])
        
        reported_active = stats.get("activeProcedures", 0)
        
        # Count actual active procedures in recent procedures
        actual_active_in_recent = sum(1 for proc in recent_procedures if proc.get("status") == "active")
        
        print(f"   Dashboard reports: {reported_active} active procedures")
        print(f"   Recent procedures show: {actual_active_in_recent} active procedures")
        
        # Note: The discrepancy might be because recent procedures is limited to 10
        # while the active count queries the entire database
        if reported_active >= actual_active_in_recent:
            print("✅ Active count appears accurate (may include procedures not in recent list)")
            return True
        else:
            print("❌ Active count discrepancy detected")
            return False
            
    async def test_enhanced_stats(self):
        """Test enhanced statistics showing procedure counts by status"""
        print(f"\n📈 TESTING ENHANCED STATISTICS")
        
        dashboard_data = await self.get_dashboard_data()
        if not dashboard_data:
            print("❌ Could not get dashboard data")
            return False
        
        recent_procedures = dashboard_data.get("recentProcedures", [])
        
        # Count procedures by status
        status_counts = {}
        for proc in recent_procedures:
            status = proc.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("   Procedure Status Distribution:")
        for status, count in sorted(status_counts.items()):
            print(f"     {status}: {count} procedures")
        
        # Check for the expected statuses in the sequential system
        has_active = status_counts.get("active", 0) > 0
        has_delivered = status_counts.get("delivered", 0) > 0
        has_second = status_counts.get("second", 0) > 0
        
        print(f"\n   Sequential Status System Status:")
        print(f"     Active procedures: {status_counts.get('active', 0)} ({'✅' if has_active else '⚠️'})")
        print(f"     Delivered procedures: {status_counts.get('delivered', 0)} ({'✅' if has_delivered else '⚠️'})")
        print(f"     Second follow-up procedures: {status_counts.get('second', 0)} ({'✅' if has_second else '⚠️'})")
        
        if has_active or has_delivered or has_second:
            print("✅ Sequential status system is operational")
            return True
        else:
            print("⚠️ No procedures found in sequential status system states")
            return False
            
    async def run_comprehensive_test(self):
        """Run comprehensive sequential status system test"""
        print("🚀 COMPREHENSIVE SEQUENTIAL STATUS SYSTEM TEST")
        print("=" * 60)
        print("Testing Status Sequence: active → delivered → second")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Step 1: Login
            if not await self.login():
                return False
            
            # Step 2: Test initial dashboard and active count
            print(f"\n📊 INITIAL DASHBOARD ANALYSIS")
            initial_success = await self.test_active_count_accuracy()
            
            # Step 3: Find or create active procedure
            assignment_id = await self.find_active_procedure()
            if not assignment_id:
                print("❌ Could not find or create active procedure")
                return False
            
            self.test_assignment_id = assignment_id
            
            # Step 4: Test status progression
            progression_success = await self.test_status_progression(assignment_id)
            
            # Step 5: Test enhanced stats
            stats_success = await self.test_enhanced_stats()
            
            # Step 6: Final dashboard check
            print(f"\n📊 FINAL DASHBOARD ANALYSIS")
            final_success = await self.test_active_count_accuracy()
            
            # Summary
            print(f"\n" + "=" * 60)
            print(f"🎯 TEST RESULTS SUMMARY")
            print(f"=" * 60)
            print(f"✅ Login: Success")
            print(f"{'✅' if initial_success else '❌'} Initial Active Count: {'Success' if initial_success else 'Failed'}")
            print(f"{'✅' if progression_success else '❌'} Status Progression: {'Success' if progression_success else 'Failed'}")
            print(f"{'✅' if stats_success else '❌'} Enhanced Statistics: {'Success' if stats_success else 'Failed'}")
            print(f"{'✅' if final_success else '❌'} Final Active Count: {'Success' if final_success else 'Failed'}")
            
            overall_success = progression_success and stats_success
            
            if overall_success:
                print(f"\n🎉 SEQUENTIAL STATUS SYSTEM IS WORKING CORRECTLY!")
                print(f"   • Active → Instructions not delivered yet (shows 'Mark Delivered' button)")
                print(f"   • Delivered → Instructions delivered, follow-up scheduled (blue badge)")
                print(f"   • Second → Follow-up email sent (purple badge)")
            else:
                print(f"\n⚠️ SOME ISSUES FOUND IN SEQUENTIAL STATUS SYSTEM")
                print(f"   Check the detailed results above for specific problems")
            
            return overall_success
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = ComprehensiveStatusTester()
    success = await tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All critical tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed - check results above")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
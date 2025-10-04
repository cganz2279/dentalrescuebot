#!/usr/bin/env python3
"""
Mark as Delivered Functionality Testing
Focus: Test the new "delivered" status workflow for procedure assignments
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import os
import sys

# Test configuration
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"
TEST_CREDENTIALS = {
    "email": "cganz2279@gmail.com",
    "password": "password123"
}

class DeliveredStatusTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.auth_token = None
        self.practice_id = None
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    async def test_practice_authentication(self):
        """Test 1: Login to Practice with cganz2279@gmail.com / password123"""
        try:
            url = f"{BACKEND_URL}/api/auth/login"
            login_data = {
                "email": TEST_CREDENTIALS["email"],
                "password": TEST_CREDENTIALS["password"]
            }
            
            async with self.session.post(url, json=login_data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success") and response_data.get("token"):
                        self.auth_token = response_data["token"]
                        self.practice_id = response_data.get("practiceId")
                        self.log_result("Practice Authentication", True, 
                                      f"Successfully authenticated. Practice ID: {self.practice_id}")
                        return True
                    else:
                        self.log_result("Practice Authentication", False, 
                                      f"Login succeeded but missing token/practiceId: {response_data}")
                        return False
                else:
                    self.log_result("Practice Authentication", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Practice Authentication", False, f"Error: {e}")
            return False
            
    async def test_get_initial_dashboard_state(self):
        """Test 2: Get current dashboard with active procedures count"""
        try:
            if not self.auth_token:
                self.log_result("Get Initial Dashboard State", False, "No auth token available")
                return None
                
            url = f"{BACKEND_URL}/api/practice/dashboard"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        stats = response_data.get("data", {}).get("stats", {})
                        active_procedures = stats.get("activeProcedures", 0)
                        total_patients = stats.get("totalPatients", 0)
                        
                        self.log_result("Get Initial Dashboard State", True, 
                                      f"Active procedures: {active_procedures}, Total patients: {total_patients}")
                        return {
                            "activeProcedures": active_procedures,
                            "totalPatients": total_patients,
                            "fullStats": stats
                        }
                    else:
                        self.log_result("Get Initial Dashboard State", False, 
                                      f"Dashboard request failed: {response_data}")
                        return None
                else:
                    self.log_result("Get Initial Dashboard State", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return None
                    
        except Exception as e:
            self.log_result("Get Initial Dashboard State", False, f"Error: {e}")
            return None
            
    async def test_get_active_procedure_assignments(self):
        """Test 3: Get list of active procedure assignments to find one to update"""
        try:
            if not self.auth_token:
                self.log_result("Get Active Procedure Assignments", False, "No auth token available")
                return None
                
            url = f"{BACKEND_URL}/api/practice/dashboard"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        recent_procedures = response_data.get("data", {}).get("recentProcedures", [])
                        active_procedures = [proc for proc in recent_procedures if proc.get("status") == "active"]
                        
                        if active_procedures:
                            # Get the first active procedure for testing
                            test_procedure = active_procedures[0]
                            assignment_id = test_procedure.get("id")
                            procedure_name = test_procedure.get("procedureName", "Unknown")
                            patient_name = test_procedure.get("patientName", "Unknown")
                            
                            self.log_result("Get Active Procedure Assignments", True, 
                                          f"Found {len(active_procedures)} active procedures. Test target: {procedure_name} for {patient_name} (ID: {assignment_id})")
                            return {
                                "assignment_id": assignment_id,
                                "procedure_name": procedure_name,
                                "patient_name": patient_name,
                                "total_active": len(active_procedures)
                            }
                        else:
                            self.log_result("Get Active Procedure Assignments", False, 
                                          f"No active procedures found. Recent procedures: {len(recent_procedures)}")
                            return None
                    else:
                        self.log_result("Get Active Procedure Assignments", False, 
                                      f"Dashboard request failed: {response_data}")
                        return None
                else:
                    self.log_result("Get Active Procedure Assignments", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return None
                    
        except Exception as e:
            self.log_result("Get Active Procedure Assignments", False, f"Error: {e}")
            return None
            
    async def test_update_procedure_status_to_delivered(self, assignment_id, procedure_name, patient_name):
        """Test 4: Update one procedure from 'active' to 'delivered' using PUT /api/practice/assignment/{assignment_id}"""
        try:
            if not self.auth_token:
                self.log_result("Update Procedure Status to Delivered", False, "No auth token available")
                return False
                
            url = f"{BACKEND_URL}/api/practice/assignment/{assignment_id}"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            update_data = {
                "status": "delivered"
            }
            
            async with self.session.put(url, json=update_data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        self.log_result("Update Procedure Status to Delivered", True, 
                                      f"Successfully updated {procedure_name} for {patient_name} to 'delivered' status")
                        return True
                    else:
                        self.log_result("Update Procedure Status to Delivered", False, 
                                      f"Update request failed: {response_data}")
                        return False
                else:
                    self.log_result("Update Procedure Status to Delivered", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Update Procedure Status to Delivered", False, f"Error: {e}")
            return False
            
    async def test_verify_dashboard_changes(self, initial_stats, updated_assignment_id):
        """Test 5: Verify dashboard changes after status update"""
        try:
            if not self.auth_token:
                self.log_result("Verify Dashboard Changes", False, "No auth token available")
                return False
                
            url = f"{BACKEND_URL}/api/practice/dashboard"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        new_stats = response_data.get("data", {}).get("stats", {})
                        new_active_procedures = new_stats.get("activeProcedures", 0)
                        initial_active_procedures = initial_stats.get("activeProcedures", 0)
                        
                        # Check if active procedures count decreased by 1
                        expected_count = initial_active_procedures - 1
                        count_decreased = new_active_procedures == expected_count
                        
                        # Check if the updated procedure shows "delivered" status
                        recent_procedures = response_data.get("data", {}).get("recentProcedures", [])
                        updated_procedure = None
                        for proc in recent_procedures:
                            if proc.get("id") == updated_assignment_id:
                                updated_procedure = proc
                                break
                        
                        status_updated = updated_procedure and updated_procedure.get("status") == "delivered"
                        
                        # Verify active procedures only include status="active"
                        active_only_procedures = [proc for proc in recent_procedures if proc.get("status") == "active"]
                        active_count_matches = len(active_only_procedures) == new_active_procedures
                        
                        # Debug information
                        delivered_procedures = [proc for proc in recent_procedures if proc.get("status") == "delivered"]
                        
                        success = count_decreased and status_updated and active_count_matches
                        
                        details = f"Active procedures: {initial_active_procedures} → {new_active_procedures} (expected: {expected_count}). "
                        details += f"Count decreased: {count_decreased}. "
                        details += f"Status updated to delivered: {status_updated}. "
                        details += f"Active count matches filter: {active_count_matches}. "
                        details += f"Recent procedures: {len(recent_procedures)} total, {len(active_only_procedures)} active, {len(delivered_procedures)} delivered"
                        
                        self.log_result("Verify Dashboard Changes", success, details)
                        return success
                    else:
                        self.log_result("Verify Dashboard Changes", False, 
                                      f"Dashboard request failed: {response_data}")
                        return False
                else:
                    self.log_result("Verify Dashboard Changes", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Verify Dashboard Changes", False, f"Error: {e}")
            return False
            
    async def test_delivered_workflow_persistence(self, assignment_id):
        """Test 6: Verify the delivered status persists correctly in database"""
        try:
            if not self.auth_token:
                self.log_result("Delivered Workflow Persistence", False, "No auth token available")
                return False
                
            # Get dashboard again to double-check persistence
            url = f"{BACKEND_URL}/api/practice/dashboard"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        recent_procedures = response_data.get("data", {}).get("recentProcedures", [])
                        
                        # Find the updated procedure
                        updated_procedure = None
                        for proc in recent_procedures:
                            if proc.get("id") == assignment_id:
                                updated_procedure = proc
                                break
                        
                        if updated_procedure:
                            status = updated_procedure.get("status")
                            if status == "delivered":
                                self.log_result("Delivered Workflow Persistence", True, 
                                              f"Status 'delivered' persists correctly in database")
                                return True
                            else:
                                self.log_result("Delivered Workflow Persistence", False, 
                                              f"Status reverted to '{status}' instead of 'delivered'")
                                return False
                        else:
                            self.log_result("Delivered Workflow Persistence", False, 
                                          f"Updated procedure (ID: {assignment_id}) not found in recent procedures")
                            return False
                    else:
                        self.log_result("Delivered Workflow Persistence", False, 
                                      f"Dashboard request failed: {response_data}")
                        return False
                else:
                    self.log_result("Delivered Workflow Persistence", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Delivered Workflow Persistence", False, f"Error: {e}")
            return False
            
    async def run_all_tests(self):
        """Run all Mark as Delivered functionality tests"""
        print("🚀 Starting Mark as Delivered Functionality Testing")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_CREDENTIALS['email']}")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Test 1: Authentication
            if not await self.test_practice_authentication():
                print("❌ Authentication failed - cannot continue with tests")
                return False
                
            # Test 2: Get initial dashboard state
            initial_stats = await self.test_get_initial_dashboard_state()
            if not initial_stats:
                print("❌ Could not get initial dashboard state - cannot continue")
                return False
                
            # Test 3: Get active procedure assignments
            assignment_info = await self.test_get_active_procedure_assignments()
            if not assignment_info:
                print("❌ No active procedures found - cannot test delivered functionality")
                return False
                
            assignment_id = assignment_info["assignment_id"]
            procedure_name = assignment_info["procedure_name"]
            patient_name = assignment_info["patient_name"]
            
            # Test 4: Update procedure status to delivered
            if not await self.test_update_procedure_status_to_delivered(assignment_id, procedure_name, patient_name):
                print("❌ Failed to update procedure status to delivered")
                return False
                
            # Test 5: Verify dashboard changes
            if not await self.test_verify_dashboard_changes(initial_stats, assignment_id):
                print("❌ Dashboard changes verification failed")
                return False
                
            # Test 6: Verify persistence
            if not await self.test_delivered_workflow_persistence(assignment_id):
                print("❌ Delivered workflow persistence verification failed")
                return False
                
            # Calculate success rate
            passed = sum(1 for result in self.test_results if result["success"])
            total = len(self.test_results)
            
            print("\n" + "=" * 60)
            print(f"🎯 TEST SUMMARY: {passed}/{total} tests passed")
            print("=" * 60)
            
            if passed == total:
                print("\n✅ All Mark as Delivered functionality tests passed!")
                print("🎉 Key Features Verified:")
                print("   • Backend assignment update endpoint accepts 'delivered' status")
                print("   • Dashboard active procedures count only includes status='active'")
                print("   • Status change persists correctly in database")
                print("   • API responses are correct for the new workflow")
                return True
            else:
                print(f"\n⚠️ {total - passed} tests failed - check results above")
                return False
                
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = DeliveredStatusTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 Mark as Delivered functionality is working correctly!")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed - delivered functionality needs attention")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
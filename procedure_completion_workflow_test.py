#!/usr/bin/env python3
"""
Procedure Completion Workflow Investigation
Focus: Investigate critical workflow gap - no process for marking procedures as "complete"

Key Questions to Investigate:
1. Procedure Status Management: Is there any UI or workflow for practices to mark procedures as complete?
2. Status Change Endpoints: Are there API endpoints to update procedure status from "active" to "completed"?
3. Automatic Status Changes: Does the system automatically change status based on time or other factors?
4. Current Procedure Statuses: What statuses actually exist in the database (all active, or are some marked differently)?
5. Missing Workflow: Is this a missing feature that should be implemented?

Authentication: cganz2279@gmail.com / password123
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone
import os
import sys

# Test configuration
BACKEND_URL = "https://dentiportal.preview.emergentagent.com"
PRACTICE_EMAIL = "cganz2279@gmail.com"
PRACTICE_PASSWORD = "password123"

class ProcedureCompletionWorkflowTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.practice_id = None
        self.test_results = []
        self.procedure_assignments = []
        
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
        
    async def authenticate_practice(self):
        """Test 1: Authenticate with practice credentials"""
        try:
            url = f"{BACKEND_URL}/api/auth/login"
            login_data = {
                "email": PRACTICE_EMAIL,
                "password": PRACTICE_PASSWORD
            }
            
            async with self.session.post(url, json=login_data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        self.auth_token = response_data.get("token")
                        self.practice_id = response_data.get("practice_id")
                        self.log_result("Practice Authentication", True, 
                                      f"Successfully authenticated practice ID: {self.practice_id}")
                        return True
                    else:
                        self.log_result("Practice Authentication", False, 
                                      f"Login failed: {response_data}")
                        return False
                else:
                    self.log_result("Practice Authentication", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Practice Authentication", False, f"Error: {e}")
            return False
            
    async def get_practice_dashboard_data(self):
        """Test 2: Get practice dashboard data to see active procedures count"""
        try:
            url = f"{BACKEND_URL}/api/practice/dashboard"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        practice_data = response_data.get("data", {})
                        stats = practice_data.get("stats", {})
                        active_procedures = stats.get("activeProcedures", 0)
                        total_patients = stats.get("totalPatients", 0)
                        
                        self.log_result("Practice Dashboard Data", True, 
                                      f"Active Procedures: {active_procedures}, Total Patients: {total_patients}")
                        return practice_data
                    else:
                        self.log_result("Practice Dashboard Data", False, 
                                      f"Dashboard request failed: {response_data}")
                        return None
                else:
                    self.log_result("Practice Dashboard Data", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return None
                    
        except Exception as e:
            self.log_result("Practice Dashboard Data", False, f"Error: {e}")
            return None
            
    async def get_recent_procedures(self):
        """Test 3: Get recent procedures from dashboard data to analyze current statuses"""
        try:
            # Recent procedures are included in the dashboard data
            url = f"{BACKEND_URL}/api/practice/dashboard"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        dashboard_data = response_data.get("data", {})
                        procedures = dashboard_data.get("recentProcedures", [])
                        self.procedure_assignments = procedures
                        
                        # Analyze statuses
                        status_counts = {}
                        for proc in procedures:
                            status = proc.get("status", "unknown")
                            status_counts[status] = status_counts.get(status, 0) + 1
                            
                        self.log_result("Recent Procedures Analysis", True, 
                                      f"Found {len(procedures)} procedures. Status breakdown: {status_counts}")
                        return procedures
                    else:
                        self.log_result("Recent Procedures Analysis", False, 
                                      f"Dashboard request failed: {response_data}")
                        return []
                else:
                    self.log_result("Recent Procedures Analysis", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return []
                    
        except Exception as e:
            self.log_result("Recent Procedures Analysis", False, f"Error: {e}")
            return []
            
    async def test_procedure_assignment_update_endpoint(self):
        """Test 4: Test if procedure assignments can be updated (status change)"""
        try:
            if not self.procedure_assignments:
                self.log_result("Procedure Assignment Update Test", False, 
                              "No procedure assignments available for testing")
                return False
                
            # Get the first active procedure assignment
            test_assignment = None
            for assignment in self.procedure_assignments:
                if assignment.get("status") == "active":
                    test_assignment = assignment
                    break
                    
            if not test_assignment:
                self.log_result("Procedure Assignment Update Test", False, 
                              "No active procedure assignments found for testing")
                return False
                
            assignment_id = test_assignment.get("_id") or test_assignment.get("id")
            if not assignment_id:
                self.log_result("Procedure Assignment Update Test", False, 
                              "No assignment ID found in procedure data")
                return False
                
            # Test updating status to "completed"
            url = f"{BACKEND_URL}/api/practice/assignment/{assignment_id}"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            update_data = {
                "status": "completed"
            }
            
            async with self.session.put(url, json=update_data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        self.log_result("Procedure Assignment Update Test", True, 
                                      f"Successfully updated assignment {assignment_id} to 'completed' status")
                        return True
                    else:
                        self.log_result("Procedure Assignment Update Test", False, 
                                      f"Update failed: {response_data}")
                        return False
                elif response.status == 404:
                    self.log_result("Procedure Assignment Update Test", False, 
                                  f"Assignment update endpoint not found (404) - missing feature")
                    return False
                else:
                    self.log_result("Procedure Assignment Update Test", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Procedure Assignment Update Test", False, f"Error: {e}")
            return False
            
    async def test_available_status_values(self):
        """Test 5: Test what status values are accepted by the system"""
        try:
            if not self.procedure_assignments:
                self.log_result("Available Status Values Test", False, 
                              "No procedure assignments available for testing")
                return False
                
            # Get an active assignment to test with
            test_assignment = None
            for assignment in self.procedure_assignments:
                if assignment.get("status") == "active":
                    test_assignment = assignment
                    break
                    
            if not test_assignment:
                self.log_result("Available Status Values Test", False, 
                              "No active procedure assignments found for testing")
                return False
                
            assignment_id = test_assignment.get("_id") or test_assignment.get("id")
            if not assignment_id:
                self.log_result("Available Status Values Test", False, 
                              "No assignment ID found in procedure data")
                return False
                
            # Test different status values
            test_statuses = ["completed", "cancelled", "in_progress", "pending", "inactive"]
            successful_statuses = []
            failed_statuses = []
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            for status in test_statuses:
                try:
                    url = f"{BACKEND_URL}/api/practice/assignment/{assignment_id}"
                    update_data = {"status": status}
                    
                    async with self.session.put(url, json=update_data, headers=headers) as response:
                        if response.status == 200:
                            response_data = await response.json()
                            if response_data.get("success"):
                                successful_statuses.append(status)
                            else:
                                failed_statuses.append(f"{status}: {response_data.get('message', 'Unknown error')}")
                        else:
                            failed_statuses.append(f"{status}: HTTP {response.status}")
                            
                except Exception as e:
                    failed_statuses.append(f"{status}: Exception {e}")
                    
            # Reset to active status
            try:
                url = f"{BACKEND_URL}/api/practice/assignment/{assignment_id}"
                reset_data = {"status": "active"}
                async with self.session.put(url, json=reset_data, headers=headers) as response:
                    pass  # Don't care about the result, just trying to reset
            except:
                pass
                
            if successful_statuses:
                self.log_result("Available Status Values Test", True, 
                              f"Accepted statuses: {successful_statuses}. Failed: {failed_statuses}")
                return True
            else:
                self.log_result("Available Status Values Test", False, 
                              f"No status updates accepted. All failed: {failed_statuses}")
                return False
                
        except Exception as e:
            self.log_result("Available Status Values Test", False, f"Error: {e}")
            return False
            
    async def check_for_completion_ui_endpoints(self):
        """Test 6: Check for any UI-related endpoints for procedure completion"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test potential UI endpoints
            ui_endpoints = [
                "/api/practice/procedures/complete",
                "/api/practice/procedures/mark-complete",
                "/api/practice/assignments/complete",
                "/api/practice/assignments/mark-complete",
                "/api/practice/patient-procedures/complete",
                "/api/practice/workflow/complete-procedure"
            ]
            
            found_endpoints = []
            missing_endpoints = []
            
            for endpoint in ui_endpoints:
                try:
                    url = f"{BACKEND_URL}{endpoint}"
                    async with self.session.get(url, headers=headers) as response:
                        if response.status != 404:
                            found_endpoints.append(f"{endpoint}: HTTP {response.status}")
                        else:
                            missing_endpoints.append(endpoint)
                except Exception as e:
                    missing_endpoints.append(f"{endpoint}: Error {e}")
                    
            if found_endpoints:
                self.log_result("Completion UI Endpoints Check", True, 
                              f"Found potential endpoints: {found_endpoints}")
            else:
                self.log_result("Completion UI Endpoints Check", False, 
                              f"No completion-specific endpoints found. Missing: {missing_endpoints}")
                
            return len(found_endpoints) > 0
            
        except Exception as e:
            self.log_result("Completion UI Endpoints Check", False, f"Error: {e}")
            return False
            
    async def analyze_database_procedure_statuses(self):
        """Test 7: Analyze what statuses actually exist in the database"""
        try:
            # This will be done through the recent procedures data we already have
            if not self.procedure_assignments:
                self.log_result("Database Status Analysis", False, 
                              "No procedure data available for analysis")
                return False
                
            # Analyze all statuses in the current data
            all_statuses = set()
            status_details = {}
            
            for assignment in self.procedure_assignments:
                status = assignment.get("status", "unknown")
                all_statuses.add(status)
                
                if status not in status_details:
                    status_details[status] = {
                        "count": 0,
                        "procedures": [],
                        "patients": set()
                    }
                    
                status_details[status]["count"] += 1
                status_details[status]["procedures"].append(assignment.get("procedureName", "Unknown"))
                if assignment.get("patientName"):
                    status_details[status]["patients"].add(assignment.get("patientName"))
                    
            # Convert sets to lists for JSON serialization
            for status in status_details:
                status_details[status]["patients"] = list(status_details[status]["patients"])
                
            analysis_result = {
                "total_assignments": len(self.procedure_assignments),
                "unique_statuses": list(all_statuses),
                "status_breakdown": status_details
            }
            
            self.log_result("Database Status Analysis", True, 
                          f"Found {len(all_statuses)} unique statuses: {list(all_statuses)}. "
                          f"Total assignments: {len(self.procedure_assignments)}")
            
            # Check if all procedures are "active" (indicating missing completion workflow)
            if len(all_statuses) == 1 and "active" in all_statuses:
                self.log_result("Workflow Gap Identified", False, 
                              "CRITICAL: ALL procedures have 'active' status - no completion workflow detected")
            elif "completed" not in all_statuses:
                self.log_result("Completion Status Missing", False, 
                              "WARNING: No 'completed' status found in current procedures")
            else:
                self.log_result("Status Variety Found", True, 
                              f"Multiple statuses found including completion indicators")
                
            return analysis_result
            
        except Exception as e:
            self.log_result("Database Status Analysis", False, f"Error: {e}")
            return None
            
    async def test_automatic_status_changes(self):
        """Test 8: Check if system has any automatic status change logic"""
        try:
            # Look for any time-based or automatic status change endpoints
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Check for scheduler or automation endpoints
            automation_endpoints = [
                "/api/practice/automation/status-updates",
                "/api/practice/scheduler/procedure-completion",
                "/api/practice/workflows/automatic",
                "/api/system/cron/procedure-updates"
            ]
            
            found_automation = []
            
            for endpoint in automation_endpoints:
                try:
                    url = f"{BACKEND_URL}{endpoint}"
                    async with self.session.get(url, headers=headers) as response:
                        if response.status != 404:
                            found_automation.append(f"{endpoint}: HTTP {response.status}")
                except:
                    pass
                    
            if found_automation:
                self.log_result("Automatic Status Changes Check", True, 
                              f"Found potential automation endpoints: {found_automation}")
                return True
            else:
                self.log_result("Automatic Status Changes Check", False, 
                              "No automatic status change endpoints found - manual workflow only")
                return False
                
        except Exception as e:
            self.log_result("Automatic Status Changes Check", False, f"Error: {e}")
            return False
            
    async def run_comprehensive_investigation(self):
        """Run comprehensive procedure completion workflow investigation"""
        print("🔍 Starting Procedure Completion Workflow Investigation")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Practice Email: {PRACTICE_EMAIL}")
        print("=" * 70)
        print("Key Questions:")
        print("1. Is there any UI or workflow for practices to mark procedures as complete?")
        print("2. Are there API endpoints to update procedure status from 'active' to 'completed'?")
        print("3. Does the system automatically change status based on time or other factors?")
        print("4. What statuses actually exist in the database?")
        print("5. Is this a missing feature that should be implemented?")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run investigation tests in sequence
            tests = [
                self.authenticate_practice,
                self.get_practice_dashboard_data,
                self.get_recent_procedures,
                self.test_procedure_assignment_update_endpoint,
                self.test_available_status_values,
                self.check_for_completion_ui_endpoints,
                self.analyze_database_procedure_statuses,
                self.test_automatic_status_changes
            ]
            
            passed = 0
            total = len(tests)
            
            for test in tests:
                try:
                    result = await test()
                    if result:
                        passed += 1
                except Exception as e:
                    print(f"❌ Test {test.__name__} failed with exception: {e}")
                    
            print("\n" + "=" * 70)
            print(f"🎯 INVESTIGATION SUMMARY: {passed}/{total} tests completed successfully")
            print("=" * 70)
            
            # Analyze findings for workflow gaps
            workflow_gaps = []
            missing_features = []
            
            for result in self.test_results:
                if not result["success"]:
                    if "404" in result["details"] or "not found" in result["details"].lower():
                        missing_features.append(f"MISSING: {result['test']} - {result['details']}")
                    elif "all procedures have 'active' status" in result["details"].lower():
                        workflow_gaps.append(f"WORKFLOW GAP: {result['test']} - {result['details']}")
                    elif "no completion" in result["details"].lower():
                        workflow_gaps.append(f"COMPLETION ISSUE: {result['test']} - {result['details']}")
                        
            print("\n🚨 CRITICAL FINDINGS:")
            if workflow_gaps:
                print("   WORKFLOW GAPS IDENTIFIED:")
                for gap in workflow_gaps:
                    print(f"   • {gap}")
            if missing_features:
                print("   MISSING FEATURES:")
                for feature in missing_features:
                    print(f"   • {feature}")
                    
            if not workflow_gaps and not missing_features:
                print("   ✅ No critical workflow gaps detected")
            else:
                print(f"\n💡 RECOMMENDATION: Implement procedure completion workflow")
                print("   • Add 'Mark Complete' button in practice UI")
                print("   • Ensure assignment update endpoint accepts 'completed' status")
                print("   • Add completion date tracking")
                print("   • Consider automatic status changes based on time")
                
            return passed, workflow_gaps, missing_features
            
        finally:
            await self.cleanup()

async def main():
    """Main investigation execution"""
    tester = ProcedureCompletionWorkflowTester()
    passed, workflow_gaps, missing_features = await tester.run_comprehensive_investigation()
    
    print(f"\n🎯 FINAL ASSESSMENT:")
    print(f"   Tests Completed: {passed}/8")
    print(f"   Workflow Gaps: {len(workflow_gaps)}")
    print(f"   Missing Features: {len(missing_features)}")
    
    if workflow_gaps or missing_features:
        print("\n⚠️ CRITICAL WORKFLOW GAP CONFIRMED")
        print("   The system lacks a proper procedure completion workflow.")
        print("   Practices cannot effectively mark procedures as 'complete'.")
        sys.exit(1)
    else:
        print("\n✅ Procedure completion workflow appears functional")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
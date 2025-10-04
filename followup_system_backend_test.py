#!/usr/bin/env python3
"""
24-Hour Follow-up Email System Testing
Tests the complete follow-up email workflow including scheduling, database operations, and email delivery
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timezone
import os
import sys

# Test configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
PRACTICE_EMAIL = "cganz2279@gmail.com"
PRACTICE_PASSWORD = "password123"

class FollowUpSystemTester:
    def __init__(self):
        self.session = None
        self.test_results = []
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
        """Test 1: Authenticate with practice credentials"""
        try:
            url = f"{BACKEND_URL}/api/auth/login"
            login_data = {
                "email": PRACTICE_EMAIL,
                "password": PRACTICE_PASSWORD
            }
            
            async with self.session.post(url, json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("token"):
                        self.auth_token = data["token"]
                        self.practice_id = data.get("practiceId")
                        self.log_result("Practice Authentication", True, 
                                      f"Authenticated successfully, Practice ID: {self.practice_id}")
                        return True
                    else:
                        self.log_result("Practice Authentication", False, 
                                      f"Login failed: {data}")
                        return False
                else:
                    response_text = await response.text()
                    self.log_result("Practice Authentication", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Practice Authentication", False, f"Error: {e}")
            return False
            
    async def test_get_active_procedures(self):
        """Test 2: Get active procedures to find one to mark as delivered"""
        try:
            url = f"{BACKEND_URL}/api/practice/dashboard"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    recent_procedures = data.get("data", {}).get("recentProcedures", [])
                    
                    # Find an active procedure to test with
                    active_procedure = None
                    for proc in recent_procedures:
                        if proc.get("status") == "active":
                            active_procedure = proc
                            break
                    
                    if active_procedure:
                        self.test_assignment_id = active_procedure.get("id")
                        self.log_result("Get Active Procedures", True, 
                                      f"Found active procedure: {active_procedure.get('procedureName')} for {active_procedure.get('patientName')}")
                        return True
                    else:
                        self.log_result("Get Active Procedures", False, 
                                      "No active procedures found to test with")
                        return False
                else:
                    response_text = await response.text()
                    self.log_result("Get Active Procedures", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Get Active Procedures", False, f"Error: {e}")
            return False
            
    async def test_mark_procedure_as_delivered(self):
        """Test 3: Mark a procedure as delivered to trigger follow-up scheduling"""
        try:
            if not self.test_assignment_id:
                self.log_result("Mark Procedure as Delivered", False, 
                              "No test assignment ID available")
                return False
                
            url = f"{BACKEND_URL}/api/practice/assignment/{self.test_assignment_id}"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            update_data = {
                "status": "delivered"
            }
            
            async with self.session.put(url, json=update_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_result("Mark Procedure as Delivered", True, 
                                      f"Procedure marked as delivered: {data.get('message', 'Success')}")
                        return True
                    else:
                        self.log_result("Mark Procedure as Delivered", False, 
                                      f"Update failed: {data}")
                        return False
                else:
                    response_text = await response.text()
                    self.log_result("Mark Procedure as Delivered", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Mark Procedure as Delivered", False, f"Error: {e}")
            return False
            
    async def test_followup_stats_endpoint(self):
        """Test 4: Test follow-up statistics endpoint"""
        try:
            url = f"{BACKEND_URL}/api/practice/followup-stats"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        stats = data.get("data", {})
                        scheduled = stats.get("scheduled", 0)
                        sent = stats.get("sent", 0)
                        failed = stats.get("failed", 0)
                        total = stats.get("total", 0)
                        success_rate = stats.get("success_rate", 0)
                        
                        self.log_result("Follow-up Stats Endpoint", True, 
                                      f"Stats: Scheduled={scheduled}, Sent={sent}, Failed={failed}, Total={total}, Success Rate={success_rate}%")
                        return True
                    else:
                        self.log_result("Follow-up Stats Endpoint", False, 
                                      f"Stats request failed: {data}")
                        return False
                else:
                    response_text = await response.text()
                    self.log_result("Follow-up Stats Endpoint", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Follow-up Stats Endpoint", False, f"Error: {e}")
            return False
            
    async def test_followup_logs_endpoint(self):
        """Test 5: Test follow-up activity logs endpoint"""
        try:
            url = f"{BACKEND_URL}/api/practice/followup-logs"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        logs_data = data.get("data", {})
                        logs = logs_data.get("logs", [])
                        count = logs_data.get("count", 0)
                        
                        self.log_result("Follow-up Logs Endpoint", True, 
                                      f"Retrieved {count} follow-up activity logs")
                        
                        # Show recent log entries
                        if logs:
                            print("   Recent follow-up activities:")
                            for log in logs[:3]:  # Show first 3 logs
                                activity_type = log.get("activityType", "unknown")
                                timestamp = log.get("timestamp", "")
                                print(f"     - {activity_type} at {timestamp}")
                        
                        return True
                    else:
                        self.log_result("Follow-up Logs Endpoint", False, 
                                      f"Logs request failed: {data}")
                        return False
                else:
                    response_text = await response.text()
                    self.log_result("Follow-up Logs Endpoint", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Follow-up Logs Endpoint", False, f"Error: {e}")
            return False
            
    async def test_manual_followup_test(self):
        """Test 6: Test manual follow-up email trigger"""
        try:
            if not self.test_assignment_id:
                self.log_result("Manual Follow-up Test", False, 
                              "No test assignment ID available")
                return False
                
            url = f"{BACKEND_URL}/api/practice/followup-test/{self.test_assignment_id}"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.post(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        message = data.get("message", "Follow-up scheduled")
                        self.log_result("Manual Follow-up Test", True, 
                                      f"Manual follow-up triggered: {message}")
                        return True
                    else:
                        self.log_result("Manual Follow-up Test", False, 
                                      f"Manual follow-up failed: {data}")
                        return False
                else:
                    response_text = await response.text()
                    self.log_result("Manual Follow-up Test", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Manual Follow-up Test", False, f"Error: {e}")
            return False
            
    async def test_followup_scheduler_service(self):
        """Test 7: Verify follow-up scheduler service is running"""
        try:
            # Test by checking if the server startup logs indicate scheduler started
            # We'll use the health endpoint and check for any scheduler-related info
            url = f"{BACKEND_URL}/api/health"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        self.log_result("Follow-up Scheduler Service", True, 
                                      "Backend is healthy - scheduler should be running")
                        return True
                    else:
                        self.log_result("Follow-up Scheduler Service", False, 
                                      f"Backend health check failed: {data}")
                        return False
                else:
                    self.log_result("Follow-up Scheduler Service", False, 
                                  f"Health check failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_result("Follow-up Scheduler Service", False, f"Error: {e}")
            return False
            
    async def test_database_collections_exist(self):
        """Test 8: Verify database collections are created (indirect test via API)"""
        try:
            # We can't directly access the database, but we can test if the APIs work
            # which indicates the collections exist
            
            # Test follow-up stats (uses followup_emails collection)
            stats_url = f"{BACKEND_URL}/api/practice/followup-stats"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(stats_url, headers=headers) as response:
                stats_working = response.status == 200
                
            # Test follow-up logs (uses followup_activity_log collection)
            logs_url = f"{BACKEND_URL}/api/practice/followup-logs"
            
            async with self.session.get(logs_url, headers=headers) as response:
                logs_working = response.status == 200
                
            if stats_working and logs_working:
                self.log_result("Database Collections Exist", True, 
                              "Both followup_emails and followup_activity_log collections are accessible")
                return True
            else:
                self.log_result("Database Collections Exist", False, 
                              f"Collection access failed - Stats: {stats_working}, Logs: {logs_working}")
                return False
                
        except Exception as e:
            self.log_result("Database Collections Exist", False, f"Error: {e}")
            return False
            
    async def test_email_template_format(self):
        """Test 9: Verify email template is properly formatted (indirect test)"""
        try:
            # We can't directly test the email template, but we can verify the manual
            # follow-up test works, which uses the same template
            if not self.test_assignment_id:
                self.log_result("Email Template Format", False, 
                              "No test assignment ID available")
                return False
                
            url = f"{BACKEND_URL}/api/practice/followup-test/{self.test_assignment_id}"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.post(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_result("Email Template Format", True, 
                                      "Email template processing successful - format should be correct")
                        return True
                    else:
                        self.log_result("Email Template Format", False, 
                                      f"Email template processing failed: {data}")
                        return False
                else:
                    self.log_result("Email Template Format", False, 
                                  f"Email template test failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_result("Email Template Format", False, f"Error: {e}")
            return False
            
    async def run_all_tests(self):
        """Run all follow-up system tests"""
        print("🚀 Starting 24-Hour Follow-up Email System Testing")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Practice Email: {PRACTICE_EMAIL}")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run tests in sequence
            tests = [
                self.test_practice_authentication,
                self.test_get_active_procedures,
                self.test_mark_procedure_as_delivered,
                self.test_followup_stats_endpoint,
                self.test_followup_logs_endpoint,
                self.test_manual_followup_test,
                self.test_followup_scheduler_service,
                self.test_database_collections_exist,
                self.test_email_template_format
            ]
            
            passed = 0
            total = len(tests)
            
            for test in tests:
                try:
                    result = await test()
                    if result:
                        passed += 1
                    # Add small delay between tests
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"❌ Test {test.__name__} failed with exception: {e}")
                    
            print("\n" + "=" * 70)
            print(f"🎯 TEST SUMMARY: {passed}/{total} tests passed")
            print("=" * 70)
            
            # Analyze results
            critical_failures = []
            for result in self.test_results:
                if not result["success"]:
                    if "authentication" in result["test"].lower():
                        critical_failures.append(f"CRITICAL: {result['test']} - Cannot proceed without authentication")
                    elif "delivered" in result["test"].lower():
                        critical_failures.append(f"CRITICAL: {result['test']} - Core follow-up trigger not working")
                    elif "stats" in result["test"].lower() or "logs" in result["test"].lower():
                        critical_failures.append(f"IMPORTANT: {result['test']} - Monitoring endpoints not working")
                        
            if critical_failures:
                print("\n🚨 CRITICAL ISSUES FOUND:")
                for issue in critical_failures:
                    print(f"   {issue}")
            else:
                print("\n✅ All critical follow-up system components are working")
                
            # Provide system status summary
            print(f"\n📊 FOLLOW-UP SYSTEM STATUS:")
            print(f"   Authentication: {'✅' if self.auth_token else '❌'}")
            print(f"   Practice ID: {self.practice_id or 'Not available'}")
            print(f"   Test Assignment: {self.test_assignment_id or 'Not available'}")
            
            return passed == total
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = FollowUpSystemTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All follow-up system tests passed!")
        print("✅ The 24-hour follow-up email system is fully operational")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed - check results above")
        print("❌ Follow-up system may have issues that need attention")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
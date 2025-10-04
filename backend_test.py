#!/usr/bin/env python3
"""
SamCart Webhook Integration System Testing
Tests the completely rebuilt SamCart payment integration system for reliability and performance.
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://samcart-auth-fix.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class SamCartWebhookTester:
    def __init__(self):
        self.test_results = []
        self.test_email = f"test.samcart.{int(time.time())}@example.com"
        self.created_accounts = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def test_webhook_test_endpoint(self):
        """Test 1: SamCart Webhook Test Endpoint"""
        try:
            url = f"{API_BASE}/webhook/samcart/test"
            params = {"test_email": self.test_email}
            
            print(f"🧪 Testing webhook test endpoint with email: {self.test_email}")
            response = requests.post(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    practice_info = data.get("practice_info", {})
                    practice_id = practice_info.get("practice_id")
                    password = practice_info.get("password")
                    email_sent = data.get("email_sent", False)
                    
                    if practice_id and password:
                        self.created_accounts.append({
                            "email": self.test_email,
                            "password": password,
                            "practice_id": practice_id
                        })
                        
                        self.log_test(
                            "SamCart Webhook Test Endpoint",
                            True,
                            f"Account created successfully. Practice ID: {practice_id}, Email sent: {email_sent}"
                        )
                        return True
                    else:
                        self.log_test(
                            "SamCart Webhook Test Endpoint",
                            False,
                            "",
                            "Missing practice_id or password in response"
                        )
                        return False
                elif data.get("status") == "duplicate":
                    self.log_test(
                        "SamCart Webhook Test Endpoint",
                        True,
                        "Account already exists (duplicate detection working)"
                    )
                    return True
                else:
                    self.log_test(
                        "SamCart Webhook Test Endpoint",
                        False,
                        "",
                        f"Unexpected status: {data.get('status')}"
                    )
                    return False
            else:
                self.log_test(
                    "SamCart Webhook Test Endpoint",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "SamCart Webhook Test Endpoint",
                False,
                "",
                str(e)
            )
            return False

    def test_account_creation_flow(self):
        """Test 2: Account Creation Flow Verification"""
        try:
            if not self.created_accounts:
                self.log_test(
                    "Account Creation Flow",
                    False,
                    "",
                    "No accounts created to verify"
                )
                return False
            
            account = self.created_accounts[0]
            
            # Verify account has proper structure
            required_fields = ["email", "password", "practice_id"]
            missing_fields = [field for field in required_fields if not account.get(field)]
            
            if missing_fields:
                self.log_test(
                    "Account Creation Flow",
                    False,
                    "",
                    f"Missing required fields: {missing_fields}"
                )
                return False
            
            # Verify password is secure (12+ characters, mixed case, numbers, special chars)
            password = account["password"]
            password_checks = {
                "length": len(password) >= 12,
                "uppercase": any(c.isupper() for c in password),
                "lowercase": any(c.islower() for c in password),
                "digits": any(c.isdigit() for c in password),
                "special": any(c in "!@#$%&*" for c in password)
            }
            
            failed_checks = [check for check, passed in password_checks.items() if not passed]
            
            if failed_checks:
                self.log_test(
                    "Account Creation Flow",
                    False,
                    "",
                    f"Password security checks failed: {failed_checks}"
                )
                return False
            
            self.log_test(
                "Account Creation Flow",
                True,
                f"Account structure valid. Password meets security requirements. Practice ID: {account['practice_id']}"
            )
            return True
            
        except Exception as e:
            self.log_test(
                "Account Creation Flow",
                False,
                "",
                str(e)
            )
            return False

    def test_login_system(self):
        """Test 3: Login System for Created Accounts"""
        try:
            if not self.created_accounts:
                self.log_test(
                    "Login System",
                    False,
                    "",
                    "No accounts created to test login"
                )
                return False
            
            account = self.created_accounts[0]
            
            # Test login with created credentials
            url = f"{API_BASE}/auth/login"
            login_data = {
                "email": account["email"],
                "password": account["password"]
            }
            
            print(f"🔐 Testing login with email: {account['email']}")
            response = requests.post(url, json=login_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("token"):
                    user = data.get("user", {})
                    practice = data.get("practice", {})
                    
                    # Verify login response structure
                    if user.get("id") and practice.get("id"):
                        self.log_test(
                            "Login System",
                            True,
                            f"Login successful. User ID: {user.get('id')}, Practice ID: {practice.get('id')}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Login System",
                            False,
                            "",
                            "Missing user or practice data in login response"
                        )
                        return False
                else:
                    self.log_test(
                        "Login System",
                        False,
                        "",
                        f"Login failed: {data.get('message', 'Unknown error')}"
                    )
                    return False
            else:
                self.log_test(
                    "Login System",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Login System",
                False,
                "",
                str(e)
            )
            return False

    def test_webhook_logging(self):
        """Test 4: Webhook Logging System"""
        try:
            url = f"{API_BASE}/webhook/samcart/logs"
            
            print("📋 Testing webhook logs endpoint")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    logs = data.get("logs", [])
                    count = data.get("count", 0)
                    
                    # Verify logs structure
                    if isinstance(logs, list) and count >= 0:
                        # Check if recent test webhook is logged
                        recent_logs = [log for log in logs if log.get("customer_email") == self.test_email]
                        
                        if recent_logs:
                            self.log_test(
                                "Webhook Logging",
                                True,
                                f"Logs endpoint working. Total logs: {count}, Recent test logs found: {len(recent_logs)}"
                            )
                        else:
                            self.log_test(
                                "Webhook Logging",
                                True,
                                f"Logs endpoint working. Total logs: {count} (test webhook may not be logged yet)"
                            )
                        return True
                    else:
                        self.log_test(
                            "Webhook Logging",
                            False,
                            "",
                            "Invalid logs structure in response"
                        )
                        return False
                else:
                    self.log_test(
                        "Webhook Logging",
                        False,
                        "",
                        f"Logs endpoint error: {data.get('message', 'Unknown error')}"
                    )
                    return False
            else:
                self.log_test(
                    "Webhook Logging",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Webhook Logging",
                False,
                "",
                str(e)
            )
            return False

    def test_webhook_stats(self):
        """Test 5: Webhook Statistics"""
        try:
            url = f"{API_BASE}/webhook/samcart/stats"
            
            print("📊 Testing webhook stats endpoint")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                required_stats = ["total_webhooks", "successful_webhooks", "failed_webhooks", "success_rate", "recent_practice_signups"]
                missing_stats = [stat for stat in required_stats if stat not in data]
                
                if missing_stats:
                    self.log_test(
                        "Webhook Statistics",
                        False,
                        "",
                        f"Missing statistics: {missing_stats}"
                    )
                    return False
                
                # Verify stats are reasonable
                total = data.get("total_webhooks", 0)
                successful = data.get("successful_webhooks", 0)
                failed = data.get("failed_webhooks", 0)
                success_rate = data.get("success_rate", 0)
                signups = data.get("recent_practice_signups", 0)
                
                if total >= 0 and successful >= 0 and failed >= 0 and 0 <= success_rate <= 100 and signups >= 0:
                    self.log_test(
                        "Webhook Statistics",
                        True,
                        f"Stats: Total: {total}, Success: {successful}, Failed: {failed}, Rate: {success_rate}%, Signups: {signups}"
                    )
                    return True
                else:
                    self.log_test(
                        "Webhook Statistics",
                        False,
                        "",
                        f"Invalid statistics values: Total: {total}, Success: {successful}, Failed: {failed}, Rate: {success_rate}%"
                    )
                    return False
            else:
                self.log_test(
                    "Webhook Statistics",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Webhook Statistics",
                False,
                "",
                str(e)
            )
            return False

    def test_duplicate_prevention(self):
        """Test 6: Duplicate Account Prevention"""
        try:
            # Try to create account with same email again
            url = f"{API_BASE}/webhook/samcart/test"
            params = {"test_email": self.test_email}
            
            print(f"🔄 Testing duplicate prevention with same email: {self.test_email}")
            response = requests.post(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "duplicate":
                    self.log_test(
                        "Duplicate Prevention",
                        True,
                        "Duplicate account correctly detected and prevented"
                    )
                    return True
                elif data.get("status") == "success":
                    self.log_test(
                        "Duplicate Prevention",
                        False,
                        "",
                        "Duplicate account was not detected - new account created instead"
                    )
                    return False
                else:
                    self.log_test(
                        "Duplicate Prevention",
                        False,
                        "",
                        f"Unexpected response status: {data.get('status')}"
                    )
                    return False
            else:
                self.log_test(
                    "Duplicate Prevention",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Duplicate Prevention",
                False,
                "",
                str(e)
            )
            return False

    def test_trial_period_setup(self):
        """Test 7: 30-Day Trial Period Implementation"""
        try:
            if not self.created_accounts:
                self.log_test(
                    "Trial Period Setup",
                    False,
                    "",
                    "No accounts created to verify trial period"
                )
                return False
            
            account = self.created_accounts[0]
            
            # Login to get practice details
            url = f"{API_BASE}/auth/login"
            login_data = {
                "email": account["email"],
                "password": account["password"]
            }
            
            response = requests.post(url, json=login_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                practice = data.get("practice", {})
                subscription = practice.get("subscription", {})
                
                # Check trial status and period
                status = subscription.get("status")
                trial_end = subscription.get("trialEndDate")
                
                if status == "trial" and trial_end:
                    # Parse trial end date and verify it's approximately 30 days from now
                    from datetime import datetime, timedelta
                    try:
                        trial_end_date = datetime.fromisoformat(trial_end.replace('Z', '+00:00'))
                        now = datetime.now(trial_end_date.tzinfo)
                        days_remaining = (trial_end_date - now).days
                        
                        if 25 <= days_remaining <= 30:  # Allow some tolerance
                            self.log_test(
                                "Trial Period Setup",
                                True,
                                f"30-day trial correctly configured. Status: {status}, Days remaining: {days_remaining}"
                            )
                            return True
                        else:
                            self.log_test(
                                "Trial Period Setup",
                                False,
                                "",
                                f"Trial period incorrect. Days remaining: {days_remaining} (expected ~30)"
                            )
                            return False
                    except Exception as date_error:
                        self.log_test(
                            "Trial Period Setup",
                            False,
                            "",
                            f"Error parsing trial end date: {date_error}"
                        )
                        return False
                else:
                    self.log_test(
                        "Trial Period Setup",
                        False,
                        "",
                        f"Trial not properly configured. Status: {status}, Trial end: {trial_end}"
                    )
                    return False
            else:
                self.log_test(
                    "Trial Period Setup",
                    False,
                    "",
                    f"Could not login to verify trial period: HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Trial Period Setup",
                False,
                "",
                str(e)
            )
            return False

    def test_password_reset_functionality(self):
        """Test 8: Password Reset for SamCart Accounts"""
        try:
            if not self.created_accounts:
                self.log_test(
                    "Password Reset Functionality",
                    False,
                    "",
                    "No accounts created to test password reset"
                )
                return False
            
            account = self.created_accounts[0]
            
            # Test forgot password endpoint
            url = f"{API_BASE}/auth/forgot-password"
            reset_data = {
                "email": account["email"],
                "recovery_method": "email"
            }
            
            print(f"🔑 Testing password reset for: {account['email']}")
            response = requests.post(url, json=reset_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    sent_methods = data.get("sent_methods", [])
                    message = data.get("message", "")
                    
                    # Check if email was sent or at least attempted
                    if "email" in sent_methods or "email" in message.lower():
                        self.log_test(
                            "Password Reset Functionality",
                            True,
                            f"Password reset working. Message: {message}, Methods: {sent_methods}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Password Reset Functionality",
                            True,
                            f"Password reset endpoint working (email may not be configured). Message: {message}"
                        )
                        return True
                else:
                    self.log_test(
                        "Password Reset Functionality",
                        False,
                        "",
                        f"Password reset failed: {data.get('message', 'Unknown error')}"
                    )
                    return False
            else:
                self.log_test(
                    "Password Reset Functionality",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Password Reset Functionality",
                False,
                "",
                str(e)
            )
            return False

    def run_all_tests(self):
        """Run all SamCart webhook integration tests"""
        print("🚀 Starting SamCart Webhook Integration System Testing")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Email: {self.test_email}")
        print("=" * 60)
        print()
        
        # Run tests in order
        tests = [
            self.test_webhook_test_endpoint,
            self.test_account_creation_flow,
            self.test_login_system,
            self.test_webhook_logging,
            self.test_webhook_stats,
            self.test_duplicate_prevention,
            self.test_trial_period_setup,
            self.test_password_reset_functionality
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        
        # Print summary
        print("=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}")
            if result["error"]:
                print(f"     Error: {result['error']}")
        
        print()
        print(f"📊 Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if self.created_accounts:
            print("\n🔐 Created Test Accounts:")
            for account in self.created_accounts:
                print(f"   Email: {account['email']}")
                print(f"   Password: {account['password']}")
                print(f"   Practice ID: {account['practice_id']}")
        
        return passed == total

if __name__ == "__main__":
    tester = SamCartWebhookTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - SamCart webhook integration is working correctly!")
        exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED - Check the results above for details")
        exit(1)
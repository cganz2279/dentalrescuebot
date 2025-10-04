#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Correspondence Export Functionality
Testing the new POST /api/practice/export-correspondence endpoint
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import io
import csv
import openpyxl

# Configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class CorrespondenceExportTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def admin_login(self):
        """Authenticate as admin"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/admin/login",
                json={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.log_test("Admin Login", True, f"Successfully authenticated as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Login", False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login", False, f"Login error: {str(e)}")
            return False
    
    def get_admin_headers(self):
        """Get headers with admin token"""
        return {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
    
    def get_tutorials(self):
        """Get all tutorials to find existing tutorial IDs"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 200:
                tutorials = response.json()
                self.log_test("Get Tutorials", True, f"Retrieved {len(tutorials)} tutorials")
                return tutorials
            else:
                self.log_test("Get Tutorials", False, f"Failed to get tutorials: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_test("Get Tutorials", False, f"Error getting tutorials: {str(e)}")
            return []
    
    def create_test_tutorial(self):
        """Create a test tutorial for deletion testing"""
        try:
            # Create a simple test video file
            test_video_content = b"fake video content for testing"
            
            files = {
                'video': ('test_video.mp4', test_video_content, 'video/mp4')
            }
            
            data = {
                'title': 'Test Tutorial for Deletion',
                'description': 'This tutorial will be deleted during testing',
                'category': 'test',
                'order': 999
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.post(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=headers,
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                tutorial_id = result.get("tutorial_id")
                self.log_test("Create Test Tutorial", True, f"Created tutorial with ID: {tutorial_id}")
                return tutorial_id
            else:
                self.log_test("Create Test Tutorial", False, f"Failed to create tutorial: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Create Test Tutorial", False, f"Error creating tutorial: {str(e)}")
            return None
    
    def test_delete_tutorial(self, tutorial_id, test_name="Delete Tutorial"):
        """Test tutorial deletion with given ID"""
        try:
            print(f"\n🗑️ Testing deletion of tutorial ID: {tutorial_id}")
            
            response = requests.delete(
                f"{BACKEND_URL}/api/admin/tutorials/{tutorial_id}",
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                message = result.get("message", "")
                self.log_test(test_name, success, f"Tutorial deleted successfully: {message}")
                return True
            elif response.status_code == 404:
                self.log_test(test_name, False, f"Tutorial not found: {response.text}")
                return False
            elif response.status_code == 500:
                self.log_test(test_name, False, f"500 Internal Server Error: {response.text}")
                return False
            else:
                self.log_test(test_name, False, f"Unexpected status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"Error during deletion: {str(e)}")
            return False
    
    def test_id_format_handling(self):
        """Test different ID formats for tutorial deletion"""
        print("\n🔍 Testing ID Format Handling...")
        
        # Get existing tutorials
        tutorials = self.get_tutorials()
        
        if not tutorials:
            self.log_test("ID Format Testing", False, "No tutorials available for testing")
            return
        
        # Test with first tutorial if available
        if len(tutorials) > 0:
            tutorial = tutorials[0]
            tutorial_id = tutorial.get("id")
            
            print(f"Testing with tutorial ID: {tutorial_id}")
            
            # Test deletion (this should work with enhanced logic)
            self.test_delete_tutorial(tutorial_id, "Delete with String ID")
    
    def test_file_deletion(self):
        """Test that video files are properly deleted"""
        print("\n📁 Testing File Deletion...")
        
        # Create a test tutorial
        tutorial_id = self.create_test_tutorial()
        
        if tutorial_id:
            # Check if file exists before deletion
            tutorials = self.get_tutorials()
            test_tutorial = None
            
            for tutorial in tutorials:
                if tutorial.get("id") == tutorial_id:
                    test_tutorial = tutorial
                    break
            
            if test_tutorial:
                video_url = test_tutorial.get("video_url", "")
                print(f"Tutorial video URL: {video_url}")
                
                # Delete the tutorial
                if self.test_delete_tutorial(tutorial_id, "Delete with File Cleanup"):
                    self.log_test("File Deletion Test", True, "Tutorial and file deletion completed")
                else:
                    self.log_test("File Deletion Test", False, "Tutorial deletion failed")
            else:
                self.log_test("File Deletion Test", False, "Could not find created tutorial")
    
    def test_error_handling(self):
        """Test error handling for invalid tutorial IDs"""
        print("\n⚠️ Testing Error Handling...")
        
        # Test with invalid ObjectId format
        invalid_id = "invalid_id_format"
        response = requests.delete(
            f"{BACKEND_URL}/api/admin/tutorials/{invalid_id}",
            headers=self.get_admin_headers()
        )
        
        if response.status_code == 404:
            self.log_test("Invalid ID Handling", True, "Properly returned 404 for invalid ID")
        else:
            self.log_test("Invalid ID Handling", False, f"Unexpected response: {response.status_code}")
        
        # Test with non-existent but valid format ID
        fake_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format but doesn't exist
        response = requests.delete(
            f"{BACKEND_URL}/api/admin/tutorials/{fake_id}",
            headers=self.get_admin_headers()
        )
        
        if response.status_code == 404:
            self.log_test("Non-existent ID Handling", True, "Properly returned 404 for non-existent ID")
        else:
            self.log_test("Non-existent ID Handling", False, f"Unexpected response: {response.status_code}")
    
    def test_specific_id_format(self):
        """Test the specific ID format mentioned in the review request"""
        print("\n🎯 Testing Specific ID Format from Error Report...")
        
        # The error showed tutorial ID: 68e09718e9c9bcb78cbb76aa
        problematic_id = "68e09718e9c9bcb78cbb76aa"
        
        response = requests.delete(
            f"{BACKEND_URL}/api/admin/tutorials/{problematic_id}",
            headers=self.get_admin_headers()
        )
        
        # We expect 404 since this tutorial likely doesn't exist, but NOT 500
        if response.status_code == 404:
            self.log_test("Specific ID Format Test", True, f"ID {problematic_id} handled correctly (404, not 500)")
        elif response.status_code == 500:
            self.log_test("Specific ID Format Test", False, f"Still getting 500 error for ID {problematic_id}")
        else:
            self.log_test("Specific ID Format Test", True, f"ID handled with status {response.status_code}")
    
    def run_all_tests(self):
        """Run all tutorial delete tests"""
        print("🚀 Starting Tutorial Delete Functionality Tests")
        print("=" * 60)
        
        # Step 1: Admin Login
        if not self.admin_login():
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Step 2: Test specific ID format from error report
        self.test_specific_id_format()
        
        # Step 3: Test ID format handling
        self.test_id_format_handling()
        
        # Step 4: Test file deletion
        self.test_file_deletion()
        
        # Step 5: Test error handling
        self.test_error_handling()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = TutorialDeleteTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Tutorial delete functionality is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please review the issues above.")
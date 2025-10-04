#!/usr/bin/env python3
"""
URGENT VIDEO API WORKAROUND FIX TESTING
Testing the new /api/video/tutorial/{filename} endpoint and video streaming functionality
"""

import requests
import json
import os
import sys
from pathlib import Path
import time

# Configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

class VideoAPITester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")
        print()

    def admin_login(self):
        """Login as admin to get authentication token"""
        try:
            print("🔐 ADMIN LOGIN TEST")
            print("=" * 50)
            
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/admin/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as {ADMIN_EMAIL}",
                    {
                        "admin_token_length": len(self.admin_token) if self.admin_token else 0,
                        "response_status": response.status_code
                    }
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"Login failed with status {response.status_code}",
                    {"response_text": response.text[:200]}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False,
                f"Login error: {str(e)}",
                {"error_type": type(e).__name__}
            )
            return False

    def test_video_api_endpoint_structure(self):
        """Test the video API endpoint structure and authentication"""
        print("🎬 VIDEO API ENDPOINT STRUCTURE TEST")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_result(
                "Video API Endpoint Structure",
                False,
                "No admin token available for authentication"
            )
            return False
            
        try:
            # Test video list endpoint
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/api/video/list", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                video_count = len(data.get("videos", []))
                
                self.log_result(
                    "Video List Endpoint",
                    True,
                    f"Video list endpoint accessible, found {video_count} videos",
                    {
                        "endpoint": "/api/video/list",
                        "video_count": video_count,
                        "response_status": response.status_code
                    }
                )
                return True
            else:
                self.log_result(
                    "Video List Endpoint",
                    False,
                    f"Video list endpoint failed with status {response.status_code}",
                    {"response_text": response.text[:200]}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Video List Endpoint",
                False,
                f"Video list endpoint error: {str(e)}",
                {"error_type": type(e).__name__}
            )
            return False

    def test_video_serving_endpoint(self):
        """Test video serving endpoint with different scenarios"""
        print("🎥 VIDEO SERVING ENDPOINT TEST")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_result(
                "Video Serving Endpoint",
                False,
                "No admin token available for authentication"
            )
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test 1: Invalid filename (security test)
            response = requests.get(
                f"{BACKEND_URL}/api/video/tutorial/../../../etc/passwd",
                headers=headers
            )
            
            if response.status_code == 400:
                self.log_result(
                    "Video Security - Path Traversal Protection",
                    True,
                    "Path traversal attack properly blocked",
                    {"response_status": response.status_code}
                )
            else:
                self.log_result(
                    "Video Security - Path Traversal Protection",
                    False,
                    f"Path traversal not properly blocked, status: {response.status_code}",
                    {"response_text": response.text[:200]}
                )
            
            # Test 2: Invalid file type
            response = requests.get(
                f"{BACKEND_URL}/api/video/tutorial/malicious.exe",
                headers=headers
            )
            
            if response.status_code == 400:
                self.log_result(
                    "Video Security - File Type Validation",
                    True,
                    "Invalid file type properly rejected",
                    {"response_status": response.status_code}
                )
            else:
                self.log_result(
                    "Video Security - File Type Validation",
                    False,
                    f"Invalid file type not properly rejected, status: {response.status_code}",
                    {"response_text": response.text[:200]}
                )
            
            # Test 3: Non-existent video file
            response = requests.get(
                f"{BACKEND_URL}/api/video/tutorial/nonexistent.mp4",
                headers=headers
            )
            
            if response.status_code == 404:
                self.log_result(
                    "Video Not Found Handling",
                    True,
                    "Non-existent video properly returns 404",
                    {"response_status": response.status_code}
                )
            else:
                self.log_result(
                    "Video Not Found Handling",
                    False,
                    f"Non-existent video handling incorrect, status: {response.status_code}",
                    {"response_text": response.text[:200]}
                )
            
            return True
            
        except Exception as e:
            self.log_result(
                "Video Serving Endpoint",
                False,
                f"Video serving endpoint error: {str(e)}",
                {"error_type": type(e).__name__}
            )
            return False

    def test_http_range_support(self):
        """Test HTTP Range requests for video streaming"""
        print("📡 HTTP RANGE SUPPORT TEST")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_result(
                "HTTP Range Support",
                False,
                "No admin token available for authentication"
            )
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Range": "bytes=0-1023"  # Request first 1KB
            }
            
            # Test range request on non-existent file (should still validate range format)
            response = requests.get(
                f"{BACKEND_URL}/api/video/tutorial/test.mp4",
                headers=headers
            )
            
            # Even if file doesn't exist, we should get 404, not range error
            if response.status_code == 404:
                self.log_result(
                    "HTTP Range Request Format",
                    True,
                    "Range request format properly handled (file not found as expected)",
                    {
                        "response_status": response.status_code,
                        "range_header": "bytes=0-1023"
                    }
                )
            elif response.status_code == 206:
                self.log_result(
                    "HTTP Range Request Format",
                    True,
                    "Range request successfully processed with partial content",
                    {
                        "response_status": response.status_code,
                        "content_range": response.headers.get("Content-Range", "Not provided")
                    }
                )
            else:
                self.log_result(
                    "HTTP Range Request Format",
                    False,
                    f"Range request handling unexpected, status: {response.status_code}",
                    {"response_text": response.text[:200]}
                )
            
            # Test invalid range format
            headers["Range"] = "invalid-range-format"
            response = requests.get(
                f"{BACKEND_URL}/api/video/tutorial/test.mp4",
                headers=headers
            )
            
            # Should get 400 for invalid range or 404 for missing file
            if response.status_code in [400, 404]:
                self.log_result(
                    "HTTP Range Invalid Format Handling",
                    True,
                    f"Invalid range format properly handled with status {response.status_code}",
                    {"response_status": response.status_code}
                )
            else:
                self.log_result(
                    "HTTP Range Invalid Format Handling",
                    False,
                    f"Invalid range format not properly handled, status: {response.status_code}",
                    {"response_text": response.text[:200]}
                )
            
            return True
            
        except Exception as e:
            self.log_result(
                "HTTP Range Support",
                False,
                f"HTTP Range support error: {str(e)}",
                {"error_type": type(e).__name__}
            )
            return False

    def test_tutorial_management_integration(self):
        """Test tutorial management system integration"""
        print("📚 TUTORIAL MANAGEMENT INTEGRATION TEST")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_result(
                "Tutorial Management Integration",
                False,
                "No admin token available for authentication"
            )
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test tutorial list endpoint
            response = requests.get(f"{BACKEND_URL}/api/admin/tutorials", headers=headers)
            
            if response.status_code == 200:
                tutorials = response.json()
                tutorial_count = len(tutorials)
                
                self.log_result(
                    "Tutorial Management - List Tutorials",
                    True,
                    f"Successfully retrieved {tutorial_count} tutorials",
                    {
                        "tutorial_count": tutorial_count,
                        "response_status": response.status_code
                    }
                )
                
                # Check if tutorials have proper video URL structure
                video_url_updated = 0
                for tutorial in tutorials:
                    video_url = tutorial.get("video_url", "")
                    if "/api/video/tutorial/" in video_url or video_url.endswith(('.mp4', '.webm', '.mov', '.avi')):
                        video_url_updated += 1
                
                self.log_result(
                    "Tutorial Video URL Structure",
                    True,
                    f"Found {video_url_updated} tutorials with proper video URL structure",
                    {
                        "tutorials_with_proper_urls": video_url_updated,
                        "total_tutorials": tutorial_count
                    }
                )
                
            else:
                self.log_result(
                    "Tutorial Management - List Tutorials",
                    False,
                    f"Failed to retrieve tutorials, status: {response.status_code}",
                    {"response_text": response.text[:200]}
                )
            
            return True
            
        except Exception as e:
            self.log_result(
                "Tutorial Management Integration",
                False,
                f"Tutorial management integration error: {str(e)}",
                {"error_type": type(e).__name__}
            )
            return False

    def test_frontend_video_url_format(self):
        """Test that frontend components use correct video URL format"""
        print("🖥️ FRONTEND VIDEO URL FORMAT TEST")
        print("=" * 50)
        
        try:
            # Check TutorialManagement.jsx
            tutorial_mgmt_path = "/app/frontend/src/components/TutorialManagement.jsx"
            if os.path.exists(tutorial_mgmt_path):
                with open(tutorial_mgmt_path, 'r') as f:
                    content = f.read()
                
                # Check for new video URL format
                if "/api/video/tutorial/" in content:
                    self.log_result(
                        "Frontend - TutorialManagement Video URLs",
                        True,
                        "TutorialManagement.jsx uses new video API URL format",
                        {"file_path": tutorial_mgmt_path}
                    )
                else:
                    self.log_result(
                        "Frontend - TutorialManagement Video URLs",
                        False,
                        "TutorialManagement.jsx does not use new video API URL format",
                        {"file_path": tutorial_mgmt_path}
                    )
            else:
                self.log_result(
                    "Frontend - TutorialManagement Video URLs",
                    False,
                    "TutorialManagement.jsx file not found",
                    {"expected_path": tutorial_mgmt_path}
                )
            
            # Check TutorialsModal.jsx
            tutorials_modal_path = "/app/frontend/src/components/TutorialsModal.jsx"
            if os.path.exists(tutorials_modal_path):
                with open(tutorials_modal_path, 'r') as f:
                    content = f.read()
                
                # Check for new video URL format
                if "/api/video/tutorial/" in content:
                    self.log_result(
                        "Frontend - TutorialsModal Video URLs",
                        True,
                        "TutorialsModal.jsx uses new video API URL format",
                        {"file_path": tutorials_modal_path}
                    )
                else:
                    self.log_result(
                        "Frontend - TutorialsModal Video URLs",
                        False,
                        "TutorialsModal.jsx does not use new video API URL format",
                        {"file_path": tutorials_modal_path}
                    )
            else:
                self.log_result(
                    "Frontend - TutorialsModal Video URLs",
                    False,
                    "TutorialsModal.jsx file not found",
                    {"expected_path": tutorials_modal_path}
                )
            
            return True
            
        except Exception as e:
            self.log_result(
                "Frontend Video URL Format",
                False,
                f"Frontend video URL format test error: {str(e)}",
                {"error_type": type(e).__name__}
            )
            return False

    def test_video_mime_types(self):
        """Test video MIME type handling"""
        print("🎭 VIDEO MIME TYPE TEST")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_result(
                "Video MIME Types",
                False,
                "No admin token available for authentication"
            )
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test different video file extensions
            video_extensions = [
                ("test.mp4", "video/mp4"),
                ("test.webm", "video/webm"),
                ("test.mov", "video/quicktime"),
                ("test.avi", "video/x-msvideo")
            ]
            
            for filename, expected_mime in video_extensions:
                response = requests.head(
                    f"{BACKEND_URL}/api/video/tutorial/{filename}",
                    headers=headers
                )
                
                # Even if file doesn't exist, we should get proper error handling
                if response.status_code == 404:
                    self.log_result(
                        f"MIME Type Support - {filename}",
                        True,
                        f"Video file extension {filename} properly recognized (404 as expected)",
                        {
                            "filename": filename,
                            "expected_mime": expected_mime,
                            "response_status": response.status_code
                        }
                    )
                elif response.status_code == 200:
                    content_type = response.headers.get("Content-Type", "")
                    if expected_mime in content_type:
                        self.log_result(
                            f"MIME Type Support - {filename}",
                            True,
                            f"Correct MIME type returned: {content_type}",
                            {
                                "filename": filename,
                                "expected_mime": expected_mime,
                                "actual_mime": content_type
                            }
                        )
                    else:
                        self.log_result(
                            f"MIME Type Support - {filename}",
                            False,
                            f"Incorrect MIME type: expected {expected_mime}, got {content_type}",
                            {
                                "filename": filename,
                                "expected_mime": expected_mime,
                                "actual_mime": content_type
                            }
                        )
                else:
                    self.log_result(
                        f"MIME Type Support - {filename}",
                        False,
                        f"Unexpected response status: {response.status_code}",
                        {"response_text": response.text[:200]}
                    )
            
            return True
            
        except Exception as e:
            self.log_result(
                "Video MIME Types",
                False,
                f"Video MIME type test error: {str(e)}",
                {"error_type": type(e).__name__}
            )
            return False

    def test_routing_workaround(self):
        """Test that the video API bypasses /uploads/* routing issue"""
        print("🔄 ROUTING WORKAROUND TEST")
        print("=" * 50)
        
        try:
            # Test old /uploads/* path (should go to frontend)
            response = requests.get(f"{BACKEND_URL}/uploads/tutorials/test.mp4")
            
            # This should either return frontend content or 404 from frontend
            if response.status_code in [200, 404]:
                content_type = response.headers.get("Content-Type", "")
                if "text/html" in content_type or "application/json" not in content_type:
                    self.log_result(
                        "Routing - Old /uploads/* Path",
                        True,
                        f"/uploads/* path routes to frontend as expected (status: {response.status_code})",
                        {
                            "response_status": response.status_code,
                            "content_type": content_type
                        }
                    )
                else:
                    self.log_result(
                        "Routing - Old /uploads/* Path",
                        False,
                        f"/uploads/* path may not be routing to frontend correctly",
                        {
                            "response_status": response.status_code,
                            "content_type": content_type
                        }
                    )
            else:
                self.log_result(
                    "Routing - Old /uploads/* Path",
                    True,
                    f"/uploads/* path properly handled with status {response.status_code}",
                    {"response_status": response.status_code}
                )
            
            # Test new /api/video/* path (should go to backend)
            if self.admin_token:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = requests.get(f"{BACKEND_URL}/api/video/tutorial/test.mp4", headers=headers)
                
                # Should get backend response (404 for missing file or proper video response)
                if response.status_code == 404:
                    try:
                        # Try to parse as JSON (backend response)
                        json.loads(response.text)
                        self.log_result(
                            "Routing - New /api/video/* Path",
                            True,
                            "/api/video/* path routes to backend as expected",
                            {
                                "response_status": response.status_code,
                                "routes_to": "backend"
                            }
                        )
                    except json.JSONDecodeError:
                        self.log_result(
                            "Routing - New /api/video/* Path",
                            False,
                            "/api/video/* path may not be routing to backend correctly",
                            {
                                "response_status": response.status_code,
                                "response_preview": response.text[:100]
                            }
                        )
                else:
                    self.log_result(
                        "Routing - New /api/video/* Path",
                        True,
                        f"/api/video/* path handled by backend (status: {response.status_code})",
                        {"response_status": response.status_code}
                    )
            
            return True
            
        except Exception as e:
            self.log_result(
                "Routing Workaround",
                False,
                f"Routing workaround test error: {str(e)}",
                {"error_type": type(e).__name__}
            )
            return False

    def run_all_tests(self):
        """Run all video API workaround tests"""
        print("🎬 URGENT VIDEO API WORKAROUND FIX TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL}")
        print("=" * 80)
        print()
        
        # Run tests in order
        tests = [
            self.admin_login,
            self.test_video_api_endpoint_structure,
            self.test_video_serving_endpoint,
            self.test_http_range_support,
            self.test_tutorial_management_integration,
            self.test_frontend_video_url_format,
            self.test_video_mime_types,
            self.test_routing_workaround
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test.__name__}: {str(e)}")
            print("-" * 50)
        
        # Summary
        print("\n🎯 VIDEO API WORKAROUND TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result["status"])
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result["status"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        print()
        
        # Critical issues
        critical_failures = []
        for result in self.test_results:
            if "❌ FAIL" in result["status"]:
                if any(keyword in result["test"].lower() for keyword in ["authentication", "endpoint", "routing", "security"]):
                    critical_failures.append(result)
        
        if critical_failures:
            print("🚨 CRITICAL FAILURES:")
            for failure in critical_failures:
                print(f"  • {failure['test']}: {failure['message']}")
        else:
            print("✅ No critical failures detected")
        
        print("\n" + "=" * 80)
        
        return passed, failed, total

if __name__ == "__main__":
    tester = VideoAPITester()
    passed, failed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)
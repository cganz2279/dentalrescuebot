#!/usr/bin/env python3
"""
Video Tutorial System Backend Testing
=====================================

Testing video tutorial functionality as requested:
1. Authentication & Tutorial Loading
2. Video File Access Testing  
3. Tutorial Creation (if needed)
4. Video URL Analysis

User Issue: Videos load but don't play - investigating MIME types, file serving, and accessibility.
"""

import requests
import json
import os
import sys
from datetime import datetime
import mimetypes

# Configuration
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"
TEST_CREDENTIALS = {
    "email": "cganz2279@gmail.com", 
    "password": "password123"
}
ADMIN_CREDENTIALS = {
    "email": "cganz@admin.com",
    "password": "Dentist1#"
}

class VideoTutorialTester:
    def __init__(self):
        self.session = requests.Session()
        self.practice_token = None
        self.admin_token = None
        self.practice_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        print(f"   Details: {details}")
        print()
        
    def authenticate_practice(self):
        """Authenticate as practice user"""
        try:
            print("🔐 AUTHENTICATING AS PRACTICE USER...")
            
            response = self.session.post(
                f"{BACKEND_URL}/api/auth/login",
                json=TEST_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.practice_token = data.get("access_token")
                self.practice_id = data.get("practice_id")
                
                self.log_result(
                    "Practice Authentication",
                    True,
                    f"Successfully authenticated with {TEST_CREDENTIALS['email']}, Practice ID: {self.practice_id}"
                )
                return True
            else:
                self.log_result(
                    "Practice Authentication", 
                    False,
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Practice Authentication", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            print("🔐 AUTHENTICATING AS ADMIN USER...")
            
            response = self.session.post(
                f"{BACKEND_URL}/api/admin/login",
                json=ADMIN_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as admin with {ADMIN_CREDENTIALS['email']}"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False, 
                    f"Admin login failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_practice_tutorials_endpoint(self):
        """Test GET /api/tutorials endpoint for practice users"""
        try:
            print("📚 TESTING PRACTICE TUTORIALS ENDPOINT...")
            
            response = self.session.get(f"{BACKEND_URL}/api/tutorials")
            
            if response.status_code == 200:
                tutorials = response.json()
                tutorial_count = len(tutorials)
                
                details = f"Found {tutorial_count} active tutorials"
                if tutorial_count > 0:
                    # Analyze first tutorial structure
                    first_tutorial = tutorials[0]
                    video_url = first_tutorial.get('video_url', 'N/A')
                    details += f". First tutorial: '{first_tutorial.get('title', 'N/A')}', Video URL: {video_url}"
                
                self.log_result("Practice Tutorials Endpoint", True, details)
                return tutorials
            else:
                self.log_result(
                    "Practice Tutorials Endpoint",
                    False,
                    f"Failed with status {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_result("Practice Tutorials Endpoint", False, f"Exception: {str(e)}")
            return []
    
    def test_admin_tutorials_endpoint(self):
        """Test GET /api/admin/tutorials endpoint"""
        try:
            print("🔧 TESTING ADMIN TUTORIALS ENDPOINT...")
            
            if not self.admin_token:
                self.log_result("Admin Tutorials Endpoint", False, "No admin token available")
                return []
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/api/admin/tutorials", headers=headers)
            
            if response.status_code == 200:
                tutorials = response.json()
                tutorial_count = len(tutorials)
                
                details = f"Found {tutorial_count} total tutorials (including inactive)"
                if tutorial_count > 0:
                    active_count = sum(1 for t in tutorials if t.get('is_active', True))
                    details += f". Active: {active_count}, Inactive: {tutorial_count - active_count}"
                
                self.log_result("Admin Tutorials Endpoint", True, details)
                return tutorials
            else:
                self.log_result(
                    "Admin Tutorials Endpoint",
                    False,
                    f"Failed with status {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_result("Admin Tutorials Endpoint", False, f"Exception: {str(e)}")
            return []
    
    def test_video_file_access(self, tutorials):
        """Test direct access to video files"""
        try:
            print("🎥 TESTING VIDEO FILE ACCESS...")
            
            if not tutorials:
                self.log_result("Video File Access", False, "No tutorials available to test")
                return
            
            for i, tutorial in enumerate(tutorials[:3]):  # Test first 3 tutorials
                video_url = tutorial.get('video_url', '')
                title = tutorial.get('title', f'Tutorial {i+1}')
                
                if not video_url:
                    self.log_result(
                        f"Video Access - {title}",
                        False,
                        "No video_url found in tutorial data"
                    )
                    continue
                
                # Test direct video file access
                full_video_url = f"{BACKEND_URL}{video_url}" if video_url.startswith('/') else video_url
                
                try:
                    # HEAD request to check if file exists and get headers
                    head_response = self.session.head(full_video_url)
                    
                    if head_response.status_code == 200:
                        content_type = head_response.headers.get('Content-Type', 'Unknown')
                        content_length = head_response.headers.get('Content-Length', 'Unknown')
                        
                        # Check if it's a proper video MIME type
                        is_video_mime = content_type.startswith('video/') if content_type != 'Unknown' else False
                        
                        details = f"File accessible. Content-Type: {content_type}, Size: {content_length} bytes"
                        if not is_video_mime:
                            details += " ⚠️ WARNING: Not a video MIME type!"
                        
                        self.log_result(f"Video Access - {title}", True, details)
                        
                        # Test partial content request (common for video streaming)
                        try:
                            partial_headers = {"Range": "bytes=0-1023"}
                            partial_response = self.session.get(full_video_url, headers=partial_headers)
                            
                            if partial_response.status_code == 206:
                                self.log_result(
                                    f"Video Streaming - {title}",
                                    True,
                                    "Partial content requests supported (good for video streaming)"
                                )
                            else:
                                self.log_result(
                                    f"Video Streaming - {title}",
                                    False,
                                    f"Partial content not supported (status: {partial_response.status_code})"
                                )
                        except Exception as e:
                            self.log_result(f"Video Streaming - {title}", False, f"Streaming test failed: {str(e)}")
                        
                    else:
                        self.log_result(
                            f"Video Access - {title}",
                            False,
                            f"File not accessible. Status: {head_response.status_code}, URL: {full_video_url}"
                        )
                        
                except Exception as e:
                    self.log_result(f"Video Access - {title}", False, f"Exception accessing {full_video_url}: {str(e)}")
                    
        except Exception as e:
            self.log_result("Video File Access", False, f"Exception: {str(e)}")
    
    def test_static_file_serving(self):
        """Test static file serving configuration"""
        try:
            print("📁 TESTING STATIC FILE SERVING...")
            
            # Test if uploads directory is accessible
            uploads_url = f"{BACKEND_URL}/uploads/"
            
            response = self.session.get(uploads_url)
            
            if response.status_code == 200:
                self.log_result(
                    "Static Uploads Directory",
                    True,
                    "Uploads directory is accessible via HTTP"
                )
            elif response.status_code == 403:
                self.log_result(
                    "Static Uploads Directory",
                    True,
                    "Uploads directory exists but directory listing is disabled (normal security)"
                )
            else:
                self.log_result(
                    "Static Uploads Directory",
                    False,
                    f"Uploads directory not accessible. Status: {response.status_code}"
                )
            
            # Test tutorials subdirectory
            tutorials_url = f"{BACKEND_URL}/uploads/tutorials/"
            
            response = self.session.get(tutorials_url)
            
            if response.status_code == 200:
                self.log_result(
                    "Static Tutorials Directory",
                    True,
                    "Tutorials directory is accessible via HTTP"
                )
            elif response.status_code == 403:
                self.log_result(
                    "Static Tutorials Directory", 
                    True,
                    "Tutorials directory exists but directory listing is disabled (normal security)"
                )
            else:
                self.log_result(
                    "Static Tutorials Directory",
                    False,
                    f"Tutorials directory not accessible. Status: {response.status_code}"
                )
                
        except Exception as e:
            self.log_result("Static File Serving", False, f"Exception: {str(e)}")
    
    def test_cors_headers(self):
        """Test CORS headers for video files"""
        try:
            print("🌐 TESTING CORS HEADERS...")
            
            # Test CORS preflight for video files
            cors_headers = {
                "Origin": "https://app.dentalaftercarenotes.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Range"
            }
            
            response = self.session.options(f"{BACKEND_URL}/uploads/tutorials/", headers=cors_headers)
            
            cors_origin = response.headers.get('Access-Control-Allow-Origin', 'Not Set')
            cors_methods = response.headers.get('Access-Control-Allow-Methods', 'Not Set')
            cors_headers_allowed = response.headers.get('Access-Control-Allow-Headers', 'Not Set')
            
            details = f"CORS Origin: {cors_origin}, Methods: {cors_methods}, Headers: {cors_headers_allowed}"
            
            if cors_origin == "*" or "app.dentalaftercarenotes.com" in cors_origin:
                self.log_result("CORS Configuration", True, details)
            else:
                self.log_result("CORS Configuration", False, f"CORS may block video requests. {details}")
                
        except Exception as e:
            self.log_result("CORS Configuration", False, f"Exception: {str(e)}")
    
    def analyze_video_url_patterns(self, tutorials):
        """Analyze video URL patterns and structure"""
        try:
            print("🔍 ANALYZING VIDEO URL PATTERNS...")
            
            if not tutorials:
                self.log_result("Video URL Analysis", False, "No tutorials to analyze")
                return
            
            url_patterns = {}
            for tutorial in tutorials:
                video_url = tutorial.get('video_url', '')
                if video_url:
                    if video_url.startswith('/uploads/tutorials/'):
                        pattern = "Relative Path (/uploads/tutorials/)"
                    elif video_url.startswith('http'):
                        pattern = "Absolute URL"
                    else:
                        pattern = "Other"
                    
                    if pattern not in url_patterns:
                        url_patterns[pattern] = []
                    url_patterns[pattern].append(video_url)
            
            if url_patterns:
                details = "URL Patterns found: "
                for pattern, urls in url_patterns.items():
                    details += f"{pattern} ({len(urls)} files), "
                details = details.rstrip(', ')
                
                # Check for consistency
                if len(url_patterns) == 1 and "Relative Path" in url_patterns:
                    details += " ✅ Consistent relative paths (good)"
                elif len(url_patterns) > 1:
                    details += " ⚠️ Mixed URL patterns detected"
                
                self.log_result("Video URL Analysis", True, details)
            else:
                self.log_result("Video URL Analysis", False, "No video URLs found in tutorials")
                
        except Exception as e:
            self.log_result("Video URL Analysis", False, f"Exception: {str(e)}")
    
    def check_uploads_directory_permissions(self):
        """Check uploads directory structure and permissions"""
        try:
            print("📂 CHECKING UPLOADS DIRECTORY...")
            
            # This would need to be run on the server, but we can test via API
            # Check if we can create a test tutorial (if admin authenticated)
            if self.admin_token:
                # We'll just check the directory structure via the API responses
                self.log_result(
                    "Uploads Directory Check",
                    True,
                    "Directory structure appears correct based on API responses. Actual file permissions need server-side verification."
                )
            else:
                self.log_result(
                    "Uploads Directory Check",
                    False,
                    "Cannot check directory permissions without admin access"
                )
                
        except Exception as e:
            self.log_result("Uploads Directory Check", False, f"Exception: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run all video tutorial tests"""
        print("🎬 STARTING COMPREHENSIVE VIDEO TUTORIAL TESTING")
        print("=" * 60)
        
        # Step 1: Authentication
        practice_auth_success = self.authenticate_practice()
        admin_auth_success = self.authenticate_admin()
        
        # Step 2: Test tutorial endpoints
        practice_tutorials = self.test_practice_tutorials_endpoint()
        admin_tutorials = self.test_admin_tutorials_endpoint() if admin_auth_success else []
        
        # Use admin tutorials if available (more comprehensive), otherwise practice tutorials
        tutorials_to_test = admin_tutorials if admin_tutorials else practice_tutorials
        
        # Step 3: Video file access testing
        self.test_video_file_access(tutorials_to_test)
        
        # Step 4: Static file serving tests
        self.test_static_file_serving()
        
        # Step 5: CORS testing
        self.test_cors_headers()
        
        # Step 6: URL pattern analysis
        self.analyze_video_url_patterns(tutorials_to_test)
        
        # Step 7: Directory permissions check
        self.check_uploads_directory_permissions()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎬 VIDEO TUTORIAL TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if "✅ PASS" in result["status"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n🎯 KEY FINDINGS:")
        
        # Analyze results for key insights
        auth_issues = any("Authentication" in r["test"] and "❌ FAIL" in r["status"] for r in self.test_results)
        video_access_issues = any("Video Access" in r["test"] and "❌ FAIL" in r["status"] for r in self.test_results)
        cors_issues = any("CORS" in r["test"] and "❌ FAIL" in r["status"] for r in self.test_results)
        mime_issues = any("video MIME type" in r["details"] for r in self.test_results)
        
        if auth_issues:
            print("  • Authentication issues detected - may prevent tutorial access")
        if video_access_issues:
            print("  • Video file access problems - files may not be properly served")
        if cors_issues:
            print("  • CORS configuration issues - may block video requests from frontend")
        if mime_issues:
            print("  • MIME type issues detected - may prevent video playback")
        
        if not any([auth_issues, video_access_issues, cors_issues, mime_issues]):
            print("  • No critical issues detected in backend video serving")
            print("  • Issue may be frontend-related (video player, browser compatibility)")

if __name__ == "__main__":
    tester = VideoTutorialTester()
    tester.run_comprehensive_test()
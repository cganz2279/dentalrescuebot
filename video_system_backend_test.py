#!/usr/bin/env python3
"""
URGENT Video Tutorial System Investigation
==========================================

Testing video tutorial upload and playback system as requested:
1. Test video upload process with admin credentials
2. Test video serving and static file configuration  
3. Check tutorial system endpoints
4. Investigate infrastructure routing issues
5. Test video file analysis and MIME types

User Issue: Videos don't upload correctly and don't play
Expected Issues: Reverse proxy routing, MIME types, file corruption
"""

import requests
import json
import os
import sys
from datetime import datetime
import mimetypes
import tempfile
import io

# Configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
ADMIN_CREDENTIALS = {
    "email": "cganz@admin.com",
    "password": "Dentist1#"
}
PRACTICE_CREDENTIALS = {
    "email": "cganz2279@gmail.com", 
    "password": "password123"
}

class VideoSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.practice_token = None
        self.test_results = []
        self.created_tutorials = []
        
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
                self.admin_token = data.get("token")
                
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
    
    def authenticate_practice(self):
        """Authenticate as practice user"""
        try:
            print("🔐 AUTHENTICATING AS PRACTICE USER...")
            
            response = self.session.post(
                f"{BACKEND_URL}/api/auth/login",
                json=PRACTICE_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.practice_token = data.get("access_token")
                
                self.log_result(
                    "Practice Authentication",
                    True,
                    f"Successfully authenticated with {PRACTICE_CREDENTIALS['email']}"
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
    
    def create_test_video_file(self, filename="test_video.mp4", size_kb=100):
        """Create a test video file for upload testing"""
        try:
            # Create a simple test file that mimics an MP4 structure
            # This won't be a real playable video, but will test upload functionality
            
            # MP4 file signature and basic structure
            mp4_header = b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom'
            
            # Create file content with proper size
            content_size = (size_kb * 1024) - len(mp4_header)
            padding = b'\x00' * max(0, content_size)
            
            file_content = mp4_header + padding
            
            return io.BytesIO(file_content), filename
            
        except Exception as e:
            print(f"Error creating test video file: {e}")
            return None, None
    
    def test_video_upload(self):
        """Test video upload functionality"""
        try:
            print("📤 TESTING VIDEO UPLOAD FUNCTIONALITY...")
            
            if not self.admin_token:
                self.log_result("Video Upload Test", False, "No admin token available")
                return None
            
            # Create test video file
            video_file, filename = self.create_test_video_file("test_tutorial_video.mp4", 50)
            if not video_file:
                self.log_result("Video Upload Test", False, "Failed to create test video file")
                return None
            
            # Prepare upload data
            files = {
                'video': (filename, video_file, 'video/mp4')
            }
            data = {
                'title': 'Test Tutorial Video Upload',
                'description': 'Testing video upload functionality for tutorial system',
                'category': 'test',
                'order': 1
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Upload video
            response = self.session.post(
                f"{BACKEND_URL}/api/admin/tutorials",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result_data = response.json()
                tutorial_id = result_data.get('tutorial_id')
                
                if tutorial_id:
                    self.created_tutorials.append(tutorial_id)
                
                self.log_result(
                    "Video Upload Test",
                    True,
                    f"Successfully uploaded video. Tutorial ID: {tutorial_id}, Response: {result_data.get('message', 'Success')}"
                )
                return tutorial_id
            else:
                self.log_result(
                    "Video Upload Test",
                    False,
                    f"Upload failed with status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Video Upload Test", False, f"Exception: {str(e)}")
            return None
    
    def test_multiple_video_uploads(self):
        """Test multiple video uploads to check consistency"""
        try:
            print("📤 TESTING MULTIPLE VIDEO UPLOADS...")
            
            if not self.admin_token:
                self.log_result("Multiple Video Upload Test", False, "No admin token available")
                return []
            
            uploaded_tutorials = []
            
            # Upload 3 test videos
            for i in range(3):
                video_file, filename = self.create_test_video_file(f"test_video_{i+1}.mp4", 25)
                if not video_file:
                    continue
                
                files = {
                    'video': (filename, video_file, 'video/mp4')
                }
                data = {
                    'title': f'Test Tutorial {i+1}',
                    'description': f'Test tutorial video {i+1} for upload testing',
                    'category': 'test',
                    'order': i+1
                }
                
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                
                response = self.session.post(
                    f"{BACKEND_URL}/api/admin/tutorials",
                    files=files,
                    data=data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result_data = response.json()
                    tutorial_id = result_data.get('tutorial_id')
                    if tutorial_id:
                        uploaded_tutorials.append(tutorial_id)
                        self.created_tutorials.append(tutorial_id)
            
            if len(uploaded_tutorials) >= 2:
                self.log_result(
                    "Multiple Video Upload Test",
                    True,
                    f"Successfully uploaded {len(uploaded_tutorials)} videos. Tutorial IDs: {uploaded_tutorials}"
                )
            else:
                self.log_result(
                    "Multiple Video Upload Test",
                    False,
                    f"Only uploaded {len(uploaded_tutorials)} out of 3 videos"
                )
            
            return uploaded_tutorials
            
        except Exception as e:
            self.log_result("Multiple Video Upload Test", False, f"Exception: {str(e)}")
            return []
    
    def test_tutorial_retrieval(self):
        """Test tutorial retrieval endpoints"""
        try:
            print("📚 TESTING TUTORIAL RETRIEVAL...")
            
            # Test practice endpoint (public)
            response = self.session.get(f"{BACKEND_URL}/api/tutorials")
            
            if response.status_code == 200:
                tutorials = response.json()
                tutorial_count = len(tutorials)
                
                self.log_result(
                    "Practice Tutorial Retrieval",
                    True,
                    f"Retrieved {tutorial_count} active tutorials from practice endpoint"
                )
                
                # Test admin endpoint
                if self.admin_token:
                    headers = {"Authorization": f"Bearer {self.admin_token}"}
                    admin_response = self.session.get(f"{BACKEND_URL}/api/admin/tutorials", headers=headers)
                    
                    if admin_response.status_code == 200:
                        admin_tutorials = admin_response.json()
                        admin_count = len(admin_tutorials)
                        
                        self.log_result(
                            "Admin Tutorial Retrieval",
                            True,
                            f"Retrieved {admin_count} total tutorials from admin endpoint"
                        )
                        
                        return admin_tutorials
                    else:
                        self.log_result(
                            "Admin Tutorial Retrieval",
                            False,
                            f"Admin endpoint failed with status {admin_response.status_code}"
                        )
                
                return tutorials
            else:
                self.log_result(
                    "Practice Tutorial Retrieval",
                    False,
                    f"Failed with status {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_result("Tutorial Retrieval", False, f"Exception: {str(e)}")
            return []
    
    def test_video_file_serving(self, tutorials):
        """Test video file serving and accessibility"""
        try:
            print("🎥 TESTING VIDEO FILE SERVING...")
            
            if not tutorials:
                self.log_result("Video File Serving", False, "No tutorials available to test")
                return
            
            serving_results = []
            
            for tutorial in tutorials[:3]:  # Test first 3 tutorials
                title = tutorial.get('title', 'Unknown')
                video_url = tutorial.get('video_url', '')
                
                if not video_url:
                    self.log_result(
                        f"Video Serving - {title}",
                        False,
                        "No video_url found in tutorial data"
                    )
                    continue
                
                # Construct full URL
                if video_url.startswith('/'):
                    full_url = f"{BACKEND_URL}{video_url}"
                else:
                    full_url = video_url
                
                try:
                    # Test HEAD request first
                    head_response = self.session.head(full_url)
                    
                    if head_response.status_code == 200:
                        content_type = head_response.headers.get('Content-Type', 'Unknown')
                        content_length = head_response.headers.get('Content-Length', 'Unknown')
                        
                        # Test GET request for actual content
                        get_response = self.session.get(full_url, stream=True)
                        
                        if get_response.status_code == 200:
                            # Read first few bytes to verify file integrity
                            first_bytes = next(get_response.iter_content(chunk_size=16), b'')
                            
                            details = f"File accessible. Content-Type: {content_type}, Size: {content_length} bytes"
                            
                            # Check for proper video MIME type
                            if not content_type.startswith('video/'):
                                details += " ⚠️ WARNING: Not a video MIME type!"
                            
                            # Check file signature
                            if first_bytes.startswith(b'\x00\x00\x00'):
                                details += " ✅ Valid file signature"
                            else:
                                details += " ⚠️ Unexpected file signature"
                            
                            self.log_result(f"Video Serving - {title}", True, details)
                            serving_results.append(True)
                            
                            # Test range requests (important for video streaming)
                            range_headers = {"Range": "bytes=0-1023"}
                            range_response = self.session.get(full_url, headers=range_headers)
                            
                            if range_response.status_code == 206:
                                self.log_result(
                                    f"Video Streaming - {title}",
                                    True,
                                    "Partial content requests supported (good for video streaming)"
                                )
                            else:
                                self.log_result(
                                    f"Video Streaming - {title}",
                                    False,
                                    f"Partial content not supported (status: {range_response.status_code})"
                                )
                        else:
                            self.log_result(
                                f"Video Serving - {title}",
                                False,
                                f"GET request failed with status {get_response.status_code}"
                            )
                            serving_results.append(False)
                    else:
                        self.log_result(
                            f"Video Serving - {title}",
                            False,
                            f"HEAD request failed with status {head_response.status_code}, URL: {full_url}"
                        )
                        serving_results.append(False)
                        
                except Exception as e:
                    self.log_result(f"Video Serving - {title}", False, f"Exception: {str(e)}")
                    serving_results.append(False)
            
            # Overall serving assessment
            if serving_results:
                success_rate = sum(serving_results) / len(serving_results) * 100
                if success_rate >= 80:
                    self.log_result(
                        "Overall Video Serving",
                        True,
                        f"Video serving working with {success_rate:.1f}% success rate"
                    )
                else:
                    self.log_result(
                        "Overall Video Serving",
                        False,
                        f"Video serving issues detected. Success rate: {success_rate:.1f}%"
                    )
                    
        except Exception as e:
            self.log_result("Video File Serving", False, f"Exception: {str(e)}")
    
    def test_static_file_infrastructure(self):
        """Test static file serving infrastructure"""
        try:
            print("🏗️ TESTING STATIC FILE INFRASTRUCTURE...")
            
            # Test uploads directory accessibility
            uploads_response = self.session.get(f"{BACKEND_URL}/uploads/")
            
            if uploads_response.status_code in [200, 403]:  # 403 is OK (directory listing disabled)
                self.log_result(
                    "Uploads Directory Access",
                    True,
                    f"Uploads directory accessible (status: {uploads_response.status_code})"
                )
            else:
                self.log_result(
                    "Uploads Directory Access",
                    False,
                    f"Uploads directory not accessible (status: {uploads_response.status_code})"
                )
            
            # Test tutorials subdirectory
            tutorials_response = self.session.get(f"{BACKEND_URL}/uploads/tutorials/")
            
            if tutorials_response.status_code in [200, 403]:
                self.log_result(
                    "Tutorials Directory Access",
                    True,
                    f"Tutorials directory accessible (status: {tutorials_response.status_code})"
                )
            else:
                self.log_result(
                    "Tutorials Directory Access",
                    False,
                    f"Tutorials directory not accessible (status: {tutorials_response.status_code})"
                )
            
            # Test CORS headers
            cors_headers = {
                "Origin": "https://app.dentalaftercarenotes.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Range"
            }
            
            cors_response = self.session.options(f"{BACKEND_URL}/uploads/tutorials/", headers=cors_headers)
            
            cors_origin = cors_response.headers.get('Access-Control-Allow-Origin', 'Not Set')
            
            if cors_origin == "*" or "app.dentalaftercarenotes.com" in cors_origin:
                self.log_result(
                    "CORS Configuration",
                    True,
                    f"CORS properly configured. Origin: {cors_origin}"
                )
            else:
                self.log_result(
                    "CORS Configuration",
                    False,
                    f"CORS may block requests. Origin: {cors_origin}"
                )
                
        except Exception as e:
            self.log_result("Static File Infrastructure", False, f"Exception: {str(e)}")
    
    def test_reverse_proxy_routing(self):
        """Test for reverse proxy routing issues"""
        try:
            print("🔀 TESTING REVERSE PROXY ROUTING...")
            
            # Test if /uploads/* routes are being handled by backend vs frontend
            test_paths = [
                "/uploads/",
                "/uploads/tutorials/",
                "/uploads/tutorials/nonexistent.mp4"
            ]
            
            routing_results = []
            
            for path in test_paths:
                response = self.session.get(f"{BACKEND_URL}{path}")
                content_type = response.headers.get('Content-Type', '')
                
                # Check if we're getting React HTML instead of proper static file response
                is_react_html = (
                    'text/html' in content_type and 
                    ('react' in response.text.lower() or 'root' in response.text.lower())
                )
                
                if is_react_html:
                    routing_results.append(f"{path}: Getting React HTML (ROUTING ISSUE)")
                else:
                    routing_results.append(f"{path}: Proper response (status: {response.status_code})")
            
            if any("ROUTING ISSUE" in result for result in routing_results):
                self.log_result(
                    "Reverse Proxy Routing",
                    False,
                    f"Routing issues detected: {'; '.join(routing_results)}"
                )
            else:
                self.log_result(
                    "Reverse Proxy Routing",
                    True,
                    f"No routing issues detected: {'; '.join(routing_results)}"
                )
                
        except Exception as e:
            self.log_result("Reverse Proxy Routing", False, f"Exception: {str(e)}")
    
    def check_file_system_permissions(self):
        """Check file system permissions and storage"""
        try:
            print("📁 CHECKING FILE SYSTEM PERMISSIONS...")
            
            # This test would ideally be run on the server, but we can infer from API responses
            if self.created_tutorials:
                self.log_result(
                    "File System Permissions",
                    True,
                    f"File uploads working - created {len(self.created_tutorials)} tutorials successfully"
                )
            else:
                self.log_result(
                    "File System Permissions",
                    False,
                    "No successful uploads to verify file system permissions"
                )
                
        except Exception as e:
            self.log_result("File System Permissions", False, f"Exception: {str(e)}")
    
    def cleanup_test_tutorials(self):
        """Clean up test tutorials created during testing"""
        try:
            print("🧹 CLEANING UP TEST TUTORIALS...")
            
            if not self.admin_token or not self.created_tutorials:
                print("   No cleanup needed")
                return
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            cleaned_count = 0
            
            for tutorial_id in self.created_tutorials:
                try:
                    response = self.session.delete(
                        f"{BACKEND_URL}/api/admin/tutorials/{tutorial_id}",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        cleaned_count += 1
                        
                except Exception as e:
                    print(f"   Failed to delete tutorial {tutorial_id}: {e}")
            
            print(f"   Cleaned up {cleaned_count} test tutorials")
            
        except Exception as e:
            print(f"   Cleanup error: {e}")
    
    def run_comprehensive_investigation(self):
        """Run comprehensive video system investigation"""
        print("🚨 URGENT: VIDEO TUTORIAL SYSTEM INVESTIGATION")
        print("=" * 60)
        print("Testing video upload and playback system...")
        print()
        
        # Step 1: Authentication
        admin_auth = self.authenticate_admin()
        practice_auth = self.authenticate_practice()
        
        if not admin_auth:
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Step 2: Test video upload process
        single_upload = self.test_video_upload()
        multiple_uploads = self.test_multiple_video_uploads()
        
        # Step 3: Test tutorial retrieval
        tutorials = self.test_tutorial_retrieval()
        
        # Step 4: Test video file serving
        self.test_video_file_serving(tutorials)
        
        # Step 5: Test infrastructure
        self.test_static_file_infrastructure()
        
        # Step 6: Test for routing issues
        self.test_reverse_proxy_routing()
        
        # Step 7: Check file system
        self.check_file_system_permissions()
        
        # Step 8: Summary and cleanup
        self.print_investigation_summary()
        self.cleanup_test_tutorials()
    
    def print_investigation_summary(self):
        """Print investigation summary"""
        print("\n" + "=" * 60)
        print("🚨 VIDEO SYSTEM INVESTIGATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if "✅ PASS" in result["status"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n🔍 CRITICAL FINDINGS:")
        
        # Analyze for specific issues mentioned in the request
        upload_issues = any("Upload" in r["test"] and "❌ FAIL" in r["status"] for r in self.test_results)
        serving_issues = any("Serving" in r["test"] and "❌ FAIL" in r["status"] for r in self.test_results)
        routing_issues = any("Routing" in r["test"] and "❌ FAIL" in r["status"] for r in self.test_results)
        mime_issues = any("video MIME type" in r["details"] for r in self.test_results)
        cors_issues = any("CORS" in r["test"] and "❌ FAIL" in r["status"] for r in self.test_results)
        
        if upload_issues:
            print("  🚨 VIDEO UPLOAD ISSUES DETECTED - Videos not uploading correctly")
        else:
            print("  ✅ Video upload functionality working")
        
        if serving_issues:
            print("  🚨 VIDEO SERVING ISSUES DETECTED - Videos not accessible")
        else:
            print("  ✅ Video serving functionality working")
        
        if routing_issues:
            print("  🚨 REVERSE PROXY ROUTING ISSUES - Similar to webhook problem")
        else:
            print("  ✅ No reverse proxy routing issues detected")
        
        if mime_issues:
            print("  🚨 MIME TYPE ISSUES - May prevent video playback")
        else:
            print("  ✅ MIME types configured correctly")
        
        if cors_issues:
            print("  🚨 CORS ISSUES - May block video requests from frontend")
        else:
            print("  ✅ CORS configured correctly")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n🎯 RECOMMENDATIONS:")
        
        if upload_issues:
            print("  • Check file upload permissions and directory structure")
            print("  • Verify video file validation and processing")
        
        if serving_issues or routing_issues:
            print("  • Check reverse proxy configuration for /uploads/* paths")
            print("  • Ensure static file serving is routed to backend, not frontend")
        
        if mime_issues:
            print("  • Configure proper MIME types for video files")
            print("  • Check FastAPI StaticFiles configuration")
        
        if not any([upload_issues, serving_issues, routing_issues, mime_issues]):
            print("  • Backend video system appears functional")
            print("  • Issue may be frontend video player or browser compatibility")
            print("  • Check browser console for JavaScript errors")

if __name__ == "__main__":
    tester = VideoSystemTester()
    tester.run_comprehensive_investigation()
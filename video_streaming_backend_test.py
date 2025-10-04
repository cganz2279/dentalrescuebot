#!/usr/bin/env python3
"""
Comprehensive Video Streaming Backend Testing
Testing video playback functionality as requested in urgent review
"""

import requests
import json
import sys
import os
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

class VideoStreamingTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def authenticate_admin(self):
        """Authenticate with admin credentials"""
        print("🔐 Authenticating with admin credentials...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/api/admin/login",
                json={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                
                self.log_test(
                    "Admin Authentication", 
                    True, 
                    f"Admin token obtained successfully"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_admin_headers(self):
        """Get admin authentication headers"""
        return {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
    
    def test_video_api_endpoint_accessibility(self):
        """Test if video API endpoint is accessible without authentication"""
        print("\n🎬 Testing video API endpoint accessibility...")
        
        try:
            # Test with a known video file
            test_filename = "test.mp4"
            response = self.session.get(
                f"{BACKEND_URL}/api/video/tutorial/{test_filename}",
                headers={"User-Agent": "Mozilla/5.0 (compatible; VideoTest/1.0)"}
            )
            
            # Should be accessible without authentication (status 200 or 404 if file doesn't exist)
            accessible = response.status_code in [200, 404, 416]  # 416 for range not satisfiable
            
            self.log_test(
                "Video API Endpoint Accessibility", 
                accessible, 
                f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type', 'N/A')}"
            )
            return accessible
            
        except Exception as e:
            self.log_test("Video API Endpoint Accessibility", False, f"Exception: {str(e)}")
            return False
    
    def test_video_files_exist(self):
        """Test if video files exist in uploads directory"""
        print("\n📁 Testing video file existence...")
        
        try:
            # Get list of video files via admin endpoint
            response = self.session.get(
                f"{BACKEND_URL}/api/video/list",
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                videos = data.get("videos", [])
                
                files_exist = len(videos) > 0
                
                self.log_test(
                    "Video Files Exist", 
                    files_exist, 
                    f"Found {len(videos)} video files: {[v['filename'] for v in videos]}"
                )
                return files_exist, videos
            else:
                self.log_test(
                    "Video Files Exist", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False, []
                
        except Exception as e:
            self.log_test("Video Files Exist", False, f"Exception: {str(e)}")
            return False, []
    
    def test_video_streaming_with_actual_files(self, video_files):
        """Test video streaming with actual video files"""
        print("\n🎥 Testing video streaming with actual files...")
        
        if not video_files:
            self.log_test("Video Streaming Test", False, "No video files available for testing")
            return False
        
        success_count = 0
        total_files = len(video_files)
        
        for video in video_files:
            filename = video['filename']
            expected_size = video['size']
            
            try:
                # Test full file request
                response = self.session.get(
                    f"{BACKEND_URL}/api/video/tutorial/{filename}",
                    headers={"User-Agent": "Mozilla/5.0 (compatible; VideoTest/1.0)"}
                )
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    content_length = response.headers.get('content-length', '0')
                    accept_ranges = response.headers.get('accept-ranges', '')
                    
                    # Verify video MIME type
                    is_video_mime = content_type.startswith('video/')
                    
                    # Verify content length matches expected size
                    size_matches = int(content_length) == expected_size
                    
                    # Verify range support
                    supports_ranges = accept_ranges == 'bytes'
                    
                    file_success = is_video_mime and size_matches and supports_ranges
                    
                    if file_success:
                        success_count += 1
                    
                    self.log_test(
                        f"Video Streaming - {filename}", 
                        file_success, 
                        f"MIME: {content_type}, Size: {content_length}/{expected_size}, Ranges: {accept_ranges}"
                    )
                else:
                    self.log_test(
                        f"Video Streaming - {filename}", 
                        False, 
                        f"Status: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_test(f"Video Streaming - {filename}", False, f"Exception: {str(e)}")
        
        overall_success = success_count == total_files
        self.log_test(
            "Overall Video Streaming", 
            overall_success, 
            f"{success_count}/{total_files} files streamed successfully"
        )
        return overall_success
    
    def test_mime_types_and_headers(self, video_files):
        """Test MIME types and HTTP headers for video files"""
        print("\n📋 Testing MIME types and HTTP headers...")
        
        if not video_files:
            self.log_test("MIME Types and Headers Test", False, "No video files available for testing")
            return False
        
        success_count = 0
        total_files = len(video_files)
        
        for video in video_files:
            filename = video['filename']
            
            try:
                # HEAD request to check headers without downloading content
                response = self.session.head(
                    f"{BACKEND_URL}/api/video/tutorial/{filename}",
                    headers={"User-Agent": "Mozilla/5.0 (compatible; VideoTest/1.0)"}
                )
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    accept_ranges = response.headers.get('accept-ranges', '')
                    cache_control = response.headers.get('cache-control', '')
                    content_length = response.headers.get('content-length', '')
                    
                    # Check required headers
                    has_video_mime = content_type.startswith('video/')
                    has_range_support = accept_ranges == 'bytes'
                    has_cache_control = 'max-age' in cache_control
                    has_content_length = content_length.isdigit()
                    
                    headers_valid = has_video_mime and has_range_support and has_cache_control and has_content_length
                    
                    if headers_valid:
                        success_count += 1
                    
                    self.log_test(
                        f"Headers - {filename}", 
                        headers_valid, 
                        f"MIME: {has_video_mime}, Ranges: {has_range_support}, Cache: {has_cache_control}, Length: {has_content_length}"
                    )
                else:
                    self.log_test(
                        f"Headers - {filename}", 
                        False, 
                        f"Status: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_test(f"Headers - {filename}", False, f"Exception: {str(e)}")
        
        overall_success = success_count == total_files
        self.log_test(
            "Overall MIME Types and Headers", 
            overall_success, 
            f"{success_count}/{total_files} files have correct headers"
        )
        return overall_success
    
    def test_range_request_support(self, video_files):
        """Test Range request support for video streaming"""
        print("\n📊 Testing Range request support...")
        
        if not video_files:
            self.log_test("Range Request Support Test", False, "No video files available for testing")
            return False
        
        # Test with the first available video file
        test_video = video_files[0]
        filename = test_video['filename']
        file_size = test_video['size']
        
        try:
            # Test range request for first 1024 bytes
            range_header = "bytes=0-1023"
            response = self.session.get(
                f"{BACKEND_URL}/api/video/tutorial/{filename}",
                headers={
                    "Range": range_header,
                    "User-Agent": "Mozilla/5.0 (compatible; VideoTest/1.0)"
                }
            )
            
            if response.status_code == 206:  # Partial Content
                content_range = response.headers.get('content-range', '')
                content_length = response.headers.get('content-length', '')
                accept_ranges = response.headers.get('accept-ranges', '')
                
                # Verify partial content response
                has_content_range = content_range.startswith('bytes 0-')
                expected_length = min(1024, file_size)  # Adjust for small files
                has_correct_length = content_length == str(expected_length)
                has_range_support = accept_ranges == 'bytes'
                actual_content_length = len(response.content)
                
                range_success = (has_content_range and has_correct_length and 
                               has_range_support and actual_content_length == expected_length)
                
                self.log_test(
                    "Range Request Support", 
                    range_success, 
                    f"Status: 206, Content-Range: {content_range}, Length: {content_length}, Actual: {actual_content_length}"
                )
                return range_success
            else:
                self.log_test(
                    "Range Request Support", 
                    False, 
                    f"Expected 206, got {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Range Request Support", False, f"Exception: {str(e)}")
            return False
    
    def test_cors_headers(self, video_files):
        """Test CORS headers for video playback"""
        print("\n🌐 Testing CORS headers...")
        
        if not video_files:
            self.log_test("CORS Headers Test", False, "No video files available for testing")
            return False
        
        test_video = video_files[0]
        filename = test_video['filename']
        
        try:
            # Test with Origin header to check CORS
            response = self.session.get(
                f"{BACKEND_URL}/api/video/tutorial/{filename}",
                headers={
                    "Origin": "https://app.dentalaftercarenotes.com",
                    "User-Agent": "Mozilla/5.0 (compatible; VideoTest/1.0)"
                }
            )
            
            if response.status_code == 200:
                access_control_allow_origin = response.headers.get('access-control-allow-origin', '')
                
                # Check if CORS is properly configured
                cors_configured = access_control_allow_origin in ['*', 'https://app.dentalaftercarenotes.com']
                
                self.log_test(
                    "CORS Headers", 
                    cors_configured, 
                    f"Access-Control-Allow-Origin: {access_control_allow_origin}"
                )
                return cors_configured
            else:
                self.log_test(
                    "CORS Headers", 
                    False, 
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("CORS Headers", False, f"Exception: {str(e)}")
            return False
    
    def test_video_url_construction(self):
        """Test video URL construction in frontend components"""
        print("\n🔗 Testing video URL construction...")
        
        try:
            # Get tutorials from admin endpoint
            response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 200:
                tutorials = response.json()
                
                if tutorials:
                    url_construction_valid = True
                    invalid_urls = []
                    
                    for tutorial in tutorials:
                        video_url = tutorial.get('video_url', '')
                        
                        # Check if video_url follows expected pattern
                        if not video_url.startswith('/uploads/tutorials/'):
                            url_construction_valid = False
                            invalid_urls.append(f"Tutorial '{tutorial.get('title', 'Unknown')}': {video_url}")
                    
                    self.log_test(
                        "Video URL Construction", 
                        url_construction_valid, 
                        f"All URLs valid" if url_construction_valid else f"Invalid URLs: {invalid_urls}"
                    )
                    return url_construction_valid
                else:
                    self.log_test(
                        "Video URL Construction", 
                        True, 
                        "No tutorials found, URL construction cannot be tested"
                    )
                    return True
            else:
                self.log_test(
                    "Video URL Construction", 
                    False, 
                    f"Failed to get tutorials: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Video URL Construction", False, f"Exception: {str(e)}")
            return False
    
    def test_video_playback_simulation(self, video_files):
        """Simulate video playback by testing multiple range requests"""
        print("\n🎮 Testing video playback simulation...")
        
        if not video_files:
            self.log_test("Video Playback Simulation", False, "No video files available for testing")
            return False
        
        # Use the largest video file for testing
        test_video = max(video_files, key=lambda x: x['size'])
        filename = test_video['filename']
        file_size = test_video['size']
        
        if file_size < 1024:
            self.log_test("Video Playback Simulation", False, f"File too small for range testing: {file_size} bytes")
            return False
        
        try:
            # Simulate video player behavior with multiple range requests
            chunk_size = min(8192, file_size // 4)  # 8KB chunks or quarter of file
            ranges_to_test = [
                f"bytes=0-{chunk_size-1}",  # Beginning
                f"bytes={file_size//2}-{file_size//2 + chunk_size-1}",  # Middle
                f"bytes={file_size-chunk_size}-{file_size-1}"  # End
            ]
            
            successful_ranges = 0
            
            for range_header in ranges_to_test:
                response = self.session.get(
                    f"{BACKEND_URL}/api/video/tutorial/{filename}",
                    headers={
                        "Range": range_header,
                        "User-Agent": "Mozilla/5.0 (compatible; VideoTest/1.0)"
                    }
                )
                
                if response.status_code == 206:
                    content_range = response.headers.get('content-range', '')
                    actual_length = len(response.content)
                    
                    if content_range and actual_length > 0:
                        successful_ranges += 1
                        print(f"   ✅ Range {range_header}: {content_range}, {actual_length} bytes")
                    else:
                        print(f"   ❌ Range {range_header}: Invalid response")
                else:
                    print(f"   ❌ Range {range_header}: Status {response.status_code}")
            
            playback_success = successful_ranges == len(ranges_to_test)
            
            self.log_test(
                "Video Playback Simulation", 
                playback_success, 
                f"{successful_ranges}/{len(ranges_to_test)} range requests successful"
            )
            return playback_success
            
        except Exception as e:
            self.log_test("Video Playback Simulation", False, f"Exception: {str(e)}")
            return False
    
    def test_backend_logs_for_errors(self):
        """Check backend logs for video-related errors"""
        print("\n📋 Checking backend logs for video errors...")
        
        try:
            # Check supervisor backend logs
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                log_content = result.stdout
                
                # Look for video-related errors
                video_errors = []
                error_keywords = ['video', 'streaming', 'range', 'tutorial', 'uploads']
                
                for line in log_content.split('\n'):
                    if any(keyword in line.lower() for keyword in error_keywords) and ('error' in line.lower() or 'exception' in line.lower()):
                        video_errors.append(line.strip())
                
                no_video_errors = len(video_errors) == 0
                
                self.log_test(
                    "Backend Logs Check", 
                    no_video_errors, 
                    f"No video errors found" if no_video_errors else f"Found {len(video_errors)} video-related errors"
                )
                
                if video_errors:
                    print("   Video-related errors found:")
                    for error in video_errors[-5:]:  # Show last 5 errors
                        print(f"   - {error}")
                
                return no_video_errors
            else:
                self.log_test("Backend Logs Check", False, "Could not read backend logs")
                return False
                
        except Exception as e:
            self.log_test("Backend Logs Check", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all video streaming tests"""
        print("🚀 Starting Video Streaming Functionality Tests")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Cannot proceed with tests.")
            return False
        
        # Test video API endpoint accessibility
        self.test_video_api_endpoint_accessibility()
        
        # Check if video files exist
        files_exist, video_files = self.test_video_files_exist()
        
        if files_exist and video_files:
            # Run tests with actual video files
            self.test_video_streaming_with_actual_files(video_files)
            self.test_mime_types_and_headers(video_files)
            self.test_range_request_support(video_files)
            self.test_cors_headers(video_files)
            self.test_video_playback_simulation(video_files)
        else:
            print("⚠️ No video files found. Skipping file-dependent tests.")
        
        # Test URL construction
        self.test_video_url_construction()
        
        # Check backend logs
        self.test_backend_logs_for_errors()
        
        # Calculate results
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 VIDEO STREAMING TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Video streaming functionality is working correctly.")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed. Review the issues above.")
            return False

def main():
    """Main test execution"""
    tester = VideoStreamingTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
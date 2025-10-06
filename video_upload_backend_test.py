#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Tutorial Video Upload Functionality
Testing the complete video upload workflow as requested in urgent review
"""

import requests
import json
import sys
import os
import tempfile
from datetime import datetime
import hashlib
import subprocess

# Configuration
BACKEND_URL = "https://dentiportal.preview.emergentagent.com"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

class VideoUploadTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.uploaded_files = []  # Track uploaded files for cleanup
        
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
    
    def create_test_video_file(self, filename="test_video.mp4", size_kb=100):
        """Create a small test MP4 file for upload testing"""
        try:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, filename)
            
            # Create a minimal MP4 file using ffmpeg if available, otherwise create dummy binary
            try:
                # Try to create a real MP4 file with ffmpeg
                cmd = [
                    'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1',
                    '-c:v', 'libx264', '-t', '1', '-pix_fmt', 'yuv420p', '-y', file_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and os.path.exists(file_path):
                    print(f"✅ Created real MP4 test file: {file_path} ({os.path.getsize(file_path)} bytes)")
                    return file_path
                else:
                    print(f"⚠️ ffmpeg failed, creating dummy MP4 file")
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print(f"⚠️ ffmpeg not available, creating dummy MP4 file")
            
            # Create a dummy MP4 file with proper MP4 header
            mp4_header = bytes([
                0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70,  # ftyp box
                0x69, 0x73, 0x6F, 0x6D, 0x00, 0x00, 0x02, 0x00,
                0x69, 0x73, 0x6F, 0x6D, 0x69, 0x73, 0x6F, 0x32,
                0x61, 0x76, 0x63, 0x31, 0x6D, 0x70, 0x34, 0x31
            ])
            
            # Pad to desired size
            padding_size = max(0, (size_kb * 1024) - len(mp4_header))
            padding = b'\x00' * padding_size
            
            with open(file_path, 'wb') as f:
                f.write(mp4_header + padding)
            
            print(f"✅ Created dummy MP4 test file: {file_path} ({os.path.getsize(file_path)} bytes)")
            return file_path
            
        except Exception as e:
            print(f"❌ Error creating test video file: {e}")
            return None
    
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
            "Authorization": f"Bearer {self.admin_token}"
        }
    
    def test_get_admin_tutorials(self):
        """Test GET /api/admin/tutorials endpoint"""
        print("\n📚 Testing GET admin tutorials endpoint...")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                tutorial_count = len(data) if isinstance(data, list) else 0
                
                self.log_test(
                    "GET Admin Tutorials", 
                    True, 
                    f"Retrieved {tutorial_count} tutorials successfully"
                )
                return True
            else:
                self.log_test(
                    "GET Admin Tutorials", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("GET Admin Tutorials", False, f"Exception: {str(e)}")
            return False
    
    def test_video_upload_small_file(self):
        """Test POST /api/admin/tutorials with small video file"""
        print("\n🎬 Testing video upload with small file...")
        
        test_file_path = None
        try:
            # Create a small test video file
            test_file_path = self.create_test_video_file("small_test.mp4", size_kb=50)
            if not test_file_path:
                self.log_test("Video Upload Small File", False, "Failed to create test file")
                return False
            
            # Calculate file hash for integrity check
            with open(test_file_path, 'rb') as f:
                original_hash = hashlib.md5(f.read()).hexdigest()
            
            # Upload the file
            with open(test_file_path, 'rb') as f:
                files = {'video': ('small_test.mp4', f, 'video/mp4')}
                data = {
                    'title': 'Test Small Video Upload',
                    'description': 'Testing small video file upload functionality',
                    'category': 'test',
                    'order': 1
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/api/admin/tutorials",
                    files=files,
                    data=data,
                    headers=self.get_admin_headers()
                )
            
            if response.status_code == 200:
                response_data = response.json()
                tutorial_id = response_data.get("tutorial_id")
                
                if tutorial_id:
                    self.uploaded_files.append(tutorial_id)
                
                self.log_test(
                    "Video Upload Small File", 
                    True, 
                    f"Upload successful, Tutorial ID: {tutorial_id}, Original hash: {original_hash[:8]}..."
                )
                
                # Store hash for later integrity check
                self.original_hash = original_hash
                self.uploaded_tutorial_id = tutorial_id
                return True
            else:
                self.log_test(
                    "Video Upload Small File", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Video Upload Small File", False, f"Exception: {str(e)}")
            return False
        finally:
            # Clean up test file
            if test_file_path and os.path.exists(test_file_path):
                try:
                    os.remove(test_file_path)
                    os.rmdir(os.path.dirname(test_file_path))
                except:
                    pass
    
    def test_uploaded_file_integrity(self):
        """Test if uploaded video files maintain integrity"""
        print("\n🔍 Testing uploaded file integrity...")
        
        if not hasattr(self, 'uploaded_tutorial_id'):
            self.log_test("File Integrity Check", False, "No uploaded file to check")
            return False
        
        try:
            # First get the tutorial details to find the video URL
            response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response.status_code != 200:
                self.log_test("File Integrity Check", False, "Failed to get tutorial list")
                return False
            
            tutorials = response.json()
            uploaded_tutorial = None
            
            for tutorial in tutorials:
                if tutorial.get('id') == self.uploaded_tutorial_id:
                    uploaded_tutorial = tutorial
                    break
            
            if not uploaded_tutorial:
                self.log_test("File Integrity Check", False, "Uploaded tutorial not found in list")
                return False
            
            video_url = uploaded_tutorial.get('video_url')
            if not video_url:
                self.log_test("File Integrity Check", False, "No video URL in tutorial record")
                return False
            
            # Check if file exists on disk
            if video_url.startswith('/uploads/tutorials/'):
                filename = os.path.basename(video_url)
                file_path = f"/app/uploads/tutorials/{filename}"
                
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    
                    # Check file hash if we have the original
                    if hasattr(self, 'original_hash'):
                        with open(file_path, 'rb') as f:
                            uploaded_hash = hashlib.md5(f.read()).hexdigest()
                        
                        integrity_ok = uploaded_hash == self.original_hash
                        
                        self.log_test(
                            "File Integrity Check", 
                            integrity_ok, 
                            f"File size: {file_size} bytes, Hash match: {integrity_ok}, Path: {file_path}"
                        )
                        return integrity_ok
                    else:
                        self.log_test(
                            "File Integrity Check", 
                            True, 
                            f"File exists with size: {file_size} bytes, Path: {file_path}"
                        )
                        return True
                else:
                    self.log_test("File Integrity Check", False, f"File not found at: {file_path}")
                    return False
            else:
                self.log_test("File Integrity Check", False, f"Invalid video URL format: {video_url}")
                return False
                
        except Exception as e:
            self.log_test("File Integrity Check", False, f"Exception: {str(e)}")
            return False
    
    def test_video_url_generation(self):
        """Test if video URLs are generated correctly"""
        print("\n🔗 Testing video URL generation...")
        
        try:
            # Get all tutorials to check URL format
            response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response.status_code != 200:
                self.log_test("Video URL Generation", False, "Failed to get tutorials")
                return False
            
            tutorials = response.json()
            
            if not tutorials:
                self.log_test("Video URL Generation", True, "No tutorials to check URLs")
                return True
            
            url_issues = []
            valid_urls = 0
            
            for tutorial in tutorials:
                video_url = tutorial.get('video_url', '')
                tutorial_id = tutorial.get('id', 'unknown')
                
                # Check URL format
                if not video_url:
                    url_issues.append(f"Tutorial {tutorial_id}: Missing video_url")
                elif not video_url.startswith('/uploads/tutorials/'):
                    url_issues.append(f"Tutorial {tutorial_id}: Invalid URL format: {video_url}")
                else:
                    # Check if filename has proper extension
                    filename = os.path.basename(video_url)
                    if not any(filename.lower().endswith(ext) for ext in ['.mp4', '.webm', '.mov', '.avi']):
                        url_issues.append(f"Tutorial {tutorial_id}: Invalid file extension: {filename}")
                    else:
                        valid_urls += 1
            
            success = len(url_issues) == 0
            
            self.log_test(
                "Video URL Generation", 
                success, 
                f"Valid URLs: {valid_urls}, Issues: {url_issues[:3]}" if url_issues else f"All {valid_urls} URLs are valid"
            )
            return success
                
        except Exception as e:
            self.log_test("Video URL Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_video_serving_api(self):
        """Test /api/video/tutorial/{filename} endpoint"""
        print("\n🎥 Testing video serving API...")
        
        try:
            # First get a tutorial with video to test serving
            response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response.status_code != 200:
                self.log_test("Video Serving API", False, "Failed to get tutorials")
                return False
            
            tutorials = response.json()
            
            if not tutorials:
                self.log_test("Video Serving API", True, "No tutorials to test video serving")
                return True
            
            # Find a tutorial with video URL
            test_tutorial = None
            for tutorial in tutorials:
                if tutorial.get('video_url', '').startswith('/uploads/tutorials/'):
                    test_tutorial = tutorial
                    break
            
            if not test_tutorial:
                self.log_test("Video Serving API", False, "No tutorials with valid video URLs found")
                return False
            
            # Extract filename from URL
            video_url = test_tutorial['video_url']
            filename = os.path.basename(video_url)
            
            # Test the video serving endpoint
            video_response = self.session.get(
                f"{BACKEND_URL}/api/video/tutorial/{filename}"
            )
            
            if video_response.status_code == 200:
                content_type = video_response.headers.get('content-type', '')
                content_length = video_response.headers.get('content-length', '0')
                
                # Check if it's a video content type
                is_video = content_type.startswith('video/')
                
                self.log_test(
                    "Video Serving API", 
                    is_video, 
                    f"Status: {video_response.status_code}, Content-Type: {content_type}, Size: {content_length} bytes"
                )
                return is_video
            else:
                self.log_test(
                    "Video Serving API", 
                    False, 
                    f"Status: {video_response.status_code}, Response: {video_response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_test("Video Serving API", False, f"Exception: {str(e)}")
            return False
    
    def test_video_streaming_headers(self):
        """Test if video serving includes proper streaming headers"""
        print("\n📡 Testing video streaming headers...")
        
        try:
            # Get a tutorial to test
            response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response.status_code != 200 or not response.json():
                self.log_test("Video Streaming Headers", True, "No tutorials to test")
                return True
            
            tutorials = response.json()
            test_tutorial = None
            
            for tutorial in tutorials:
                if tutorial.get('video_url', '').startswith('/uploads/tutorials/'):
                    test_tutorial = tutorial
                    break
            
            if not test_tutorial:
                self.log_test("Video Streaming Headers", True, "No valid tutorials to test")
                return True
            
            filename = os.path.basename(test_tutorial['video_url'])
            
            # Test HEAD request for headers
            head_response = self.session.head(
                f"{BACKEND_URL}/api/video/tutorial/{filename}"
            )
            
            if head_response.status_code == 200:
                headers = head_response.headers
                
                # Check for streaming-related headers
                has_accept_ranges = 'accept-ranges' in headers
                has_content_length = 'content-length' in headers
                has_cache_control = 'cache-control' in headers
                
                streaming_ready = has_accept_ranges and has_content_length
                
                self.log_test(
                    "Video Streaming Headers", 
                    streaming_ready, 
                    f"Accept-Ranges: {has_accept_ranges}, Content-Length: {has_content_length}, Cache-Control: {has_cache_control}"
                )
                return streaming_ready
            else:
                self.log_test(
                    "Video Streaming Headers", 
                    False, 
                    f"HEAD request failed: {head_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Video Streaming Headers", False, f"Exception: {str(e)}")
            return False
    
    def test_range_request_support(self):
        """Test if video serving supports HTTP Range requests"""
        print("\n📊 Testing HTTP Range request support...")
        
        try:
            # Get a tutorial to test
            response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response.status_code != 200 or not response.json():
                self.log_test("Range Request Support", True, "No tutorials to test")
                return True
            
            tutorials = response.json()
            test_tutorial = None
            
            for tutorial in tutorials:
                if tutorial.get('video_url', '').startswith('/uploads/tutorials/'):
                    test_tutorial = tutorial
                    break
            
            if not test_tutorial:
                self.log_test("Range Request Support", True, "No valid tutorials to test")
                return True
            
            filename = os.path.basename(test_tutorial['video_url'])
            
            # Test range request
            range_response = self.session.get(
                f"{BACKEND_URL}/api/video/tutorial/{filename}",
                headers={"Range": "bytes=0-1023"}
            )
            
            if range_response.status_code == 206:  # Partial Content
                content_range = range_response.headers.get('content-range', '')
                content_length = range_response.headers.get('content-length', '')
                
                range_working = 'bytes' in content_range and content_length == '1024'
                
                self.log_test(
                    "Range Request Support", 
                    range_working, 
                    f"Status: 206, Content-Range: {content_range}, Content-Length: {content_length}"
                )
                return range_working
            elif range_response.status_code == 200:
                # Server doesn't support ranges but returns full file
                self.log_test(
                    "Range Request Support", 
                    False, 
                    "Server returned full file instead of range (status 200)"
                )
                return False
            else:
                self.log_test(
                    "Range Request Support", 
                    False, 
                    f"Unexpected status: {range_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Range Request Support", False, f"Exception: {str(e)}")
            return False
    
    def test_upload_corruption_detection(self):
        """Test for upload corruption by comparing file sizes and basic integrity"""
        print("\n🔍 Testing upload corruption detection...")
        
        test_file_path = None
        try:
            # Create a test file with known content
            test_file_path = self.create_test_video_file("corruption_test.mp4", size_kb=200)
            if not test_file_path:
                self.log_test("Upload Corruption Detection", False, "Failed to create test file")
                return False
            
            original_size = os.path.getsize(test_file_path)
            
            # Upload the file
            with open(test_file_path, 'rb') as f:
                files = {'video': ('corruption_test.mp4', f, 'video/mp4')}
                data = {
                    'title': 'Corruption Test Video',
                    'description': 'Testing for upload corruption',
                    'category': 'test',
                    'order': 999
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/api/admin/tutorials",
                    files=files,
                    data=data,
                    headers=self.get_admin_headers()
                )
            
            if response.status_code != 200:
                self.log_test("Upload Corruption Detection", False, f"Upload failed: {response.status_code}")
                return False
            
            response_data = response.json()
            tutorial_id = response_data.get("tutorial_id")
            
            if tutorial_id:
                self.uploaded_files.append(tutorial_id)
            
            # Get the uploaded file details
            tutorials_response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if tutorials_response.status_code != 200:
                self.log_test("Upload Corruption Detection", False, "Failed to get tutorial details")
                return False
            
            tutorials = tutorials_response.json()
            uploaded_tutorial = None
            
            for tutorial in tutorials:
                if tutorial.get('id') == tutorial_id:
                    uploaded_tutorial = tutorial
                    break
            
            if not uploaded_tutorial:
                self.log_test("Upload Corruption Detection", False, "Uploaded tutorial not found")
                return False
            
            # Check file on disk
            video_url = uploaded_tutorial.get('video_url', '')
            if video_url.startswith('/uploads/tutorials/'):
                filename = os.path.basename(video_url)
                uploaded_file_path = f"/app/uploads/tutorials/{filename}"
                
                if os.path.exists(uploaded_file_path):
                    uploaded_size = os.path.getsize(uploaded_file_path)
                    size_match = original_size == uploaded_size
                    
                    # Check if file is readable as binary
                    try:
                        with open(uploaded_file_path, 'rb') as f:
                            first_bytes = f.read(32)  # Read first 32 bytes
                        readable = len(first_bytes) > 0
                    except:
                        readable = False
                    
                    corruption_detected = not (size_match and readable)
                    
                    self.log_test(
                        "Upload Corruption Detection", 
                        not corruption_detected, 
                        f"Original: {original_size} bytes, Uploaded: {uploaded_size} bytes, Size match: {size_match}, Readable: {readable}"
                    )
                    return not corruption_detected
                else:
                    self.log_test("Upload Corruption Detection", False, f"Uploaded file not found: {uploaded_file_path}")
                    return False
            else:
                self.log_test("Upload Corruption Detection", False, f"Invalid video URL: {video_url}")
                return False
                
        except Exception as e:
            self.log_test("Upload Corruption Detection", False, f"Exception: {str(e)}")
            return False
        finally:
            # Clean up test file
            if test_file_path and os.path.exists(test_file_path):
                try:
                    os.remove(test_file_path)
                    os.rmdir(os.path.dirname(test_file_path))
                except:
                    pass
    
    def test_mime_type_validation(self):
        """Test MIME type validation for uploaded files"""
        print("\n📋 Testing MIME type validation...")
        
        test_file_path = None
        try:
            # Create a non-video file (text file with .mp4 extension)
            temp_dir = tempfile.mkdtemp()
            test_file_path = os.path.join(temp_dir, "fake_video.mp4")
            
            with open(test_file_path, 'w') as f:
                f.write("This is not a video file, just text content.")
            
            # Try to upload the fake video file
            with open(test_file_path, 'rb') as f:
                files = {'video': ('fake_video.mp4', f, 'text/plain')}  # Wrong MIME type
                data = {
                    'title': 'Fake Video Test',
                    'description': 'Testing MIME type validation',
                    'category': 'test',
                    'order': 998
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/api/admin/tutorials",
                    files=files,
                    data=data,
                    headers=self.get_admin_headers()
                )
            
            # Should reject non-video files
            validation_working = response.status_code == 400
            
            self.log_test(
                "MIME Type Validation", 
                validation_working, 
                f"Status: {response.status_code}, Response: {response.text[:100]}"
            )
            return validation_working
                
        except Exception as e:
            self.log_test("MIME Type Validation", False, f"Exception: {str(e)}")
            return False
        finally:
            # Clean up test file
            if test_file_path and os.path.exists(test_file_path):
                try:
                    os.remove(test_file_path)
                    os.rmdir(os.path.dirname(test_file_path))
                except:
                    pass
    
    def cleanup_uploaded_files(self):
        """Clean up uploaded test files"""
        print("\n🧹 Cleaning up uploaded test files...")
        
        cleanup_count = 0
        for tutorial_id in self.uploaded_files:
            try:
                response = self.session.delete(
                    f"{BACKEND_URL}/api/admin/tutorials/{tutorial_id}",
                    headers=self.get_admin_headers()
                )
                
                if response.status_code == 200:
                    cleanup_count += 1
                    print(f"   ✅ Deleted tutorial: {tutorial_id}")
                else:
                    print(f"   ⚠️ Failed to delete tutorial: {tutorial_id} (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ Error deleting tutorial {tutorial_id}: {e}")
        
        print(f"🧹 Cleaned up {cleanup_count}/{len(self.uploaded_files)} uploaded files")
    
    def run_all_tests(self):
        """Run all video upload tests"""
        print("🚀 Starting Tutorial Video Upload Functionality Tests")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all tests
        tests = [
            self.test_get_admin_tutorials,
            self.test_video_upload_small_file,
            self.test_uploaded_file_integrity,
            self.test_video_url_generation,
            self.test_video_serving_api,
            self.test_video_streaming_headers,
            self.test_range_request_support,
            self.test_upload_corruption_detection,
            self.test_mime_type_validation
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
        
        # Clean up uploaded files
        if self.uploaded_files:
            self.cleanup_uploaded_files()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 VIDEO UPLOAD TEST SUMMARY")
        print("=" * 70)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Video upload functionality is working correctly.")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed. Review the issues above.")
            return False

def main():
    """Main test execution"""
    tester = VideoUploadTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
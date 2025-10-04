#!/usr/bin/env python3
"""
Real Video Upload Test - Testing with actual MP4 files
"""

import requests
import json
import sys
import os
import tempfile
from datetime import datetime
import hashlib

# Configuration
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

class RealVideoUploadTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.uploaded_files = []
        
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
            "Authorization": f"Bearer {self.admin_token}"
        }
    
    def create_real_mp4_file(self, filename="real_test.mp4"):
        """Create a small but valid MP4 file"""
        try:
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, filename)
            
            # Create a minimal but valid MP4 file structure
            # This is a very basic MP4 with proper boxes
            mp4_data = bytearray()
            
            # ftyp box (file type)
            ftyp_box = b'\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2avc1mp41'
            mp4_data.extend(ftyp_box)
            
            # mdat box (media data) - minimal
            mdat_size = 1024  # 1KB of dummy data
            mdat_header = b'\x00\x00\x04\x08mdat'  # size (1032 bytes) + 'mdat'
            mdat_data = b'\x00' * (mdat_size - 8)  # dummy video data
            mp4_data.extend(mdat_header + mdat_data)
            
            # Write to file
            with open(file_path, 'wb') as f:
                f.write(mp4_data)
            
            print(f"✅ Created real MP4 test file: {file_path} ({len(mp4_data)} bytes)")
            return file_path
            
        except Exception as e:
            print(f"❌ Error creating real MP4 file: {e}")
            return None
    
    def test_real_mp4_upload(self):
        """Test uploading a real MP4 file"""
        print("\n🎬 Testing real MP4 file upload...")
        
        test_file_path = None
        try:
            # Create a real MP4 file
            test_file_path = self.create_real_mp4_file("real_upload_test.mp4")
            if not test_file_path:
                self.log_test("Real MP4 Upload", False, "Failed to create real MP4 file")
                return False
            
            original_size = os.path.getsize(test_file_path)
            
            # Calculate file hash
            with open(test_file_path, 'rb') as f:
                original_hash = hashlib.md5(f.read()).hexdigest()
            
            # Upload the file
            with open(test_file_path, 'rb') as f:
                files = {'video': ('real_upload_test.mp4', f, 'video/mp4')}
                data = {
                    'title': 'Real MP4 Upload Test',
                    'description': 'Testing with a real MP4 file structure',
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
                
                # Verify the uploaded file
                success = self.verify_uploaded_file(tutorial_id, original_size, original_hash)
                
                self.log_test(
                    "Real MP4 Upload", 
                    success, 
                    f"Upload successful, Tutorial ID: {tutorial_id}, Size: {original_size} bytes, Verification: {success}"
                )
                return success
            else:
                self.log_test(
                    "Real MP4 Upload", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Real MP4 Upload", False, f"Exception: {str(e)}")
            return False
        finally:
            # Clean up test file
            if test_file_path and os.path.exists(test_file_path):
                try:
                    os.remove(test_file_path)
                    os.rmdir(os.path.dirname(test_file_path))
                except:
                    pass
    
    def verify_uploaded_file(self, tutorial_id, expected_size, expected_hash):
        """Verify the uploaded file integrity"""
        try:
            # Get tutorial details
            response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response.status_code != 200:
                return False
            
            tutorials = response.json()
            tutorial = None
            
            for t in tutorials:
                if t.get('id') == tutorial_id:
                    tutorial = t
                    break
            
            if not tutorial:
                return False
            
            video_url = tutorial.get('video_url', '')
            if not video_url.startswith('/uploads/tutorials/'):
                return False
            
            # Check file on disk
            filename = os.path.basename(video_url)
            file_path = f"/app/uploads/tutorials/{filename}"
            
            if not os.path.exists(file_path):
                print(f"   ❌ File not found: {file_path}")
                return False
            
            actual_size = os.path.getsize(file_path)
            
            # Check hash
            with open(file_path, 'rb') as f:
                actual_hash = hashlib.md5(f.read()).hexdigest()
            
            size_match = actual_size == expected_size
            hash_match = actual_hash == expected_hash
            
            print(f"   📊 Size: Expected {expected_size}, Got {actual_size}, Match: {size_match}")
            print(f"   🔍 Hash: Expected {expected_hash[:8]}..., Got {actual_hash[:8]}..., Match: {hash_match}")
            
            return size_match and hash_match
            
        except Exception as e:
            print(f"   ❌ Verification error: {e}")
            return False
    
    def test_video_playback_headers(self):
        """Test if uploaded videos have proper headers for playback"""
        print("\n🎥 Testing video playback headers...")
        
        try:
            # Get all tutorials
            response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response.status_code != 200:
                self.log_test("Video Playback Headers", False, "Failed to get tutorials")
                return False
            
            tutorials = response.json()
            
            if not tutorials:
                self.log_test("Video Playback Headers", True, "No tutorials to test")
                return True
            
            # Test the first tutorial with a video
            test_tutorial = None
            for tutorial in tutorials:
                if tutorial.get('video_url', '').startswith('/uploads/tutorials/'):
                    test_tutorial = tutorial
                    break
            
            if not test_tutorial:
                self.log_test("Video Playback Headers", True, "No tutorials with videos")
                return True
            
            filename = os.path.basename(test_tutorial['video_url'])
            
            # Test video serving endpoint
            video_response = self.session.get(
                f"{BACKEND_URL}/api/video/tutorial/{filename}"
            )
            
            if video_response.status_code == 200:
                headers = video_response.headers
                content_type = headers.get('content-type', '')
                accept_ranges = headers.get('accept-ranges', '')
                cache_control = headers.get('cache-control', '')
                content_length = headers.get('content-length', '')
                
                # Check for video-friendly headers
                has_video_type = content_type.startswith('video/')
                has_ranges = 'bytes' in accept_ranges
                has_cache = 'public' in cache_control
                has_length = content_length.isdigit() if content_length else False
                
                playback_ready = has_video_type and has_ranges and has_length
                
                self.log_test(
                    "Video Playback Headers", 
                    playback_ready, 
                    f"Content-Type: {content_type}, Accept-Ranges: {accept_ranges}, Cache: {cache_control}, Length: {content_length}"
                )
                return playback_ready
            else:
                self.log_test(
                    "Video Playback Headers", 
                    False, 
                    f"Video serving failed: {video_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Video Playback Headers", False, f"Exception: {str(e)}")
            return False
    
    def test_existing_uploaded_files(self):
        """Test existing uploaded files in the system"""
        print("\n📁 Testing existing uploaded files...")
        
        try:
            # Check files in uploads directory
            uploads_dir = "/app/uploads/tutorials"
            if not os.path.exists(uploads_dir):
                self.log_test("Existing Uploaded Files", False, "Uploads directory not found")
                return False
            
            files = os.listdir(uploads_dir)
            video_files = [f for f in files if f.lower().endswith(('.mp4', '.webm', '.mov', '.avi'))]
            
            if not video_files:
                self.log_test("Existing Uploaded Files", True, "No existing video files to test")
                return True
            
            issues = []
            valid_files = 0
            
            for filename in video_files:
                file_path = os.path.join(uploads_dir, filename)
                file_size = os.path.getsize(file_path)
                
                # Check if file is suspiciously small (likely corrupted)
                if file_size < 1000:  # Less than 1KB is suspicious for video
                    issues.append(f"{filename}: Very small size ({file_size} bytes)")
                else:
                    valid_files += 1
                
                # Test if file can be served
                try:
                    serve_response = self.session.head(f"{BACKEND_URL}/api/video/tutorial/{filename}")
                    if serve_response.status_code != 200:
                        issues.append(f"{filename}: Cannot be served (status {serve_response.status_code})")
                except:
                    issues.append(f"{filename}: Serving test failed")
            
            success = len(issues) == 0
            
            self.log_test(
                "Existing Uploaded Files", 
                success, 
                f"Total files: {len(video_files)}, Valid: {valid_files}, Issues: {issues[:3]}" if issues else f"All {len(video_files)} files are valid"
            )
            return success
                
        except Exception as e:
            self.log_test("Existing Uploaded Files", False, f"Exception: {str(e)}")
            return False
    
    def test_database_video_urls(self):
        """Test if database records have correct video URLs"""
        print("\n🗄️ Testing database video URL records...")
        
        try:
            # Get all tutorials from database
            response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response.status_code != 200:
                self.log_test("Database Video URLs", False, "Failed to get tutorials from database")
                return False
            
            tutorials = response.json()
            
            if not tutorials:
                self.log_test("Database Video URLs", True, "No tutorials in database")
                return True
            
            url_issues = []
            valid_urls = 0
            
            for tutorial in tutorials:
                tutorial_id = tutorial.get('id', 'unknown')
                video_url = tutorial.get('video_url', '')
                title = tutorial.get('title', 'Untitled')
                
                if not video_url:
                    url_issues.append(f"Tutorial '{title}' ({tutorial_id}): Missing video_url")
                    continue
                
                if not video_url.startswith('/uploads/tutorials/'):
                    url_issues.append(f"Tutorial '{title}': Invalid URL format: {video_url}")
                    continue
                
                # Check if file exists
                filename = os.path.basename(video_url)
                file_path = f"/app/uploads/tutorials/{filename}"
                
                if not os.path.exists(file_path):
                    url_issues.append(f"Tutorial '{title}': File not found: {filename}")
                    continue
                
                valid_urls += 1
            
            success = len(url_issues) == 0
            
            self.log_test(
                "Database Video URLs", 
                success, 
                f"Total tutorials: {len(tutorials)}, Valid URLs: {valid_urls}, Issues: {url_issues[:3]}" if url_issues else f"All {len(tutorials)} URLs are valid"
            )
            return success
                
        except Exception as e:
            self.log_test("Database Video URLs", False, f"Exception: {str(e)}")
            return False
    
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
        """Run all real video upload tests"""
        print("🚀 Starting Real Video Upload Tests")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all tests
        tests = [
            self.test_existing_uploaded_files,
            self.test_database_video_urls,
            self.test_real_mp4_upload,
            self.test_video_playback_headers
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
        print("\n" + "=" * 60)
        print("📊 REAL VIDEO UPLOAD TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Real video upload functionality is working correctly.")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed. Review the issues above.")
            return False

def main():
    """Main test execution"""
    tester = RealVideoUploadTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
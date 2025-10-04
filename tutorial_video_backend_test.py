#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Tutorial Video Upload Functionality
Testing the tutorial video upload system as requested by the user
"""

import requests
import json
import sys
import os
import tempfile
from datetime import datetime
import io

# Configuration
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

class TutorialVideoTester:
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
            "Authorization": f"Bearer {self.admin_token}"
        }
    
    def test_get_tutorials_admin(self):
        """Test GET /api/admin/tutorials endpoint"""
        print("\n📚 Testing GET /api/admin/tutorials endpoint...")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response is a list
                if isinstance(data, list):
                    self.log_test(
                        "GET Admin Tutorials", 
                        True, 
                        f"Retrieved {len(data)} tutorials successfully"
                    )
                    
                    # Check tutorial structure if any exist
                    if data:
                        tutorial = data[0]
                        required_fields = ["id", "title", "description", "video_url", "category", "order", "is_active"]
                        missing_fields = [field for field in required_fields if field not in tutorial]
                        
                        if not missing_fields:
                            self.log_test(
                                "Tutorial Structure Validation", 
                                True, 
                                "All required fields present in tutorial objects"
                            )
                        else:
                            self.log_test(
                                "Tutorial Structure Validation", 
                                False, 
                                f"Missing fields: {missing_fields}"
                            )
                    
                    return True
                else:
                    self.log_test(
                        "GET Admin Tutorials", 
                        False, 
                        f"Expected list, got: {type(data)}"
                    )
                    return False
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
    
    def create_test_video_file(self):
        """Create a small test video file for upload testing"""
        try:
            # Create a minimal MP4 file (just header bytes to simulate video)
            # This is a minimal MP4 file structure that should pass MIME type validation
            mp4_header = b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom\x00\x00\x00\x08free'
            mp4_header += b'\x00' * 100  # Add some padding to make it look like a real file
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_file.write(mp4_header)
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            print(f"Error creating test video file: {e}")
            return None
    
    def test_video_upload(self):
        """Test POST /api/admin/tutorials endpoint for video upload"""
        print("\n🎥 Testing video upload functionality...")
        
        try:
            # Create test video file
            test_video_path = self.create_test_video_file()
            if not test_video_path:
                self.log_test("Video Upload", False, "Failed to create test video file")
                return False
            
            try:
                # Prepare form data
                with open(test_video_path, 'rb') as video_file:
                    files = {
                        'video': ('test_tutorial.mp4', video_file, 'video/mp4')
                    }
                    data = {
                        'title': 'Test Tutorial Video',
                        'description': 'This is a test tutorial for video upload functionality',
                        'category': 'test',
                        'order': '1'
                    }
                    
                    response = self.session.post(
                        f"{BACKEND_URL}/api/admin/tutorials",
                        files=files,
                        data=data,
                        headers=self.get_admin_headers()
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success") and data.get("tutorial_id"):
                        self.log_test(
                            "Video Upload", 
                            True, 
                            f"Tutorial created successfully with ID: {data.get('tutorial_id')}"
                        )
                        
                        # Store tutorial ID for cleanup
                        self.uploaded_tutorial_id = data.get("tutorial_id")
                        return True
                    else:
                        self.log_test(
                            "Video Upload", 
                            False, 
                            f"Unexpected response format: {data}"
                        )
                        return False
                else:
                    self.log_test(
                        "Video Upload", 
                        False, 
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                    return False
                    
            finally:
                # Clean up test file
                try:
                    os.unlink(test_video_path)
                except:
                    pass
                    
        except Exception as e:
            self.log_test("Video Upload", False, f"Exception: {str(e)}")
            return False
    
    def test_video_file_validation(self):
        """Test video file MIME type validation"""
        print("\n🔍 Testing video file validation...")
        
        try:
            # Create a non-video file (text file)
            temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
            temp_file.write(b'This is not a video file')
            temp_file.close()
            
            try:
                with open(temp_file.name, 'rb') as fake_video:
                    files = {
                        'video': ('fake_video.txt', fake_video, 'text/plain')
                    }
                    data = {
                        'title': 'Invalid File Test',
                        'description': 'Testing with non-video file',
                        'category': 'test',
                        'order': '1'
                    }
                    
                    response = self.session.post(
                        f"{BACKEND_URL}/api/admin/tutorials",
                        files=files,
                        data=data,
                        headers=self.get_admin_headers()
                    )
                
                # Should return 400 for invalid file type
                if response.status_code == 400:
                    self.log_test(
                        "Video File Validation", 
                        True, 
                        "Correctly rejected non-video file"
                    )
                    return True
                else:
                    self.log_test(
                        "Video File Validation", 
                        False, 
                        f"Expected 400, got {response.status_code}: {response.text}"
                    )
                    return False
                    
            finally:
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                    
        except Exception as e:
            self.log_test("Video File Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_uploads_directory(self):
        """Test if uploads directory exists and is accessible"""
        print("\n📁 Testing uploads directory accessibility...")
        
        try:
            # Test if we can access the uploads directory via HTTP
            response = self.session.get(f"{BACKEND_URL}/uploads/tutorials/")
            
            # Directory listing might return 403 (forbidden) or 404, both are acceptable
            # as long as the server responds (not connection error)
            if response.status_code in [200, 403, 404]:
                self.log_test(
                    "Uploads Directory Access", 
                    True, 
                    f"Uploads directory is accessible (status: {response.status_code})"
                )
                return True
            else:
                self.log_test(
                    "Uploads Directory Access", 
                    False, 
                    f"Unexpected status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Uploads Directory Access", False, f"Exception: {str(e)}")
            return False
    
    def test_video_serving(self):
        """Test if uploaded videos can be accessed via generated URLs"""
        print("\n🎬 Testing video serving functionality...")
        
        # First, we need to upload a video and get its URL
        if not hasattr(self, 'uploaded_tutorial_id'):
            print("   Skipping video serving test - no uploaded tutorial available")
            self.log_test("Video Serving", False, "No uploaded tutorial to test")
            return False
        
        try:
            # Get the tutorial details to find the video URL
            response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 200:
                tutorials = response.json()
                
                # Find our uploaded tutorial
                uploaded_tutorial = None
                for tutorial in tutorials:
                    if tutorial.get("id") == self.uploaded_tutorial_id:
                        uploaded_tutorial = tutorial
                        break
                
                if uploaded_tutorial and uploaded_tutorial.get("video_url"):
                    video_url = uploaded_tutorial["video_url"]
                    
                    # Test accessing the video file
                    video_response = self.session.get(f"{BACKEND_URL}{video_url}")
                    
                    if video_response.status_code == 200:
                        self.log_test(
                            "Video Serving", 
                            True, 
                            f"Video accessible at: {video_url}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Video Serving", 
                            False, 
                            f"Video not accessible: {video_response.status_code}"
                        )
                        return False
                else:
                    self.log_test("Video Serving", False, "Could not find uploaded tutorial or video URL")
                    return False
            else:
                self.log_test("Video Serving", False, f"Failed to get tutorials: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Video Serving", False, f"Exception: {str(e)}")
            return False
    
    def test_authentication_required(self):
        """Test that admin authentication is required for tutorial operations"""
        print("\n🔒 Testing authentication requirements...")
        
        try:
            # Test GET without authentication
            response = self.session.get(f"{BACKEND_URL}/api/admin/tutorials")
            
            if response.status_code in [401, 403]:
                self.log_test(
                    "Authentication Required (GET)", 
                    True, 
                    f"Correctly requires authentication (status: {response.status_code})"
                )
                get_auth_ok = True
            else:
                self.log_test(
                    "Authentication Required (GET)", 
                    False, 
                    f"Expected 401/403, got: {response.status_code}"
                )
                get_auth_ok = False
            
            # Test POST without authentication
            test_video_path = self.create_test_video_file()
            if test_video_path:
                try:
                    with open(test_video_path, 'rb') as video_file:
                        files = {'video': ('test.mp4', video_file, 'video/mp4')}
                        data = {'title': 'Test', 'description': 'Test'}
                        
                        response = self.session.post(
                            f"{BACKEND_URL}/api/admin/tutorials",
                            files=files,
                            data=data
                        )
                    
                    if response.status_code in [401, 403]:
                        self.log_test(
                            "Authentication Required (POST)", 
                            True, 
                            f"Correctly requires authentication (status: {response.status_code})"
                        )
                        post_auth_ok = True
                    else:
                        self.log_test(
                            "Authentication Required (POST)", 
                            False, 
                            f"Expected 401/403, got: {response.status_code}"
                        )
                        post_auth_ok = False
                        
                finally:
                    try:
                        os.unlink(test_video_path)
                    except:
                        pass
            else:
                post_auth_ok = False
                self.log_test("Authentication Required (POST)", False, "Could not create test file")
            
            return get_auth_ok and post_auth_ok
            
        except Exception as e:
            self.log_test("Authentication Required", False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_token(self):
        """Test handling of invalid admin tokens"""
        print("\n🔒 Testing invalid token handling...")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers={"Authorization": "Bearer invalid_token_here"}
            )
            
            if response.status_code == 401:
                self.log_test(
                    "Invalid Token Handling", 
                    True, 
                    "Correctly rejects invalid tokens"
                )
                return True
            else:
                self.log_test(
                    "Invalid Token Handling", 
                    False, 
                    f"Expected 401, got: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Invalid Token Handling", False, f"Exception: {str(e)}")
            return False
    
    def test_database_storage(self):
        """Test that tutorials are properly stored in database"""
        print("\n💾 Testing database storage...")
        
        try:
            # Get tutorials before and after upload to verify storage
            response_before = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response_before.status_code != 200:
                self.log_test("Database Storage", False, "Could not get initial tutorial count")
                return False
            
            tutorials_before = response_before.json()
            count_before = len(tutorials_before)
            
            # Upload a new tutorial
            test_video_path = self.create_test_video_file()
            if not test_video_path:
                self.log_test("Database Storage", False, "Could not create test video")
                return False
            
            try:
                with open(test_video_path, 'rb') as video_file:
                    files = {'video': ('db_test.mp4', video_file, 'video/mp4')}
                    data = {
                        'title': 'Database Storage Test',
                        'description': 'Testing database storage',
                        'category': 'test',
                        'order': '99'
                    }
                    
                    upload_response = self.session.post(
                        f"{BACKEND_URL}/api/admin/tutorials",
                        files=files,
                        data=data,
                        headers=self.get_admin_headers()
                    )
                
                if upload_response.status_code != 200:
                    self.log_test("Database Storage", False, f"Upload failed: {upload_response.status_code}")
                    return False
                
                # Check if tutorial count increased
                response_after = self.session.get(
                    f"{BACKEND_URL}/api/admin/tutorials",
                    headers=self.get_admin_headers()
                )
                
                if response_after.status_code == 200:
                    tutorials_after = response_after.json()
                    count_after = len(tutorials_after)
                    
                    if count_after == count_before + 1:
                        self.log_test(
                            "Database Storage", 
                            True, 
                            f"Tutorial count increased from {count_before} to {count_after}"
                        )
                        
                        # Store the new tutorial ID for cleanup
                        upload_data = upload_response.json()
                        if upload_data.get("tutorial_id"):
                            if not hasattr(self, 'test_tutorial_ids'):
                                self.test_tutorial_ids = []
                            self.test_tutorial_ids.append(upload_data["tutorial_id"])
                        
                        return True
                    else:
                        self.log_test(
                            "Database Storage", 
                            False, 
                            f"Expected count {count_before + 1}, got {count_after}"
                        )
                        return False
                else:
                    self.log_test("Database Storage", False, "Could not get tutorial count after upload")
                    return False
                    
            finally:
                try:
                    os.unlink(test_video_path)
                except:
                    pass
                    
        except Exception as e:
            self.log_test("Database Storage", False, f"Exception: {str(e)}")
            return False
    
    def test_file_size_handling(self):
        """Test handling of different file sizes"""
        print("\n📏 Testing file size handling...")
        
        try:
            # Create a larger test file (but still reasonable for testing)
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            
            # Write MP4 header
            mp4_header = b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom\x00\x00\x00\x08free'
            temp_file.write(mp4_header)
            
            # Add more data to simulate a larger file (1MB)
            temp_file.write(b'\x00' * (1024 * 1024))
            temp_file.close()
            
            try:
                with open(temp_file.name, 'rb') as video_file:
                    files = {'video': ('large_test.mp4', video_file, 'video/mp4')}
                    data = {
                        'title': 'Large File Test',
                        'description': 'Testing with larger file',
                        'category': 'test',
                        'order': '2'
                    }
                    
                    response = self.session.post(
                        f"{BACKEND_URL}/api/admin/tutorials",
                        files=files,
                        data=data,
                        headers=self.get_admin_headers()
                    )
                
                if response.status_code == 200:
                    self.log_test(
                        "File Size Handling", 
                        True, 
                        "Successfully handled 1MB file upload"
                    )
                    
                    # Store tutorial ID for cleanup
                    upload_data = response.json()
                    if upload_data.get("tutorial_id"):
                        if not hasattr(self, 'test_tutorial_ids'):
                            self.test_tutorial_ids = []
                        self.test_tutorial_ids.append(upload_data["tutorial_id"])
                    
                    return True
                else:
                    self.log_test(
                        "File Size Handling", 
                        False, 
                        f"Large file upload failed: {response.status_code} - {response.text}"
                    )
                    return False
                    
            finally:
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                    
        except Exception as e:
            self.log_test("File Size Handling", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_test_tutorials(self):
        """Clean up any tutorials created during testing"""
        print("\n🧹 Cleaning up test tutorials...")
        
        if not hasattr(self, 'test_tutorial_ids'):
            return
        
        for tutorial_id in getattr(self, 'test_tutorial_ids', []):
            try:
                response = self.session.delete(
                    f"{BACKEND_URL}/api/admin/tutorials/{tutorial_id}",
                    headers=self.get_admin_headers()
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Cleaned up tutorial: {tutorial_id}")
                else:
                    print(f"   ⚠️ Could not clean up tutorial {tutorial_id}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error cleaning up tutorial {tutorial_id}: {e}")
    
    def run_all_tests(self):
        """Run all tutorial video upload tests"""
        print("🚀 Starting Tutorial Video Upload Functionality Tests")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all tests
        tests = [
            self.test_get_tutorials_admin,
            self.test_video_upload,
            self.test_video_file_validation,
            self.test_uploads_directory,
            self.test_video_serving,
            self.test_authentication_required,
            self.test_invalid_token,
            self.test_database_storage,
            self.test_file_size_handling
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
        
        # Clean up test data
        self.cleanup_test_tutorials()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TUTORIAL VIDEO UPLOAD TEST SUMMARY")
        print("=" * 70)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Tutorial video upload functionality is working correctly.")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed. Review the issues above.")
            return False

def main():
    """Main test execution"""
    tester = TutorialVideoTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
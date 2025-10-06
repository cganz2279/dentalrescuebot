#!/usr/bin/env python3
"""
Upload Corruption Investigation Test
Testing to identify why uploaded MP4 files are corrupted
"""

import requests
import json
import sys
import os
import tempfile
from datetime import datetime
import hashlib

# Configuration
BACKEND_URL = "https://dentiportal.preview.emergentagent.com"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

class UploadCorruptionTester:
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
    
    def create_sample_mp4_with_content(self, filename="sample.mp4", size_kb=500):
        """Create a sample MP4 file with actual content"""
        try:
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, filename)
            
            # Create a more substantial MP4 file with proper structure
            mp4_data = bytearray()
            
            # ftyp box (file type) - 32 bytes
            ftyp_box = b'\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2avc1mp41'
            mp4_data.extend(ftyp_box)
            
            # moov box (movie metadata) - minimal structure
            moov_size = 200
            moov_header = (moov_size).to_bytes(4, 'big') + b'moov'
            moov_data = b'\x00' * (moov_size - 8)
            mp4_data.extend(moov_header + moov_data)
            
            # mdat box (media data) - bulk of the file
            target_size = size_kb * 1024
            current_size = len(mp4_data)
            mdat_data_size = target_size - current_size - 8  # 8 bytes for mdat header
            
            if mdat_data_size > 0:
                mdat_header = (mdat_data_size + 8).to_bytes(4, 'big') + b'mdat'
                # Create some varied content instead of all zeros
                mdat_content = bytearray()
                for i in range(mdat_data_size):
                    mdat_content.append(i % 256)
                
                mp4_data.extend(mdat_header + mdat_content)
            
            # Write to file
            with open(file_path, 'wb') as f:
                f.write(mp4_data)
            
            print(f"✅ Created sample MP4: {file_path} ({len(mp4_data)} bytes)")
            return file_path
            
        except Exception as e:
            print(f"❌ Error creating sample MP4: {e}")
            return None
    
    def test_upload_with_different_sizes(self):
        """Test upload with different file sizes to identify size-related corruption"""
        print("\n📏 Testing upload with different file sizes...")
        
        sizes_to_test = [1, 10, 50, 100, 500]  # KB
        results = []
        
        for size_kb in sizes_to_test:
            test_file_path = None
            try:
                # Create test file
                test_file_path = self.create_sample_mp4_with_content(f"size_test_{size_kb}kb.mp4", size_kb)
                if not test_file_path:
                    results.append(f"{size_kb}KB: Failed to create")
                    continue
                
                original_size = os.path.getsize(test_file_path)
                
                # Calculate hash
                with open(test_file_path, 'rb') as f:
                    original_hash = hashlib.md5(f.read()).hexdigest()
                
                # Upload the file
                with open(test_file_path, 'rb') as f:
                    files = {'video': (f'size_test_{size_kb}kb.mp4', f, 'video/mp4')}
                    data = {
                        'title': f'Size Test {size_kb}KB',
                        'description': f'Testing upload with {size_kb}KB file',
                        'category': 'test',
                        'order': size_kb
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
                    
                    # Check uploaded file
                    corruption_detected = self.check_file_corruption(tutorial_id, original_size, original_hash)
                    
                    if corruption_detected:
                        results.append(f"{size_kb}KB: CORRUPTED")
                    else:
                        results.append(f"{size_kb}KB: OK")
                else:
                    results.append(f"{size_kb}KB: Upload failed ({response.status_code})")
                    
            except Exception as e:
                results.append(f"{size_kb}KB: Exception ({str(e)})")
            finally:
                # Clean up test file
                if test_file_path and os.path.exists(test_file_path):
                    try:
                        os.remove(test_file_path)
                        os.rmdir(os.path.dirname(test_file_path))
                    except:
                        pass
        
        # Analyze results
        corrupted_count = sum(1 for r in results if "CORRUPTED" in r)
        success = corrupted_count == 0
        
        self.log_test(
            "Upload Different Sizes", 
            success, 
            f"Results: {results}, Corrupted: {corrupted_count}/{len(sizes_to_test)}"
        )
        return success
    
    def check_file_corruption(self, tutorial_id, expected_size, expected_hash):
        """Check if uploaded file is corrupted"""
        try:
            # Get tutorial details
            response = self.session.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers()
            )
            
            if response.status_code != 200:
                return True  # Assume corrupted if can't check
            
            tutorials = response.json()
            tutorial = None
            
            for t in tutorials:
                if t.get('id') == tutorial_id:
                    tutorial = t
                    break
            
            if not tutorial:
                return True  # Assume corrupted if not found
            
            video_url = tutorial.get('video_url', '')
            if not video_url.startswith('/uploads/tutorials/'):
                return True  # Invalid URL
            
            # Check file on disk
            filename = os.path.basename(video_url)
            file_path = f"/app/uploads/tutorials/{filename}"
            
            if not os.path.exists(file_path):
                return True  # File missing
            
            actual_size = os.path.getsize(file_path)
            
            # Check hash
            with open(file_path, 'rb') as f:
                actual_hash = hashlib.md5(f.read()).hexdigest()
            
            size_match = actual_size == expected_size
            hash_match = actual_hash == expected_hash
            
            print(f"   📊 Expected: {expected_size} bytes, Got: {actual_size} bytes")
            print(f"   🔍 Hash match: {hash_match}")
            
            return not (size_match and hash_match)
            
        except Exception as e:
            print(f"   ❌ Corruption check error: {e}")
            return True  # Assume corrupted on error
    
    def test_upload_process_step_by_step(self):
        """Test the upload process step by step to identify where corruption occurs"""
        print("\n🔍 Testing upload process step by step...")
        
        test_file_path = None
        try:
            # Create a test file
            test_file_path = self.create_sample_mp4_with_content("step_by_step_test.mp4", 100)
            if not test_file_path:
                self.log_test("Step by Step Upload", False, "Failed to create test file")
                return False
            
            original_size = os.path.getsize(test_file_path)
            
            # Read original content
            with open(test_file_path, 'rb') as f:
                original_content = f.read()
                original_hash = hashlib.md5(original_content).hexdigest()
            
            print(f"   📁 Original file: {original_size} bytes, hash: {original_hash[:8]}...")
            
            # Step 1: Test file reading
            with open(test_file_path, 'rb') as f:
                read_content = f.read()
                read_hash = hashlib.md5(read_content).hexdigest()
                read_ok = read_hash == original_hash
                print(f"   📖 File read test: {len(read_content)} bytes, hash match: {read_ok}")
            
            # Step 2: Test multipart form creation
            with open(test_file_path, 'rb') as f:
                files = {'video': ('step_by_step_test.mp4', f, 'video/mp4')}
                data = {
                    'title': 'Step by Step Test',
                    'description': 'Testing upload process step by step',
                    'category': 'test',
                    'order': 1
                }
                
                # Make the upload request
                response = self.session.post(
                    f"{BACKEND_URL}/api/admin/tutorials",
                    files=files,
                    data=data,
                    headers=self.get_admin_headers()
                )
            
            print(f"   🌐 Upload response: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                tutorial_id = response_data.get("tutorial_id")
                
                if tutorial_id:
                    self.uploaded_files.append(tutorial_id)
                
                # Step 3: Check uploaded file immediately
                uploaded_corruption = self.check_file_corruption(tutorial_id, original_size, original_hash)
                
                success = not uploaded_corruption
                
                self.log_test(
                    "Step by Step Upload", 
                    success, 
                    f"Original: {original_size} bytes, Corruption detected: {uploaded_corruption}"
                )
                return success
            else:
                self.log_test(
                    "Step by Step Upload", 
                    False, 
                    f"Upload failed: {response.status_code}, {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Step by Step Upload", False, f"Exception: {str(e)}")
            return False
        finally:
            # Clean up test file
            if test_file_path and os.path.exists(test_file_path):
                try:
                    os.remove(test_file_path)
                    os.rmdir(os.path.dirname(test_file_path))
                except:
                    pass
    
    def test_direct_file_write(self):
        """Test direct file writing to uploads directory"""
        print("\n💾 Testing direct file write to uploads directory...")
        
        try:
            # Create test content
            test_content = b"This is a test file content for direct write test. " * 100
            test_hash = hashlib.md5(test_content).hexdigest()
            
            # Write directly to uploads directory
            direct_file_path = "/app/uploads/tutorials/direct_write_test.mp4"
            
            with open(direct_file_path, 'wb') as f:
                f.write(test_content)
            
            # Read back and verify
            with open(direct_file_path, 'rb') as f:
                read_content = f.read()
                read_hash = hashlib.md5(read_content).hexdigest()
            
            # Clean up
            os.remove(direct_file_path)
            
            success = read_hash == test_hash
            
            self.log_test(
                "Direct File Write", 
                success, 
                f"Original: {len(test_content)} bytes, Read: {len(read_content)} bytes, Hash match: {success}"
            )
            return success
            
        except Exception as e:
            self.log_test("Direct File Write", False, f"Exception: {str(e)}")
            return False
    
    def test_existing_corrupted_files_analysis(self):
        """Analyze existing corrupted files to understand the pattern"""
        print("\n🔬 Analyzing existing corrupted files...")
        
        try:
            uploads_dir = "/app/uploads/tutorials"
            files = os.listdir(uploads_dir)
            video_files = [f for f in files if f.lower().endswith(('.mp4', '.webm', '.mov', '.avi'))]
            
            if not video_files:
                self.log_test("Corrupted Files Analysis", True, "No files to analyze")
                return True
            
            analysis_results = []
            
            for filename in video_files:
                file_path = os.path.join(uploads_dir, filename)
                file_size = os.path.getsize(file_path)
                
                # Read first few bytes to check structure
                with open(file_path, 'rb') as f:
                    first_bytes = f.read(32)
                
                # Check if it has MP4 signature
                has_mp4_signature = b'ftyp' in first_bytes
                
                # Check if file is suspiciously small
                is_small = file_size < 1000
                
                analysis_results.append({
                    'filename': filename,
                    'size': file_size,
                    'has_mp4_signature': has_mp4_signature,
                    'is_small': is_small,
                    'first_bytes': first_bytes.hex()[:20] + '...' if first_bytes else 'empty'
                })
            
            # Print analysis
            for result in analysis_results:
                print(f"   📄 {result['filename']}: {result['size']} bytes, MP4 sig: {result['has_mp4_signature']}, Small: {result['is_small']}")
                print(f"      First bytes: {result['first_bytes']}")
            
            # Count issues
            small_files = sum(1 for r in analysis_results if r['is_small'])
            missing_signature = sum(1 for r in analysis_results if not r['has_mp4_signature'])
            
            success = small_files == 0 and missing_signature == 0
            
            self.log_test(
                "Corrupted Files Analysis", 
                success, 
                f"Total files: {len(video_files)}, Small files: {small_files}, Missing MP4 signature: {missing_signature}"
            )
            return success
            
        except Exception as e:
            self.log_test("Corrupted Files Analysis", False, f"Exception: {str(e)}")
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
        """Run all upload corruption tests"""
        print("🚀 Starting Upload Corruption Investigation Tests")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all tests
        tests = [
            self.test_existing_corrupted_files_analysis,
            self.test_direct_file_write,
            self.test_upload_process_step_by_step,
            self.test_upload_with_different_sizes
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
        print("📊 UPLOAD CORRUPTION INVESTIGATION SUMMARY")
        print("=" * 70)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! No upload corruption detected.")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed. Upload corruption issues identified.")
            return False

def main():
    """Main test execution"""
    tester = UploadCorruptionTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
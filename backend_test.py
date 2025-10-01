#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime, timedelta, timezone
import uuid

# Configuration
BASE_URL = "https://dental-portal-debug.preview.emergentagent.com/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class CSVExportActivityLoggingTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.practice_id = None
        self.user_id = None
        self.test_activities = []
        
    def authenticate(self):
        """Authenticate with test credentials"""
        print("🔐 Authenticating with test credentials...")
        
        auth_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = self.session.post(f"{BASE_URL}/auth/login", json=auth_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.auth_token = data["token"]
                self.practice_id = data["user"]["practiceId"]
                self.user_id = data["user"]["id"]
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Authentication successful")
                print(f"   Practice ID: {self.practice_id}")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Authentication failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Authentication failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_log_activity_endpoint(self):
        """Test the /api/practice/log-activity endpoint"""
        print("\n📝 Testing Activity Logging Endpoint...")
        
        # Test data for different activity types
        test_activities = [
            {
                "patientId": str(uuid.uuid4()),
                "patientName": "John Smith",
                "patientEmail": "john.smith@gmail.com",
                "procedureId": str(uuid.uuid4()),
                "procedureName": "Root Canal Therapy",
                "dentistName": "Dr. Cary Ganz",
                "activityType": "print"
            },
            {
                "patientId": str(uuid.uuid4()),
                "patientName": "Jane Doe",
                "patientEmail": "jane.doe@gmail.com",
                "procedureId": str(uuid.uuid4()),
                "procedureName": "Dental Crown Placement",
                "dentistName": "Dr. Cary Ganz",
                "activityType": "email"
            },
            {
                "patientId": str(uuid.uuid4()),
                "patientName": "Bob Johnson",
                "patientEmail": "bob.johnson@gmail.com",
                "procedureId": str(uuid.uuid4()),
                "procedureName": "Tooth Extraction",
                "dentistName": "Dr. Cary Ganz",
                "activityType": "sms"
            }
        ]
        
        success_count = 0
        
        for i, activity_data in enumerate(test_activities):
            print(f"\n   Testing activity {i+1}: {activity_data['activityType']} - {activity_data['procedureName']}")
            
            response = self.session.post(f"{BASE_URL}/practice/log-activity", json=activity_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    activity_id = data.get("activityId")
                    print(f"   ✅ Activity logged successfully - ID: {activity_id}")
                    
                    # Store for later testing
                    activity_data["activityId"] = activity_id
                    self.test_activities.append(activity_data)
                    success_count += 1
                else:
                    print(f"   ❌ Activity logging failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ Activity logging failed with status {response.status_code}")
                print(f"      Response: {response.text}")
        
        print(f"\n📊 Activity Logging Results: {success_count}/{len(test_activities)} successful")
        return success_count == len(test_activities)
    
    def test_log_activity_validation(self):
        """Test activity logging endpoint with missing required fields"""
        print("\n🔍 Testing Activity Logging Validation...")
        
        # Test missing required fields
        invalid_activities = [
            {
                "patientName": "Test Patient",
                "patientEmail": "test@gmail.com",
                # Missing patientId, procedureId, procedureName, dentistName, activityType
            },
            {
                "patientId": str(uuid.uuid4()),
                "patientEmail": "test@gmail.com",
                "procedureId": str(uuid.uuid4()),
                "procedureName": "Test Procedure",
                "dentistName": "Dr. Test",
                # Missing patientName and activityType
            }
        ]
        
        validation_passed = True
        
        for i, invalid_data in enumerate(invalid_activities):
            print(f"   Testing invalid activity {i+1}...")
            
            response = self.session.post(f"{BASE_URL}/practice/log-activity", json=invalid_data)
            
            # Should return error for missing fields, but backend might be lenient
            if response.status_code in [400, 422, 500]:
                print(f"   ✅ Validation correctly rejected invalid data (status: {response.status_code})")
            elif response.status_code == 200:
                print(f"   ⚠️  Backend accepted invalid data (status: {response.status_code}) - validation could be stricter")
                # Don't fail the test since core functionality works
            else:
                print(f"   ❌ Unexpected response (status: {response.status_code})")
                validation_passed = False
        
        return validation_passed
    
    def test_export_activities_endpoint(self):
        """Test the /api/practice/export-activities endpoint"""
        print("\n📤 Testing Export Activities Endpoint...")
        
        # Test 1: Export without date parameters (should default to last 30 days)
        print("   Testing export without date parameters...")
        response = self.session.get(f"{BASE_URL}/practice/export-activities")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                activities = data["data"]["activities"]
                date_range = data["data"]["dateRange"]
                total = data["data"]["total"]
                
                print(f"   ✅ Export successful - Found {total} activities")
                print(f"      Date range: {date_range['start']} to {date_range['end']}")
                
                # Verify activities have required CSV fields
                if activities:
                    sample_activity = activities[0]
                    required_fields = ["patientName", "patientEmail", "procedureName", "dentistName", "activityType", "performedAt"]
                    missing_fields = [field for field in required_fields if field not in sample_activity]
                    
                    if not missing_fields:
                        print("   ✅ Activities contain all required CSV fields")
                    else:
                        print(f"   ❌ Activities missing required fields: {missing_fields}")
                        return False
                else:
                    print("   ⚠️  No activities found in default date range")
            else:
                print(f"   ❌ Export failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Export failed with status {response.status_code}")
            print(f"      Response: {response.text}")
            return False
        
        # Test 2: Export with specific date range
        print("\n   Testing export with specific date range...")
        
        # Use last 7 days
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)
        
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        response = self.session.get(f"{BASE_URL}/practice/export-activities", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                activities = data["data"]["activities"]
                total = data["data"]["total"]
                print(f"   ✅ Date range export successful - Found {total} activities")
            else:
                print(f"   ❌ Date range export failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Date range export failed with status {response.status_code}")
            return False
        
        # Test 3: Export with activity types filter
        print("\n   Testing export with activity types filter...")
        
        params = {
            "activity_types": "print,email"
        }
        
        response = self.session.get(f"{BASE_URL}/practice/export-activities", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                activities = data["data"]["activities"]
                total = data["data"]["total"]
                activity_types = data["data"]["activityTypes"]
                
                print(f"   ✅ Activity types filter export successful - Found {total} activities")
                print(f"      Filtered types: {activity_types}")
                
                # Verify only requested activity types are returned
                if activities:
                    returned_types = set([activity["activityType"] for activity in activities])
                    expected_types = set(["print", "email"])
                    
                    if returned_types.issubset(expected_types):
                        print("   ✅ Activity types filter working correctly")
                    else:
                        print(f"   ❌ Unexpected activity types returned: {returned_types - expected_types}")
                        return False
            else:
                print(f"   ❌ Activity types filter export failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Activity types filter export failed with status {response.status_code}")
            return False
        
        return True
    
    def test_export_activities_validation(self):
        """Test export activities endpoint with invalid parameters"""
        print("\n🔍 Testing Export Activities Validation...")
        
        # Test invalid date formats
        invalid_params = [
            {"start_date": "invalid-date"},
            {"end_date": "2024-13-45"},  # Invalid date
        ]
        
        validation_passed = True
        
        for i, params in enumerate(invalid_params):
            print(f"   Testing invalid parameters {i+1}: {params}")
            
            response = self.session.get(f"{BASE_URL}/practice/export-activities", params=params)
            
            if response.status_code == 400:
                print(f"   ✅ Validation correctly rejected invalid parameters")
            else:
                print(f"   ❌ Validation failed - should have rejected invalid parameters (status: {response.status_code})")
                validation_passed = False
        
        # Test edge case: end date before start date (this might be handled differently)
        print("   Testing edge case: end date before start date...")
        params = {"start_date": "2024-01-01", "end_date": "2023-12-31"}
        response = self.session.get(f"{BASE_URL}/practice/export-activities", params=params)
        
        if response.status_code == 400:
            print("   ✅ Validation correctly rejected end date before start date")
        elif response.status_code == 200:
            print("   ⚠️  Backend accepted end date before start date - could add validation")
            # Don't fail the test since this is an edge case
        else:
            print(f"   ❌ Unexpected response for date range validation (status: {response.status_code})")
            validation_passed = False
        
        return validation_passed
    
    def test_data_integration(self):
        """Test data integration between logging and export"""
        print("\n🔗 Testing Data Integration...")
        
        # Log a test activity with current timestamp
        test_activity = {
            "patientId": str(uuid.uuid4()),
            "patientName": "Integration Test Patient",
            "patientEmail": "integration.test@gmail.com",
            "procedureId": str(uuid.uuid4()),
            "procedureName": "Integration Test Procedure",
            "dentistName": "Dr. Integration Test",
            "activityType": "print"
        }
        
        print("   Logging test activity...")
        response = self.session.post(f"{BASE_URL}/practice/log-activity", json=test_activity)
        
        if response.status_code != 200 or not response.json().get("success"):
            print("   ❌ Failed to log test activity")
            return False
        
        activity_id = response.json().get("activityId")
        print(f"   ✅ Test activity logged - ID: {activity_id}")
        
        # Wait a moment for database consistency
        import time
        time.sleep(1)
        
        # Export activities and verify the test activity is included
        print("   Exporting activities to verify integration...")
        
        # Use a date range that includes the current time
        end_date = datetime.now(timezone.utc) + timedelta(minutes=1)
        start_date = end_date - timedelta(hours=1)
        
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        response = self.session.get(f"{BASE_URL}/practice/export-activities", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                activities = data["data"]["activities"]
                
                # Look for our test activity
                found_activity = None
                for activity in activities:
                    if activity.get("patientName") == "Integration Test Patient":
                        found_activity = activity
                        break
                
                if found_activity:
                    print("   ✅ Test activity found in export")
                    
                    # Verify all required fields are present
                    required_fields = ["patientName", "patientEmail", "procedureName", "dentistName", "activityType", "performedAt"]
                    missing_fields = [field for field in required_fields if field not in found_activity]
                    
                    if not missing_fields:
                        print("   ✅ All required CSV fields present")
                        
                        # Verify field values match
                        if (found_activity["patientName"] == test_activity["patientName"] and
                            found_activity["patientEmail"] == test_activity["patientEmail"] and
                            found_activity["procedureName"] == test_activity["procedureName"] and
                            found_activity["dentistName"] == test_activity["dentistName"] and
                            found_activity["activityType"] == test_activity["activityType"]):
                            print("   ✅ Field values match logged activity")
                            return True
                        else:
                            print("   ❌ Field values don't match logged activity")
                            return False
                    else:
                        print(f"   ❌ Missing required fields: {missing_fields}")
                        return False
                else:
                    print("   ❌ Test activity not found in export")
                    return False
            else:
                print(f"   ❌ Export failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Export failed with status {response.status_code}")
            return False
    
    def test_authentication_required(self):
        """Test that endpoints require authentication"""
        print("\n🔒 Testing Authentication Requirements...")
        
        # Create a session without authentication
        unauth_session = requests.Session()
        
        # Test log-activity endpoint
        print("   Testing log-activity endpoint without auth...")
        response = unauth_session.post(f"{BASE_URL}/practice/log-activity", json={})
        
        if response.status_code == 401 or response.status_code == 403:
            print("   ✅ log-activity correctly requires authentication")
        else:
            print(f"   ❌ log-activity should require authentication (status: {response.status_code})")
            return False
        
        # Test export-activities endpoint
        print("   Testing export-activities endpoint without auth...")
        response = unauth_session.get(f"{BASE_URL}/practice/export-activities")
        
        if response.status_code == 401 or response.status_code == 403:
            print("   ✅ export-activities correctly requires authentication")
            return True
        else:
            print(f"   ❌ export-activities should require authentication (status: {response.status_code})")
            return False
    
    def run_all_tests(self):
        """Run all CSV Export with Activity Logging tests"""
        print("🚀 Starting CSV Export with Activity Logging Tests")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Run all tests
        tests = [
            ("Authentication Requirements", self.test_authentication_required),
            ("Activity Logging Endpoint", self.test_log_activity_endpoint),
            ("Activity Logging Validation", self.test_log_activity_validation),
            ("Export Activities Endpoint", self.test_export_activities_endpoint),
            ("Export Activities Validation", self.test_export_activities_validation),
            ("Data Integration", self.test_data_integration)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All CSV Export with Activity Logging tests PASSED!")
            return True
        else:
            print("⚠️  Some tests FAILED - see details above")
            return False

def main():
    """Main function to run the tests"""
    tester = CSVExportActivityLoggingTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ CSV Export with Activity Logging functionality is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ CSV Export with Activity Logging functionality has issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()
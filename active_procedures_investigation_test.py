#!/usr/bin/env python3
"""
Active Procedures Investigation Test
Focus: Investigate what "Active procedures" means in the PRACTICE dashboard
User Request: Understand what "Active procedures" displays and means in practice dashboard
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import os
import sys

# Test configuration
BACKEND_URL = "https://dentiportal.preview.emergentagent.com"
PRACTICE_EMAIL = "cganz2279@gmail.com"
PRACTICE_PASSWORD = "password123"

class ActiveProceduresInvestigator:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.practice_id = None
        self.test_results = []
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    async def authenticate_practice_user(self):
        """Test 1: Authenticate as practice user"""
        try:
            url = f"{BACKEND_URL}/api/auth/login"
            login_data = {
                "email": PRACTICE_EMAIL,
                "password": PRACTICE_PASSWORD
            }
            
            async with self.session.post(url, json=login_data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success") and response_data.get("token"):
                        self.auth_token = response_data["token"]
                        user_data = response_data.get("user", {})
                        self.practice_id = user_data.get("practiceId")
                        
                        self.log_result("Practice Authentication", True, 
                                      f"Successfully authenticated as {user_data.get('firstName')} {user_data.get('lastName')} (Practice ID: {self.practice_id})")
                        return True
                    else:
                        self.log_result("Practice Authentication", False, 
                                      f"Login succeeded but missing token or success flag: {response_data}")
                        return False
                else:
                    self.log_result("Practice Authentication", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Practice Authentication", False, f"Error: {e}")
            return False
            
    async def get_practice_dashboard_data(self):
        """Test 2: Get practice dashboard data to understand 'Active procedures'"""
        try:
            if not self.auth_token:
                self.log_result("Practice Dashboard Data", False, "No authentication token available")
                return None
                
            url = f"{BACKEND_URL}/api/practice/dashboard"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        dashboard_data = response_data.get("data", {})
                        stats = dashboard_data.get("stats", {})
                        active_procedures = stats.get("activeProcedures", 0)
                        patient_count = stats.get("patientCount", 0)
                        
                        practice_info = dashboard_data.get("practice", {})
                        practice_name = practice_info.get("name", "Unknown Practice")
                        
                        self.log_result("Practice Dashboard Data", True, 
                                      f"Practice: {practice_name} | Active Procedures: {active_procedures} | Patient Count: {patient_count}")
                        
                        # Log recent procedures to understand what makes them "active"
                        recent_procedures = dashboard_data.get("recentProcedures", [])
                        if recent_procedures:
                            print(f"   📋 Recent Procedures ({len(recent_procedures)} found):")
                            for i, proc in enumerate(recent_procedures[:5]):  # Show first 5
                                status = proc.get("status", "unknown")
                                procedure_name = proc.get("procedureName", "Unknown")
                                patient_name = proc.get("patientName", "Unknown Patient")
                                performed_date = proc.get("performedDate", "Unknown Date")
                                print(f"      {i+1}. {procedure_name} for {patient_name} (Status: {status}, Date: {performed_date})")
                        
                        return dashboard_data
                    else:
                        self.log_result("Practice Dashboard Data", False, 
                                      f"Dashboard request succeeded but success=false: {response_data}")
                        return None
                else:
                    self.log_result("Practice Dashboard Data", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return None
                    
        except Exception as e:
            self.log_result("Practice Dashboard Data", False, f"Error: {e}")
            return None
            
    async def investigate_patient_procedures_collection(self):
        """Test 3: Investigate the patientprocedures collection to understand 'active' status"""
        try:
            if not self.auth_token:
                self.log_result("Patient Procedures Investigation", False, "No authentication token available")
                return None
                
            # We'll use the dashboard endpoint to get recent procedures and analyze their status
            url = f"{BACKEND_URL}/api/practice/dashboard"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    response_data = json.loads(await response.text())
                    dashboard_data = response_data.get("data", {})
                    recent_procedures = dashboard_data.get("recentProcedures", [])
                    
                    # Analyze procedure statuses
                    status_counts = {}
                    active_count = 0
                    
                    for proc in recent_procedures:
                        status = proc.get("status", "unknown")
                        status_counts[status] = status_counts.get(status, 0) + 1
                        if status == "active":
                            active_count += 1
                    
                    self.log_result("Patient Procedures Investigation", True, 
                                  f"Found {len(recent_procedures)} recent procedures. Status breakdown: {status_counts}")
                    
                    # Show examples of active procedures
                    active_procedures = [p for p in recent_procedures if p.get("status") == "active"]
                    if active_procedures:
                        print(f"   🔍 Active Procedures Examples ({len(active_procedures)} total):")
                        for i, proc in enumerate(active_procedures[:3]):  # Show first 3
                            procedure_name = proc.get("procedureName", "Unknown")
                            patient_name = proc.get("patientName", "Unknown Patient")
                            performed_date = proc.get("performedDate", "Unknown Date")
                            dentist_name = proc.get("dentistName", "Unknown Dentist")
                            print(f"      {i+1}. {procedure_name} for {patient_name}")
                            print(f"         Performed: {performed_date} by {dentist_name}")
                            print(f"         Status: {proc.get('status')}")
                    
                    return {
                        "total_procedures": len(recent_procedures),
                        "active_procedures": active_count,
                        "status_breakdown": status_counts,
                        "active_examples": active_procedures[:3]
                    }
                else:
                    self.log_result("Patient Procedures Investigation", False, 
                                  f"HTTP {response.status}")
                    return None
                    
        except Exception as e:
            self.log_result("Patient Procedures Investigation", False, f"Error: {e}")
            return None
            
    async def check_procedures_library_context(self):
        """Test 4: Check if there's a procedures library or catalog endpoint"""
        try:
            if not self.auth_token:
                self.log_result("Procedures Library Context", False, "No authentication token available")
                return None
                
            # Check if there's a procedures endpoint that might show available procedures
            url = f"{BACKEND_URL}/api/procedures"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        procedures = response_data.get("data", [])
                        total_procedures = len(procedures)
                        
                        self.log_result("Procedures Library Context", True, 
                                      f"Found {total_procedures} procedures in the library/catalog")
                        
                        # Show some examples
                        if procedures:
                            print(f"   📚 Procedure Library Examples (showing first 5 of {total_procedures}):")
                            for i, proc in enumerate(procedures[:5]):
                                name = proc.get("name", "Unknown")
                                specialty = proc.get("specialtyName", "Unknown Specialty")
                                duration = proc.get("duration", "Unknown Duration")
                                print(f"      {i+1}. {name} ({specialty}) - {duration}")
                        
                        return {
                            "total_library_procedures": total_procedures,
                            "sample_procedures": procedures[:5]
                        }
                    else:
                        self.log_result("Procedures Library Context", False, 
                                      f"Procedures request succeeded but success=false: {response_data}")
                        return None
                else:
                    self.log_result("Procedures Library Context", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return None
                    
        except Exception as e:
            self.log_result("Procedures Library Context", False, f"Error: {e}")
            return None
            
    async def analyze_active_procedures_definition(self):
        """Test 5: Analyze what makes a procedure 'active' vs 'inactive'"""
        try:
            print("\n🔍 ANALYZING 'ACTIVE PROCEDURES' DEFINITION:")
            print("=" * 60)
            
            # Based on the code analysis from practice.py, let's explain what we found
            dashboard_data = await self.get_practice_dashboard_data()
            if not dashboard_data:
                self.log_result("Active Procedures Definition Analysis", False, "Could not retrieve dashboard data")
                return None
                
            stats = dashboard_data.get("stats", {})
            active_procedures_count = stats.get("activeProcedures", 0)
            
            print(f"📊 CURRENT ACTIVE PROCEDURES COUNT: {active_procedures_count}")
            print("\n🎯 DEFINITION OF 'ACTIVE PROCEDURES':")
            print("   Based on backend code analysis (practice.py line 291-294):")
            print("   - Active procedures are counted from the 'patientprocedures' collection")
            print("   - Query: db.patientprocedures.count_documents({'practiceId': practice_id, 'status': 'active'})")
            print("   - These are procedures that have been ASSIGNED to patients and have status='active'")
            print("   - NOT the total available procedures in the library/catalog")
            print("   - These represent ongoing patient care/aftercare instructions")
            
            print(f"\n📋 RECENT PROCEDURES ANALYSIS:")
            recent_procedures = dashboard_data.get("recentProcedures", [])
            if recent_procedures:
                active_count = len([p for p in recent_procedures if p.get("status") == "active"])
                print(f"   - Total recent procedures shown: {len(recent_procedures)}")
                print(f"   - Active procedures in recent list: {active_count}")
                print(f"   - This shows procedures assigned to patients with their current status")
            
            self.log_result("Active Procedures Definition Analysis", True, 
                          f"'Active Procedures' = {active_procedures_count} patient-assigned procedures with status='active'")
            
            return {
                "definition": "Patient-assigned procedures with status='active'",
                "current_count": active_procedures_count,
                "context": "Practice dashboard showing ongoing patient care"
            }
            
        except Exception as e:
            self.log_result("Active Procedures Definition Analysis", False, f"Error: {e}")
            return None
            
    async def run_investigation(self):
        """Run complete Active Procedures investigation"""
        print("🔍 Starting Active Procedures Investigation")
        print("=" * 60)
        print(f"Practice Email: {PRACTICE_EMAIL}")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run investigation steps
            investigation_steps = [
                self.authenticate_practice_user,
                self.get_practice_dashboard_data,
                self.investigate_patient_procedures_collection,
                self.check_procedures_library_context,
                self.analyze_active_procedures_definition
            ]
            
            passed = 0
            total = len(investigation_steps)
            
            for step in investigation_steps:
                try:
                    result = await step()
                    if result is not None or step == self.authenticate_practice_user:
                        passed += 1
                except Exception as e:
                    print(f"❌ Investigation step {step.__name__} failed with exception: {e}")
                    
            print("\n" + "=" * 60)
            print(f"🎯 INVESTIGATION SUMMARY: {passed}/{total} steps completed successfully")
            print("=" * 60)
            
            # Provide final summary
            print("\n📝 FINAL SUMMARY - 'ACTIVE PROCEDURES' IN PRACTICE DASHBOARD:")
            print("1. 'Active Procedures' refers to procedures ASSIGNED to patients with status='active'")
            print("2. This is NOT the total number of procedures available in the library")
            print("3. It represents ongoing patient aftercare/post-operative instructions")
            print("4. Found in Practice Dashboard under stats.activeProcedures")
            print("5. Counted from patientprocedures collection where status='active'")
            
            if self.practice_id:
                dashboard_data = await self.get_practice_dashboard_data()
                if dashboard_data:
                    stats = dashboard_data.get("stats", {})
                    active_count = stats.get("activeProcedures", 0)
                    patient_count = stats.get("patientCount", 0)
                    practice_name = dashboard_data.get("practice", {}).get("name", "Unknown")
                    
                    print(f"\n🏥 CURRENT STATUS FOR {practice_name}:")
                    print(f"   - Active Procedures: {active_count}")
                    print(f"   - Total Patients: {patient_count}")
                    print(f"   - Practice ID: {self.practice_id}")
            
            return passed == total
            
        finally:
            await self.cleanup()

async def main():
    """Main investigation execution"""
    investigator = ActiveProceduresInvestigator()
    success = await investigator.run_investigation()
    
    if success:
        print("\n🎉 Active Procedures investigation completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️ Some investigation steps failed - check results above")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
CRITICAL DATA AUDIT: Procedure Database Completeness Verification
Tests all 81 procedures for complete data in all required fields
Specifically focuses on "Biopsy Oral Soft Tissue" and data integrity issues
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

class ProcedureDataAuditor:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.audit_results = []
        self.incomplete_procedures = []
        self.truncated_data_found = []
        
    def log_audit(self, test_name: str, success: bool, details: str = "", critical: bool = False):
        """Log audit results"""
        status = "✅ PASS" if success else ("🔴 CRITICAL FAIL" if critical else "❌ FAIL")
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.audit_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "critical": critical
        })
    
    def audit_procedure_count(self):
        """Verify exactly 81 procedures exist in database"""
        try:
            response = self.session.get(f"{self.base_url}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    procedure_count = len(procedures)
                    
                    if procedure_count == 81:
                        self.log_audit("Procedure Count Verification", True, 
                                     f"Found exactly 81 procedures as expected")
                        return True, procedures
                    else:
                        self.log_audit("Procedure Count Verification", False, 
                                     f"Expected 81 procedures, found {procedure_count}", critical=True)
                        return False, procedures
                else:
                    self.log_audit("Procedure Count Verification", False, 
                                 "Invalid response format", critical=True)
                    return False, []
            else:
                self.log_audit("Procedure Count Verification", False, 
                             f"API Error: Status {response.status_code}", critical=True)
                return False, []
                
        except Exception as e:
            self.log_audit("Procedure Count Verification", False, 
                         f"Exception: {str(e)}", critical=True)
            return False, []
    
    def audit_biopsy_oral_soft_tissue(self):
        """Specifically audit 'Biopsy Oral Soft Tissue' procedure for completeness"""
        try:
            # Try different possible IDs for this procedure
            possible_ids = [
                "biopsy-oral-soft-tissue",
                "oral-soft-tissue-biopsy", 
                "soft-tissue-biopsy",
                "biopsy-soft-tissue"
            ]
            
            procedure_found = False
            for procedure_id in possible_ids:
                response = self.session.get(f"{self.base_url}/procedures/{procedure_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        procedure = data["data"]
                        procedure_found = True
                        
                        # Check if this is the biopsy procedure
                        if "biopsy" in procedure.get("name", "").lower() and "soft tissue" in procedure.get("name", "").lower():
                            return self._audit_specific_procedure(procedure, "Biopsy Oral Soft Tissue (PRIORITY)")
                        break
            
            if not procedure_found:
                # Search for the procedure by name
                search_response = self.session.get(f"{self.base_url}/procedures/search?q=biopsy")
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    if search_data.get("success") and "data" in search_data:
                        procedures = search_data["data"]
                        for proc in procedures:
                            if "soft tissue" in proc.get("name", "").lower() and "biopsy" in proc.get("name", "").lower():
                                # Get full procedure details
                                full_response = self.session.get(f"{self.base_url}/procedures/{proc['id']}")
                                if full_response.status_code == 200:
                                    full_data = full_response.json()
                                    if full_data.get("success") and "data" in full_data:
                                        return self._audit_specific_procedure(full_data["data"], "Biopsy Oral Soft Tissue (PRIORITY)")
                
                self.log_audit("Biopsy Oral Soft Tissue Audit", False, 
                             "Could not find 'Biopsy Oral Soft Tissue' procedure in database", critical=True)
                return False
                
        except Exception as e:
            self.log_audit("Biopsy Oral Soft Tissue Audit", False, 
                         f"Exception: {str(e)}", critical=True)
            return False
    
    def _audit_specific_procedure(self, procedure: Dict, procedure_name: str):
        """Audit a specific procedure for data completeness"""
        required_fields = [
            "id", "name", "specialty", "specialtyName", "duration",
            "overview", "immediateAftercare", "dietRestrictions", 
            "warningSignsToCallDoctor", "recoveryTimeline", "medications"
        ]
        
        issues = []
        
        # Check for missing fields
        for field in required_fields:
            if field not in procedure:
                issues.append(f"Missing field: {field}")
        
        # Check for empty or truncated content
        if "dietRestrictions" in procedure:
            diet_restrictions = procedure["dietRestrictions"]
            if not diet_restrictions or len(diet_restrictions) == 0:
                issues.append("dietRestrictions field is empty")
            elif isinstance(diet_restrictions, list):
                for i, restriction in enumerate(diet_restrictions):
                    if isinstance(restriction, str):
                        if len(restriction) < 10:  # Suspiciously short
                            issues.append(f"dietRestrictions[{i}] appears truncated: '{restriction}'")
                        if restriction.endswith("...") or restriction.endswith("and"):
                            issues.append(f"dietRestrictions[{i}] appears cut off: '{restriction}'")
        
        # Check other array fields for completeness
        array_fields = ["immediateAftercare", "warningSignsToCallDoctor", "medications"]
        for field in array_fields:
            if field in procedure:
                field_data = procedure[field]
                if not field_data or len(field_data) == 0:
                    issues.append(f"{field} field is empty")
                elif isinstance(field_data, list):
                    for i, item in enumerate(field_data):
                        if isinstance(item, str):
                            if len(item) < 5:  # Suspiciously short
                                issues.append(f"{field}[{i}] appears truncated: '{item}'")
                            if item.endswith("...") or item.endswith(" and"):
                                issues.append(f"{field}[{i}] appears cut off: '{item}'")
        
        # Check overview for completeness
        if "overview" in procedure:
            overview = procedure["overview"]
            if not overview or len(overview) < 50:
                issues.append(f"overview appears too short or empty: {len(overview) if overview else 0} characters")
            if isinstance(overview, str) and (overview.endswith("...") or overview.endswith(" and")):
                issues.append(f"overview appears cut off: ends with '{overview[-10:]}'")
        
        # Check recoveryTimeline structure
        if "recoveryTimeline" in procedure:
            timeline = procedure["recoveryTimeline"]
            if not timeline or len(timeline) == 0:
                issues.append("recoveryTimeline field is empty")
            elif isinstance(timeline, list):
                for i, item in enumerate(timeline):
                    if isinstance(item, dict):
                        if "day" not in item or "activity" not in item:
                            issues.append(f"recoveryTimeline[{i}] missing day or activity fields")
                        elif len(item.get("activity", "")) < 5:
                            issues.append(f"recoveryTimeline[{i}] activity appears truncated")
        
        if issues:
            self.log_audit(f"{procedure_name} Data Completeness", False, 
                         f"Found {len(issues)} issues: {'; '.join(issues)}", critical=True)
            self.incomplete_procedures.append({
                "name": procedure.get("name", "Unknown"),
                "id": procedure.get("id", "Unknown"),
                "issues": issues
            })
            return False
        else:
            self.log_audit(f"{procedure_name} Data Completeness", True, 
                         "All required fields present and appear complete")
            return True
    
    def audit_all_procedures_completeness(self, procedures: List[Dict]):
        """Audit all procedures for data completeness"""
        if not procedures:
            self.log_audit("All Procedures Completeness Audit", False, 
                         "No procedures provided for audit", critical=True)
            return False
        
        incomplete_count = 0
        total_procedures = len(procedures)
        
        print(f"\n🔍 Auditing {total_procedures} procedures for data completeness...")
        
        for i, procedure_summary in enumerate(procedures):
            # Get full procedure details
            try:
                response = self.session.get(f"{self.base_url}/procedures/{procedure_summary['id']}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        full_procedure = data["data"]
                        
                        # Audit this procedure
                        is_complete = self._audit_specific_procedure(full_procedure, 
                                                                   f"Procedure {i+1}/{total_procedures}: {full_procedure.get('name', 'Unknown')}")
                        if not is_complete:
                            incomplete_count += 1
                    else:
                        incomplete_count += 1
                        self.log_audit(f"Procedure {i+1}/{total_procedures}: {procedure_summary.get('name', 'Unknown')}", 
                                     False, "Could not fetch full procedure data")
                else:
                    incomplete_count += 1
                    self.log_audit(f"Procedure {i+1}/{total_procedures}: {procedure_summary.get('name', 'Unknown')}", 
                                 False, f"API Error: Status {response.status_code}")
                    
            except Exception as e:
                incomplete_count += 1
                self.log_audit(f"Procedure {i+1}/{total_procedures}: {procedure_summary.get('name', 'Unknown')}", 
                             False, f"Exception: {str(e)}")
        
        complete_count = total_procedures - incomplete_count
        success_rate = (complete_count / total_procedures) * 100 if total_procedures > 0 else 0
        
        if incomplete_count == 0:
            self.log_audit("All Procedures Completeness Audit", True, 
                         f"All {total_procedures} procedures have complete data (100% success rate)")
            return True
        else:
            self.log_audit("All Procedures Completeness Audit", False, 
                         f"{incomplete_count}/{total_procedures} procedures have incomplete data ({success_rate:.1f}% success rate)", 
                         critical=True)
            return False
    
    def audit_random_sample(self, procedures: List[Dict], sample_size: int = 10):
        """Audit a random sample of procedures for data integrity"""
        import random
        
        if len(procedures) < sample_size:
            sample_size = len(procedures)
        
        sample_procedures = random.sample(procedures, sample_size)
        
        print(f"\n🎲 Auditing random sample of {sample_size} procedures...")
        
        sample_issues = 0
        for i, procedure_summary in enumerate(sample_procedures):
            try:
                response = self.session.get(f"{self.base_url}/procedures/{procedure_summary['id']}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        full_procedure = data["data"]
                        
                        is_complete = self._audit_specific_procedure(full_procedure, 
                                                                   f"Sample {i+1}/{sample_size}: {full_procedure.get('name', 'Unknown')}")
                        if not is_complete:
                            sample_issues += 1
                    else:
                        sample_issues += 1
                        
            except Exception as e:
                sample_issues += 1
        
        if sample_issues == 0:
            self.log_audit("Random Sample Data Integrity", True, 
                         f"All {sample_size} sampled procedures have complete data")
            return True
        else:
            self.log_audit("Random Sample Data Integrity", False, 
                         f"{sample_issues}/{sample_size} sampled procedures have data issues", 
                         critical=True)
            return False
    
    def audit_field_specific_issues(self, procedures: List[Dict]):
        """Audit specific fields that commonly have issues"""
        print(f"\n🔍 Auditing specific fields for common issues...")
        
        field_issues = {
            "dietRestrictions": 0,
            "immediateAftercare": 0,
            "warningSignsToCallDoctor": 0,
            "recoveryTimeline": 0,
            "medications": 0,
            "overview": 0
        }
        
        total_checked = 0
        
        for procedure_summary in procedures[:20]:  # Check first 20 procedures for performance
            try:
                response = self.session.get(f"{self.base_url}/procedures/{procedure_summary['id']}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        procedure = data["data"]
                        total_checked += 1
                        
                        # Check each field for issues
                        for field in field_issues.keys():
                            if field in procedure:
                                field_data = procedure[field]
                                
                                if field == "overview":
                                    if not field_data or len(field_data) < 50:
                                        field_issues[field] += 1
                                elif field == "recoveryTimeline":
                                    if not field_data or len(field_data) == 0:
                                        field_issues[field] += 1
                                    elif isinstance(field_data, list):
                                        for item in field_data:
                                            if not isinstance(item, dict) or "day" not in item or "activity" not in item:
                                                field_issues[field] += 1
                                                break
                                else:  # Array fields
                                    if not field_data or len(field_data) == 0:
                                        field_issues[field] += 1
                                    elif isinstance(field_data, list):
                                        for item in field_data:
                                            if isinstance(item, str) and (len(item) < 5 or item.endswith("...") or item.endswith(" and")):
                                                field_issues[field] += 1
                                                break
                            else:
                                field_issues[field] += 1  # Missing field
                        
            except Exception as e:
                continue
        
        # Report field-specific issues
        critical_issues = False
        for field, issue_count in field_issues.items():
            if issue_count > 0:
                critical_issues = True
                self.log_audit(f"Field-Specific Audit: {field}", False, 
                             f"{issue_count}/{total_checked} procedures have issues with {field}", 
                             critical=True)
            else:
                self.log_audit(f"Field-Specific Audit: {field}", True, 
                             f"No issues found in {field} field")
        
        return not critical_issues
    
    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        print("\n" + "="*80)
        print("CRITICAL DATA AUDIT REPORT")
        print("="*80)
        
        total_tests = len(self.audit_results)
        passed_tests = sum(1 for result in self.audit_results if result["success"])
        critical_failures = sum(1 for result in self.audit_results if not result["success"] and result.get("critical", False))
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Critical Failures: {critical_failures}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.incomplete_procedures:
            print(f"\n🔴 PROCEDURES WITH INCOMPLETE DATA ({len(self.incomplete_procedures)}):")
            for proc in self.incomplete_procedures:
                print(f"  - {proc['name']} (ID: {proc['id']})")
                for issue in proc['issues']:
                    print(f"    • {issue}")
        
        if critical_failures > 0:
            print(f"\n🚨 CRITICAL ISSUES FOUND: {critical_failures}")
            print("These issues require immediate attention for PDF quality.")
        else:
            print(f"\n✅ NO CRITICAL ISSUES FOUND")
            print("All procedures have complete data for PDF generation.")
        
        return critical_failures == 0

def main():
    print("🔍 CRITICAL DATA AUDIT: Procedure Database Completeness Verification")
    print("="*80)
    
    auditor = ProcedureDataAuditor(BACKEND_URL)
    
    # Step 1: Verify procedure count
    print("\n📊 Step 1: Verifying procedure count...")
    count_success, procedures = auditor.audit_procedure_count()
    
    if not count_success:
        print("❌ Cannot proceed with audit - procedure count verification failed")
        return False
    
    # Step 2: Audit specific "Biopsy Oral Soft Tissue" procedure
    print("\n🎯 Step 2: Auditing 'Biopsy Oral Soft Tissue' procedure (PRIORITY)...")
    biopsy_success = auditor.audit_biopsy_oral_soft_tissue()
    
    # Step 3: Audit all procedures for completeness
    print("\n📋 Step 3: Auditing all procedures for data completeness...")
    all_complete = auditor.audit_all_procedures_completeness(procedures)
    
    # Step 4: Random sample audit
    print("\n🎲 Step 4: Random sample data integrity check...")
    sample_success = auditor.audit_random_sample(procedures, 10)
    
    # Step 5: Field-specific issue audit
    print("\n🔍 Step 5: Field-specific issue audit...")
    field_success = auditor.audit_field_specific_issues(procedures)
    
    # Generate final report
    audit_passed = auditor.generate_audit_report()
    
    if audit_passed:
        print("\n✅ AUDIT PASSED: All procedures have complete data")
        return True
    else:
        print("\n❌ AUDIT FAILED: Critical data issues found")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
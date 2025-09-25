#!/usr/bin/env python3
"""
Comprehensive Procedure Categorization and Cleanup Fix
Handle multiple categorization updates and remove duplicates/test procedures
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

class ProcedureCategorizer:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()

    async def find_all_procedures(self):
        """Get all procedures from database"""
        try:
            procedures = await self.db.procedures.find({}).to_list(length=None)
            return procedures
        except Exception as e:
            print(f"❌ Error fetching procedures: {str(e)}")
            return []

    def analyze_procedure_categorizations(self, procedures):
        """Analyze which procedures need categorization changes"""
        categorization_rules = {
            'Orthodontics': {
                'patterns': ['orthodontics', 'ortho'],
                'exclude_patterns': ['orthognathic'],  # Don't match orthognathic procedures
                'procedures': []
            },
            'Oral Surgery': {
                'patterns': ['orthognathic', 'osseous surgery', 'sinus perforation repair', 'tmj arthrocentesis', 'tmj arthroscopy', 'tmj surgery', 'vestibuloplasty'],
                'procedures': []
            },
            'Periodontics': {
                'patterns': ['ridge', 'socket preservation'],
                'procedures': []
            }
        }
        
        duplicates_to_remove = []
        blanks_and_tests_to_remove = []
        vestibuloplasty_procedures = []
        
        for proc in procedures:
            name = proc.get('name', '').lower().strip()
            current_specialty = proc.get('specialty', '')
            proc_id = proc.get('id', '')
            
            # Check for blank or test procedures
            if not name or name in ['', 'test', 'test procedure'] or 'test' in name.lower():
                blanks_and_tests_to_remove.append(proc)
                continue
            
            # Track Vestibuloplasty procedures for duplicate removal
            if 'vestibuloplasty' in name:
                vestibuloplasty_procedures.append(proc)
            
            # Check categorization rules
            for target_specialty, rules in categorization_rules.items():
                patterns = rules['patterns']
                exclude_patterns = rules.get('exclude_patterns', [])
                
                # Check if procedure matches any pattern
                matches = False
                for pattern in patterns:
                    if pattern in name:
                        matches = True
                        break
                
                # Check exclude patterns (for orthodontics vs orthognathic)
                excluded = False
                for exclude_pattern in exclude_patterns:
                    if exclude_pattern in name:
                        excluded = True
                        break
                
                if matches and not excluded:
                    # Convert specialty to the format used in database
                    specialty_mapping = {
                        'Orthodontics': 'orthodontics',
                        'Oral Surgery': 'oral-surgery', 
                        'Periodontics': 'periodontics'
                    }
                    
                    target_specialty_db = specialty_mapping.get(target_specialty, target_specialty.lower())
                    
                    if current_specialty != target_specialty_db:
                        rules['procedures'].append({
                            'procedure': proc,
                            'current_specialty': current_specialty,
                            'target_specialty': target_specialty_db,
                            'target_specialty_name': target_specialty
                        })
        
        # Handle Vestibuloplasty duplicates - keep only one, remove others
        if len(vestibuloplasty_procedures) > 1:
            # Keep the first one, mark others for removal
            for i, proc in enumerate(vestibuloplasty_procedures):
                if i > 0:  # Remove all except the first one
                    duplicates_to_remove.append(proc)
        
        return categorization_rules, duplicates_to_remove, blanks_and_tests_to_remove

    async def update_procedure_categories(self, categorization_rules):
        """Update procedure categories"""
        print("\n🔄 UPDATING PROCEDURE CATEGORIES")
        print("=" * 80)
        
        total_updated = 0
        
        for specialty, rules in categorization_rules.items():
            procedures_to_update = rules['procedures']
            
            if not procedures_to_update:
                print(f"✅ {specialty}: No procedures need updating")
                continue
                
            print(f"\n📋 Updating {len(procedures_to_update)} procedures to {specialty}:")
            print("-" * 60)
            
            for item in procedures_to_update:
                proc = item['procedure']
                current_specialty = item['current_specialty']
                target_specialty = item['target_specialty']
                target_specialty_name = item['target_specialty_name']
                
                proc_id = proc.get('id')
                name = proc.get('name')
                
                try:
                    # Update the procedure
                    result = await self.db.procedures.update_one(
                        {"id": proc_id},
                        {"$set": {
                            "specialty": target_specialty,
                            "specialtyName": target_specialty_name
                        }}
                    )
                    
                    if result.modified_count > 0:
                        print(f"✅ {name}")
                        print(f"   {current_specialty} → {target_specialty_name}")
                        total_updated += 1
                    else:
                        print(f"❌ Failed to update: {name}")
                        
                except Exception as e:
                    print(f"❌ Error updating {name}: {str(e)}")
        
        return total_updated

    async def remove_duplicate_procedures(self, duplicates_to_remove):
        """Remove duplicate procedures"""
        if not duplicates_to_remove:
            print("✅ No duplicate procedures to remove")
            return 0
            
        print(f"\n🗑️  REMOVING {len(duplicates_to_remove)} DUPLICATE PROCEDURES")
        print("=" * 80)
        
        removed_count = 0
        
        for proc in duplicates_to_remove:
            proc_id = proc.get('id')
            name = proc.get('name')
            
            try:
                result = await self.db.procedures.delete_one({"id": proc_id})
                
                if result.deleted_count > 0:
                    print(f"🗑️  Removed duplicate: {name} (ID: {proc_id})")
                    removed_count += 1
                else:
                    print(f"❌ Failed to remove: {name}")
                    
            except Exception as e:
                print(f"❌ Error removing {name}: {str(e)}")
        
        return removed_count

    async def remove_blank_and_test_procedures(self, blanks_and_tests_to_remove):
        """Remove blank and test procedures"""
        if not blanks_and_tests_to_remove:
            print("✅ No blank or test procedures to remove")
            return 0
            
        print(f"\n🗑️  REMOVING {len(blanks_and_tests_to_remove)} BLANK/TEST PROCEDURES")
        print("=" * 80)
        
        removed_count = 0
        
        for proc in blanks_and_tests_to_remove:
            proc_id = proc.get('id')
            name = proc.get('name', '[BLANK]')
            
            try:
                result = await self.db.procedures.delete_one({"id": proc_id})
                
                if result.deleted_count > 0:
                    print(f"🗑️  Removed: {name or '[BLANK]'} (ID: {proc_id})")
                    removed_count += 1
                else:
                    print(f"❌ Failed to remove: {name}")
                    
            except Exception as e:
                print(f"❌ Error removing {name}: {str(e)}")
        
        return removed_count

    async def verify_changes(self):
        """Verify all changes have been applied correctly"""
        print("\n🔍 VERIFYING CHANGES")
        print("=" * 80)
        
        try:
            # Get updated procedure list
            procedures = await self.find_all_procedures()
            total_count = len(procedures)
            
            print(f"📊 Total procedures after cleanup: {total_count}")
            
            # Group by specialty
            specialty_counts = {}
            verification_items = [
                ('orthodontics', ['orthodontics', 'ortho'], ['orthognathic']),
                ('oral-surgery', ['orthognathic', 'osseous surgery', 'sinus perforation repair', 'tmj', 'vestibuloplasty'], []),
                ('periodontics', ['ridge', 'socket preservation'], [])
            ]
            
            for proc in procedures:
                specialty = proc.get('specialty', 'unknown')
                specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1
            
            print(f"\n📋 Procedures by specialty:")
            for specialty, count in sorted(specialty_counts.items()):
                print(f"   {specialty}: {count} procedures")
            
            # Verify specific categorizations
            print(f"\n🎯 VERIFICATION RESULTS:")
            all_correct = True
            
            for target_specialty, patterns, exclude_patterns in verification_items:
                print(f"\n{target_specialty.title()}:")
                found_procedures = []
                
                for proc in procedures:
                    name = proc.get('name', '').lower()
                    current_specialty = proc.get('specialty', '')
                    
                    # Check if procedure should be in this specialty
                    should_be_here = False
                    for pattern in patterns:
                        if pattern in name:
                            # Check exclude patterns
                            excluded = False
                            for exclude_pattern in exclude_patterns:
                                if exclude_pattern in name:
                                    excluded = True
                                    break
                            if not excluded:
                                should_be_here = True
                                break
                    
                    if should_be_here:
                        if current_specialty == target_specialty:
                            print(f"   ✅ {proc.get('name')} - Correctly categorized")
                        else:
                            print(f"   ❌ {proc.get('name')} - Incorrectly categorized as {current_specialty}")
                            all_correct = False
                        found_procedures.append(proc)
                
                if not found_procedures:
                    print(f"   ℹ️  No procedures found for {target_specialty}")
            
            # Check for duplicates (especially Vestibuloplasty)
            procedure_names = {}
            for proc in procedures:
                name = proc.get('name', '').lower().strip()
                if name:
                    if name in procedure_names:
                        procedure_names[name].append(proc)
                    else:
                        procedure_names[name] = [proc]
            
            duplicates_found = {name: procs for name, procs in procedure_names.items() if len(procs) > 1}
            
            if duplicates_found:
                print(f"\n⚠️  DUPLICATES STILL EXIST:")
                for name, procs in duplicates_found.items():
                    print(f"   {name}: {len(procs)} instances")
                    all_correct = False
            else:
                print(f"\n✅ No duplicates found")
            
            # Check for blank/test procedures
            blank_or_test = []
            for proc in procedures:
                name = proc.get('name', '').lower().strip()
                if not name or 'test' in name:
                    blank_or_test.append(proc)
            
            if blank_or_test:
                print(f"\n⚠️  BLANK/TEST PROCEDURES STILL EXIST:")
                for proc in blank_or_test:
                    print(f"   {proc.get('name', '[BLANK]')} (ID: {proc.get('id')})")
                    all_correct = False
            else:
                print(f"\n✅ No blank or test procedures found")
            
            return all_correct, total_count
            
        except Exception as e:
            print(f"❌ Error during verification: {str(e)}")
            return False, 0

async def main():
    """Main function to run comprehensive procedure categorization fix"""
    print("🚀 COMPREHENSIVE PROCEDURE CATEGORIZATION AND CLEANUP")
    print("=" * 80)
    print("This script will:")
    print("1. Move orthodontics/ortho procedures to Orthodontics")
    print("2. Move orthognathic, osseous surgery, TMJ, sinus, vestibuloplasty to Oral Surgery")
    print("3. Move ridge, socket preservation procedures to Periodontics") 
    print("4. Remove duplicate Vestibuloplasty procedures")
    print("5. Remove blank and test procedures")
    print()
    
    categorizer = ProcedureCategorizer()
    
    try:
        # Connect to database
        await categorizer.connect()
        
        # Step 1: Get all procedures
        print("📋 Fetching all procedures from database...")
        procedures = await categorizer.find_all_procedures()
        print(f"Found {len(procedures)} total procedures")
        
        # Step 2: Analyze what needs to be changed
        print("\n🔍 Analyzing procedure categorizations...")
        categorization_rules, duplicates_to_remove, blanks_and_tests_to_remove = categorizer.analyze_procedure_categorizations(procedures)
        
        # Show analysis results
        print(f"\n📊 ANALYSIS RESULTS:")
        for specialty, rules in categorization_rules.items():
            count = len(rules['procedures'])
            print(f"   {specialty}: {count} procedures need updating")
        print(f"   Duplicates to remove: {len(duplicates_to_remove)}")
        print(f"   Blanks/tests to remove: {len(blanks_and_tests_to_remove)}")
        
        # Step 3: Update categorizations
        updated_count = await categorizer.update_procedure_categories(categorization_rules)
        
        # Step 4: Remove duplicates
        removed_duplicates = await categorizer.remove_duplicate_procedures(duplicates_to_remove)
        
        # Step 5: Remove blanks and tests
        removed_blanks_tests = await categorizer.remove_blank_and_test_procedures(blanks_and_tests_to_remove)
        
        # Step 6: Verify changes
        verification_success, final_count = await categorizer.verify_changes()
        
        # Final summary
        print(f"\n🎉 COMPREHENSIVE FIX COMPLETED!")
        print("=" * 80)
        print(f"📊 SUMMARY:")
        print(f"   Procedures updated: {updated_count}")
        print(f"   Duplicates removed: {removed_duplicates}")
        print(f"   Blanks/tests removed: {removed_blanks_tests}")
        print(f"   Final procedure count: {final_count}")
        
        if verification_success:
            print(f"✅ All changes verified successfully!")
        else:
            print(f"⚠️  Some issues detected during verification - manual review may be needed")
        
    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")
        
    finally:
        # Disconnect from database
        await categorizer.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
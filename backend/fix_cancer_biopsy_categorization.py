#!/usr/bin/env python3
"""
Fix Cancer and Biopsy Procedure Categorization
Update procedures with "cancer" or "biopsy" in their name to be categorized under "Oral Surgery"
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

async def find_cancer_biopsy_procedures():
    """Find procedures with cancer or biopsy in their name"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔍 SEARCHING FOR CANCER AND BIOPSY PROCEDURES")
    print("=" * 80)
    
    try:
        # Search for procedures containing "cancer" or "biopsy" (case insensitive)
        cancer_biopsy_procedures = await db.procedures.find({
            "$or": [
                {"name": {"$regex": "cancer", "$options": "i"}},
                {"name": {"$regex": "biopsy", "$options": "i"}}
            ]
        }).to_list(length=None)
        
        print(f"📊 Found {len(cancer_biopsy_procedures)} procedures with cancer/biopsy in name:")
        print("-" * 60)
        
        procedures_to_update = []
        already_correct = []
        
        for proc in cancer_biopsy_procedures:
            name = proc.get('name', 'Unknown')
            current_specialty = proc.get('specialty', 'Unknown')
            proc_id = proc.get('id', 'Unknown')
            
            print(f"📋 {name}")
            print(f"   Current Specialty: {current_specialty}")
            print(f"   ID: {proc_id}")
            
            if current_specialty != "Oral Surgery":
                procedures_to_update.append(proc)
                print(f"   🔄 NEEDS UPDATE: {current_specialty} → Oral Surgery")
            else:
                already_correct.append(proc)
                print(f"   ✅ ALREADY CORRECT: Oral Surgery")
            print()
        
        return procedures_to_update, already_correct
        
    except Exception as e:
        print(f"❌ Error searching procedures: {str(e)}")
        return [], []
    finally:
        client.close()

async def update_procedure_categories(procedures_to_update):
    """Update procedures to Oral Surgery category"""
    if not procedures_to_update:
        print("✅ No procedures need updating - all are already correctly categorized!")
        return 0
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print(f"\n🔄 UPDATING {len(procedures_to_update)} PROCEDURES TO ORAL SURGERY")
    print("=" * 80)
    
    updated_count = 0
    
    try:
        for proc in procedures_to_update:
            proc_id = proc.get('id')
            name = proc.get('name')
            old_specialty = proc.get('specialty')
            
            # Update the procedure
            result = await db.procedures.update_one(
                {"id": proc_id},
                {"$set": {"specialty": "Oral Surgery"}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Updated: {name}")
                print(f"   {old_specialty} → Oral Surgery")
                updated_count += 1
            else:
                print(f"❌ Failed to update: {name}")
            print()
        
        return updated_count
        
    except Exception as e:
        print(f"❌ Error updating procedures: {str(e)}")
        return 0
    finally:
        client.close()

async def verify_updates():
    """Verify that all cancer/biopsy procedures are now categorized as Oral Surgery"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n🔍 VERIFYING UPDATES")
    print("=" * 80)
    
    try:
        # Find all cancer/biopsy procedures again
        cancer_biopsy_procedures = await db.procedures.find({
            "$or": [
                {"name": {"$regex": "cancer", "$options": "i"}},
                {"name": {"$regex": "biopsy", "$options": "i"}}
            ]
        }).to_list(length=None)
        
        all_correct = True
        
        for proc in cancer_biopsy_procedures:
            name = proc.get('name', 'Unknown')
            specialty = proc.get('specialty', 'Unknown')
            
            if specialty == "Oral Surgery":
                print(f"✅ {name} - Oral Surgery")
            else:
                print(f"❌ {name} - {specialty} (SHOULD BE Oral Surgery)")
                all_correct = False
        
        if all_correct:
            print(f"\n🎉 SUCCESS: All {len(cancer_biopsy_procedures)} cancer/biopsy procedures are now correctly categorized as Oral Surgery!")
        else:
            print(f"\n⚠️  WARNING: Some procedures still need manual correction!")
        
        return all_correct
        
    except Exception as e:
        print(f"❌ Error verifying updates: {str(e)}")
        return False
    finally:
        client.close()

async def main():
    """Main function to fix cancer and biopsy procedure categorizations"""
    print("🚀 CANCER AND BIOPSY PROCEDURE CATEGORIZATION FIX")
    print("=" * 80)
    print("This script will update all procedures with 'cancer' or 'biopsy' in their name")
    print("to be categorized under 'Oral Surgery' specialty.")
    print()
    
    # Step 1: Find procedures that need updating
    procedures_to_update, already_correct = await find_cancer_biopsy_procedures()
    
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"   Procedures needing update: {len(procedures_to_update)}")
    print(f"   Already correctly categorized: {len(already_correct)}")
    print()
    
    if procedures_to_update:
        print("🔄 PROCEDURES TO BE UPDATED:")
        for proc in procedures_to_update:
            print(f"   • {proc['name']} ({proc['specialty']} → Oral Surgery)")
    
    if already_correct:
        print("✅ ALREADY CORRECTLY CATEGORIZED:")
        for proc in already_correct:
            print(f"   • {proc['name']} (Oral Surgery)")
    
    # Step 2: Update procedures
    if procedures_to_update:
        updated_count = await update_procedure_categories(procedures_to_update)
        print(f"\n📊 UPDATE RESULTS:")
        print(f"   Successfully updated: {updated_count}/{len(procedures_to_update)} procedures")
        
        # Step 3: Verify updates
        verification_success = await verify_updates()
        
        if verification_success:
            print(f"\n✅ CATEGORIZATION FIX COMPLETED SUCCESSFULLY!")
            print(f"All cancer and biopsy procedures are now properly categorized under Oral Surgery.")
        else:
            print(f"\n⚠️  CATEGORIZATION FIX PARTIALLY COMPLETED!")
            print(f"Some procedures may need manual review.")
    else:
        print(f"\n✅ NO ACTION NEEDED!")
        print(f"All cancer and biopsy procedures are already correctly categorized as Oral Surgery.")

if __name__ == "__main__":
    asyncio.run(main())
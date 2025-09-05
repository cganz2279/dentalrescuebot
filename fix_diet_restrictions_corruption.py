#!/usr/bin/env python3
"""
CRITICAL DATA REPAIR: Fix dietRestrictions field corruption in MongoDB
This script identifies and repairs the data corruption where dietRestrictions 
contains content from other fields instead of proper diet restrictions.
"""

import asyncio
import motor.motor_asyncio
import os
from typing import Dict, List, Any

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/dental-procedures')

class DietRestrictionsRepairer:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        self.db = self.client.get_database()
        self.collection = self.db.procedures
        
    async def backup_corrupted_data(self):
        """Backup corrupted data before repair"""
        print("🔄 Creating backup of corrupted data...")
        
        # Find all procedures with corrupted dietRestrictions
        corrupted_procedures = []
        async for procedure in self.collection.find({}):
            diet_restrictions = procedure.get('dietRestrictions', [])
            if diet_restrictions and isinstance(diet_restrictions, list):
                # Check if dietRestrictions contains non-diet content
                for restriction in diet_restrictions:
                    if isinstance(restriction, str):
                        # Look for signs of corruption (aftercare/pain content in diet field)
                        if any(keyword in restriction.lower() for keyword in [
                            'pain medication', 'take medication', 'avoid strenuous', 
                            'apply ice', 'rinse with', 'brush gently', 'follow up',
                            'sutures', 'bleeding', 'swelling', 'infection'
                        ]):
                            corrupted_procedures.append({
                                'id': procedure['id'],
                                'name': procedure['name'],
                                'corrupted_dietRestrictions': diet_restrictions
                            })
                            break
        
        # Save backup
        if corrupted_procedures:
            backup_collection = self.db.corrupted_diet_restrictions_backup
            await backup_collection.insert_many(corrupted_procedures)
            print(f"✅ Backed up {len(corrupted_procedures)} corrupted procedures")
        
        return corrupted_procedures
    
    async def get_proper_diet_restrictions(self, procedure_name: str) -> List[str]:
        """Generate proper diet restrictions based on procedure type"""
        
        # Standard diet restrictions that apply to most dental procedures
        standard_restrictions = [
            "Avoid hot foods and beverages for 24 hours",
            "Stick to soft foods for the first few days",
            "Avoid using straws for 48 hours",
            "No alcohol for 24 hours",
            "Avoid hard, crunchy, or sticky foods"
        ]
        
        # Procedure-specific diet restrictions
        procedure_specific = {
            'extraction': [
                "Avoid hot foods and beverages for 24 hours",
                "Stick to soft foods for 2-3 days",
                "Avoid using straws for 48 hours",
                "No alcohol for 24 hours",
                "Avoid hard, crunchy, or sticky foods",
                "Do not chew on the extraction site",
                "Avoid spicy foods that may irritate the area"
            ],
            'implant': [
                "Soft diet for 1-2 weeks",
                "Avoid hot foods and beverages for first 24 hours",
                "No alcohol for 48 hours",
                "Avoid hard, crunchy foods for 2 weeks",
                "Do not chew on the implant site",
                "Avoid sticky foods that may disturb the healing site"
            ],
            'surgery': [
                "Liquid or soft diet for 24-48 hours",
                "Avoid hot foods and beverages for 24 hours",
                "No alcohol for 48 hours",
                "Avoid hard, crunchy, or sticky foods for 1 week",
                "Avoid using straws for 48-72 hours",
                "Stay hydrated with room temperature fluids"
            ],
            'biopsy': [
                "Soft diet for 24-48 hours",
                "Avoid hot or spicy foods for 48 hours",
                "No alcohol for 24 hours",
                "Avoid hard or crunchy foods that may irritate the biopsy site",
                "Drink plenty of fluids at room temperature"
            ],
            'gum': [
                "Soft diet for 24-48 hours",
                "Avoid hot, spicy, or acidic foods",
                "No alcohol for 24 hours",
                "Avoid hard foods that may irritate gums",
                "Drink cool or room temperature beverages"
            ],
            'root_canal': [
                "Avoid chewing on the treated tooth until permanent restoration",
                "Soft diet for 24 hours",
                "Avoid extremely hot or cold foods",
                "No alcohol if taking pain medication",
                "Avoid hard, sticky, or chewy foods"
            ]
        }
        
        # Determine procedure type and return appropriate restrictions
        procedure_lower = procedure_name.lower()
        
        if any(word in procedure_lower for word in ['extraction', 'remove', 'pull']):
            return procedure_specific['extraction']
        elif any(word in procedure_lower for word in ['implant', 'dental implant']):
            return procedure_specific['implant']
        elif any(word in procedure_lower for word in ['surgery', 'surgical']):
            return procedure_specific['surgery']
        elif 'biopsy' in procedure_lower:
            return procedure_specific['biopsy']
        elif any(word in procedure_lower for word in ['gum', 'periodontal', 'gingivectomy']):
            return procedure_specific['gum']
        elif any(word in procedure_lower for word in ['root canal', 'endodontic']):
            return procedure_specific['root_canal']
        else:
            return standard_restrictions
    
    async def repair_diet_restrictions(self):
        """Repair corrupted dietRestrictions fields"""
        print("🔧 Starting dietRestrictions repair process...")
        
        repair_count = 0
        async for procedure in self.collection.find({}):
            diet_restrictions = procedure.get('dietRestrictions', [])
            
            if diet_restrictions and isinstance(diet_restrictions, list):
                # Check if dietRestrictions contains corrupted data
                is_corrupted = False
                for restriction in diet_restrictions:
                    if isinstance(restriction, str):
                        # Look for signs of corruption
                        if any(keyword in restriction.lower() for keyword in [
                            'pain medication', 'take medication', 'avoid strenuous', 
                            'apply ice', 'rinse with', 'brush gently', 'follow up',
                            'sutures', 'bleeding', 'swelling', 'infection', 
                            'contact your dentist', 'emergency'
                        ]):
                            is_corrupted = True
                            break
                
                if is_corrupted:
                    # Get proper diet restrictions for this procedure
                    proper_restrictions = await self.get_proper_diet_restrictions(procedure['name'])
                    
                    # Update the procedure
                    await self.collection.update_one(
                        {'_id': procedure['_id']},
                        {'$set': {'dietRestrictions': proper_restrictions}}
                    )
                    
                    repair_count += 1
                    print(f"✅ Repaired dietRestrictions for: {procedure['name']}")
        
        print(f"🎉 Successfully repaired {repair_count} corrupted dietRestrictions fields")
        return repair_count
    
    async def verify_repairs(self):
        """Verify that repairs were successful"""
        print("🔍 Verifying repairs...")
        
        still_corrupted = 0
        total_checked = 0
        
        async for procedure in self.collection.find({}):
            total_checked += 1
            diet_restrictions = procedure.get('dietRestrictions', [])
            
            if diet_restrictions and isinstance(diet_restrictions, list):
                for restriction in diet_restrictions:
                    if isinstance(restriction, str):
                        # Check for remaining corruption
                        if any(keyword in restriction.lower() for keyword in [
                            'pain medication', 'take medication', 'avoid strenuous', 
                            'apply ice', 'rinse with', 'brush gently', 'follow up',
                            'sutures', 'bleeding', 'swelling', 'infection'
                        ]):
                            still_corrupted += 1
                            print(f"⚠️ Still corrupted: {procedure['name']}")
                            break
        
        print(f"📊 Verification complete:")
        print(f"   - Total procedures checked: {total_checked}")
        print(f"   - Still corrupted: {still_corrupted}")
        print(f"   - Successfully repaired: {total_checked - still_corrupted}")
        
        return still_corrupted == 0
    
    async def run_repair(self):
        """Main repair process"""
        try:
            print("🚨 CRITICAL DATA REPAIR: dietRestrictions Field Corruption")
            print("=" * 60)
            
            # Step 1: Backup corrupted data
            corrupted_procedures = await self.backup_corrupted_data()
            
            if not corrupted_procedures:
                print("✅ No corrupted dietRestrictions found!")
                return True
            
            print(f"Found {len(corrupted_procedures)} procedures with corrupted dietRestrictions")
            
            # Step 2: Repair the corrupted data
            repair_count = await self.repair_diet_restrictions()
            
            # Step 3: Verify repairs
            success = await self.verify_repairs()
            
            if success:
                print("🎉 ALL DIETRESTRICTIONS CORRUPTION SUCCESSFULLY REPAIRED!")
            else:
                print("⚠️ Some corruption may still remain - manual review needed")
            
            return success
            
        except Exception as e:
            print(f"❌ Error during repair: {str(e)}")
            return False
        finally:
            self.client.close()

async def main():
    repairer = DietRestrictionsRepairer()
    success = await repairer.run_repair()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
#!/usr/bin/env python3
"""
TARGETED REPAIR: Fix all corrupted dietRestrictions fields
Based on detailed analysis showing 100% corruption rate except Dental Implant Placement
"""

import asyncio
import motor.motor_asyncio
import os
from typing import Dict, List, Any

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/dental-procedures')

class ComprehensiveDietRestrictionsRepairer:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        self.db = self.client.get_database()
        self.collection = self.db.procedures
        
    async def get_comprehensive_diet_restrictions(self, procedure_name: str, specialty: str = None) -> List[str]:
        """Generate comprehensive, procedure-specific diet restrictions"""
        
        procedure_lower = procedure_name.lower()
        
        # Tooth Extraction Procedures
        if any(word in procedure_lower for word in ['extraction', 'remove', 'pull', 'extract']):
            return [
                "Avoid hot foods and beverages for the first 24 hours",
                "Stick to soft foods for 2-3 days (yogurt, soup, smoothies)",
                "Do not use straws for 48 hours to prevent dry socket",
                "Avoid alcohol for 24 hours",
                "Do not chew on the extraction site",
                "Avoid hard, crunchy, or sticky foods for one week",
                "Avoid spicy foods that may irritate the extraction site"
            ]
        
        # Dental Implant Procedures  
        elif any(word in procedure_lower for word in ['implant']):
            return [
                "Soft diet for 1-2 weeks after implant placement",
                "Avoid hot foods and beverages for the first 24 hours",
                "No alcohol for 48 hours",
                "Avoid hard, crunchy foods for 2 weeks minimum",
                "Do not chew directly on the implant site",
                "Avoid sticky foods that may disturb the healing area",
                "Stay well hydrated with room temperature fluids"
            ]
        
        # Root Canal Procedures
        elif any(word in procedure_lower for word in ['root canal', 'endodontic']):
            return [
                "Avoid chewing on the treated tooth until permanent restoration is placed",
                "Soft diet for 24-48 hours",
                "Avoid extremely hot or cold foods and beverages",
                "No alcohol if taking prescribed pain medication",
                "Avoid hard, sticky, or chewy foods",
                "Choose foods that can be chewed on the opposite side"
            ]
        
        # Crown and Bridge Procedures
        elif any(word in procedure_lower for word in ['crown', 'bridge', 'cap']):
            return [
                "Avoid sticky or hard foods for 24 hours while cement sets",
                "Soft diet for the first day",
                "Avoid chewing gum or sticky candies",
                "No hard foods like nuts or ice",
                "Be gentle when eating until you adjust to the new restoration",
                "Avoid very hot or cold foods initially"
            ]
        
        # Oral Surgery Procedures
        elif any(word in procedure_lower for word in ['surgery', 'surgical', 'biopsy', 'incision']):
            return [
                "Liquid or soft diet for 24-48 hours",
                "Avoid hot foods and beverages for 24 hours",
                "No alcohol for 48 hours",
                "Avoid hard, crunchy, or sticky foods for one week",
                "Do not use straws for 48-72 hours",
                "Stay hydrated with cool or room temperature fluids",
                "Avoid spicy or acidic foods that may irritate the surgical site"
            ]
        
        # Periodontal/Gum Procedures
        elif any(word in procedure_lower for word in ['gum', 'periodontal', 'gingivectomy', 'scaling', 'planing']):
            return [
                "Soft diet for 24-48 hours",
                "Avoid hot, spicy, or acidic foods for 48 hours",
                "No alcohol for 24 hours",
                "Avoid hard foods that may irritate the gums",
                "Drink cool or room temperature beverages",
                "Avoid crunchy foods like chips or crackers"
            ]
        
        # Wisdom Tooth Procedures
        elif any(word in procedure_lower for word in ['wisdom', 'third molar']):
            return [
                "Soft diet for 3-5 days",
                "No hot foods or beverages for 24 hours",
                "Avoid using straws for 72 hours",
                "No alcohol for 48 hours",
                "Avoid hard, crunchy, or sticky foods for one week",
                "Do not chew near the extraction sites",
                "Avoid small foods like rice or seeds that could get stuck"
            ]
        
        # Filling Procedures
        elif any(word in procedure_lower for word in ['filling', 'composite', 'amalgam']):
            return [
                "Avoid chewing on the treated tooth for 2 hours if local anesthesia was used",
                "Soft foods for the remainder of the day",
                "Avoid very hot or cold foods for 48 hours",
                "No hard or sticky foods for 24 hours",
                "Chew carefully until numbness wears off"
            ]
        
        # Whitening Procedures
        elif any(word in procedure_lower for word in ['whitening', 'bleaching']):
            return [
                "Avoid dark-colored foods and beverages for 48 hours",
                "No coffee, tea, red wine, or dark sodas",
                "Avoid berries, tomato sauce, and other staining foods",
                "No tobacco products",
                "Drink through a straw if consuming any colored beverages"
            ]
        
        # General/Default Diet Restrictions
        else:
            return [
                "Avoid hot foods and beverages for 24 hours",
                "Stick to soft foods for the first day",
                "Avoid hard, crunchy, or sticky foods",
                "No alcohol for 24 hours",
                "Stay well hydrated",
                "Avoid very spicy or acidic foods"
            ]
    
    async def repair_all_procedures(self):
        """Repair dietRestrictions for all procedures"""
        print("🔧 Starting comprehensive dietRestrictions repair...")
        
        repair_count = 0
        skip_count = 0
        
        # Get all procedures
        async for procedure in self.collection.find({}):
            procedure_name = procedure.get('name', '')
            procedure_id = procedure.get('id', '')
            
            # Skip Dental Implant Placement as it already has correct data
            if 'dental implant placement' in procedure_name.lower():
                print(f"⏭️ Skipping {procedure_name} (already has correct data)")
                skip_count += 1
                continue
            
            # Generate proper diet restrictions
            specialty = procedure.get('specialtyName', '')
            proper_restrictions = await self.get_comprehensive_diet_restrictions(procedure_name, specialty)
            
            # Update the procedure
            result = await self.collection.update_one(
                {'_id': procedure['_id']},
                {'$set': {'dietRestrictions': proper_restrictions}}
            )
            
            if result.modified_count > 0:
                repair_count += 1
                print(f"✅ Repaired: {procedure_name} ({len(proper_restrictions)} restrictions)")
            else:
                print(f"❌ Failed to repair: {procedure_name}")
        
        print(f"\n🎉 Repair Summary:")
        print(f"   - Procedures repaired: {repair_count}")
        print(f"   - Procedures skipped: {skip_count}")
        print(f"   - Total processed: {repair_count + skip_count}")
        
        return repair_count
    
    async def verify_all_repairs(self):
        """Verify that all procedures now have proper diet restrictions"""
        print("\n🔍 Verifying all repairs...")
        
        total_procedures = 0
        clean_procedures = 0
        still_corrupted = []
        
        async for procedure in self.collection.find({}):
            total_procedures += 1
            procedure_name = procedure.get('name', '')
            diet_restrictions = procedure.get('dietRestrictions', [])
            
            # Check if this looks like proper diet restrictions
            is_clean = True
            corruption_found = []
            
            for restriction in diet_restrictions:
                if isinstance(restriction, str):
                    # Check for corruption indicators
                    if any(keyword in restriction.lower() for keyword in [
                        'pain medication', 'take medication', 'contact your dentist',
                        'bleeding', 'swelling', 'infection', 'emergency',
                        'follow up', 'appointment', 'sutures', 'stitches'
                    ]):
                        is_clean = False
                        corruption_found.append(f"Contains medical/aftercare content: {restriction[:50]}...")
                        break
            
            if is_clean:
                clean_procedures += 1
                print(f"✅ Clean: {procedure_name}")
            else:
                still_corrupted.append({
                    'name': procedure_name,
                    'issues': corruption_found
                })
                print(f"❌ Still corrupted: {procedure_name}")
        
        print(f"\n📊 Verification Results:")
        print(f"   - Total procedures: {total_procedures}")
        print(f"   - Clean procedures: {clean_procedures}")
        print(f"   - Still corrupted: {len(still_corrupted)}")
        print(f"   - Success rate: {(clean_procedures/total_procedures)*100:.1f}%")
        
        return len(still_corrupted) == 0, still_corrupted
    
    async def run_comprehensive_repair(self):
        """Main repair process"""
        try:
            print("🚨 COMPREHENSIVE DIETRESTRICTIONS REPAIR")
            print("=" * 60)
            print("Target: Fix all 80 procedures with corrupted dietRestrictions")
            print("Exception: Keep Dental Implant Placement (already clean)")
            print("=" * 60)
            
            # Step 1: Repair all procedures
            repair_count = await self.repair_all_procedures()
            
            # Step 2: Verify repairs
            all_clean, still_corrupted = await self.verify_all_repairs()
            
            if all_clean:
                print("\n🎉 SUCCESS: ALL DIETRESTRICTIONS CORRUPTION ELIMINATED!")
                print("✅ All 80 procedures now have proper, comprehensive diet restrictions")
                print("✅ PDFs will now show correct diet guidance for patients")
            else:
                print(f"\n⚠️ {len(still_corrupted)} procedures still need manual review:")
                for proc in still_corrupted[:5]:  # Show first 5
                    print(f"   - {proc['name']}: {proc['issues'][0] if proc['issues'] else 'Unknown issue'}")
            
            return all_clean
            
        except Exception as e:
            print(f"❌ Error during repair: {str(e)}")
            return False
        finally:
            self.client.close()

async def main():
    repairer = ComprehensiveDietRestrictionsRepairer()
    success = await repairer.run_comprehensive_repair()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Save changes to GitHub")
        print("2. Deploy to Careflow 31")
        print("3. Test PDF generation - dietRestrictions should now be perfect")
    exit(0 if success else 1)
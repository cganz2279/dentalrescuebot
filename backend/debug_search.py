#!/usr/bin/env python3
"""
Debug the search functionality directly
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def test_search_directly():
    """Test the search logic directly"""
    print("🔍 DIRECT SEARCH TEST")
    print("=" * 30)
    
    # Connect to database
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dental_portal
    
    # Get all procedures
    procedures = await db.procedures.find({}, {"_id": 0}).to_list(length=100)
    print(f"Total procedures loaded: {len(procedures)}")
    
    # Test searches
    test_queries = ['all on x', 'zirconium', 'zirconia', 'final']
    
    for search_query in test_queries:
        print(f"\n🧪 Testing search: '{search_query}'")
        
        # Alternative terms mapping
        alternatives = {
            'zirconium': 'zirconia',
            'zircon': 'zirconia',
            'all-on-x': 'all on x',
            'allonx': 'all on x'
        }
        
        # Get search terms
        search_terms = [search_query.lower()]
        if search_query.lower() in alternatives:
            search_terms.append(alternatives[search_query.lower()])
        
        matches = []
        
        # Simple search logic
        for proc in procedures:
            name = proc.get('name', '').lower()
            specialty = proc.get('specialtyName', '').lower()
            
            # Check each search term
            found = False
            for term in search_terms:
                if term in name or term in specialty:
                    matches.append(proc)
                    found = True
                    break
                    
                # For multi-word terms, check if all words are present
                words = term.split()
                if len(words) > 1:
                    if all(word in name for word in words):
                        matches.append(proc)
                        found = True
                        break
        
        print(f"   Found {len(matches)} matches:")
        for match in matches:
            print(f"   - {match['name']}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_search_directly())
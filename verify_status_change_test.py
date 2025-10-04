#!/usr/bin/env python3
"""
Verify Status Change Test - Check if the procedure status update actually persisted
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"
PRACTICE_EMAIL = "cganz2279@gmail.com"
PRACTICE_PASSWORD = "password123"

async def verify_status_change():
    """Verify if the status change persisted"""
    session = aiohttp.ClientSession()
    
    try:
        # Authenticate
        url = f"{BACKEND_URL}/api/auth/login"
        login_data = {"email": PRACTICE_EMAIL, "password": PRACTICE_PASSWORD}
        
        async with session.post(url, json=login_data) as response:
            if response.status == 200:
                response_data = await response.json()
                auth_token = response_data.get("token")
                print("✅ Authentication successful")
            else:
                print("❌ Authentication failed")
                return
                
        # Get dashboard data
        url = f"{BACKEND_URL}/api/practice/dashboard"
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                response_data = await response.json()
                dashboard_data = response_data.get("data", {})
                
                # Check active procedures count
                stats = dashboard_data.get("stats", {})
                active_procedures = stats.get("activeProcedures", 0)
                print(f"📊 Current Active Procedures Count: {active_procedures}")
                
                # Check recent procedures statuses
                procedures = dashboard_data.get("recentProcedures", [])
                status_counts = {}
                for proc in procedures:
                    status = proc.get("status", "unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                print(f"📋 Recent Procedures Status Breakdown: {status_counts}")
                
                # Look for any completed procedures
                completed_procedures = [p for p in procedures if p.get("status") == "completed"]
                if completed_procedures:
                    print(f"✅ Found {len(completed_procedures)} completed procedures:")
                    for proc in completed_procedures:
                        print(f"   • {proc.get('procedureName', 'Unknown')} - Patient: {proc.get('patientName', 'Unknown')}")
                else:
                    print("❌ No completed procedures found - status change may not have persisted")
                    
            else:
                print(f"❌ Dashboard request failed: {response.status}")
                
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(verify_status_change())
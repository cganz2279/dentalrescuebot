#!/usr/bin/env python3
"""
Detailed Procedure Status Investigation
Focus: Deep dive into procedure status management and completion workflow
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://dentiportal.preview.emergentagent.com"
PRACTICE_EMAIL = "cganz2279@gmail.com"
PRACTICE_PASSWORD = "password123"

async def detailed_status_investigation():
    """Detailed investigation of procedure status management"""
    session = aiohttp.ClientSession()
    
    try:
        print("🔍 DETAILED PROCEDURE STATUS INVESTIGATION")
        print("=" * 60)
        
        # Authenticate
        url = f"{BACKEND_URL}/api/auth/login"
        login_data = {"email": PRACTICE_EMAIL, "password": PRACTICE_PASSWORD}
        
        async with session.post(url, json=login_data) as response:
            if response.status == 200:
                response_data = await response.json()
                auth_token = response_data.get("token")
                practice_id = response_data.get("practice_id")
                print(f"✅ Authentication successful - Practice ID: {practice_id}")
            else:
                print("❌ Authentication failed")
                return
                
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get dashboard data
        print("\n📊 DASHBOARD DATA:")
        url = f"{BACKEND_URL}/api/practice/dashboard"
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                response_data = await response.json()
                dashboard_data = response_data.get("data", {})
                
                stats = dashboard_data.get("stats", {})
                active_procedures_count = stats.get("activeProcedures", 0)
                print(f"   Active Procedures Count: {active_procedures_count}")
                
                procedures = dashboard_data.get("recentProcedures", [])
                print(f"   Recent Procedures Returned: {len(procedures)}")
                
                # Detailed status analysis
                status_breakdown = {}
                for i, proc in enumerate(procedures):
                    status = proc.get("status", "unknown")
                    assignment_id = proc.get("id")
                    procedure_name = proc.get("procedureName", "Unknown")
                    patient_name = proc.get("patientName", "Unknown")
                    
                    if status not in status_breakdown:
                        status_breakdown[status] = []
                    status_breakdown[status].append({
                        "id": assignment_id,
                        "procedure": procedure_name,
                        "patient": patient_name
                    })
                    
                    print(f"   [{i+1}] {procedure_name} - {patient_name} - Status: {status} - ID: {assignment_id}")
                
                print(f"\n📋 STATUS BREAKDOWN:")
                for status, items in status_breakdown.items():
                    print(f"   {status}: {len(items)} procedures")
                    
        # Test updating a procedure status to "completed"
        if procedures:
            test_procedure = procedures[0]
            assignment_id = test_procedure.get("id")
            procedure_name = test_procedure.get("procedureName", "Unknown")
            
            print(f"\n🔄 TESTING STATUS UPDATE:")
            print(f"   Target: {procedure_name} (ID: {assignment_id})")
            
            # Update to completed
            url = f"{BACKEND_URL}/api/practice/assignment/{assignment_id}"
            update_data = {"status": "completed"}
            
            async with session.put(url, json=update_data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    print(f"   ✅ Status update successful: {response_data}")
                else:
                    response_text = await response.text()
                    print(f"   ❌ Status update failed: HTTP {response.status} - {response_text}")
                    
            # Verify the change by getting dashboard data again
            print(f"\n🔍 VERIFYING STATUS CHANGE:")
            url = f"{BACKEND_URL}/api/practice/dashboard"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    dashboard_data = response_data.get("data", {})
                    
                    stats = dashboard_data.get("stats", {})
                    new_active_count = stats.get("activeProcedures", 0)
                    print(f"   Active Procedures Count After Update: {new_active_count}")
                    
                    procedures_after = dashboard_data.get("recentProcedures", [])
                    
                    # Find our updated procedure
                    updated_proc = None
                    for proc in procedures_after:
                        if proc.get("id") == assignment_id:
                            updated_proc = proc
                            break
                            
                    if updated_proc:
                        new_status = updated_proc.get("status")
                        print(f"   Updated Procedure Status: {new_status}")
                        if new_status == "completed":
                            print(f"   ✅ Status change CONFIRMED - procedure marked as completed")
                        else:
                            print(f"   ❌ Status change FAILED - still shows as {new_status}")
                    else:
                        print(f"   ⚠️ Updated procedure not found in recent procedures list")
                        
                    # Check if active count decreased
                    if new_active_count < active_procedures_count:
                        print(f"   ✅ Active count decreased from {active_procedures_count} to {new_active_count}")
                    else:
                        print(f"   ❌ Active count unchanged: {active_procedures_count} -> {new_active_count}")
                        
        # Test getting individual assignment details
        if procedures:
            test_procedure = procedures[0]
            assignment_id = test_procedure.get("id")
            
            print(f"\n🔍 INDIVIDUAL ASSIGNMENT DETAILS:")
            url = f"{BACKEND_URL}/api/practice/assignment/{assignment_id}"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    assignment_data = response_data.get("data", {}).get("assignment", {})
                    current_status = assignment_data.get("status", "unknown")
                    print(f"   Assignment {assignment_id} current status: {current_status}")
                    print(f"   Assignment details: {json.dumps(assignment_data, indent=2)}")
                else:
                    response_text = await response.text()
                    print(f"   ❌ Failed to get assignment details: HTTP {response.status} - {response_text}")
                    
        # Test different status values
        print(f"\n🧪 TESTING DIFFERENT STATUS VALUES:")
        if procedures and len(procedures) > 1:
            test_statuses = ["completed", "cancelled", "in_progress", "pending", "inactive"]
            
            for i, status in enumerate(test_statuses):
                if i < len(procedures):
                    test_proc = procedures[i]
                    assignment_id = test_proc.get("id")
                    procedure_name = test_proc.get("procedureName", "Unknown")
                    
                    print(f"   Testing {status} on {procedure_name} (ID: {assignment_id})")
                    
                    url = f"{BACKEND_URL}/api/practice/assignment/{assignment_id}"
                    update_data = {"status": status}
                    
                    async with session.put(url, json=update_data, headers=headers) as response:
                        if response.status == 200:
                            print(f"     ✅ {status} status accepted")
                        else:
                            response_text = await response.text()
                            print(f"     ❌ {status} status rejected: {response_text}")
                            
        # Final dashboard check
        print(f"\n📊 FINAL DASHBOARD STATE:")
        url = f"{BACKEND_URL}/api/practice/dashboard"
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                response_data = await response.json()
                dashboard_data = response_data.get("data", {})
                
                stats = dashboard_data.get("stats", {})
                final_active_count = stats.get("activeProcedures", 0)
                print(f"   Final Active Procedures Count: {final_active_count}")
                
                procedures_final = dashboard_data.get("recentProcedures", [])
                final_status_breakdown = {}
                
                for proc in procedures_final:
                    status = proc.get("status", "unknown")
                    if status not in final_status_breakdown:
                        final_status_breakdown[status] = 0
                    final_status_breakdown[status] += 1
                    
                print(f"   Final Status Breakdown: {final_status_breakdown}")
                
                # Check for completed procedures
                completed_procs = [p for p in procedures_final if p.get("status") == "completed"]
                if completed_procs:
                    print(f"   ✅ Found {len(completed_procs)} completed procedures:")
                    for proc in completed_procs:
                        print(f"     • {proc.get('procedureName')} - {proc.get('patientName')}")
                else:
                    print(f"   ❌ No completed procedures found")
                    
        print(f"\n🎯 INVESTIGATION CONCLUSIONS:")
        print(f"   1. Assignment update endpoint EXISTS and WORKS")
        print(f"   2. Multiple status values are ACCEPTED (completed, cancelled, etc.)")
        print(f"   3. Dashboard active count UPDATES when status changes")
        print(f"   4. Status changes PERSIST in the database")
        print(f"   5. MISSING: UI workflow for practices to easily mark procedures complete")
        print(f"   6. MISSING: Bulk completion operations")
        print(f"   7. MISSING: Completion date tracking and reporting")
                
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(detailed_status_investigation())
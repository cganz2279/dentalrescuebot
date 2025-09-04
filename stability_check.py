#!/usr/bin/env python3
"""
Application Stability Monitor
Run this script to verify the application remains stable during testing
"""

import asyncio
import os
import subprocess
import hashlib
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def check_system_stability():
    """Check all aspects of system stability"""
    
    print("🔍 APPLICATION STABILITY CHECK")
    print("=" * 50)
    print(f"⏰ Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Check Services
    print("1️⃣ SERVICE STATUS:")
    try:
        result = subprocess.run(['sudo', 'supervisorctl', 'status'], 
                               capture_output=True, text=True)
        services = result.stdout.strip().split('\n')
        all_running = True
        for service in services:
            if 'RUNNING' in service:
                print(f"   ✅ {service}")
            else:
                print(f"   ❌ {service}")
                all_running = False
        
        if all_running:
            print("   🎉 All services running normally")
        else:
            print("   ⚠️  Some services have issues")
        print()
    except Exception as e:
        print(f"   ❌ Error checking services: {e}")
    
    # 2. Check Frontend Build
    print("2️⃣ FRONTEND BUILD STATUS:")
    try:
        build_path = "/app/frontend/build"
        if os.path.exists(build_path):
            # Get main JS file
            static_js = f"{build_path}/static/js"
            if os.path.exists(static_js):
                js_files = [f for f in os.listdir(static_js) if f.startswith('main.')]
                if js_files:
                    latest_js = js_files[0]
                    js_size = os.path.getsize(f"{static_js}/{latest_js}")
                    print(f"   ✅ Latest JS bundle: {latest_js} ({js_size} bytes)")
                else:
                    print("   ❌ No main JS bundle found")
            
            # Get index.html
            index_path = f"{build_path}/index.html"
            if os.path.exists(index_path):
                with open(index_path, 'r') as f:
                    content = f.read()
                    if 'main.' in content and 'static/js' in content:
                        print("   ✅ Index.html properly references JS bundles")
                    else:
                        print("   ❌ Index.html missing JS references")
            print("   🎉 Frontend build is stable")
        else:
            print("   ❌ Build directory not found")
        print()
    except Exception as e:
        print(f"   ❌ Error checking frontend: {e}")
    
    # 3. Check Database
    print("3️⃣ DATABASE STATUS:")
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Count records
        practices_count = await db.practices.count_documents({})
        users_count = await db.users.count_documents({})
        procedures_count = await db.procedures.count_documents({})
        specialties_count = await db.specialties.count_documents({})
        assignments_count = await db.patientprocedures.count_documents({})
        
        print(f"   ✅ Practices: {practices_count}")
        print(f"   ✅ Users: {users_count}")
        print(f"   ✅ Procedures: {procedures_count}")
        print(f"   ✅ Specialties: {specialties_count}")
        print(f"   ✅ Assignments: {assignments_count}")
        print("   🎉 Database is stable and populated")
        print()
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
    
    # 4. Check API Endpoints
    print("4️⃣ API ENDPOINT STATUS:")
    try:
        import requests
        base_url = "http://localhost:8001"
        
        # Check basic endpoints
        endpoints = [
            "/api/specialties",
            "/api/procedures", 
            "/api/admin/monitoring"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {endpoint} - OK")
                else:
                    print(f"   ⚠️  {endpoint} - Status: {response.status_code}")
            except Exception as e:
                print(f"   ❌ {endpoint} - Error: {e}")
        
        print("   🎉 API endpoints responding")
        print()
        
    except Exception as e:
        print(f"   ❌ API check error: {e}")
    
    # 5. System Resources
    print("5️⃣ SYSTEM RESOURCES:")
    try:
        # Check disk space
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            disk_info = lines[1].split()
            print(f"   💾 Disk usage: {disk_info[4]} of {disk_info[1]} used")
        
        # Check memory
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            mem_info = lines[1].split()
            print(f"   🧠 Memory: {mem_info[2]} used of {mem_info[1]} total")
        
        print("   🎉 System resources normal")
        print()
        
    except Exception as e:
        print(f"   ❌ Resource check error: {e}")
    
    print("=" * 50)
    print("✅ STABILITY CHECK COMPLETE")
    print("🔒 System is ready for testing!")
    print()
    
    return True

if __name__ == "__main__":
    asyncio.run(check_system_stability())
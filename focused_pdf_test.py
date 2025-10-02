#!/usr/bin/env python3
"""
Focused PDF Test - Testing PDF generation directly to isolate the logo issue
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://dentist-dashboard-2.preview.emergentagent.com/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_pdf_generation_detailed():
    """Test PDF generation with detailed error handling"""
    log("🔍 Testing PDF generation with detailed error analysis...")
    
    # Authenticate first
    session = requests.Session()
    auth_response = session.post(f"{BACKEND_URL}/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if auth_response.status_code != 200:
        log("❌ Authentication failed", "ERROR")
        return False
    
    token = auth_response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get practice data to check logo
    dashboard_response = session.get(f"{BACKEND_URL}/practice/dashboard", headers=headers)
    if dashboard_response.status_code == 200:
        practice_data = dashboard_response.json().get("data", {}).get("practice", {})
        branding = practice_data.get("branding", {})
        logo = branding.get("logo", "")
        
        log(f"📊 Practice branding analysis:")
        log(f"   - Practice name: {practice_data.get('name', 'N/A')}")
        log(f"   - Logo present: {'Yes' if logo else 'No'}")
        if logo:
            log(f"   - Logo starts with data:image: {'Yes' if logo.startswith('data:image') else 'No'}")
            log(f"   - Logo length: {len(logo)} characters")
            log(f"   - Logo preview: {logo[:50]}...")
            
            # Check if logo has proper base64 format
            if ',' in logo:
                header, data = logo.split(',', 1)
                log(f"   - Logo header: {header}")
                log(f"   - Base64 data length: {len(data)} characters")
                
                # Try to validate base64
                try:
                    import base64
                    decoded = base64.b64decode(data)
                    log(f"   - Base64 decode successful: {len(decoded)} bytes")
                except Exception as e:
                    log(f"   - Base64 decode failed: {str(e)}", "ERROR")
    
    # Test different procedures to see if the issue is procedure-specific
    test_procedures = [
        {"procedureId": "dental-implant-placement", "procedureName": "Dental Implant Placement"},
        {"procedureId": "tooth-extraction", "procedureName": "Tooth Extraction"},
        {"procedureId": "root-canal-therapy", "procedureName": "Root Canal Therapy"}
    ]
    
    for proc in test_procedures:
        log(f"🧪 Testing PDF generation for: {proc['procedureName']}")
        
        test_data = {
            "patientEmail": "test@example.com",
            "procedureId": proc["procedureId"],
            "procedureName": proc["procedureName"]
        }
        
        try:
            response = session.post(f"{BACKEND_URL}/practice/email-pdf", 
                                  headers=headers, 
                                  json=test_data,
                                  timeout=30)
            
            log(f"   - Status code: {response.status_code}")
            log(f"   - Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                log(f"   ✅ PDF generation successful for {proc['procedureName']}")
                return True
            else:
                log(f"   ❌ PDF generation failed for {proc['procedureName']}")
                
        except Exception as e:
            log(f"   ❌ Exception during PDF generation: {str(e)}", "ERROR")
    
    return False

def check_pdf_generator_availability():
    """Check if PDF generator and dependencies are available"""
    log("🔧 Checking PDF generator dependencies...")
    
    try:
        # Check if reportlab is available
        import reportlab
        log("   ✅ ReportLab available")
        
        # Check if PIL/Pillow is available for image processing
        try:
            from PIL import Image
            log("   ✅ PIL/Pillow available")
        except ImportError:
            log("   ⚠️ PIL/Pillow not available - may cause image issues", "WARN")
        
        # Check if the PDF generator module can be imported
        sys.path.append('/app/backend')
        from utils.pdf_generator import generate_pdf_content
        log("   ✅ PDF generator module available")
        
        return True
        
    except Exception as e:
        log(f"   ❌ PDF generator dependency issue: {str(e)}", "ERROR")
        return False

def main():
    log("🚀 Starting focused PDF generation test...")
    log("=" * 60)
    
    # Check dependencies
    deps_ok = check_pdf_generator_availability()
    
    if deps_ok:
        # Test PDF generation
        pdf_ok = test_pdf_generation_detailed()
        
        if pdf_ok:
            log("🎉 PDF generation test PASSED")
        else:
            log("❌ PDF generation test FAILED")
    else:
        log("❌ PDF generator dependencies not available")
    
    log("=" * 60)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Create IV Sedation via backend API (not direct database)
"""

import requests
import json

# Backend API endpoint
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"
LOGIN_EMAIL = "cganz2279@gmail.com"
LOGIN_PASSWORD = "password123"

def authenticate():
    """Get authentication token"""
    login_data = {
        "email": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            token = data.get("token")
            print(f"✅ Authenticated successfully")
            return token
        else:
            print(f"❌ Login failed: {data}")
            return None
    else:
        print(f"❌ Login request failed: {response.status_code} - {response.text}")
        return None

def create_iv_sedation_via_api(token):
    """Create IV Sedation procedure via backend API"""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # IV Sedation procedure data
    procedure_data = {
        "id": "iv-sedation",
        "name": "I.V. Sedation",
        "overview": """Purpose: Provide safe, comfortable dental treatment using intravenous sedation while maintaining proper breathing and response.
First 24 Hours:
- A responsible adult should remain with you today and overnight.
- No driving, operating machinery, alcohol, recreational drugs, or signing legal documents until tomorrow.
- Expect drowsiness, lightheadedness, or mild forgetfulness—move slowly from lying to standing.
- Sleep with your head elevated; use CPAP/BiPAP if prescribed.
Pain & Swelling:
- Begin prescribed/approved pain medication before numbness fully wears off.
- If permitted, many patients alternate ibuprofen and acetaminophen; follow label limits.
- Apply ice packs to the outside of your face for 20 minutes on/off for the first 24 hours.
- Switch to warm compresses after 48 hours to help with stiffness.
- Gentle jaw stretching after 3 days can help prevent limited opening if your jaw is sore.
Diet:
- Start with clear liquids (water, electrolyte drinks, broth), then advance to soft foods (yogurt, eggs, mashed potatoes).
- Avoid hot foods/drinks until numbness is gone to prevent burns.
- If you had extractions or grafting, avoid straws for at least 1 week to protect the blood clot.
Activity:
- Rest the day of your procedure; light activity the next day as tolerated.
- Avoid strenuous exercise, heavy lifting, or bending over for 48 hours.
- Change positions slowly to reduce dizziness or fainting.
Special Precautions:
- Take only medications listed on your after-visit summary or prescriptions; do not mix with extra sedatives.
- Nausea can occur—use small sips of clear fluids; take the prescribed anti-nausea medicine if needed.
- Patients with diabetes should monitor glucose more often today and maintain hydration.
- Breastfeeding: confirm medication compatibility before nursing; you may be advised to pump and discard breast milk.
- Call if you have trouble breathing, bluish lips, or severe snoring that doesn't improve when repositioned.
Follow-Up:
- Contact the office for: fever over 101°F (38.3°C), heavy bleeding, worsening pain not relieved by medication.
- Use the after-hours number provided on your paperwork. If you experience severe breathing trouble or other concerning symptoms, seek immediate medical attention.""",
        "specialty": "oral-surgery",
        "specialtyName": "Oral Surgery",
        "duration": "Variable",
        "contentSource": "original_uploaded_pdf"
    }
    
    # Try different API endpoints to create procedure
    endpoints_to_try = [
        f"{BACKEND_URL}/procedures",
        f"{BACKEND_URL}/admin/procedures",
        f"{BACKEND_URL}/practice/procedures"
    ]
    
    for endpoint in endpoints_to_try:
        print(f"🔄 Trying to create via: {endpoint}")
        
        response = requests.post(endpoint, json=procedure_data, headers=headers)
        
        if response.status_code in [200, 201]:
            print(f"✅ IV Sedation created successfully via {endpoint}")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Failed via {endpoint}: {response.status_code} - {response.text}")
    
    print("❌ All API endpoints failed")
    return False

def verify_creation(token):
    """Verify IV Sedation was created"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BACKEND_URL}/procedures/iv-sedation", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            procedure = data.get("data", {})
            print(f"✅ IV Sedation verification successful:")
            print(f"   Name: {procedure.get('name')}")
            print(f"   Specialty: {procedure.get('specialtyName')}")
            print(f"   Overview length: {len(procedure.get('overview', ''))}")
            return True
        else:
            print(f"❌ Verification failed: {data}")
            return False
    else:
        print(f"❌ Verification request failed: {response.status_code}")
        return False

def main():
    print("🏥 Creating IV Sedation via Backend API")
    print("=" * 50)
    
    # Authenticate
    token = authenticate()
    if not token:
        return
    
    # Create procedure
    success = create_iv_sedation_via_api(token)
    if not success:
        print("❌ Failed to create IV Sedation")
        return
    
    # Verify creation
    if verify_creation(token):
        print("\n🎉 SUCCESS! IV Sedation created and verified!")
    else:
        print("\n❌ Creation may have failed - verification unsuccessful")

if __name__ == "__main__":
    main()

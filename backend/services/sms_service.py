import os
from twilio.rest import Client
from dotenv import load_dotenv
from pathlib import Path
import uuid
from datetime import datetime

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

class SMSService:
    def __init__(self):
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            raise ValueError("Missing Twilio credentials. Please check TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in environment variables.")
        
        self.client = Client(self.account_sid, self.auth_token)
    
    def send_pdf_link_sms(self, patient_cellphone: str, patient_name: str, procedure_name: str, practice_name: str, pdf_link: str):
        """
        Send SMS with PDF link to patient
        
        Args:
            patient_cellphone: Patient's cellphone number in E.164 format
            patient_name: Patient's full name
            procedure_name: Name of the procedure
            practice_name: Name of the dental practice
            pdf_link: Secure link to access the PDF
        
        Returns:
            dict: Result containing success status and message details
        """
        try:
            # Ensure phone number is in E.164 format
            if not patient_cellphone.startswith('+'):
                # Assume US number if no country code
                if len(patient_cellphone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')) == 10:
                    cleaned = ''.join(filter(str.isdigit, patient_cellphone))
                    patient_cellphone = f'+1{cleaned}'
                else:
                    patient_cellphone = f'+{patient_cellphone}'
            
            # Create SMS message (keeping under 160 characters for single SMS)
            message_text = f"Hi {patient_name}, your {procedure_name} post-op instructions: {pdf_link}. From {practice_name}"
            
            # Truncate if too long
            if len(message_text) > 160:
                short_message = f"{patient_name}, your {procedure_name} instructions: {pdf_link}. - {practice_name}"
                if len(short_message) > 160:
                    # Further truncate
                    message_text = f"{patient_name}, post-op instructions: {pdf_link}"
                else:
                    message_text = short_message
            
            # Send SMS using Twilio
            message = self.client.messages.create(
                body=message_text,
                from_=self.phone_number,
                to=patient_cellphone
            )
            
            return {
                'success': True,
                'message_sid': message.sid,
                'message': f"SMS sent successfully to {patient_cellphone}",
                'sms_content': message_text,
                'patient_cellphone': patient_cellphone,
                'sent_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"SMS send error: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to send SMS to {patient_cellphone}",
                'patient_cellphone': patient_cellphone
            }
    
    def validate_phone_number(self, phone_number: str):
        """
        Validate phone number format
        
        Args:
            phone_number: Phone number to validate
        
        Returns:
            dict: Validation result with cleaned phone number
        """
        try:
            # Clean the phone number
            cleaned = ''.join(filter(str.isdigit, phone_number))
            
            # Check if it's a valid length
            if len(cleaned) == 10:
                # US number without country code
                formatted = f'+1{cleaned}'
            elif len(cleaned) == 11 and cleaned.startswith('1'):
                # US number with country code
                formatted = f'+{cleaned}'
            elif phone_number.startswith('+'):
                # Already has country code
                formatted = phone_number
            else:
                return {
                    'valid': False,
                    'error': 'Invalid phone number format'
                }
            
            return {
                'valid': True,
                'formatted': formatted,
                'original': phone_number
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }

# Create global SMS service instance
sms_service = SMSService()
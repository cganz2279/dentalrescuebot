import uuid
import jwt
from datetime import datetime, timezone, timedelta
import os
from typing import Optional, Dict, Any

JWT_SECRET = os.environ.get('JWT_SECRET', 'your-super-secret-jwt-key-change-in-production')

class SecurePDFLinkService:
    """
    Service for generating and validating secure PDF links
    """
    
    def __init__(self):
        self.secret_key = JWT_SECRET
        self.base_url = os.environ.get('FRONTEND_URL', 'https://dental-admin-3.preview.emergentagent.com')
    
    def generate_secure_link(self, assignment_id: str, patient_id: str, practice_id: str, 
                           procedure_name: str, expiry_hours: int = 72) -> str:
        """
        Generate a secure link for PDF access
        
        Args:
            assignment_id: Procedure assignment ID
            patient_id: Patient ID
            practice_id: Practice ID
            procedure_name: Name of the procedure
            expiry_hours: Link expiry time in hours (default 72 hours)
        
        Returns:
            str: Secure URL for PDF access
        """
        try:
            # Create token payload
            token_data = {
                'type': 'pdf_access',
                'assignment_id': assignment_id,
                'patient_id': patient_id,
                'practice_id': practice_id,
                'procedure_name': procedure_name,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'expires_at': (datetime.now(timezone.utc) + timedelta(hours=expiry_hours)).isoformat(),
                'access_id': str(uuid.uuid4())  # Unique access ID for tracking
            }
            
            # Generate JWT token
            token = jwt.encode(token_data, self.secret_key, algorithm='HS256')
            
            # Create secure URL
            secure_url = f"{self.base_url}/secure-pdf/{token}"
            
            return secure_url
            
        except Exception as e:
            print(f"Error generating secure link: {e}")
            raise Exception(f"Failed to generate secure PDF link: {str(e)}")
    
    def validate_secure_link(self, token: str) -> Dict[str, Any]:
        """
        Validate a secure PDF link token
        
        Args:
            token: JWT token from the secure link
        
        Returns:
            dict: Validation result with decoded data if valid
        """
        try:
            # Decode JWT token
            decoded_data = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Check if token type is correct
            if decoded_data.get('type') != 'pdf_access':
                return {
                    'valid': False,
                    'error': 'Invalid token type'
                }
            
            # Check expiry
            expires_at = datetime.fromisoformat(decoded_data.get('expires_at'))
            if datetime.now(timezone.utc) > expires_at:
                return {
                    'valid': False,
                    'error': 'Link has expired'
                }
            
            return {
                'valid': True,
                'data': decoded_data
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'valid': False,
                'error': 'Link has expired'
            }
        except jwt.InvalidTokenError as e:
            return {
                'valid': False,
                'error': f'Invalid link: {str(e)}'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Link validation error: {str(e)}'
            }
    
    def create_short_link(self, full_url: str) -> str:
        """
        Create a shorter version of the URL for SMS (optional enhancement)
        For now, just return the full URL
        
        Args:
            full_url: The full secure URL
        
        Returns:
            str: Shortened URL (or full URL if shortening not implemented)
        """
        # For now, return full URL
        # In future, could integrate with URL shortening service
        return full_url

# Global instance
pdf_link_service = SecurePDFLinkService()
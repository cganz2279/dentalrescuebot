from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment
from sendgrid.helpers.mail.file_content import FileContent
from sendgrid.helpers.mail.file_name import FileName
from sendgrid.helpers.mail.file_type import FileType
from sendgrid.helpers.mail.disposition import Disposition
import os
import base64
from typing import Optional
from datetime import datetime

class EmailService:
    def __init__(self):
        self.sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        self.sender_email = os.environ.get('SENDER_EMAIL', 'noreply@theoncallbot.com')
        self.admin_email = os.environ.get('ADMIN_EMAIL', 'admin@theoncallbot.com')
    
    def send_registration_notification(self, registration_data: dict, registration_type: str = "regular"):
        """
        Send email notification when a new user registers
        
        Args:
            registration_data: Dictionary containing registration information
            registration_type: "regular" or "samcart"
        """
        try:
            # Create email subject
            subject = f"🎉 New User Registration - {registration_data.get('practiceName', 'Unknown Practice')}"
            
            # Create detailed email content
            html_content = self._create_registration_email_html(registration_data, registration_type)
            
            message = Mail(
                from_email=self.sender_email,
                to_emails=self.admin_email,
                subject=subject,
                html_content=html_content
            )
            
            # Add reply-to address
            message.reply_to = "support@theoncallbot.com"
            
            response = self.sg.send(message)
            return response.status_code == 202
            
        except Exception as e:
            print(f"Failed to send registration notification email: {str(e)}")
            return False
    
    def _create_registration_email_html(self, data: dict, registration_type: str) -> str:
        """Create HTML content for registration notification email"""
        
        payment_status = "✅ PAID (SamCart)" if registration_type == "samcart" else "⚠️ TRIAL (Payment Required)"
        payment_class = "paid" if registration_type == "samcart" else "trial"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .section {{ margin-bottom: 20px; padding: 15px; border-left: 4px solid #2563eb; background-color: #f8f9fa; }}
                .payment-status {{ padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; margin: 20px 0; }}
                .paid {{ background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                .trial {{ background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
                .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
                .info-item {{ background: #f8f9fa; padding: 10px; border-radius: 5px; }}
                .label {{ font-weight: bold; color: #2563eb; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; margin-top: 30px; }}
                @media (max-width: 600px) {{ .info-grid {{ grid-template-columns: 1fr; }} }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎉 New Practice Registration</h1>
                <p>A new dental practice has registered for the DRB Post Operative Library</p>
            </div>
            
            <div class="content">
                <div class="payment-status {payment_class}">
                    {payment_status}
                </div>
                
                <div class="section">
                    <h2>📋 Practice Information</h2>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="label">Practice Name:</span><br>
                            {data.get('practiceName', 'Not provided')}
                        </div>
                        <div class="info-item">
                            <span class="label">Email:</span><br>
                            {data.get('email', 'Not provided')}
                        </div>
                        <div class="info-item">
                            <span class="label">Phone:</span><br>
                            {data.get('phone', 'Not provided')}
                        </div>
                        <div class="info-item">
                            <span class="label">Website:</span><br>
                            {data.get('website', 'Not provided')}
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>👤 Administrator Details</h2>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="label">First Name:</span><br>
                            {data.get('adminFirstName', 'Not provided')}
                        </div>
                        <div class="info-item">
                            <span class="label">Last Name:</span><br>
                            {data.get('adminLastName', 'Not provided')}
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📍 Practice Address</h2>
                    <div class="info-item">
                        <span class="label">Address:</span><br>
                        {data.get('street', 'Not provided')}<br>
                        {data.get('city', '')}{', ' if data.get('city') and data.get('state') else ''}{data.get('state', '')} {data.get('zipCode', '')}<br>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📊 Registration Details</h2>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="label">Registration Type:</span><br>
                            {registration_type.title()} Registration
                        </div>
                        <div class="info-item">
                            <span class="label">Registration Time:</span><br>
                            {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
                        </div>
                    </div>
                </div>
                
                {self._get_payment_verification_section(registration_type)}
            </div>
            
            <div class="footer">
                <p><strong>DRB Post Operative Library</strong></p>
                <p>This is an automated notification from your dental practice management system.</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _get_payment_verification_section(self, registration_type: str) -> str:
        """Get payment verification section based on registration type"""
        if registration_type == "samcart":
            return """
                <div class="section" style="border-left-color: #28a745;">
                    <h2>✅ Payment Verification</h2>
                    <div style="color: #28a745; font-weight: bold;">
                        <p>✅ Payment has been processed through SamCart</p>
                        <p>✅ Practice is immediately active</p>
                        <p>✅ User can access the full library</p>
                    </div>
                </div>
            """
        else:
            return """
                <div class="section" style="border-left-color: #dc3545;">
                    <h2>⚠️ Payment Verification Required</h2>
                    <div style="color: #dc3545; font-weight: bold;">
                        <p>⚠️ This is a trial registration</p>
                        <p>⚠️ Payment method setup required</p>
                        <p>⚠️ Verify payment status before full activation</p>
                    </div>
                </div>
            """

# Create a global instance
email_service = EmailService()
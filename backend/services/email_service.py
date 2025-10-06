from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, Email, To, ReplyTo
from sendgrid.helpers.mail.file_content import FileContent
from sendgrid.helpers.mail.file_name import FileName
from sendgrid.helpers.mail.file_type import FileType
from sendgrid.helpers.mail.disposition import Disposition
import os
import base64
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class EmailData(BaseModel):
    to: List[str]
    subject: str
    html_content: str
    from_email: Optional[str] = None

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
                        <p>✅ Payment has been processed successfully</p>
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

    def send_pdf_email(self, patient_email: str, pdf_content: bytes, procedure_name: str, practice_info: dict) -> bool:
        """
        Send PDF email to patient with practice information
        
        Args:
            patient_email: Patient's email address
            pdf_content: PDF content as bytes
            procedure_name: Name of the procedure (e.g., "Amalgam Fillings")
            practice_info: Dictionary containing practice information
        """
        try:
            # Create email subject
            subject = f"Post Treatment PDF {procedure_name}"
            
            # Create email content
            html_content = self._create_pdf_email_html(procedure_name, practice_info)
            
            # Create message
            message = Mail(
                from_email=(self.sender_email, practice_info.get('name', 'Dental Practice')),
                to_emails=patient_email,
                subject=subject,
                html_content=html_content
            )
            
            # Create PDF attachment
            encoded_file = base64.b64encode(pdf_content).decode()
            
            attached_file = Attachment(
                FileContent(encoded_file),
                FileName(f"{procedure_name}.pdf"),
                FileType("application/pdf"),
                Disposition("attachment")
            )
            message.attachment = attached_file
            
            response = self.sg.send(message)
            print(f"Email sent successfully to {patient_email}. Status code: {response.status_code}")
            return response.status_code == 202
            
        except Exception as e:
            print(f"Failed to send PDF email to {patient_email}: {str(e)}")
            return False
    
    def _create_pdf_email_html(self, procedure_name: str, practice_info: dict) -> str:
        """Create HTML content for PDF email"""
        
        practice_name = practice_info.get('name', 'Dental Practice')
        office_phone = practice_info.get('phone', practice_info.get('emergencyContact', 'Contact office'))
        office_hours = practice_info.get('officeHours', 'Please contact office for hours')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 30px; background-color: #f8f9fa; }}
                .practice-info {{ background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2563eb; }}
                .info-item {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #2563eb; }}
                .footer {{ background-color: #e9ecef; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; color: #6c757d; }}
                .attachment-note {{ background-color: #d1ecf1; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #bee5eb; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Post-Operative Instructions</h1>
                <p>{procedure_name}</p>
            </div>
            
            <div class="content">
                <p>Dear Patient,</p>
                
                <p>Please find attached your post-operative instructions for <strong>{procedure_name}</strong>. These instructions will help ensure proper healing and the best possible outcome from your treatment.</p>
                
                <div class="attachment-note">
                    <strong>📎 Attachment:</strong> {procedure_name}.pdf
                </div>
                
                <p>Please review these instructions carefully and follow them as directed. If you have any questions or concerns during your recovery, please don't hesitate to contact our office.</p>
                
                <div class="practice-info">
                    <h3>{practice_name}</h3>
                    <div class="info-item">
                        <span class="label">📞 Phone:</span> {office_phone}
                    </div>
                    <div class="info-item">
                        <span class="label">🕒 Office Hours:</span> {office_hours}
                    </div>
                </div>
                
                <p>Thank you for choosing {practice_name} for your dental care.</p>
                
                <p>Best regards,<br>
                <strong>{practice_name}</strong></p>
            </div>
            
            <div class="footer">
                <p>This is an automated message from {practice_name}. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        return html_content

    def send_welcome_email(self, practice_data: dict, admin_credentials: dict, app_url: str = "https://app.dentalaftercarenotes.com"):
        """
        Send welcome email to new practice with login credentials using professional template
        
        Args:
            practice_data: Dictionary containing practice information (name, etc.)
            admin_credentials: Dictionary containing admin email and password
            app_url: The application URL for login
        """
        try:
            practice_name = practice_data.get('practiceName', 'Your Practice')
            admin_email = admin_credentials.get('adminEmail')
            temp_password = admin_credentials.get('tempPassword')
            admin_name = f"{admin_credentials.get('adminFirstName', '')} {admin_credentials.get('adminLastName', '')}".strip()
            
            # Create email subject
            subject = "Welcome to Dental Aftercare Notes – Your Account Is Ready"
            
            # Professional HTML template with dynamic field replacement
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="x-apple-disable-message-reformatting">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Welcome to Dental Aftercare Notes</title>
  <style>
    @media (max-width: 600px){{
      .container{{ width:100% !important; }}
      .p-24{{ padding:16px !important; }}
      .h1{{ font-size:22px !important; line-height:28px !important; }}
      .btn a{{ display:block !important; }}
    }}
    @media (prefers-color-scheme: dark){{
      body, .card{{ background:#0b0b0f !important; color:#EDEDED !important; }}
      .btn a{{ color:#ffffff !important; }}
      .muted{{ color:#B5B5B5 !important; }}
    }}
  </style>
</head>
<body style="margin:0; padding:0; background:#f2f4f7; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; color:#0b1220;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f2f4f7;">
    <tr>
      <td align="center" style="padding:24px;">
        <table role="presentation" width="600" class="container" cellspacing="0" cellpadding="0" style="width:600px; max-width:600px; background:#ffffff; border-radius:12px; overflow:hidden;">
          <tr>
            <td align="left" style="padding:20px 24px; background:#0b5fff;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <td align="left">
                    <img src="https://customer-assets.emergentagent.com/job_samcart-auth-fix/artifacts/xqx7wou5_ChatGPT%20Image%20Sep%2028%2C%202025%2C%2011_41_56%20PM.png" width="160" height="40" alt="Dental AfterCare Notes" style="display:block; height:auto; border:0; max-width:100%; filter: brightness(0) invert(1);" />
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td class="p-24" style="padding:24px;">
              <h1 class="h1" style="margin:0 0 12px; font-size:24px; line-height:30px; font-weight:700; color:#0b1220;">Welcome to Dental Aftercare Notes – Your Account Is Ready</h1>
              <p style="margin:0 0 16px;">Dear {admin_name},</p>
              <p style="margin:0 0 16px;">
                Welcome to <strong>Dental Aftercare Notes</strong>, a service from <em>The Oncall Bot LLC</em>! We're excited to help you simplify how you provide clear, dentist-approved post-treatment instructions to your patients.
              </p>
              <table role="presentation" cellspacing="0" cellpadding="0" style="margin:16px 0 12px; background:#f7f9fc; border:1px solid #e6eaf1; border-radius:8px; width:100%;">
                <tr>
                  <td style="padding:14px 16px;">
                    <p style="margin:0 0 6px; font-weight:600;">Your Login Details</p>
                    <p style="margin:0;"><strong>Username (Email):</strong> {admin_email}</p>
                    <p style="margin:6px 0 0;"><strong>Temporary Password:</strong> {temp_password}</p>
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 16px;"><strong>Security note:</strong> You'll be prompted to change this password at your first sign-in.</p>
              <table role="presentation" cellspacing="0" cellpadding="0" class="btn" style="margin:20px 0 8px;">
                <tr>
                  <td align="left" style="border-radius:10px; background:#0b5fff;">
                    <a href="{app_url}" target="_blank"
                       style="display:inline-block; padding:12px 18px; font-weight:700; text-decoration:none; color:#ffffff; border-radius:10px;">
                      Access Your Account
                    </a>
                  </td>
                </tr>
              </table>
              <p style="margin:10px 0 18px; font-size:14px; color:#475266;">
                If the button doesn't work, paste this link into your browser: <br>
                <span style="word-break:break-all; color:#0b5fff;">{app_url}</span>
              </p>
              <h2 style="margin:24px 0 10px; font-size:18px;">Quick Start</h2>
              <ol style="margin:0 0 18px; padding-left:20px;">
                <li style="margin:6px 0;">Go to the secure link above.</li>
                <li style="margin:6px 0;">Sign in with your email and temporary password.</li>
                <li style="margin:6px 0;">Create your new password when prompted.</li>
                <li style="margin:6px 0;">Start using Dental Aftercare Notes immediately.</li>
              </ol>
              <p style="margin:0 0 16px;">
                <strong>Helpful tip:</strong> Before you begin, take a few minutes to watch/listen to our quick tutorials.
                They'll walk you through the key features so you can get the most out of your account from the start.
              </p>
              <p style="margin:0 0 16px;">
                If you need assistance, we're here to help at
                <a href="mailto:support@theoncallbot.com" style="color:#0b5fff; text-decoration:none;">support@theoncallbot.com</a>.
              </p>
              <p style="margin:0 0 6px;">Warm regards,</p>
              <p style="margin:0;"><strong>The Oncall Bot LLC Team</strong></p>
            </td>
          </tr>
          <tr>
            <td style="padding:16px 24px; background:#ffffff; border-top:1px solid #eef1f6;">
              <p class="muted" style="margin:0; font-size:12px; color:#6b7280;">
                You're receiving this transactional email because an account was created for you on Dental Aftercare Notes.
              </p>
            </td>
          </tr>
        </table>
        <div style="height:24px; line-height:24px;">&nbsp;</div>
      </td>
    </tr>
  </table>
</body>
</html>"""
            
            # Send email
            message = Mail(
                from_email=self.sender_email,
                to_emails=admin_email,
                subject=subject,
                html_content=html_content
            )
            
            # Create fresh SendGrid client with current API key to avoid 401 errors
            fresh_sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = fresh_sg.send(message)
            
            if response.status_code in [200, 202]:
                print(f"✅ Welcome email sent successfully to {admin_email}")
                return True
            else:
                print(f"❌ Failed to send welcome email. Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending welcome email: {e}")
            return False

    def send_password_reset_email(self, to_email: str, user_name: str, reset_link: str, reset_token: str):
        """
        Send password reset email with reset link
        """
        try:
            # Create HTML content for password reset
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Password Reset Request</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #2563eb; margin: 0;">Password Reset Request</h1>
                        <p style="color: #666; margin-top: 10px;">Secure access to your dental practice account</p>
                    </div>

                    <!-- Main Content -->
                    <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h2 style="color: #333; margin-top: 0;">Hello {user_name or 'there'},</h2>
                        
                        <p style="color: #555; margin-bottom: 15px;">
                            We received a request to reset the password for your dental practice account associated with this email address.
                        </p>
                        
                        <p style="color: #555; margin-bottom: 20px;">
                            If you made this request, click the button below to reset your password:
                        </p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_link}" 
                               style="background-color: #2563eb; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                                Reset My Password
                            </a>
                        </div>
                        
                        <p style="color: #555; font-size: 14px; margin-bottom: 15px;">
                            <strong>Important:</strong> This link will expire in 1 hour for security reasons.
                        </p>
                        
                        <p style="color: #555; font-size: 14px; margin-bottom: 15px;">
                            If the button doesn't work, copy and paste this link into your browser:
                        </p>
                        
                        <div style="background-color: #e5e7eb; padding: 10px; border-radius: 5px; word-break: break-all; font-size: 12px;">
                            {reset_link}
                        </div>
                    </div>

                    <!-- Security Notice -->
                    <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin-bottom: 20px;">
                        <h3 style="color: #dc2626; margin: 0 0 10px 0; font-size: 16px;">Security Notice</h3>
                        <ul style="color: #7f1d1d; margin: 0; padding-left: 20px;">
                            <li>If you didn't request this password reset, please ignore this email</li>
                            <li>Your password will remain unchanged</li>
                            <li>Never share your password or reset links with anyone</li>
                        </ul>
                    </div>

                    <!-- Footer -->
                    <div style="text-align: center; border-top: 1px solid #e5e7eb; padding-top: 20px; color: #666; font-size: 12px;">
                        <p style="margin: 5px 0;">This email was sent by your Dental Practice Management System</p>
                        <p style="margin: 5px 0;">For support, contact your system administrator</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Create plain text version
            text_content = f"""
            Password Reset Request

            Hello {user_name or 'there'},

            We received a request to reset the password for your dental practice account.

            To reset your password, please visit the following link (expires in 1 hour):
            {reset_link}

            If you didn't request this password reset, please ignore this email.

            Security Notice:
            - Never share your password or reset links with anyone
            - If you didn't request this reset, your password remains unchanged

            For support, contact your system administrator.
            """

            # Create the email message
            message = Mail(
                from_email=self.sender_email,
                to_emails=to_email,
                subject="Password Reset Request - Dental Practice Account",
                html_content=html_content,
                plain_text_content=text_content
            )

            # Send the email
            response = self.sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ Password reset email sent successfully to {to_email}")
                return True
            else:
                print(f"❌ Failed to send password reset email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending password reset email: {e}")
            return False

# Create a global instance
email_service = EmailService()

# Async function for SamCart integration
async def send_email(email_data: EmailData) -> bool:
    """
    Async wrapper for sending emails using SendGrid with improved background task support
    """
    try:
        # Get fresh environment variables for each send (fixes background task issues)
        sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        sender_email = os.environ.get('SENDER_EMAIL', 'noreply@theoncallbot.com')
        
        if not sendgrid_api_key:
            print("❌ SENDGRID_API_KEY not found in environment variables")
            return False
            
        # Create new SendGrid client instance for each send (fixes background task auth issues)
        sg_client = SendGridAPIClient(sendgrid_api_key)
        
        from_email = email_data.from_email or sender_email
        
        print(f"🔍 Sending email from {from_email} to {email_data.to}")
        
        message = Mail(
            from_email=from_email,
            to_emails=email_data.to,
            subject=email_data.subject,
            html_content=email_data.html_content
        )
        
        # Send email with detailed error logging
        response = sg_client.send(message)
        
        print(f"🔍 SendGrid response - Status: {response.status_code}")
        
        if response.status_code in [200, 202]:
            print(f"✅ Email sent successfully to {email_data.to}")
            return True
        else:
            error_body = response.body.decode('utf-8') if hasattr(response.body, 'decode') else str(response.body)
            print(f"❌ Failed to send email. Status: {response.status_code}, Body: {error_body}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    async def send_custom_email(self, to_email: str, subject: str, html_content: str, from_email: str = None, from_name: str = None):
        """Send a custom email with specified content"""
        try:
            # Create a fresh SendGrid client for this email
            sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            
            from_email_obj = Email(from_email or "noreply@dentalaftercarenotes.com", from_name or "Dental AfterCare Notes")
            to_email_obj = To(to_email)
            
            # Create the email
            mail = Mail(
                from_email=from_email_obj,
                to_emails=to_email_obj,
                subject=subject,
                html_content=html_content
            )
            
            # Set reply-to if different from sender
            if from_email and from_email != "noreply@dentalaftercarenotes.com":
                mail.reply_to = ReplyTo(from_email, from_name)
            
            # Send email
            response = sg.send(mail)
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ Custom email sent successfully to {to_email}")
                return True
            else:
                print(f"❌ Failed to send custom email. Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending custom email: {str(e)}")
            traceback.print_exc()
            return False
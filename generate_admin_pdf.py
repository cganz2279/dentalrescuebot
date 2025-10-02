#!/usr/bin/env python3
"""
Generate Professional PDF Admin Guide for Practice Notes
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

def create_admin_guide_pdf():
    # Create PDF document
    doc = SimpleDocTemplate("/app/Practice_Notes_Admin_Guide.pdf", 
                          pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2c5a87'),
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#3c7ab7'),
        leftIndent=0
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=16,
        textColor=colors.HexColor('#2c5a87')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        backColor=colors.HexColor('#f8f9fa'),
        leftIndent=20,
        rightIndent=20
    )
    
    # Build content
    story = []
    
    # Title page
    story.append(Paragraph("Practice Notes SaaS", title_style))
    story.append(Paragraph("Complete Admin Guide", title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Overview
    story.append(Paragraph("🏥 Application Overview", heading_style))
    story.append(Paragraph("Practice Notes is a comprehensive B2B SaaS dental application providing post-operative care instructions with over 80 detailed procedure guides, patient management, and branded PDF downloads.", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # URLs Section
    story.append(Paragraph("🔗 Critical URLs & Access Points", heading_style))
    
    # Main Application URLs table
    story.append(Paragraph("Main Application URLs", subheading_style))
    url_data = [
        ['Service', 'URL', 'Purpose'],
        ['Main App', 'https://aftercareportal.preview.emergentagent.com', 'Primary dental practice application'],
        ['Admin Console', 'https://aftercareportal.preview.emergentagent.com/admin', 'Full admin management interface'],
        ['HTML Admin Dashboard', 'https://aftercareportal.preview.emergentagent.com/api/admin/dashboard-html', 'Advanced admin dashboard (backup)']
    ]
    
    url_table = Table(url_data, colWidths=[1.5*inch, 3*inch, 2.5*inch])
    url_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c5a87')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(url_table)
    story.append(Spacer(1, 0.2*inch))
    
    # WordPress Integration URLs
    story.append(Paragraph("WordPress Integration URLs", subheading_style))
    wp_data = [
        ['Page', 'URL', 'Purpose'],
        ['Practice Login', 'www.theoncallbot.com/practice-notes', 'Main practice login portal'],
        ['Password Reset', 'www.theoncallbot.com/practice-notes-reset-password', 'Password reset interface'],
        ['WordPress Admin', 'www.theoncallbot.com/wp-admin', 'WordPress backend management']
    ]
    
    wp_table = Table(wp_data, colWidths=[1.5*inch, 3*inch, 2.5*inch])
    wp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c5a87')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(wp_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Admin Credentials
    story.append(Paragraph("🔑 Admin Credentials", heading_style))
    story.append(Paragraph("Super Admin Access", subheading_style))
    story.append(Paragraph("• <b>Email:</b> cganz@admin.com", body_style))
    story.append(Paragraph("• <b>Password:</b> Dentist1#", body_style))
    story.append(Paragraph("• <b>Access Level:</b> Full system administration", body_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("Your Practice Account", subheading_style))
    story.append(Paragraph("• <b>Email:</b> cganz2279@gmail.com", body_style))
    story.append(Paragraph("• <b>Practice:</b> Cary Ganz DDS PC", body_style))
    story.append(Paragraph("• <b>Status:</b> Active", body_style))
    story.append(Paragraph("• <b>Role:</b> Practice Administrator", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Admin Console Features
    story.append(Paragraph("📊 Admin Console Features", heading_style))
    
    story.append(Paragraph("Dashboard Tab", subheading_style))
    story.append(Paragraph("• <b>Total Practices:</b> Real-time count of all registered practices", body_style))
    story.append(Paragraph("• <b>Active Practices:</b> Currently operational practices", body_style))
    story.append(Paragraph("• <b>Procedure Requests:</b> Pending dentist requests for new procedures", body_style))
    story.append(Paragraph("• <b>Total Revenue:</b> Financial overview and transaction summaries", body_style))
    story.append(Paragraph("• <b>Key Metrics:</b> All statistics update automatically from live data", body_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("Practices Management", subheading_style))
    story.append(Paragraph("• <b>View All Practices:</b> Complete list with status indicators", body_style))
    story.append(Paragraph("• <b>Practice Details:</b> Comprehensive information including contact information, address, subscription status, billing details, creation dates, and technical IDs", body_style))
    story.append(Paragraph("• <b>Actions Available:</b> Activate/deactivate practices, view detailed information, manage subscriptions", body_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("Procedure Requests Management", subheading_style))
    story.append(Paragraph("• <b>Enhanced Request Forms:</b> Dentists now provide detailed procedure descriptions and clinical justifications", body_style))
    story.append(Paragraph("• <b>Priority Levels:</b> Normal, High, Urgent with visual indicators", body_style))
    story.append(Paragraph("• <b>Admin Actions:</b> View comprehensive details, approve/reject with admin notes, track status", body_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("Payment Transactions", subheading_style))
    story.append(Paragraph("• <b>Transaction Monitoring:</b> All payment activities and status tracking", body_style))
    story.append(Paragraph("• <b>Financial Data:</b> Amounts, dates, transaction IDs, and practice correlations", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Page break for next section
    story.append(PageBreak())
    
    # System Management
    story.append(Paragraph("🛠 System Management", heading_style))
    story.append(Paragraph("Backend API Endpoints", subheading_style))
    story.append(Paragraph("Base URL: https://aftercareportal.preview.emergentagent.com/api", code_style))
    story.append(Paragraph("• POST /admin/login - Admin authentication", body_style))
    story.append(Paragraph("• GET /admin/practices - Practice management", body_style))
    story.append(Paragraph("• GET /admin/procedure-requests - Procedure requests", body_style))
    story.append(Paragraph("• GET /admin/payments - Payment transactions", body_style))
    story.append(Paragraph("• GET /admin/dashboard - Dashboard statistics", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Key Management Tasks
    story.append(Paragraph("🔧 Key Management Tasks", heading_style))
    
    story.append(Paragraph("Practice Management", subheading_style))
    story.append(Paragraph("1. <b>Monitor Practice Status:</b> Access Admin Console → Practices Tab, review active/inactive status, check subscription details", body_style))
    story.append(Paragraph("2. <b>Activate/Deactivate Practices:</b> Click practice action buttons, confirm status changes, monitor impact on access", body_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("Procedure Request Management", subheading_style))
    story.append(Paragraph("1. <b>Review New Requests:</b> Admin Console → Procedure Requests Tab, detailed dentist descriptions and justifications, priority levels for urgent requests", body_style))
    story.append(Paragraph("2. <b>Approve/Reject Decisions:</b> Click 'View Details' for comprehensive information, use 'Approve' or 'Reject' buttons, add admin notes for feedback", body_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("Financial Monitoring", subheading_style))
    story.append(Paragraph("1. <b>Payment Tracking:</b> Admin Console → Payments Tab, monitor transaction status, track revenue and payment issues", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Enhanced Features
    story.append(Paragraph("📋 Enhanced Features Implemented", heading_style))
    
    story.append(Paragraph("Password Reset System", subheading_style))
    story.append(Paragraph("• Complete WordPress integration with professional branded interface", body_style))
    story.append(Paragraph("• Secure token validation and user-friendly experience", body_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("Admin Dashboard", subheading_style))
    story.append(Paragraph("• Multi-tab interface: Dashboard, Practices, Requests, Payments", body_style))
    story.append(Paragraph("• Real-time data with live statistics and comprehensive management", body_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("Procedure Request Enhancement", subheading_style))
    story.append(Paragraph("• Detailed forms requiring comprehensive information from dentists", body_style))
    story.append(Paragraph("• Clinical justification with frequency and importance details", body_style))
    story.append(Paragraph("• Priority system with visual indicators and admin decision support", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Troubleshooting
    story.append(Paragraph("🚨 Troubleshooting Guide", heading_style))
    
    story.append(Paragraph("Common Issues", subheading_style))
    story.append(Paragraph("1. <b>Login Problems:</b> Verify credentials (cganz@admin.com / Dentist1#), clear browser cache, try incognito mode", body_style))
    story.append(Paragraph("2. <b>Data Not Loading:</b> Check internet connection, refresh page, verify admin token validity", body_style))
    story.append(Paragraph("3. <b>WordPress Integration:</b> Ensure forms are properly embedded in WordPress pages", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Next Steps
    story.append(Paragraph("📈 Next Steps & Pending Tasks", heading_style))
    
    story.append(Paragraph("Priority Items", subheading_style))
    story.append(Paragraph("1. SamCart Webhook Integration: Automated account activation/deactivation", body_style))
    story.append(Paragraph("2. Enhanced Website Integration: Additional navigation and pages", body_style))
    story.append(Paragraph("3. Legal Pages: Disclaimers and privacy statements", body_style))
    story.append(Paragraph("4. Sales & Marketing: Outreach to dental practices", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("System Monitoring", subheading_style))
    story.append(Paragraph("• Regular checks of admin console functionality, practice login system, procedure request processing, and payment transaction tracking", body_style))
    story.append(Paragraph("• Data management including monitoring practice registrations, reviewing procedure request patterns, tracking financial metrics, and maintaining system performance", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Technical Support
    story.append(Paragraph("📞 Support Information", heading_style))
    story.append(Paragraph("Technical Details", subheading_style))
    story.append(Paragraph("• <b>Platform:</b> Emergent Agent Environment", body_style))
    story.append(Paragraph("• <b>Stack:</b> FastAPI + React + MongoDB", body_style))
    story.append(Paragraph("• <b>Deployment:</b> Kubernetes cluster with supervisor management", body_style))
    story.append(Paragraph("• <b>Environment Variables:</b> Protected (REACT_APP_BACKEND_URL, MONGO_URL)", body_style))
    story.append(Paragraph("• <b>Service Ports:</b> Backend (8001), Frontend (3000)", body_style))
    story.append(Paragraph("• <b>API Routing:</b> All backend routes prefixed with '/api'", body_style))
    story.append(Paragraph("• <b>Authentication:</b> JWT token-based with secure admin access", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # System Status
    story.append(Paragraph("✅ System Status: PRODUCTION READY", heading_style))
    story.append(Paragraph("Current Status: Fully operational dental SaaS platform with comprehensive admin management capabilities.", body_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Last Updated: {datetime.now().strftime('%B %Y')}", body_style))
    story.append(Paragraph("Admin Guide Version: 1.0", body_style))
    story.append(Paragraph("System Environment: Production-ready deployment", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("<i>This guide provides complete information for managing and monitoring the Practice Notes dental SaaS application. Keep this document accessible for ongoing system management and troubleshooting.</i>", body_style))
    
    # Build PDF
    doc.build(story)
    print("✅ Professional PDF generated successfully: Practice_Notes_Admin_Guide.pdf")

if __name__ == "__main__":
    create_admin_guide_pdf()
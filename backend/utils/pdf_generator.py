from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from io import BytesIO
import base64
import os

def generate_pdf_content(procedure_name: str, procedure_data: dict, practice_info: dict) -> bytes:
    """
    Generate PDF content for procedure instructions
    
    Args:
        procedure_name: Name of the procedure
        procedure_data: Procedure details from database
        practice_info: Practice information
    
    Returns:
        bytes: PDF content as bytes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        textColor=HexColor('#2563eb'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#2563eb'),
        spaceBefore=16,
        spaceAfter=8
    )
    
    bold_style = ParagraphStyle(
        'BoldText',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        spaceBefore=8,
        spaceAfter=4
    )
    
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=11,
        spaceBefore=4,
        spaceAfter=4
    )
    
    # Build content
    content = []
    
    # Try to add logo from base64 file
    try:
        logo_path = "/app/frontend/public/dental-rescue-logo-base64.txt"
        if os.path.exists(logo_path):
            with open(logo_path, 'r') as f:
                logo_base64 = f.read().strip()
                if logo_base64.startswith('data:image'):
                    # Remove the data:image/png;base64, prefix
                    logo_data = logo_base64.split(',')[1]
                    logo_bytes = base64.b64decode(logo_data)
                    logo_buffer = BytesIO(logo_bytes)
                    
                    # Add logo
                    logo = Image(logo_buffer, width=2*inch, height=1*inch)
                    logo.hAlign = 'CENTER'
                    content.append(logo)
                    content.append(Spacer(1, 12))
    except:
        # Fallback to text header if logo fails
        content.append(Paragraph("DENTAL RESCUE NOTES", title_style))
        content.append(Spacer(1, 12))
    
    # Procedure title
    content.append(Paragraph(f"Post-Operative Instructions", header_style))
    content.append(Paragraph(procedure_name, title_style))
    content.append(Spacer(1, 20))
    
    # Purpose section
    if procedure_data.get('overview'):
        content.append(Paragraph("Purpose", bold_style))
        content.append(Paragraph(procedure_data['overview'], normal_style))
        content.append(Spacer(1, 12))
    
    # Immediate aftercare
    if procedure_data.get('immediateAftercare'):
        content.append(Paragraph("First 24 Hours", bold_style))
        for instruction in procedure_data['immediateAftercare']:
            content.append(Paragraph(f"• {instruction}", normal_style))
        content.append(Spacer(1, 12))
    
    # Diet restrictions
    if procedure_data.get('dietRestrictions'):
        content.append(Paragraph("Diet", bold_style))
        for restriction in procedure_data['dietRestrictions']:
            content.append(Paragraph(f"• {restriction}", normal_style))
        content.append(Spacer(1, 12))
    
    # Medications
    if procedure_data.get('medications'):
        content.append(Paragraph("Pain & Sensitivity", bold_style))
        for medication in procedure_data['medications']:
            content.append(Paragraph(f"• {medication}", normal_style))
        content.append(Spacer(1, 12))
    
    # Warning signs
    if procedure_data.get('warningSignsToCallDoctor'):
        content.append(Paragraph("Special Precautions", bold_style))
        for warning in procedure_data['warningSignsToCallDoctor']:
            content.append(Paragraph(f"• {warning}", normal_style))
        content.append(Spacer(1, 12))
    
    # Recovery timeline
    if procedure_data.get('recoveryTimeline'):
        content.append(Paragraph("Follow-Up", bold_style))
        for timeline_item in procedure_data['recoveryTimeline']:
            if isinstance(timeline_item, dict):
                period = timeline_item.get('period', '')
                description = timeline_item.get('description', '')
                content.append(Paragraph(f"• {period}: {description}", normal_style))
            else:
                content.append(Paragraph(f"• {timeline_item}", normal_style))
        content.append(Spacer(1, 12))
    
    # Practice information footer
    content.append(Spacer(1, 30))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#666666'),
        alignment=TA_CENTER,
        spaceBefore=20
    )
    
    practice_name = practice_info.get('name', 'Dental Practice')
    practice_phone = practice_info.get('phone', practice_info.get('emergencyContact', 'Contact office'))
    office_hours = practice_info.get('officeHours', 'Please contact office for hours')
    
    content.append(Paragraph("─" * 50, footer_style))
    content.append(Paragraph(f"<b>{practice_name}</b>", footer_style))
    content.append(Paragraph(f"Phone: {practice_phone}", footer_style))
    content.append(Paragraph(f"Office Hours: {office_hours}", footer_style))
    content.append(Paragraph("If you have any questions or concerns, please contact our office.", footer_style))
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer.getvalue()
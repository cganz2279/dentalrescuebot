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
        spaceBefore=6,
        spaceAfter=2,
        textColor=HexColor('#000000')
    )
    
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=0,
        spaceAfter=3,
        leftIndent=0,
        alignment=0  # Left alignment
    )
    
    # Build content
    content = []
    
    # Try to add practice logo
    try:
        # First try to use practice's custom logo from branding
        logo_added = False
        
        if practice_info and practice_info.get('branding', {}).get('logo'):
            try:
                logo_data_url = practice_info['branding']['logo']
                if logo_data_url and logo_data_url.startswith('data:image'):
                    # Remove the data:image/png;base64, prefix
                    logo_data = logo_data_url.split(',')[1]
                    logo_bytes = base64.b64decode(logo_data)
                    
                    # Validate image data size
                    print(f"🔍 Custom logo data size: {len(logo_bytes)} bytes")
                    
                    if len(logo_bytes) < 100:
                        print("⚠️ Custom logo data too small, likely corrupted placeholder")
                        raise Exception("Custom logo data corrupted (too small)")
                    
                    logo_buffer = BytesIO(logo_bytes)
                    
                    # Add custom practice logo
                    logo = Image(logo_buffer, width=2*inch, height=1*inch)
                    logo.hAlign = 'CENTER'
                    content.append(logo)
                    content.append(Spacer(1, 12))
                    logo_added = True
                    print("✅ Using custom practice logo in PDF")
                else:
                    print("⚠️ Practice logo not in data:image format")
            except Exception as e:
                print(f"⚠️ Failed to use custom practice logo: {e}")
                # Clear any potential partial content
                if 'logo' in locals():
                    del logo
        else:
            print("ℹ️ No custom practice logo found in practice_info")
        
        # Fallback to default logo file if custom logo failed
        if not logo_added:
            logo_path = "/app/frontend/public/dental-rescue-logo-base64.txt"
            if os.path.exists(logo_path):
                print("⚠️ Using default logo fallback")
                with open(logo_path, 'r') as f:
                    logo_base64 = f.read().strip()
                    if logo_base64.startswith('data:image'):
                        # Remove the data:image/png;base64, prefix
                        logo_data = logo_base64.split(',')[1]
                        logo_bytes = base64.b64decode(logo_data)
                        logo_buffer = BytesIO(logo_bytes)
                        
                        # Add default logo
                        logo = Image(logo_buffer, width=2*inch, height=1*inch)
                        logo.hAlign = 'CENTER'
                        content.append(logo)
                        content.append(Spacer(1, 12))
                        logo_added = True
                        print("✅ Using default logo in PDF")
            else:
                print("⚠️ Default logo file not found")
        
        # Final fallback to text header if no logo worked
        if not logo_added:
            # Use practice name if available, otherwise fallback to generic title
            practice_title = practice_info.get('name', 'DENTAL RESCUE NOTES') if practice_info else 'DENTAL RESCUE NOTES'
            content.append(Paragraph(practice_title, title_style))
            content.append(Spacer(1, 12))
            print(f"ℹ️ Using text header in PDF: {practice_title}")
            
    except Exception as e:
        print(f"❌ Logo handling error: {e}")
        # Fallback to text header if logo fails
        practice_title = practice_info.get('name', 'DENTAL RESCUE NOTES') if practice_info else 'DENTAL RESCUE NOTES'
        content.append(Paragraph(practice_title, title_style))
        content.append(Spacer(1, 12))
    
    # Add practice name below logo/header if we have logo but want to show practice name too
    if logo_added and practice_info and practice_info.get('name'):
        practice_name_style = ParagraphStyle(
            'PracticeName',
            parent=styles['Normal'],
            fontSize=12,
            textColor=HexColor('#2563eb'),
            alignment=TA_CENTER,
            spaceAfter=16
        )
        content.append(Paragraph(practice_info['name'], practice_name_style))
    
    # Procedure title
    content.append(Paragraph("Post-Operative Instructions", header_style))
    content.append(Paragraph(procedure_name, title_style))
    content.append(Spacer(1, 20))
    
    # Debug: Print what fields are actually available
    print(f"🔍 DEBUG: Procedure data fields: {list(procedure_data.keys())}")
    print(f"🔍 DEBUG: Full overview content: {procedure_data.get('overview', 'NO OVERVIEW FOUND')}")
    
    # Use the full overview content with simple formatting
    if procedure_data.get('overview'):
        overview_text = procedure_data['overview']
        
        # Split by common section separators but keep all content
        sections = []
        
        # Try to split by double newlines first (paragraph breaks)
        paragraphs = overview_text.split('\n\n')
        
        # If no double newlines, split by single newlines
        if len(paragraphs) == 1:
            paragraphs = overview_text.split('\n')
        
        # If still one big block, split by periods followed by capital letters (sentence breaks)
        if len(paragraphs) == 1:
            import re
            paragraphs = re.split(r'(?<=\.)\s+(?=[A-Z])', overview_text)
        
        print(f"🔍 DEBUG: Split into {len(paragraphs)} paragraphs")
        
        # Look for obvious section headers in the text
        section_headers = ['Purpose', 'First 24-48 Hours', 'Pain and Sensitivity', 'Oral Hygiene', 'Diet', 'Special Precautions', 'Followup']
        current_section = 'Post-Operative Care Instructions'  # Default header
        
        for i, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # Check if this paragraph is a section header
            is_header = False
            for header in section_headers:
                if header.lower() in paragraph.lower() and len(paragraph) < 100:
                    current_section = header
                    is_header = True
                    break
            
            if is_header:
                # Add section header
                content.append(Paragraph(f"<b>{current_section}</b>", bold_style))
                content.append(Spacer(1, 2))
            else:
                # Add content paragraph
                # Clean up any existing formatting
                clean_paragraph = paragraph.replace('**', '').replace('*', '').strip()
                if clean_paragraph:
                    content.append(Paragraph(clean_paragraph, normal_style))
                    content.append(Spacer(1, 3))  # Small space between paragraphs
        
        # If no content was added (shouldn't happen), add the raw text
        content_before = len([item for item in content if hasattr(item, 'text')])
        if content_before == 0:
            content.append(Paragraph("<b>Post-Operative Care Instructions</b>", bold_style))
            content.append(Spacer(1, 4))
            content.append(Paragraph(overview_text, normal_style))
    
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
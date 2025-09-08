import jsPDF from 'jspdf';

// Helper function to format phone numbers
const formatPhoneNumber = (phone) => {
  if (!phone) return '';
  
  // Remove all non-digit characters
  const cleaned = phone.replace(/\D/g, '');
  
  // Format based on length
  if (cleaned.length === 10) {
    // US format: (123) 456-7890
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  } else if (cleaned.length === 11 && cleaned[0] === '1') {
    // US format with country code: +1 (123) 456-7890
    return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  } else {
    // Return original if can't format
    return phone;
  }
};

// Format original PDF content to extract readable sections
const formatOriginalPDFContent = (content) => {
  if (!content) return 'No content available';
  
  // Extract and clean up the content to match your original PDF format
  let cleanContent = content
    // Remove any truncated text ending with "..."
    .replace(/\.{3,}$/, '')
    // Clean up spacing
    .replace(/\s+/g, ' ')
    .trim();
  
  return cleanContent;
};

// Generate actual PDF file using jsPDF (OVERVIEW ONLY)
export const generateProcedurePDF = async (procedure) => {
  console.log('🎯 PDF Generator Entry - Procedure Object:', procedure);
  
  try {
    console.log('🎨 Starting SIMPLIFIED PDF generation...');
    
    // Create new PDF document
    const pdf = new jsPDF();
    
    // Set up document properties
    pdf.setProperties({
      title: `${procedure.name || 'Procedure'} - Post-Operative Care Guide`,
      subject: 'Post-Operative Care Instructions',
      author: procedure.practiceName || 'Dental Practice',
      creator: 'Dental Practice Management System'
    });
    
    let yPos = 20;
    
    // Header
    pdf.setFontSize(18);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedure.name || 'Post-Operative Care', 20, yPos);
    yPos += 15;
    
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'normal');
    pdf.text('Post-Operative Care Instructions', 20, yPos);
    yPos += 20;
    
    // Practice info
    if (procedure.practiceName) {
      pdf.setFontSize(12);
      pdf.setFont(undefined, 'bold');
      pdf.text(procedure.practiceName, 20, yPos);
      yPos += 10;
    }
    
    if (procedure.practicePhone) {
      pdf.setFont(undefined, 'normal');
      pdf.text(`Phone: ${formatPhoneNumber(procedure.practicePhone)}`, 20, yPos);
      yPos += 15;
    }
    
    // Simple content sections - no complex object handling
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'normal');
    
    // Add main content (use overview for simplicity)
    if (procedure.overview) {
      const cleanText = String(procedure.overview).replace(/\[object Object\]/g, '').trim();
      if (cleanText) {
        const lines = pdf.splitTextToSize(cleanText, 170);
        
        lines.forEach(line => {
          if (yPos > 250) {
            pdf.addPage();
            yPos = 20;
          }
          pdf.text(line, 20, yPos);
          yPos += 6;
        });
        yPos += 15;
      }
    }
    
    // ALWAYS add Office Hours and Emergency Contact at the end
    yPos = Math.max(yPos, 200); // Ensure we're near bottom of page
    
    // Add new page if needed for footer
    if (yPos > 220) {
      pdf.addPage();
      yPos = 20;
    }
    
    // Generation timestamp
    pdf.setFontSize(10);
    pdf.setFont(undefined, 'italic');
    pdf.text(`Generated on ${new Date().toLocaleDateString()}`, 20, yPos);
    yPos += 15;
    
    // FORCE Office Hours - Use any available source
    const officeHours = procedure.practiceOfficeHours || 
                       procedure.officeHours || 
                       'Mon-Fri: 8:00 AM - 5:00 PM (EST/EDT) • Sat: 9:00 AM - 2:00 PM';
    
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'bold');
    pdf.text('Office Hours:', 20, yPos);
    yPos += 8;
    pdf.setFont(undefined, 'normal');
    pdf.text(officeHours, 20, yPos);
    yPos += 15;
    
    // FORCE Emergency Contact - Use any available source  
    const emergencyContact = procedure.practiceEmergencyContact || 
                           procedure.emergencyContact ||
                           procedure.practicePhone ||
                           '📞 (555) 123-4567 • 🚨 Emergency Line';
    
    pdf.setFont(undefined, 'bold');
    pdf.text('Emergency Contact:', 20, yPos);
    yPos += 8;
    pdf.setFont(undefined, 'normal');
    pdf.text(formatPhoneNumber(emergencyContact), 20, yPos);
    
    // Save the PDF
    const filename = `${(procedure.name || 'Procedure').replace(/\s+/g, '_')}_Care_Guide.pdf`;
    pdf.save(filename);
    
    console.log('✅ SIMPLIFIED PDF generated successfully:', filename);
    console.log('✅ Office Hours included:', officeHours);
    console.log('✅ Emergency Contact included:', emergencyContact);
    
    return true;
    
  } catch (error) {
    console.error('❌ PDF generation failed:', error);
    return false;
  }
};








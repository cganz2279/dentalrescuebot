import jsPDF from 'jspdf';

// Helper function to format phone numbers
const formatPhoneNumber = (phone) => {
  if (!phone) return '';
  
  const cleaned = phone.replace(/\D/g, '');
  
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  } else if (cleaned.length === 11 && cleaned[0] === '1') {
    return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  } else {
    return phone;
  }
};

// SIMPLE PDF GENERATOR - EXACT UPLOADED PDF FORMAT
export const generateProcedurePDF = async (procedure) => {
  // Alert to confirm new code is running
  alert('🎯 SIMPLE PDF GENERATOR - EXACT UPLOADED PDF FORMAT!');
  console.log('📄 Simple PDF Generator - Raw Overview Text Only');
  
  try {
    const pdf = new jsPDF();
    
    pdf.setProperties({
      title: `${procedure.name || 'Procedure'} - Post-Operative Care Guide`,
      subject: 'Post-Operative Care Instructions',
      author: procedure.practiceName || 'Dental Practice',
      creator: 'Dental Practice Management System'
    });
    
    let yPos = 20;
    
    // Procedure Name as title
    pdf.setFontSize(16);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedure.name || 'Post-Operative Care', 20, yPos);
    yPos += 25;
    
    // Raw overview text - NO FORMATTING, NO PARSING
    if (procedure.overview) {
      pdf.setFontSize(11);
      pdf.setFont(undefined, 'normal');
      
      // Simply wrap the text and display it exactly as stored
      const wrappedText = pdf.splitTextToSize(procedure.overview, 170);
      
      wrappedText.forEach(line => {
        // Check if we need a new page
        if (yPos > 270) {
          pdf.addPage();
          yPos = 20;
        }
        
        pdf.text(line, 20, yPos);
        yPos += 6;
      });
    }
    
    // Add spacing before practice information
    yPos += 20;
    
    // Check if we need a new page for practice info
    if (yPos > 220) {
      pdf.addPage();
      yPos = 30;
    }
    
    // Practice Information
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('Practice Information', 20, yPos);
    yPos += 15;
    
    // Practice name
    if (procedure.practiceName) {
      pdf.setFontSize(12);
      pdf.setFont(undefined, 'bold');
      pdf.text(procedure.practiceName, 20, yPos);
      yPos += 12;
    }
    
    // Office Hours
    const officeHours = procedure.practiceOfficeHours || 
                       procedure.officeHours || 
                       'Mon-Fri: 8:00 AM - 5:00 PM, Sat: 9:00 AM - 2:00 PM';
    
    pdf.setFontSize(10);
    pdf.setFont(undefined, 'bold');
    pdf.text('Office Hours:', 20, yPos);
    yPos += 8;
    pdf.setFont(undefined, 'normal');
    pdf.text(officeHours, 20, yPos);
    yPos += 8;
    
    // Emergency Contact
    const emergencyContact = procedure.practiceEmergencyContact || 
                           procedure.practicePhone ||
                           '(555) 123-4567';
    
    pdf.setFont(undefined, 'bold');
    pdf.text('Emergency Contact:', 20, yPos);
    yPos += 8;
    pdf.setFont(undefined, 'normal');
    pdf.text(formatPhoneNumber(emergencyContact), 20, yPos);
    
    // Save the PDF
    const filename = `${(procedure.name || 'Procedure').replace(/\s+/g, '_')}_ORIGINAL_FORMAT.pdf`;
    pdf.save(filename);
    
    console.log('✅ Simple PDF generated - raw overview text only:', filename);
    
    return true;
    
  } catch (error) {
    console.error('❌ PDF generation failed:', error);
    return false;
  }
};
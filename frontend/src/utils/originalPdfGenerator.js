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

// ORIGINAL PDF TEXT ONLY GENERATOR - TIMESTAMP: 2025-09-19
export const generateProcedurePDF = async (procedure) => {
  // FORCE ALERT TO SHOW NEW GENERATOR IS LOADING
  alert('🎯 ORIGINAL PDF TEXT GENERATOR LOADED - ' + new Date().toISOString());
  console.log('📄 ORIGINAL PDF TEXT GENERATOR - Using exact uploaded PDF text');
  console.log('📝 Procedure:', procedure.name);
  console.log('📝 Overview text:', procedure.overview ? procedure.overview.substring(0, 100) + '...' : 'No overview');
  
  try {
    const pdf = new jsPDF();
    
    pdf.setProperties({
      title: `${procedure.name || 'Procedure'} - Post-Operative Care Guide`,
      subject: 'Post-Operative Care Instructions',
      author: procedure.practiceName || 'Dental Practice',
      creator: 'Dental Practice Management System'
    });
    
    let yPos = 20;
    
    // Procedure Name
    pdf.setFontSize(16);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedure.name || 'Post-Operative Care', 20, yPos);
    yPos += 25;
    
    // EXACT OVERVIEW TEXT FROM ORIGINAL UPLOADED PDFs - NO CHANGES
    if (procedure.overview) {
      pdf.setFontSize(11);
      pdf.setFont(undefined, 'normal');
      
      // Use the text exactly as it is - just wrap for PDF width
      const textLines = pdf.splitTextToSize(procedure.overview, 170);
      
      textLines.forEach(line => {
        if (yPos > 270) {
          pdf.addPage();
          yPos = 20;
        }
        
        pdf.text(line, 20, yPos);
        yPos += 6;
      });
    } else {
      pdf.text('No post-operative instructions available.', 20, yPos);
    }
    
    // Add spacing
    yPos += 20;
    
    // Practice Information
    if (yPos > 220) {
      pdf.addPage();
      yPos = 30;
    }
    
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
    
    // Save with timestamp to show it's new
    const timestamp = Date.now();
    const filename = `${(procedure.name || 'Procedure').replace(/\s+/g, '_')}_ORIGINAL_${timestamp}.pdf`;
    pdf.save(filename);
    
    console.log('✅ PDF with original text generated:', filename);
    
    return true;
    
  } catch (error) {
    console.error('❌ PDF generation failed:', error);
    return false;
  }
};
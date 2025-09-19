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

// FINAL PDF GENERATOR - TIMESTAMP: 2025-09-19 - EXACT ORIGINAL PDF FORMAT
export const generateProcedurePDF = async (procedure) => {
  // CRITICAL ALERT - ENSURE NEW CODE IS LOADING
  alert('🚀 FINAL PDF GENERATOR v5.0 - LOADED SUCCESSFULLY! - ' + new Date().toISOString());
  console.log('🔥🔥🔥 FINAL PDF GENERATOR v5.0 - TIMESTAMP:', new Date().toISOString());
  console.log('📄 PROCEDURE DATA:', procedure);
  
  try {
    const pdf = new jsPDF();
    
    pdf.setProperties({
      title: `${procedure.name || 'Procedure'} - Post-Operative Care Guide`,
      subject: 'Post-Operative Care Instructions',
      author: procedure.practiceName || 'Dental Practice',
      creator: 'Dental Practice Management System'
    });
    
    let yPos = 20;
    
    // Procedure Name as title ONLY (no DENTAL RESCUE BOT as user requested)
    pdf.setFontSize(16);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedure.name || 'Post-Operative Care', 20, yPos);
    yPos += 25;
    
    // Raw overview text - ABSOLUTELY NO FORMATTING OR PROCESSING
    if (procedure.overview) {
      console.log('📝 Overview content length:', procedure.overview.length);
      console.log('📝 Overview preview:', procedure.overview.substring(0, 100));
      
      pdf.setFontSize(11);
      pdf.setFont(undefined, 'normal');
      
      // Simply display the raw text exactly as stored - no parsing whatsoever
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
    } else {
      console.log('❌ No overview content found');
      pdf.text('No post-operative care instructions available.', 20, yPos);
      yPos += 20;
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
    
    // Save the PDF with unique timestamp filename
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${(procedure.name || 'Procedure').replace(/\s+/g, '_')}_FINAL_v5_${timestamp}.pdf`;
    pdf.save(filename);
    
    console.log('✅ FINAL PDF v5.0 generated successfully:', filename);
    
    return true;
    
  } catch (error) {
    console.error('❌ FINAL PDF generation failed:', error);
    return false;
  }
};
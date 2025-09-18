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

// NEW PDF GENERATOR - EXACT USER FORMAT v4.0
export const generateProcedurePDF = async (procedure) => {
  // FORCE ALERT TO CONFIRM NEW CODE IS RUNNING
  alert('🎯 PDF GENERATOR v4.0 - EXACT USER FORMAT LOADED!');
  console.log('🔥 PDF Generator v4.0 - EXACT USER FORMAT - TIMESTAMP:', new Date().toISOString());
  
  try {
    const pdf = new jsPDF();
    
    pdf.setProperties({
      title: `${procedure.name || 'Procedure'} - Post-Operative Care Guide`,
      subject: 'Post-Operative Care Instructions',
      author: procedure.practiceName || 'Dental Practice',
      creator: 'Dental Practice Management System'
    });
    
    let yPos = 20;
    
    // Procedure Name as title (NO DENTAL RESCUE BOT - as user requested)
    pdf.setFontSize(16);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedure.name || 'Post-Operative Care', 20, yPos);
    yPos += 25;
    
    // Display overview content exactly as user showed in sample
    if (procedure.overview) {
      pdf.setFontSize(11);
      pdf.setFont(undefined, 'normal');
      
      // Split by lines and process each line exactly as user sample shows
      const lines = procedure.overview.split('\n');
      
      for (const line of lines) {
        const trimmedLine = line.trim();
        
        // Skip empty lines but add spacing
        if (!trimmedLine) {
          yPos += 5;
          continue;
        }
        
        // Check if we need a new page
        if (yPos > 260) {
          pdf.addPage();
          yPos = 20;
        }
        
        // Check if it's a section header (ends with :)
        // Handle all possible section headers including "First 24–48 Hours:"
        if (trimmedLine.endsWith(':')) {
          pdf.setFont(undefined, 'bold');
          pdf.text(trimmedLine, 20, yPos);
          pdf.setFont(undefined, 'normal');
          yPos += 12;
        }
        // Check if it's a bullet point (starts with -)
        else if (trimmedLine.startsWith('- ')) {
          const bulletText = trimmedLine.substring(2); // Remove "- "
          const wrappedLines = pdf.splitTextToSize(`- ${bulletText}`, 170);
          wrappedLines.forEach(wrappedLine => {
            pdf.text(wrappedLine, 20, yPos);
            yPos += 6;
          });
        }
        // Regular text (like Purpose description)
        else {
          const wrappedLines = pdf.splitTextToSize(trimmedLine, 170);
          wrappedLines.forEach(wrappedLine => {
            pdf.text(wrappedLine, 20, yPos);
            yPos += 6;
          });
        }
      }
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
    const wrappedHours = pdf.splitTextToSize(officeHours, 170);
    wrappedHours.forEach(line => {
      pdf.text(line, 20, yPos);
      yPos += 6;
    });
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
    const filename = `${(procedure.name || 'Procedure').replace(/\s+/g, '_')}_EXACT_FORMAT.pdf`;
    pdf.save(filename);
    
    console.log('✅ PDF generated with EXACT user format v4.0:', filename);
    
    return true;
    
  } catch (error) {
    console.error('❌ PDF generation failed:', error);
    return false;
  }
};
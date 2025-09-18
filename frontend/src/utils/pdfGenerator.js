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

// Generate PDF with RAW overview content - NO FORMATTING OR PARSING
export const generateProcedurePDF = async (procedure) => {
  console.log('🎯 PDF Generator - Creating PDF with RAW overview content (NO formatting)');
  console.log('📄 Input procedure:', {
    name: procedure.name,
    hasOverview: !!procedure.overview,
    overviewLength: procedure.overview ? procedure.overview.length : 0
  });
  
  try {
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
    
    // DENTAL RESCUE BOT Header
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('DENTAL RESCUE BOT', 20, yPos);
    yPos += 20;
    
    // Procedure Name
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedure.name || 'Post-Operative Care', 20, yPos);
    yPos += 20;
    
    // RAW Overview Content - NO PARSING, NO FORMATTING
    if (procedure.overview) {
      console.log('📖 Adding RAW overview content without any formatting...');
      
      pdf.setFontSize(11);
      pdf.setFont(undefined, 'normal');
      
      // Simply split the overview text to fit PDF width - NO OTHER PROCESSING
      const rawText = String(procedure.overview);
      const wrappedLines = pdf.splitTextToSize(rawText, 170);
      
      wrappedLines.forEach(line => {
        // Check if we need a new page
        if (yPos > 270) {
          pdf.addPage();
          yPos = 20;
        }
        
        pdf.text(line, 20, yPos);
        yPos += 6;
      });
      
      console.log(`📝 Added ${wrappedLines.length} lines of raw overview content`);
    } else {
      console.log('⚠️ No overview content found');
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
    
    // Practice Information Section
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'bold');
    pdf.text('Practice Information', 20, yPos);
    yPos += 15;
    
    // Practice name
    if (procedure.practiceName) {
      pdf.setFontSize(11);
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
    yPos += 12;
    
    // Generation timestamp
    pdf.setFontSize(8);
    pdf.setFont(undefined, 'italic');
    pdf.text(`Generated on ${new Date().toLocaleDateString()}`, 20, yPos);
    
    // Save the PDF
    const filename = `${(procedure.name || 'Procedure').replace(/\s+/g, '_')}_Care_Guide.pdf`;
    pdf.save(filename);
    
    console.log('✅ PDF generated with RAW overview content (no formatting):', filename);
    
    return true;
    
  } catch (error) {
    console.error('❌ PDF generation failed:', error);
    return false;
  }
};








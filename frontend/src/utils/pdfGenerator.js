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
  console.log('🏢 PDF Generator - Practice Info:', {
    practiceName: procedure.practiceName,
    practiceOfficeHours: procedure.practiceOfficeHours,
    practiceEmergencyContact: procedure.practiceEmergencyContact
  });
  try {
    console.log('🎨 Starting PDF generation...');
    
    // Create new PDF document
    const pdf = new jsPDF();
    
    // Set up document properties
    pdf.setProperties({
      title: `${procedure.name} - Post-Operative Care Guide`,
      subject: 'Post-Operative Care Instructions',
      author: procedure.practiceName || 'Your Dental Practice',
      creator: 'Dental Practice Management System'
    });
    
    // Header
    pdf.setFontSize(20);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedure.name, 20, 30);
    
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'normal');
    pdf.text('Post-Operative Care Instructions', 20, 45);
    
    // Practice info
    let yPos = 60;
    if (procedure.practiceName) {
      pdf.setFontSize(12);
      pdf.setFont(undefined, 'bold');
      pdf.text(procedure.practiceName, 20, yPos);
      yPos += 10;
    }
    
    if (procedure.practicePhone) {
      pdf.setFont(undefined, 'normal');
      pdf.text(`Phone: ${formatPhoneNumber(procedure.practicePhone)}`, 20, yPos);
      yPos += 10;
    }
    
    yPos += 10; // Add some space
    
    // ONLY OVERVIEW CONTENT - This is the key fix!
    if (procedure.overview) {
      pdf.setFontSize(16);
      pdf.setFont(undefined, 'bold');
      pdf.text('Post-Operative Care Instructions', 20, yPos);
      yPos += 15;
      
      // Format and add the overview content
      const formattedContent = formatOriginalPDFContent(procedure.overview);
      
      pdf.setFontSize(11);
      pdf.setFont(undefined, 'normal');
      
      // Split content into lines that fit the page width
      const lines = pdf.splitTextToSize(formattedContent, 170);
      
      // Add each line to the PDF
      for (let i = 0; i < lines.length; i++) {
        // Check if we need a new page
        if (yPos > 270) {
          pdf.addPage();
          yPos = 30;
        }
        
        pdf.text(lines[i], 20, yPos);
        yPos += 6;
      }
    }
    
    // Footer with practice information
    yPos = Math.max(yPos + 20, 280);
    if (yPos > 270) {
      pdf.addPage();
      yPos = 30;
    }
    
    pdf.setFontSize(10);
    pdf.setFont(undefined, 'italic');
    pdf.text(`Generated on ${new Date().toLocaleDateString()}`, 20, yPos);
    
    // Office Hours
    console.log('📅 Adding Office Hours to PDF:', procedure.practiceOfficeHours);
    if (procedure.practiceOfficeHours) {
      console.log('✅ Office Hours found, adding to PDF');
      yPos += 10;
      pdf.setFont(undefined, 'bold');
      pdf.text('Office Hours:', 20, yPos);
      yPos += 6;
      pdf.setFont(undefined, 'normal');
      pdf.text(procedure.practiceOfficeHours, 20, yPos);
    } else {
      console.log('❌ No Office Hours found in procedure object');
    }
    
    // Emergency Contact
    console.log('📞 Adding Emergency Contact to PDF:', procedure.practiceEmergencyContact);
    if (procedure.practiceEmergencyContact) {
      console.log('✅ Emergency Contact found, adding to PDF');
      yPos += 10;
      pdf.setFont(undefined, 'bold');
      pdf.text('Emergency Contact:', 20, yPos);
      yPos += 6;
      pdf.setFont(undefined, 'normal');
      pdf.text(formatPhoneNumber(procedure.practiceEmergencyContact), 20, yPos);
    } else if (procedure.practicePhone) {
      console.log('📞 Using practicePhone as Emergency Contact');
      yPos += 10;
      pdf.setFont(undefined, 'bold');
      pdf.text('Emergency Contact:', 20, yPos);
      yPos += 6;
      pdf.setFont(undefined, 'normal');
      pdf.text(formatPhoneNumber(procedure.practicePhone), 20, yPos);
    } else {
      console.log('❌ No Emergency Contact found in procedure object');
    }
    
    // Generate filename
    const filename = `${procedure.name.replace(/[^a-zA-Z0-9]/g, '_')}_Care_Guide.pdf`;
    
    // Download the PDF
    pdf.save(filename);
    
    console.log('✅ PDF downloaded successfully');
    
    // Show success message
    alert('✅ Care Guide Downloaded!\n\nYour simplified post-operative care guide has been downloaded as a PDF file.');
    
    return true;
    
  } catch (error) {
    console.error('❌ PDF generation failed:', error);
    alert('PDF generation failed: ' + error.message);
    return false;
  }
};








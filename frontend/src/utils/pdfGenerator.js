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

// Helper function to add structured content sections matching original PDF format
const addStructuredSection = (pdf, title, content, yPos) => {
  if (!content || (Array.isArray(content) && content.length === 0)) {
    return yPos;
  }

  // Check if we need a new page
  if (yPos > 240) {
    pdf.addPage();
    yPos = 20;
  }

  // Section title
  pdf.setFontSize(14);
  pdf.setFont(undefined, 'bold');
  pdf.text(title, 20, yPos);
  yPos += 12;

  // Section content
  pdf.setFontSize(11);
  pdf.setFont(undefined, 'normal');

  // Handle array or string content
  const contentItems = Array.isArray(content) ? content : content.split('\n');
  
  contentItems.forEach((item) => {
    const line = typeof item === 'string' ? item.trim() : '';
    if (!line) return;

    // Check if we need a new page
    if (yPos > 250) {
      pdf.addPage();
      yPos = 20;
    }

    // Clean up the line - remove existing bullet markers
    const cleanLine = line.replace(/^[•\-\*]\s*/, '');
    
    // Add bullet point
    const wrappedLines = pdf.splitTextToSize(`- ${cleanLine}`, 170);
    wrappedLines.forEach(wrappedLine => {
      pdf.text(wrappedLine, 25, yPos);
      yPos += 6;
    });
  });

  yPos += 10; // Spacing after section
  return yPos;
};

// Generate PDF matching exact original format
export const generateProcedurePDF = async (procedure) => {
  console.log('🎯 PDF Generator - Creating PDF matching original PostOp format');
  console.log('📄 Procedure data:', {
    name: procedure.name,
    hasOverview: !!procedure.overview,
    hasImmediateAftercare: !!procedure.immediateAftercare,
    hasDietRestrictions: !!procedure.dietRestrictions,
    hasWarningSignsToCallDoctor: !!procedure.warningSignsToCallDoctor,
    hasRecoveryTimeline: !!procedure.recoveryTimeline,
    hasMedications: !!procedure.medications
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
    
    // DENTAL RESCUE BOT Header (matching original)
    pdf.setFontSize(16);
    pdf.setFont(undefined, 'bold');
    pdf.text('DENTAL RESCUE BOT', 20, yPos);
    yPos += 20;
    
    // Procedure Name
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedure.name || 'Post-Operative Care', 20, yPos);
    yPos += 20;
    
    // Purpose section (from overview if available)
    if (procedure.overview) {
      // Extract purpose from overview or use overview as purpose
      let purposeText = procedure.overview;
      
      // Try to extract purpose if it exists in the overview
      const purposeMatch = purposeText.match(/Purpose:\s*([^\.]+\.)/i);
      if (purposeMatch) {
        purposeText = purposeMatch[1];
      } else {
        // If no specific purpose found, use first sentence or brief description
        const firstSentence = purposeText.split('.')[0] + '.';
        if (firstSentence.length < 200) {
          purposeText = firstSentence;
        }
      }
      
      pdf.setFontSize(12);
      pdf.setFont(undefined, 'bold');
      pdf.text('Purpose:', 20, yPos);
      yPos += 8;
      
      pdf.setFont(undefined, 'normal');
      const wrappedPurpose = pdf.splitTextToSize(purposeText, 170);
      wrappedPurpose.forEach(line => {
        pdf.text(line, 20, yPos);
        yPos += 6;
      });
      yPos += 15;
    }
    
    // First 24 Hours (from immediateAftercare)
    if (procedure.immediateAftercare) {
      yPos = addStructuredSection(pdf, 'First 24 Hours:', procedure.immediateAftercare, yPos);
    }
    
    // Pain & Sensitivity (from medications if available, or extract from overview)
    if (procedure.medications) {
      // Look for pain-related content in medications
      const painContent = Array.isArray(procedure.medications) 
        ? procedure.medications.filter(med => 
            med.toLowerCase().includes('pain') || 
            med.toLowerCase().includes('otc') ||
            med.toLowerCase().includes('medication')
          ) 
        : procedure.medications.split('\n').filter(med => 
            med.toLowerCase().includes('pain') || 
            med.toLowerCase().includes('otc') ||
            med.toLowerCase().includes('medication')
          );
      
      if (painContent.length > 0) {
        yPos = addStructuredSection(pdf, 'Pain & Sensitivity:', painContent, yPos);
      }
    }
    
    // Oral Hygiene (extract from overview or use general instruction)
    const oralHygieneContent = ['Brush and floss normally, avoiding excessive pressure on the treated area.'];
    yPos = addStructuredSection(pdf, 'Oral Hygiene:', oralHygieneContent, yPos);
    
    // Diet (from dietRestrictions)
    if (procedure.dietRestrictions) {
      yPos = addStructuredSection(pdf, 'Diet:', procedure.dietRestrictions, yPos);
    }
    
    // Special Precautions (from warningSignsToCallDoctor or overview)
    if (procedure.warningSignsToCallDoctor) {
      // Convert warning signs to precautions format
      const precautionContent = Array.isArray(procedure.warningSignsToCallDoctor)
        ? procedure.warningSignsToCallDoctor.map(warning => 
            `Watch for ${warning.toLowerCase()}`)
        : procedure.warningSignsToCallDoctor.split('\n').map(warning => 
            `Watch for ${warning.toLowerCase()}`);
      
      yPos = addStructuredSection(pdf, 'Special Precautions:', precautionContent, yPos);
    }
    
    // Follow-Up (from recoveryTimeline or general instruction)
    let followUpContent = [];
    if (procedure.recoveryTimeline) {
      followUpContent = Array.isArray(procedure.recoveryTimeline) 
        ? procedure.recoveryTimeline 
        : procedure.recoveryTimeline.split('\n');
    } else {
      followUpContent = ['Contact the office if pain worsens, swelling develops, or you notice signs of infection.'];
    }
    
    // Add standard follow-up instruction
    followUpContent.push('Follow-up appointments are important for monitoring healing progress.');
    
    yPos = addStructuredSection(pdf, 'Follow-Up:', followUpContent, yPos);
    
    // Practice Information Footer
    yPos += 20;
    
    // Check if we need a new page for practice info
    if (yPos > 220) {
      pdf.addPage();
      yPos = 30;
    }
    
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('Practice Information', 20, yPos);
    yPos += 20;
    
    // Practice name
    if (procedure.practiceName) {
      pdf.setFontSize(12);
      pdf.setFont(undefined, 'bold');
      pdf.text(procedure.practiceName, 20, yPos);
      yPos += 15;
    }
    
    // Office Hours
    const officeHours = procedure.practiceOfficeHours || 
                       procedure.officeHours || 
                       'Mon-Fri: 8:00 AM - 5:00 PM, Sat: 9:00 AM - 2:00 PM';
    
    pdf.setFontSize(11);
    pdf.setFont(undefined, 'bold');
    pdf.text('Office Hours:', 20, yPos);
    yPos += 8;
    pdf.setFont(undefined, 'normal');
    const wrappedHours = pdf.splitTextToSize(officeHours, 170);
    wrappedHours.forEach(line => {
      pdf.text(line, 20, yPos);
      yPos += 6;
    });
    yPos += 10;
    
    // Emergency Contact
    const emergencyContact = procedure.practiceEmergencyContact || 
                           procedure.practicePhone ||
                           '(555) 123-4567';
    
    pdf.setFont(undefined, 'bold');
    pdf.text('Emergency Contact:', 20, yPos);
    yPos += 8;
    pdf.setFont(undefined, 'normal');
    pdf.text(formatPhoneNumber(emergencyContact), 20, yPos);
    yPos += 15;
    
    // Generation timestamp
    pdf.setFontSize(9);
    pdf.setFont(undefined, 'italic');
    pdf.text(`Generated on ${new Date().toLocaleDateString()}`, 20, yPos);
    
    // Save the PDF
    const filename = `${(procedure.name || 'Procedure').replace(/\s+/g, '_')}_Care_Guide.pdf`;
    pdf.save(filename);
    
    console.log('✅ PDF generated successfully matching original format:', filename);
    
    return true;
    
  } catch (error) {
    console.error('❌ PDF generation failed:', error);
    return false;
  }
};








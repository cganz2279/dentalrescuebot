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

// Helper function to parse the overview text and extract sections exactly as in original PDFs
const parseOverviewSections = (overviewText) => {
  if (!overviewText) return [];
  
  const sections = [];
  
  // Define the section patterns exactly as they appear in original PDFs
  const sectionPatterns = [
    'Purpose:',
    'First 24 Hours:',
    'Pain & Sensitivity:',
    'Oral Hygiene:',
    'Diet:',
    'Special Precautions:',
    'Follow-Up:'
  ];
  
  // Find all section positions
  const sectionPositions = [];
  sectionPatterns.forEach(pattern => {
    const index = overviewText.indexOf(pattern);
    if (index !== -1) {
      sectionPositions.push({ pattern, index });
    }
  });
  
  // Sort by position
  sectionPositions.sort((a, b) => a.index - b.index);
  
  // Extract each section's content
  sectionPositions.forEach((section, i) => {
    const startIndex = section.index + section.pattern.length;
    const endIndex = i < sectionPositions.length - 1 
      ? sectionPositions[i + 1].index 
      : overviewText.length;
    
    const content = overviewText.substring(startIndex, endIndex).trim();
    
    if (content) {
      // Split content by bullet points or sentences
      const items = content
        .split(/(?:^|\s+)-\s+/) // Split by bullet points
        .map(item => item.trim())
        .filter(item => item.length > 0)
        .map(item => {
          // Clean up and ensure proper formatting
          if (!item.startsWith('-') && !item.startsWith('•')) {
            // For non-bullet items, check if they should be split into bullets
            if (item.includes('. ') && item.length > 100) {
              return item.split('. ').filter(s => s.length > 0).map(s => s.endsWith('.') ? s : s + '.');
            }
            return [item];
          }
          return [item.replace(/^[-•]\s*/, '')];
        })
        .flat();
      
      sections.push({
        title: section.pattern,
        content: items
      });
    }
  });
  
  return sections;
};

// Helper function to add a section to PDF with exact original formatting
const addPDFSection = (pdf, title, content, yPos) => {
  if (!content || content.length === 0) {
    return yPos;
  }

  // Check if we need a new page
  if (yPos > 240) {
    pdf.addPage();
    yPos = 20;
  }

  // Section title
  pdf.setFontSize(12);
  pdf.setFont(undefined, 'bold');
  pdf.text(title, 20, yPos);
  yPos += 10;

  // Section content
  pdf.setFontSize(11);
  pdf.setFont(undefined, 'normal');

  content.forEach((item) => {
    if (!item || item.trim().length === 0) return;

    // Check if we need a new page
    if (yPos > 250) {
      pdf.addPage();
      yPos = 20;
    }

    const cleanItem = item.trim();
    
    // Add bullet point formatting for content items
    if (title !== 'Purpose:') {
      const wrappedLines = pdf.splitTextToSize(`- ${cleanItem}`, 170);
      wrappedLines.forEach(line => {
        pdf.text(line, 25, yPos);
        yPos += 6;
      });
    } else {
      // Purpose section - no bullets
      const wrappedLines = pdf.splitTextToSize(cleanItem, 170);
      wrappedLines.forEach(line => {
        pdf.text(line, 20, yPos);
        yPos += 6;
      });
    }
  });

  yPos += 8; // Spacing after section
  return yPos;
};

// Generate PDF matching exact original PostOp document format
export const generateProcedurePDF = async (procedure) => {
  console.log('🎯 PDF Generator - Creating PDF matching exact original PostOp format');
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
    
    // DENTAL RESCUE BOT Header (exactly as in original)
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('DENTAL RESCUE BOT', 20, yPos);
    yPos += 20;
    
    // Procedure Name (exactly as in original)
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedure.name || 'Post-Operative Care', 20, yPos);
    yPos += 20;
    
    // Parse and render sections from overview
    if (procedure.overview) {
      console.log('📖 Parsing overview content...');
      const sections = parseOverviewSections(procedure.overview);
      console.log('📑 Found sections:', sections.map(s => s.title));
      
      sections.forEach(section => {
        yPos = addPDFSection(pdf, section.title, section.content, yPos);
      });
    } else {
      // Fallback if no overview - use structured fields
      console.log('⚠️ No overview found, using structured fields...');
      
      if (procedure.immediateAftercare) {
        yPos = addPDFSection(pdf, 'First 24 Hours:', 
          Array.isArray(procedure.immediateAftercare) 
            ? procedure.immediateAftercare 
            : procedure.immediateAftercare.split('\n'), 
          yPos);
      }
      
      if (procedure.dietRestrictions) {
        yPos = addPDFSection(pdf, 'Diet:', 
          Array.isArray(procedure.dietRestrictions) 
            ? procedure.dietRestrictions 
            : procedure.dietRestrictions.split('\n'), 
          yPos);
      }
      
      if (procedure.warningSignsToCallDoctor) {
        yPos = addPDFSection(pdf, 'Follow-Up:', 
          Array.isArray(procedure.warningSignsToCallDoctor) 
            ? procedure.warningSignsToCallDoctor 
            : procedure.warningSignsToCallDoctor.split('\n'), 
          yPos);
      }
    }
    
    // Add some spacing before practice information
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
    
    console.log('✅ PDF generated successfully matching original PostOp format:', filename);
    console.log('✅ Practice info included:', {
      name: procedure.practiceName,
      hours: officeHours,
      emergency: emergencyContact
    });
    
    return true;
    
  } catch (error) {
    console.error('❌ PDF generation failed:', error);
    return false;
  }
};








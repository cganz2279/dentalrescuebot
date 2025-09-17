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

// Helper function to add formatted content with proper sections to PDF
const addFormattedContent = (pdf, overviewText, startY) => {
  let yPos = startY;
  
  // Parse content into sections using the same logic as the frontend
  const sections = [];
  let currentSection = null;
  
  // Split by section headers that are followed by content
  const sectionPattern = /\b([A-Z][a-zA-Z\s&]+):\s*/g;
  let lastIndex = 0;
  let match;
  
  while ((match = sectionPattern.exec(overviewText)) !== null) {
    // If we have a previous section, get its content
    if (currentSection) {
      const sectionContent = overviewText.substring(lastIndex, match.index).trim();
      if (sectionContent) {
        // Split content by sentences and bullet points
        const contentLines = sectionContent
          .split(/[.]\s+/) // Split by sentences
          .map(line => line.trim())
          .filter(line => line.length > 0)
          .map(line => line.endsWith('.') ? line : line + '.'); // Ensure sentences end with period
        
        currentSection.content = contentLines;
      }
      sections.push(currentSection);
    }
    
    // Start new section
    currentSection = {
      title: match[1] + ':',
      content: []
    };
    lastIndex = match.index + match[0].length;
  }
  
  // Handle the last section
  if (currentSection) {
    const sectionContent = overviewText.substring(lastIndex).trim();
    if (sectionContent) {
      const contentLines = sectionContent
        .split(/[.]\s+/)
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(line => line.endsWith('.') ? line : line + '.');
      
      currentSection.content = contentLines;
    }
    sections.push(currentSection);
  }
  
  // If no sections were found, treat the entire content as one section
  if (sections.length === 0 && overviewText) {
    sections.push({
      title: 'Post-Operative Instructions:',
      content: overviewText
        .split(/[.]\s+/)
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(line => line.endsWith('.') ? line : line + '.')
    });
  }
  
  // Render sections in PDF
  sections.forEach((section, sectionIndex) => {
    // Check if we need a new page
    if (yPos > 240) {
      pdf.addPage();
      yPos = 20;
    }
    
    // Section header
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text(section.title, 20, yPos);
    yPos += 12;
    
    // Section content
    pdf.setFontSize(11);
    pdf.setFont(undefined, 'normal');
    
    section.content.forEach((item, index) => {
      const line = typeof item === 'string' ? item.trim() : '';
      if (!line) return;
      
      // Check if we need a new page
      if (yPos > 250) {
        pdf.addPage();
        yPos = 20;
      }
      
      // Handle bullet points
      if (line.startsWith('•') || line.startsWith('-')) {
        const bulletText = line.replace(/^[•-]\s*/, '');
        const wrappedLines = pdf.splitTextToSize(`• ${bulletText}`, 170);
        wrappedLines.forEach(wrappedLine => {
          pdf.text(wrappedLine, 25, yPos);
          yPos += 6;
        });
      }
      // Handle lines that contain bullet points within them
      else if (line.includes(' - ') || line.includes(' • ')) {
        // Split the line by bullet markers and create separate bullet items
        const parts = line.split(/\s+[-•]\s+/);
        const introText = parts[0].trim();
        
        // Add intro text if it exists
        if (introText && !introText.match(/^[-•]/)) {
          const wrappedIntro = pdf.splitTextToSize(introText, 170);
          wrappedIntro.forEach(wrappedLine => {
            pdf.text(wrappedLine, 20, yPos);
            yPos += 6;
          });
        }
        
        // Add bullet points
        parts.slice(1).forEach((bulletText) => {
          if (bulletText.trim()) {
            const wrappedLines = pdf.splitTextToSize(`• ${bulletText.trim()}`, 170);
            wrappedLines.forEach(wrappedLine => {
              pdf.text(wrappedLine, 25, yPos);
              yPos += 6;
            });
          }
        });
      }
      // Regular paragraphs
      else if (line.length > 0) {
        const wrappedLines = pdf.splitTextToSize(line, 170);
        wrappedLines.forEach(wrappedLine => {
          pdf.text(wrappedLine, 20, yPos);
          yPos += 6;
        });
      }
      
      yPos += 2; // Small spacing between items
    });
    
    yPos += 10; // Spacing between sections
  });
  
  return yPos;
};


// Generate actual PDF file using jsPDF with proper formatting to match screen display
export const generateProcedurePDF = async (procedure) => {
  console.log('🎯 PDF Generator Entry - Procedure Object:', procedure);
  
  try {
    console.log('🎨 Starting STRUCTURED PDF generation...');
    
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
    
    // Parse and format the overview content with proper sections
    if (procedure.overview) {
      const overviewText = String(procedure.overview).replace(/\[object Object\]/g, '').trim();
      if (overviewText) {
        yPos = addFormattedContent(pdf, overviewText, yPos);
      }
    }
    
    // ALWAYS add Office Hours and Emergency Contact at the end
    // Force a new page for footer to ensure visibility
    pdf.addPage();
    yPos = 30;
    
    // FORCE Office Hours - Use any available source
    const officeHours = procedure.practiceOfficeHours || 
                       procedure.officeHours || 
                       'Mon-Fri: 8:00 AM - 5:00 PM (EST/EDT) • Sat: 9:00 AM - 2:00 PM';
    
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('Practice Information', 20, yPos);
    yPos += 20;
    
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'bold');
    pdf.text('Office Hours:', 20, yPos);
    yPos += 10;
    pdf.setFont(undefined, 'normal');
    pdf.text(officeHours, 20, yPos);
    yPos += 20;
    
    // FORCE Emergency Contact - Use any available source  
    const emergencyContact = procedure.practiceEmergencyContact || 
                           procedure.emergencyContact ||
                           procedure.practicePhone ||
                           '📞 (555) 123-4567 • 🚨 Emergency Line';
    
    pdf.setFont(undefined, 'bold');
    pdf.text('Emergency Contact:', 20, yPos);
    yPos += 10;
    pdf.setFont(undefined, 'normal');
    pdf.text(formatPhoneNumber(emergencyContact), 20, yPos);
    yPos += 20;
    
    // Generation timestamp
    pdf.setFontSize(10);
    pdf.setFont(undefined, 'italic');
    pdf.text(`Generated on ${new Date().toLocaleDateString()}`, 20, yPos);
    
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








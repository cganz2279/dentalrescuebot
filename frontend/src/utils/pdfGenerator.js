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

// Helper function to parse overview text into exact sections matching original PostOp PDFs
const parseOriginalPostOpSections = (overviewText) => {
  if (!overviewText) return [];
  
  console.log('📖 Parsing overview text:', overviewText.substring(0, 200) + '...');
  
  const sections = [];
  
  // Split the overview by clear section patterns exactly as they appear in original PDFs
  const sectionRegex = /(Purpose|First 24 Hours|Pain & Sensitivity|Oral Hygiene|Diet|Special Precautions|Follow-Up):\s*/g;
  
  let lastIndex = 0;
  let match;
  const matches = [];
  
  // Find all section headers
  while ((match = sectionRegex.exec(overviewText)) !== null) {
    matches.push({
      title: match[1] + ':',
      startIndex: match.index,
      headerEnd: match.index + match[0].length
    });
  }
  
  // Extract content for each section
  matches.forEach((currentMatch, index) => {
    const nextMatch = matches[index + 1];
    const endIndex = nextMatch ? nextMatch.startIndex : overviewText.length;
    
    // Get the content between current header and next header (or end)
    const rawContent = overviewText.substring(currentMatch.headerEnd, endIndex).trim();
    
    if (rawContent) {
      // Parse content into bullet points, preserving original structure
      let contentItems = [];
      
      // Split by lines first, then check for bullet patterns
      const lines = rawContent.split(/\n+/).filter(line => line.trim());
      
      for (const line of lines) {
        const trimmedLine = line.trim();
        if (!trimmedLine) continue;
        
        // Check if line contains bullet points (- markers)
        if (trimmedLine.includes(' - ')) {
          // Split by bullet markers and add each as separate item
          const parts = trimmedLine.split(' - ');
          const prefix = parts[0].trim();
          
          // If there's a prefix before bullets, add it
          if (prefix && !prefix.match(/^-/)) {
            contentItems.push(prefix);
          }
          
          // Add each bullet point
          parts.slice(1).forEach(bulletText => {
            if (bulletText.trim()) {
              contentItems.push(bulletText.trim());
            }
          });
        } else if (trimmedLine.startsWith('- ')) {
          // Already a bullet point
          contentItems.push(trimmedLine.substring(2).trim());
        } else {
          // Regular content - split by sentences if very long
          if (trimmedLine.length > 150 && trimmedLine.includes('. ')) {
            const sentences = trimmedLine.split('. ').filter(s => s.trim());
            sentences.forEach((sentence, i) => {
              const cleanSentence = sentence.trim();
              if (cleanSentence) {
                // Add period back if not last sentence or doesn't end with punctuation
                const finalSentence = cleanSentence.match(/[.!?]$/) || i === sentences.length - 1
                  ? cleanSentence 
                  : cleanSentence + '.';
                contentItems.push(finalSentence);
              }
            });
          } else {
            contentItems.push(trimmedLine);
          }
        }
      }
      
      if (contentItems.length > 0) {
        sections.push({
          title: currentMatch.title,
          content: contentItems
        });
        console.log(`📑 Parsed section "${currentMatch.title}" with ${contentItems.length} items`);
      }
    }
  });
  
  console.log(`📚 Total sections parsed: ${sections.length}`);
  return sections;
};

// Helper function to add a section to PDF with exact original formatting
const addOriginalPDFSection = (pdf, title, content, yPos) => {
  if (!content || content.length === 0) {
    return yPos;
  }

  // Check if we need a new page
  if (yPos > 240) {
    pdf.addPage();
    yPos = 20;
  }

  // Section title with exact original formatting
  pdf.setFontSize(12);
  pdf.setFont(undefined, 'bold');
  pdf.text(title, 20, yPos);
  yPos += 12;

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
    
    // Format content with bullet points (except for Purpose section)
    if (title === 'Purpose:') {
      // Purpose section - no bullets, just plain text
      const wrappedLines = pdf.splitTextToSize(cleanItem, 170);
      wrappedLines.forEach(line => {
        pdf.text(line, 20, yPos);
        yPos += 6;
      });
    } else {
      // All other sections - add bullet points
      const wrappedLines = pdf.splitTextToSize(`- ${cleanItem}`, 170);
      wrappedLines.forEach(line => {
        pdf.text(line, 20, yPos);
        yPos += 6;
      });
    }
  });

  yPos += 10; // Spacing after section
  return yPos;
};

// Generate PDF exactly matching original PostOp document format
export const generateProcedurePDF = async (procedure) => {
  console.log('🎯 PDF Generator - Creating PDF matching EXACT original PostOp format');
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
    
    // DENTAL RESCUE BOT Header (exactly as in original PDFs)
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('DENTAL RESCUE BOT', 20, yPos);
    yPos += 20;
    
    // Procedure Name (exactly as in original PDFs)
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedure.name || 'Post-Operative Care', 20, yPos);
    yPos += 20;
    
    // Parse and render sections from overview text
    if (procedure.overview) {
      console.log('📖 Parsing overview content for exact original format...');
      const sections = parseOriginalPostOpSections(procedure.overview);
      console.log('📑 Found sections:', sections.map(s => s.title));
      
      // Render each section exactly as in original PDFs
      sections.forEach(section => {
        yPos = addOriginalPDFSection(pdf, section.title, section.content, yPos);
      });
    } else {
      console.log('⚠️ No overview found - cannot match original format');
      
      // Add a generic message
      pdf.setFontSize(11);
      pdf.setFont(undefined, 'normal');
      pdf.text('Post-operative care instructions not available.', 20, yPos);
      yPos += 20;
    }
    
    // Add spacing before practice information
    yPos += 20;
    
    // Check if we need a new page for practice info
    if (yPos > 220) {
      pdf.addPage();
      yPos = 30;
    }
    
    // Practice Information Section (as in original PDFs)
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
    
    console.log('✅ PDF generated successfully matching EXACT original PostOp format:', filename);
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








import jsPDF from 'jspdf';

// Function to load base64 logo from the text file
async function getBase64Logo() {
  try {
    const response = await fetch('/dental-rescue-logo-base64.txt');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const base64String = await response.text();
    return base64String.trim(); // Remove any whitespace/newlines
  } catch (error) {
    console.log('Failed to load base64 logo:', error);
    return null;
  }
}

// ENHANCED PDF GENERATOR WITH LOGO AND BOLD FORMATTING
export const generateProcedurePDF = async (procedure) => {
  // Force timestamp to bust cache
  const timestamp = new Date().toISOString();
  const cacheKey = Date.now();
  
  console.log('🚨 ENHANCED PDF WITH LOGO GENERATOR LOADED - v14 (Comprehensive Keywords)');
  console.log('🚨 TIMESTAMP:', timestamp);
  console.log('🚨 CACHE KEY:', cacheKey);
  console.log('🚨 PROCEDURE DATA:', procedure);
  
  try {
    const pdf = new jsPDF();
    let yPos = 20;
    
    // Add logo at the top centered using base64
    try {
      // Get the base64 logo string
      const base64Logo = await getBase64Logo();
      
      if (base64Logo) {
        // Calculate centered position for logo
        const imgWidth = 40; // Desired width
        const imgHeight = 30; // Desired height
        const xPos = (pdf.internal.pageSize.width - imgWidth) / 2; // Center horizontally
        
        // Add logo to PDF using base64 data
        pdf.addImage(`data:image/png;base64,${base64Logo}`, 'PNG', xPos, yPos, imgWidth, imgHeight);
        yPos += imgHeight + 10; // Move down after logo
        
        console.log('✅ Logo successfully added from base64 data');
      } else {
        throw new Error('Base64 logo not available');
      }
    } catch (logoError) {
      console.log('Logo loading failed, using text header:', logoError);
      // Fall back to text header
      pdf.setFontSize(18);
      pdf.setFont(undefined, 'bold');
      pdf.setTextColor(41, 98, 184);
      pdf.text('DENTAL RESCUE NOTES', 105, yPos, { align: 'center' });
      yPos += 15;
    }
    
    // Subtitle
    pdf.setFontSize(10);
    pdf.setFont(undefined, 'normal');
    pdf.setTextColor(100, 100, 100);
    pdf.text('Post-Operative Care Instructions', 105, yPos, { align: 'center' });
    yPos += 15;
    
    // Decorative line under the header
    pdf.setDrawColor(41, 98, 184);
    pdf.setLineWidth(1);
    pdf.line(50, yPos, 160, yPos);
    yPos += 20;
    
    // Title - handle different data structures
    const procedureName = procedure?.name || procedure?.procedureName || 'Procedure';
    pdf.setTextColor(0, 0, 0); // Reset to black
    pdf.setFontSize(16);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedureName, 20, yPos);
    yPos += 20;
    
    // Get the overview content
    const overviewContent = procedure?.overview || 
                           procedure?.procedureDetails?.overview || 
                           procedure?.procedureData?.overview ||
                           '';
    
    if (overviewContent) {
      // Simple approach: render text normally and use different method for emphasis
      console.log('📝 Using simple text rendering approach...');
      
      // Add formatted content to PDF with simple bold detection
      addSimpleFormattedContentToPDF(pdf, overviewContent, yPos);
      
    } else {
      pdf.setFontSize(11);
      pdf.text('No overview content available', 20, yPos);
      console.log('⚠️ No overview content found in procedure data structure');
    }
    
    // Add practice information footer
    addPracticeFooter(pdf, procedure);
    
    // Save with timestamp filename
    const filenameProcedureName = procedure?.name || procedure?.procedureName || 'Procedure';
    const filename = `${filenameProcedureName.replace(/[^a-zA-Z0-9]/g, '_')}_RAW_${cacheKey}.pdf`;
    pdf.save(filename);
    
    console.log('🚨 ENHANCED PDF SAVED:', filename);
    
    return true;
    
  } catch (error) {
    console.error('🚨 ENHANCED PDF ERROR:', error);
    return false;
  }
};

// Function to process content and identify words/phrases that should be bold
function processContentForBoldFormatting(content) {
  const boldKeywords = [
    'Purpose',
    'Instructions',
    'First 24 Hours',
    'First 24 hours',
    'First Twenty-Four Hours',
    'Pain & Sensitivity',
    'Pain and Sensitivity',
    'Pain & Swelling',
    'Pain and Swelling',
    'Pain Management',
    'Pain Control',
    'Bleeding',
    'Blood/Bleeding',
    'Oral Hygiene',
    'Oral Care',
    'Mouth Care',
    'Diet',
    'Dietary Instructions',
    'Eating',
    'Food',
    'Special Precautions',
    'Precautions',
    'Important Notes',
    'Follow-Up',
    'Follow Up',
    'Follow-up',
    'Followup',
    'Next Appointment',
    'Return Visit',
    'Activity',
    'Activities',
    'Medications',
    'Medicine',
    'Swelling',
    'Ice/Cold Therapy',
    'Ice Application',
    'Healing',
    'Recovery',
    'Warning Signs',
    'When to Call',
    'Emergency'
  ];
  
  // Create an array of content segments with formatting info
  const segments = [];
  let remainingContent = content;
  
  while (remainingContent.length > 0) {
    let foundKeyword = false;
    let earliestIndex = remainingContent.length;
    let matchedKeyword = null;
    
    // Find the earliest occurring keyword
    for (const keyword of boldKeywords) {
      const regex = new RegExp(`\\b${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
      const match = remainingContent.match(regex);
      
      if (match && match.index < earliestIndex) {
        earliestIndex = match.index;
        matchedKeyword = {
          keyword: keyword,
          actualText: match[0],
          index: match.index
        };
        foundKeyword = true;
      }
    }
    
    if (foundKeyword && matchedKeyword) {
      // Add text before the keyword as normal
      if (matchedKeyword.index > 0) {
        const beforeText = remainingContent.substring(0, matchedKeyword.index);
        if (beforeText.trim()) {
          segments.push({
            text: beforeText,
            bold: false
          });
        }
      }
      
      // Add the keyword as bold
      segments.push({
        text: matchedKeyword.actualText,
        bold: true
      });
      
      // Continue with remaining text
      remainingContent = remainingContent.substring(matchedKeyword.index + matchedKeyword.actualText.length);
    } else {
      // No more keywords, add remaining text as normal
      if (remainingContent.trim()) {
        segments.push({
          text: remainingContent,
          bold: false
        });
      }
      break;
    }
  }
  
  return segments;
}

// Function to add practice information footer to all pages
function addPracticeFooter(pdf, procedure) {
  const pageCount = pdf.internal.getNumberOfPages();
  
  // Extract practice information from procedure data
  const practiceName = procedure?.practiceName || 
                      procedure?.practice?.name || 
                      procedure?.practiceData?.name || 
                      'Your Practice Name';
                      
  const practicePhone = procedure?.practicePhone || 
                       procedure?.practice?.phone || 
                       procedure?.practiceData?.phone ||
                       procedure?.practiceEmergencyContact || 
                       procedure?.practice?.emergencyContact ||
                       'Contact Number Not Available';

  console.log('📋 Adding practice footer:', { practiceName, practicePhone });
  
  // Add footer to all pages
  for (let i = 1; i <= pageCount; i++) {
    pdf.setPage(i);
    
    // Footer styling
    pdf.setFont('times', 'normal');
    pdf.setFontSize(10);
    pdf.setTextColor(80, 80, 80); // Gray color
    
    // Add a line above footer
    pdf.setDrawColor(200, 200, 200);
    pdf.setLineWidth(0.5);
    pdf.line(20, 275, 190, 275);
    
    // Practice name (left side)
    pdf.text(practiceName, 20, 285);
    
    // Practice phone (right side)
    const phoneText = `Phone: ${practicePhone}`;
    const phoneTextWidth = pdf.getTextWidth(phoneText);
    pdf.text(phoneText, 190 - phoneTextWidth, 285);
    
    // Page number (center)
    if (pageCount > 1) {
      const pageText = `Page ${i} of ${pageCount}`;
      const pageTextWidth = pdf.getTextWidth(pageText);
      pdf.text(pageText, (210 - pageTextWidth) / 2, 290);
    }
  }
  
  // Reset text color
  pdf.setTextColor(0, 0, 0);
}
function addSimpleFormattedContentToPDF(pdf, content, startY) {
  let yPos = startY;
  const lineHeight = 5.5;
  const maxWidth = 170;
  const leftMargin = 20;
  
  // Set consistent font
  pdf.setFont('times', 'normal');
  pdf.setFontSize(11);
  pdf.setTextColor(0, 0, 0);
  
  // Define bold keywords first
  const boldKeywords = [
    'Purpose',
    'Instructions',
    'First 24 Hours',
    'First 24 hours',
    'First Twenty-Four Hours',
    'Pain & Sensitivity',
    'Pain and Sensitivity',
    'Pain & Swelling',
    'Pain and Swelling',
    'Pain Management',
    'Pain Control',
    'Bleeding',
    'Blood/Bleeding',
    'Oral Hygiene',
    'Oral Care',
    'Mouth Care',
    'Diet',
    'Dietary Instructions',
    'Eating',
    'Food',
    'Special Precautions',
    'Precautions',
    'Important Notes',
    'Follow-Up',
    'Follow Up',
    'Follow-up',
    'Followup',
    'Next Appointment',
    'Return Visit',
    'Activity',
    'Activities',
    'Medications',
    'Medicine',
    'Swelling',
    'Ice/Cold Therapy',
    'Ice Application',
    'Healing',
    'Recovery',
    'Warning Signs',
    'When to Call',
    'Emergency'
  ];
  
  console.log('📝 Using simple text rendering - preserving original formatting');
  console.log('📝 Bold keywords to search for:', boldKeywords);
  
  // Split content into lines using jsPDF's built-in function
  const lines = pdf.splitTextToSize(content, maxWidth);
  
  for (const line of lines) {
    // Check if we need a new page
    if (yPos > 275) {
      pdf.addPage();
      yPos = 20;
      pdf.setFont('times', 'normal');
      pdf.setFontSize(11);
    }
    
    // Check if this line contains any of our keywords for bold formatting
    let shouldBeBold = false;
    for (const keyword of boldKeywords) {
      // Use simple case-insensitive includes for more reliable matching
      if (line.toLowerCase().includes(keyword.toLowerCase())) {
        shouldBeBold = true;
        console.log(`📝 Making line bold (contains "${keyword}"): ${line.substring(0, 40)}...`);
        break;
      }
    }
    
    // Apply formatting and render line
    if (shouldBeBold) {
      pdf.setFont('times', 'bold');
    } else {
      pdf.setFont('times', 'normal');
    }
    
    pdf.text(line, leftMargin, yPos);
    yPos += lineHeight;
  }
  
  // Reset font
  pdf.setFont('times', 'normal');
}
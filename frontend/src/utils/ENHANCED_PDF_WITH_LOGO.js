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
  
  console.log('🚨 ENHANCED PDF WITH LOGO GENERATOR LOADED - v4');
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
      // Process content with bold formatting for specific keywords
      console.log('📝 Processing content for bold formatting...');
      const contentWithBoldFormatting = processContentForBoldFormatting(overviewContent);
      
      console.log(`📝 Found ${contentWithBoldFormatting.length} text segments for formatting`);
      const boldSegments = contentWithBoldFormatting.filter(s => s.bold);
      console.log(`📝 Bold segments: ${boldSegments.length}`);
      boldSegments.forEach((segment, index) => {
        console.log(`📝 Bold segment ${index + 1}: "${segment.text}"`);
      });
      
      // Add formatted content to PDF
      addFormattedContentToPDF(pdf, contentWithBoldFormatting, yPos);
      
    } else {
      pdf.setFontSize(11);
      pdf.text('No overview content available', 20, yPos);
      console.log('⚠️ No overview content found in procedure data structure');
    }
    
    // Footer with timestamp
    const pageCount = pdf.internal.getNumberOfPages();
    pdf.setPage(pageCount);
    pdf.setFontSize(8);
    pdf.text(`Generated: ${timestamp} - Cache: ${cacheKey}`, 20, 285);
    
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
    'First 24 Hours', 
    'Pain & Sensitivity',
    'Oral Hygiene',
    'Diet',
    'Special Precautions',
    'Follow-Up',
    'Follow Up'
  ];
  
  // Create an array of content segments with formatting info
  const segments = [];
  let currentContent = content;
  let currentIndex = 0;
  
  while (currentIndex < currentContent.length) {
    let nextBoldStart = currentContent.length;
    let nextBoldKeyword = null;
    
    // Find the next bold keyword
    for (const keyword of boldKeywords) {
      const index = currentContent.toLowerCase().indexOf(keyword.toLowerCase(), currentIndex);
      if (index !== -1 && index < nextBoldStart) {
        nextBoldStart = index;
        nextBoldKeyword = keyword;
      }
    }
    
    if (nextBoldKeyword && nextBoldStart > currentIndex) {
      // Add normal text before bold keyword
      if (nextBoldStart > currentIndex) {
        segments.push({
          text: currentContent.substring(currentIndex, nextBoldStart),
          bold: false
        });
      }
      
      // Add bold keyword
      segments.push({
        text: currentContent.substring(nextBoldStart, nextBoldStart + nextBoldKeyword.length),
        bold: true
      });
      
      currentIndex = nextBoldStart + nextBoldKeyword.length;
    } else {
      // Add remaining text as normal
      segments.push({
        text: currentContent.substring(currentIndex),
        bold: false
      });
      break;
    }
  }
  
  return segments;
}

// Function to add formatted content to PDF with proper line wrapping and bold formatting
function addFormattedContentToPDF(pdf, segments, startY) {
  let yPos = startY;
  const lineHeight = 6;
  const maxWidth = 170;
  const leftMargin = 20;
  
  pdf.setFontSize(11);
  
  for (const segment of segments) {
    if (!segment.text) continue;
    
    console.log(`📝 Rendering segment: "${segment.text.substring(0, 50)}" - Bold: ${segment.bold}`);
    
    // Set font style for this segment - use explicit font names
    if (segment.bold) {
      pdf.setFont('times', 'bold');  // Use Times font which definitely supports bold
      console.log('📝 Applied BOLD formatting');
    } else {
      pdf.setFont('times', 'normal');
      console.log('📝 Applied NORMAL formatting');
    }
    
    // Handle line wrapping manually to preserve formatting
    const words = segment.text.split(' ');
    let currentLine = '';
    
    for (let i = 0; i < words.length; i++) {
      const testLine = currentLine + (currentLine ? ' ' : '') + words[i];
      const textWidth = pdf.getTextWidth(testLine);
      
      if (textWidth > maxWidth && currentLine !== '') {
        // Current line is full, print it and start new line
        if (yPos > 270) {
          pdf.addPage();
          yPos = 20;
        }
        
        console.log(`📝 Printing line: "${currentLine}" - Font: times, Style: ${segment.bold ? 'bold' : 'normal'}`);
        pdf.text(currentLine, leftMargin, yPos);
        yPos += lineHeight;
        currentLine = words[i];
      } else {
        currentLine = testLine;
      }
    }
    
    // Print the last line if there's content
    if (currentLine) {
      if (yPos > 270) {
        pdf.addPage();
        yPos = 20;
      }
      
      console.log(`📝 Printing final line: "${currentLine}" - Font: times, Style: ${segment.bold ? 'bold' : 'normal'}`);
      pdf.text(currentLine, leftMargin, yPos);
      yPos += lineHeight;
    }
  }
}
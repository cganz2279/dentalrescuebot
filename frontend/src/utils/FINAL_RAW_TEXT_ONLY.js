import jsPDF from 'jspdf';

// Base64 encoded logo image
const LOGO_BASE64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABAAAAAQACAYAAAB/HSuDAAAACXBIWXMAAAsTAAALEwEAmpwYAAezH0lEQVR4nOzdd7ilyVXf+++qqvd9dzihc/fkpEmKI2mEhES6YEQQiGiwgWsMGDAyYGO4Bq5BmGCwMeliZJtsTPK1wGAMCAwKoISykNAEzWhiz3TuE/feb6iqdf+o3SP5wfbFQKtn+qyPnlF3n7jP2f08fdavVq0lqooxxhhjjDHGGGMub+5SPwBjjDHGGGOMMcZcfBYAGGOMMcYYY4wxe4AFAMYYY4wxxhhj';

// ENHANCED PDF GENERATOR WITH LOGO AND BOLD FORMATTING - v4
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
    
    // Add embedded logo at the top centered
    try {
      // Calculate centered position for logo
      const imgWidth = 40; // Desired width
      const imgHeight = 30; // Desired height
      const xPos = (pdf.internal.pageSize.width - imgWidth) / 2; // Center horizontally
      
      // Add logo to PDF using base64 data
      pdf.addImage(LOGO_BASE64, 'PNG', xPos, yPos, imgWidth, imgHeight);
      yPos += imgHeight + 10; // Move down after logo
      
      console.log('✅ Logo added successfully from base64');
      
    } catch (logoError) {
      console.log('Logo loading failed, using text header:', logoError);
      // Fallback to text header
      pdf.setFontSize(18);
      pdf.setFont(undefined, 'bold');
      pdf.setTextColor(41, 98, 184);
      pdf.text('DENTAL RESCUE NOTES', 105, yPos, { align: 'center' });
      yPos += 8;
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
      const contentWithBoldFormatting = processContentForBoldFormatting(overviewContent);
      
      // Add formatted content to PDF
      yPos = addFormattedContentToPDF(pdf, contentWithBoldFormatting, yPos);
      
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
  let remainingContent = content;
  
  while (remainingContent.length > 0) {
    let nextBoldIndex = -1;
    let nextBoldKeyword = null;
    
    // Find the next bold keyword (case-insensitive)
    for (const keyword of boldKeywords) {
      const index = remainingContent.toLowerCase().indexOf(keyword.toLowerCase());
      if (index !== -1 && (nextBoldIndex === -1 || index < nextBoldIndex)) {
        nextBoldIndex = index;
        nextBoldKeyword = keyword;
      }
    }
    
    if (nextBoldIndex !== -1) {
      // Add text before the bold keyword (if any)
      if (nextBoldIndex > 0) {
        segments.push({
          text: remainingContent.substring(0, nextBoldIndex),
          bold: false
        });
      }
      
      // Add the bold keyword
      segments.push({
        text: remainingContent.substring(nextBoldIndex, nextBoldIndex + nextBoldKeyword.length),
        bold: true
      });
      
      // Continue with remaining content
      remainingContent = remainingContent.substring(nextBoldIndex + nextBoldKeyword.length);
    } else {
      // No more bold keywords, add remaining text as normal
      segments.push({
        text: remainingContent,
        bold: false
      });
      break;
    }
  }
  
  return segments;
}

// Function to add formatted content to PDF with proper line wrapping
function addFormattedContentToPDF(pdf, segments, startY) {
  let yPos = startY;
  const lineHeight = 6;
  const maxWidth = 170;
  const leftMargin = 20;
  
  pdf.setFontSize(11);
  
  for (const segment of segments) {
    if (!segment.text.trim()) continue;
    
    // Set font style
    pdf.setFont(undefined, segment.bold ? 'bold' : 'normal');
    
    // Split text to fit page width
    const lines = pdf.splitTextToSize(segment.text, maxWidth);
    
    for (const line of lines) {
      // Check if we need a new page
      if (yPos > 270) {
        pdf.addPage();
        yPos = 20;
      }
      
      pdf.text(line, leftMargin, yPos);
      yPos += lineHeight;
    }
  }
  
  return yPos;
}
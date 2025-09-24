import jsPDF from 'jspdf';

// ULTRA SIMPLE - ONLY RAW OVERVIEW TEXT - CACHE BUSTED VERSION
export const generateProcedurePDF = async (procedure) => {
  // Force timestamp to bust cache
  const timestamp = new Date().toISOString();
  const cacheKey = Date.now();
  
  // Silent generation - alerts removed for better user experience
  
  console.log('🚨🚨🚨 FINAL_RAW_TEXT_ONLY GENERATOR LOADED - v2');
  console.log('🚨 TIMESTAMP:', timestamp);
  console.log('🚨 CACHE KEY:', cacheKey);
  console.log('🚨 BUILD TIMESTAMP: 2025-09-20-17:30');
  console.log('🚨 PROCEDURE NAME:', procedure.name);
  console.log('🚨 OVERVIEW TEXT FULL:', procedure.overview);
  
  try {
    const pdf = new jsPDF();
    let yPos = 20;
    
    // Add Dental Rescue Notes logo - Enhanced styling
    try {
      // Large, centered title with professional styling
      pdf.setFontSize(18);
      pdf.setFont(undefined, 'bold');
      pdf.setTextColor(41, 98, 184); // Professional blue color
      pdf.text('DENTAL RESCUE NOTES', 105, yPos, { align: 'center' });
      yPos += 8;
      
      // Subtitle
      pdf.setFontSize(10);
      pdf.setFont(undefined, 'normal');
      pdf.setTextColor(100, 100, 100); // Gray color
      pdf.text('Post-Operative Care Instructions', 105, yPos, { align: 'center' });
      yPos += 15;
      
      // Decorative line under the header
      pdf.setDrawColor(41, 98, 184);
      pdf.setLineWidth(1);
      pdf.line(50, yPos, 160, yPos);
      yPos += 20;
    } catch (logoError) {
      console.log('Logo header added as enhanced text');
    }
    
    // Title
    pdf.setTextColor(0, 0, 0); // Reset to black
    pdf.setFontSize(16);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedure.name || 'Procedure', 20, yPos);
    yPos += 20;
    
    // ONLY THE RAW OVERVIEW TEXT - NOTHING ELSE
    if (procedure.overview) {
      pdf.setFontSize(11);
      pdf.setFont(undefined, 'normal');
      
      // Split text to fit page
      const lines = pdf.splitTextToSize(procedure.overview, 170);
      
      lines.forEach(line => {
        if (yPos > 270) {
          pdf.addPage();
          yPos = 20;
        }
        pdf.text(line, 20, yPos);
        yPos += 6;
      });
    } else {
      pdf.setFontSize(11);
      pdf.text('No overview content available', 20, yPos);
    }
    
    // Footer with timestamp to confirm this generator ran
    const pageCount = pdf.internal.getNumberOfPages();
    pdf.setPage(pageCount);
    pdf.setFontSize(8);
    pdf.text(`Generated: ${timestamp} - Cache: ${cacheKey}`, 20, 285);
    
    // Save with timestamp filename
    const procedureName = procedure?.name || procedure?.procedureName || 'Procedure';
    const filename = `${procedureName.replace(/[^a-zA-Z0-9]/g, '_')}_RAW_${cacheKey}.pdf`;
    pdf.save(filename);
    
    console.log('🚨 PDF SAVED:', filename);
    
    return true;
    
  } catch (error) {
    console.error('🚨 PDF ERROR:', error);
    return false;
  }
};
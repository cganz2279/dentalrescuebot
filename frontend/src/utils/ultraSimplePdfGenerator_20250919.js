import jsPDF from 'jspdf';

// ULTRA SIMPLE PDF GENERATOR - TIMESTAMP: 2025-09-19 - RAW TEXT ONLY
export const generateProcedurePDF = async (procedure) => {
  // CRITICAL ALERT - FORCE BROWSER TO KNOW NEW CODE IS LOADING
  alert('🚨 ULTRA SIMPLE PDF GENERATOR LOADED - 2025-09-19 - RAW TEXT ONLY');
  console.log('🚨🚨🚨 ULTRA SIMPLE PDF GENERATOR - RAW TEXT ONLY - TIMESTAMP: 2025-09-19');
  console.log('📄 PROCEDURE:', procedure.name);
  console.log('📝 OVERVIEW EXISTS:', !!procedure.overview);
  console.log('📝 OVERVIEW CONTENT:', procedure.overview ? procedure.overview.substring(0, 200) + '...' : 'NO CONTENT');
  
  try {
    const pdf = new jsPDF();
    
    let yPos = 20;
    
    // Just the procedure name
    pdf.setFontSize(16);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedure.name || 'Procedure', 20, yPos);
    yPos += 30;
    
    // ONLY THE RAW OVERVIEW TEXT - ABSOLUTELY NO PROCESSING
    if (procedure.overview) {
      console.log('✅ Adding raw overview text to PDF...');
      
      pdf.setFontSize(11);
      pdf.setFont(undefined, 'normal');
      
      // Just display the text exactly as it is - no processing, no parsing, no formatting
      const textLines = pdf.splitTextToSize(procedure.overview, 170);
      
      textLines.forEach(line => {
        if (yPos > 270) {
          pdf.addPage();
          yPos = 20;
        }
        
        pdf.text(line, 20, yPos);
        yPos += 6;
      });
      
      console.log(`✅ Added ${textLines.length} lines of raw text`);
    } else {
      console.log('❌ No overview content to add');
      pdf.text('No overview content available.', 20, yPos);
    }
    
    // Save with timestamp
    const timestamp = Date.now();
    const filename = `${procedure.name.replace(/\s+/g, '_')}_ULTRA_SIMPLE_${timestamp}.pdf`;
    pdf.save(filename);
    
    console.log('✅ PDF saved:', filename);
    
    return true;
    
  } catch (error) {
    console.error('❌ PDF generation error:', error);
    alert('PDF generation failed: ' + error.message);
    return false;
  }
};
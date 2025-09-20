import jsPDF from 'jspdf';

// RAW OVERVIEW TEXT ONLY - NO PROCESSING WHATSOEVER - FORCED UPDATE
export const generateProcedurePDF = async (procedure) => {
  // FORCE ALERT - CRITICAL TEST
  alert('🚨🚨🚨 EMERGENCY PDF GENERATOR - FORCED UPDATE - ' + new Date().toISOString());
  console.log('🚨🚨🚨 EMERGENCY PDF GENERATOR LOADED');
  console.log('🚨🚨🚨 TIMESTAMP:', new Date().toISOString());
  console.log('🚨🚨🚨 PROCEDURE:', procedure.name);
  console.log('🚨🚨🚨 OVERVIEW:', procedure.overview);
  
  // Force another alert to make sure this code runs
  alert('SECOND ALERT - PDF GENERATOR IS DEFINITELY RUNNING');
  
  try {
    const pdf = new jsPDF();
    
    let yPos = 20;
    
    // Procedure name
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedure.name || 'Procedure', 20, yPos);
    yPos += 20;
    
    // JUST THE RAW OVERVIEW TEXT - NOTHING ELSE
    if (procedure.overview) {
      pdf.setFontSize(11);
      pdf.setFont(undefined, 'normal');
      
      // Display the overview text exactly as it is stored
      const lines = pdf.splitTextToSize(procedure.overview, 170);
      
      lines.forEach(line => {
        if (yPos > 270) {
          pdf.addPage();
          yPos = 20;
        }
        pdf.text(line, 20, yPos);
        yPos += 6;
      });
    }
    
    // Save PDF with emergency filename
    const filename = `EMERGENCY_${procedure.name.replace(/\s+/g, '_')}_${Date.now()}.pdf`;
    pdf.save(filename);
    
    alert('PDF SAVED: ' + filename);
    console.log('🚨 EMERGENCY PDF saved:', filename);
    return true;
    
  } catch (error) {
    alert('PDF ERROR: ' + error.message);
    console.error('🚨 PDF error:', error);
    return false;
  }
};
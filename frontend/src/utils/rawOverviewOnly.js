import jsPDF from 'jspdf';

// RAW OVERVIEW TEXT ONLY - NO PROCESSING WHATSOEVER
export const generateProcedurePDF = async (procedure) => {
  // FORCE ALERT
  alert('📝 RAW OVERVIEW ONLY PDF GENERATOR - NO FORMATTING AT ALL');
  console.log('📝📝📝 RAW OVERVIEW ONLY - NO FORMATTING - TIMESTAMP:', new Date().toISOString());
  console.log('PROCEDURE NAME:', procedure.name);
  console.log('OVERVIEW TEXT:', procedure.overview);
  
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
    
    // Save PDF
    const filename = `${procedure.name.replace(/\s+/g, '_')}_RAW_OVERVIEW_ONLY.pdf`;
    pdf.save(filename);
    
    console.log('PDF saved with raw overview only:', filename);
    return true;
    
  } catch (error) {
    console.error('PDF error:', error);
    return false;
  }
};
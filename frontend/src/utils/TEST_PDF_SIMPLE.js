import jsPDF from 'jspdf';

// Simple test PDF generator to diagnose the issue
export const testSimplePDF = () => {
  console.log('🧪 Testing simple PDF generation...');
  
  try {
    const pdf = new jsPDF();
    
    // Add some simple text
    pdf.setFontSize(20);
    pdf.text('Test PDF', 20, 20);
    pdf.setFontSize(12);
    pdf.text('This is a test PDF to diagnose the download issue.', 20, 40);
    pdf.text('If you can see this PDF, the basic jsPDF functionality works.', 20, 60);
    
    const filename = `test_pdf_${Date.now()}.pdf`;
    console.log('🚨 Attempting to save PDF:', filename);
    
    // Try the same save method as the main PDF generator
    pdf.save(filename);
    
    console.log('✅ PDF save command executed');
    return true;
    
  } catch (error) {
    console.error('❌ Simple PDF test failed:', error);
    return false;
  }
};
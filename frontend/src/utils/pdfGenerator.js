import jsPDF from 'jspdf';

export const generateProcedurePDF = (procedure, practice = null, dentist = null, patientName = null) => {
  try {
    // Create new PDF document
    const pdf = new jsPDF();
    let yPosition = 20;
    const pageWidth = pdf.internal.pageSize.width;
    const margin = 20;
    const contentWidth = pageWidth - (margin * 2);

    // Helper function to add text with word wrapping
    const addText = (text, fontSize = 11, isBold = false, color = [0, 0, 0]) => {
      pdf.setFontSize(fontSize);
      pdf.setTextColor(color[0], color[1], color[2]);
      
      if (isBold) {
        pdf.setFont(undefined, 'bold');
      } else {
        pdf.setFont(undefined, 'normal');
      }

      const lines = pdf.splitTextToSize(text, contentWidth);
      
      // Check if we need a new page
      if (yPosition + (lines.length * fontSize * 0.5) > pdf.internal.pageSize.height - 20) {
        pdf.addPage();
        yPosition = 20;
      }
      
      pdf.text(lines, margin, yPosition);
      yPosition += lines.length * fontSize * 0.5 + 3;
    };

    // Helper function to add a professional section
    const addSection = (title, items, isWarning = false) => {
      // Add spacing before section
      yPosition += 8;
      
      // Section title
      const titleColor = isWarning ? [180, 0, 0] : [0, 0, 0];
      addText(title, 13, true, titleColor);
      
      // Add a subtle line under the title
      pdf.setDrawColor(200, 200, 200);
      pdf.setLineWidth(0.5);
      pdf.line(margin, yPosition - 3, margin + contentWidth, yPosition - 3);
      yPosition += 3;
      
      // Ensure items is an array before processing
      if (Array.isArray(items) && items.length > 0) {
        items.forEach((item, index) => {
          const bullet = isWarning ? '•' : '•';
          addText(`   ${bullet} ${item}`, 10);
        });
      } else {
        addText('   • Follow standard care instructions as discussed', 10);
      }
      
      yPosition += 5;
    };

    // Professional Header
    pdf.setFontSize(18);
    pdf.setFont(undefined, 'bold');
    pdf.setTextColor(0, 0, 0);
    pdf.text('POST-OPERATIVE CARE INSTRUCTIONS', margin, yPosition);
    yPosition += 15;

    // Practice information
    if (practice && practice.name) {
      pdf.setFontSize(12);
      pdf.setFont(undefined, 'bold');
      pdf.text(practice.name, margin, yPosition);
      yPosition += 8;
      
      if (practice.phone) {
        pdf.setFont(undefined, 'normal');
        pdf.setFontSize(10);
        pdf.text(`Phone: ${practice.phone}`, margin, yPosition);
        yPosition += 6;
      }
    }

    // Horizontal line separator
    pdf.setDrawColor(0, 0, 0);
    pdf.setLineWidth(1);
    pdf.line(margin, yPosition, margin + contentWidth, yPosition);
    yPosition += 15;

    // Procedure information
    addText(`Procedure: ${procedure.name}`, 12, true);
    addText(`Date: ${new Date().toLocaleDateString()}`, 10);
    yPosition += 10;

    // Main instructions sections
    addSection('IMMEDIATE AFTERCARE INSTRUCTIONS', procedure.immediateAftercare);
    addSection('DIET RESTRICTIONS', procedure.dietRestrictions);
    addSection('MEDICATIONS', procedure.medications);
    
    // Recovery Timeline
    yPosition += 8;
    addText('RECOVERY TIMELINE', 13, true);
    pdf.setDrawColor(200, 200, 200);
    pdf.setLineWidth(0.5);
    pdf.line(margin, yPosition - 3, margin + contentWidth, yPosition - 3);
    yPosition += 3;
    
    if (Array.isArray(procedure.recoveryTimeline) && procedure.recoveryTimeline.length > 0) {
      procedure.recoveryTimeline.forEach((timeline) => {
        addText(`   Day ${timeline.day}: ${timeline.activity}`, 10);
      });
    } else {
      addText('   Follow standard recovery guidelines as discussed', 10);
    }
    yPosition += 10;

    // Warning signs - highlighted but professional
    addSection('⚠️ WHEN TO CONTACT YOUR DENTIST IMMEDIATELY', procedure.warningSignsToCallDoctor, true);

    // Custom instructions if available
    if (Array.isArray(procedure.instructions) && procedure.instructions.length > 0) {
      addSection('ADDITIONAL INSTRUCTIONS', procedure.instructions);
    }

    // Contact section
    yPosition += 15;
    addText('CONTACT INFORMATION', 13, true);
    pdf.setDrawColor(200, 200, 200);
    pdf.setLineWidth(0.5);
    pdf.line(margin, yPosition - 3, margin + contentWidth, yPosition - 3);
    yPosition += 3;
    
    addText('For questions or concerns, please contact our office during regular business hours.', 10);
    addText('For after-hours emergencies, follow the emergency contact instructions provided.', 10);
    yPosition += 15;

    // Patient acknowledgment section
    if (yPosition > pdf.internal.pageSize.height - 80) {
      pdf.addPage();
      yPosition = 20;
    }
    
    addText('PATIENT ACKNOWLEDGMENT', 13, true);
    pdf.setDrawColor(200, 200, 200);
    pdf.setLineWidth(0.5);
    pdf.line(margin, yPosition - 3, margin + contentWidth, yPosition - 3);
    yPosition += 8;
    
    addText('I acknowledge that I have received and understand these post-operative care instructions. I will follow these instructions carefully and contact my dental office if I have any questions or concerns.', 10);
    yPosition += 15;
    
    // Signature lines
    pdf.setDrawColor(0, 0, 0);
    pdf.setLineWidth(0.5);
    
    // Patient signature line
    const signatureY = yPosition + 5;
    pdf.line(margin, signatureY, margin + 120, signatureY);
    pdf.setFontSize(9);
    pdf.text('Patient Signature', margin, signatureY + 12);
    
    // Date line
    const dateLineX = margin + 140;
    pdf.line(dateLineX, signatureY, dateLineX + 60, signatureY);
    pdf.text('Date', dateLineX, signatureY + 12);
    
    yPosition += 35;

    // Professional footer
    if (yPosition > pdf.internal.pageSize.height - 40) {
      pdf.addPage();
      yPosition = 20;
    }
    
    yPosition = pdf.internal.pageSize.height - 35;
    pdf.setFontSize(8);
    pdf.setTextColor(100, 100, 100);
    pdf.text('DISCLAIMER: This information is for educational purposes only and does not replace professional medical advice.', margin, yPosition);
    pdf.text('Always consult your dentist or physician for specific medical concerns.', margin, yPosition + 8);
    pdf.text(`Generated on: ${new Date().toLocaleDateString()} | DentalRescueBot - www.theoncallbot.com`, margin, yPosition + 18);

    // Save the PDF with a clean filename
    const fileName = `${procedure.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_post_op_instructions.pdf`;
    pdf.save(fileName);
    
    return true;
  } catch (error) {
    console.error('Error generating PDF:', error);
    return false;
  }
};
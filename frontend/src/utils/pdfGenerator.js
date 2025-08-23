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

    // Helper function to add a colored section box (like the View page)
    const addColoredSection = (title, items, bgColor = [245, 245, 245], textColor = [0, 0, 0], titleColor = [0, 0, 0]) => {
      // Add spacing before section
      yPosition += 8;
      
      // Calculate box height needed
      let itemsHeight = 0;
      if (Array.isArray(items) && items.length > 0) {
        itemsHeight = items.length * 12; // Approximate height per item
      } else {
        itemsHeight = 12; // Height for default text
      }
      
      const boxHeight = 25 + itemsHeight; // Title + items + padding
      
      // Check if we need a new page
      if (yPosition + boxHeight > pdf.internal.pageSize.height - 20) {
        pdf.addPage();
        yPosition = 20;
      }
      
      // Draw colored background box
      pdf.setFillColor(bgColor[0], bgColor[1], bgColor[2]);
      pdf.setDrawColor(200, 200, 200);
      pdf.setLineWidth(0.5);
      pdf.roundedRect(margin, yPosition - 5, contentWidth, boxHeight, 3, 3, 'FD');
      
      // Section title
      addText(title, 12, true, titleColor);
      yPosition += 3;
      
      // Items
      if (Array.isArray(items) && items.length > 0) {
        items.forEach((item, index) => {
          addText(`• ${item}`, 10, false, textColor);
        });
      } else {
        addText('• Follow standard care instructions as discussed', 10, false, textColor);
      }
      
      yPosition += 5;
    };

    // Professional Header (matching View page)
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

    // Procedure Information Box (matching View page)
    pdf.setFillColor(249, 250, 251);
    pdf.setDrawColor(200, 200, 200);
    pdf.roundedRect(margin, yPosition - 5, contentWidth, 45, 3, 3, 'FD');
    
    addText('PROCEDURE INFORMATION', 13, true, [0, 0, 0]);
    addText(`Procedure: ${procedure.name}`, 11, true);
    if (procedure.dentistName) {
      addText(`Performing Dentist: Dr. ${procedure.dentistName}`, 10);
    }
    addText(`Date: ${new Date().toLocaleDateString()}`, 10);
    yPosition += 15;

    // Detailed Post-Operative Care Instructions (matching View page sections)
    addText('DETAILED POST-OPERATIVE CARE INSTRUCTIONS', 14, true, [34, 197, 94]);
    yPosition += 5;

    // Immediate Aftercare (Red section like View page)
    addColoredSection(
      '🕐 IMMEDIATE AFTERCARE (First 24 Hours)',
      [
        'Apply ice to the treated area for 15 minutes every hour for the first 24 hours to reduce swelling',
        'Keep gauze in place for 30-60 minutes after treatment, then remove gently',
        'Do not rinse or spit forcefully for the first 24 hours',
        'Take prescribed medications as directed by your dentist'
      ],
      [254, 242, 242], // Light red background
      [153, 27, 27],   // Dark red text
      [185, 28, 28]    // Red title
    );

    // Diet Instructions (Orange section like View page)
    addColoredSection(
      '🍽️ DIET AND EATING INSTRUCTIONS',
      [
        'Stick to soft foods for the first 24-48 hours (yogurt, soup, mashed potatoes)',
        'Avoid hot liquids and foods until numbness wears off',
        'No alcohol while taking prescribed medications',
        'Avoid using straws for the first few days to prevent dry socket'
      ],
      [255, 247, 237], // Light orange background
      [154, 52, 18],   // Dark orange text
      [194, 65, 12]    // Orange title
    );

    // Medication Guidelines (Blue section like View page)
    addColoredSection(
      '💊 MEDICATION GUIDELINES',
      [
        'Take all prescribed medications exactly as directed',
        'Complete the full course of antibiotics if prescribed',
        'Use over-the-counter pain relief as recommended (ibuprofen, acetaminophen)',
        'Do not exceed recommended dosages of any medication'
      ],
      [239, 246, 255], // Light blue background
      [30, 58, 138],   // Dark blue text
      [37, 99, 235]    // Blue title
    );

    // Warning Signs (Red alert box like View page)
    addColoredSection(
      '⚠️ WHEN TO CONTACT YOUR DENTIST IMMEDIATELY',
      [
        'Severe or worsening pain after 48 hours',
        'Excessive bleeding that does not stop with gentle pressure',
        'Signs of infection: fever, excessive swelling, pus, or foul taste',
        'Numbness that persists beyond the expected timeframe',
        'Difficulty swallowing or breathing'
      ],
      [254, 226, 226], // Light red background
      [127, 29, 29],   // Very dark red text
      [185, 28, 28]    // Red title
    );

    // Custom instructions if available (matching View page)
    if (Array.isArray(procedure.instructions) && procedure.instructions.length > 0) {
      addColoredSection(
        '📋 ADDITIONAL CUSTOM INSTRUCTIONS',
        procedure.instructions,
        [240, 253, 244], // Light green background
        [22, 101, 52],   // Dark green text
        [34, 197, 94]    // Green title
      );
    }

    // Contact Information (matching View page)
    addColoredSection(
      '📞 CONTACT INFORMATION',
      [
        'For questions or concerns, please contact our office during regular business hours',
        'For after-hours emergencies, follow the emergency contact instructions provided'
      ],
      [249, 250, 251], // Light gray background
      [55, 65, 81],    // Dark gray text
      [0, 0, 0]        // Black title
    );

    // Patient acknowledgment section (matching View page)
    if (yPosition > pdf.internal.pageSize.height - 100) {
      pdf.addPage();
      yPosition = 20;
    }
    
    yPosition += 15;
    addText('PATIENT ACKNOWLEDGMENT', 13, true);
    pdf.setDrawColor(200, 200, 200);
    pdf.setLineWidth(0.5);
    pdf.line(margin, yPosition - 3, margin + contentWidth, yPosition - 3);
    yPosition += 8;
    
    addText('I acknowledge that I have received and understand these post-operative care instructions. I will follow these instructions carefully and contact my dental office if I have any questions or concerns.', 10);
    yPosition += 15;
    
    // Signature lines (matching View page)
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
import jsPDF from 'jspdf';

export const generateProcedurePDF = (procedure) => {
  try {
    // Create new PDF document
    const pdf = new jsPDF();
    let yPosition = 25;
    const pageWidth = pdf.internal.pageSize.width;
    const margin = 20;
    const contentWidth = pageWidth - (margin * 2);

    // Helper function to add text with word wrapping and larger fonts
    const addText = (text, fontSize = 14, isBold = false, indent = 0) => {
      pdf.setFontSize(fontSize);
      pdf.setTextColor(0, 0, 0); // Always black text
      
      if (isBold) {
        pdf.setFont(undefined, 'bold');
      } else {
        pdf.setFont(undefined, 'normal');
      }

      const availableWidth = contentWidth - indent;
      const lines = pdf.splitTextToSize(text, availableWidth);
      
      // Check if we need a new page
      if (yPosition + (lines.length * fontSize * 0.6) > pdf.internal.pageSize.height - 30) {
        pdf.addPage();
        yPosition = 25;
      }
      
      pdf.text(lines, margin + indent, yPosition);
      yPosition += lines.length * fontSize * 0.6 + 4;
    };

    // Helper function to add bulleted list with proper formatting
    const addBulletList = (items, fontSize = 13) => {
      if (!items || items.length === 0) return;
      
      items.forEach((item) => {
        // Clean up the item text (remove existing bullets)
        const cleanItem = item.replace(/^[•·-]\s*/, '').trim();
        addText(`• ${cleanItem}`, fontSize, false, 10);
      });
    };

    // Helper function to add spacing
    const addSpace = (space = 12) => {
      yPosition += space;
    };

    // Practice Header with Logo/Branding
    if (procedure.practiceName) {
      addText(procedure.practiceName, 20, true);
      if (procedure.practiceAddress) {
        addText(procedure.practiceAddress, 12);
      }
      if (procedure.practicePhone) {
        addText(`Phone: ${procedure.practicePhone}`, 12);
      }
      if (procedure.practiceWebsite) {
        addText(procedure.practiceWebsite, 12);
      }
      addSpace(20);
    }

    // Header - Clean and simple with larger fonts
    addText('Procedure Details', 22, true);
    addText(`${procedure.name} for ${procedure.patientName}`, 18, true);
    addSpace(20);

    // Assignment Information Section
    addText('Assignment Information', 18, true);
    addSpace(8);
    
    addText('Patient Details', 16, true);
    addText(`Patient: ${procedure.patientName}`, 13);
    if (procedure.patientEmail) {
      addText(`Email: ${procedure.patientEmail}`, 13);
    }
    addSpace(12);
    
    addText('Treatment Details', 16, true);
    addText(`Performed: ${procedure.performedDate}`, 13);
    if (procedure.followUpDate) {
      addText(`Follow-up: ${procedure.followUpDate}`, 13);
    }
    addText(`Dentist: ${procedure.dentistName}`, 13);
    addText(`Status: ${procedure.status || 'active'}`, 13);
    addSpace(18);

    // Practice Notes Section
    if (procedure.practiceNotes) {
      addText('Practice Notes', 18, true);
      addSpace(5);
      addText(procedure.practiceNotes, 13);
      addSpace(18);
    }

    // Custom Instructions Section
    if (procedure.customInstructions && procedure.customInstructions.length > 0) {
      addText('Custom Instructions', 18, true);
      addSpace(5);
      addBulletList(procedure.customInstructions, 13);
      addSpace(18);
    }

    // Post-Operative Care Instructions Section
    addText('Post-Operative Care Instructions', 18, true);
    addSpace(12);
    
    // Overview - break into bullets if it's a long paragraph
    if (procedure.overview) {
      addText('Overview', 16, true);
      addSpace(5);
      // Split overview into sentences for better readability
      const overviewSentences = procedure.overview.split(/[.!?]+/).filter(s => s.trim().length > 0);
      if (overviewSentences.length > 1) {
        overviewSentences.forEach(sentence => {
          if (sentence.trim()) {
            addText(`• ${sentence.trim()}.`, 13, false, 10);
          }
        });
      } else {
        addText(procedure.overview, 13);
      }
      addSpace(15);
    }
    
    // Immediate Aftercare with proper bullets
    if (procedure.immediateAftercare && procedure.immediateAftercare.length > 0) {
      addText('Immediate Aftercare', 16, true);
      addSpace(5);
      addBulletList(procedure.immediateAftercare, 13);
      addSpace(15);
    }

    // Diet Restrictions with proper bullets
    if (procedure.dietRestrictions && procedure.dietRestrictions.length > 0) {
      addText('Diet Restrictions', 16, true);
      addSpace(5);
      addBulletList(procedure.dietRestrictions, 13);
      addSpace(15);
    }

    // Warning Signs with proper bullets
    if (procedure.warningSignsToCallDoctor && procedure.warningSignsToCallDoctor.length > 0) {
      addText('⚠️ Warning Signs - Call Your Dentist Immediately', 16, true);
      addSpace(5);
      addBulletList(procedure.warningSignsToCallDoctor, 13);
      addSpace(15);
    }

    // Recovery Timeline with proper formatting
    if (procedure.recoveryTimeline && procedure.recoveryTimeline.length > 0) {
      addText('Recovery Timeline', 16, true);
      addSpace(5);
      procedure.recoveryTimeline.forEach((timeline) => {
        addText(`• Day ${timeline.day}: ${timeline.activity}`, 13, false, 10);
      });
      addSpace(15);
    }

    // Medications with proper bullets
    if (procedure.medications && procedure.medications.length > 0) {
      addText('Medications', 16, true);
      addSpace(5);
      addBulletList(procedure.medications, 13);
      addSpace(20);
    }

    // Contact Information - Clean footer with practice info
    addText('Contact Information', 16, true);
    addSpace(5);
    if (procedure.practiceName) {
      addText(`Practice: ${procedure.practiceName}`, 13);
    }
    if (procedure.practicePhone) {
      addText(`Phone: ${procedure.practicePhone}`, 13);
    }
    addText('For emergencies, contact your dentist immediately or call 911.', 13, true);

    // Save the PDF with clean filename
    const fileName = `${procedure.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${procedure.patientName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_postop_care.pdf`;
    pdf.save(fileName);
    
    return true;
  } catch (error) {
    console.error('Error generating PDF:', error);
    return false;
  }
};
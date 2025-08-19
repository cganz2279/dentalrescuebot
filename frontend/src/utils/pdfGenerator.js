import jsPDF from 'jspdf';

export const generateProcedurePDF = (procedure) => {
  try {
    // Create new PDF document
    const pdf = new jsPDF();
    let yPosition = 20;
    const pageWidth = pdf.internal.pageSize.width;
    const margin = 20;
    const contentWidth = pageWidth - (margin * 2);

    // Helper function to add text with word wrapping
    const addText = (text, fontSize = 12, isBold = false) => {
      pdf.setFontSize(fontSize);
      pdf.setTextColor(0, 0, 0); // Always black text
      
      if (isBold) {
        pdf.setFont(undefined, 'bold');
      } else {
        pdf.setFont(undefined, 'normal');
      }

      const lines = pdf.splitTextToSize(text, contentWidth);
      
      // Check if we need a new page
      if (yPosition + (lines.length * fontSize * 0.5) > pdf.internal.pageSize.height - 30) {
        pdf.addPage();
        yPosition = 20;
      }
      
      pdf.text(lines, margin, yPosition);
      yPosition += lines.length * fontSize * 0.5 + 3;
    };

    // Helper function to add spacing
    const addSpace = (space = 10) => {
      yPosition += space;
    };

    // Header - Clean and simple
    addText('Procedure Details', 18, true);
    addText(`${procedure.name} for ${procedure.patientName}`, 14, true);
    addSpace(15);

    // Assignment Information Section
    addText('Assignment Information', 14, true);
    addSpace(5);
    
    addText('Patient Details', 12, true);
    addText(`${procedure.patientName}`, 11);
    if (procedure.patientEmail) {
      addText(`${procedure.patientEmail}`, 11);
    }
    addSpace(8);
    
    addText('Treatment Details', 12, true);
    addText(`Performed: ${procedure.performedDate}`, 11);
    if (procedure.followUpDate) {
      addText(`Follow-up: ${new Date(procedure.followUpDate).toLocaleDateString()}`, 11);
    }
    addText(`Dentist: ${procedure.dentistName}`, 11);
    addText(`Status: ${procedure.status || 'active'}`, 11);
    addSpace(15);

    // Practice Notes Section
    if (procedure.practiceNotes) {
      addText('Practice Notes', 14, true);
      addSpace(5);
      addText(procedure.practiceNotes, 11);
      addSpace(15);
    }

    // Custom Instructions Section
    if (procedure.customInstructions && procedure.customInstructions.length > 0) {
      addText('Custom Instructions', 14, true);
      addSpace(5);
      procedure.customInstructions.forEach((instruction) => {
        addText(`• ${instruction}`, 11);
      });
      addSpace(15);
    }

    // Post-Operative Care Instructions Section
    addText('Post-Operative Care Instructions', 14, true);
    addSpace(8);
    
    // Overview
    if (procedure.overview) {
      addText('Overview', 12, true);
      addSpace(3);
      addText(procedure.overview, 11);
      addSpace(10);
    }
    
    // Immediate Aftercare
    if (procedure.immediateAftercare && procedure.immediateAftercare.length > 0) {
      addText('Immediate Aftercare', 12, true);
      addSpace(3);
      procedure.immediateAftercare.forEach((instruction) => {
        addText(`• ${instruction}`, 11);
      });
      addSpace(10);
    }

    // Diet Restrictions
    if (procedure.dietRestrictions && procedure.dietRestrictions.length > 0) {
      addText('Diet Restrictions', 12, true);
      addSpace(3);
      procedure.dietRestrictions.forEach((restriction) => {
        addText(`• ${restriction}`, 11);
      });
      addSpace(10);
    }

    // Warning Signs
    if (procedure.warningSignsToCallDoctor && procedure.warningSignsToCallDoctor.length > 0) {
      addText('⚠️ Warning Signs - Call Your Dentist Immediately', 12, true);
      addSpace(3);
      procedure.warningSignsToCallDoctor.forEach((warning) => {
        addText(`• ${warning}`, 11);
      });
      addSpace(10);
    }

    // Recovery Timeline
    if (procedure.recoveryTimeline && procedure.recoveryTimeline.length > 0) {
      addText('Recovery Timeline', 12, true);
      addSpace(3);
      procedure.recoveryTimeline.forEach((timeline) => {
        addText(`Day ${timeline.day}: ${timeline.activity}`, 11);
      });
      addSpace(10);
    }

    // Medications
    if (procedure.medications && procedure.medications.length > 0) {
      addText('Medications', 12, true);
      addSpace(3);
      procedure.medications.forEach((medication) => {
        addText(`• ${medication}`, 11);
      });
      addSpace(15);
    }

    // Contact Information - Simple footer
    addText('Contact Information', 12, true);
    addSpace(3);
    if (procedure.practiceName) {
      addText(`Practice: ${procedure.practiceName}`, 11);
    }
    if (procedure.practicePhone) {
      addText(`Phone: ${procedure.practicePhone}`, 11);
    }
    addText('For emergencies, contact your dentist immediately or call 911.', 11);

    // Save the PDF with clean filename
    const fileName = `${procedure.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${procedure.patientName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_postop_care.pdf`;
    pdf.save(fileName);
    
    return true;
  } catch (error) {
    console.error('Error generating PDF:', error);
    return false;
  }
};
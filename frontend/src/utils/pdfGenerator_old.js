import jsPDF from 'jspdf';

export const generateProcedurePDF = (procedure) => {
  try {
    console.log('🎨 Starting enhanced WYSIWYG PDF generation with better colors...');
    
    // Create PDF with better settings for color rendering
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
      putOnlyUsedFonts: true,
      compress: true
    });

    let yPosition = 20;
    const pageWidth = pdf.internal.pageSize.width;
    const pageHeight = pdf.internal.pageSize.height;
    const margin = 15;
    const contentWidth = pageWidth - (margin * 2);

    // Enhanced color palette (RGB values for better rendering)
    const colors = {
      blue: [37, 99, 235],
      green: [34, 197, 94], 
      orange: [249, 115, 22],
      red: [239, 68, 68],
      purple: [147, 51, 234],
      gray: [107, 114, 128],
      lightGray: [249, 250, 251],
      white: [255, 255, 255],
      darkText: [31, 41, 55],
      lightText: [75, 85, 99]
    };

    // Helper function to draw filled rectangle with color
    const drawColoredRect = (x, y, width, height, color, opacity = 1) => {
      pdf.setFillColor(color[0], color[1], color[2]);
      if (opacity < 1) {
        pdf.setGState(pdf.GState({opacity: opacity}));
      }
      pdf.rect(x, y, width, height, 'F');
      if (opacity < 1) {
        pdf.setGState(pdf.GState({opacity: 1}));
      }
    };

    // Helper function to add text with color
    const addColoredText = (text, x, y, options = {}) => {
      const {
        fontSize = 12,
        fontStyle = 'normal',
        color = colors.darkText,
        align = 'left',
        maxWidth = contentWidth
      } = options;

      pdf.setFontSize(fontSize);
      pdf.setFont('helvetica', fontStyle);
      pdf.setTextColor(color[0], color[1], color[2]);
      
      const lines = pdf.splitTextToSize(text, maxWidth);
      pdf.text(lines, x, y, { align });
      
      return lines.length * (fontSize * 0.35); // Return height used
    };

    // Helper function to check and add new page if needed
    const checkNewPage = (additionalHeight = 20) => {
      if (yPosition + additionalHeight > pageHeight - 20) {
        pdf.addPage();
        yPosition = 20;
        return true;
      }
      return false;
    };

    // HEADER SECTION with blue background
    drawColoredRect(margin, yPosition, contentWidth, 25, colors.blue);
    yPosition += 8;
    addColoredText('Post-Operative Care Guide', margin, yPosition, {
      fontSize: 18,
      fontStyle: 'bold',
      color: colors.white,
      align: 'center',
      maxWidth: contentWidth
    });
    yPosition += 15;

    // Procedure name with specialty badge
    yPosition += 10;
    drawColoredRect(margin, yPosition, contentWidth, 20, colors.lightGray);
    yPosition += 6;
    
    // Specialty badge
    const specialtyText = procedure.specialtyName || 'General';
    const badgeWidth = specialtyText.length * 4 + 10;
    drawColoredRect(margin + 10, yPosition, badgeWidth, 8, colors.gray);
    addColoredText(specialtyText, margin + 15, yPosition + 5, {
      fontSize: 8,
      fontStyle: 'bold',
      color: colors.white
    });
    
    yPosition += 12;
    addColoredText(procedure.name, margin, yPosition, {
      fontSize: 16,
      fontStyle: 'bold',
      color: colors.darkText,
      align: 'center'
    });
    yPosition += 20;

    // OVERVIEW SECTION (Blue theme)
    checkNewPage(30);
    drawColoredRect(margin, yPosition, 4, 15, colors.blue); // Left border
    drawColoredRect(margin, yPosition, contentWidth, 15, [219, 234, 254]); // Light blue background
    yPosition += 5;
    addColoredText('● OVERVIEW', margin + 10, yPosition, {
      fontSize: 14,
      fontStyle: 'bold',
      color: colors.blue
    });
    yPosition += 15;

    if (procedure.overview) {
      const overviewLines = procedure.overview.split('\n');
      overviewLines.forEach(line => {
        const trimmedLine = line.trim();
        if (trimmedLine) {
          checkNewPage();
          if (trimmedLine.startsWith('•') || trimmedLine.startsWith('-')) {
            addColoredText('•', margin + 8, yPosition, { color: colors.blue, fontSize: 12 });
            const bulletText = trimmedLine.replace(/^[•-]\s*/, '');
            yPosition += addColoredText(bulletText, margin + 15, yPosition, { fontSize: 11 });
          } else if (trimmedLine.includes('**')) {
            const cleanText = trimmedLine.replace(/\*\*/g, '');
            yPosition += addColoredText(cleanText, margin + 8, yPosition, { 
              fontSize: 12, 
              fontStyle: 'bold' 
            });
          } else {
            yPosition += addColoredText(trimmedLine, margin + 8, yPosition, { fontSize: 11 });
          }
          yPosition += 3;
        }
      });
    }
    yPosition += 10;

    // EMERGENCY ALERT (Red theme)
    checkNewPage(25);
    drawColoredRect(margin, yPosition, contentWidth, 20, [254, 242, 242]); // Light red background
    drawColoredRect(margin, yPosition, contentWidth, 20, colors.red, 0.1); // Red overlay
    yPosition += 6;
    addColoredText('🚨 EMERGENCY ALERT', margin, yPosition, {
      fontSize: 13,
      fontStyle: 'bold',
      color: colors.red,
      align: 'center'
    });
    yPosition += 8;
    addColoredText('If you experience severe bleeding, difficulty breathing, or allergic reaction, call 911 immediately.', 
      margin + 5, yPosition, {
      fontSize: 10,
      fontStyle: 'bold',
      color: [153, 27, 27], // Darker red
      maxWidth: contentWidth - 10
    });
    yPosition += 20;

    // IMMEDIATE AFTERCARE (Green theme)
    if (procedure.immediateAftercare && procedure.immediateAftercare.length > 0) {
      checkNewPage(40);
      drawColoredRect(margin, yPosition, 4, 15, colors.green);
      drawColoredRect(margin, yPosition, contentWidth, 15, [220, 252, 231]); // Light green
      yPosition += 5;
      addColoredText('♥ IMMEDIATE AFTERCARE', margin + 10, yPosition, {
        fontSize: 14,
        fontStyle: 'bold',
        color: colors.green
      });
      yPosition += 15;

      procedure.immediateAftercare.forEach((item, index) => {
        checkNewPage();
        // Draw green circular number badge
        pdf.setFillColor(34, 197, 94);
        pdf.circle(margin + 10, yPosition + 2, 4, 'F');
        addColoredText((index + 1).toString(), margin + 10, yPosition + 3, {
          fontSize: 9,
          fontStyle: 'bold',
          color: colors.white,
          align: 'center'
        });
        
        yPosition += addColoredText(item, margin + 20, yPosition, { fontSize: 11 });
        yPosition += 8;
      });
      yPosition += 5;
    }

    // DIET RESTRICTIONS (Orange theme)
    if (procedure.dietRestrictions && procedure.dietRestrictions.length > 0) {
      checkNewPage(40);
      drawColoredRect(margin, yPosition, 4, 15, colors.orange);
      drawColoredRect(margin, yPosition, contentWidth, 15, [254, 215, 170]); // Light orange
      yPosition += 5;
      addColoredText('🍽 DIET RESTRICTIONS', margin + 10, yPosition, {
        fontSize: 14,
        fontStyle: 'bold',
        color: colors.orange
      });
      yPosition += 15;

      procedure.dietRestrictions.forEach((item, index) => {
        checkNewPage();
        // Draw orange circular number badge
        pdf.setFillColor(249, 115, 22);
        pdf.circle(margin + 10, yPosition + 2, 4, 'F');
        addColoredText((index + 1).toString(), margin + 10, yPosition + 3, {
          fontSize: 9,
          fontStyle: 'bold',
          color: colors.white,
          align: 'center'
        });
        
        yPosition += addColoredText(item, margin + 20, yPosition, { fontSize: 11 });
        yPosition += 8;
      });
      yPosition += 5;
    }

    // WARNING SIGNS (Red theme)
    if (procedure.warningSignsToCallDoctor && procedure.warningSignsToCallDoctor.length > 0) {
      checkNewPage(50);
      drawColoredRect(margin, yPosition, contentWidth, 
        (procedure.warningSignsToCallDoctor.length * 12) + 25, [254, 242, 242]); // Red background
      
      yPosition += 8;
      addColoredText('⚠️ WARNING SIGNS - CALL YOUR DENTIST IMMEDIATELY', margin, yPosition, {
        fontSize: 13,
        fontStyle: 'bold',
        color: colors.red,
        align: 'center'
      });
      yPosition += 10;
      addColoredText('Contact your dental office immediately if you experience:', margin + 8, yPosition, {
        fontSize: 11,
        fontStyle: 'bold',
        color: [185, 28, 28]
      });
      yPosition += 12;

      procedure.warningSignsToCallDoctor.forEach(sign => {
        addColoredText('▲', margin + 15, yPosition, { color: colors.red, fontSize: 10 });
        yPosition += addColoredText(sign, margin + 25, yPosition, { 
          fontSize: 10, 
          color: [185, 28, 28],
          maxWidth: contentWidth - 30 
        });
        yPosition += 8;
      });
      yPosition += 10;
    }

    // RECOVERY TIMELINE (Purple theme)
    if (procedure.recoveryTimeline && procedure.recoveryTimeline.length > 0) {
      checkNewPage(40);
      drawColoredRect(margin, yPosition, 4, 15, colors.purple);
      drawColoredRect(margin, yPosition, contentWidth, 15, [243, 232, 255]); // Light purple
      yPosition += 5;
      addColoredText('📅 RECOVERY TIMELINE', margin + 10, yPosition, {
        fontSize: 14,
        fontStyle: 'bold',
        color: colors.purple
      });
      yPosition += 15;

      procedure.recoveryTimeline.forEach(timeline => {
        checkNewPage();
        // Draw purple day badge
        const dayText = `Day ${timeline.day}`;
        const badgeWidth = dayText.length * 3 + 8;
        drawColoredRect(margin + 8, yPosition - 2, badgeWidth, 8, colors.purple);
        addColoredText(dayText, margin + 12, yPosition + 2, {
          fontSize: 8,
          fontStyle: 'bold',
          color: colors.white
        });
        
        yPosition += addColoredText(timeline.activity, margin + badgeWidth + 15, yPosition, { 
          fontSize: 11,
          maxWidth: contentWidth - badgeWidth - 20
        });
        yPosition += 10;
      });
      yPosition += 5;
    }

    // MEDICATIONS (Blue theme)
    if (procedure.medications && procedure.medications.length > 0) {
      checkNewPage(40);
      drawColoredRect(margin, yPosition, 4, 15, [59, 130, 246]); // Light blue
      drawColoredRect(margin, yPosition, contentWidth, 15, [219, 234, 254]);
      yPosition += 5;
      addColoredText('💊 MEDICATIONS', margin + 10, yPosition, {
        fontSize: 14,
        fontStyle: 'bold',
        color: [59, 130, 246]
      });
      yPosition += 15;

      procedure.medications.forEach(medication => {
        checkNewPage();
        addColoredText('💊', margin + 8, yPosition, { fontSize: 10, color: [59, 130, 246] });
        yPosition += addColoredText(medication, margin + 18, yPosition, { fontSize: 11 });
        yPosition += 8;
      });

      // Important note
      yPosition += 5;
      drawColoredRect(margin, yPosition, contentWidth, 15, [239, 246, 255]);
      yPosition += 5;
      addColoredText('IMPORTANT: Always follow your dentist\'s specific medication instructions.', 
        margin + 8, yPosition, {
        fontSize: 10,
        fontStyle: 'bold',
        color: [30, 64, 175]
      });
      yPosition += 15;
    }

    // Color definitions matching the screen display
    const colors = {
      primary: [37, 99, 235],     // Blue-600
      secondary: [107, 114, 128], // Gray-500
      success: [34, 197, 94],     // Green-500
      warning: [249, 115, 22],    // Orange-500
      danger: [239, 68, 68],      // Red-500
      purple: [147, 51, 234],     // Purple-500
      lightBlue: [59, 130, 246],  // Blue-500
      text: [31, 41, 55],         // Gray-800
      lightText: [75, 85, 99],    // Gray-600
      background: [249, 250, 251], // Gray-50
      white: [255, 255, 255]
    };

    // Helper function to set color
    const setColor = (colorArray) => {
      pdf.setTextColor(colorArray[0], colorArray[1], colorArray[2]);
    };

    // Helper function to draw filled rectangle (for backgrounds and cards)
    const drawRect = (x, y, width, height, fillColor, borderColor = null) => {
      if (fillColor) {
        pdf.setFillColor(fillColor[0], fillColor[1], fillColor[2]);
        pdf.rect(x, y, width, height, 'F');
      }
      if (borderColor) {
        pdf.setDrawColor(borderColor[0], borderColor[1], borderColor[2]);
        pdf.setLineWidth(0.5);
        pdf.rect(x, y, width, height, 'S');
      }
    };

    // Helper function to draw rounded rectangle (simulated with small rectangles)
    const drawRoundedRect = (x, y, width, height, fillColor) => {
      if (fillColor) {
        pdf.setFillColor(fillColor[0], fillColor[1], fillColor[2]);
        // Main rectangle
        pdf.rect(x + 1, y, width - 2, height, 'F');
        pdf.rect(x, y + 1, width, height - 2, 'F');
        // Corner pixels for rounded effect
        pdf.rect(x + 0.5, y + 0.5, 1, 1, 'F');
        pdf.rect(x + width - 1.5, y + 0.5, 1, 1, 'F');
        pdf.rect(x + 0.5, y + height - 1.5, 1, 1, 'F');
        pdf.rect(x + width - 1.5, y + height - 1.5, 1, 1, 'F');
      }
    };

    // Helper function to add text with enhanced styling
    const addText = (text, fontSize = 12, options = {}) => {
      const {
        isBold = false,
        color = colors.text,
        indent = 0,
        align = 'left',
        backgroundColor = null,
        padding = 0
      } = options;

      pdf.setFontSize(fontSize);
      setColor(color);
      
      if (isBold) {
        pdf.setFont(undefined, 'bold');
      } else {
        pdf.setFont(undefined, 'normal');
      }

      const availableWidth = contentWidth - indent - (padding * 2);
      const lines = pdf.splitTextToSize(text, availableWidth);
      
      // Check if we need a new page
      const lineHeight = fontSize * 0.6;
      const totalHeight = lines.length * lineHeight + (padding * 2);
      
      if (yPosition + totalHeight > pageHeight - 30) {
        pdf.addPage();
        yPosition = 25;
      }

      // Add background if specified
      if (backgroundColor) {
        drawRoundedRect(
          margin + indent - padding,
          yPosition - padding,
          availableWidth + (padding * 2),
          totalHeight,
          backgroundColor
        );
      }
      
      const xPos = align === 'center' 
        ? margin + indent + (availableWidth / 2) 
        : margin + indent + padding;
      
      pdf.text(lines, xPos, yPosition + padding + (fontSize * 0.3), { 
        align: align === 'center' ? 'center' : 'left' 
      });
      yPosition += totalHeight + 4;
    };

    // Helper function to add card-style section header (like the app)
    const addSectionHeader = (title, icon, color, fontSize = 16) => {
      addSpace(10);
      
      // Add colored left border (matching the app's border-l-4 design)
      pdf.setFillColor(color[0], color[1], color[2]);
      pdf.rect(margin, yPosition, 3, 12, 'F');
      
      // Add background for header
      drawRoundedRect(margin, yPosition, contentWidth, 12, [248, 250, 252]); // Gray-50
      
      // Add icon (using text symbols for now)
      const iconSymbol = icon || '●';
      addText(`${iconSymbol} ${title.toUpperCase()}`, fontSize, {
        isBold: true,
        color: color,
        indent: 8,
        padding: 3
      });
      
      addSpace(8);
    };

    // Helper function to add numbered list with colored badges (matching the app)
    const addNumberedList = (items, color, fontSize = 12) => {
      if (!items || items.length === 0) return;
      
      items.forEach((item, index) => {
        // Clean up the item text
        const cleanItem = item.replace(/^[•·\-0-9\.)\s]*/, '').trim();
        
        // Draw circular number badge (matching the app's design)
        const badgeX = margin + 5;
        const badgeY = yPosition - 2;
        
        pdf.setFillColor(color[0] + 40, color[1] + 40, color[2] + 40); // Lighter shade for background
        pdf.circle(badgeX + 3, badgeY + 3, 3, 'F');
        
        // Add number in badge
        pdf.setFontSize(10);
        pdf.setFont(undefined, 'bold');
        setColor(color);
        pdf.text((index + 1).toString(), badgeX + 3, badgeY + 4, { align: 'center' });
        
        // Add item text
        addText(cleanItem, fontSize, {
          color: colors.text,
          indent: 15
        });
        
        addSpace(2);
      });
    };

    // Helper function to add bulleted list with colored bullets
    const addBulletList = (items, color, fontSize = 12) => {
      if (!items || items.length === 0) return;
      
      items.forEach((item) => {
        const cleanItem = item.replace(/^[•·-]\s*/, '').trim();
        
        // Add colored bullet
        pdf.setFontSize(14);
        setColor(color);
        pdf.setFont(undefined, 'bold');
        pdf.text('•', margin + 8, yPosition + 3);
        
        // Add item text
        addText(cleanItem, fontSize, {
          color: colors.text,
          indent: 15
        });
        
        addSpace(1);
      });
    };

    // Helper function to add spacing
    const addSpace = (space = 6) => {
      yPosition += space;
    };

    // Helper function to add alert box (matching the app's Alert component)
    const addAlert = (text, alertColor, backgroundColor, icon = '⚠') => {
      const alertHeight = 20;
      
      // Draw alert background
      drawRoundedRect(margin, yPosition, contentWidth, alertHeight, backgroundColor);
      
      // Draw left border
      pdf.setFillColor(alertColor[0], alertColor[1], alertColor[2]);
      pdf.rect(margin, yPosition, 3, alertHeight, 'F');
      
      // Add alert text with icon
      addText(`${icon} ${text}`, 12, {
        isBold: true,
        color: alertColor,
        padding: 4
      });
      
      addSpace(10);
    };

    // Practice Header with Professional Styling
    if (procedure.practiceName) {
      // Main practice header with background
      drawRoundedRect(margin, yPosition, contentWidth, 25, colors.primary);
      addText(procedure.practiceName, 18, {
        isBold: true,
        color: colors.white,
        align: 'center',
        padding: 6
      });
      
      // Practice details in smaller text
      if (procedure.practiceAddress || procedure.practicePhone || procedure.practiceWebsite) {
        addSpace(5);
        const details = [
          procedure.practiceAddress,
          procedure.practicePhone && `Phone: ${procedure.practicePhone}`,
          procedure.practiceWebsite
        ].filter(Boolean).join(' • ');
        
        addText(details, 10, {
          color: colors.lightText,
          align: 'center'
        });
      }
      
      addSpace(15);
    }

    // Document Header with Professional Styling
    drawRoundedRect(margin, yPosition, contentWidth, 30, [241, 245, 249]); // Blue-50
    addText('Post-Operative Care Guide', 20, {
      isBold: true,
      color: colors.primary,
      align: 'center',
      padding: 8
    });
    
    // Procedure name with badge
    drawRoundedRect(margin + 20, yPosition, contentWidth - 40, 15, colors.secondary);
    addText(procedure.specialtyName, 10, {
      isBold: true,
      color: colors.white,
      align: 'center',
      padding: 3
    });
    
    addSpace(8);
    addText(procedure.name, 18, {
      isBold: true,
      color: colors.text,
      align: 'center'
    });
    
    // Check if this is a patient-specific assignment or general library procedure
    const isPatientAssignment = procedure.patientName && procedure.performedDate;
    
    if (isPatientAssignment) {
      addSpace(15);
      
      // Assignment Information Section with professional styling
      addSectionHeader('Assignment Information', '👤', colors.lightBlue);
      
      // Patient Details Card
      drawRoundedRect(margin, yPosition, contentWidth, 25, [248, 250, 252]); // Gray-50
      addText('Patient Details', 13, {
        isBold: true,
        color: colors.text,
        padding: 4
      });
      
      yPosition -= 5; // Adjust for same card
      addText(`Patient: ${procedure.patientName}`, 11, {
        color: colors.text,
        padding: 4
      });
      
      if (procedure.patientEmail) {
        yPosition -= 5;
        addText(`Email: ${procedure.patientEmail}`, 11, {
          color: colors.lightText,
          padding: 4
        });
      }
      
      addSpace(10);
      
      // Treatment Details Card
      drawRoundedRect(margin, yPosition, contentWidth, 30, [248, 250, 252]);
      addText('Treatment Details', 13, {
        isBold: true,
        color: colors.text,
        padding: 4
      });
      
      const treatmentDetails = [
        `Performed: ${procedure.performedDate}`,
        procedure.followUpDate && `Follow-up: ${procedure.followUpDate}`,
        procedure.dentistName && `Dentist: ${procedure.dentistName}`,
        `Status: ${procedure.status || 'active'}`
      ].filter(Boolean);
      
      treatmentDetails.forEach(detail => {
        yPosition -= 5;
        addText(detail, 11, {
          color: colors.text,
          padding: 4
        });
      });
      
      addSpace(15);

      // Practice Notes Section
      if (procedure.practiceNotes) {
        addSectionHeader('Practice Notes', '📝', colors.secondary);
        drawRoundedRect(margin, yPosition, contentWidth, 15, [249, 250, 251]);
        addText(procedure.practiceNotes, 11, {
          color: colors.text,
          padding: 4
        });
        addSpace(10);
      }

      // Custom Instructions Section
      if (procedure.customInstructions && procedure.customInstructions.length > 0) {
        addSectionHeader('Custom Instructions', '✏️', colors.purple);
        drawRoundedRect(margin, yPosition, contentWidth, 15, [248, 250, 252]);
        addText(procedure.customInstructions, 11, {
          color: colors.text,
          padding: 4
        });
        addSpace(10);
      }
    } else {
      // For library procedures, add specialty info with styling
      if (procedure.specialtyName || procedure.duration) {
        addSpace(10);
        
        const libraryInfo = [
          procedure.specialtyName && `Specialty: ${procedure.specialtyName}`,
          procedure.duration && `Typical Recovery: ${procedure.duration}`
        ].filter(Boolean).join(' • ');
        
        drawRoundedRect(margin, yPosition, contentWidth, 12, [243, 244, 246]); // Gray-100
        addText(libraryInfo, 11, {
          color: colors.lightText,
          align: 'center',
          padding: 3
        });
        
        addSpace(10);
      }
    }

    addSpace(20);

    // Overview Section (matching the app's card design)
    if (procedure.overview) {
      addSectionHeader('Overview', '●', colors.primary);
      
      // Parse overview exactly like ProcedurePage.jsx does
      const lines = procedure.overview.split('\n');
      lines.forEach((line) => {
        const trimmedLine = line.trim();
        
        // Handle empty lines - create spacing
        if (trimmedLine === '') {
          addSpace(3);
          return;
        }
        
        // Handle bullet points with blue bullets (matching app)
        if (trimmedLine.startsWith('•') || trimmedLine.startsWith('-')) {
          const bulletText = trimmedLine.replace(/^[•-]\s*/, '');
          
          // Add blue bullet
          pdf.setFontSize(12);
          setColor(colors.primary);
          pdf.setFont(undefined, 'bold');
          pdf.text('•', margin + 8, yPosition + 3);
          
          // Add bullet text
          addText(bulletText, 11, {
            color: colors.text,
            indent: 15
          });
          return;
        }
        
        // Handle markdown-style headers (**text**)
        if (trimmedLine.includes('**')) {
          if (trimmedLine.startsWith('**') && trimmedLine.endsWith('**') && trimmedLine.length > 4) {
            const headerText = trimmedLine.replace(/\*\*/g, '');
            addText(headerText, 13, {
              isBold: true,
              color: colors.text
            });
            addSpace(3);
            return;
          }
          // Handle mixed content - simplified for PDF
          else {
            const cleanText = trimmedLine.replace(/\*\*/g, '');
            addText(cleanText, 11, {
              color: colors.text
            });
            return;
          }
        }
        
        // Regular paragraphs
        if (trimmedLine.length > 0) {
          addText(trimmedLine, 11, {
            color: colors.text
          });
          addSpace(2);
        }
      });
    }
    
    // Emergency Alert (red alert box matching the app)
    addAlert(
      'EMERGENCY: If you experience severe bleeding, difficulty breathing, or signs of severe allergic reaction, call 911 IMMEDIATELY.',
      colors.danger,
      [254, 242, 242], // Red-50
      '🚨'
    );
    
    // Immediate Aftercare (green section like the app)
    if (procedure.immediateAftercare && procedure.immediateAftercare.length > 0) {
      addSectionHeader('Immediate Aftercare', '♥', colors.success);
      addNumberedList(procedure.immediateAftercare, colors.success);
      addSpace(10);
    }

    // Diet Restrictions (orange section like the app)
    if (procedure.dietRestrictions && procedure.dietRestrictions.length > 0) {
      addSectionHeader('Diet Restrictions', '🍽', colors.warning);
      addNumberedList(procedure.dietRestrictions, colors.warning);
      addSpace(10);
    }

    // Warning Signs (red section with background like the app)
    if (procedure.warningSignsToCallDoctor && procedure.warningSignsToCallDoctor.length > 0) {
      addSpace(10);
      
      // Red warning section with background
      const warningHeight = (procedure.warningSignsToCallDoctor.length * 8) + 25;
      drawRoundedRect(margin, yPosition, contentWidth, warningHeight, [254, 242, 242]); // Red-50
      
      // Warning header
      addText('⚠️ WARNING SIGNS - CALL YOUR DENTIST IMMEDIATELY', 14, {
        isBold: true,
        color: colors.danger,
        padding: 4
      });
      
      addText('Contact your dental office immediately if you experience any of the following:', 11, {
        isBold: true,
        color: [185, 28, 28], // Red-700
        padding: 2
      });
      
      addSpace(5);
      
      // Warning signs with triangular warning icons
      procedure.warningSignsToCallDoctor.forEach((sign) => {
        const cleanSign = sign.replace(/^[•·-]\s*/, '').trim();
        
        // Add warning triangle
        pdf.setFontSize(10);
        setColor(colors.danger);
        pdf.setFont(undefined, 'bold');
        pdf.text('▲', margin + 8, yPosition + 3);
        
        // Add warning text
        addText(cleanSign, 11, {
          color: [185, 28, 28], // Red-700
          indent: 15
        });
        
        addSpace(1);
      });
      
      addSpace(10);
    }

    // Recovery Timeline (purple section like the app)
    if (procedure.recoveryTimeline && procedure.recoveryTimeline.length > 0) {
      addSectionHeader('Recovery Timeline', '📅', colors.purple);
      
      procedure.recoveryTimeline.forEach((timeline) => {
        // Draw day badge (matching the app's purple badges)
        const badgeX = margin + 5;
        const badgeY = yPosition - 2;
        
        drawRoundedRect(badgeX, badgeY, 20, 8, colors.purple);
        
        pdf.setFontSize(9);
        pdf.setFont(undefined, 'bold');
        setColor(colors.white);
        pdf.text(`Day ${timeline.day}`, badgeX + 10, badgeY + 5, { align: 'center' });
        
        // Add activity description
        addText(timeline.activity, 11, {
          color: colors.text,
          indent: 30
        });
        
        addSpace(3);
      });
      
      addSpace(10);
    }

    // Medications (blue section like the app)
    if (procedure.medications && procedure.medications.length > 0) {
      addSectionHeader('Medications', '💊', colors.lightBlue);
      
      procedure.medications.forEach((medication) => {
        const cleanMed = medication.replace(/^[•·-]\s*/, '').trim();
        
        // Add pill icon
        pdf.setFontSize(10);
        setColor(colors.lightBlue);
        pdf.setFont(undefined, 'bold');
        pdf.text('💊', margin + 8, yPosition + 3);
        
        // Add medication text
        addText(cleanMed, 11, {
          color: colors.text,
          indent: 15
        });
        
        addSpace(1);
      });
      
      // Important note (like the app's blue info box)
      addSpace(5);
      drawRoundedRect(margin, yPosition, contentWidth, 15, [239, 246, 255]); // Blue-50
      addText('IMPORTANT: Always follow your dentist\'s specific medication instructions. These are general guidelines only.', 10, {
        isBold: true,
        color: [30, 64, 175], // Blue-800
        padding: 4
      });
      
      addSpace(10);
    }

    // Contact Information (gray section like the app)
    addSectionHeader('Need Help?', '📞', colors.secondary);
    
    addText('If you have questions about your recovery or need to speak with your dental team:', 11, {
      color: colors.text
    });
    
    addSpace(8);
    
    // Office hours box
    drawRoundedRect(margin, yPosition, (contentWidth / 2) - 5, 20, colors.white);
    pdf.setDrawColor(colors.secondary[0], colors.secondary[1], colors.secondary[2]);
    pdf.setLineWidth(0.5);
    pdf.rect(margin, yPosition, (contentWidth / 2) - 5, 20, 'S');
    
    addText('Office Hours', 12, {
      isBold: true,
      color: colors.text,
      padding: 3
    });
    yPosition -= 8; // Adjust position for next text in same box
    addText('Contact your dental office during regular business hours', 9, {
      color: colors.lightText,
      padding: 3
    });
    
    // After hours box (positioned next to office hours)
    const afterHoursX = margin + (contentWidth / 2) + 5;
    yPosition -= 12; // Reset to box top
    drawRoundedRect(afterHoursX, yPosition, (contentWidth / 2) - 5, 20, colors.white);
    pdf.rect(afterHoursX, yPosition, (contentWidth / 2) - 5, 20, 'S');
    
    // Manually position after hours text
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'bold');
    setColor(colors.text);
    pdf.text('After Hours', afterHoursX + 3, yPosition + 8);
    
    pdf.setFontSize(9);
    pdf.setFont(undefined, 'normal');
    setColor(colors.lightText);
    pdf.text('Follow your dentist\'s emergency contact instructions', afterHoursX + 3, yPosition + 15);
    
    yPosition += 25; // Move past the boxes
    
    if (procedure.practiceName || procedure.practicePhone) {
      addSpace(10);
      if (procedure.practiceName) {
        addText(`Practice: ${procedure.practiceName}`, 11, {
          isBold: true,
          color: colors.text
        });
      }
      if (procedure.practicePhone) {
        addText(`Phone: ${procedure.practicePhone}`, 11, {
          isBold: true,
          color: colors.primary
        });
      }
    }
    
    addSpace(8);
    addText('For emergencies, contact your dentist immediately or call 911.', 11, {
      isBold: true,
      color: colors.danger
    });

    // Save the PDF with clean filename
    const procedureName = procedure.name ? procedure.name.replace(/[^a-zA-Z0-9\s]/g, '').replace(/\s+/g, '_') : 'procedure';
    const patientPart = procedure.patientName ? `_${procedure.patientName.replace(/[^a-zA-Z0-9\s]/g, '').replace(/\s+/g, '_')}` : '';
    const fileName = `${procedureName}${patientPart}_PostOp_Care.pdf`;
    
    pdf.save(fileName);
    console.log('✅ Enhanced PDF generated successfully with WYSIWYG styling');
    
    return true;
  } catch (error) {
    console.error('❌ Error generating enhanced PDF:', error);
    return false;
  }
};
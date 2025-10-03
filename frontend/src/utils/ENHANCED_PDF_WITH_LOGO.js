import jsPDF from 'jspdf';

// ENHANCED PDF GENERATOR WITH LOGO AND BOLD FORMATTING
export const generateProcedurePDF = async (procedure, practiceData) => {
  // Force timestamp to bust cache
  const timestamp = new Date().toISOString();
  const cacheKey = Date.now();
  
  console.log('🚨 ENHANCED PDF WITH LOGO GENERATOR LOADED - v17 (LOGO FIX)');
  console.log('🔍 Procedure data:', procedure?.name);
  console.log('🔍 Practice data structure:', practiceData);
  console.log('🔍 Practice branding:', practiceData?.branding);
  console.log('🔍 Practice logo:', practiceData?.branding?.logo ? `${practiceData.branding.logo.substring(0, 50)}...` : 'No logo');
  
  try {
    const pdf = new jsPDF();
    let yPos = 20;
    
    // Add logo at the top centered using practice custom logo
    try {
      // Try to use practice custom logo first
      let logoAdded = false;
      
      if (practiceData?.branding?.logo) {
        try {
          const logoData = practiceData.branding.logo;
          
          // Check if logo is corrupted (1x1 pixel placeholder)
          if (logoData.length < 200) {
            console.log('❌ Logo appears to be corrupted placeholder (too small):', logoData.length, 'characters');
            console.log('❌ Logo content:', logoData.substring(0, 100) + '...');
          } else {
            console.log('✅ Logo data looks valid:', logoData.length, 'characters');
          }
          
          console.log('🖼️ Adding custom logo to PDF...');
          
          // Handle different logo data formats
          let processedLogoData = logoData;
          
          // If logo data is a data URL, use it directly; if it's just base64, add the prefix
          if (!logoData.startsWith('data:image')) {
            processedLogoData = `data:image/png;base64,${logoData}`;
          }
          
          console.log('🖼️ Using logo format:', processedLogoData.substring(0, 30) + '...');
          
          // Use jsPDF's built-in getImageProperties for accurate dimensions
          try {
            const imageProps = pdf.getImageProperties(processedLogoData);
            console.log(`📏 Image properties:`, imageProps);
            
            if (imageProps && imageProps.width && imageProps.height) {
              // Calculate aspect ratio from actual image properties
              const aspectRatio = imageProps.width / imageProps.height;
              console.log(`📏 Aspect ratio: ${aspectRatio}`);
              
              // Set maximum dimensions for the logo in the PDF
              const maxWidth = 60;  // Maximum logo width in PDF units
              const maxHeight = 45; // Maximum logo height in PDF units
              
              let finalWidth, finalHeight;
              
              if (aspectRatio > maxWidth / maxHeight) {
                // Wide image - limit by width
                finalWidth = maxWidth;
                finalHeight = maxWidth / aspectRatio;
              } else {
                // Tall image - limit by height  
                finalHeight = maxHeight;
                finalWidth = maxHeight * aspectRatio;
              }
              
              console.log(`📏 Final calculated dimensions: ${finalWidth.toFixed(2)}x${finalHeight.toFixed(2)}`);
              
              // Calculate centered position
              const xPos = (pdf.internal.pageSize.width - finalWidth) / 2;
              
              // Add custom practice logo with proper aspect ratio
              pdf.addImage(processedLogoData, 'PNG', xPos, yPos, finalWidth, finalHeight);
              yPos += finalHeight + 10;
              logoAdded = true;
              
              console.log('✅ Custom logo added successfully with preserved aspect ratio');
              
            } else {
              throw new Error('Could not get image properties');
            }
            
          } catch (dimensionError) {
            console.log(`⚠️ Could not calculate aspect ratio (${dimensionError.message}), using proportional default`);
            
            // Use a reasonable square-ish default that works for most logos
            const imgWidth = 50;
            const imgHeight = 40;  // Slightly rectangular default
            const xPos = (pdf.internal.pageSize.width - imgWidth) / 2;
            
            pdf.addImage(processedLogoData, 'PNG', xPos, yPos, imgWidth, imgHeight);
            yPos += imgHeight + 10;
            logoAdded = true;
            
            console.log('✅ Custom logo added with default proportional dimensions');
          }
          
        } catch (customLogoError) {
          console.log('❌ Custom logo failed:', customLogoError.message);
          console.log('⚠️ Using fallback logo instead');
        }
      } else {
        console.log('❌ No custom logo found in practice data');
        console.log('🔍 Practice data structure:', practiceData);
        console.log('🔍 Branding data:', practiceData?.branding);
      }
      
      // Fallback to default logo if custom logo failed
      if (!logoAdded) {
        try {
          console.log('⚠️ Falling back to default logo');
          const response = await fetch('/dental-rescue-logo-base64.txt');
          if (response.ok) {
            const base64Logo = await response.text();
            if (base64Logo) {
              const imgWidth = 40;
              const imgHeight = 30;
              const xPos = (pdf.internal.pageSize.width - imgWidth) / 2;
              
              pdf.addImage(`data:image/png;base64,${base64Logo}`, 'PNG', xPos, yPos, imgWidth, imgHeight);
              yPos += imgHeight + 10;
              logoAdded = true;
              console.log('✅ Default logo successfully added to PDF');
            }
          }
        } catch (defaultLogoError) {
          console.log('⚠️ Failed to load default logo:', defaultLogoError);
        }
      }
      
      // Final fallback to text header if no logo worked
      if (!logoAdded) {
        console.log('ℹ️ Using text header as final fallback');
        pdf.setFontSize(18);
        pdf.setFont(undefined, 'bold');
        pdf.setTextColor(41, 98, 184);
        const practiceTitle = practiceData?.practiceName || 'DENTAL RESCUE NOTES';
        pdf.text(practiceTitle, 105, yPos, { align: 'center' });
        yPos += 15;
      }
      
    } catch (logoError) {
      console.log('❌ Logo handling failed, using text header:', logoError);
      // Fall back to text header with practice name
      pdf.setFontSize(18);
      pdf.setFont(undefined, 'bold');
      pdf.setTextColor(41, 98, 184);
      const practiceTitle = practiceData?.practiceName || 'DENTAL RESCUE NOTES';
      pdf.text(practiceTitle, 105, yPos, { align: 'center' });
      yPos += 15;
    }
    
    // Subtitle
    pdf.setFontSize(10);
    pdf.setFont(undefined, 'normal');
    pdf.setTextColor(100, 100, 100);
    pdf.text('Post-Operative Care Instructions', 105, yPos, { align: 'center' });
    yPos += 15;
    
    // Decorative line under the header
    pdf.setDrawColor(41, 98, 184);
    pdf.setLineWidth(1);
    pdf.line(50, yPos, 160, yPos);
    yPos += 20;
    
    // Title - handle different data structures
    const procedureName = procedure?.name || procedure?.procedureName || 'Procedure';
    pdf.setTextColor(0, 0, 0); // Reset to black
    pdf.setFontSize(16);
    pdf.setFont(undefined, 'bold');
    pdf.text(procedureName, 20, yPos);
    yPos += 20;
    
    // Get procedure content from available data sources
    
    // Get the overview content - first try from the procedure object, then fetch from API if needed
    let overviewContent = procedure?.overview || 
                          procedure?.procedureDetails?.overview || 
                          procedure?.procedureData?.overview ||
                          procedure?.content ||
                          procedure?.instructions ||
                          procedure?.description ||
                          '';
    
    // If no content found in procedure object, try to fetch it from the API
    if (!overviewContent && procedure?.procedureId) {
      try {
        // Use the existing authApi service to maintain consistent authentication
        const { practiceApi } = await import('../services/authApi');
        const response = await practiceApi.getPracticeProcedures();
        
        if (response.success && response.procedures) {
          // Find the procedure by ID
          const fullProcedure = response.procedures.find(p => p.id === procedure.procedureId);
          if (fullProcedure) {
            overviewContent = fullProcedure.overview || fullProcedure.content || fullProcedure.description || '';
          } else {
            // Try alternative search by name
            const byName = response.procedures.find(p => p.name === procedure.procedureName);
            if (byName) {
              overviewContent = byName.overview || byName.content || byName.description || '';
            }
          }
        } else {
          console.log('⚠️ API response not successful:', response);
        }
      } catch (apiError) {
        console.log('⚠️ Failed to fetch procedure content from API:', apiError);
      }
    }
    
    if (overviewContent) {
      // Add formatted content to PDF with simple bold detection
      addSimpleFormattedContentToPDF(pdf, overviewContent, yPos);
      
    } else {
      // If no overview content, add some basic text
      pdf.setFontSize(11);
      pdf.text('Post-operative care instructions will be available here.', 20, yPos);
      yPos += 15;
      pdf.text('Please follow up with your dental practice for specific instructions.', 20, yPos);
    }
    
    // Add practice information footer
    addPracticeFooter(pdf, procedure);
    
    // Save with timestamp filename
    const filenameProcedureName = procedure?.name || procedure?.procedureName || 'Procedure';
    const filename = `${filenameProcedureName.replace(/[^a-zA-Z0-9]/g, '_')}_RAW_${cacheKey}.pdf`;
    
    console.log('🚨 About to save PDF:', filename);
    console.log('🚨 PDF object:', pdf);
    console.log('🚨 Calling pdf.save()...');
    
    // Try to save the PDF with error handling
    try {
      pdf.save(filename);
      console.log('✅ ENHANCED PDF SAVE COMMAND EXECUTED:', filename);
      
      // Give a moment for the download to start
      setTimeout(() => {
        console.log('✅ PDF save complete (after timeout)');
      }, 1000);
      
    } catch (saveError) {
      console.error('❌ PDF save error:', saveError);
      throw new Error(`PDF save failed: ${saveError.message}`);
    }
    
    return true;
    
  } catch (error) {
    console.error('🚨 ENHANCED PDF ERROR:', error);
    return false;
  }
};

// Function to process content and identify words/phrases that should be bold
function processContentForBoldFormatting(content) {
  const boldKeywords = [
    'Purpose',
    'Instructions',
    'First 24 Hours',
    'First 24 hours',
    'First Twenty-Four Hours',
    'Pain & Sensitivity',
    'Pain and Sensitivity',
    'Pain & Swelling',
    'Pain and Swelling',
    'Pain Management',
    'Pain Control',
    'Bleeding',
    'Blood/Bleeding',
    'Oral Hygiene',
    'Oral Care',
    'Mouth Care',
    'Diet',
    'Dietary Instructions',
    'Eating',
    'Food',
    'Special Precautions',
    'Precautions',
    'Important Notes',
    'Follow-Up',
    'Follow Up',
    'Follow-up',
    'Followup',
    'Next Appointment',
    'Return Visit',
    'Activity',
    'Activities',
    'Medications',
    'Medicine',
    'Swelling',
    'Ice/Cold Therapy',
    'Ice Application',
    'Healing',
    'Recovery',
    'Warning Signs',
    'When to Call',
    'Emergency'
  ];
  
  // Create an array of content segments with formatting info
  const segments = [];
  let remainingContent = content;
  
  while (remainingContent.length > 0) {
    let foundKeyword = false;
    let earliestIndex = remainingContent.length;
    let matchedKeyword = null;
    
    // Find the earliest occurring keyword
    for (const keyword of boldKeywords) {
      const regex = new RegExp(`\\b${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
      const match = remainingContent.match(regex);
      
      if (match && match.index < earliestIndex) {
        earliestIndex = match.index;
        matchedKeyword = {
          keyword: keyword,
          actualText: match[0],
          index: match.index
        };
        foundKeyword = true;
      }
    }
    
    if (foundKeyword && matchedKeyword) {
      // Add text before the keyword as normal
      if (matchedKeyword.index > 0) {
        const beforeText = remainingContent.substring(0, matchedKeyword.index);
        if (beforeText.trim()) {
          segments.push({
            text: beforeText,
            bold: false
          });
        }
      }
      
      // Add the keyword as bold
      segments.push({
        text: matchedKeyword.actualText,
        bold: true
      });
      
      // Continue with remaining text
      remainingContent = remainingContent.substring(matchedKeyword.index + matchedKeyword.actualText.length);
    } else {
      // No more keywords, add remaining text as normal
      if (remainingContent.trim()) {
        segments.push({
          text: remainingContent,
          bold: false
        });
      }
      break;
    }
  }
  
  return segments;
}

// Function to add practice information footer to all pages
function addPracticeFooter(pdf, procedure) {
  const pageCount = pdf.internal.getNumberOfPages();
  
  // Extract practice information from procedure data
  const practiceName = procedure?.practiceName || 
                      procedure?.practice?.name || 
                      procedure?.practiceData?.name || 
                      'Your Practice Name';
                      
  const practicePhone = procedure?.practicePhone || 
                       procedure?.practice?.phone || 
                       procedure?.practiceData?.phone ||
                       procedure?.practiceEmergencyContact || 
                       procedure?.practice?.emergencyContact ||
                       'Contact Number Not Available';

  console.log('📋 Adding practice footer:', { practiceName, practicePhone });
  
  // Add footer to all pages
  for (let i = 1; i <= pageCount; i++) {
    pdf.setPage(i);
    
    // Footer styling
    pdf.setFont('times', 'normal');
    pdf.setFontSize(10);
    pdf.setTextColor(80, 80, 80); // Gray color
    
    // Add a line above footer
    pdf.setDrawColor(200, 200, 200);
    pdf.setLineWidth(0.5);
    pdf.line(20, 275, 190, 275);
    
    // Practice name (left side)
    pdf.text(practiceName, 20, 285);
    
    // Practice phone (right side)
    const phoneText = `Phone: ${practicePhone}`;
    const phoneTextWidth = pdf.getTextWidth(phoneText);
    pdf.text(phoneText, 190 - phoneTextWidth, 285);
    
    // Page number (center)
    if (pageCount > 1) {
      const pageText = `Page ${i} of ${pageCount}`;
      const pageTextWidth = pdf.getTextWidth(pageText);
      pdf.text(pageText, (210 - pageTextWidth) / 2, 290);
    }
  }
  
  // Reset text color
  pdf.setTextColor(0, 0, 0);
}
function addSimpleFormattedContentToPDF(pdf, content, startY) {
  let yPos = startY;
  const lineHeight = 5.5;
  const paragraphSpacing = 8; // Extra space between paragraphs
  const maxWidth = 170;
  const leftMargin = 20;
  
  // Set consistent font
  pdf.setFont('times', 'normal');
  pdf.setFontSize(11);
  pdf.setTextColor(0, 0, 0);
  
  console.log('🎯 Processing PDF content for formatting...');
  
  // Define section headers that should be bold (more comprehensive)
  const sectionHeaders = [
    'Purpose:',
    'Instructions:',
    'First 24 Hours:',
    'First 24 hours:',
    'First Twenty-Four Hours:',
    'Pain & Sensitivity:',
    'Pain and Sensitivity:',
    'Pain & Swelling:',
    'Pain and Swelling:',
    'Pain Management:',
    'Pain Control:',
    'Bleeding:',
    'Blood/Bleeding:',
    'Oral Hygiene:',
    'Oral Care:',
    'Mouth Care:',
    'Diet:',
    'Dietary Instructions:',
    'Eating:',
    'Food:',
    'Special Precautions:',
    'Precautions:',
    'Important Notes:',
    'Follow-Up:',
    'Follow Up:',
    'Follow-up:',
    'Followup:',
    'Next Appointment:',
    'Return Visit:',
    'Activity:',
    'Activities:',
    'Medications:',
    'Medicine:',
    'Swelling:',
    'Ice/Cold Therapy:',
    'Ice Application:',
    'Healing:',
    'Recovery:',
    'Warning Signs:',
    'When to Call:',
    'Emergency:',
    'Do Not:',
    'Avoid:',
    'Remember:',
    'Note:'
  ];
  
  // First, split content into paragraphs (double line breaks or section breaks)
  const paragraphs = content.split(/\n\s*\n|\r\n\s*\r\n/).filter(p => p.trim().length > 0);
  
  console.log(`🎯 Found ${paragraphs.length} paragraphs to format`);
  
  for (let i = 0; i < paragraphs.length; i++) {
    const paragraph = paragraphs[i].trim();
    if (!paragraph) continue;
    
    console.log(`🎯 Processing paragraph ${i + 1}: ${paragraph.substring(0, 50)}...`);
    
    // Check if this paragraph starts with a section header
    let isSectionHeader = false;
    let headerText = '';
    let bodyText = '';
    
    for (const header of sectionHeaders) {
      if (paragraph.toLowerCase().startsWith(header.toLowerCase())) {
        isSectionHeader = true;
        headerText = header;
        bodyText = paragraph.substring(header.length).trim();
        console.log(`✅ Found section header: "${header}"`);
        break;
      }
    }
    
    if (isSectionHeader && headerText) {
      // Add extra space before section headers (except first one)
      if (i > 0) {
        yPos += paragraphSpacing;
      }
      
      // Check if we need a new page
      if (yPos > 270) {
        pdf.addPage();
        yPos = 20;
      }
      
      // Render bold section header
      pdf.setFont('times', 'bold');
      pdf.text(headerText, leftMargin, yPos);
      yPos += lineHeight;
      
      // Render body text if present
      if (bodyText) {
        pdf.setFont('times', 'normal');
        const bodyLines = pdf.splitTextToSize(bodyText, maxWidth);
        
        for (const line of bodyLines) {
          if (yPos > 270) {
            pdf.addPage();
            yPos = 20;
          }
          
          pdf.text(line, leftMargin, yPos);
          yPos += lineHeight;
        }
      }
    } else {
      // Regular paragraph - not a section header
      if (i > 0) {
        yPos += paragraphSpacing / 2; // Smaller space between regular paragraphs
      }
      
      pdf.setFont('times', 'normal');
      const lines = pdf.splitTextToSize(paragraph, maxWidth);
      
      for (const line of lines) {
        if (yPos > 270) {
          pdf.addPage();
          yPos = 20;
        }
        
        pdf.text(line, leftMargin, yPos);
        yPos += lineHeight;
      }
    }
  }
  
  // Reset font
  pdf.setFont('times', 'normal');
  console.log('✅ PDF content formatting complete');
}
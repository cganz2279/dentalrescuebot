// Format original PDF content to match the user's provided structure
const formatOriginalPDFContent = (content) => {
  if (!content) return '<p>No content available</p>';
  
  // Split content by sections and format properly
  let formattedContent = content
    // Handle Purpose section
    .replace(/Purpose:\s*/gi, '<h4>Purpose:</h4><p>')
    // Handle First 24 Hours section
    .replace(/First 24 Hours:\s*/gi, '</p><h4>First 24 Hours:</h4><p>')
    // Handle Pain & Sensitivity section
    .replace(/Pain & Sensitivity:\s*/gi, '</p><h4>Pain & Sensitivity:</h4><p>')
    // Handle Oral Hygiene section
    .replace(/Oral Hygiene:\s*/gi, '</p><h4>Oral Hygiene:</h4><p>')
    // Handle Diet section
    .replace(/Diet:\s*/gi, '</p><h4>Diet:</h4><p>')
    // Handle Special Precautions section
    .replace(/Special Precautions:\s*/gi, '</p><h4>Special Precautions:</h4><p>')
    // Handle Follow-Up section
    .replace(/Follow-Up:\s*/gi, '</p><h4>Follow-Up:</h4><p>')
    // Handle bullet points starting with -
    .replace(/- ([^-\n]+)/g, '<br>• $1')
    // Clean up any double paragraph tags
    .replace(/<\/p><p>/g, '<br><br>')
    // Add closing paragraph tag
    + '</p>';
  
  // Clean up any issues
  formattedContent = formattedContent
    .replace(/^<\/p>/, '') // Remove opening </p>
    .replace(/<p><\/p>/g, '') // Remove empty paragraphs
    .replace(/<br><br><h4>/g, '</p><h4>') // Fix spacing before headers
    .replace(/<h4>/g, '<h4 style="color: #1f2937; font-weight: 600; margin: 16px 0 8px 0;">');
  
  return formattedContent;
};

// Helper function to format phone numbers
const formatPhoneNumber = (phone) => {
  if (!phone) return '';
  
  // Remove all non-digit characters
  const cleaned = phone.replace(/\D/g, '');
  
  // Format based on length
  if (cleaned.length === 10) {
    // US format: (123) 456-7890
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  } else if (cleaned.length === 11 && cleaned[0] === '1') {
    // US format with country code: +1 (123) 456-7890
    return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  } else {
    // Return original if can't format
    return phone;
  }
};

// Improved PDF Generator with better popup handling
export const generateProcedurePDF = async (procedure) => {
  try {
    console.log('🎨 Starting PDF generation...');
    
    // Create optimized HTML content with print-specific styling
    const printContent = createOptimizedPrintHTML(procedure);
    
    // Create new window with specific parameters to prevent blocking
    const printWindow = window.open('', 'PDFWindow', 'width=800,height=600,scrollbars=yes,resizable=yes');
    
    if (!printWindow) {
      throw new Error('Popup blocked. Please allow popups and try again.');
    }
    
    // Write content to window
    printWindow.document.open();
    printWindow.document.write(printContent);
    printWindow.document.close();
    
    // Wait for content to fully load before showing
    printWindow.addEventListener('load', () => {
      console.log('✅ PDF content loaded successfully');
      
      // Focus and show print dialog after a longer delay
      setTimeout(() => {
        printWindow.focus();
        
        // Add user instruction
        if (!printWindow.closed) {
          printWindow.print();
        }
        
        // Don't auto-close - let user close manually
        printWindow.onafterprint = () => {
          console.log('✅ Print dialog completed');
          // Optional: auto-close after 30 seconds
          setTimeout(() => {
            if (!printWindow.closed) {
              printWindow.close();
            }
          }, 30000);
        };
        
      }, 1500); // Longer delay to ensure content is ready
    });
    
    return true;
    
  } catch (error) {
    console.error('❌ PDF generation failed:', error);
    alert('PDF generation failed: ' + error.message + '\n\nPlease check your popup blocker settings.');
    return false;
  }
};

// Create optimized HTML that matches the View page layout exactly
const createOptimizedPrintHTML = (procedure) => {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${procedure.name} - Care Guide</title>
    <style>
        @page {
            size: A4;
            margin: 1in;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #374151;
            margin: 0;
            padding: 0;
            background: white;
        }
        
        .header {
            text-align: center;
            margin-bottom: 32px;
            padding-bottom: 24px;
            border-bottom: 3px solid #2563eb;
        }
        
        .procedure-title {
            font-size: 28px;
            font-weight: bold;
            color: #1f2937;
            margin-bottom: 8px;
        }
        
        .specialty-badge {
            display: inline-block;
            background: #dbeafe;
            color: #1d4ed8;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 16px;
        }
        
        .practice-info {
            margin-top: 16px;
            font-size: 16px;
            color: #4b5563;
        }
        
        .practice-name {
            font-weight: 600;
            color: #1f2937;
        }
        
        .content-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
        }
        
        .card-header {
            font-size: 20px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
        }
        
        .overview-content p {
            margin-bottom: 12px;
            color: #4b5563;
        }
        
        .overview-content h4 {
            color: #1f2937;
            font-weight: 600;
            margin: 16px 0 8px 0;
        }
        
        .overview-bullet {
            display: flex;
            margin-bottom: 8px;
            align-items: flex-start;
        }
        
        .overview-bullet-point {
            color: #2563eb;
            margin-right: 8px;
            font-weight: bold;
            margin-top: 2px;
        }
        
        .footer-info {
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            font-size: 14px;
            color: #6b7280;
        }
        
        .footer-info p {
            margin: 4px 0;
        }
        
        .footer-info strong {
            color: #374151;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="procedure-title">${procedure.name}</div>
        ${procedure.specialtyName ? `<div class="specialty-badge">${procedure.specialtyName}</div>` : ''}
        ${procedure.duration ? `<div style="color: #6b7280; font-size: 14px;">Estimated Duration: ${procedure.duration}</div>` : ''}
        
        ${procedure.practiceName || procedure.practicePhone || procedure.practiceAddress ? `
            <div class="practice-info">
                ${procedure.practiceName ? `<div class="practice-name">${procedure.practiceName}</div>` : ''}
                ${procedure.practicePhone ? `<div>📞 ${formatPhoneNumber(procedure.practicePhone)}</div>` : ''}
                ${procedure.practiceAddress ? `<div>📍 ${procedure.practiceAddress}</div>` : ''}
                ${procedure.practiceEmail ? `<div>📧 ${procedure.practiceEmail}</div>` : ''}
            </div>
        ` : ''}
    </div>
    
    <!-- ONLY Overview Content -->
    ${procedure.overview ? `
        <div class="content-card">
            <div class="card-header">
                <span style="margin-right: 8px;">📋</span>
                Post-Operative Care Instructions
            </div>
            <div class="overview-content">
                ${formatOriginalPDFContent(procedure.overview)}
            </div>
        </div>
    ` : ''}
    
    <!-- Footer -->
    <div class="footer-info">
        <p>
            Generated on ${new Date().toLocaleDateString()} | 
            ${procedure.practiceName || 'Your Dental Practice'} | 
            Post-Operative Care Guide
        </p>
        ${procedure.emergencyContact || procedure.practicePhone ? `
            <p style="margin-top: 8px;">
                <strong>Emergency Contact:</strong> ${formatPhoneNumber(procedure.emergencyContact || procedure.practicePhone)}
            </p>
        ` : ''}
        ${procedure.afterHoursContact ? `
            <p style="margin-top: 4px;">
                <strong>After Hours:</strong> ${formatPhoneNumber(procedure.afterHoursContact)}
            </p>
        ` : ''}
        ${procedure.dentistName ? `
            <p style="margin-top: 8px;">
                <strong>Your Doctor:</strong> ${procedure.dentistName}
            </p>
        ` : ''}
    </div>
</body>
</html>
  `;
};








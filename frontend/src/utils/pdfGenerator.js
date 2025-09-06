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
                ${procedure.overview.split('\n').map(line => {
                    const trimmedLine = line.trim();
                    
                    if (trimmedLine === '') {
                        return '<div style="margin-bottom: 8px;"></div>';
                    }
                    
                    if (trimmedLine.startsWith('•') || trimmedLine.startsWith('-')) {
                        const bulletText = trimmedLine.replace(/^[•-]\s*/, '');
                        return `
                            <div class="overview-bullet">
                                <span class="overview-bullet-point">•</span>
                                <span>${bulletText}</span>
                            </div>
                        `;
                    }
                    
                    if (trimmedLine.includes('**')) {
                        if (trimmedLine.startsWith('**') && trimmedLine.endsWith('**') && trimmedLine.length > 4) {
                            const headerText = trimmedLine.replace(/\*\*/g, '');
                            return `<h4>${headerText}</h4>`;
                        } else {
                            const parts = trimmedLine.split(/(\*\*[^*]+\*\*)/);
                            return `<p>${parts.map(part => {
                                if (part.startsWith('**') && part.endsWith('**')) {
                                    return `<strong>${part.replace(/\*\*/g, '')}</strong>`;
                                }
                                return part;
                            }).join('')}</p>`;
                        }
                    }
                    
                    if (trimmedLine.length > 0) {
                        return `<p>${trimmedLine}</p>`;
                    }
                    
                    return '';
                }).join('')}
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



// Create enhanced HTML for printing with proper styling
const createEnhancedPrintHTML = (procedure) => {
  const isPatientAssignment = procedure.patientName && procedure.performedDate;
  
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Post-Operative Care Guide - ${procedure.name}</title>
    <style>
        @page {
            size: A4;
            margin: 1in 1in 1in 1in; /* Default margins: top right bottom left */
        }
        
        @page :first {
            margin-bottom: 1.5in; /* Increased bottom margin for first page */
        }
        
        @page :nth(2) {
            margin-top: 1.5in; /* Increased top margin for second page */
        }
        
        @page :nth(n+3) {
            margin-top: 1.25in; /* Adjusted top margin for third page and beyond */
            margin-bottom: 1.25in; /* Adjusted bottom margin for third page and beyond */
        }
        
        @media print {
            * {
                -webkit-print-color-adjust: exact !important;
                color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #374151;
                background: white;
                margin: 0;
                padding: 0;
            }
            
            .container {
                max-width: none;
                width: 100%;
                background: white;
            }
            
            .header {
                background: #2563eb !important;
                color: white !important;
                padding: 20px;
                text-align: center;
                margin-bottom: 20px;
            }
            
            .header h1 {
                font-size: 24px;
                font-weight: bold;
                margin: 0 0 8px 0;
                color: white !important;
            }
            
            .header h2 {
                font-size: 18px;
                font-weight: 600;
                margin: 8px 0 0 0;
                color: white !important;
            }
            
            .header p {
                color: #bfdbfe !important;
                margin: 4px 0 0 0;
            }
            
            .section {
                margin-bottom: 20px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                overflow: hidden;
                break-inside: avoid;
            }
            
            .section-header {
                padding: 16px;
                font-size: 16px;
                font-weight: 600;
                display: flex;
                align-items: center;
            }
            
            .section-content {
                padding: 16px;
            }
            
            .aftercare {
                border-left: 4px solid #10b981 !important;
            }
            
            .aftercare .section-header {
                color: #059669;
            }
            
            .diet {
                border-left: 4px solid #f59e0b !important;
            }
            
            .diet .section-header {
                color: #d97706;
            }
            
            .warnings {
                border-left: 4px solid #ef4444 !important;
                background: #fef2f2 !important;
            }
            
            .warnings .section-header {
                color: #dc2626;
            }
            
            .timeline {
                border-left: 4px solid #8b5cf6 !important;
            }
            
            .timeline .section-header {
                color: #7c3aed;
            }
            
            .medications {
                border-left: 4px solid #3b82f6 !important;
            }
            
            .medications .section-header {
                color: #2563eb;
            }
            
            .overview {
                border-left: 4px solid #6b7280 !important;
            }
            
            .list-item {
                display: flex;
                align-items: flex-start;
                margin-bottom: 8px;
            }
            
            .badge {
                width: 20px;
                height: 20px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: 600;
                margin-right: 8px;
                margin-top: 2px;
                flex-shrink: 0;
            }
            
            .badge-green {
                background: #dcfce7 !important;
                color: #16a34a !important;
            }
            
            .badge-orange {
                background: #fef3c7 !important;
                color: #d97706 !important;
            }
            
            .badge-purple {
                background: #ede9fe !important;
                color: #7c3aed !important;
                border-radius: 12px;
                padding: 2px 8px;
            }
            
            .icon {
                margin-right: 8px;
                width: 16px;
                height: 16px;
                display: inline-block;
            }
            
            .warning-item {
                display: flex;
                align-items: flex-start;
                margin-bottom: 6px;
                color: #991b1b;
            }
            
            .warning-icon {
                color: #ef4444;
                margin-right: 8px;
                margin-top: 2px;
                flex-shrink: 0;
            }
            
            .grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 20px;
            }
            
            .footer {
                background: #f3f4f6 !important;
                padding: 16px;
                text-align: center;
                border-top: 1px solid #e5e7eb;
                margin-top: 20px;
                font-size: 12px;
                color: #6b7280;
            }
            
            @media print {
                .grid {
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                }
                
                /* Ensure section breaks work properly with new margins */
                .section {
                    break-inside: avoid;
                    page-break-inside: avoid;
                }
                
                /* Force page break before warning section if needed */
                .warnings {
                    break-before: auto;
                    page-break-before: auto;
                }
                
                /* Ensure footer doesn't break awkwardly */
                .footer {
                    break-inside: avoid;
                    page-break-inside: avoid;
                }
            }
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #374151;
            background: white;
            margin: 0;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>Post-Operative Care Guide</h1>
            ${procedure.practiceName ? `
                <div>
                    <h2>${procedure.practiceName}</h2>
                    ${procedure.practicePhone ? `<p>Phone: ${formatPhoneNumber(procedure.practicePhone)}</p>` : ''}
                </div>
            ` : ''}
        </div>
        
        <!-- Patient Info -->
        ${isPatientAssignment ? `
            <div class="section" style="background: #eff6ff; border-left: 4px solid #3b82f6;">
                <div class="section-content">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
                        <div>
                            <strong>Patient:</strong> ${procedure.patientName}
                        </div>
                        <div>
                            <strong>Procedure Date:</strong> ${new Date(procedure.performedDate).toLocaleDateString()}
                        </div>
                        ${procedure.dentistName ? `
                            <div>
                                <strong>Dentist:</strong> ${procedure.dentistName}
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        ` : ''}
        
        <!-- Title -->
        <div style="text-align: center; margin: 20px 0; padding: 16px;">
            <h2 style="font-size: 20px; font-weight: bold; margin: 0;">${procedure.name}</h2>
            ${procedure.specialtyName ? `
                <span style="background: #4b5563; color: white; padding: 4px 12px; border-radius: 16px; font-size: 12px; margin-top: 8px; display: inline-block;">
                    ${procedure.specialtyName}
                </span>
            ` : ''}
            ${procedure.duration ? `
                <p style="color: #6b7280; margin: 8px 0 0 0;">⏰ Duration: ${procedure.duration}</p>
            ` : ''}
        </div>
        
        <!-- Overview -->
        ${procedure.overview ? `
            <div class="section overview">
                <div class="section-header">
                    <span class="icon">📋</span>
                    Overview
                </div>
                <div class="section-content">
                    <div style="white-space: pre-line; line-height: 1.7;">${procedure.overview.replace(/\\n/g, '\n').replace(/\n/g, '<br>')}</div>
                </div>
            </div>
        ` : ''}
        
        <!-- Main Content Grid -->
        <div class="grid">
            <!-- Immediate Aftercare -->
            <div class="section aftercare">
                <div class="section-header">
                    <span class="icon">⚡</span>
                    Immediate Aftercare
                </div>
                <div class="section-content">
                    ${procedure.immediateAftercare?.map((instruction, index) => `
                        <div class="list-item">
                            <span class="badge badge-green">${index + 1}</span>
                            <span>${instruction}</span>
                        </div>
                    `).join('') || '<p>No specific aftercare instructions provided.</p>'}
                </div>
            </div>
            
            <!-- Diet Restrictions -->
            <div class="section diet">
                <div class="section-header">
                    <span class="icon">🍽️</span>
                    Diet Restrictions
                </div>
                <div class="section-content">
                    ${procedure.dietRestrictions?.map((restriction, index) => `
                        <div class="list-item">
                            <span class="badge badge-orange">${index + 1}</span>
                            <span>${restriction}</span>
                        </div>
                    `).join('') || '<p>No specific diet restrictions.</p>'}
                </div>
            </div>
        </div>
        
        <!-- Warning Signs -->
        <div class="section warnings">
            <div class="section-header">
                <span class="icon">⚠️</span>
                Warning Signs - Call Your Dentist
            </div>
            <div class="section-content">
                <p style="font-weight: 500; margin-bottom: 12px; color: #b91c1c;">
                    Contact your dental office immediately if you experience any of the following:
                </p>
                ${procedure.warningSignsToCallDoctor?.map((sign) => `
                    <div class="warning-item">
                        <span class="warning-icon">⚠️</span>
                        <span>${sign}</span>
                    </div>
                `).join('') || '<div class="warning-item"><span>Please contact your dentist if you have any concerns.</span></div>'}
            </div>
        </div>
        
        <!-- Bottom Grid -->
        <div class="grid">
            <!-- Recovery Timeline -->
            <div class="section timeline">
                <div class="section-header">
                    <span class="icon">📅</span>
                    Recovery Timeline
                </div>
                <div class="section-content">
                    ${procedure.recoveryTimeline?.map((timeline) => `
                        <div class="list-item">
                            <span class="badge badge-purple">Day ${timeline.day}</span>
                            <span style="font-size: 14px;">${timeline.activity}</span>
                        </div>
                    `).join('') || '<p>Standard recovery timeline applies.</p>'}
                </div>
            </div>
            
            <!-- Medications -->
            <div class="section medications">
                <div class="section-header">
                    <span class="icon">💊</span>
                    Medications
                </div>
                <div class="section-content">
                    ${procedure.medications?.map((medication) => `
                        <div class="list-item">
                            <span class="icon">💊</span>
                            <span style="font-size: 14px;">${medication}</span>
                        </div>
                    `).join('') || '<p>No specific medications prescribed.</p>'}
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
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
    </div>
</body>
</html>
  `;
};




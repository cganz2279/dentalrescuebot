// Enhanced PDF Generator that captures the actual screen content
export const generateProcedurePDF = async (procedure) => {
  try {
    console.log('🎨 Starting enhanced PDF generation...');
    
    // Find the main content area that's currently displayed
    const contentElement = document.querySelector('.max-w-4xl') || document.querySelector('main') || document.body;
    
    if (!contentElement) {
      throw new Error('Could not find content to capture');
    }
    
    // Use the browser's native print functionality for best results
    return generatePrintStylePDF(procedure);
    
  } catch (error) {
    console.error('❌ PDF generation failed:', error);
    return false;
  }
};

// Generate PDF using browser's print functionality with enhanced styling
const generatePrintStylePDF = (procedure) => {
  try {
    console.log('🖨️ Using browser print functionality...');
    
    // Create enhanced HTML content with print-specific styling
    const printContent = createEnhancedPrintHTML(procedure);
    
    // Create new window for printing
    const printWindow = window.open('', '_blank', 'width=800,height=600');
    
    if (!printWindow) {
      throw new Error('Could not open print window. Please check popup blocker settings.');
    }
    
    // Write content and setup print handling
    printWindow.document.write(printContent);
    printWindow.document.close();
    
    // Wait for content to load, then trigger print
    setTimeout(() => {
      printWindow.focus();
      
      // Add print event listeners
      printWindow.onbeforeprint = () => {
        console.log('🖨️ Print dialog opening...');
      };
      
      printWindow.onafterprint = () => {
        console.log('✅ Print completed');
        setTimeout(() => {
          if (!printWindow.closed) {
            printWindow.close();
          }
        }, 1000);
      };
      
      // Trigger print
      printWindow.print();
    }, 1000);
    
    console.log('✅ Print window opened successfully');
    return true;
    
  } catch (error) {
    console.error('❌ Print generation failed:', error);
    return false;
  }
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
                    ${procedure.practicePhone ? `<p>Phone: ${procedure.practicePhone}</p>` : ''}
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
                    <p>${procedure.overview}</p>
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
                ${procedure.practiceName || 'Dental Practice'} | 
                Post-Operative Care Guide
            </p>
            ${procedure.practicePhone ? `
                <p style="margin-top: 8px;">
                    <strong>Emergency Contact:</strong> ${procedure.practicePhone}
                </p>
            ` : ''}
        </div>
    </div>
</body>
</html>
  `;
};


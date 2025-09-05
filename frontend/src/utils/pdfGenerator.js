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

// Create optimized HTML for better PDF viewing
const createOptimizedPrintHTML = (procedure) => {
  const isPatientAssignment = procedure.patientName && procedure.performedDate;
  
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
            margin: 1in 1in 1.5in 1in;
            
            @bottom-right {
                content: "Page " counter(page);
                font-size: 10px;
                color: #6b7280;
                margin-bottom: 0.5in;
            }
        }
        
        @page :first {
            margin-bottom: 1.75in;
            
            @bottom-right {
                content: "Page " counter(page);
                font-size: 10px;
                color: #6b7280;
                margin-bottom: 0.5in;
            }
        }
        
        @page :nth(2) {
            margin-top: 1.75in;
            
            @bottom-right {
                content: "Page " counter(page);
                font-size: 10px;
                color: #6b7280;
                margin-bottom: 0.5in;
            }
        }
        
        @page :nth(n+3) {
            margin-top: 1.5in;
            margin-bottom: 1.5in;
            
            @bottom-right {
                content: "Page " counter(page);
                font-size: 10px;
                color: #6b7280;
                margin-bottom: 0.5in;
            }
        }
        
        * {
            -webkit-print-color-adjust: exact !important;
            color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #374151;
            background: white !important;
            margin: 0;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
        }
        
        .header {
            background: #2563eb !important;
            color: white !important;
            padding: 24px;
            text-align: center;
            margin-bottom: 20px;
            border-radius: 8px;
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: bold;
            margin: 0 0 8px 0;
            color: white !important;
        }
        
        .section {
            margin-bottom: 20px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
            break-inside: avoid;
            page-break-inside: avoid;
        }
        
        .section-header {
            padding: 16px;
            font-size: 18px;
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
            background: #dcfce7 !important;
            color: #059669 !important;
        }
        
        .diet {
            border-left: 4px solid #f59e0b !important;
        }
        
        .diet .section-header {
            background: #fef3c7 !important;
            color: #d97706 !important;
        }
        
        .warnings {
            border-left: 4px solid #ef4444 !important;
            background: #fef2f2 !important;
        }
        
        .warnings .section-header {
            background: #fee2e2 !important;
            color: #dc2626 !important;
        }
        
        .timeline {
            border-left: 4px solid #8b5cf6 !important;
        }
        
        .timeline .section-header {
            background: #ede9fe !important;
            color: #7c3aed !important;
        }
        
        .medications {
            border-left: 4px solid #3b82f6 !important;
        }
        
        .medications .section-header {
            background: #dbeafe !important;
            color: #2563eb !important;
        }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .list-item {
            display: flex;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        
        .badge {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
            margin-right: 12px;
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
        
        .footer {
            background: #f3f4f6 !important;
            padding: 16px;
            text-align: center;
            border-top: 1px solid #e5e7eb;
            margin-top: 20px;
            font-size: 12px;
            color: #6b7280;
        }
        
        @media screen {
            body {
                padding: 40px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>Post-Operative Care Guide</h1>
            ${procedure.practiceName ? `
                <div style="margin-top: 16px;">
                    <h2 style="font-size: 20px; font-weight: 600; margin: 0; color: white;">${procedure.practiceName}</h2>
                    ${procedure.practicePhone ? `<p style="color: #bfdbfe; margin: 4px 0 0 0;">📞 ${formatPhoneNumber(procedure.practicePhone)}</p>` : ''}
                    ${procedure.practiceAddress ? `<p style="color: #bfdbfe; margin: 4px 0 0 0;">📍 ${procedure.practiceAddress}</p>` : ''}
                    ${procedure.practiceEmail ? `<p style="color: #bfdbfe; margin: 4px 0 0 0;">📧 ${procedure.practiceEmail}</p>` : ''}
                </div>
            ` : ''}
        </div>
        
        ${procedure.patientName && procedure.performedDate ? `
            <div class="section" style="background: #eff6ff; border-left: 4px solid #3b82f6;">
                <div class="section-content">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
                        <div>
                            <strong>Patient:</strong> ${procedure.patientName}
                        </div>
                        <div>
                            <strong>Date:</strong> ${new Date(procedure.performedDate).toLocaleDateString()}
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
            <h2 style="font-size: 24px; font-weight: bold; margin: 0; color: #111827;">${procedure.name}</h2>
            ${procedure.specialtyName ? `
                <span style="background: #4b5563; color: white; padding: 4px 12px; border-radius: 16px; font-size: 14px; margin-top: 8px; display: inline-block;">
                    ${procedure.specialtyName}
                </span>
            ` : ''}
            ${procedure.duration ? `
                <p style="color: #6b7280; margin: 8px 0 0 0;">⏰ Duration: ${procedure.duration}</p>
            ` : ''}
        </div>
        
        ${procedure.overview ? `
            <div class="section">
                <div class="section-header" style="background: #f3f4f6;">
                    <span style="margin-right: 8px;">📋</span>
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
                    <span style="margin-right: 8px;">⚡</span>
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
                    <span style="margin-right: 8px;">🍽️</span>
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
                <span style="margin-right: 8px;">⚠️</span>
                Warning Signs - Call Your Dentist
            </div>
            <div class="section-content">
                <p style="font-weight: 500; margin-bottom: 12px; color: #b91c1c;">
                    Contact your dental office immediately if you experience any of the following:
                </p>
                ${procedure.warningSignsToCallDoctor?.map((sign) => `
                    <div style="display: flex; align-items: flex-start; margin-bottom: 8px;">
                        <span style="color: #ef4444; margin-right: 8px; margin-top: 4px; flex-shrink: 0;">⚠️</span>
                        <span style="color: #991b1b;">${sign}</span>
                    </div>
                `).join('') || '<div style="color: #991b1b;">Please contact your dentist if you have any concerns.</div>'}
            </div>
        </div>
        
        <!-- Bottom Grid -->
        <div class="grid">
            <!-- Recovery Timeline -->
            <div class="section timeline">
                <div class="section-header">
                    <span style="margin-right: 8px;">📅</span>
                    Recovery Timeline
                </div>
                <div class="section-content">
                    ${procedure.recoveryTimeline?.map((timeline) => `
                        <div class="list-item">
                            <span style="background: #ede9fe; color: #7c3aed; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-right: 16px; flex-shrink: 0;">
                                Day ${timeline.day}
                            </span>
                            <span style="font-size: 14px;">${timeline.activity}</span>
                        </div>
                    `).join('') || '<p>Standard recovery timeline applies.</p>'}
                </div>
            </div>
            
            <!-- Medications -->
            <div class="section medications">
                <div class="section-header">
                    <span style="margin-right: 8px;">💊</span>
                    Medications
                </div>
                <div class="section-content">
                    ${procedure.medications?.map((medication) => `
                        <div class="list-item">
                            <span style="color: #3b82f6; margin-right: 8px; margin-top: 4px; flex-shrink: 0;">💊</span>
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
                    <strong>Emergency Contact:</strong> ${procedure.emergencyContact || procedure.practicePhone}
                </p>
            ` : ''}
            ${procedure.afterHoursContact ? `
                <p style="margin-top: 4px;">
                    <strong>After Hours:</strong> ${procedure.afterHoursContact}
                </p>
            ` : ''}
            ${procedure.dentistName ? `
                <p style="margin-top: 8px;">
                    <strong>Your Doctor:</strong> ${procedure.dentistName}
                </p>
            ` : ''}
            ${procedure.generatedBy ? `
                <p style="margin-top: 4px; font-size: 10px; color: #9ca3af;">
                    Personalized for ${procedure.generatedFor} by ${procedure.generatedBy}
                </p>
            ` : ''}
        </div>
    </div>
</body>
</html>
  `;
};

// Create HTML that exactly matches screen appearance
const createWYSIWYGPrintHTML = (contentHTML, procedure) => {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${procedure.name} - Care Guide</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @page {
            size: A4;
            margin: 1in 1in 1.5in 1in; /* top right bottom left */
        }
        
        @page :first {
            margin-bottom: 1.75in; /* Extra space on first page bottom */
        }
        
        @page :nth(2) {
            margin-top: 1.75in; /* Extra space on second page top */
        }
        
        @page :nth(n+3) {
            margin-top: 1.5in;
            margin-bottom: 1.5in;
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
                background: white !important;
                margin: 0;
                padding: 0;
            }
            
            /* Preserve all background colors */
            .bg-blue-600, .bg-blue-500 {
                background-color: #2563eb !important;
                color: white !important;
            }
            
            .bg-green-100 {
                background-color: #dcfce7 !important;
            }
            
            .bg-orange-100 {
                background-color: #fed7aa !important;
            }
            
            .bg-red-50 {
                background-color: #fef2f2 !important;
            }
            
            .bg-purple-100 {
                background-color: #f3e8ff !important;
            }
            
            .bg-gray-50 {
                background-color: #f9fafb !important;
            }
            
            /* Preserve text colors */
            .text-green-600 {
                color: #16a34a !important;
            }
            
            .text-orange-600 {
                color: #ea580c !important;
            }
            
            .text-red-600 {
                color: #dc2626 !important;
            }
            
            .text-purple-600 {
                color: #9333ea !important;
            }
            
            .text-blue-600 {
                color: #2563eb !important;
            }
            
            /* Preserve borders */
            .border-l-4 {
                border-left-width: 4px !important;
            }
            
            .border-l-green-500 {
                border-left-color: #22c55e !important;
            }
            
            .border-l-orange-500 {
                border-left-color: #f97316 !important;
            }
            
            .border-l-red-500 {
                border-left-color: #ef4444 !important;
            }
            
            .border-l-purple-500 {
                border-left-color: #a855f7 !important;
            }
            
            .border-l-blue-500 {
                border-left-color: #3b82f6 !important;
            }
            
            /* Page break controls */
            .break-inside-avoid {
                break-inside: avoid;
                page-break-inside: avoid;
            }
            
            .break-before-auto {
                break-before: auto;
                page-break-before: auto;
            }
        }
        
        /* Screen styles that should also apply to print */
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #374151;
            background: white;
        }
    </style>
</head>
<body>
    <div class="min-h-screen bg-white">
        ${contentHTML}
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
                    <strong>Emergency Contact:</strong> ${procedure.emergencyContact || procedure.practicePhone}
                </p>
            ` : ''}
            ${procedure.afterHoursContact ? `
                <p style="margin-top: 4px;">
                    <strong>After Hours:</strong> ${procedure.afterHoursContact}
                </p>
            ` : ''}
            ${procedure.dentistName ? `
                <p style="margin-top: 8px;">
                    <strong>Your Doctor:</strong> ${procedure.dentistName}
                </p>
            ` : ''}
            ${procedure.generatedBy ? `
                <p style="margin-top: 4px; font-size: 10px; color: #9ca3af;">
                    Personalized for ${procedure.generatedFor} by ${procedure.generatedBy}
                </p>
            ` : ''}
        </div>
    </div>
</body>
</html>
  `;
};

// Fallback content creation if screen content can't be captured
const createEnhancedContentHTML = (procedure) => {
  const isPatientAssignment = procedure.patientName && procedure.performedDate;
  
  return `
    <div class="max-w-4xl mx-auto bg-white shadow-lg rounded-lg overflow-hidden">
      <!-- Header -->
      <div class="bg-blue-600 text-white p-8 text-center">
        <h1 class="text-3xl font-bold mb-2">Post-Operative Care Guide</h1>
        ${procedure.practiceName ? `
          <div class="mt-4">
            <h2 class="text-xl font-semibold">${procedure.practiceName}</h2>
            ${procedure.practicePhone ? `<p class="text-blue-100 mt-1">Phone: ${procedure.practicePhone}</p>` : ''}
          </div>
        ` : ''}
      </div>
      
      <!-- Patient Info -->
      ${isPatientAssignment ? `
        <div class="bg-blue-50 border-l-4 border-l-blue-500 p-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span class="font-semibold text-blue-800">Patient:</span>
              <span class="ml-2 text-blue-700">${procedure.patientName}</span>
            </div>
            <div>
              <span class="font-semibold text-blue-800">Date:</span>
              <span class="ml-2 text-blue-700">${new Date(procedure.performedDate).toLocaleDateString()}</span>
            </div>
            ${procedure.dentistName ? `
              <div>
                <span class="font-semibold text-blue-800">Dentist:</span>
                <span class="ml-2 text-blue-700">${procedure.dentistName}</span>
              </div>
            ` : ''}
          </div>
        </div>
      ` : ''}
      
      <!-- Procedure Title -->
      <div class="bg-gray-50 p-6 border-b">
        <div class="flex items-center justify-between">
          <h2 class="text-2xl font-bold text-gray-900">${procedure.name}</h2>
          ${procedure.specialtyName ? `
            <span class="bg-gray-600 text-white px-3 py-1 rounded-full text-sm font-medium">
              ${procedure.specialtyName}
            </span>
          ` : ''}
        </div>
        ${procedure.duration ? `
          <div class="flex items-center mt-2 text-gray-600">
            <span>⏰ Duration: ${procedure.duration}</span>
          </div>
        ` : ''}
      </div>
      
      <!-- Overview -->
      ${procedure.overview ? `
        <div class="p-6 border-b">
          <h3 class="text-lg font-semibold mb-3 text-gray-900">Overview</h3>
          <div class="text-gray-700 leading-relaxed" style="white-space: pre-line; line-height: 1.7;">${procedure.overview.replace(/\\n/g, '\n').replace(/\n/g, '<br>')}</div>
        </div>
      ` : ''}
      
      <div class="p-6">
        <!-- Main Content Grid -->
        <div class="grid gap-8 lg:grid-cols-2">
          <!-- Immediate Aftercare -->
          <div class="bg-white border border-gray-200 border-l-4 border-l-green-500 rounded-lg shadow-sm break-inside-avoid">
            <div class="p-6">
              <h3 class="text-lg font-semibold flex items-center text-green-600 mb-4">
                <span class="mr-2">⚡</span>
                Immediate Aftercare
              </h3>
              <ul class="space-y-3">
                ${procedure.immediateAftercare?.map((instruction, index) => `
                  <li class="flex items-start">
                    <div class="w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-semibold mr-3 mt-0.5 flex-shrink-0">
                      ${index + 1}
                    </div>
                    <span class="text-gray-700">${instruction}</span>
                  </li>
                `).join('') || '<li class="text-gray-500">No specific aftercare instructions provided.</li>'}
              </ul>
            </div>
          </div>
          
          <!-- Diet Restrictions -->
          <div class="bg-white border border-gray-200 border-l-4 border-l-orange-500 rounded-lg shadow-sm break-inside-avoid">
            <div class="p-6">
              <h3 class="text-lg font-semibold flex items-center text-orange-600 mb-4">
                <span class="mr-2">🍽️</span>
                Diet Restrictions
              </h3>
              <ul class="space-y-3">
                ${procedure.dietRestrictions?.map((restriction, index) => `
                  <li class="flex items-start">
                    <div class="w-6 h-6 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center text-sm font-semibold mr-3 mt-0.5 flex-shrink-0">
                      ${index + 1}
                    </div>
                    <span class="text-gray-700">${restriction}</span>
                  </li>
                `).join('') || '<li class="text-gray-500">No specific diet restrictions.</li>'}
              </ul>
            </div>
          </div>
        </div>
        
        <!-- Warning Signs -->
        <div class="bg-red-50 border border-red-200 border-l-4 border-l-red-500 rounded-lg shadow-sm mt-8 break-inside-avoid">
          <div class="p-6">
            <h3 class="text-lg font-semibold flex items-center text-red-600 mb-4">
              <span class="mr-2">⚠️</span>
              Warning Signs - Call Your Dentist
            </h3>
            <p class="text-red-700 mb-4 font-medium">
              Contact your dental office immediately if you experience:
            </p>
            <ul class="space-y-2">
              ${procedure.warningSignsToCallDoctor?.map((sign) => `
                <li class="flex items-start">
                  <span class="text-red-500 mr-2 mt-1 flex-shrink-0">⚠️</span>
                  <span class="text-red-800">${sign}</span>
                </li>
              `).join('') || '<li class="text-red-800">Contact your dentist with any concerns.</li>'}
            </ul>
          </div>
        </div>
        
        <!-- Bottom Grid -->
        <div class="grid gap-8 lg:grid-cols-2 mt-8">
          <!-- Recovery Timeline -->
          <div class="bg-white border border-gray-200 border-l-4 border-l-purple-500 rounded-lg shadow-sm break-inside-avoid">
            <div class="p-6">
              <h3 class="text-lg font-semibold flex items-center text-purple-600 mb-4">
                <span class="mr-2">📅</span>
                Recovery Timeline
              </h3>
              <div class="space-y-4">
                ${procedure.recoveryTimeline?.map((timeline) => `
                  <div class="flex items-start">
                    <div class="bg-purple-100 text-purple-600 px-3 py-1 rounded-full text-sm font-semibold mr-4 flex-shrink-0">
                      Day ${timeline.day}
                    </div>
                    <p class="text-gray-700 text-sm mt-0.5">${timeline.activity}</p>
                  </div>
                `).join('') || '<p class="text-gray-500">Standard recovery applies.</p>'}
              </div>
            </div>
          </div>
          
          <!-- Medications -->
          <div class="bg-white border border-gray-200 border-l-4 border-l-blue-500 rounded-lg shadow-sm break-inside-avoid">
            <div class="p-6">
              <h3 class="text-lg font-semibold flex items-center text-blue-600 mb-4">
                <span class="mr-2">💊</span>
                Medications
              </h3>
              <ul class="space-y-3">
                ${procedure.medications?.map((medication) => `
                  <li class="flex items-start">
                    <span class="text-blue-500 mr-2 mt-1 flex-shrink-0">💊</span>
                    <span class="text-gray-700 text-sm">${medication}</span>
                  </li>
                `).join('') || '<li class="text-gray-500">No specific medications prescribed.</li>'}
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Footer -->
      <div class="bg-gray-100 p-6 text-center border-t">
        <p class="text-gray-600 text-sm">
          Generated ${new Date().toLocaleDateString()} | 
          ${procedure.practiceName || 'Your Dental Practice'} | 
          Post-Operative Care Guide
        </p>
        ${procedure.emergencyContact || procedure.practicePhone ? `
          <p class="text-gray-600 text-sm mt-2">
            <strong>Emergency Contact:</strong> ${procedure.emergencyContact || procedure.practicePhone}
          </p>
        ` : ''}
        ${procedure.afterHoursContact ? `
          <p class="text-gray-600 text-sm mt-1">
            <strong>After Hours:</strong> ${procedure.afterHoursContact}
          </p>
        ` : ''}
        ${procedure.dentistName ? `
          <p class="text-gray-600 text-sm mt-2">
            <strong>Your Doctor:</strong> ${procedure.dentistName}
          </p>
        ` : ''}
        ${procedure.generatedBy ? `
          <p class="text-gray-500 text-xs mt-1">
            Personalized for ${procedure.generatedFor} by ${procedure.generatedBy}
          </p>
        ` : ''}
      </div>
    </div>
  `;
};


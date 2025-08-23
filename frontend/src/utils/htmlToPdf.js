// Shared HTML-to-PDF generator that creates PDFs identical to the View page
export const generateViewPagePDF = async (procedure, practice = null) => {
  try {
    // Import html2canvas and jsPDF for HTML-to-PDF conversion
    const html2canvas = (await import('html2canvas')).default;
    const { jsPDF } = await import('jspdf');
    
    // Create a printable version of the current page
    const printElement = document.createElement('div');
    printElement.innerHTML = `
      <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; padding: 20px; background: white; max-width: 800px; margin: 0 auto; page-break-inside: avoid;">
        <!-- Header -->
        <div style="text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #000; page-break-after: avoid;">
          <h1 style="font-size: 24px; font-weight: bold; margin: 0 0 10px 0; color: #000;">POST-OPERATIVE CARE INSTRUCTIONS</h1>
          ${practice?.name ? `<h2 style="font-size: 16px; font-weight: bold; margin: 5px 0; color: #000;">${practice.name}</h2>` : ''}
          ${practice?.phone ? `<p style="font-size: 12px; margin: 5px 0; color: #666;">Phone: ${practice.phone}</p>` : ''}
        </div>

        <!-- Procedure Information -->
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 20px; page-break-inside: avoid;">
          <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 15px 0; color: #000;">PROCEDURE INFORMATION</h3>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div>
              <p style="font-size: 12px; font-weight: 500; color: #6b7280; margin: 0 0 5px 0;">Procedure Name</p>
              <p style="font-size: 16px; font-weight: bold; margin: 0; color: #000;">${procedure.procedureName || procedure.name}</p>
            </div>
            <div>
              <p style="font-size: 12px; font-weight: 500; color: #6b7280; margin: 0 0 5px 0;">Performing Dentist</p>
              <p style="font-size: 16px; margin: 0; color: #000;">Dr. ${procedure.dentistName || 'Your Dentist'}</p>
            </div>
            <div>
              <p style="font-size: 12px; font-weight: 500; color: #6b7280; margin: 0 0 5px 0;">Performed Date</p>
              <p style="font-size: 16px; margin: 0; color: #000;">${procedure.performedDate ? new Date(procedure.performedDate).toLocaleDateString() : new Date().toLocaleDateString()}</p>
            </div>
            <div>
              <p style="font-size: 12px; font-weight: 500; color: #6b7280; margin: 0 0 5px 0;">Status</p>
              <span style="background: #f0fdf4; color: #166534; padding: 4px 8px; border-radius: 4px; font-size: 12px; border: 1px solid #bbf7d0;">${procedure.status || 'active'}</span>
            </div>
          </div>
        </div>

        ${procedure.practiceNotes && procedure.practiceNotes.trim() ? `
        <!-- Practice Notes -->
        <div style="background: #f3e8ff; border: 1px solid #d8b4fe; border-radius: 8px; padding: 20px; margin-bottom: 20px; page-break-inside: avoid;">
          <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 15px 0; color: #7c3aed;">👤 Practice Notes</h3>
          <div style="background: #faf5ff; padding: 15px; border-radius: 6px;">
            <p style="color: #6b21a8; margin: 0; white-space: pre-wrap;">${procedure.practiceNotes}</p>
          </div>
        </div>
        ` : ''}

        ${procedure.customInstructions && procedure.customInstructions.length > 0 ? `
        <!-- Custom Instructions -->
        <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 20px; margin-bottom: 20px; page-break-inside: avoid;">
          <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 15px 0; color: #2563eb;">📋 Custom Post-Operative Instructions</h3>
          <div style="background: #dbeafe; padding: 15px; border-radius: 6px;">
            <ul style="margin: 0; padding-left: 0; list-style: none;">
              ${procedure.customInstructions.map(instruction => `
                <li style="margin-bottom: 8px; color: #1e40af;">
                  <span style="font-weight: bold; color: #2563eb;">•</span> ${instruction}
                </li>
              `).join('')}
            </ul>
          </div>
        </div>
        ` : ''}

        <!-- Detailed Post-Operative Care Instructions -->
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin-bottom: 20px; page-break-inside: avoid;">
          <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 20px 0; color: #16a34a; page-break-after: avoid;">📄 Detailed Post-Operative Care Instructions</h3>
          
          <!-- Immediate Aftercare -->
          <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin-bottom: 15px; border-radius: 6px; page-break-inside: avoid;">
            <h4 style="font-size: 14px; font-weight: bold; margin: 0 0 10px 0; color: #dc2626; page-break-after: avoid;">🕐 IMMEDIATE AFTERCARE (First 24 Hours)</h4>
            <ul style="margin: 0; padding-left: 0; list-style: none;">
              <li style="margin-bottom: 6px; color: #991b1b;"><span style="font-weight: bold; color: #dc2626;">•</span> Apply ice to the treated area for 15 minutes every hour for the first 24 hours to reduce swelling</li>
              <li style="margin-bottom: 6px; color: #991b1b;"><span style="font-weight: bold; color: #dc2626;">•</span> Keep gauze in place for 30-60 minutes after treatment, then remove gently</li>
              <li style="margin-bottom: 6px; color: #991b1b;"><span style="font-weight: bold; color: #dc2626;">•</span> Do not rinse or spit forcefully for the first 24 hours</li>
              <li style="margin-bottom: 6px; color: #991b1b;"><span style="font-weight: bold; color: #dc2626;">•</span> Take prescribed medications as directed by your dentist</li>
            </ul>
          </div>

          <!-- Diet Instructions -->
          <div style="background: #fff7ed; border-left: 4px solid #f97316; padding: 15px; margin-bottom: 15px; border-radius: 6px; page-break-inside: avoid;">
            <h4 style="font-size: 14px; font-weight: bold; margin: 0 0 10px 0; color: #ea580c; page-break-after: avoid;">🍽️ DIET AND EATING INSTRUCTIONS</h4>
            <ul style="margin: 0; padding-left: 0; list-style: none;">
              <li style="margin-bottom: 6px; color: #9a3412;"><span style="font-weight: bold; color: #ea580c;">•</span> Stick to soft foods for the first 24-48 hours (yogurt, soup, mashed potatoes)</li>
              <li style="margin-bottom: 6px; color: #9a3412;"><span style="font-weight: bold; color: #ea580c;">•</span> Avoid hot liquids and foods until numbness wears off</li>
              <li style="margin-bottom: 6px; color: #9a3412;"><span style="font-weight: bold; color: #ea580c;">•</span> No alcohol while taking prescribed medications</li>
              <li style="margin-bottom: 6px; color: #9a3412;"><span style="font-weight: bold; color: #ea580c;">•</span> Avoid using straws for the first few days to prevent dry socket</li>
            </ul>
          </div>

          <!-- Medications -->
          <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 15px; margin-bottom: 15px; border-radius: 6px; page-break-inside: avoid;">
            <h4 style="font-size: 14px; font-weight: bold; margin: 0 0 10px 0; color: #2563eb; page-break-after: avoid;">💊 MEDICATION GUIDELINES</h4>
            <ul style="margin: 0; padding-left: 0; list-style: none;">
              <li style="margin-bottom: 6px; color: #1e3a8a;"><span style="font-weight: bold; color: #2563eb;">•</span> Take all prescribed medications exactly as directed</li>
              <li style="margin-bottom: 6px; color: #1e3a8a;"><span style="font-weight: bold; color: #2563eb;">•</span> Complete the full course of antibiotics if prescribed</li>
              <li style="margin-bottom: 6px; color: #1e3a8a;"><span style="font-weight: bold; color: #2563eb;">•</span> Use over-the-counter pain relief as recommended (ibuprofen, acetaminophen)</li>
              <li style="margin-bottom: 6px; color: #1e3a8a;"><span style="font-weight: bold; color: #2563eb;">•</span> Do not exceed recommended dosages of any medication</li>
            </ul>
          </div>

          <!-- Warning Signs -->
          <div style="background: #fef2f2; border: 2px solid #ef4444; padding: 15px; margin-bottom: 15px; border-radius: 6px; page-break-inside: avoid;">
            <h4 style="font-size: 14px; font-weight: bold; margin: 0 0 10px 0; color: #dc2626; page-break-after: avoid;">⚠️ WHEN TO CONTACT YOUR DENTIST IMMEDIATELY</h4>
            <ul style="margin: 0; padding-left: 0; list-style: none;">
              <li style="margin-bottom: 6px; color: #7f1d1d;"><span style="font-weight: bold; color: #dc2626;">•</span> Severe or worsening pain after 48 hours</li>
              <li style="margin-bottom: 6px; color: #7f1d1d;"><span style="font-weight: bold; color: #dc2626;">•</span> Excessive bleeding that does not stop with gentle pressure</li>
              <li style="margin-bottom: 6px; color: #7f1d1d;"><span style="font-weight: bold; color: #dc2626;">•</span> Signs of infection: fever, excessive swelling, pus, or foul taste</li>
              <li style="margin-bottom: 6px; color: #7f1d1d;"><span style="font-weight: bold; color: #dc2626;">•</span> Numbness that persists beyond the expected timeframe</li>
              <li style="margin-bottom: 6px; color: #7f1d1d;"><span style="font-weight: bold; color: #dc2626;">•</span> Difficulty swallowing or breathing</li>
            </ul>
          </div>
        </div>

        <!-- General Post-Operative Care -->
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin-bottom: 20px; page-break-inside: avoid;">
          <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 15px 0; color: #16a34a; page-break-after: avoid;">📋 General Post-Operative Care</h3>
          <div style="background: #dcfce7; padding: 15px; border-radius: 6px;">
            <ul style="margin: 0; padding-left: 0; list-style: none;">
              <li style="margin-bottom: 8px; color: #166534;"><span style="font-weight: bold; color: #16a34a;">•</span> Follow all post-operative care instructions carefully</li>
              <li style="margin-bottom: 8px; color: #166534;"><span style="font-weight: bold; color: #16a34a;">•</span> Take prescribed medications as directed</li>
              <li style="margin-bottom: 8px; color: #166534;"><span style="font-weight: bold; color: #16a34a;">•</span> Contact office if you experience any complications</li>
              <li style="margin-bottom: 8px; color: #166534;"><span style="font-weight: bold; color: #16a34a;">•</span> Attend follow-up appointments as scheduled</li>
            </ul>
          </div>
        </div>

        <!-- Contact Information -->
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 30px; page-break-inside: avoid;">
          <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 15px 0; color: #374151; page-break-after: avoid;">📞 Contact Information</h3>
          <div style="background: #f3f4f6; padding: 15px; border-radius: 6px;">
            <p style="color: #374151; margin: 0;">For questions or concerns about this procedure, please contact your dental office during regular business hours or follow the emergency contact instructions provided.</p>
          </div>
        </div>

        <!-- Patient Acknowledgment - SINGLE INSTANCE -->
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 20px; page-break-inside: avoid;">
          <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 15px 0; color: #000; page-break-after: avoid;">PATIENT ACKNOWLEDGMENT</h3>
          <p style="margin: 0 0 30px 0; color: #374151; page-break-after: avoid;">I acknowledge that I have received and understand these post-operative care instructions. I will follow these instructions carefully and contact my dental office if I have any questions or concerns.</p>
          
          <div style="display: flex; justify-content: space-between; margin-top: 30px;">
            <div style="width: 45%;">
              <div style="border-bottom: 2px solid #000; height: 2px; margin-bottom: 8px;"></div>
              <p style="font-size: 12px; margin: 0; color: #666; font-weight: bold;">Patient Signature</p>
            </div>
            <div style="width: 30%;">
              <div style="border-bottom: 2px solid #000; height: 2px; margin-bottom: 8px;"></div>
              <p style="font-size: 12px; margin: 0; color: #666; font-weight: bold;">Date</p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div style="text-align: center; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 10px; color: #666; page-break-inside: avoid;">
          <p style="margin: 0 0 5px 0;">DISCLAIMER: This information is for educational purposes only and does not replace professional medical advice.</p>
          <p style="margin: 0 0 5px 0;">Always consult your dentist or physician for specific medical concerns.</p>
          <p style="margin: 0;">Generated on: ${new Date().toLocaleDateString()} | DentalRescueBot - www.theoncallbot.com</p>
        </div>
      </div>
    `;
    
    // Append to body temporarily
    printElement.style.position = 'absolute';
    printElement.style.left = '-9999px';
    printElement.style.top = '-9999px';
    printElement.style.width = '800px';
    document.body.appendChild(printElement);
    
    // Convert HTML to canvas with better quality and page break handling
    const canvas = await html2canvas(printElement, {
      scale: 2,
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#ffffff',
      width: 800,
      height: printElement.offsetHeight,
      scrollX: 0,
      scrollY: 0,
      windowWidth: 800,
      windowHeight: printElement.offsetHeight
    });
    
    // Remove temporary element
    document.body.removeChild(printElement);
    
    // Create PDF with proper margins and page numbering
    const pdf = new jsPDF('p', 'mm', 'a4');
    const imgData = canvas.toDataURL('image/png', 1.0);
    
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();
    const topMargin = 20; // 20mm top margin
    const bottomMargin = 25; // 25mm bottom margin (extra space for page numbers)
    const sideMargin = 15; // 15mm side margins
    const imgWidth = pdfWidth - (sideMargin * 2);
    const availableHeight = pdfHeight - topMargin - bottomMargin;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    
    let heightLeft = imgHeight;
    let position = topMargin;
    let pageNumber = 1;
    
    // Add first page with proper margins
    pdf.addImage(imgData, 'PNG', sideMargin, position, imgWidth, imgHeight, undefined, 'FAST');
    
    // Add page number to first page
    pdf.setFontSize(10);
    pdf.setTextColor(100, 100, 100);
    pdf.text(`Page ${pageNumber}`, pdfWidth - 25, pdfHeight - 10, { align: 'right' });
    
    heightLeft -= availableHeight;
    
    // Add additional pages if needed with proper margins and page numbers
    while (heightLeft >= 0) {
      position = heightLeft - imgHeight + topMargin;
      pdf.addPage();
      pageNumber++;
      
      pdf.addImage(imgData, 'PNG', sideMargin, position, imgWidth, imgHeight, undefined, 'FAST');
      
      // Add page number to each additional page
      pdf.setFontSize(10);
      pdf.setTextColor(100, 100, 100);
      pdf.text(`Page ${pageNumber}`, pdfWidth - 25, pdfHeight - 10, { align: 'right' });
      
      heightLeft -= availableHeight;
    }
    
    // Save the PDF
    const fileName = `${(procedure.procedureName || procedure.name).replace(/[^a-z0-9]/gi, '_').toLowerCase()}_post_op_instructions.pdf`;
    pdf.save(fileName);
    
    return true;
  } catch (error) {
    console.error('Error generating PDF:', error);
    return false;
  }
};
// Shared HTML-to-PDF generator that creates PDFs - UPDATED VERSION
export const generateViewPagePDF = async (procedure, practice = null) => {
  try {
    console.log('PDF Generator: Starting PDF generation for', procedure.procedureName);
    
    // Import html2canvas and jsPDF for HTML-to-PDF conversion
    const html2canvas = (await import('html2canvas')).default;
    const { jsPDF } = await import('jspdf');
    
    // Try to find the main content area from procedure view page first
    let mainContent = document.querySelector('.max-w-4xl.mx-auto.py-8');
    
    // If not found, we're probably on dashboard - create minimal content from procedure data
    if (!mainContent) {
      console.log('PDF Generator: Main content area not found - generating from procedure data instead');
      // Create a minimal procedure content structure for dashboard context
      const contentElement = document.createElement('div');
      contentElement.innerHTML = `
        <div class="space-y-6">
          <div class="border-l-4 border-l-blue-500 bg-white p-6 rounded-lg shadow">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">${procedure.procedureName}</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 class="text-sm font-medium text-gray-500 mb-2">Performing Dentist</h3>
                <p class="text-lg">Dr. ${procedure.dentistName}</p>
              </div>
              <div>
                <h3 class="text-sm font-medium text-gray-500 mb-2">Performed Date</h3>
                <p class="text-lg">${new Date(procedure.performedDate).toLocaleDateString()}</p>
              </div>
            </div>
          </div>
          
          ${procedure.practiceNotes ? `
          <div class="bg-purple-50 p-6 rounded-lg">
            <h3 class="text-lg font-semibold text-purple-800 mb-3">Practice Notes</h3>
            <p class="text-purple-800 whitespace-pre-wrap">${procedure.practiceNotes}</p>
          </div>
          ` : ''}
          
          ${procedure.customInstructions && procedure.customInstructions.length > 0 ? `
          <div class="bg-blue-50 p-6 rounded-lg">
            <h3 class="text-lg font-semibold text-blue-800 mb-3">Custom Instructions</h3>
            <ul class="space-y-2">
              ${procedure.customInstructions.map(instruction => `
                <li class="flex items-start space-x-2 text-blue-800">
                  <span class="font-bold text-blue-600">•</span>
                  <span>${instruction}</span>
                </li>
              `).join('')}
            </ul>
          </div>
          ` : ''}
          
          <div class="bg-green-50 border-l-4 border-green-500 p-6 rounded-lg">
            <h3 class="text-lg font-semibold text-green-800 mb-3">Standard Post-Operative Care Instructions</h3>
            <div class="space-y-4 text-green-800">
              <div>
                <h4 class="font-semibold mb-2 flex items-center">
                  <span class="text-red-600 mr-2">🩺</span>
                  Immediate Aftercare (First 24 Hours)
                </h4>
                <ul class="space-y-1 ml-4">
                  <li>• Apply ice to the treated area for 15 minutes every hour for the first 24 hours to reduce swelling</li>
                  <li>• Keep gauze in place for 30-60 minutes after treatment, then remove gently</li>
                  <li>• Do not rinse or spit forcefully for the first 24 hours</li>
                  <li>• Take prescribed medications as directed by your dentist</li>
                </ul>
              </div>
              
              <div>
                <h4 class="font-semibold mb-2 flex items-center">
                  <span class="text-orange-600 mr-2">🍽️</span>
                  Diet Restrictions
                </h4>
                <ul class="space-y-1 ml-4">
                  <li>• Stick to soft foods for the first 24-48 hours (yogurt, soup, mashed potatoes)</li>
                  <li>• Avoid hot liquids and foods until numbness wears off</li>
                  <li>• Avoid using straws for the first few days to prevent dry socket</li>
                  <li>• No alcohol while taking prescribed medications</li>
                </ul>
              </div>
              
              <div>
                <h4 class="font-semibold mb-2 flex items-center">
                  <span class="text-red-600 mr-2">⚠️</span>
                  Contact Your Dentist If You Experience:
                </h4>
                <ul class="space-y-1 ml-4 text-red-800">
                  <li>• Severe or worsening pain after 48 hours</li>
                  <li>• Excessive bleeding that does not stop with gentle pressure</li>
                  <li>• Signs of infection: fever, excessive swelling, pus, or foul taste</li>
                  <li>• Numbness that persists beyond the expected timeframe</li>
                  <li>• Difficulty swallowing or breathing</li>
                </ul>
              </div>
              
              <div>
                <h4 class="font-semibold mb-2 flex items-center">
                  <span class="text-blue-600 mr-2">💊</span>
                  Medication Guidelines
                </h4>
                <ul class="space-y-1 ml-4">
                  <li>• Take all prescribed medications exactly as directed</li>
                  <li>• Complete the full course of antibiotics if prescribed</li>
                  <li>• Use over-the-counter pain relief as recommended (ibuprofen, acetaminophen)</li>
                  <li>• Do not exceed recommended dosages of any medication</li>
                </ul>
              </div>
              
              <div>
                <h4 class="font-semibold mb-2 flex items-center">
                  <span class="text-green-600 mr-2">✅</span>
                  General Care Instructions
                </h4>
                <ul class="space-y-1 ml-4">
                  <li>• Follow all post-operative care instructions carefully</li>
                  <li>• Take prescribed medications as directed</li>
                  <li>• Contact office if you experience any complications</li>
                  <li>• Attend follow-up appointments as scheduled</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      `;
      mainContent = contentElement;
    }
    
    // Create a printable version of the current page content
    const printElement = document.createElement('div');
    printElement.innerHTML = `
      <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; padding: 25px 20px; background: white; max-width: 800px; margin: 0 auto; page-break-inside: avoid;">
        <!-- Header -->
        <div style="text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #000; page-break-after: avoid;">
          <h1 style="font-size: 24px; font-weight: bold; margin: 0 0 10px 0; color: #000;">POST-OPERATIVE CARE INSTRUCTIONS</h1>
          ${practice?.name ? `<h2 style="font-size: 16px; font-weight: bold; margin: 5px 0; color: #000;">${practice.name}</h2>` : ''}
          ${practice?.phone ? `<p style="font-size: 12px; margin: 5px 0; color: #666;">Phone: ${practice.phone}</p>` : ''}
        </div>

        <!-- Main content from the actual page -->
        <div id="procedure-content">
          ${mainContent.innerHTML}
        </div>

        <!-- Patient Acknowledgment Section -->
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 30px 0 20px 0; page-break-inside: avoid;">
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
    
    // Clean up any duplicate content in the captured HTML
    const contentDiv = printElement.querySelector('#procedure-content');
    if (contentDiv) {
      // Remove any existing Contact Information cards from the captured content
      // since we have our own standardized disclaimer/contact section at the bottom
      const allCards = contentDiv.querySelectorAll('[class*="Card"], [class*="card"], div');
      allCards.forEach(card => {
        const cardText = card.textContent || '';
        if (cardText.includes('Contact Information') || 
            cardText.includes('contact your dental office') ||
            cardText.includes('DISCLAIMER') || 
            cardText.includes('educational purposes') ||
            cardText.includes('professional medical advice') ||
            cardText.includes('Generated on:') ||
            cardText.includes('DentalRescueBot')) {
          card.remove();
        }
      });
      
      // Also remove any paragraph or text elements with disclaimer content
      const allPs = contentDiv.querySelectorAll('p, span, div');
      allPs.forEach(element => {
        const text = element.textContent || '';
        if ((text.includes('DISCLAIMER') && text.includes('educational')) ||
            (text.includes('Always consult your dentist') && text.includes('medical concerns')) ||
            text.includes('Generated on:') ||
            text.includes('DentalRescueBot')) {
          element.remove();
        }
      });
    }
    
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
    
    // Create PDF with proper page-by-page margins
    const pdf = new jsPDF('p', 'mm', 'a4');
    
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();
    const sideMargin = 10; // 10mm side margins
    const imgWidth = pdfWidth - (sideMargin * 2);
    
    // Different margins for different pages as requested by user
    const page1TopMargin = 15;    // 15mm top margin for page 1
    const page1BottomMargin = 30; // 30mm bottom margin for page 1 (larger as requested)
    const page2PlusTopMargin = 25; // 25mm top margin for page 2+ (larger as requested)
    const page2PlusBottomMargin = 20; // 20mm bottom margin for page 2+
    
    const page1AvailableHeight = pdfHeight - page1TopMargin - page1BottomMargin;
    const page2PlusAvailableHeight = pdfHeight - page2PlusTopMargin - page2PlusBottomMargin;
    
    // Convert canvas dimensions to PDF dimensions
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    const scaleFactor = imgWidth / canvas.width;
    
    let remainingCanvasHeight = canvas.height;
    let canvasYOffset = 0;
    let pageNumber = 1;
    
    // PAGE 1: Special margins (larger bottom margin)
    if (remainingCanvasHeight > 0) {
      const page1CanvasHeight = Math.min(remainingCanvasHeight, page1AvailableHeight / scaleFactor);
      
      // Create a cropped canvas for page 1
      const page1Canvas = document.createElement('canvas');
      page1Canvas.width = canvas.width;
      page1Canvas.height = page1CanvasHeight;
      const page1Ctx = page1Canvas.getContext('2d');
      
      page1Ctx.drawImage(
        canvas,
        0, canvasYOffset,           // Source x, y
        canvas.width, page1CanvasHeight, // Source width, height
        0, 0,                      // Dest x, y
        canvas.width, page1CanvasHeight  // Dest width, height
      );
      
      const page1ImgData = page1Canvas.toDataURL('image/png', 1.0);
      const page1ImgHeight = page1CanvasHeight * scaleFactor;
      
      pdf.addImage(
        page1ImgData, 'PNG',
        sideMargin, page1TopMargin,
        imgWidth, page1ImgHeight,
        undefined, 'FAST'
      );
      
      // Add page number to page 1
      pdf.setFontSize(10);
      pdf.setTextColor(100, 100, 100);
      pdf.text(`Page ${pageNumber}`, pdfWidth - sideMargin, pdfHeight - 8, { align: 'right' });
      
      remainingCanvasHeight -= page1CanvasHeight;
      canvasYOffset += page1CanvasHeight;
    }
    
    // PAGE 2+: Different margins (larger top margin, follow same pattern)
    while (remainingCanvasHeight > 0) {
      pdf.addPage();
      pageNumber++;
      
      const pageCanvasHeight = Math.min(remainingCanvasHeight, page2PlusAvailableHeight / scaleFactor);
      
      // Create a cropped canvas for this page
      const pageCanvas = document.createElement('canvas');
      pageCanvas.width = canvas.width;
      pageCanvas.height = pageCanvasHeight;
      const pageCtx = pageCanvas.getContext('2d');
      
      pageCtx.drawImage(
        canvas,
        0, canvasYOffset,           // Source x, y
        canvas.width, pageCanvasHeight, // Source width, height
        0, 0,                      // Dest x, y
        canvas.width, pageCanvasHeight  // Dest width, height
      );
      
      const pageImgData = pageCanvas.toDataURL('image/png', 1.0);
      const pageImgHeight = pageCanvasHeight * scaleFactor;
      
      pdf.addImage(
        pageImgData, 'PNG',
        sideMargin, page2PlusTopMargin,
        imgWidth, pageImgHeight,
        undefined, 'FAST'
      );
      
      // Add page number
      pdf.setFontSize(10);
      pdf.setTextColor(100, 100, 100);
      pdf.text(`Page ${pageNumber}`, pdfWidth - sideMargin, pdfHeight - 8, { align: 'right' });
      
      remainingCanvasHeight -= pageCanvasHeight;
      canvasYOffset += pageCanvasHeight;
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
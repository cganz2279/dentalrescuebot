// Shared HTML-to-PDF generator that creates PDFs identical to the View page
export const generateViewPagePDF = async (procedure, practice = null) => {
  try {
    // Import html2canvas and jsPDF for HTML-to-PDF conversion
    const html2canvas = (await import('html2canvas')).default;
    const { jsPDF } = await import('jspdf');
    
    // Find the main content area of the current page (excluding header/navigation)
    const mainContent = document.querySelector('.max-w-4xl.mx-auto.py-8');
    
    if (!mainContent) {
      throw new Error('Could not find main content area to print');
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
    const imgData = canvas.toDataURL('image/png', 1.0);
    
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();
    const sideMargin = 10; // 10mm side margins
    const imgWidth = pdfWidth - (sideMargin * 2);
    
    // Different margins for different pages
    const page1TopMargin = 15;    // 15mm top margin for page 1
    const page1BottomMargin = 30; // 30mm bottom margin for page 1
    const page2PlusTopMargin = 25; // 25mm top margin for page 2+
    const page2PlusBottomMargin = 20; // 20mm bottom margin for page 2+
    
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    const page1AvailableHeight = pdfHeight - page1TopMargin - page1BottomMargin;
    const page2PlusAvailableHeight = pdfHeight - page2PlusTopMargin - page2PlusBottomMargin;
    
    let remainingHeight = imgHeight;
    let contentOffset = 0; // Track how much content we've already placed
    let pageNumber = 1;
    
    // Page 1 with specific margins
    const page1ContentHeight = Math.min(remainingHeight, page1AvailableHeight);
    
    pdf.addImage(
      imgData, 'PNG',
      sideMargin, page1TopMargin,
      imgWidth, imgHeight,
      undefined, 'FAST',
      0, 0 // Start from top of image
    );
    
    // Add page number to page 1
    pdf.setFontSize(10);
    pdf.setTextColor(100, 100, 100);
    pdf.text(`Page ${pageNumber}`, pdfWidth - sideMargin, pdfHeight - 8, { align: 'right' });
    
    remainingHeight -= page1AvailableHeight;
    contentOffset += page1AvailableHeight;
    
    // Page 2+ with different margins
    while (remainingHeight > 0) {
      pdf.addPage();
      pageNumber++;
      
      // Calculate how much content fits on this page
      const pageContentHeight = Math.min(remainingHeight, page2PlusAvailableHeight);
      
      // Position the image so the continuation appears at the top of the new page
      const yOffset = -(contentOffset * imgWidth / canvas.width);
      
      pdf.addImage(
        imgData, 'PNG',
        sideMargin, page2PlusTopMargin + yOffset,
        imgWidth, imgHeight,
        undefined, 'FAST'
      );
      
      // Add page number
      pdf.setFontSize(10);
      pdf.setTextColor(100, 100, 100);
      pdf.text(`Page ${pageNumber}`, pdfWidth - sideMargin, pdfHeight - 8, { align: 'right' });
      
      remainingHeight -= page2PlusAvailableHeight;
      contentOffset += page2PlusAvailableHeight;
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
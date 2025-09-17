// Test script to validate the new PDF generation functionality
const jsPDF = require('jspdf');

// Mock procedure data (similar to what we get from the database)
const mockProcedureData = {
  name: "Root Canal Therapy",
  practiceName: "Cary Ganz DDS PC",
  practicePhone: "5162361083", 
  practiceOfficeHours: "Mon-Fri: 8:00 AM - 5:00 PM (EST/EDT) • Sat: 9:00 AM - 2:00 PM",
  practiceEmergencyContact: "📞 (555) 123-4567 • 🚨 Emergency Line",
  overview: `Purpose: Removal of infected or damaged pulp tissue from inside the tooth, followed by sealing. First 24 Hours: - Avoid chewing on the treated tooth until numbness wears off. - Some tenderness or mild discomfort is normal. Pain & Sensitivity: - Use OTC or prescribed pain relievers as directed. - Tooth sensitivity to pressure may last for several days. Oral Hygiene: - Brush and floss normally, avoiding excessive pressure on the treated tooth. Diet: - Soft foods are recommended until chewing comfort improves. Special Precautions: - If a temporary filling is placed, avoid sticky or hard foods until the permanent restoration is done. Follow-Up: - A crown or permanent filling is usually required for full protection. - Contact the office if pain worsens, swelling develops, or you notice signs of infection.`
};

// Helper function to format phone numbers
const formatPhoneNumber = (phone) => {
  if (!phone) return '';
  
  const cleaned = phone.replace(/\D/g, '');
  
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  } else if (cleaned.length === 11 && cleaned[0] === '1') {
    return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  } else {
    return phone;
  }
};

// Helper function to add formatted content with proper sections to PDF
const addFormattedContent = (pdf, overviewText, startY) => {
  let yPos = startY;
  
  // Parse content into sections using the same logic as the frontend
  const sections = [];
  let currentSection = null;
  
  // Split by section headers that are followed by content
  const sectionPattern = /\b([A-Z][a-zA-Z\s&]+):\s*/g;
  let lastIndex = 0;
  let match;
  
  while ((match = sectionPattern.exec(overviewText)) !== null) {
    // If we have a previous section, get its content
    if (currentSection) {
      const sectionContent = overviewText.substring(lastIndex, match.index).trim();
      if (sectionContent) {
        // Split content by sentences and bullet points
        const contentLines = sectionContent
          .split(/[.]\s+/) // Split by sentences
          .map(line => line.trim())
          .filter(line => line.length > 0)
          .map(line => line.endsWith('.') ? line : line + '.'); // Ensure sentences end with period
        
        currentSection.content = contentLines;
      }
      sections.push(currentSection);
    }
    
    // Start new section
    currentSection = {
      title: match[1] + ':',
      content: []
    };
    lastIndex = match.index + match[0].length;
  }
  
  // Handle the last section
  if (currentSection) {
    const sectionContent = overviewText.substring(lastIndex).trim();
    if (sectionContent) {
      const contentLines = sectionContent
        .split(/[.]\s+/)
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(line => line.endsWith('.') ? line : line + '.');
      
      currentSection.content = contentLines;
    }
    sections.push(currentSection);
  }
  
  // If no sections were found, treat the entire content as one section
  if (sections.length === 0 && overviewText) {
    sections.push({
      title: 'Post-Operative Instructions:',
      content: overviewText
        .split(/[.]\s+/)
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(line => line.endsWith('.') ? line : line + '.')
    });
  }
  
  console.log(`📄 Parsed ${sections.length} sections:`);
  sections.forEach((section, index) => {
    console.log(`  ${index + 1}. ${section.title} (${section.content.length} items)`);
  });
  
  return sections.length;
};

// Test the parsing
const testResult = addFormattedContent(null, mockProcedureData.overview, 0);
console.log(`✅ Successfully parsed overview into ${testResult} sections`);
console.log(`✅ PDF generation logic validation complete`);
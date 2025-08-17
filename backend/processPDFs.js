const fs = require('fs');
const path = require('path');
const pdf = require('pdf-parse');
const mongoose = require('mongoose');
const Specialty = require('./models/Specialty');
const Procedure = require('./models/Procedure');
require('dotenv').config();

// Specialty mapping based on procedure names and content
const specialtyMapping = {
  'endodontics': {
    keywords: ['root canal', 'apicoectomy', 'pulpotomy', 'vital pulp', 'hemisection', 'root amputation', 'root resection'],
    name: 'Endodontics',
    icon: 'Activity',
    color: 'bg-blue-50 border-blue-200'
  },
  'oral-surgery': {
    keywords: ['extraction', 'surgical', 'wisdom tooth', 'impacted', 'bone graft', 'sinus lift', 'implant', 'cysts', 'lesion removal', 'trauma', 'cancer surgery', 'orthognathic', 'tori removal', 'cleft'],
    name: 'Oral Surgery',
    icon: 'Scissors', 
    color: 'bg-red-50 border-red-200'
  },
  'prosthodontics': {
    keywords: ['crown', 'bridge', 'denture', 'veneer', 'inlay', 'onlay', 'full mouth rehabilitation', 'immediate dentures', 'reline'],
    name: 'Prosthodontics',
    icon: 'Crown',
    color: 'bg-purple-50 border-purple-200'
  },
  'periodontics': {
    keywords: ['scaling', 'root planing', 'periodontal', 'gum', 'gingivectomy', 'gingivoplasty', 'flap surgery', 'tissue graft', 'connective tissue', 'free gingival', 'crown lengthening', 'osseous', 'regenerative', 'guided tissue'],
    name: 'Periodontics',
    icon: 'Heart',
    color: 'bg-green-50 border-green-200'
  },
  'general-dentistry': {
    keywords: ['filling', 'amalgam', 'tooth colored', 'bonding', 'sealant', 'whitening', 'cleaning'],
    name: 'General Dentistry',
    icon: 'Shield',
    color: 'bg-orange-50 border-orange-200'
  },
  'orthodontics': {
    keywords: ['orthodontic', 'tad placement', 'surgical orthodontics', 'adjustment', 'appliance delivery'],
    name: 'Orthodontics',
    icon: 'Zap',
    color: 'bg-teal-50 border-teal-200'
  },
  'pedodontics': {
    keywords: ['pediatric', 'child', 'kids'],
    name: 'Pediatric Dentistry', 
    icon: 'Baby',
    color: 'bg-pink-50 border-pink-200'
  },
  'oral-medicine': {
    keywords: ['tmj', 'sleep apnea', 'nightguard', 'occlusal guard', 'oral cancer screening', 'biopsy'],
    name: 'Oral Medicine',
    icon: 'Stethoscope',
    color: 'bg-indigo-50 border-indigo-200'
  }
};

function categorizeByKeywords(procedureName, content) {
  const text = (procedureName + ' ' + content).toLowerCase();
  
  for (const [specialtyId, specialty] of Object.entries(specialtyMapping)) {
    for (const keyword of specialty.keywords) {
      if (text.includes(keyword.toLowerCase())) {
        return {
          id: specialtyId,
          name: specialty.name,
          icon: specialty.icon,
          color: specialty.color
        };
      }
    }
  }
  
  // Default to general dentistry if no match
  return {
    id: 'general-dentistry',
    name: 'General Dentistry',
    icon: 'Shield',
    color: 'bg-orange-50 border-orange-200'
  };
}

function extractStructuredData(text, filename) {
  // Clean up the text
  const cleanText = text.replace(/\s+/g, ' ').trim();
  
  // Extract procedure name from filename
  const procedureName = filename
    .replace('Post_Op_', '')
    .replace('.pdf', '')
    .replace(/_/g, ' ')
    .replace(/\s+\(\d+\)/g, '') // Remove (1), (2) etc.
    .trim();

  // Create unique ID
  const procedureId = procedureName.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-');

  // Extract sections using various patterns
  const sections = {
    overview: '',
    immediateAftercare: [],
    dietRestrictions: [],
    warningSignsToCallDoctor: [],
    recoveryTimeline: [],
    medications: []
  };

  // Try to extract overview (first meaningful paragraph)
  const overviewMatch = cleanText.match(/(?:overview|description|procedure|what to expect)[:\s]+(.*?)(?=\n\n|\.|immediate|post|care|instructions)/i);
  if (overviewMatch) {
    sections.overview = overviewMatch[1].trim();
  } else {
    // Use first 200 characters as overview
    sections.overview = cleanText.substring(0, 200).trim() + '...';
  }

  // Extract immediate aftercare instructions
  const aftercarePatterns = [
    /(?:immediate|post-?op|after\s*care|instructions)[:\s]+(.*?)(?=diet|food|eating|warning|call|contact|medication)/is,
    /(?:immediately|first|today)[:\s]+(.*?)(?=diet|food|eating|warning|call|contact)/is
  ];
  
  for (const pattern of aftercarePatterns) {
    const match = cleanText.match(pattern);
    if (match) {
      const instructions = match[1].split(/[•\n\r]/).filter(item => item.trim().length > 10);
      sections.immediateAftercare = instructions.slice(0, 6).map(item => item.trim());
      break;
    }
  }

  // Extract diet restrictions
  const dietPatterns = [
    /(?:diet|food|eating|drink)[:\s]+(.*?)(?=warning|call|contact|medication|pain)/is,
    /(?:avoid|do not eat|don't eat)[:\s]+(.*?)(?=warning|call|contact)/is
  ];
  
  for (const pattern of dietPatterns) {
    const match = cleanText.match(pattern);
    if (match) {
      const restrictions = match[1].split(/[•\n\r]/).filter(item => item.trim().length > 10);
      sections.dietRestrictions = restrictions.slice(0, 5).map(item => item.trim());
      break;
    }
  }

  // Extract warning signs
  const warningPatterns = [
    /(?:warning|call|contact|emergency|concern)[:\s]+(.*?)(?=medication|pain|recovery|follow)/is,
    /(?:signs?|symptoms?|when to call)[:\s]+(.*?)(?=medication|recovery)/is
  ];
  
  for (const pattern of warningPatterns) {
    const match = cleanText.match(pattern);
    if (match) {
      const warnings = match[1].split(/[•\n\r]/).filter(item => item.trim().length > 10);
      sections.warningSignsToCallDoctor = warnings.slice(0, 5).map(item => item.trim());
      break;
    }
  }

  // Extract medications
  const medicationPatterns = [
    /(?:medication|medicine|drug|pain|ibuprofen|acetaminophen)[:\s]+(.*?)(?=recovery|follow|appointment)/is,
    /(?:take|prescribed)[:\s]+(.*?)(?=recovery|follow)/is
  ];
  
  for (const pattern of medicationPatterns) {
    const match = cleanText.match(pattern);
    if (match) {
      const meds = match[1].split(/[•\n\r]/).filter(item => item.trim().length > 10);
      sections.medications = meds.slice(0, 4).map(item => item.trim());
      break;
    }
  }

  // Create default content if extraction failed
  if (sections.immediateAftercare.length === 0) {
    sections.immediateAftercare = [
      'Follow your dentist\'s specific post-operative instructions',
      'Take prescribed medications as directed',
      'Apply ice pack to reduce swelling if recommended',
      'Maintain gentle oral hygiene as instructed'
    ];
  }

  if (sections.dietRestrictions.length === 0) {
    sections.dietRestrictions = [
      'Avoid hard or crunchy foods for 24-48 hours',
      'Eat soft foods and liquids initially', 
      'Avoid extremely hot or cold foods/drinks',
      'No smoking or alcohol during healing period'
    ];
  }

  if (sections.warningSignsToCallDoctor.length === 0) {
    sections.warningSignsToCallDoctor = [
      'Severe pain that worsens after 2-3 days',
      'Excessive bleeding that won\'t stop',
      'Signs of infection (fever, pus, bad taste)',
      'Unusual swelling that increases after 48 hours',
      'Persistent numbness beyond expected timeframe'
    ];
  }

  if (sections.medications.length === 0) {
    sections.medications = [
      'Take prescribed pain medication as directed',
      'Use anti-inflammatory medication to reduce swelling',
      'Complete antibiotic course if prescribed'
    ];
  }

  // Create recovery timeline based on procedure type
  const timelineMap = {
    'extraction': [
      { day: '1', activity: 'Blood clot formation - avoid disturbing' },
      { day: '2-3', activity: 'Peak swelling, gradual pain reduction' },
      { day: '7', activity: 'Soft tissue healing progresses' },
      { day: '14-21', activity: 'Complete initial healing' }
    ],
    'surgical': [
      { day: '1-3', activity: 'Initial healing and swelling reduction' },
      { day: '7-10', activity: 'Suture removal if placed' },
      { day: '2-4 weeks', activity: 'Soft tissue healing' },
      { day: '6-8 weeks', activity: 'Complete healing expected' }
    ],
    'implant': [
      { day: '1-7', activity: 'Initial healing phase' },
      { day: '2-6 weeks', activity: 'Soft tissue integration' },
      { day: '3-6 months', activity: 'Osseointegration process' },
      { day: '6+ months', activity: 'Ready for final restoration' }
    ],
    'default': [
      { day: '1-2', activity: 'Initial healing and adjustment' },
      { day: '3-7', activity: 'Gradual improvement in comfort' },
      { day: '1-2 weeks', activity: 'Most symptoms should resolve' },
      { day: '2+ weeks', activity: 'Complete healing expected' }
    ]
  };

  let timelineType = 'default';
  if (procedureName.toLowerCase().includes('extraction')) timelineType = 'extraction';
  else if (procedureName.toLowerCase().includes('surgical') || procedureName.toLowerCase().includes('implant')) timelineType = 'surgical';
  else if (procedureName.toLowerCase().includes('implant')) timelineType = 'implant';

  sections.recoveryTimeline = timelineMap[timelineType];

  // Estimate duration based on procedure type
  let duration = '3-7 days recovery';
  if (procedureName.toLowerCase().includes('implant')) duration = '3-6 months healing';
  else if (procedureName.toLowerCase().includes('surgical')) duration = '7-14 days recovery';
  else if (procedureName.toLowerCase().includes('extraction')) duration = '5-10 days recovery';
  else if (procedureName.toLowerCase().includes('root canal')) duration = '7-14 days recovery';

  return {
    id: procedureId,
    name: procedureName,
    duration: duration,
    ...sections
  };
}

async function processPDFs() {
  try {
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGO_URL);
    console.log('Connected to MongoDB');

    const pdfDir = '/app/pdf-source';
    const pdfFiles = fs.readdirSync(pdfDir).filter(file => file.endsWith('.pdf'));
    
    console.log(`Found ${pdfFiles.length} PDF files to process`);

    // Process each PDF
    for (let i = 0; i < pdfFiles.length; i++) {
      const filename = pdfFiles[i];
      const filePath = path.join(pdfDir, filename);
      
      console.log(`Processing ${i + 1}/${pdfFiles.length}: ${filename}`);
      
      try {
        // Read and parse PDF
        const dataBuffer = fs.readFileSync(filePath);
        const data = await pdf(dataBuffer);
        const text = data.text;

        // Extract structured data
        const procedureData = extractStructuredData(text, filename);
        
        // Categorize into specialty
        const specialty = categorizeByKeywords(procedureData.name, text);
        
        // Add specialty information
        procedureData.specialty = specialty.id;
        procedureData.specialtyName = specialty.name;

        // Ensure specialty exists in database
        await Specialty.findOneAndUpdate(
          { id: specialty.id },
          {
            id: specialty.id,
            name: specialty.name,
            description: `${specialty.name} procedures and treatments`,
            icon: specialty.icon,
            color: specialty.color
          },
          { upsert: true, new: true }
        );

        // Save procedure to database
        await Procedure.findOneAndUpdate(
          { id: procedureData.id },
          procedureData,
          { upsert: true, new: true }
        );

        console.log(`✅ Processed: ${procedureData.name} -> ${specialty.name}`);

      } catch (error) {
        console.error(`❌ Error processing ${filename}:`, error.message);
      }
    }

    console.log('\n🎉 PDF processing complete!');
    
    // Get final counts
    const specialtyCount = await Specialty.countDocuments();
    const procedureCount = await Procedure.countDocuments();
    
    console.log(`📊 Final Database Stats:`);
    console.log(`   Specialties: ${specialtyCount}`);
    console.log(`   Procedures: ${procedureCount}`);

    process.exit(0);

  } catch (error) {
    console.error('❌ Error processing PDFs:', error);
    process.exit(1);
  }
}

processPDFs();
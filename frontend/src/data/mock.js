export const dentalSpecialties = [
  {
    id: 'endodontics',
    name: 'Endodontics',
    description: 'Root canal treatments and related procedures',
    icon: 'Activity',
    color: 'bg-blue-50 border-blue-200',
    procedures: [
      {
        id: 'root-canal',
        name: 'Root Canal Treatment',
        duration: '7-14 days recovery',
        specialty: 'endodontics'
      },
      {
        id: 'apicoectomy',
        name: 'Apicoectomy',
        duration: '10-14 days recovery',
        specialty: 'endodontics'
      }
    ]
  },
  {
    id: 'oral-surgery',
    name: 'Oral Surgery',
    description: 'Tooth extractions, implants, and surgical procedures',
    icon: 'Scissors',
    color: 'bg-red-50 border-red-200',
    procedures: [
      {
        id: 'tooth-extraction',
        name: 'Tooth Extraction',
        duration: '3-7 days recovery',
        specialty: 'oral-surgery'
      },
      {
        id: 'wisdom-teeth',
        name: 'Wisdom Teeth Removal',
        duration: '7-10 days recovery',
        specialty: 'oral-surgery'
      },
      {
        id: 'dental-implant',
        name: 'Dental Implant Placement',
        duration: '3-6 months healing',
        specialty: 'oral-surgery'
      }
    ]
  },
  {
    id: 'prosthodontics',
    name: 'Prosthodontics',
    description: 'Crowns, bridges, and denture procedures',
    icon: 'Crown',
    color: 'bg-purple-50 border-purple-200',
    procedures: [
      {
        id: 'dental-crown',
        name: 'Dental Crown',
        duration: '2-3 days sensitivity',
        specialty: 'prosthodontics'
      },
      {
        id: 'dental-bridge',
        name: 'Dental Bridge',
        duration: '3-5 days adjustment',
        specialty: 'prosthodontics'
      },
      {
        id: 'dentures',
        name: 'Complete/Partial Dentures',
        duration: '2-4 weeks adjustment',
        specialty: 'prosthodontics'
      }
    ]
  },
  {
    id: 'periodontics',
    name: 'Periodontics',
    description: 'Gum treatments and periodontal surgery',
    icon: 'Heart',
    color: 'bg-green-50 border-green-200',
    procedures: [
      {
        id: 'scaling-planing',
        name: 'Scaling & Root Planing',
        duration: '1-3 days sensitivity',
        specialty: 'periodontics'
      },
      {
        id: 'gum-graft',
        name: 'Gum Graft Surgery',
        duration: '7-14 days recovery',
        specialty: 'periodontics'
      },
      {
        id: 'crown-lengthening',
        name: 'Crown Lengthening',
        duration: '7-10 days recovery',
        specialty: 'periodontics'
      }
    ]
  },
  {
    id: 'general-dentistry',
    name: 'General Dentistry',
    description: 'Fillings, cleanings, and routine procedures',
    icon: 'Shield',
    color: 'bg-orange-50 border-orange-200',
    procedures: [
      {
        id: 'dental-filling',
        name: 'Dental Filling',
        duration: '24-48 hours sensitivity',
        specialty: 'general-dentistry'
      },
      {
        id: 'deep-cleaning',
        name: 'Deep Cleaning',
        duration: '1-2 days sensitivity',
        specialty: 'general-dentistry'
      }
    ]
  },
  {
    id: 'orthodontics',
    name: 'Orthodontics',
    description: 'Braces, aligners, and teeth straightening',
    icon: 'Zap',
    color: 'bg-teal-50 border-teal-200',
    procedures: [
      {
        id: 'braces-placement',
        name: 'Braces Placement',
        duration: '3-7 days adjustment',
        specialty: 'orthodontics'
      },
      {
        id: 'invisalign',
        name: 'Invisalign Treatment',
        duration: '2-3 days adjustment',
        specialty: 'orthodontics'
      }
    ]
  },
  {
    id: 'pedodontics',
    name: 'Pediatric Dentistry',
    description: 'Dental procedures for children',
    icon: 'Baby',
    color: 'bg-pink-50 border-pink-200',
    procedures: [
      {
        id: 'pediatric-extraction',
        name: 'Pediatric Tooth Extraction',
        duration: '2-5 days recovery',
        specialty: 'pedodontics'
      },
      {
        id: 'pediatric-filling',
        name: 'Pediatric Filling',
        duration: '24 hours sensitivity',
        specialty: 'pedodontics'
      }
    ]
  }
];

export const procedureDetails = {
  'root-canal': {
    id: 'root-canal',
    name: 'Root Canal Treatment',
    specialty: 'Endodontics',
    overview: 'Root canal treatment removes infected or damaged tissue from inside your tooth to save it from extraction.',
    immediateAftercare: [
      'Apply ice pack to reduce swelling (15 minutes on, 15 minutes off)',
      'Take prescribed pain medication as directed',
      'Avoid chewing on the treated tooth until permanent restoration',
      'Maintain gentle oral hygiene around the area'
    ],
    dietRestrictions: [
      'Avoid hard, crunchy foods for 24-48 hours',
      'No extremely hot or cold foods/drinks',
      'Chew on the opposite side of your mouth',
      'Avoid sticky candies and gum'
    ],
    warningSignsToCallDoctor: [
      'Severe pain that worsens after 2-3 days',
      'Swelling that increases after 48 hours',
      'Fever above 101°F (38.3°C)',
      'Temporary filling falls out',
      'Allergic reaction to medication'
    ],
    recoveryTimeline: [
      { day: '1-2', activity: 'Mild discomfort and sensitivity normal' },
      { day: '3-5', activity: 'Pain should significantly decrease' },
      { day: '7-10', activity: 'Most discomfort should resolve' },
      { day: '14+', activity: 'Return for permanent restoration placement' }
    ],
    medications: [
      'Ibuprofen 600mg every 6 hours for inflammation',
      'Acetaminophen as needed for additional pain relief',
      'Antibiotics if prescribed - complete full course'
    ]
  },
  'tooth-extraction': {
    id: 'tooth-extraction',
    name: 'Tooth Extraction',
    specialty: 'Oral Surgery',
    overview: 'Tooth extraction is the removal of a tooth from its socket in the jawbone.',
    immediateAftercare: [
      'Bite on gauze pad for 30-45 minutes to control bleeding',
      'Apply ice pack to reduce swelling (20 minutes on, 20 minutes off)',
      'Take prescribed pain medication before numbness wears off',
      'Rest with head elevated on pillows'
    ],
    dietRestrictions: [
      'No solid foods for first 24 hours - liquids and soft foods only',
      'Avoid hot liquids for 24 hours',
      'No drinking through straws for 1 week',
      'No alcohol or smoking for at least 72 hours',
      'Gradually return to normal diet as comfort allows'
    ],
    warningSignsToCallDoctor: [
      'Heavy bleeding that won\'t stop after 2 hours',
      'Severe pain that worsens after day 3',
      'Dry socket symptoms (severe throbbing pain)',
      'Signs of infection (fever, pus, bad taste)',
      'Numbness lasting more than 24 hours'
    ],
    recoveryTimeline: [
      { day: '1', activity: 'Blood clot forms - avoid disturbing' },
      { day: '2-3', activity: 'Swelling peaks then begins to decrease' },
      { day: '7', activity: 'Stitches removed if placed' },
      { day: '14-21', activity: 'Complete soft tissue healing' }
    ],
    medications: [
      'Ibuprofen for pain and swelling reduction',
      'Prescription pain medication if provided',
      'Antibiotics only if prescribed'
    ]
  },
  'dental-crown': {
    id: 'dental-crown',
    name: 'Dental Crown',
    specialty: 'Prosthodontics',
    overview: 'A dental crown is a tooth-shaped cap placed over a damaged tooth to restore its shape, size, and strength.',
    immediateAftercare: [
      'Avoid chewing on the crown side until numbness wears off',
      'Temporary crown may feel loose - this is normal',
      'Brush and floss gently around the temporary crown',
      'Use warm salt water rinses to keep area clean'
    ],
    dietRestrictions: [
      'Avoid sticky foods that could pull off temporary crown',
      'No hard or crunchy foods on the crown side',
      'Cut foods into smaller pieces',
      'Avoid chewing gum and hard candies'
    ],
    warningSignsToCallDoctor: [
      'Temporary crown falls off completely',
      'Severe sensitivity to hot/cold that persists',
      'Crown feels too high when biting',
      'Gum swelling or bleeding around crown',
      'Persistent bad taste or odor'
    ],
    recoveryTimeline: [
      { day: '1-2', activity: 'Mild sensitivity and adjustment period' },
      { day: '3-7', activity: 'Comfort with temporary crown' },
      { day: '14-21', activity: 'Permanent crown placement appointment' },
      { day: '21+', activity: 'Full function and comfort restored' }
    ],
    medications: [
      'Over-the-counter pain relievers as needed',
      'Desensitizing toothpaste if recommended'
    ]
  },
  'wisdom-teeth': {
    id: 'wisdom-teeth',
    name: 'Wisdom Teeth Removal',
    specialty: 'Oral Surgery',
    overview: 'Wisdom teeth removal is the surgical extraction of one or more third molars (wisdom teeth).',
    immediateAftercare: [
      'Bite on gauze for 45-60 minutes after surgery',
      'Apply ice packs for first 24 hours (20 min on, 20 min off)',
      'Keep head elevated when lying down',
      'Take medications as prescribed',
      'Get plenty of rest'
    ],
    dietRestrictions: [
      'Liquids only for first 24 hours',
      'No hot liquids or foods for 48 hours',
      'Soft foods only for first week',
      'No straws, spitting, or smoking for 1 week',
      'Avoid small seeds and nuts for 2 weeks'
    ],
    warningSignsToCallDoctor: [
      'Excessive bleeding that won\'t stop',
      'Severe pain increasing after day 3',
      'Dry socket (intense throbbing pain)',
      'Fever above 101°F for more than 24 hours',
      'Numbness or tingling lasting beyond first day'
    ],
    recoveryTimeline: [
      { day: '1-3', activity: 'Peak swelling and discomfort' },
      { day: '4-7', activity: 'Gradual improvement in symptoms' },
      { day: '7-10', activity: 'Most swelling resolved' },
      { day: '14-21', activity: 'Complete soft tissue healing' }
    ],
    medications: [
      'Prescription pain medication as directed',
      'Anti-inflammatory medication for swelling',
      'Antibiotics if prescribed - complete full course'
    ]
  }
};

export const searchProcedures = (query) => {
  const allProcedures = dentalSpecialties.flatMap(specialty => 
    specialty.procedures.map(proc => ({
      ...proc,
      specialtyName: specialty.name,
      specialtyColor: specialty.color
    }))
  );
  
  if (!query) return allProcedures;
  
  return allProcedures.filter(proc => 
    proc.name.toLowerCase().includes(query.toLowerCase()) ||
    proc.specialtyName.toLowerCase().includes(query.toLowerCase())
  );
};
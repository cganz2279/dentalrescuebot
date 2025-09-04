const mongoose = require('mongoose');

const recoveryTimelineSchema = new mongoose.Schema({
  day: {
    type: String,
    required: true
  },
  activity: {
    type: String,
    required: true
  }
}, { _id: false });

const procedureSchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    unique: true
  },
  name: {
    type: String,
    required: true
  },
  specialty: {
    type: String,
    required: true
  },
  specialtyName: {
    type: String,
    required: true
  },
  duration: {
    type: String,
    required: true
  },
  overview: {
    type: String,
    required: true
  },
  immediateAftercare: [{
    type: String,
    required: true
  }],
  dietRestrictions: [{
    type: String,
    required: true
  }],
  warningSignsToCallDoctor: [{
    type: String,
    required: true
  }],
  recoveryTimeline: [recoveryTimelineSchema],
  medications: [{
    type: String,
    required: true
  }]
}, {
  timestamps: true
});

// Create text index for search
procedureSchema.index({ 
  name: 'text', 
  specialtyName: 'text', 
  overview: 'text' 
});

module.exports = mongoose.model('Procedure', procedureSchema);
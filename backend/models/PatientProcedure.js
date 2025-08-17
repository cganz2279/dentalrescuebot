const mongoose = require('mongoose');

const patientProcedureSchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    unique: true
  },
  patientId: {
    type: String,
    required: true
  },
  practiceId: {
    type: String,
    required: true
  },
  procedureId: {
    type: String,
    required: true
  },
  // Procedure details
  procedureName: {
    type: String,
    required: true
  },
  performedDate: {
    type: Date,
    required: true
  },
  dentistName: {
    type: String,
    required: true
  },
  // Custom notes from the practice
  practiceNotes: {
    type: String,
    required: false
  },
  customInstructions: [{
    type: String
  }],
  // Patient progress tracking
  status: {
    type: String,
    enum: ['active', 'completed', 'complicated'],
    default: 'active'
  },
  followUpDate: Date,
  // Tracking
  pdfDownloadCount: {
    type: Number,
    default: 0
  },
  lastViewedAt: Date,
  viewCount: {
    type: Number,
    default: 0
  }
}, {
  timestamps: true
});

// Create indexes for performance
patientProcedureSchema.index({ patientId: 1 });
patientProcedureSchema.index({ practiceId: 1 });
patientProcedureSchema.index({ practiceId: 1, patientId: 1 });
patientProcedureSchema.index({ performedDate: -1 });

module.exports = mongoose.model('PatientProcedure', patientProcedureSchema);
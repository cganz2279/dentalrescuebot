const mongoose = require('mongoose');

const specialtySchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    unique: true
  },
  name: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    required: true
  }
}, {
  timestamps: true
});

// Create text index for search
specialtySchema.index({ name: 'text', description: 'text' });

module.exports = mongoose.model('Specialty', specialtySchema);
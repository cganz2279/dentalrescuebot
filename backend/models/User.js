const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    unique: true
  },
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true
  },
  password: {
    type: String,
    required: true,
    minlength: 6
  },
  firstName: {
    type: String,
    required: true
  },
  lastName: {
    type: String,
    required: true
  },
  role: {
    type: String,
    enum: ['super_admin', 'practice_admin', 'practice_staff', 'patient'],
    required: true
  },
  // Practice association
  practiceId: {
    type: String,
    required: function() {
      return this.role !== 'super_admin';
    }
  },
  // Patient-specific fields
  patientInfo: {
    phone: String,
    dateOfBirth: Date,
    emergencyContact: {
      name: String,
      phone: String,
      relationship: String
    },
    medicalHistory: [{
      condition: String,
      medications: [String],
      allergies: [String]
    }]
  },
  // Account status
  isActive: {
    type: Boolean,
    default: true
  },
  isEmailVerified: {
    type: Boolean,
    default: false
  },
  emailVerificationToken: String,
  passwordResetToken: String,
  passwordResetExpires: Date,
  // Login tracking
  lastLoginAt: Date,
  loginCount: {
    type: Number,
    default: 0
  },
  // Invitation system
  invitedBy: {
    type: String, // User ID of who invited them
    required: false
  },
  invitedAt: Date,
  acceptedInvitationAt: Date
}, {
  timestamps: true
});

// Hash password before saving
userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  
  try {
    const salt = await bcrypt.genSalt(12);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Compare password method
userSchema.methods.comparePassword = async function(candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

// Create indexes for performance
userSchema.index({ email: 1 });
userSchema.index({ practiceId: 1 });
userSchema.index({ role: 1 });
userSchema.index({ practiceId: 1, role: 1 });

module.exports = mongoose.model('User', userSchema);
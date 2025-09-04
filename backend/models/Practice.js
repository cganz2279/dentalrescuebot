const mongoose = require('mongoose');

const practiceSchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    unique: true
  },
  name: {
    type: String,
    required: true
  },
  email: {
    type: String,
    required: true,
    unique: true
  },
  phone: {
    type: String,
    required: false
  },
  address: {
    street: String,
    city: String,
    state: String,
    zipCode: String
  },
  website: {
    type: String,
    required: false
  },
  // Branding customization
  branding: {
    logo: String, // URL to logo image
    primaryColor: {
      type: String,
      default: '#2563eb' // Default blue
    },
    secondaryColor: {
      type: String, 
      default: '#1e40af'
    },
    customDomain: String,
    welcomeMessage: {
      type: String,
      default: 'Welcome to our dental post-operative care portal'
    }
  },
  // Subscription information
  subscription: {
    plan: {
      type: String,
      enum: ['basic', 'professional', 'enterprise'],
      default: 'basic'
    },
    status: {
      type: String,
      enum: ['active', 'inactive', 'trial', 'cancelled'],
      default: 'trial'
    },
    stripeCustomerId: String,
    stripeSubscriptionId: String,
    trialEndsAt: Date,
    currentPeriodEnd: Date
  },
  // Settings
  settings: {
    allowPatientRegistration: {
      type: Boolean,
      default: false // Patients must be invited by practice
    },
    requirePatientApproval: {
      type: Boolean,
      default: true
    },
    customProcedures: [{
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Procedure'
    }]
  },
  isActive: {
    type: Boolean,
    default: true
  }
}, {
  timestamps: true
});

// Create indexes for performance
practiceSchema.index({ email: 1 });
practiceSchema.index({ 'subscription.status': 1 });

module.exports = mongoose.model('Practice', practiceSchema);
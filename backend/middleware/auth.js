const jwt = require('jsonwebtoken');
const User = require('../models/User');
const Practice = require('../models/Practice');

const JWT_SECRET = process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-in-production';

// Generate JWT token
const generateToken = (userId, role, practiceId = null) => {
  return jwt.sign(
    { 
      userId, 
      role, 
      practiceId 
    },
    JWT_SECRET,
    { expiresIn: '7d' }
  );
};

// Verify JWT token middleware
const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      return res.status(401).json({
        success: false,
        error: 'Access token required'
      });
    }

    const decoded = jwt.verify(token, JWT_SECRET);
    
    // Get user from database
    const user = await User.findOne({ id: decoded.userId });
    if (!user || !user.isActive) {
      return res.status(401).json({
        success: false,
        error: 'Invalid or inactive user'
      });
    }

    // Update last login
    await User.updateOne(
      { id: decoded.userId },
      { 
        lastLoginAt: new Date(),
        $inc: { loginCount: 1 }
      }
    );

    req.user = user;
    req.userRole = decoded.role;
    req.practiceId = decoded.practiceId;
    
    next();
  } catch (error) {
    console.error('Auth middleware error:', error);
    return res.status(403).json({
      success: false,
      error: 'Invalid or expired token'
    });
  }
};

// Role-based authorization middleware
const requireRole = (roles) => {
  return (req, res, next) => {
    if (!roles.includes(req.userRole)) {
      return res.status(403).json({
        success: false,
        error: 'Insufficient permissions'
      });
    }
    next();
  };
};

// Practice access middleware (ensures user can only access their practice data)
const requirePracticeAccess = async (req, res, next) => {
  try {
    const requestedPracticeId = req.params.practiceId || req.body.practiceId || req.query.practiceId;
    
    // Super admins can access any practice
    if (req.userRole === 'super_admin') {
      return next();
    }
    
    // Users can only access their own practice
    if (req.practiceId !== requestedPracticeId) {
      return res.status(403).json({
        success: false,
        error: 'Access denied to this practice'
      });
    }
    
    // Verify practice is active
    const practice = await Practice.findOne({ 
      id: req.practiceId, 
      isActive: true,
      'subscription.status': { $in: ['active', 'trial'] }
    });
    
    if (!practice) {
      return res.status(403).json({
        success: false,
        error: 'Practice not found or subscription inactive'
      });
    }
    
    req.practice = practice;
    next();
  } catch (error) {
    console.error('Practice access middleware error:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
};

module.exports = {
  generateToken,
  authenticateToken,
  requireRole,
  requirePracticeAccess
};
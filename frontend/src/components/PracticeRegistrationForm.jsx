import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Building, Mail, Phone, Globe, User, Lock, MapPin } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';

const PracticeRegistrationForm = ({ onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    // Practice information
    practiceName: '',
    email: '',
    phone: '',
    website: '',
    
    // Admin user information
    adminFirstName: '',
    adminLastName: '',
    adminPassword: '',
    confirmPassword: '',
    
    // Address information
    street: '',
    city: '',
    state: '',
    zipCode: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { registerPractice } = useAuth();
  const { toast } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validate passwords match
    if (formData.adminPassword !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    // Validate password strength
    if (formData.adminPassword.length < 6) {
      setError('Password must be at least 6 characters long');
      setLoading(false);
      return;
    }

    try {
      const result = await registerPractice(formData);
      
      if (result.success) {
        toast({
          title: "Registration Successful!",
          description: `Welcome to DentalRescueBot, ${result.user.firstName}! Your 15-day trial has started.`,
          variant: "default",
        });
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <img 
              src="https://customer-assets.emergentagent.com/job_dental-healing/artifacts/j7ayzg7r_DentalRescueBotWithRoundedText.png"
              alt="DentalRescueBot Logo"
              className="h-16 w-auto"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">
            Register Your Dental Practice
          </CardTitle>
          <p className="text-gray-600 mt-2">
            Start your 15-day free trial today
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <Alert className="border-red-200 bg-red-50">
                <AlertDescription className="text-red-800">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            {/* Practice Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                <Building className="h-5 w-5 mr-2 text-blue-600" />
                Practice Information
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="practiceName" className="text-sm font-medium text-gray-700">
                    Practice Name *
                  </label>
                  <Input
                    id="practiceName"
                    name="practiceName"
                    type="text"
                    required
                    value={formData.practiceName}
                    onChange={handleInputChange}
                    placeholder="Your Dental Practice"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium text-gray-700">
                    Practice Email *
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      required
                      value={formData.email}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="practice@example.com"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label htmlFor="phone" className="text-sm font-medium text-gray-700">
                    Phone Number
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="phone"
                      name="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="(555) 123-4567"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label htmlFor="website" className="text-sm font-medium text-gray-700">
                    Website
                  </label>
                  <div className="relative">
                    <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="website"
                      name="website"
                      type="url"
                      value={formData.website}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="www.yourpractice.com"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Address Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                <MapPin className="h-5 w-5 mr-2 text-blue-600" />
                Practice Address
              </h3>
              
              <div className="space-y-2">
                <label htmlFor="street" className="text-sm font-medium text-gray-700">
                  Street Address
                </label>
                <Input
                  id="street"
                  name="street"
                  type="text"
                  value={formData.street}
                  onChange={handleInputChange}
                  placeholder="123 Main Street"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label htmlFor="city" className="text-sm font-medium text-gray-700">
                    City
                  </label>
                  <Input
                    id="city"
                    name="city"
                    type="text"
                    value={formData.city}
                    onChange={handleInputChange}
                    placeholder="City"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="state" className="text-sm font-medium text-gray-700">
                    State
                  </label>
                  <Input
                    id="state"
                    name="state"
                    type="text"
                    value={formData.state}
                    onChange={handleInputChange}
                    placeholder="State"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="zipCode" className="text-sm font-medium text-gray-700">
                    ZIP Code
                  </label>
                  <Input
                    id="zipCode"
                    name="zipCode"
                    type="text"
                    value={formData.zipCode}
                    onChange={handleInputChange}
                    placeholder="12345"
                  />
                </div>
              </div>
            </div>

            {/* Admin User Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                <User className="h-5 w-5 mr-2 text-blue-600" />
                Administrator Account
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="adminFirstName" className="text-sm font-medium text-gray-700">
                    First Name *
                  </label>
                  <Input
                    id="adminFirstName"
                    name="adminFirstName"
                    type="text"
                    required
                    value={formData.adminFirstName}
                    onChange={handleInputChange}
                    placeholder="John"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="adminLastName" className="text-sm font-medium text-gray-700">
                    Last Name *
                  </label>
                  <Input
                    id="adminLastName"
                    name="adminLastName"
                    type="text"
                    required
                    value={formData.adminLastName}
                    onChange={handleInputChange}
                    placeholder="Smith"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="adminPassword" className="text-sm font-medium text-gray-700">
                    Password *
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="adminPassword"
                      name="adminPassword"
                      type="password"
                      required
                      value={formData.adminPassword}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="At least 6 characters"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
                    Confirm Password *
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="confirmPassword"
                      name="confirmPassword"
                      type="password"
                      required
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="Confirm password"
                    />
                  </div>
                </div>
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3"
              disabled={loading}
            >
              {loading ? 'Creating Account...' : 'Start Free Trial'}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <button
                onClick={onSwitchToLogin}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Sign In
              </button>
            </p>
          </div>

          <div className="mt-4 text-center">
            <p className="text-xs text-gray-500">
              By registering, you agree to our Terms of Service and Privacy Policy.
              <br />
              <strong>15-day free trial</strong> - No credit card required to start!
              <br />
              After your trial, continue for just $49/month. Cancel anytime.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PracticeRegistrationForm;
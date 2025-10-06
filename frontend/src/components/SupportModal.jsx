import React, { useState } from 'react';
import { X, HelpCircle, Send, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { useToast } from '../hooks/use-toast';
import { practiceApi } from '../services/authApi';

const SupportModal = ({ isOpen, onClose, practiceData }) => {
  const [formData, setFormData] = useState({
    practice_name: practiceData?.name || '',
    email: practiceData?.email || '',
    phone: '',
    support: false,
    suggestions: false,
    description: ''
  });
  
  const [fieldErrors, setFieldErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();

  // Format phone number as user types
  const formatPhoneNumber = (value) => {
    if (!value) return value;
    const phoneNumber = value.replace(/[^\d]/g, '');
    const phoneNumberLength = phoneNumber.length;
    if (phoneNumberLength < 4) return phoneNumber;
    if (phoneNumberLength < 7) {
      return `(${phoneNumber.slice(0, 3)}) ${phoneNumber.slice(3)}`;
    }
    return `(${phoneNumber.slice(0, 3)}) ${phoneNumber.slice(3, 6)}-${phoneNumber.slice(6, 10)}`;
  };

  const validateForm = () => {
    const errors = {};
    
    // Required fields
    if (!formData.practice_name.trim()) {
      errors.practice_name = 'Practice name is required';
    }
    
    if (!formData.email.trim()) {
      errors.email = 'Email address is required';
    } else {
      // Email format validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        errors.email = 'Please enter a valid email address';
      }
    }
    
    if (!formData.description.trim()) {
      errors.description = 'Please describe your issue or suggestion';
    } else if (formData.description.trim().length < 10) {
      errors.description = 'Description must be at least 10 characters long';
    } else if (formData.description.length > 2000) {
      errors.description = 'Description cannot exceed 2000 characters';
    }
    
    // At least one checkbox must be checked
    if (!formData.support && !formData.suggestions) {
      errors.checkboxes = 'Please select at least one option: Support or Suggestions';
    }
    
    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      return;
    }
    
    setIsSubmitting(true);
    setFieldErrors({});
    
    try {
      const response = await practiceApi.submitSupportRequest(formData);
      
      if (response.success) {
        toast({
          title: "Support Request Submitted",
          description: "Thank you! We'll respond within 24 hours.",
          variant: "default"
        });
        
        // Reset form
        setFormData({
          practice_name: practiceData?.name || '',
          email: practiceData?.email || '',
          phone: '',
          support: false,
          suggestions: false,
          description: ''
        });
        
        onClose();
      }
    } catch (error) {
      console.error('Support request error:', error);
      toast({
        title: "Submission Failed", 
        description: "Please try again or contact support directly.",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear field error when user starts typing
    if (fieldErrors[field]) {
      setFieldErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const getCurrentDateTime = () => {
    const now = new Date();
    const date = now.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long', 
      day: 'numeric'
    });
    const time = now.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
    return { date, time };
  };

  const { date, time } = getCurrentDateTime();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <Card className="border-0 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b">
            <div className="flex items-center space-x-2">
              <HelpCircle className="h-5 w-5 text-blue-600" />
              <CardTitle className="text-xl font-bold text-gray-900">Get Help & Support</CardTitle>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={onClose}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </CardHeader>
          
          <CardContent className="p-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Auto-filled date and time */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date *
                  </label>
                  <Input 
                    value={date}
                    disabled
                    className="bg-gray-50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Time *
                  </label>
                  <Input 
                    value={time}
                    disabled  
                    className="bg-gray-50"
                  />
                </div>
              </div>

              {/* Practice Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Practice Name *
                </label>
                <Input
                  value={formData.practice_name}
                  onChange={(e) => handleInputChange('practice_name', e.target.value)}
                  placeholder="Enter practice name"
                  className={fieldErrors.practice_name ? "border-red-500 focus:border-red-500" : ""}
                />
                {fieldErrors.practice_name && (
                  <p className="text-red-500 text-sm mt-1 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {fieldErrors.practice_name}
                  </p>
                )}
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address *
                </label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  placeholder="Enter email address"
                  className={fieldErrors.email ? "border-red-500 focus:border-red-500" : ""}
                />
                {fieldErrors.email && (
                  <p className="text-red-500 text-sm mt-1 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {fieldErrors.email}
                  </p>
                )}
              </div>

              {/* Phone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number
                </label>
                <Input
                  value={formData.phone}
                  onChange={(e) => {
                    const formatted = formatPhoneNumber(e.target.value);
                    handleInputChange('phone', formatted);
                  }}
                  placeholder="(555) 123-4567"
                  maxLength={14}
                />
              </div>

              {/* Request Type Checkboxes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reason for Contact *
                </label>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="support"
                      checked={formData.support}
                      onChange={(e) => handleInputChange('support', e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="support" className="text-sm text-gray-700">
                      Support - I need help with an issue or problem
                    </label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox" 
                      id="suggestions"
                      checked={formData.suggestions}
                      onChange={(e) => handleInputChange('suggestions', e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="suggestions" className="text-sm text-gray-700">
                      Suggestions - I have feedback or feature requests
                    </label>
                  </div>
                </div>
                {fieldErrors.checkboxes && (
                  <p className="text-red-500 text-sm mt-1 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {fieldErrors.checkboxes}
                  </p>
                )}
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description *
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Please describe your issue, suggestion, or feedback in detail..."
                  rows={6}
                  maxLength={2000}
                  className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    fieldErrors.description ? "border-red-500 focus:border-red-500" : ""
                  }`}
                />
                <div className="flex justify-between items-center mt-1">
                  {fieldErrors.description ? (
                    <p className="text-red-500 text-sm flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {fieldErrors.description}
                    </p>
                  ) : (
                    <div></div>
                  )}
                  <span className="text-xs text-gray-500">
                    {formData.description.length}/2000
                  </span>
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex justify-end space-x-3">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={onClose}
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  disabled={isSubmitting}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {isSubmitting ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Submitting...
                    </div>
                  ) : (
                    <div className="flex items-center">
                      <Send className="h-4 w-4 mr-2" />
                      Submit Request
                    </div>
                  )}
                </Button>
              </div>
            </form>

            {/* Response time notice */}
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="text-sm text-blue-800 font-medium">
                    Response Time Commitment
                  </p>
                  <p className="text-sm text-blue-700 mt-1">
                    We do our best to return all requests within 24 hours or less. 
                    For urgent issues, please call us directly.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SupportModal;
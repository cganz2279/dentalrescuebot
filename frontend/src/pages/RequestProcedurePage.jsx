import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { ArrowLeft, FileText, Send, Plus, Lightbulb } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import { useToast } from '../hooks/use-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const RequestProcedurePage = () => {
  const navigate = useNavigate();
  const { user, practice } = useAuth();
  const { toast } = useToast();
  
  const [formData, setFormData] = useState({
    procedureName: '',
    specialty: '',
    description: '',
    requestType: 'new', // 'new' or 'custom'
    customInstructions: '',
    urgency: 'normal',
    additionalNotes: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const specialties = [
    'General Dentistry',
    'Oral Surgery',
    'Periodontics',
    'Endodontics',
    'Orthodontics',
    'Prosthodontics',
    'Pediatric Dentistry'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validate required fields
    if (!formData.procedureName || !formData.specialty || !formData.description) {
      setError('Please fill in all required fields');
      setLoading(false);
      return;
    }

    try {
      const response = await practiceApi.requestProcedure(formData);
      
      if (response.success) {
        toast({
          title: "Request Submitted Successfully!",
          description: "Your procedure request has been submitted for review. You'll be notified when it's available.",
          variant: "default",
        });
        
        // Navigate back to dashboard
        navigate('/');
      } else {
        setError(response.message || 'Failed to submit request');
      }
    } catch (err) {
      setError('Failed to submit request. Please try again.');
      console.error('Request procedure error:', err);
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

  const handleSelectChange = (name, value) => {
    setFormData({
      ...formData,
      [name]: value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center space-x-4">
            <Button
              onClick={() => navigate('/')}
              variant="outline"
              size="sm"
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Dashboard</span>
            </Button>
            <div className="flex items-center space-x-2">
              <img 
                src="https://customer-assets.emergentagent.com/job_dental-healing/artifacts/j7ayzg7r_DentalRescueBotWithRoundedText.png"
                alt="DentalRescueBot Logo"
                className="h-8 w-auto"
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
              <h1 className="text-2xl font-bold text-gray-900">Request New Procedure</h1>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 py-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center text-xl">
              <FileText className="h-6 w-6 mr-2 text-blue-600" />
              Request Post-Operative Procedure
            </CardTitle>
            <p className="text-gray-600">
              Request a new post-operative care guide or submit your own custom instructions
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

              {/* Request Type */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  Request Type *
                </label>
                <Select value={formData.requestType} onValueChange={(value) => handleSelectChange('requestType', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose request type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="new">Request New Procedure (not in library)</SelectItem>
                    <SelectItem value="custom">Submit My Own Custom Instructions</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Procedure Name */}
              <div className="space-y-2">
                <label htmlFor="procedureName" className="text-sm font-medium text-gray-700">
                  Procedure Name *
                </label>
                <Input
                  id="procedureName"
                  name="procedureName"
                  type="text"
                  required
                  value={formData.procedureName}
                  onChange={handleInputChange}
                  placeholder="e.g., Wisdom Tooth Extraction, Crown Preparation"
                  disabled={loading}
                />
              </div>

              {/* Specialty */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  Dental Specialty *
                </label>
                <Select value={formData.specialty} onValueChange={(value) => handleSelectChange('specialty', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose specialty" />
                  </SelectTrigger>
                  <SelectContent>
                    {specialties.map((specialty) => (
                      <SelectItem key={specialty} value={specialty}>
                        {specialty}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <label htmlFor="description" className="text-sm font-medium text-gray-700">
                  Procedure Description *
                </label>
                <Textarea
                  id="description"
                  name="description"
                  required
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Describe the procedure and what post-operative care instructions are needed..."
                  rows="3"
                  disabled={loading}
                />
              </div>

              {/* Custom Instructions (only show if custom type) */}
              {formData.requestType === 'custom' && (
                <div className="space-y-2">
                  <label htmlFor="customInstructions" className="text-sm font-medium text-gray-700">
                    Your Custom Instructions *
                  </label>
                  <Textarea
                    id="customInstructions"
                    name="customInstructions"
                    required
                    value={formData.customInstructions}
                    onChange={handleInputChange}
                    placeholder="Provide your complete post-operative care instructions here..."
                    rows="8"
                    disabled={loading}
                  />
                  <p className="text-xs text-gray-500">
                    Please include all relevant instructions: pain management, diet restrictions, activity limitations, warning signs, etc.
                  </p>
                </div>
              )}

              {/* Urgency */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  Priority Level
                </label>
                <Select value={formData.urgency} onValueChange={(value) => handleSelectChange('urgency', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose priority" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low - Can wait 2-3 weeks</SelectItem>
                    <SelectItem value="normal">Normal - Within 1 week</SelectItem>
                    <SelectItem value="high">High - Within 2-3 days</SelectItem>
                    <SelectItem value="urgent">Urgent - Need ASAP</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Additional Notes */}
              <div className="space-y-2">
                <label htmlFor="additionalNotes" className="text-sm font-medium text-gray-700">
                  Additional Notes
                </label>
                <Textarea
                  id="additionalNotes"
                  name="additionalNotes"
                  value={formData.additionalNotes}
                  onChange={handleInputChange}
                  placeholder="Any additional information or special requirements..."
                  rows="2"
                  disabled={loading}
                />
              </div>

              <div className="flex justify-end space-x-4 pt-6">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/')}
                  disabled={loading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Submitting Request...
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4 mr-2" />
                      Submit Request
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <Card className="border-green-200 bg-green-50">
            <CardContent className="pt-6">
              <div className="flex items-start space-x-3">
                <div className="bg-green-100 rounded-full p-2">
                  <Plus className="h-4 w-4 text-green-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-green-900 mb-2">Request New Procedure</h3>
                  <p className="text-sm text-green-800">
                    Can't find a specific procedure? Request it and our team will create professional post-op instructions for you.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-purple-200 bg-purple-50">
            <CardContent className="pt-6">
              <div className="flex items-start space-x-3">
                <div className="bg-purple-100 rounded-full p-2">
                  <Lightbulb className="h-4 w-4 text-purple-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-purple-900 mb-2">Custom Instructions</h3>
                  <p className="text-sm text-purple-800">
                    Have your own post-op instructions? Submit them and we'll format them for your practice.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default RequestProcedurePage;
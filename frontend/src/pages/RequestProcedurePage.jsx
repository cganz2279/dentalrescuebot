import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { ArrowLeft, FileText, Send, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const RequestProcedurePage = () => {
  const navigate = useNavigate();
  const { user, practice } = useAuth();
  const { toast } = useToast();
  
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    procedureName: '',
    specialty: '',
    description: '',
    reasonForRequest: '',
    urgencyLevel: 'normal'
  });
  const [errors, setErrors] = useState({});

  const specialties = [
    'General Dentistry',
    'Oral Surgery',
    'Endodontics',
    'Periodontics',
    'Orthodontics',
    'Prosthodontics',
    'Pediatric Dentistry',
    'Oral Pathology',
    'Other'
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.procedureName.trim()) {
      newErrors.procedureName = 'Procedure name is required';
    }
    
    if (!formData.specialty) {
      newErrors.specialty = 'Specialty is required';
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }
    
    if (!formData.reasonForRequest.trim()) {
      newErrors.reasonForRequest = 'Reason for request is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setSubmitting(true);
    
    try {
      const requestData = {
        procedureName: formData.procedureName.trim(),
        specialty: formData.specialty,
        description: formData.description.trim(),
        reasonForRequest: formData.reasonForRequest.trim(),
        urgencyLevel: formData.urgencyLevel
      };
      
      const response = await practiceApi.requestNewProcedure(requestData);
      
      toast({
        title: "Request Submitted!",
        description: "Your procedure request has been submitted to our admin team for review.",
        variant: "default",
      });
      
      // Reset form
      setFormData({
        procedureName: '',
        specialty: '',
        description: '',
        reasonForRequest: '',
        urgencyLevel: 'normal'
      });
      
      // Navigate back after delay
      setTimeout(() => {
        navigate('/assign-procedure');
      }, 2000);
      
    } catch (error) {
      console.error('Request procedure error:', error);
      toast({
        title: "Request Failed",
        description: error.response?.data?.detail || "Failed to submit request. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center space-x-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/assign-procedure')}
              className="flex items-center"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Assign Procedure
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Request New Procedure</h1>
              <p className="text-gray-600">
                Request a procedure that's not currently in our database
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 py-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="h-5 w-5 mr-2 text-blue-600" />
              Procedure Request Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <Label htmlFor="procedureName">Procedure Name *</Label>
                <Input
                  id="procedureName"
                  type="text"
                  value={formData.procedureName}
                  onChange={(e) => handleInputChange('procedureName', e.target.value)}
                  placeholder="e.g., Laser Gum Therapy, Bone Grafting, etc."
                  disabled={submitting}
                  className={errors.procedureName ? 'border-red-500' : ''}
                />
                {errors.procedureName && (
                  <p className="text-sm text-red-500 mt-1">{errors.procedureName}</p>
                )}
              </div>

              <div>
                <Label htmlFor="specialty">Specialty *</Label>
                <Select
                  value={formData.specialty}
                  onValueChange={(value) => handleInputChange('specialty', value)}
                >
                  <SelectTrigger className={errors.specialty ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select the dental specialty" />
                  </SelectTrigger>
                  <SelectContent>
                    {specialties.map((specialty) => (
                      <SelectItem key={specialty} value={specialty}>
                        {specialty}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.specialty && (
                  <p className="text-sm text-red-500 mt-1">{errors.specialty}</p>
                )}
              </div>

              <div>
                <Label htmlFor="description">Detailed Procedure Description *</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Provide a comprehensive description of the procedure including:
• What the procedure involves step-by-step
• Typical duration of the procedure
• Equipment or materials used
• Expected patient experience during the procedure
• Any variations or complications that may occur
• Specific post-operative care instructions needed..."
                  disabled={submitting}
                  rows={6}
                  className={errors.description ? 'border-red-500' : ''}
                />
                {errors.description && (
                  <p className="text-sm text-red-500 mt-1">{errors.description}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  <strong>Be as detailed as possible.</strong> This information helps our team understand exactly what post-operative instructions to create.
                </p>
              </div>

              <div>
                <Label htmlFor="reasonForRequest">Detailed Justification & Clinical Need *</Label>
                <Textarea
                  id="reasonForRequest"
                  value={formData.reasonForRequest}
                  onChange={(e) => handleInputChange('reasonForRequest', e.target.value)}
                  placeholder="Please provide detailed information about:
• How frequently you perform this procedure (daily, weekly, monthly)
• Why existing procedures in our database don't meet your needs
• What specific patient education materials you're currently lacking
• How this addition would improve patient care in your practice
• Any unique aspects of your patient population that require this procedure
• Expected patient volume for this procedure..."
                  disabled={submitting}
                  rows={5}
                  className={errors.reasonForRequest ? 'border-red-500' : ''}
                />
                {errors.reasonForRequest && (
                  <p className="text-sm text-red-500 mt-1">{errors.reasonForRequest}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  <strong>This helps us prioritize requests.</strong> Explain the clinical importance and frequency of use.
                </p>
              </div>

              <div>
                <Label htmlFor="urgencyLevel">Priority Level</Label>
                <Select
                  value={formData.urgencyLevel}
                  onValueChange={(value) => handleInputChange('urgencyLevel', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low - Nice to have</SelectItem>
                    <SelectItem value="normal">Normal - Routine request</SelectItem>
                    <SelectItem value="high">High - Needed soon</SelectItem>
                    <SelectItem value="urgent">Urgent - Needed ASAP</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex justify-end space-x-3 pt-6">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/assign-procedure')}
                  disabled={submitting}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={submitting}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {submitting ? (
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

        {/* Info Card */}
        <Card className="mt-6 border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <AlertCircle className="h-5 w-5 text-blue-600" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-900">How to Submit an Effective Request</h3>
                <div className="mt-1 text-sm text-blue-800">
                  <p className="font-semibold mb-2">✅ <strong>Detailed requests get approved faster:</strong></p>
                  <p>• Be specific about the procedure steps and post-op care needed</p>
                  <p>• Explain the clinical importance and frequency of use</p>
                  <p>• Include any special patient education requirements</p>
                  <p>• Mention if you have reference materials or examples</p>
                  <div className="mt-3 pt-2 border-t border-blue-300">
                    <p><strong>Review Process:</strong> Clinical team reviews within 3-5 business days</p>
                    <p><strong>Priority:</strong> High/urgent requests with detailed justification reviewed first</p>
                    <p><strong>Approval:</strong> Once approved, procedure is available to all practices</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default RequestProcedurePage;
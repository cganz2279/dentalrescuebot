import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { ArrowLeft, User, Mail, Phone, Plus, UserCheck } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../hooks/use-toast';
import { ToastAction } from '../components/ui/toast';

const AddPatientPage = () => {
  const navigate = useNavigate();
  const { user, practice } = useAuth();
  const { toast } = useToast();
  
  const [dentists, setDentists] = useState([]);
  const [loadingDentists, setLoadingDentists] = useState(true);
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    cellphone: '',
    primaryDentist: user?.firstName ? `Dr. ${user.firstName} ${user.lastName}` : ''
  });
  
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    loadDentists();
  }, []);

  const loadDentists = async () => {
    try {
      setLoadingDentists(true);
      
      // Try to load dentists from new API, fallback to old doctors API
      try {
        const dentistsResponse = await practiceApi.getDentists();
        setDentists(dentistsResponse.data || []);
      } catch (dentistsError) {
        console.warn('Failed to load dentists, trying doctors API:', dentistsError);
        // Fallback to old doctors API and convert format
        try {
          const doctorsResponse = await practiceApi.getPracticeDoctors();
          const doctorsData = doctorsResponse.data || [];
          // Convert doctors format to dentists format
          const convertedDentists = doctorsData.map(doctor => ({
            id: doctor.id,
            firstName: doctor.firstName || doctor.name?.split(' ')[0] || '',
            lastName: doctor.lastName || doctor.name?.split(' ').slice(1).join(' ') || '',
            email: doctor.email || '',
            phone: doctor.phone || '',
            specialties: doctor.specialties || []
          }));
          setDentists(convertedDentists);
        } catch (doctorsError) {
          console.warn('Failed to load doctors:', doctorsError);
          // Set default dentist from current user
          if (user?.firstName && user?.lastName) {
            setDentists([{
              id: user.id,
              firstName: user.firstName,
              lastName: user.lastName,
              email: user.email || '',
              phone: user.phone || '',
              specialties: []
            }]);
          }
        }
      }
      
    } catch (error) {
      console.error('Load dentists error:', error);
      toast({
        title: "Warning",
        description: "Could not load dentists. You can still add the patient.",
        variant: "destructive",
      });
    } finally {
      setLoadingDentists(false);
    }
  };

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
    
    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }
    
    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await practiceApi.createPatient({
        firstName: formData.firstName.trim(),
        lastName: formData.lastName.trim(),
        email: formData.email.trim().toLowerCase(),
        phone: formData.phone.trim() || null,
        primaryDentist: (formData.primaryDentist && formData.primaryDentist !== 'none') ? formData.primaryDentist : null
      });
      
      const patientName = `${formData.firstName} ${formData.lastName}`;
      
      toast({
        title: "Success!",
        description: `Patient ${patientName} has been added successfully with ${(formData.primaryDentist && formData.primaryDentist !== 'none') ? formData.primaryDentist : 'no assigned dentist'}.`,
        variant: "default",
        action: (
          <ToastAction
            altText="Assign Procedure"
            onClick={() => {
              // Navigate to assign procedure page with the new patient pre-selected
              navigate(`/assign-procedure?patientId=${response.data.patientId}&patientName=${encodeURIComponent(patientName)}`);
            }}
          >
            Assign Procedure
          </ToastAction>
        )
      });
      
      // Reset form
      setFormData({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        primaryDentist: user?.firstName ? `Dr. ${user.firstName} ${user.lastName}` : ''
      });
      
      // Navigate back to dashboard after delay, unless user clicks "Assign Procedure"
      setTimeout(() => {
        navigate('/');
      }, 4000);
      
    } catch (error) {
      console.error('Create patient error:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to add patient. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
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
              onClick={() => navigate('/')}
              className="flex items-center"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Add New Patient</h1>
              <p className="text-gray-600">
                Add a patient to {practice?.name}
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
              <User className="h-5 w-5 mr-2 text-blue-600" />
              Patient Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="firstName">First Name *</Label>
                  <Input
                    id="firstName"
                    type="text"
                    value={formData.firstName}
                    onChange={(e) => handleInputChange('firstName', e.target.value)}
                    placeholder="Enter first name"
                    disabled={loading}
                    className={errors.firstName ? 'border-red-500' : ''}
                  />
                  {errors.firstName && (
                    <p className="text-sm text-red-500 mt-1">{errors.firstName}</p>
                  )}
                </div>
                
                <div>
                  <Label htmlFor="lastName">Last Name *</Label>
                  <Input
                    id="lastName"
                    type="text"
                    value={formData.lastName}
                    onChange={(e) => handleInputChange('lastName', e.target.value)}
                    placeholder="Enter last name"
                    disabled={loading}
                    className={errors.lastName ? 'border-red-500' : ''}
                  />
                  {errors.lastName && (
                    <p className="text-sm text-red-500 mt-1">{errors.lastName}</p>
                  )}
                </div>
              </div>

              <div>
                <Label htmlFor="email">Email Address *</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    placeholder="Enter email address"
                    disabled={loading}
                    className={`pl-10 ${errors.email ? 'border-red-500' : ''}`}
                  />
                </div>
                {errors.email && (
                  <p className="text-sm text-red-500 mt-1">{errors.email}</p>
                )}
              </div>

              <div>
                <Label htmlFor="phone">Phone Number (Optional)</Label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    placeholder="Enter phone number"
                    disabled={loading}
                    className="pl-10"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="primaryDentist">Primary Dentist (Optional)</Label>
                {loadingDentists ? (
                  <div className="flex items-center space-x-2 p-3 border rounded-md">
                    <LoadingSpinner size="sm" />
                    <span className="text-sm text-gray-500">Loading dentists...</span>
                  </div>
                ) : (
                  <Select
                    value={formData.primaryDentist}
                    onValueChange={(value) => handleInputChange('primaryDentist', value)}
                  >
                    <SelectTrigger className={errors.primaryDentist ? 'border-red-500' : ''}>
                      <SelectValue placeholder="Select a primary dentist" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">
                        <div className="flex items-center text-gray-500">
                          <UserCheck className="h-4 w-4 mr-2" />
                          No primary dentist assigned
                        </div>
                      </SelectItem>
                      {dentists.length > 0 ? (
                        dentists.map((dentist) => (
                          <SelectItem key={dentist.id} value={`Dr. ${dentist.firstName} ${dentist.lastName}`}>
                            <div className="flex items-center">
                              <UserCheck className="h-4 w-4 mr-2 text-blue-600" />
                              Dr. {dentist.firstName} {dentist.lastName}
                              {dentist.specialties && dentist.specialties.length > 0 && (
                                <span className="ml-2 text-xs text-gray-500">
                                  ({dentist.specialties.slice(0, 2).join(', ')})
                                </span>
                              )}
                            </div>
                          </SelectItem>
                        ))
                      ) : (
                        <SelectItem value="no-dentists" disabled>
                          <div className="flex items-center text-gray-400">
                            <UserCheck className="h-4 w-4 mr-2" />
                            No dentists found - Add dentists in Practice Settings
                          </div>
                        </SelectItem>
                      )}
                    </SelectContent>
                  </Select>
                )}
                {errors.primaryDentist && (
                  <p className="text-sm text-red-500 mt-1">{errors.primaryDentist}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  The primary dentist will be pre-selected when assigning procedures to this patient
                </p>
              </div>

              <div className="flex justify-end space-x-3 pt-6">
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
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {loading ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Adding Patient...
                    </>
                  ) : (
                    <>
                      <Plus className="h-4 w-4 mr-2" />
                      Add Patient
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
                <User className="h-5 w-5 text-blue-600" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-900">About Patient Access</h3>
                <div className="mt-1 text-sm text-blue-800">
                  <p>• Patients will be able to log in using their email address</p>
                  <p>• They can view assigned post-operative care instructions</p>
                  <p>• Branded PDFs can be downloaded for their reference</p>
                  <p>• You can assign procedures to patients after adding them</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AddPatientPage;
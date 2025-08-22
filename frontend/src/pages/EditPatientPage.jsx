import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { ArrowLeft, User, Mail, Phone, Save } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import { useToast } from '../hooks/use-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const EditPatientPage = () => {
  const navigate = useNavigate();
  const { patientId } = useParams();
  const { user, practice } = useAuth();
  const { toast } = useToast();
  
  const [dentists, setDentists] = useState([]);
  const [patient, setPatient] = useState(null);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    assignedDentistId: ''
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [selectedDentist, setSelectedDentist] = useState(null);

  useEffect(() => {
    loadData();
  }, [patientId]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load patient data and dentists in parallel
      const [patientResponse, dentistsResponse] = await Promise.all([
        practiceApi.getPatient(patientId),
        practiceApi.getStaff()
      ]);
      
      if (patientResponse.success) {
        const patientData = patientResponse.data;
        setPatient(patientData);
        setFormData({
          firstName: patientData.firstName || '',
          lastName: patientData.lastName || '',
          email: patientData.email || '',
          phone: patientData.phone || '',
          assignedDentistId: patientData.assignedDentistId || ''
        });
        
        // Set selected dentist if one is assigned
        if (patientData.assignedDentistId && dentistsResponse.success) {
          const dentist = dentistsResponse.data.find(d => d.id === patientData.assignedDentistId);
          setSelectedDentist(dentist);
        }
      }
      
      if (dentistsResponse.success) {
        setDentists(dentistsResponse.data);
      }
      
    } catch (err) {
      setError('Failed to load patient data. Please try again.');
      console.error('Load patient error:', err);
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

  const handleDentistSelect = (dentistId) => {
    const dentist = dentists.find(d => d.id === dentistId);
    setSelectedDentist(dentist);
    setFormData({
      ...formData,
      assignedDentistId: dentistId
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    // Validate required fields
    if (!formData.firstName || !formData.lastName || !formData.email) {
      setError('Please fill in first name, last name, and email');
      setSaving(false);
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      setSaving(false);
      return;
    }

    try {
      const response = await practiceApi.updatePatient(patientId, formData);
      
      if (response.success) {
        toast({
          title: "Patient Updated Successfully!",
          description: `${formData.firstName} ${formData.lastName} has been updated.`,
          variant: "default",
        });
        
        // Navigate back to dashboard
        navigate('/');
      } else {
        setError(response.message || 'Failed to update patient');
      }
    } catch (err) {
      setError('Failed to update patient. Please try again.');
      console.error('Update patient error:', err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

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
              <h1 className="text-2xl font-bold text-gray-900">Edit Patient</h1>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 py-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center text-xl">
              <User className="h-6 w-6 mr-2 text-blue-600" />
              Edit Patient Information
            </CardTitle>
            <p className="text-gray-600">
              Update patient details and dentist assignment for {practice?.name}
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

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="firstName" className="text-sm font-medium text-gray-700">
                    First Name *
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="firstName"
                      name="firstName"
                      type="text"
                      required
                      value={formData.firstName}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="First name"
                      disabled={saving}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label htmlFor="lastName" className="text-sm font-medium text-gray-700">
                    Last Name *
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="lastName"
                      name="lastName"
                      type="text"
                      required
                      value={formData.lastName}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="Last name"
                      disabled={saving}
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-gray-700">
                  Email Address *
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
                    placeholder="patient@example.com"
                    disabled={saving}
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
                    disabled={saving}
                  />
                </div>
              </div>

              {/* Dentist Assignment */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  Assigned Dentist
                </label>
                <Select value={formData.assignedDentistId} onValueChange={handleDentistSelect}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a dentist (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">No dentist assigned</SelectItem>
                    {dentists.map((dentist) => (
                      <SelectItem key={dentist.id} value={dentist.id}>
                        Dr. {dentist.firstName} {dentist.lastName} ({dentist.role === 'practice_admin' ? 'Admin' : 'Staff'})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedDentist && (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
                    <p className="text-blue-800 text-sm">
                      <strong>Patient assigned to Dr. {selectedDentist.firstName} {selectedDentist.lastName}</strong>
                    </p>
                  </div>
                )}
                <p className="text-xs text-gray-500">
                  You can change the assigned dentist or leave unassigned
                </p>
              </div>

              <div className="flex justify-end space-x-4 pt-6">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/')}
                  disabled={saving}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Updating Patient...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Update Patient
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default EditPatientPage;
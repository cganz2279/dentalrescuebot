import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { ArrowLeft, User, Mail, Phone, Calendar, Save, Plus, X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import { useToast } from '../hooks/use-toast';

const AddPatientPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [dentists, setDentists] = useState([]);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    assignedDentistId: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedDentist, setSelectedDentist] = useState(null);
  const [showAddDentist, setShowAddDentist] = useState(false);
  const [dentistFormData, setDentistFormData] = useState({
    firstName: '',
    lastName: '',
    email: ''
  });

  useEffect(() => {
    loadDentists();
  }, []);

  const loadDentists = async () => {
    try {
      const response = await practiceApi.getStaff();
      if (response.success) {
        setDentists(response.data);
      }
    } catch (err) {
      console.error('Failed to load dentists:', err);
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
      assignedDentistId: dentistId === 'unassigned' ? '' : dentistId
    });
  };

  const handleAddDentist = async (e) => {
    e.preventDefault();
    
    try {
      const BACKEND_URL = import.meta.env?.REACT_APP_BACKEND_URL || 
                          process.env?.REACT_APP_BACKEND_URL || 
                          window.location.origin;
      
      const response = await fetch(`${BACKEND_URL}/api/practice/add-staff`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('dentalToken')}`
        },
        body: JSON.stringify({
          firstName: dentistFormData.firstName,
          lastName: dentistFormData.lastName,
          email: dentistFormData.email
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Refresh dentist list
        await loadDentists();
        
        // Select the newly added dentist
        setFormData({
          ...formData,
          assignedDentistId: data.staffMember.id
        });
        setSelectedDentist(data.staffMember);
        
        // Close modal and reset form
        setShowAddDentist(false);
        setDentistFormData({ firstName: '', lastName: '', email: '' });
        
        toast({
          title: "Dentist Added Successfully!",
          description: `Dr. ${dentistFormData.firstName} ${dentistFormData.lastName} has been added to your practice.`,
          variant: "default",
        });
      } else {
        throw new Error(data.message || 'Failed to add dentist');
      }
    } catch (err) {
      toast({
        title: "Error",
        description: err.message || 'Failed to add dentist',
        variant: "destructive",
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validate required fields
    if (!formData.firstName || !formData.lastName || !formData.email) {
      setError('Please fill in first name, last name, and email');
      setLoading(false);
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      setLoading(false);
      return;
    }

    try {
      const response = await practiceApi.createPatient(formData);
      
      if (response.success) {
        toast({
          title: "Patient Added Successfully!",
          description: `${formData.firstName} ${formData.lastName} has been added to your practice.`,
          variant: "default",
        });

        // Navigate back to dashboard
        navigate('/');
      } else {
        setError(response.detail || response.message || 'Failed to add patient');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add patient. Please try again.');
      console.error('Add patient error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Dashboard</span>
              </Button>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="flex items-center space-x-2">
                <User className="h-5 w-5 text-gray-600" />
                <h1 className="text-xl font-semibold text-gray-900">Add New Patient</h1>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-gray-900">
              Add New Patient
            </CardTitle>
            <p className="text-gray-600 mt-2">
              Add a patient to your practice to assign post-operative procedures
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

              {/* Patient Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                  <User className="h-5 w-5 mr-2 text-blue-600" />
                  Patient Information
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label htmlFor="firstName" className="text-sm font-medium text-gray-700">
                      First Name *
                    </label>
                    <Input
                      id="firstName"
                      name="firstName"
                      type="text"
                      required
                      value={formData.firstName}
                      onChange={handleInputChange}
                      placeholder="John"
                    />
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="lastName" className="text-sm font-medium text-gray-700">
                      Last Name *
                    </label>
                    <Input
                      id="lastName"
                      name="lastName"
                      type="text"
                      required
                      value={formData.lastName}
                      onChange={handleInputChange}
                      placeholder="Smith"
                    />
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
                        placeholder="john@example.com"
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

                  {/* Dentist Assignment */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium text-gray-700">
                        Assign to Dentist (Optional)
                      </label>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setShowAddDentist(true)}
                        className="flex items-center space-x-1"
                      >
                        <Plus className="h-3 w-3" />
                        <span>Add New Dentist</span>
                      </Button>
                    </div>
                    <Select value={formData.assignedDentistId} onValueChange={handleDentistSelect}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose a dentist (optional)" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="unassigned">No dentist assigned</SelectItem>
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
                          <strong>Patient will be assigned to Dr. {selectedDentist.firstName} {selectedDentist.lastName}</strong>
                        </p>
                      </div>
                    )}
                    <p className="text-xs text-gray-500">
                      You can assign this patient to a specific dentist or leave unassigned
                    </p>
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <label htmlFor="dateOfBirth" className="text-sm font-medium text-gray-700">
                      Date of Birth (Optional)
                    </label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        id="dateOfBirth"
                        name="dateOfBirth"
                        type="date"
                        value={formData.dateOfBirth}
                        onChange={handleInputChange}
                        className="pl-10"
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
                <Save className="h-4 w-4 mr-2" />
                {loading ? 'Adding Patient...' : 'Add Patient to Practice'}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-xs text-gray-500">
                After adding the patient, you can assign post-operative procedures.
                <br />
                Patient information will be stored in your practice database.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Add Dentist Modal */}
      {showAddDentist && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Add New Dentist</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAddDentist(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            <form onSubmit={handleAddDentist} className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">First Name</label>
                <Input
                  value={dentistFormData.firstName}
                  onChange={(e) => setDentistFormData({...dentistFormData, firstName: e.target.value})}
                  placeholder="Enter first name"
                  required
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700">Last Name</label>
                <Input
                  value={dentistFormData.lastName}
                  onChange={(e) => setDentistFormData({...dentistFormData, lastName: e.target.value})}
                  placeholder="Enter last name"
                  required
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700">Email</label>
                <Input
                  type="email"
                  value={dentistFormData.email}
                  onChange={(e) => setDentistFormData({...dentistFormData, email: e.target.value})}
                  placeholder="Enter email address"
                  required
                />
              </div>
              
              <div className="flex space-x-3 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowAddDentist(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button type="submit" className="flex-1 bg-blue-600 hover:bg-blue-700">
                  Add Dentist
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AddPatientPage;
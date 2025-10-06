import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { 
  ArrowLeft, 
  UserPlus,
  Users,
  Edit,
  Trash2,
  X,
  Save
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import { useToast } from '../hooks/use-toast';

const DentistManagementPage = () => {
  const navigate = useNavigate();
  const { user, practice } = useAuth();
  const { toast } = useToast();

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [dentists, setDentists] = useState([]);
  const [fieldErrors, setFieldErrors] = useState({});
  const [newDentist, setNewDentist] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    licenseNumber: '',
    specialties: []
  });
  const [showAddDentist, setShowAddDentist] = useState(false);

  // Phone number formatting function
  const formatPhoneNumber = (value) => {
    console.log('🔢 Formatting phone number:', value);
    
    // Remove all non-numeric characters
    const phoneNumber = value.replace(/[^\d]/g, '');
    console.log('📱 Cleaned phone number:', phoneNumber);
    
    // Don't format if less than 4 digits
    if (phoneNumber.length < 4) {
      console.log('📱 Too short, returning as-is');
      return phoneNumber;
    }
    
    let formatted;
    // Format as (123) 123-1234
    if (phoneNumber.length <= 6) {
      formatted = `(${phoneNumber.slice(0, 3)}) ${phoneNumber.slice(3)}`;
    } else {
      formatted = `(${phoneNumber.slice(0, 3)}) ${phoneNumber.slice(3, 6)}-${phoneNumber.slice(6, 10)}`;
    }
    
    console.log('📱 Formatted result:', formatted);
    return formatted;
  };

  useEffect(() => {
    loadDentists();
  }, []);

  useEffect(() => {
    console.log('🔍 fieldErrors state changed:', fieldErrors);
  }, [fieldErrors]);

  const loadDentists = async () => {
    setLoading(true);
    try {
      const response = await practiceApi.getDentists();
      setDentists(response.data || []);
    } catch (error) {
      console.error('Failed to load dentists:', error);
      toast({
        title: "Error",
        description: "Failed to load dentists",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddDentist = async () => {
    console.log('🚀 handleAddDentist called with newDentist:', newDentist);
    console.log('🔍 newDentist.id value:', newDentist.id);
    
    if (!newDentist.firstName || !newDentist.lastName || !newDentist.email) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields (First Name, Last Name, Email)",
        variant: "destructive",
      });
      return;
    }

    setSaving(true);
    try {
      if (newDentist.id) {
        // Update existing dentist
        await practiceApi.updateDentist(newDentist.id, {
          firstName: newDentist.firstName,
          lastName: newDentist.lastName,
          email: newDentist.email,
          phone: newDentist.phone,
          licenseNumber: newDentist.licenseNumber,
          specialties: newDentist.specialties
        });
        toast({
          title: "Success",
          description: "Dentist updated successfully!",
        });
      } else {
        // Add new dentist
        await practiceApi.addDentist(newDentist);
        toast({
          title: "Success",
          description: "Dentist added successfully!",
        });
      }
      
      setNewDentist({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        licenseNumber: '',
        specialties: []
      });
      
      // Clear any field errors on successful submission
      setFieldErrors({});
      
      setShowAddDentist(false);
      loadDentists(); // Reload the list
    } catch (error) {
      console.error('🚨 Dentist save error caught:', error);
      console.error('🚨 Error response data:', error.response?.data);
      
      let errorMessage = "Failed to save dentist";
      let hasFieldErrors = false;
      const newFieldErrors = {};
      
      try {
        // Handle different error response formats
        if (error.response?.data) {
          const errorData = error.response.data;
          console.log('🔍 Processing error data:', errorData);
          
          // Handle Pydantic validation errors (array format)
          if (Array.isArray(errorData)) {
            console.log('📝 Array format validation error');
            errorData.forEach(err => {
              if (typeof err === 'object' && err.loc && err.msg) {
                const fieldName = err.loc[err.loc.length - 1]; // Get the field name
                if (fieldName === 'email') {
                  newFieldErrors.email = err.msg;
                  hasFieldErrors = true;
                } else {
                  errorMessage = err.msg;
                }
              }
            });
            if (!hasFieldErrors) {
              errorMessage = errorData.map(err => 
                typeof err === 'object' && err.msg ? err.msg : String(err)
              ).join(', ');
            }
          }
          // Handle FastAPI validation error with detail containing array
          else if (errorData.detail && Array.isArray(errorData.detail)) {
            console.log('📝 Detail array format validation error');
            errorData.detail.forEach(err => {
              if (typeof err === 'object' && err.loc && err.msg) {
                const fieldName = err.loc[err.loc.length - 1]; // Get the field name
                if (fieldName === 'email') {
                  newFieldErrors.email = err.msg;
                  hasFieldErrors = true;
                } else {
                  errorMessage = err.msg;
                }
              }
            });
            if (!hasFieldErrors) {
              errorMessage = errorData.detail.map(err => 
                typeof err === 'object' && err.msg ? err.msg : String(err)
              ).join(', ');
            }
          }
          // Handle standard error responses
          else if (typeof errorData.detail === 'string') {
            console.log('📝 String detail error');
            errorMessage = errorData.detail;
          }
          // Handle any other object error responses - convert to string
          else if (typeof errorData === 'object') {
            console.log('📝 Object error - converting to string');
            errorMessage = `Validation error: ${JSON.stringify(errorData)}`;
          }
          else {
            console.log('📝 Other error type');
            errorMessage = String(errorData);
          }
        }
        // Fallback for network errors
        else if (error.message) {
          errorMessage = error.message;
        }
      } catch (parseError) {
        console.error('Error parsing error response:', parseError);
        errorMessage = "An unexpected error occurred";
      }
      
      // Ensure the errorMessage is always a string
      if (typeof errorMessage !== 'string') {
        console.warn('⚠️ Error message was not a string:', errorMessage);
        errorMessage = String(errorMessage);
      }
      
      console.log('✅ Final error processing:', { 
        hasFieldErrors, 
        newFieldErrors, 
        errorMessage,
        action: newDentist.id ? 'UPDATE' : 'ADD'
      });
      
      // Set field-specific errors using functional update to avoid closure issues
      setFieldErrors(prevErrors => {
        console.log('🔧 Previous fieldErrors state:', prevErrors);
        console.log('🔧 Setting fieldErrors state to:', newFieldErrors);
        return {...newFieldErrors};
      });
      
      // Only show toast for general errors, not field-specific ones
      if (!hasFieldErrors) {
        console.log('📢 Showing toast error since no field errors detected');
        toast({
          title: "Error",
          description: errorMessage,
          variant: "destructive",
        });
      } else {
        console.log('🎯 Field errors detected, not showing toast:', newFieldErrors);
        console.log('🚫 Suppressing toast notification');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleRemoveDentist = async (dentistId) => {
    if (!confirm('Are you sure you want to remove this dentist?')) return;

    try {
      await practiceApi.removeDentist(dentistId);
      toast({
        title: "Success",
        description: "Dentist removed successfully",
      });
      loadDentists();
    } catch (error) {
      toast({
        title: "Error", 
        description: "Failed to remove dentist",
        variant: "destructive",
      });
    }
  };

  const resetForm = () => {
    setNewDentist({
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      licenseNumber: '',
      specialties: []
    });
    
    // Clear any field errors when resetting form
    setFieldErrors({});
    
    setShowAddDentist(false);
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
                onClick={() => navigate('/dashboard')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Dashboard</span>
              </Button>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-indigo-600" />
                <h1 className="text-xl font-semibold text-gray-900">Dentist Management</h1>
              </div>
            </div>
            <Button 
              onClick={() => setShowAddDentist(true)}
              className="bg-indigo-600 hover:bg-indigo-700"
            >
              <UserPlus className="h-4 w-4 mr-2" />
              Add Dentist
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        
        {/* Add/Edit Dentist Form */}
        {showAddDentist && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{newDentist.id ? 'Edit Dentist' : 'Add New Dentist'}</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={resetForm}
                >
                  <X className="h-4 w-4" />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">First Name *</label>
                  <Input
                    value={newDentist.firstName}
                    onChange={(e) => setNewDentist({...newDentist, firstName: e.target.value})}
                    placeholder="Enter first name"
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Last Name *</label>
                  <Input
                    value={newDentist.lastName}
                    onChange={(e) => setNewDentist({...newDentist, lastName: e.target.value})}
                    placeholder="Enter last name"
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Email Address *</label>
                  <Input
                    type="text"
                    value={newDentist.email}
                    onChange={(e) => {
                      const newEmail = e.target.value;
                      console.log('Email onChange:', newEmail);
                      
                      // Clear field error when user starts typing
                      if (fieldErrors.email) {
                        setFieldErrors({...fieldErrors, email: null});
                      }
                      
                      setNewDentist({...newDentist, email: newEmail});
                    }}
                    onBlur={(e) => {
                      console.log('Email onBlur:', e.target.value);
                    }}
                    placeholder="Enter email address"
                    autoComplete="email"
                    noValidate
                    className={fieldErrors.email ? "border-red-500 focus:border-red-500" : ""}
                    style={fieldErrors.email ? {borderColor: 'red', borderWidth: '2px'} : {}}
                  />
                  {fieldErrors.email && (
                    <div className="text-red-500 text-sm mt-1 bg-red-100 p-2 rounded border">
                      ⚠️ EMAIL ERROR: {fieldErrors.email}
                    </div>
                  )}
                  {/* Debug info */}
                  <div className="text-xs text-gray-500 mt-1">
                    Debug - fieldErrors: {JSON.stringify(fieldErrors)}
                  </div>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Phone Number</label>
                  <Input
                    value={newDentist.phone}
                    onChange={(e) => {
                      const formattedPhone = formatPhoneNumber(e.target.value);
                      setNewDentist({...newDentist, phone: formattedPhone});
                    }}
                    placeholder="(555) 123-4567"
                    maxLength={14}
                  />
                </div>
                
                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium text-gray-700">License Number</label>
                  <Input
                    value={newDentist.licenseNumber}
                    onChange={(e) => setNewDentist({...newDentist, licenseNumber: e.target.value})}
                    placeholder="Enter license number"
                  />
                </div>
                
                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium text-gray-700">Specialties</label>
                  <Input
                    value={newDentist.specialties?.join(', ')}
                    onChange={(e) => setNewDentist({
                      ...newDentist, 
                      specialties: e.target.value.split(',').map(s => s.trim()).filter(s => s)
                    })}
                    placeholder="Enter specialties separated by commas (e.g., Oral Surgery, Endodontics)"
                  />
                  <p className="text-sm text-gray-500">Separate multiple specialties with commas</p>
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <Button
                  variant="outline"
                  onClick={resetForm}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleAddDentist}
                  disabled={saving}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {saving ? 'Saving...' : (newDentist.id ? 'Update Dentist' : 'Add Dentist')}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Dentists List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-indigo-600" />
              <span>Practice Dentists ({dentists.length})</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            
            {loading ? (
              <div className="text-center py-8">
                <div className="text-lg">Loading dentists...</div>
              </div>
            ) : dentists.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Users className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <h3 className="text-lg font-medium mb-2">No dentists added yet</h3>
                <p className="text-sm mb-6">Add dentists to your practice to assign procedures</p>
                <Button 
                  onClick={() => setShowAddDentist(true)}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  <UserPlus className="h-4 w-4 mr-2" />
                  Add Your First Dentist
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {dentists.map((dentist) => (
                  <div key={dentist.id} className="flex items-center justify-between p-6 border border-gray-200 rounded-lg hover:bg-gray-50">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
                          <span className="text-indigo-600 font-semibold">
                            {dentist.firstName?.[0]}{dentist.lastName?.[0]}
                          </span>
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900 text-lg">
                            Dr. {dentist.firstName} {dentist.lastName}
                          </h4>
                          <p className="text-gray-600">{dentist.email}</p>
                          {dentist.phone && (
                            <p className="text-gray-500 text-sm">{dentist.phone}</p>
                          )}
                          {dentist.licenseNumber && (
                            <p className="text-gray-500 text-sm">License: {dentist.licenseNumber}</p>
                          )}
                          {dentist.specialties && dentist.specialties.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {dentist.specialties.map((specialty, index) => (
                                <span key={index} className="inline-block bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded-full">
                                  {specialty}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setNewDentist({
                            ...dentist,
                            specialties: dentist.specialties || []
                          });
                          setShowAddDentist(true);
                        }}
                      >
                        <Edit className="h-4 w-4 mr-2" />
                        Edit
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRemoveDentist(dentist.id)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Remove
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DentistManagementPage;
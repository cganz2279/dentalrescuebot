import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { ArrowLeft, FileText, User, Calendar, UserCheck, Plus } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi, authApi } from '../services/authApi';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const AssignProcedurePage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, practice } = useAuth();
  const { toast } = useToast();
  
  // Get pre-selected patient from URL parameters
  const preSelectedPatientId = searchParams.get('patientId');
  const preSelectedPatientName = searchParams.get('patientName');
  
  const [patients, setPatients] = useState([]);
  const [procedures, setProcedures] = useState([]);
  const [dentists, setDentists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  
  // Multi-procedure selection state
  const [isMultiProcedureMode, setIsMultiProcedureMode] = useState(false);
  const [selectedProcedures, setSelectedProcedures] = useState(new Set());
  
  const [formData, setFormData] = useState({
    patientId: preSelectedPatientId || '',
    procedureId: '',
    performedDate: new Date().toISOString().split('T')[0],
    dentistName: user?.firstName ? `${user.firstName} ${user.lastName}` : '',
    practiceNotes: '',
    customInstructions: '',
    followUpDate: ''
  });
  
  const [errors, setErrors] = useState({});

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load essential data first
      const [patientsResponse, proceduresResponse] = await Promise.all([
        practiceApi.getPatients(),
        authApi.getProcedures() // Use global procedures API instead of practice-specific
      ]);
      
      // The API functions already return response.data, which contains {success: true, data: [...]}
      setPatients(patientsResponse.data || []);
      setProcedures(proceduresResponse.data || []);
      
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
      
      // Debug logging
      console.log('Patients loaded:', patientsResponse.data?.length || 0);
      console.log('Procedures loaded:', proceduresResponse.data?.length || 0);
      
    } catch (error) {
      console.error('Load data error:', error);
      toast({
        title: "Error",
        description: "Failed to load patients and procedures",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    // Special handling for procedure selection
    if (field === 'procedureId' && value === 'request-new') {
      // Navigate to request procedure page
      navigate('/request-procedure');
      return;
    }
    
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

  // Multi-procedure selection functions
  const handleProcedureToggle = (procedureId, procedureName) => {
    const newSelected = new Set(selectedProcedures);
    if (newSelected.has(procedureId)) {
      newSelected.delete(procedureId);
    } else {
      newSelected.add(procedureId);
    }
    setSelectedProcedures(newSelected);
    
    // Clear procedure errors when user selects procedures
    if (errors.procedureId || errors.procedures) {
      setErrors(prev => ({
        ...prev,
        procedureId: null,
        procedures: null
      }));
    }
  };

  const handleSelectAllProcedures = () => {
    const allProcedureIds = new Set(procedures.map(p => p.id));
    setSelectedProcedures(allProcedureIds);
  };

  const handleDeselectAllProcedures = () => {
    setSelectedProcedures(new Set());
  };

  const toggleProcedureMode = () => {
    setIsMultiProcedureMode(!isMultiProcedureMode);
    // Clear selections when switching modes
    setSelectedProcedures(new Set());
    setFormData(prev => ({
      ...prev,
      procedureId: ''
    }));
    // Clear any procedure-related errors
    setErrors(prev => ({
      ...prev,
      procedureId: null,
      procedures: null
    }));
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.patientId) {
      newErrors.patientId = 'Please select a patient';
    }
    
    // Validate procedures based on mode
    if (isMultiProcedureMode) {
      if (selectedProcedures.size === 0) {
        newErrors.procedures = 'Please select at least one procedure';
      }
    } else {
      if (!formData.procedureId) {
        newErrors.procedureId = 'Please select a procedure';
      }
    }
    
    if (!formData.performedDate) {
      newErrors.performedDate = 'Performed date is required';
    }
    
    if (!formData.dentistName.trim()) {
      newErrors.dentistName = 'Dentist name is required';
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
      const selectedPatient = patients.find(p => p.id === formData.patientId);
      const customInstructions = formData.customInstructions
        ? formData.customInstructions.split('\n').filter(line => line.trim())
        : [];
      
      if (isMultiProcedureMode) {
        // Multi-procedure assignment
        const selectedProcedureList = Array.from(selectedProcedures).map(procId => {
          const procedure = procedures.find(p => p.id === procId);
          return {
            procedureId: procId,
            procedureName: procedure.name
          };
        });
        
        const multiAssignmentData = {
          patientId: formData.patientId,
          procedures: selectedProcedureList,
          performedDate: new Date(formData.performedDate).toISOString(),
          dentistName: formData.dentistName.trim(),
          practiceNotes: formData.practiceNotes.trim() || null,
          customInstructions: customInstructions.length > 0 ? customInstructions : null,
          followUpDate: formData.followUpDate ? new Date(formData.followUpDate).toISOString() : null
        };
        
        await practiceApi.assignMultipleProcedures(multiAssignmentData);
        
        toast({
          title: "Success!",
          description: `${selectedProcedureList.length} procedures have been assigned to ${selectedPatient.firstName} ${selectedPatient.lastName}.`,
          variant: "default",
        });
        
      } else {
        // Single procedure assignment (existing functionality)
        const selectedProcedure = procedures.find(p => p.id === formData.procedureId);
        
        const assignmentData = {
          patientId: formData.patientId,
          procedureId: formData.procedureId,
          procedureName: selectedProcedure.name,
          performedDate: new Date(formData.performedDate).toISOString(),
          dentistName: formData.dentistName.trim(),
          practiceNotes: formData.practiceNotes.trim() || null,
          customInstructions: customInstructions.length > 0 ? customInstructions : null,
          followUpDate: formData.followUpDate ? new Date(formData.followUpDate).toISOString() : null
        };
        
        await practiceApi.assignProcedure(assignmentData);
        
        toast({
          title: "Success!",
          description: `${selectedProcedure.name} has been assigned to ${selectedPatient.firstName} ${selectedPatient.lastName}.`,
          variant: "default",
        });
      }
      
      // Navigate back to dashboard after short delay
      setTimeout(() => {
        navigate('/');
      }, 1500);
      
    } catch (error) {
      console.error('Assign procedure error:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to assign procedure. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
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
              variant="outline"
              size="sm"
              onClick={() => navigate('/')}
              className="flex items-center"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Assign Procedures</h1>
              <p className="text-gray-600">
                Assign post-operative care instructions to a patient
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
              Procedure Assignment
            </CardTitle>
          </CardHeader>
          <CardContent>
            {preSelectedPatientName && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center">
                  <UserCheck className="h-5 w-5 text-green-600 mr-2" />
                  <div>
                    <p className="text-sm font-medium text-green-800">
                      Patient Pre-selected
                    </p>
                    <p className="text-sm text-green-700">
                      Ready to assign a procedure to <span className="font-semibold">{preSelectedPatientName}</span>
                    </p>
                  </div>
                </div>
              </div>
            )}
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Procedure Mode Toggle */}
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="multiProcedureMode"
                      checked={isMultiProcedureMode}
                      onChange={toggleProcedureMode}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <Label htmlFor="multiProcedureMode" className="text-sm font-medium text-gray-700">
                      Select multiple procedures
                    </Label>
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  {isMultiProcedureMode 
                    ? `${selectedProcedures.size} procedure${selectedProcedures.size !== 1 ? 's' : ''} selected`
                    : 'Single procedure mode'
                  }
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="patientId">Patient *</Label>
                  <Select
                    value={formData.patientId}
                    onValueChange={(value) => handleInputChange('patientId', value)}
                  >
                    <SelectTrigger className={errors.patientId ? 'border-red-500' : ''}>
                      <SelectValue placeholder="Select a patient" />
                    </SelectTrigger>
                    <SelectContent>
                      {patients.length > 0 ? (
                        patients.map((patient) => (
                          <SelectItem key={patient.id} value={patient.id}>
                            <div className="flex items-center">
                              <User className="h-4 w-4 mr-2" />
                              {patient.firstName} {patient.lastName}
                            </div>
                          </SelectItem>
                        ))
                      ) : (
                        <SelectItem value="no-patients" disabled>
                          No patients found
                        </SelectItem>
                      )}
                    </SelectContent>
                  </Select>
                  {errors.patientId && (
                    <p className="text-sm text-red-500 mt-1">{errors.patientId}</p>
                  )}
                  {patients.length === 0 && (
                    <p className="text-sm text-blue-600 mt-1">
                      <Button
                        type="button"
                        variant="link"
                        className="p-0 h-auto"
                        onClick={() => navigate('/add-patient')}
                      >
                        Add a patient first
                      </Button>
                    </p>
                  )}
                </div>
                
                {/* Dynamic Procedure Selection */}
                <div>
                  <Label htmlFor="procedureId">
                    {isMultiProcedureMode ? 'Procedures *' : 'Procedure *'}
                  </Label>
                  
                  {isMultiProcedureMode ? (
                    // Multi-procedure selection with checkboxes
                    <div className="space-y-2">
                      {/* Multi-select controls */}
                      <div className="flex items-center justify-between text-xs">
                        <button
                          type="button"
                          onClick={handleSelectAllProcedures}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          Select All
                        </button>
                        <button
                          type="button"
                          onClick={handleDeselectAllProcedures}
                          className="text-red-600 hover:text-red-800"
                        >
                          Deselect All
                        </button>
                      </div>
                      
                      {/* Checkbox list */}
                      <div className={`border rounded-md max-h-60 overflow-y-auto ${errors.procedures ? 'border-red-500' : 'border-gray-300'}`}>
                        {procedures.length > 0 ? (
                          procedures.map((procedure) => (
                            <div
                              key={procedure.id}
                              className="flex items-center p-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                            >
                              <input
                                type="checkbox"
                                id={`procedure-${procedure.id}`}
                                checked={selectedProcedures.has(procedure.id)}
                                onChange={() => handleProcedureToggle(procedure.id, procedure.name)}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                              />
                              <label
                                htmlFor={`procedure-${procedure.id}`}
                                className="ml-3 flex flex-col cursor-pointer flex-1"
                              >
                                <span className="font-medium text-sm">{procedure.name}</span>
                                <span className="text-xs text-gray-500">{procedure.specialty}</span>
                              </label>
                            </div>
                          ))
                        ) : (
                          <div className="p-3 text-center text-gray-500">
                            No procedures available
                          </div>
                        )}
                      </div>
                    </div>
                  ) : (
                    // Single procedure selection (existing functionality)
                    <Select
                      value={formData.procedureId}
                      onValueChange={(value) => handleInputChange('procedureId', value)}
                    >
                      <SelectTrigger className={errors.procedureId ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select a procedure" />
                      </SelectTrigger>
                      <SelectContent>
                        {procedures.map((procedure) => (
                          <SelectItem key={procedure.id} value={procedure.id}>
                            <div className="flex flex-col items-start">
                              <span className="font-medium">{procedure.name}</span>
                              <span className="text-xs text-gray-500">{procedure.specialty}</span>
                            </div>
                          </SelectItem>
                        ))}
                        <SelectItem value="request-new" className="border-t border-gray-200">
                          <div className="flex items-center text-blue-600">
                            <Plus className="h-4 w-4 mr-2" />
                            Request New Procedure...
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  )}
                  
                  {/* Error messages */}
                  {errors.procedureId && (
                    <p className="text-sm text-red-500 mt-1">{errors.procedureId}</p>
                  )}
                  {errors.procedures && (
                    <p className="text-sm text-red-500 mt-1">{errors.procedures}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="performedDate">Performed Date *</Label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      id="performedDate"
                      type="date"
                      value={formData.performedDate}
                      onChange={(e) => handleInputChange('performedDate', e.target.value)}
                      disabled={submitting}
                      className={`pl-10 ${errors.performedDate ? 'border-red-500' : ''}`}
                    />
                  </div>
                  {errors.performedDate && (
                    <p className="text-sm text-red-500 mt-1">{errors.performedDate}</p>
                  )}
                </div>
                
                <div>
                  <Label htmlFor="followUpDate">Follow-up Date (Optional)</Label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      id="followUpDate"
                      type="date"
                      value={formData.followUpDate}
                      onChange={(e) => handleInputChange('followUpDate', e.target.value)}
                      disabled={submitting}
                      className="pl-10"
                    />
                  </div>
                </div>
              </div>

                <div>
                  <Label htmlFor="dentistName">Dentist *</Label>
                  <Select
                    value={formData.dentistName}
                    onValueChange={(value) => handleInputChange('dentistName', value)}
                  >
                    <SelectTrigger className={errors.dentistName ? 'border-red-500' : ''}>
                      <SelectValue placeholder="Select a dentist" />
                    </SelectTrigger>
                    <SelectContent>
                      {dentists.length > 0 ? (
                        dentists.map((dentist, index) => {
                          // Create unique display name to handle duplicates
                          const baseName = `Dr. ${dentist.firstName} ${dentist.lastName}`;
                          const duplicates = dentists.filter(d => 
                            `Dr. ${d.firstName} ${d.lastName}` === baseName
                          );
                          
                          let displayName = baseName;
                          if (duplicates.length > 1) {
                            // Add email or license to distinguish duplicates
                            const identifier = dentist.email || dentist.licenseNumber || `(${index + 1})`;
                            displayName = `${baseName} - ${identifier}`;
                          }
                          
                          return (
                            <SelectItem key={dentist.id} value={displayName}>
                              <div className="flex items-center">
                                <UserCheck className="h-4 w-4 mr-2" />
                                {displayName}
                              </div>
                            </SelectItem>
                          );
                        })
                      ) : (
                        <SelectItem value="no-dentists" disabled>
                          No dentists found - Add dentists in Practice Settings
                        </SelectItem>
                      )}
                    </SelectContent>
                  </Select>
                  {errors.dentistName && (
                    <p className="text-sm text-red-500 mt-1">{errors.dentistName}</p>
                  )}
                </div>

              <div>
                <Label htmlFor="practiceNotes">Practice Notes (Optional)</Label>
                <Textarea
                  id="practiceNotes"
                  value={formData.practiceNotes}
                  onChange={(e) => handleInputChange('practiceNotes', e.target.value)}
                  placeholder="Add any notes about this procedure..."
                  disabled={submitting}
                  rows={3}
                />
              </div>

              <div>
                <Label htmlFor="customInstructions">Custom Instructions (Optional)</Label>
                <Textarea
                  id="customInstructions"
                  value={formData.customInstructions}
                  onChange={(e) => handleInputChange('customInstructions', e.target.value)}
                  placeholder="Add custom instructions, one per line..."
                  disabled={submitting}
                  rows={4}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Enter each custom instruction on a new line
                </p>
              </div>

              <div className="flex justify-end space-x-3 pt-6">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/')}
                  disabled={submitting}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={submitting || patients.length === 0}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {submitting ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Assigning...
                    </>
                  ) : (
                    <>
                      <Plus className="h-4 w-4 mr-2" />
                      {isMultiProcedureMode 
                        ? `Assign ${selectedProcedures.size} Procedure${selectedProcedures.size !== 1 ? 's' : ''}`
                        : 'Assign Procedure'
                      }
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Info Card */}
        <Card className="mt-6 border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <FileText className="h-5 w-5 text-green-600" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-900">About Procedure Assignment</h3>
                <div className="mt-1 text-sm text-green-800">
                  <p>• Patients will be able to access their assigned post-op instructions</p>
                  <p>• PDFs will be branded with your practice colors and logo</p>
                  <p>• Patients can download instructions for offline reference</p>
                  <p>• Follow-up reminders can be set for patient care</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AssignProcedurePage;
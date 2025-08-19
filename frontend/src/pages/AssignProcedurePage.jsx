import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Textarea } from '../components/ui/textarea';
import { ArrowLeft, FileText, User, Calendar, Stethoscope, ClipboardList } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import { dentalApi } from '../services/api';
import { useToast } from '../hooks/use-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const AssignProcedurePage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const preSelectedPatientId = searchParams.get('patientId');
  const { user } = useAuth();
  const { toast } = useToast();

  const [patients, setPatients] = useState([]);
  const [procedures, setProcedures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    patientId: preSelectedPatientId || '',
    procedureId: '',
    procedureName: '',
    performedDate: new Date().toISOString().split('T')[0], // Today's date
    dentistName: '',
    practiceNotes: '',
    customInstructions: [''],
    followUpDate: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Load patients and procedures in parallel
      const [patientsResponse, proceduresResponse] = await Promise.all([
        practiceApi.getPatients(),
        dentalApi.getProcedures()
      ]);

      if (patientsResponse.success) {
        setPatients(patientsResponse.data);
      } else {
        throw new Error('Failed to load patients');
      }

      if (proceduresResponse.success) {
        setProcedures(proceduresResponse.data);
      } else {
        throw new Error('Failed to load procedures');
      }

    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load data';
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
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

  const handleProcedureChange = (procedureId) => {
    const selectedProcedure = procedures.find(p => p.id === procedureId);
    setFormData({
      ...formData,
      procedureId,
      procedureName: selectedProcedure ? selectedProcedure.name : ''
    });
  };

  const handleCustomInstructionChange = (index, value) => {
    const newInstructions = [...formData.customInstructions];
    newInstructions[index] = value;
    setFormData({
      ...formData,
      customInstructions: newInstructions
    });
  };

  const addCustomInstruction = () => {
    setFormData({
      ...formData,
      customInstructions: [...formData.customInstructions, '']
    });
  };

  const removeCustomInstruction = (index) => {
    const newInstructions = formData.customInstructions.filter((_, i) => i !== index);
    setFormData({
      ...formData,
      customInstructions: newInstructions.length > 0 ? newInstructions : ['']
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    // Validate required fields
    if (!formData.patientId || !formData.procedureId || !formData.dentistName) {
      setError('Please fill in patient, procedure, and dentist name');
      setSubmitting(false);
      return;
    }

    try {
      // Filter out empty custom instructions
      const cleanInstructions = formData.customInstructions.filter(instruction => instruction.trim() !== '');
      
      const assignmentData = {
        patientId: formData.patientId,
        procedureId: formData.procedureId,
        procedureName: formData.procedureName,
        performedDate: formData.performedDate + 'T00:00:00Z', // ISO format
        dentistName: formData.dentistName,
        practiceNotes: formData.practiceNotes || null,
        customInstructions: cleanInstructions.length > 0 ? cleanInstructions : null,
        followUpDate: formData.followUpDate ? formData.followUpDate + 'T00:00:00Z' : null
      };

      const response = await practiceApi.assignProcedure(assignmentData);
      
      if (response.success) {
        toast({
          title: "Procedure Assigned Successfully!",
          description: `${formData.procedureName} has been assigned to the selected patient.`,
          variant: "default",
        });

        // Navigate back to dashboard
        navigate('/dashboard');
      } else {
        setError(response.detail || response.message || 'Failed to assign procedure');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to assign procedure. Please try again.';
      setError(errorMessage);
      console.error('Assign procedure error:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

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
                <FileText className="h-5 w-5 text-gray-600" />
                <h1 className="text-xl font-semibold text-gray-900">Assign Procedure</h1>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-gray-900">
              Assign Post-Operative Procedure
            </CardTitle>
            <p className="text-gray-600 mt-2">
              Assign a post-operative care procedure to a patient
            </p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-8">
              {error && (
                <Alert className="border-red-200 bg-red-50">
                  <AlertDescription className="text-red-800">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              {/* Patient Selection */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                  <User className="h-5 w-5 mr-2 text-blue-600" />
                  Select Patient
                </h3>
                
                <div className="space-y-2">
                  <Label htmlFor="patientId">Patient *</Label>
                  <Select value={formData.patientId} onValueChange={(value) => setFormData({...formData, patientId: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a patient" />
                    </SelectTrigger>
                    <SelectContent>
                      {patients.map((patient) => (
                        <SelectItem key={patient.id} value={patient.id}>
                          {patient.firstName} {patient.lastName} ({patient.email})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {patients.length === 0 && (
                    <p className="text-sm text-gray-500">
                      No patients found. <Button variant="link" onClick={() => navigate('/add-patient')} className="p-0 h-auto">Add a patient first</Button>
                    </p>
                  )}
                </div>
              </div>

              {/* Procedure Selection */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                  <ClipboardList className="h-5 w-5 mr-2 text-green-600" />
                  Select Procedure
                </h3>
                
                <div className="space-y-2">
                  <Label htmlFor="procedureId">Procedure *</Label>
                  <Select value={formData.procedureId} onValueChange={handleProcedureChange}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a procedure" />
                    </SelectTrigger>
                    <SelectContent>
                      {procedures.map((procedure) => (
                        <SelectItem key={procedure.id} value={procedure.id}>
                          {procedure.name} ({procedure.specialtyName})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Procedure Details */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                  <Stethoscope className="h-5 w-5 mr-2 text-purple-600" />
                  Procedure Details
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="performedDate">Procedure Date *</Label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        id="performedDate"
                        name="performedDate"
                        type="date"
                        required
                        value={formData.performedDate}
                        onChange={handleInputChange}
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="dentistName">Dentist Name *</Label>
                    <div className="relative">
                      <Stethoscope className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        id="dentistName"
                        name="dentistName"
                        type="text"
                        required
                        value={formData.dentistName}
                        onChange={handleInputChange}
                        className="pl-10"
                        placeholder="Dr. Smith"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="followUpDate">Follow-up Date (Optional)</Label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        id="followUpDate"
                        name="followUpDate"
                        type="date"
                        value={formData.followUpDate}
                        onChange={handleInputChange}
                        className="pl-10"
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="practiceNotes">Practice Notes (Optional)</Label>
                  <Textarea
                    id="practiceNotes"
                    name="practiceNotes"
                    value={formData.practiceNotes}
                    onChange={handleInputChange}
                    placeholder="Any additional notes for this procedure..."
                    rows={3}
                  />
                </div>
              </div>

              {/* Custom Instructions */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800">
                  Custom Instructions (Optional)
                </h3>
                <p className="text-sm text-gray-600">
                  Add any specific instructions for this patient beyond the standard procedure guidelines
                </p>
                
                {formData.customInstructions.map((instruction, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <Input
                      value={instruction}
                      onChange={(e) => handleCustomInstructionChange(index, e.target.value)}
                      placeholder={`Custom instruction ${index + 1}`}
                      className="flex-1"
                    />
                    {formData.customInstructions.length > 1 && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => removeCustomInstruction(index)}
                      >
                        Remove
                      </Button>
                    )}
                  </div>
                ))}
                
                <Button
                  type="button"
                  variant="outline"
                  onClick={addCustomInstruction}
                  className="w-full"
                >
                  Add Another Instruction
                </Button>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3"
                disabled={submitting}
              >
                <FileText className="h-4 w-4 mr-2" />
                {submitting ? 'Assigning Procedure...' : 'Assign Procedure to Patient'}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-xs text-gray-500">
                After assigning the procedure, the patient can view their post-operative care instructions.
                <br />
                They will be able to download a personalized PDF with your practice branding.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AssignProcedurePage;
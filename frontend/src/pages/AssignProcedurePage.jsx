import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Textarea } from '../components/ui/textarea';
import { ArrowLeft, FileText, User, Calendar, Stethoscope, Search, Plus } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import { dentalApi } from '../services/api';
import { useToast } from '../hooks/use-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const AssignProcedurePage = () => {
  const navigate = useNavigate();
  const { user, practice } = useAuth();
  const { toast } = useToast();
  
  const [patients, setPatients] = useState([]);
  const [procedures, setProcedures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    patientId: '',
    procedureId: '',
    performedDate: new Date().toISOString().split('T')[0], // Today's date
    dentistName: '',
    practiceNotes: '',
    followUpDate: ''
  });
  
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [selectedProcedure, setSelectedProcedure] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load patients and procedures in parallel
      const [patientsResponse, proceduresResponse] = await Promise.all([
        practiceApi.getPatients(),
        dentalApi.getProcedures()
      ]);
      
      if (patientsResponse.success) {
        setPatients(patientsResponse.data);
      }
      
      if (proceduresResponse.success) {
        setProcedures(proceduresResponse.data);
      }
      
    } catch (err) {
      setError('Failed to load data. Please try again.');
      console.error('Load data error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    // Validate required fields
    if (!formData.patientId || !formData.procedureId || !formData.dentistName || !formData.performedDate) {
      setError('Please fill in all required fields');
      setSubmitting(false);
      return;
    }

    try {
      const assignmentData = {
        patientId: formData.patientId,
        procedureId: formData.procedureId,
        procedureName: selectedProcedure?.name || '',
        performedDate: formData.performedDate + 'T00:00:00Z',
        dentistName: formData.dentistName,
        practiceNotes: formData.practiceNotes,
        followUpDate: formData.followUpDate ? formData.followUpDate + 'T00:00:00Z' : null
      };

      const response = await practiceApi.assignProcedure(assignmentData);
      
      if (response.success) {
        toast({
          title: "Procedure Assigned Successfully!",
          description: `${selectedProcedure?.name} has been assigned to ${selectedPatient?.firstName} ${selectedPatient?.lastName}.`,
          variant: "default",
        });
        
        // Navigate back to dashboard
        navigate('/');
      } else {
        setError(response.message || 'Failed to assign procedure');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to assign procedure. Please try again.');
      console.error('Assign procedure error:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handlePatientSelect = (patientId) => {
    const patient = patients.find(p => p.id === patientId);
    setSelectedPatient(patient);
    setFormData({
      ...formData,
      patientId: patientId
    });
  };

  const handleProcedureSelect = (procedureId) => {
    const procedure = procedures.find(p => p.id === procedureId);
    setSelectedProcedure(procedure);
    setFormData({
      ...formData,
      procedureId: procedureId
    });
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
              <h1 className="text-2xl font-bold text-gray-900">Assign Procedure</h1>
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
              Assign Post-Operative Procedure
            </CardTitle>
            <p className="text-gray-600">
              Assign a post-operative care procedure to a patient
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

              {/* Patient Selection */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  Select Patient *
                </label>
                <Select value={formData.patientId} onValueChange={handlePatientSelect}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a patient" />
                  </SelectTrigger>
                  <SelectContent>
                    {patients.length === 0 ? (
                      <SelectItem value="no-patients" disabled>
                        No patients available - Add patients first
                      </SelectItem>
                    ) : (
                      patients.map((patient) => (
                        <SelectItem key={patient.id} value={patient.id}>
                          {patient.firstName} {patient.lastName} ({patient.email})
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
                {patients.length === 0 && (
                  <div className="flex items-center justify-between p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                    <p className="text-yellow-800 text-sm">No patients found. Add patients first.</p>
                    <Button
                      type="button"
                      size="sm"
                      onClick={() => navigate('/add-patient')}
                      className="bg-yellow-600 hover:bg-yellow-700 text-white"
                    >
                      <Plus className="h-4 w-4 mr-1" />
                      Add Patient
                    </Button>
                  </div>
                )}
              </div>

              {/* Procedure Selection */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  Select Procedure *
                </label>
                <Select value={formData.procedureId} onValueChange={handleProcedureSelect}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a procedure" />
                  </SelectTrigger>
                  <SelectContent>
                    {procedures.map((procedure) => (
                      <SelectItem key={procedure.id} value={procedure.id}>
                        {procedure.name} ({procedure.specialtyName})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedProcedure && (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
                    <p className="text-blue-800 text-sm">
                      <strong>{selectedProcedure.name}</strong> - {selectedProcedure.duration}
                    </p>
                  </div>
                )}
              </div>

              {/* Procedure Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="performedDate" className="text-sm font-medium text-gray-700">
                    Procedure Date *
                  </label>
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
                      disabled={submitting}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label htmlFor="followUpDate" className="text-sm font-medium text-gray-700">
                    Follow-up Date
                  </label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="followUpDate"
                      name="followUpDate"
                      type="date"
                      value={formData.followUpDate}
                      onChange={handleInputChange}
                      className="pl-10"
                      disabled={submitting}
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="dentistName" className="text-sm font-medium text-gray-700">
                  Dentist Name *
                </label>
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
                    disabled={submitting}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="practiceNotes" className="text-sm font-medium text-gray-700">
                  Practice Notes (Optional)
                </label>
                <Textarea
                  id="practiceNotes"
                  name="practiceNotes"
                  value={formData.practiceNotes}
                  onChange={handleInputChange}
                  placeholder="Any additional notes or custom instructions for this patient..."
                  rows="3"
                  disabled={submitting}
                />
              </div>

              <div className="flex justify-end space-x-4 pt-6">
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
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                  disabled={submitting || patients.length === 0}
                >
                  {submitting ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Assigning...
                    </>
                  ) : (
                    <>
                      <FileText className="h-4 w-4 mr-2" />
                      Assign Procedure
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
            <div className="flex items-start space-x-3">
              <div className="bg-green-100 rounded-full p-2">
                <FileText className="h-4 w-4 text-green-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-green-900 mb-2">What happens after assignment?</h3>
                <ul className="text-sm text-green-800 space-y-1">
                  <li>• Procedure is assigned to the patient in your system</li>
                  <li>• You can view and manage all assigned procedures</li>
                  <li>• Generate and print customized post-op instruction sheets</li>
                  <li>• Track patient procedures in your practice dashboard</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AssignProcedurePage;
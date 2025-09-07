import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { ArrowLeft, Search, User, FileText, Calendar, Download, Edit, Eye } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const PatientManagementPage = () => {
  const navigate = useNavigate();
  const { practice } = useAuth();
  const { toast } = useToast();
  
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientProcedures, setPatientProcedures] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [loadingProcedures, setLoadingProcedures] = useState(false);

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      setLoading(true);
      const response = await practiceApi.getPatients();
      setPatients(response.data || []);
    } catch (error) {
      console.error('Load patients error:', error);
      toast({
        title: "Error",
        description: "Failed to load patients",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadPatientProcedures = async (patientId) => {
    try {
      setLoadingProcedures(true);
      
      // Get all procedures for this specific patient
      const response = await practiceApi.getExportData();
      const allData = response.data;
      
      // Find the specific patient and their procedures
      const patient = allData.patients.find(p => p.id === patientId);
      if (patient && patient.assignedProcedures) {
        setPatientProcedures(patient.assignedProcedures);
      } else {
        setPatientProcedures([]);
      }
      
    } catch (error) {
      console.error('Load patient procedures error:', error);
      toast({
        title: "Error",
        description: "Failed to load patient procedures",
        variant: "destructive",
      });
    } finally {
      setLoadingProcedures(false);
    }
  };

  const handlePatientSelect = (patient) => {
    setSelectedPatient(patient);
    loadPatientProcedures(patient.id);
  };

  const handleEditPatient = (patient) => {
    // Navigate to edit patient page with patient data
    navigate('/edit-patient', { state: { patient } });
  };

  const handlePrintProcedure = async (procedureId) => {
    try {
      toast({
        title: "Generating PDF",
        description: "Creating branded post-operative care document...",
        variant: "default",
      });
      
      const response = await practiceApi.getProcedureAssignment(procedureId);
      const data = response.data;
      
      const { generateProcedurePDF } = await import('../utils/pdfGenerator');
      
      const procedureForPDF = {
        id: data.procedure.id,
        name: data.assignment.procedureName,
        specialty: data.procedure.specialty,
        specialtyName: data.procedure.specialtyName,
        overview: data.procedure.overview,
        immediateAftercare: data.procedure.immediateAftercare || [],
        dietRestrictions: data.procedure.dietRestrictions || [],
        warningSignsToCallDoctor: data.procedure.warningSignsToCallDoctor || [],
        recoveryTimeline: data.procedure.recoveryTimeline || [],
        medications: data.procedure.medications || [],
        patientName: data.patient ? `${data.patient.firstName} ${data.patient.lastName}` : 'Patient',
        patientEmail: data.patient ? data.patient.email : '',
        dentistName: data.assignment.dentistName,
        performedDate: new Date(data.assignment.performedDate).toLocaleDateString(),
        followUpDate: data.assignment.followUpDate ? new Date(data.assignment.followUpDate).toLocaleDateString() : null,
        status: data.assignment.status,
        practiceNotes: data.assignment.practiceNotes,
        customInstructions: data.assignment.customInstructions || [],
        practiceName: practice?.name || 'Dental Practice',
        practiceAddress: practice?.address || practice?.location || '',
        practicePhone: practice?.phone || '',
        practiceWebsite: practice?.website || '',
        practiceOfficeHours: practice?.officeHours || '',
        practiceEmergencyContact: practice?.emergencyContact || ''
      };
      
      const success = generateProcedurePDF(procedureForPDF);
      
      if (success) {
        toast({
          title: "PDF Ready",
          description: `${data.assignment.procedureName} document downloaded successfully.`,
          variant: "default",
        });
      } else {
        throw new Error('PDF generation failed');
      }
      
    } catch (error) {
      console.error('Print error:', error);
      toast({
        title: "Print Failed",
        description: "Failed to generate PDF. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Filter patients based on search term
  const filteredPatients = patients.filter(patient => {
    const searchLower = searchTerm.toLowerCase();
    return (
      patient.firstName.toLowerCase().includes(searchLower) ||
      patient.lastName.toLowerCase().includes(searchLower) ||
      patient.email.toLowerCase().includes(searchLower)
    );
  });

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
              <h1 className="text-2xl font-bold text-gray-900">Patient Management</h1>
              <p className="text-gray-600">
                Manage patients and their procedure assignments
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Side - Patient List */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <User className="h-5 w-5 mr-2 text-blue-600" />
                  Patients ({filteredPatients.length})
                </CardTitle>
                {/* Search Bar */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type="text"
                    placeholder="Search patients..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex justify-center py-8">
                    <LoadingSpinner />
                  </div>
                ) : (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {filteredPatients.map((patient) => (
                      <div
                        key={patient.id}
                        className={`p-3 rounded-lg border transition-colors ${
                          selectedPatient?.id === patient.id
                            ? 'bg-blue-50 border-blue-200'
                            : 'bg-white border-gray-200 hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div 
                            onClick={() => handlePatientSelect(patient)}
                            className="flex-1 cursor-pointer"
                          >
                            <p className="font-medium text-sm">
                              {patient.firstName} {patient.lastName}
                            </p>
                            <p className="text-xs text-gray-500">{patient.email}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleEditPatient(patient);
                              }}
                              className="h-8 w-8 p-0"
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <User className="h-4 w-4 text-gray-400" />
                          </div>
                        </div>
                      </div>
                    ))}
                    {filteredPatients.length === 0 && (
                      <p className="text-center text-gray-500 py-4">
                        {searchTerm ? 'No patients found matching your search' : 'No patients found'}
                      </p>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right Side - Patient Procedures */}
          <div className="lg:col-span-2">
            {selectedPatient ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <FileText className="h-5 w-5 mr-2 text-blue-600" />
                    Procedures for {selectedPatient.firstName} {selectedPatient.lastName}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {loadingProcedures ? (
                    <div className="flex justify-center py-8">
                      <LoadingSpinner />
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {patientProcedures.length > 0 ? (
                        patientProcedures.map((procedure) => (
                          <div key={procedure.id} className="border rounded-lg p-4 bg-white">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <h3 className="font-semibold text-lg">{procedure.procedureName}</h3>
                                <div className="mt-2 space-y-1">
                                  <p className="text-sm text-gray-600">
                                    <Calendar className="h-4 w-4 inline mr-2" />
                                    Performed: {new Date(procedure.performedDate).toLocaleDateString()}
                                  </p>
                                  <p className="text-sm text-gray-600">
                                    Dentist: {procedure.dentistName}
                                  </p>
                                  {procedure.practiceNotes && (
                                    <p className="text-sm text-gray-600">
                                      Notes: {procedure.practiceNotes}
                                    </p>
                                  )}
                                </div>
                                <Badge variant="outline" className="mt-2">
                                  {procedure.status}
                                </Badge>
                              </div>
                              <div className="flex flex-col space-y-2 ml-4">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => navigate(`/procedure-details/${procedure.id}`)}
                                  className="text-xs"
                                >
                                  <Eye className="h-3 w-3 mr-1" />
                                  View
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => navigate(`/edit-procedure/${procedure.id}`)}
                                  className="text-xs"
                                >
                                  <Edit className="h-3 w-3 mr-1" />
                                  Edit
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handlePrintProcedure(procedure.id)}
                                  className="text-xs"
                                >
                                  <Download className="h-3 w-3 mr-1" />
                                  PDF
                                </Button>
                              </div>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8">
                          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                          <p className="text-gray-500">
                            No procedures assigned to {selectedPatient.firstName} {selectedPatient.lastName}
                          </p>
                          <Button
                            onClick={() => navigate('/assign-procedure')}
                            className="mt-4"
                          >
                            Assign Procedure
                          </Button>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">
                      Select a patient from the list to view their procedures
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientManagementPage;
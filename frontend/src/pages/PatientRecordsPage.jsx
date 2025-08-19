import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { 
  ArrowLeft, 
  Search, 
  User, 
  FileText, 
  Calendar,
  Printer,
  Edit,
  Palette,
  Plus,
  Mail,
  Phone
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../hooks/use-toast';
import { generateBrandedPatientPDF } from '../utils/pdfGenerator';

const PatientRecordsPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();

  const [loading, setLoading] = useState(true);
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientProcedures, setPatientProcedures] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loadingProcedures, setLoadingProcedures] = useState(false);

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      setLoading(true);
      const response = await practiceApi.getPatients();
      
      if (response.success) {
        setPatients(response.data);
      } else {
        throw new Error(response.message || 'Failed to load patients');
      }
    } catch (err) {
      toast({
        title: "Error",
        description: err.message || "Failed to load patients",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadPatientProcedures = async (patientId) => {
    try {
      setLoadingProcedures(true);
      const response = await practiceApi.getPatientProcedures(patientId);
      
      if (response.success) {
        setPatientProcedures(response.data);
      } else {
        throw new Error(response.message || 'Failed to load patient procedures');
      }
    } catch (err) {
      toast({
        title: "Error",
        description: err.message || "Failed to load patient procedures",
        variant: "destructive",
      });
      setPatientProcedures([]);
    } finally {
      setLoadingProcedures(false);
    }
  };

  const handlePatientSelect = (patient) => {
    setSelectedPatient(patient);
    loadPatientProcedures(patient.id);
  };

  const handleGeneratePDF = async (assignmentId) => {
    try {
      toast({
        title: "Generating PDF...",
        description: "Please wait while we prepare your branded document.",
        variant: "default",
      });

      const response = await practiceApi.getAssignmentDetails(assignmentId);
      if (response.success) {
        const { assignment, patient, procedure, practice } = response.data;
        const success = await generateBrandedPatientPDF(assignment, procedure, patient, practice);
        
        if (success) {
          toast({
            title: "PDF Generated Successfully!",
            description: `Post-operative guide for ${patient.firstName} ${patient.lastName} has been downloaded.`,
            variant: "default",
          });
        } else {
          throw new Error("PDF generation failed");
        }
      } else {
        throw new Error(response.message || "Failed to get assignment details");
      }
    } catch (err) {
      toast({
        title: "PDF Generation Failed",
        description: err.message || "Failed to generate PDF. Please try again.",
        variant: "destructive",
      });
    }
  };

  const filteredPatients = patients.filter(patient =>
    `${patient.firstName} ${patient.lastName}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
                <User className="h-5 w-5 text-gray-600" />
                <h1 className="text-xl font-semibold text-gray-900">Patient Records</h1>
              </div>
            </div>
            <Button
              onClick={() => navigate('/add-patient')}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="h-4 w-4" />
              <span>Add Patient</span>
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Patient List */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <User className="h-5 w-5 mr-2 text-blue-600" />
                  Patients ({filteredPatients.length})
                </CardTitle>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search patients..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="max-h-96 overflow-y-auto">
                  {filteredPatients.length > 0 ? (
                    filteredPatients.map((patient) => (
                      <div
                        key={patient.id}
                        onClick={() => handlePatientSelect(patient)}
                        className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors ${
                          selectedPatient?.id === patient.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                        }`}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h3 className="font-medium text-gray-900">
                              {patient.firstName} {patient.lastName}
                            </h3>
                            <p className="text-sm text-gray-600 flex items-center mt-1">
                              <Mail className="h-3 w-3 mr-1" />
                              {patient.email}
                            </p>
                            {patient.patientInfo?.phone && (
                              <p className="text-sm text-gray-600 flex items-center mt-1">
                                <Phone className="h-3 w-3 mr-1" />
                                {patient.patientInfo.phone}
                              </p>
                            )}
                          </div>
                          <Badge variant="outline" className="ml-2">
                            {patient.procedureCount || 0} procedures
                          </Badge>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-8 text-center">
                      <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">
                        {searchTerm ? 'No patients match your search' : 'No patients found'}
                      </p>
                      {!searchTerm && (
                        <Button
                          onClick={() => navigate('/add-patient')}
                          variant="outline"
                          className="mt-4"
                        >
                          <Plus className="h-4 w-4 mr-2" />
                          Add Your First Patient
                        </Button>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Patient Details and Procedures */}
          <div className="lg:col-span-2">
            {selectedPatient ? (
              <div className="space-y-6">
                {/* Patient Info */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center">
                        <User className="h-5 w-5 mr-2 text-blue-600" />
                        {selectedPatient.firstName} {selectedPatient.lastName}
                      </div>
                      <Button
                        onClick={() => navigate(`/assign-procedure?patientId=${selectedPatient.id}`)}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <Plus className="h-4 w-4 mr-2" />
                        Assign Procedure
                      </Button>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Email</p>
                        <p className="font-medium">{selectedPatient.email}</p>
                      </div>
                      {selectedPatient.patientInfo?.phone && (
                        <div>
                          <p className="text-sm text-gray-600">Phone</p>
                          <p className="font-medium">{selectedPatient.patientInfo.phone}</p>
                        </div>
                      )}
                      {selectedPatient.patientInfo?.dateOfBirth && (
                        <div>
                          <p className="text-sm text-gray-600">Date of Birth</p>
                          <p className="font-medium">
                            {new Date(selectedPatient.patientInfo.dateOfBirth).toLocaleDateString()}
                          </p>
                        </div>
                      )}
                      <div>
                        <p className="text-sm text-gray-600">Added Date</p>
                        <p className="font-medium">
                          {new Date(selectedPatient.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Patient Procedures */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <FileText className="h-5 w-5 mr-2 text-green-600" />
                      Post-Operative Procedures ({patientProcedures.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {loadingProcedures ? (
                      <div className="flex justify-center py-8">
                        <LoadingSpinner />
                      </div>
                    ) : patientProcedures.length > 0 ? (
                      <div className="space-y-4">
                        {patientProcedures.map((procedure) => (
                          <div key={procedure.id} className="border rounded-lg p-4 bg-gray-50">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <h3 className="font-medium text-gray-900">
                                  {procedure.procedureName}
                                </h3>
                                <p className="text-sm text-gray-600 mt-1">
                                  Dr. {procedure.dentistName}
                                </p>
                                <p className="text-sm text-gray-500 flex items-center mt-1">
                                  <Calendar className="h-3 w-3 mr-1" />
                                  {new Date(procedure.performedDate).toLocaleDateString()}
                                </p>
                                {procedure.followUpDate && (
                                  <p className="text-sm text-gray-500 flex items-center mt-1">
                                    <Calendar className="h-3 w-3 mr-1" />
                                    Follow-up: {new Date(procedure.followUpDate).toLocaleDateString()}
                                  </p>
                                )}
                                {procedure.practiceNotes && (
                                  <p className="text-sm text-gray-600 mt-2 italic">
                                    Notes: {procedure.practiceNotes}
                                  </p>
                                )}
                              </div>
                              <div className="flex flex-col space-y-2 ml-4">
                                <Badge variant="outline">
                                  {procedure.status || 'Active'}
                                </Badge>
                                <div className="flex space-x-1">
                                  <Button
                                    onClick={() => navigate(`/edit-assignment/${procedure.id}`)}
                                    variant="outline"
                                    size="sm"
                                  >
                                    <Edit className="h-3 w-3" />
                                  </Button>
                                  <Button
                                    onClick={() => navigate(`/customize-pdf/${procedure.id}`)}
                                    variant="outline"
                                    size="sm"
                                  >
                                    <Palette className="h-3 w-3" />
                                  </Button>
                                  <Button
                                    onClick={() => handleGeneratePDF(procedure.id)}
                                    variant="outline"
                                    size="sm"
                                  >
                                    <Printer className="h-3 w-3" />
                                  </Button>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-600 mb-4">
                          No post-operative procedures assigned yet
                        </p>
                        <Button
                          onClick={() => navigate(`/assign-procedure?patientId=${selectedPatient.id}`)}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          <Plus className="h-4 w-4 mr-2" />
                          Assign First Procedure
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Card>
                <CardContent className="py-16">
                  <div className="text-center">
                    <User className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Select a Patient
                    </h3>
                    <p className="text-gray-600 mb-6">
                      Choose a patient from the list to view their post-operative procedures and notes
                    </p>
                    <Button
                      onClick={() => navigate('/add-patient')}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Add New Patient
                    </Button>
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

export default PatientRecordsPage;
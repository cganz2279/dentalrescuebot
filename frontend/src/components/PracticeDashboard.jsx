import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  Users, 
  FileText, 
  Calendar, 
  Settings,
  Plus,
  Download,
  Activity,
  Clock,
  AlertCircle,
  Printer,
  Edit,
  Palette,
  FolderOpen
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import LoadingSpinner, { LoadingCard, ErrorMessage } from './LoadingSpinner';
import { useToast } from '../hooks/use-toast';
import { generateBrandedPatientPDF } from '../utils/pdfGenerator';

const PracticeDashboard = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [allPatients, setAllPatients] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientProcedures, setPatientProcedures] = useState([]);
  const [loadingPatientData, setLoadingPatientData] = useState(false);
  const { user, practice, logout } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    loadDashboard();
    loadAllPatients();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await practiceApi.getDashboard();
      setDashboardData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load dashboard');
      toast({
        title: "Error",
        description: "Failed to load dashboard data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadAllPatients = async () => {
    try {
      const response = await practiceApi.getPatients();
      
      if (response.success) {
        setAllPatients(response.data);
      } else {
        console.error('Failed to load patients:', response.message);
      }
    } catch (err) {
      console.error('Error loading patients:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex justify-center items-center py-32">
            <LoadingSpinner size="xl" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <ErrorMessage message={error} onRetry={loadDashboard} />
        </div>
      </div>
    );
  }

  const getSubscriptionStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'trial': return 'bg-blue-100 text-blue-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleGeneratePDF = async (assignmentId) => {
    try {
      toast({
        title: "Generating PDF...",
        description: "Please wait while we prepare your branded document.",
        variant: "default",
      });

      // Get assignment details
      const response = await practiceApi.getAssignmentDetails(assignmentId);
      if (response.success) {
        const { assignment, patient, procedure, practice } = response.data;
        
        // Generate the branded PDF
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
      console.error('PDF generation error:', err);
      toast({
        title: "PDF Generation Failed",
        description: err.message || "Failed to generate PDF. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleEditAssignment = (assignmentId) => {
    // Navigate to edit assignment page
    navigate(`/edit-assignment/${assignmentId}`);
  };

  const handleCustomizePDF = (assignmentId) => {
    // Navigate to customize PDF content page
    navigate(`/customize-pdf/${assignmentId}`);
  };

  const handlePatientSelect = async (patient) => {
    try {
      setLoadingPatientData(true);
      setSelectedPatient(patient);
      
      const response = await practiceApi.getPatientProcedures(patient.id);
      if (response.success) {
        setPatientProcedures(response.data);
      } else {
        setPatientProcedures([]);
        toast({
          title: "Error",
          description: "Failed to load patient procedures",
          variant: "destructive",
        });
      }
    } catch (err) {
      setPatientProcedures([]);
      console.error('Error loading patient procedures:', err);
    } finally {
      setLoadingPatientData(false);
    }
  };

  const filteredPatients = allPatients.filter(patient =>
    `${patient.firstName} ${patient.lastName}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <img 
                src="https://customer-assets.emergentagent.com/job_dental-healing/artifacts/j7ayzg7r_DentalRescueBotWithRoundedText.png"
                alt="DentalRescueBot Logo"
                className="h-12 w-auto"
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {dashboardData?.practice?.name || 'Practice Dashboard'}
                </h1>
                <p className="text-gray-600">
                  Welcome back, {user?.firstName}!
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge className={getSubscriptionStatusColor(dashboardData?.stats?.subscriptionStatus)}>
                {dashboardData?.stats?.subscriptionStatus?.toUpperCase() || 'UNKNOWN'}
              </Badge>
              <Button variant="outline" onClick={logout}>
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Patients</CardTitle>
              <Users className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats?.patientCount || 0}</div>
              <p className="text-xs text-gray-600">Registered patients</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Procedures</CardTitle>
              <FileText className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats?.activeProcedures || 0}</div>
              <p className="text-xs text-gray-600">Current post-op care</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Subscription</CardTitle>
              <Activity className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold capitalize">
                {dashboardData?.stats?.subscriptionStatus || 'Unknown'}
              </div>
              <p className="text-xs text-gray-600">Current plan status</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Button 
            onClick={() => navigate('/add-patient')}
            className="h-16 bg-blue-600 hover:bg-blue-700 text-white flex flex-col items-center justify-center space-y-2"
          >
            <Plus className="h-6 w-6" />
            <span className="font-medium">Add Patient</span>
          </Button>
          
          <Button 
            onClick={() => navigate('/assign-procedure')}
            className="h-16 bg-green-600 hover:bg-green-700 text-white flex flex-col items-center justify-center space-y-2"
          >
            <FileText className="h-6 w-6" />
            <span className="font-medium">Assign Procedure</span>
          </Button>

          <Button 
            onClick={() => navigate('/patient-records')}
            className="h-16 bg-purple-600 hover:bg-purple-700 text-white flex flex-col items-center justify-center space-y-2"
          >
            <FolderOpen className="h-6 w-6" />
            <span className="font-medium">Patient Records</span>
          </Button>
          
          <Button 
            onClick={() => navigate('/practice-settings')}
            variant="outline"
            className="h-16 flex flex-col items-center justify-center space-y-2"
          >
            <Settings className="h-6 w-6" />
            <span className="font-medium">Practice Settings</span>
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Patients */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="h-5 w-5 mr-2 text-blue-600" />
                Recent Patients
              </CardTitle>
            </CardHeader>
            <CardContent>
              {dashboardData?.recentPatients?.length > 0 ? (
                <div className="space-y-4">
                  {dashboardData.recentPatients.map((patient) => (
                    <div key={patient.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium">{patient.firstName} {patient.lastName}</p>
                        <p className="text-sm text-gray-600">{patient.email}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-500">
                          Added {new Date(patient.createdAt).toLocaleDateString()}
                        </p>
                        {patient.lastLoginAt && (
                          <p className="text-xs text-gray-400">
                            Last login: {new Date(patient.lastLoginAt).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No patients yet</p>
                  <p className="text-sm text-gray-500">Start by adding your first patient</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Procedures */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2 text-green-600" />
                Recent Procedures
              </CardTitle>
            </CardHeader>
            <CardContent>
              {dashboardData?.recentProcedures?.length > 0 ? (
                <div className="space-y-4">
                  {dashboardData.recentProcedures.map((procedure) => (
                    <div key={procedure.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <p className="font-medium">{procedure.procedureName}</p>
                        <p className="text-sm text-gray-600">Dr. {procedure.dentistName}</p>
                        <p className="text-xs text-gray-400">
                          {new Date(procedure.performedDate).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className="mb-1">
                          {procedure.status}
                        </Badge>
                        <Button
                          onClick={() => handleEditAssignment(procedure.id)}
                          variant="outline"
                          size="sm"
                          className="flex items-center space-x-1"
                        >
                          <Edit className="h-4 w-4" />
                          <span>Edit</span>
                        </Button>
                        <Button
                          onClick={() => handleCustomizePDF(procedure.id)}
                          variant="outline"
                          size="sm"
                          className="flex items-center space-x-1"
                        >
                          <Palette className="h-4 w-4" />
                          <span>Customize</span>
                        </Button>
                        <Button
                          onClick={() => handleGeneratePDF(procedure.id)}
                          variant="outline"
                          size="sm"
                          className="flex items-center space-x-1"
                        >
                          <Printer className="h-4 w-4" />
                          <span>PDF</span>
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No procedures assigned yet</p>
                  <p className="text-sm text-gray-500">Assign post-op care to patients</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Trial Notice */}
        {dashboardData?.stats?.subscriptionStatus === 'trial' && (
          <Card className="mt-8 border-blue-200 bg-blue-50">
            <CardContent className="pt-6">
              <div className="flex items-center">
                <AlertCircle className="h-5 w-5 text-blue-600 mr-3" />
                <div className="flex-1">
                  <h3 className="font-semibold text-blue-900">Free Trial Active</h3>
                  <p className="text-blue-800 text-sm">
                    Your 15-day free trial is active. Subscribe to continue using DentalRescueBot after your trial ends.
                  </p>
                </div>
                <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                  Subscribe for $49/month
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default PracticeDashboard;
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
  Edit,
  Eye,
  Printer,
  MoreHorizontal
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import LoadingSpinner, { LoadingCard, ErrorMessage } from './LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const PracticeDashboard = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientProcedures, setPatientProcedures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingProcedures, setLoadingProcedures] = useState(false);
  const [error, setError] = useState(null);
  const { user, practice, logout } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load dashboard stats and practice info
      const dashboardResponse = await practiceApi.getDashboard();
      
      // Load ALL patients (not just recent ones)
      const patientsResponse = await practiceApi.getPatients();
      
      // Combine the data
      const combinedData = {
        ...dashboardResponse.data,
        allPatients: patientsResponse.data || [], // All patients for selection
        recentPatients: patientsResponse.data || [] // Keep this for compatibility but use all patients
      };
      
      setDashboardData(combinedData);
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

  const selectPatient = async (patient) => {
    try {
      setSelectedPatient(patient);
      setLoadingProcedures(true);
      setPatientProcedures([]);
      
      // Load procedures for this specific patient
      // This would require a new API endpoint or filtering
      // For now, filter from dashboard data
      const procedures = dashboardData?.recentProcedures?.filter(
        proc => proc.patientId === patient.id
      ) || [];
      
      setPatientProcedures(procedures);
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to load patient procedures",
        variant: "destructive",
      });
    } finally {
      setLoadingProcedures(false);
    }
  };

  const clearPatientSelection = () => {
    setSelectedPatient(null);
    setPatientProcedures([]);
  };

  const viewProcedure = (procedure) => {
    try {
      console.log('Viewing procedure:', procedure);
      // Navigate to procedure details page using the assignment ID (not template ID)
      const assignmentId = procedure.id; // Use assignment ID, not procedureId
      console.log('Navigating to view with assignment ID:', assignmentId);
      navigate(`/procedure/${assignmentId}`);
    } catch (error) {
      console.error('View procedure error:', error);
      toast({
        title: "Error",
        description: "Failed to open procedure details",
        variant: "destructive",
      });
    }
  };

  const editProcedure = (procedure) => {
    try {
      console.log('Editing procedure:', procedure);
      // Navigate to edit procedure assignment page using the assignment ID
      const assignmentId = procedure.id;
      console.log('Navigating to:', `/edit-procedure/${assignmentId}`);
      navigate(`/edit-procedure/${assignmentId}`);
    } catch (error) {
      console.error('Edit procedure error:', error);
      toast({
        title: "Error",
        description: "Failed to open procedure editor",
        variant: "destructive",
      });
    }
  };

  const printProcedure = async (procedure) => {
    try {
      console.log('=== PRINT DEBUG START ===');
      console.log('Printing procedure - raw data:', procedure);
      console.log('Practice data:', practice);
      
      // Validate required data
      if (!procedure || !procedure.procedureName) {
        throw new Error('Procedure data is incomplete');
      }

      // Use the shared HTML-to-PDF generator for identical output
      const { generateViewPagePDF } = await import('../utils/htmlToPdf');
      const result = await generateViewPagePDF(procedure, practice);
      
      console.log('PDF generation result:', result);
      console.log('=== PRINT DEBUG END ===');
      
      if (result) {
        toast({
          title: "Success",
          description: `PDF for ${procedure.procedureName} downloaded successfully`,
          variant: "default",
        });
      } else {
        throw new Error('PDF generation returned false');
      }
    } catch (err) {
      console.error('=== PRINT ERROR ===');
      console.error('Print procedure error:', err);
      console.error('Error stack:', err.stack);
      console.error('===================');
      
      toast({
        title: "Error", 
        description: "Failed to generate PDF: " + (err.message || 'Unknown error'),
        variant: "destructive",
      });
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-8">
          <Button 
            onClick={() => navigate('/add-patient')}
            className="bg-blue-600 hover:bg-blue-700 text-white h-20 flex flex-col"
          >
            <Plus className="h-6 w-6 mb-2" />
            Add Patient
          </Button>
          <Button 
            onClick={() => navigate('/assign-procedure')}
            variant="outline" 
            className="h-20 flex flex-col"
          >
            <FileText className="h-6 w-6 mb-2" />
            Assign Procedure
          </Button>
          <Button 
            onClick={() => navigate('/library')}
            variant="outline" 
            className="h-20 flex flex-col"
          >
            <FileText className="h-6 w-6 mb-2" />
            Procedure Library
          </Button>
          <Button 
            onClick={() => navigate('/add-staff')}
            variant="outline" 
            className="h-20 flex flex-col"
          >
            <Plus className="h-6 w-6 mb-2" />
            Add Dentist
          </Button>
          <Button 
            onClick={() => navigate('/request-procedure')}
            variant="outline" 
            className="h-20 flex flex-col"
          >
            <Plus className="h-6 w-6 mb-2" />
            Request Procedure
          </Button>
          <Button 
            onClick={() => navigate('/practice-settings')}
            variant="outline" 
            className="h-20 flex flex-col"
          >
            <Settings className="h-6 w-6 mb-2" />
            Practice Settings
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Patients */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center">
                  <Users className="h-5 w-5 mr-2 text-blue-600" />
                  All Patients
                </div>
                {selectedPatient && (
                  <Button 
                    size="sm" 
                    variant="outline" 
                    onClick={clearPatientSelection}
                    className="text-xs"
                  >
                    Clear Selection
                  </Button>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {dashboardData?.recentPatients?.length > 0 ? (
                <div className="space-y-4">
                  {dashboardData.recentPatients.map((patient) => (
                    <div 
                      key={patient.id} 
                      className={`flex justify-between items-center p-3 rounded-lg cursor-pointer transition-colors ${
                        selectedPatient?.id === patient.id 
                          ? 'bg-blue-100 border-2 border-blue-300' 
                          : 'bg-gray-50 hover:bg-gray-100'
                      }`}
                      onClick={() => selectPatient(patient)}
                    >
                      <div className="flex-1">
                        <p className="font-medium">{patient.firstName} {patient.lastName}</p>
                        <div className="text-sm text-gray-600">
                          {patient.email}
                        </div>
                        <p className="text-sm text-gray-500">
                          Added {new Date(patient.createdAt).toLocaleDateString()}
                        </p>
                        {patient.assignedDentistName && (
                          <p className="text-xs text-blue-600">
                            Assigned to: {patient.assignedDentistName}
                          </p>
                        )}
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/edit-patient/${patient.id}`);
                          }}
                          className="flex items-center space-x-1"
                        >
                          <Edit className="h-3 w-3" />
                          <span>Edit</span>
                        </Button>
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
                {selectedPatient ? `Procedures for ${selectedPatient.firstName} ${selectedPatient.lastName}` : 'Patient Procedures'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {selectedPatient ? (
                loadingProcedures ? (
                  <div className="flex items-center justify-center py-8">
                    <LoadingSpinner />
                  </div>
                ) : patientProcedures.length > 0 ? (
                  <div className="space-y-4">
                    {patientProcedures.map((procedure) => (
                      <div key={procedure.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <p className="font-medium">{procedure.procedureName}</p>
                          <p className="text-sm text-gray-600">Dr. {procedure.dentistName}</p>
                          <div className="flex items-center space-x-4 mt-2">
                            <Badge variant="outline">
                              {procedure.status}
                            </Badge>
                            <p className="text-xs text-gray-400">
                              {new Date(procedure.performedDate).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => viewProcedure(procedure)}
                            className="flex items-center space-x-1"
                          >
                            <Eye className="h-3 w-3" />
                            <span>View</span>
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => editProcedure(procedure)}
                            className="flex items-center space-x-1"
                          >
                            <Edit className="h-3 w-3" />
                            <span>Edit</span>
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => printProcedure(procedure)}
                            className="flex items-center space-x-1"
                          >
                            <Printer className="h-3 w-3" />
                            <span>Print</span>
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No procedures for this patient</p>
                    <p className="text-sm text-gray-500">Assign post-op care procedures</p>
                  </div>
                )
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Select a patient to view procedures</p>
                  <p className="text-sm text-gray-500">Click on a patient to see their assigned procedures</p>
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
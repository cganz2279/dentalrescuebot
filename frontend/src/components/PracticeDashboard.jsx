import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
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
  Search,
  X,
  UserPlus,
  Eye,
  User
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import LoadingSpinner, { LoadingCard, ErrorMessage } from './LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const PracticeDashboard = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [realPatients, setRealPatients] = useState([]);  // Store real patients separately
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPatientId, setSelectedPatientId] = useState(null);
  const [patientSearchTerm, setPatientSearchTerm] = useState('');
  const [procedureSearchTerm, setProcedureSearchTerm] = useState('');
  const { user, practice, logout } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleExportData = async () => {
    try {
      const response = await practiceApi.getExportData();
      const exportData = response.data;
      
      // Create CSV content
      let csvContent = "Patient Name,Email,Procedure,Performed Date,Dentist,Status,Notes\n";
      
      exportData.patients.forEach(patient => {
        if (patient.assignedProcedures && patient.assignedProcedures.length > 0) {
          patient.assignedProcedures.forEach(proc => {
            const row = [
              `"${patient.firstName} ${patient.lastName}"`,
              `"${patient.email}"`,
              `"${proc.procedureName}"`,
              `"${new Date(proc.performedDate).toLocaleDateString()}"`,
              `"${proc.dentistName}"`,
              `"${proc.status}"`,
              `"${proc.practiceNotes || ''}"`
            ].join(',');
            csvContent += row + "\n";
          });
        } else {
          // Patient with no procedures
          const row = [
            `"${patient.firstName} ${patient.lastName}"`,
            `"${patient.email}"`,
            `"No procedures assigned"`,
            `""`,
            `""`,
            `""`,
            `""`
          ].join(',');
          csvContent += row + "\n";
        }
      });
      
      // Create and download file
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `practice_data_${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast({
        title: "Export Complete",
        description: "Practice data has been exported to CSV file.",
        variant: "default",
      });
      
    } catch (error) {
      console.error('Export error:', error);
      toast({
        title: "Export Failed",
        description: "Failed to export data. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleOpenProcedure = (procedureId) => {
    // Navigate to procedure details page
    navigate(`/procedure-details/${procedureId}`);
  };

  const handleEditProcedure = (procedureId) => {
    console.log('🔧 handleEditProcedure called with ID:', procedureId);
    // Navigate to procedure details page where they can edit content
    navigate(`/procedure-details/${procedureId}`);
  };

  const handlePrintProcedure = async (procedureId) => {
    // Navigate directly to the procedure details page where they can see and print the clean format
    navigate(`/procedure-details/${procedureId}`);
  };

  const handlePatientClick = (patientId) => {
    // Toggle patient selection - if same patient clicked, deselect
    if (selectedPatientId === patientId) {
      setSelectedPatientId(null);
    } else {
      setSelectedPatientId(patientId);
    }
    // Clear search when patient is selected
    setPatientSearchTerm('');
    setProcedureSearchTerm('');
  };

  const handleClearFilters = () => {
    setSelectedPatientId(null);
    setPatientSearchTerm('');
    setProcedureSearchTerm('');
  };

  // Filter and sort real patients only - search by patient name or email
  const filteredRealPatients = realPatients?.filter(patient => {
    if (patientSearchTerm) {
      const searchLower = patientSearchTerm.toLowerCase();
      return (
        patient.firstName?.toLowerCase().includes(searchLower) ||
        patient.lastName?.toLowerCase().includes(searchLower) ||
        patient.email?.toLowerCase().includes(searchLower)
      );
    }
    return true; // Show all real patients when no search term
  })
  .sort((a, b) => {
    // Sort by last name alphabetically
    return a.lastName.localeCompare(b.lastName);
  }) || [];

  // Filter procedures based on selected patient and search term
  const filteredProcedures = dashboardData?.recentProcedures?.filter(procedure => {
    // Filter by selected patient
    if (selectedPatientId && procedure.patientId !== selectedPatientId) {
      return false;
    }
    
    // Filter by search term
    if (procedureSearchTerm) {
      const searchLower = procedureSearchTerm.toLowerCase();
      return (
        procedure.procedureName.toLowerCase().includes(searchLower) ||
        procedure.dentistName.toLowerCase().includes(searchLower) ||
        (procedure.patientName && procedure.patientName.toLowerCase().includes(searchLower))
      );
    }
    
    return true;
  }) || [];

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load dashboard data and real patients separately
      const [dashboardResponse, patientsResponse] = await Promise.all([
        practiceApi.getDashboard(),
        practiceApi.getPatients()
      ]);
      
      setDashboardData(dashboardResponse.data);
      
      // Filter for only Gmail patients (real patients)
      const gmailPatients = patientsResponse.data.filter(patient => 
        patient.email.toLowerCase().includes('@gmail.com')
      );
      
      // Add status to Gmail patients
      const gmailPatientsWithStatus = gmailPatients.map(patient => ({
        ...patient,
        status: patient.isActive !== false ? 'Active' : 'Inactive'
      }));
      
      setRealPatients(gmailPatientsWithStatus);
      
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-7 gap-4 mb-8">
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
            onClick={() => navigate('/procedure-library')}
            className="bg-purple-600 hover:bg-purple-700 text-white h-20 flex flex-col"
          >
            <FileText className="h-6 w-6 mb-2" />
            <span className="font-medium">Procedure Library</span>
            <span className="text-xs opacity-90">View & Print Docs</span>
          </Button>
          <Button 
            onClick={() => navigate('/practice-settings')}
            variant="outline" 
            className="h-20 flex flex-col"
          >
            <Settings className="h-6 w-6 mb-2" />
            Practice Settings
          </Button>
          <Button 
            onClick={() => navigate('/dentist-management')}
            className="bg-indigo-600 hover:bg-indigo-700 text-white h-20 flex flex-col"
          >
            <Users className="h-6 w-6 mb-2" />
            <span className="font-medium">Manage Dentists</span>
            <span className="text-xs opacity-90">Add & Edit Dentists</span>
          </Button>
          <Button 
            onClick={() => navigate('/patient-management')}
            className="bg-green-600 hover:bg-green-700 text-white h-20 flex flex-col"
          >
            <Users className="h-6 w-6 mb-2" />
            <span className="font-medium">Manage Patients</span>
            <span className="text-xs opacity-90">Search & View Records</span>
          </Button>
          <Button 
            onClick={handleExportData}
            variant="outline" 
            className="h-20 flex flex-col"
          >
            <Download className="h-6 w-6 mb-2" />
            <span className="font-medium">Export Data</span>
            <span className="text-xs text-gray-600">Download CSV</span>
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Patients */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <Users className="h-5 w-5 mr-2 text-blue-600" />
                  Recent Patients
                  {patientSearchTerm && (
                    <Badge variant="outline" className="ml-2">
                      Search: "{patientSearchTerm}"
                    </Badge>
                  )}
                </CardTitle>
                {patientSearchTerm && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPatientSearchTerm('')}
                    className="text-xs"
                  >
                    <X className="h-3 w-3 mr-1" />
                    Clear Search
                  </Button>
                )}
              </div>
              
              {/* Search Box */}
              <div className="relative mt-4">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Search patients by name or email..."
                  value={patientSearchTerm}
                  onChange={(e) => setPatientSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              
              {/* Filter Info */}
              <div className="flex items-center justify-between mt-3">
                <div className="text-sm text-gray-600">
                  Showing real patients only (Gmail addresses)
                </div>
                <div className="text-xs text-gray-500">
                  {filteredRealPatients.length} patients shown
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {filteredRealPatients.length > 0 ? (
                <div className="space-y-4">
                  {filteredRealPatients.map((patient) => (
                    <div 
                      key={patient.id} 
                      onClick={() => handlePatientClick(patient.id)}
                      className={`flex justify-between items-center p-4 rounded-lg cursor-pointer transition-colors border ${
                        selectedPatientId === patient.id 
                          ? 'bg-blue-100 border-2 border-blue-300' 
                          : 'bg-gray-50 hover:bg-gray-100'
                      }`}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-lg">{patient.firstName} {patient.lastName}</h4>
                          <Badge 
                            variant={patient.status === 'Active' ? 'default' : 'secondary'}
                            className={`text-xs ${
                              patient.status === 'Active' 
                                ? 'bg-green-100 text-green-800 border-green-200' 
                                : 'bg-gray-100 text-gray-600 border-gray-200'
                            }`}
                          >
                            {patient.status || 'Active'}
                          </Badge>
                          <Badge 
                            variant="outline" 
                            className="text-xs bg-blue-50 text-blue-600 border-blue-200"
                          >
                            Real Patient
                          </Badge>
                        </div>
                        
                        <div className="space-y-1 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <User className="h-4 w-4" />
                            <span>{patient.email}</span>
                          </div>
                          
                          {patient.lastLoginAt && (
                            <div className="flex items-center gap-1">
                              <Calendar className="h-4 w-4" />
                              <span>Last login: {new Date(patient.lastLoginAt).toLocaleDateString()}</span>
                            </div>
                          )}
                          
                          {patient.status === 'Inactive' && patient.deactivatedAt && (
                            <div className="flex items-center gap-1 text-red-600">
                              <AlertCircle className="h-4 w-4" />
                              <span>Deactivated: {new Date(patient.deactivatedAt).toLocaleDateString()}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center">
                        <div className={`flex items-center ${selectedPatientId === patient.id ? 'text-blue-600' : 'text-gray-400'}`}>
                          <Users className="h-5 w-5" />
                          {selectedPatientId === patient.id && (
                            <span className="ml-2 text-xs font-medium">Selected</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-lg mb-2">No patients found</p>
                  <p className="text-sm">
                    {patientSearchTerm 
                      ? `No patients match "${patientSearchTerm}"`
                      : "No real patients found"
                    }
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Procedures */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-green-600" />
                  Recent Procedures
                  {selectedPatientId && (
                    <Badge variant="outline" className="ml-2">
                      Patient Filtered
                    </Badge>
                  )}
                </CardTitle>
                {selectedPatientId && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleClearFilters}
                    className="text-xs"
                  >
                    <X className="h-3 w-3 mr-1" />
                    Clear Filter
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {filteredProcedures.length > 0 ? (
                <div className="space-y-4">
                  {filteredProcedures.map((procedure) => (
                    <div key={procedure.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <p className="font-medium">{procedure.procedureName}</p>
                        <p className="text-sm text-gray-600">
                          {procedure.dentistName && procedure.dentistName.startsWith('Dr.') 
                            ? procedure.dentistName 
                            : `Dr. ${procedure.dentistName}`}
                        </p>
                        <p className="text-xs text-gray-500">
                          Patient: {procedure.patientName || 'Unknown'}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="text-right mr-3">
                          <Badge variant="outline" className="mb-1">
                            {procedure.status}
                          </Badge>
                          <p className="text-xs text-gray-400">
                            {new Date(procedure.performedDate).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex flex-col space-y-1">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleOpenProcedure(procedure.id)}
                            className="text-xs px-2 py-1 h-7"
                          >
                            Open
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleEditProcedure(procedure.id)}
                            className="text-xs px-2 py-1 h-7"
                          >
                            Edit
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handlePrintProcedure(procedure.id)}
                            className="text-xs px-2 py-1 h-7"
                          >
                            Print
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  {selectedPatientId ? (
                    <div>
                      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p>No procedures found for selected patient</p>
                      <Button
                        onClick={() => navigate('/assign-procedure')}
                        className="mt-2"
                        size="sm"
                      >
                        Assign Procedure
                      </Button>
                    </div>
                  ) : (
                    <div>
                      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p>No procedures assigned yet</p>
                      <Button
                        onClick={() => navigate('/assign-procedure')}
                        className="mt-2"
                        size="sm"
                      >
                        Assign First Procedure
                      </Button>
                    </div>
                  )}
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
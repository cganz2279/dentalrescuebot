import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  FileText, 
  Calendar, 
  User, 
  Phone, 
  MapPin, 
  Download,
  Eye,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { patientsApi } from '../services/authApi';
import LoadingSpinner from './LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const PatientDashboard = () => {
  const navigate = useNavigate();
  const { user, practice } = useAuth();
  const { toast } = useToast();
  
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const response = await patientsApi.getDashboard();
      setDashboardData(response.data);
    } catch (error) {
      console.error('Dashboard load error:', error);
      toast({
        title: "Error",
        description: "Failed to load dashboard",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleViewProcedure = (assignmentId) => {
    navigate(`/patient/procedure/${assignmentId}`);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'expired':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <Clock className="h-4 w-4" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <p>No data available</p>
      </div>
    );
  }

  const { patient, practice: practiceInfo, assignedProcedures, stats } = dashboardData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {practiceInfo?.branding?.logo ? (
                <img 
                  src={practiceInfo.branding.logo} 
                  alt={practiceInfo.name}
                  className="h-12 w-12 rounded-full object-cover"
                />
              ) : (
                <div className="h-12 w-12 bg-blue-600 rounded-full flex items-center justify-center">
                  <User className="h-6 w-6 text-white" />
                </div>
              )}
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Welcome, {patient.firstName}!
                </h1>
                <p className="text-gray-600">
                  {practiceInfo?.name} - Post-Operative Care Portal
                </p>
              </div>
            </div>
            <Button
              variant="outline"
              onClick={() => {
                localStorage.removeItem('dentalToken');
                window.location.href = '/';
              }}
            >
              Sign Out
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <FileText className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Procedures</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalProcedures}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Active Procedures</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.activeProcedures}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Calendar className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Completed</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.completedProcedures}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Assigned Procedures */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="h-5 w-5 mr-2 text-blue-600" />
              Your Post-Operative Instructions
            </CardTitle>
          </CardHeader>
          <CardContent>
            {assignedProcedures.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No procedures assigned yet</h3>
                <p className="text-gray-600">
                  Your dental procedures and post-operative instructions will appear here.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {assignedProcedures.map((assignment) => (
                  <div
                    key={assignment.id}
                    className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => handleViewProcedure(assignment.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {assignment.procedureDetails?.name || assignment.procedureName}
                          </h3>
                          <Badge className={getStatusColor(assignment.status)}>
                            <div className="flex items-center space-x-1">
                              {getStatusIcon(assignment.status)}
                              <span className="capitalize">{assignment.status}</span>
                            </div>
                          </Badge>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                          <div className="flex items-center">
                            <Calendar className="h-4 w-4 mr-2" />
                            Performed: {formatDate(assignment.performedDate)}
                          </div>
                          <div className="flex items-center">
                            <User className="h-4 w-4 mr-2" />
                            Dr. {assignment.dentistName}
                          </div>
                          {assignment.followUpDate && (
                            <div className="flex items-center">
                              <Clock className="h-4 w-4 mr-2" />
                              Follow-up: {formatDate(assignment.followUpDate)}
                            </div>
                          )}
                          <div className="flex items-center">
                            <Eye className="h-4 w-4 mr-2" />
                            Viewed {assignment.viewCount || 0} times
                          </div>
                        </div>

                        {assignment.practiceNotes && (
                          <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                            <p className="text-sm text-blue-900">
                              <strong>Practice Notes:</strong> {assignment.practiceNotes}
                            </p>
                          </div>
                        )}
                      </div>
                      
                      <div className="ml-4">
                        <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                          <Eye className="h-4 w-4 mr-2" />
                          View Instructions
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Practice Contact Info */}
        {practiceInfo && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Phone className="h-5 w-5 mr-2 text-green-600" />
                Contact Your Practice
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center">
                  <Phone className="h-5 w-5 text-green-600 mr-3" />
                  <div>
                    <p className="font-medium">Phone</p>
                    <p className="text-gray-600">{practiceInfo.phone}</p>
                  </div>
                </div>
                {practiceInfo.address && (
                  <div className="flex items-start">
                    <MapPin className="h-5 w-5 text-green-600 mr-3 mt-1" />
                    <div>
                      <p className="font-medium">Address</p>
                      <p className="text-gray-600">
                        {practiceInfo.address.street}<br />
                        {practiceInfo.address.city}, {practiceInfo.address.state} {practiceInfo.address.zipCode}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default PatientDashboard;
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  FileText, 
  Download, 
  Calendar, 
  Stethoscope,
  Phone,
  Mail,
  Clock,
  AlertCircle,
  Heart,
  User
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { authApi } from '../services/authApi';
import LoadingSpinner, { LoadingCard, ErrorMessage } from './LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const PatientDashboard = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user, logout } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await authApi.getPatientDashboard();
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

  const practice = dashboardData?.practice;
  const patient = dashboardData?.patient;
  const assignedProcedures = dashboardData?.assignedProcedures || [];
  const stats = dashboardData?.stats;

  // Use practice branding colors if available
  const primaryColor = practice?.branding?.primaryColor || '#2563eb';
  const secondaryColor = practice?.branding?.secondaryColor || '#1e40af';

  const handleViewProcedure = (procedureId) => {
    // Navigate to procedure detail page with patient context
    navigate(`/procedure/${procedureId}`);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not specified';
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
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
              {/* Practice Logo or Default Logo */}
              {practice?.branding?.logo ? (
                <img 
                  src={practice.branding.logo}
                  alt={`${practice.name} Logo`}
                  className="h-12 w-auto"
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              ) : (
                <img 
                  src="https://customer-assets.emergentagent.com/job_dental-healing/artifacts/j7ayzg7r_DentalRescueBotWithRoundedText.png"
                  alt="DentalRescueBot Logo"
                  className="h-12 w-auto"
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              )}
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {practice?.name || 'Post-Operative Care Portal'}
                </h1>
                <p className="text-gray-600">
                  Welcome, {patient?.firstName}!
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" onClick={logout}>
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Welcome Message */}
      {practice?.branding?.welcomeMessage && (
        <div className="bg-blue-50 border-b">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center space-x-3">
              <Heart className="h-5 w-5 text-blue-600" />
              <p className="text-blue-800">{practice.branding.welcomeMessage}</p>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Your Procedures</CardTitle>
              <FileText className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.totalProcedures || 0}</div>
              <p className="text-xs text-gray-600">Total assigned</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Care</CardTitle>
              <Clock className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.activeProcedures || 0}</div>
              <p className="text-xs text-gray-600">Currently in care</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Practice Contact</CardTitle>
              <Phone className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-sm font-semibold">{practice?.phone || 'Contact practice'}</div>
              <p className="text-xs text-gray-600">For emergencies</p>
            </CardContent>
          </Card>
        </div>

        {/* Assigned Procedures */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="h-5 w-5 mr-2" style={{ color: primaryColor }} />
              Your Post-Operative Care Instructions
            </CardTitle>
            <p className="text-gray-600">
              Review your personalized care instructions and follow the recommended guidelines
            </p>
          </CardHeader>
          <CardContent>
            {assignedProcedures.length > 0 ? (
              <div className="space-y-4">
                {assignedProcedures.map((assignment) => (
                  <div key={assignment.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg text-gray-900">
                          {assignment.procedureName}
                        </h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                          <div className="flex items-center space-x-1">
                            <Stethoscope className="h-4 w-4" />
                            <span>Dr. {assignment.dentistName}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Calendar className="h-4 w-4" />
                            <span>Performed: {formatDate(assignment.performedDate)}</span>
                          </div>
                        </div>
                      </div>
                      <Badge className={getStatusColor(assignment.status)}>
                        {assignment.status?.toUpperCase() || 'ACTIVE'}
                      </Badge>
                    </div>

                    {assignment.practiceNotes && (
                      <div className="mb-3 p-3 bg-blue-50 rounded-md">
                        <p className="text-sm text-blue-800">
                          <strong>Special Notes:</strong> {assignment.practiceNotes}
                        </p>
                      </div>
                    )}

                    {assignment.followUpDate && (
                      <div className="mb-3 flex items-center text-sm text-amber-700">
                        <Calendar className="h-4 w-4 mr-1" />
                        <span>Follow-up scheduled: {formatDate(assignment.followUpDate)}</span>
                      </div>
                    )}

                    <div className="flex justify-between items-center">
                      <div className="text-xs text-gray-500">
                        Assigned {formatDate(assignment.createdAt)}
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          onClick={() => handleViewProcedure(assignment.procedureId)}
                          size="sm"
                          style={{ backgroundColor: primaryColor }}
                          className="text-white hover:opacity-90"
                        >
                          <FileText className="h-4 w-4 mr-1" />
                          View Instructions
                        </Button>
                        <Button
                          onClick={() => {
                            // TODO: Implement PDF download
                            toast({
                              title: "Coming Soon",
                              description: "PDF download will be available soon.",
                              variant: "default",
                            });
                          }}
                          variant="outline"
                          size="sm"
                        >
                          <Download className="h-4 w-4 mr-1" />
                          Download PDF
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  No Procedures Assigned Yet
                </h3>
                <p className="text-gray-600 mb-4">
                  Your dentist hasn't assigned any post-operative care instructions yet.
                </p>
                <p className="text-sm text-gray-500">
                  Contact your practice if you're expecting care instructions.
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Emergency Contact Info */}
        <Card className="mt-8 border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-600 mr-3" />
              <div className="flex-1">
                <h3 className="font-semibold text-red-900">Emergency Contact</h3>
                <p className="text-red-800 text-sm">
                  For urgent dental concerns, contact {practice?.name || 'your practice'} immediately
                </p>
              </div>
              <div className="text-right">
                <div className="flex flex-col space-y-1">
                  {practice?.phone && (
                    <div className="flex items-center space-x-1 text-red-800">
                      <Phone className="h-4 w-4" />
                      <span className="font-semibold">{practice.phone}</span>
                    </div>
                  )}
                  {practice?.email && (
                    <div className="flex items-center space-x-1 text-red-800">
                      <Mail className="h-4 w-4" />
                      <span className="text-sm">{practice.email}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PatientDashboard;
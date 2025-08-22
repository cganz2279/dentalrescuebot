import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { ArrowLeft, FileText, Clock, CheckCircle, XCircle, Eye } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const AdminRequestsPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    try {
      setLoading(true);
      // This would call an admin API to get all procedure requests
      // For now, we'll show mock data
      const mockRequests = [
        {
          id: '1',
          procedureName: 'Complex Wisdom Tooth Extraction',
          specialty: 'Oral Surgery',
          description: 'Need post-op instructions for impacted wisdom tooth removal with bone removal',
          requestType: 'new',
          urgency: 'high',
          status: 'pending',
          practiceName: 'Dental Excellence',
          requestedByName: 'Dr. Smith',
          createdAt: new Date().toISOString()
        },
        {
          id: '2',
          procedureName: 'Custom Crown Prep Instructions',
          specialty: 'Prosthodontics',
          description: 'My custom post-op instructions for crown preparation',
          requestType: 'custom',
          customInstructions: 'After crown preparation: 1. Avoid sticky foods 2. Use temporary crown carefully...',
          urgency: 'normal',
          status: 'in_review',
          practiceName: 'Family Dental Care',
          requestedByName: 'Dr. Johnson',
          createdAt: new Date(Date.now() - 86400000).toISOString()
        }
      ];
      
      setRequests(mockRequests);
    } catch (err) {
      setError('Failed to load requests');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'in_review': return 'bg-blue-100 text-blue-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'completed': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'urgent': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'normal': return 'bg-blue-100 text-blue-800';
      case 'low': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleStatusChange = async (requestId, newStatus) => {
    try {
      // Here you would call an API to update the status
      toast({
        title: "Status Updated",
        description: `Request status changed to ${newStatus}`,
        variant: "default",
      });
      
      // Update local state
      setRequests(prev => prev.map(req => 
        req.id === requestId ? { ...req, status: newStatus } : req
      ));
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to update status",
        variant: "destructive",
      });
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
              <h1 className="text-2xl font-bold text-gray-900">Procedure Requests</h1>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {error && (
          <Alert className="border-red-200 bg-red-50 mb-6">
            <AlertDescription className="text-red-800">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {requests.length > 0 ? (
          <div className="space-y-6">
            {requests.map((request) => (
              <Card key={request.id} className="border-l-4 border-l-blue-500">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <CardTitle className="flex items-center text-lg">
                        <FileText className="h-5 w-5 mr-2 text-blue-600" />
                        {request.procedureName}
                      </CardTitle>
                      <div className="flex items-center space-x-4 mt-2">
                        <Badge className={getStatusColor(request.status)}>
                          {request.status.toUpperCase()}
                        </Badge>
                        <Badge className={getUrgencyColor(request.urgency)}>
                          {request.urgency.toUpperCase()} PRIORITY
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {request.specialty}
                        </span>
                      </div>
                    </div>
                    <div className="text-right text-sm text-gray-500">
                      <div>{request.practiceName}</div>
                      <div>{request.requestedByName}</div>
                      <div>{new Date(request.createdAt).toLocaleDateString()}</div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Description:</h4>
                      <p className="text-gray-700">{request.description}</p>
                    </div>
                    
                    {request.requestType === 'custom' && request.customInstructions && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">Custom Instructions:</h4>
                        <div className="bg-gray-50 p-3 rounded-md">
                          <p className="text-gray-700 whitespace-pre-wrap">{request.customInstructions}</p>
                        </div>
                      </div>
                    )}

                    <div className="flex justify-between items-center pt-4 border-t">
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">
                          {request.requestType === 'new' ? 'New Procedure Request' : 'Custom Instructions'}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          onClick={() => handleStatusChange(request.id, 'in_review')}
                          size="sm"
                          variant="outline"
                          disabled={request.status === 'in_review'}
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          Review
                        </Button>
                        <Button
                          onClick={() => handleStatusChange(request.id, 'approved')}
                          size="sm"
                          className="bg-green-600 hover:bg-green-700 text-white"
                          disabled={request.status === 'approved' || request.status === 'completed'}
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Approve
                        </Button>
                        <Button
                          onClick={() => handleStatusChange(request.id, 'rejected')}
                          size="sm"
                          variant="destructive"
                          disabled={request.status === 'rejected'}
                        >
                          <XCircle className="h-4 w-4 mr-1" />
                          Reject
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="text-center py-12">
              <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No Procedure Requests
              </h3>
              <p className="text-gray-600">
                No procedure requests have been submitted yet.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default AdminRequestsPage;
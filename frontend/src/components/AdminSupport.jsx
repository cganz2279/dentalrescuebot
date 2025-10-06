import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  MessageCircle, 
  RefreshCw, 
  Calendar, 
  Clock, 
  Mail, 
  Phone, 
  CheckCircle2,
  AlertCircle,
  Building2,
  User
} from 'lucide-react';
import { adminApi } from '../services/authApi';
import { useToast } from '../hooks/use-toast';
import LoadingSpinner from './LoadingSpinner';

const AdminSupport = () => {
  const [supportRequests, setSupportRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { toast } = useToast();

  const loadSupportRequests = async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const requests = await adminApi.getAllSupportRequests();
      setSupportRequests(requests);
    } catch (error) {
      console.error('Failed to load support requests:', error);
      toast({
        title: "Loading Failed",
        description: "Could not load support requests. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadSupportRequests();
  }, []);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getRequestTypeDisplay = (request) => {
    const types = [];
    if (request.support) types.push('Support');
    if (request.suggestions) types.push('Suggestions');
    return types.join(' & ');
  };

  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'open':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800 border-yellow-200">Open</Badge>;
      case 'in-progress':
        return <Badge variant="secondary" className="bg-blue-100 text-blue-800 border-blue-200">In Progress</Badge>;
      case 'resolved':
        return <Badge variant="default" className="bg-green-100 text-green-800 border-green-200">Resolved</Badge>;
      case 'closed':
        return <Badge variant="outline">Closed</Badge>;
      default:
        return <Badge variant="secondary">Open</Badge>;
    }
  };

  const getPriorityIcon = (request) => {
    if (request.support && !request.suggestions) {
      return <AlertCircle className="h-4 w-4 text-red-500" title="Support Issue" />;
    }
    if (request.suggestions && !request.support) {
      return <CheckCircle2 className="h-4 w-4 text-blue-500" title="Suggestion" />;
    }
    return <MessageCircle className="h-4 w-4 text-purple-500" title="Mixed Request" />;
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <MessageCircle className="h-5 w-5 mr-2 text-blue-600" />
            All Support Requests
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner />
            <span className="ml-3 text-gray-600">Loading support requests...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="max-w-6xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center">
            <MessageCircle className="h-5 w-5 mr-2 text-blue-600" />
            All Support Requests ({supportRequests.length})
          </CardTitle>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => loadSupportRequests(true)}
            disabled={refreshing}
            className="flex items-center"
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </CardHeader>
      
      <CardContent>
        {supportRequests.length === 0 ? (
          <div className="text-center py-12">
            <MessageCircle className="h-16 w-16 mx-auto mb-4 text-gray-300" />
            <h3 className="text-xl font-medium text-gray-900 mb-2">No Support Requests</h3>
            <p className="text-gray-600">
              No support requests have been submitted yet.
            </p>
          </div>
        ) : (
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {supportRequests.map((request) => (
              <div 
                key={request.id} 
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    {getPriorityIcon(request)}
                    <div>
                      <h4 className="font-semibold text-gray-900 flex items-center">
                        <Building2 className="h-4 w-4 mr-2 text-gray-500" />
                        {request.practice_name}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {getRequestTypeDisplay(request)} Request
                      </p>
                    </div>
                    {getStatusBadge(request.status)}
                  </div>
                  <div className="text-xs text-gray-500">
                    ID: {request.id.slice(-8)}
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 text-sm">
                  <div className="flex items-center space-x-2 text-gray-600">
                    <Calendar className="h-4 w-4" />
                    <span>{formatDate(request.created_at)} at {formatTime(request.created_at)}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-gray-600">
                    <Mail className="h-4 w-4" />
                    <a 
                      href={`mailto:${request.email}?subject=Re: ${getRequestTypeDisplay(request)} Request #${request.id.slice(-8)}`}
                      className="text-blue-600 hover:text-blue-800 underline"
                    >
                      {request.email}
                    </a>
                  </div>
                  {request.phone && (
                    <div className="flex items-center space-x-2 text-gray-600">
                      <Phone className="h-4 w-4" />
                      <a 
                        href={`tel:${request.phone}`}
                        className="text-blue-600 hover:text-blue-800 underline"
                      >
                        {request.phone}
                      </a>
                    </div>
                  )}
                </div>
                
                <div className="bg-gray-50 rounded-lg p-3 mb-3">
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Description:</h5>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">
                    {request.description}
                  </p>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {request.support && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-red-100 text-red-800">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        Support Needed
                      </span>
                    )}
                    {request.suggestions && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        Feature Request
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => window.open(`mailto:${request.email}?subject=Re: ${getRequestTypeDisplay(request)} Request #${request.id.slice(-8)}&body=Hi ${request.practice_name},%0D%0A%0D%0AThank you for contacting our support team.%0D%0A%0D%0A`, '_blank')}
                    >
                      <Mail className="h-3 w-3 mr-1" />
                      Reply
                    </Button>
                    {request.phone && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => window.open(`tel:${request.phone}`, '_self')}
                      >
                        <Phone className="h-3 w-3 mr-1" />
                        Call
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {supportRequests.length > 0 && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start space-x-2">
              <CheckCircle2 className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <p className="text-sm text-blue-800 font-medium">
                  Support Request Management
                </p>
                <p className="text-sm text-blue-700 mt-1">
                  Click "Reply" to respond via email, or "Call" to contact directly. 
                  Remember to update customers on their request status.
                </p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default AdminSupport;
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  HelpCircle, 
  RefreshCw, 
  Calendar, 
  Clock, 
  Mail, 
  Phone, 
  MessageCircle,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { practiceApi } from '../services/authApi';
import { useToast } from '../hooks/use-toast';

const SupportHistory = () => {
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
      const requests = await practiceApi.getSupportRequests();
      setSupportRequests(requests);
    } catch (error) {
      console.error('Failed to load support requests:', error);
      toast({
        title: "Loading Failed",
        description: "Could not load support history. Please try again.",
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
      month: 'long',
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

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <HelpCircle className="h-5 w-5 mr-2 text-blue-600" />
            Support History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2 text-gray-600">Loading support history...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center">
            <HelpCircle className="h-5 w-5 mr-2 text-blue-600" />
            Support History
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
          <div className="text-center py-8">
            <HelpCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Support Requests</h3>
            <p className="text-gray-600">
              You haven't submitted any support requests yet. Use the "Get Help" button to contact our support team.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {supportRequests.map((request) => (
              <div 
                key={request.id} 
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <MessageCircle className="h-5 w-5 text-blue-600" />
                    <h4 className="font-medium text-gray-900">
                      {getRequestTypeDisplay(request)} Request
                    </h4>
                    {getStatusBadge(request.status)}
                  </div>
                  <div className="text-xs text-gray-500">
                    ID: {request.id.slice(-8)}
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Calendar className="h-4 w-4" />
                    <span>{formatDate(request.created_at)}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Clock className="h-4 w-4" />
                    <span>{formatTime(request.created_at)}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Mail className="h-4 w-4" />
                    <span>{request.email}</span>
                  </div>
                  {request.phone && (
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Phone className="h-4 w-4" />
                      <span>{request.phone}</span>
                    </div>
                  )}
                </div>
                
                <div className="bg-gray-50 rounded-lg p-3">
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Description:</h5>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">
                    {request.description}
                  </p>
                </div>
                
                <div className="mt-3 flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {request.support && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-red-100 text-red-800">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        Support
                      </span>
                    )}
                    {request.suggestions && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        Suggestions
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-gray-500">
                    Submitted {new Date(request.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SupportHistory;
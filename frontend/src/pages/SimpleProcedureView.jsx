import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { ArrowLeft, FileText, Calendar, User, Clock, Download } from 'lucide-react';
import { practiceApi } from '../services/authApi';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const SimpleProcedureView = () => {
  const { procedureId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [procedure, setProcedure] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProcedureData();
  }, [procedureId]);

  const loadProcedureData = async () => {
    try {
      setLoading(true);
      // Try to get procedure assignment data
      const response = await practiceApi.getProcedureAssignment(procedureId);
      
      if (response.success) {
        setProcedure(response.data);
      } else {
        setError('Procedure not found');
      }
    } catch (err) {
      console.error('Failed to load procedure:', err);
      setError('Failed to load procedure data');
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = async () => {
    if (!procedure) return;
    
    try {
      // Format procedure data for PDF generation
      const formattedProcedure = {
        name: procedure.procedureName || 'Unknown Procedure',
        specialtyName: 'Post-Operative Care',
        description: 'Post-operative care instructions for ' + procedure.procedureName,
        duration: 'As prescribed',
        difficulty: 'Standard',
        materials: [],
        instructions: procedure.customInstructions || [
          'Follow all post-operative care instructions carefully',
          'Take prescribed medications as directed',
          'Contact office if you experience any complications'
        ],
        warnings: ['Contact your dental office if you experience severe pain, swelling, or bleeding'],
        recoveryTimeline: [
          { day: 1, activity: 'Rest and follow post-op instructions' },
          { day: 2, activity: 'Light activity as tolerated' },
          { day: 7, activity: 'Follow-up appointment if scheduled' }
        ],
        medications: ['Take medications as prescribed by your dentist']
      };

      const { generateProcedurePDF } = await import('../utils/pdfGenerator');
      const result = await generateProcedurePDF(formattedProcedure);
      
      if (result) {
        toast({
          title: "Success",
          description: "Procedure PDF downloaded successfully",
          variant: "default",
        });
      } else {
        throw new Error('PDF generation failed');
      }
    } catch (err) {
      console.error('Print error:', err);
      toast({
        title: "Error", 
        description: "Failed to generate PDF: " + (err.message || 'Unknown error'),
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (error || !procedure) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Dashboard</span>
              </Button>
            </div>
          </div>
        </div>
        <div className="max-w-4xl mx-auto py-8 px-4 text-center">
          <p className="text-red-600">{error || 'Procedure not found'}</p>
        </div>
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
                onClick={() => navigate('/')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Dashboard</span>
              </Button>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-gray-600" />
                <h1 className="text-xl font-semibold text-gray-900">Procedure Details</h1>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileText className="h-6 w-6 text-blue-600" />
              <span>Procedure Information</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Procedure ID</h3>
                  <p className="text-lg">{procedureId}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Status</h3>
                  <Badge variant="outline">Active</Badge>
                </div>
              </div>

              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <Calendar className="h-5 w-5 mr-2 text-green-600" />
                  Post-Operative Instructions
                </h3>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-blue-800">
                    This is a placeholder for the detailed procedure information. 
                    The procedure view functionality is being developed.
                  </p>
                  <ul className="mt-3 space-y-1 text-blue-700">
                    <li>• Follow all post-operative care instructions</li>
                    <li>• Take prescribed medications as directed</li>
                    <li>• Contact office if you experience any complications</li>
                    <li>• Attend follow-up appointments as scheduled</li>
                  </ul>
                </div>
              </div>

              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <User className="h-5 w-5 mr-2 text-purple-600" />
                  Contact Information
                </h3>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-700">
                    For questions or concerns about this procedure, please contact your dental office 
                    during regular business hours or follow the emergency contact instructions provided.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SimpleProcedureView;
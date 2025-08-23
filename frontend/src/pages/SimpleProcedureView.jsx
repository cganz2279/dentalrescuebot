import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { ArrowLeft, FileText, Calendar, User, Clock, Download, AlertTriangle } from 'lucide-react';
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
    if (procedureId) {
      loadProcedureData();
    }
  }, [procedureId]);

  const loadProcedureData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to get procedure assignment data
      const response = await practiceApi.getProcedureAssignment(procedureId);
      
      if (response.success && response.data) {
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
                <h1 className="text-xl font-semibold text-gray-900">{procedure.procedureName}</h1>
              </div>
            </div>
            <Button onClick={handlePrint} className="flex items-center space-x-2">
              <Download className="h-4 w-4" />
              <span>Download PDF</span>
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* Procedure Info */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-6 w-6 text-blue-600" />
                <span>Procedure Information</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Procedure Name</h3>
                  <p className="text-lg font-semibold">{procedure.procedureName}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Performing Dentist</h3>
                  <p className="text-lg">Dr. {procedure.dentistName}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Performed Date</h3>
                  <p className="text-lg flex items-center">
                    <Calendar className="h-4 w-4 mr-2 text-green-600" />
                    {new Date(procedure.performedDate).toLocaleDateString()}
                  </p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Status</h3>
                  <Badge variant="outline" className="text-green-600 border-green-600">
                    {procedure.status || 'Active'}
                  </Badge>
                </div>

                {procedure.followUpDate && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Follow-up Date</h3>
                    <p className="text-lg flex items-center">
                      <Clock className="h-4 w-4 mr-2 text-orange-600" />
                      {new Date(procedure.followUpDate).toLocaleDateString()}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Practice Notes */}
          {procedure.practiceNotes && procedure.practiceNotes.trim() && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="h-5 w-5 text-purple-600" />
                  <span>Practice Notes</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <p className="text-purple-800 whitespace-pre-wrap">{procedure.practiceNotes}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Custom Instructions */}
          {procedure.customInstructions && procedure.customInstructions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <FileText className="h-5 w-5 text-blue-600" />
                  <span>Custom Post-Operative Instructions</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <ul className="space-y-2">
                    {procedure.customInstructions.map((instruction, index) => (
                      <li key={index} className="flex items-start space-x-2 text-blue-800">
                        <span className="font-bold text-blue-600">•</span>
                        <span>{instruction}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Comprehensive Post-Operative Care Instructions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-green-600" />
                <span>Detailed Post-Operative Care Instructions</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Immediate Aftercare */}
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                    <Clock className="h-4 w-4 mr-2 text-red-600" />
                    Immediate Aftercare (First 24 Hours)
                  </h4>
                  <div className="bg-red-50 p-4 rounded-lg">
                    <ul className="space-y-2 text-red-800">
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Apply ice to the treated area for 15 minutes every hour for the first 24 hours to reduce swelling</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Keep gauze in place for 30-60 minutes after treatment, then remove gently</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Do not rinse or spit forcefully for the first 24 hours</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Take prescribed medications as directed by your dentist</span>
                      </li>
                    </ul>
                  </div>
                </div>

                {/* Diet Instructions */}
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                    <User className="h-4 w-4 mr-2 text-orange-600" />
                    Diet and Eating Instructions
                  </h4>
                  <div className="bg-orange-50 p-4 rounded-lg">
                    <ul className="space-y-2 text-orange-800">
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-orange-600">•</span>
                        <span>Stick to soft foods for the first 24-48 hours (yogurt, soup, mashed potatoes)</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-orange-600">•</span>
                        <span>Avoid hot liquids and foods until numbness wears off</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-orange-600">•</span>
                        <span>No alcohol while taking prescribed medications</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-orange-600">•</span>
                        <span>Avoid using straws for the first few days to prevent dry socket</span>
                      </li>
                    </ul>
                  </div>
                </div>

                {/* Medication Instructions */}
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                    <Calendar className="h-4 w-4 mr-2 text-blue-600" />
                    Medication Guidelines
                  </h4>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <ul className="space-y-2 text-blue-800">
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-blue-600">•</span>
                        <span>Take all prescribed medications exactly as directed</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-blue-600">•</span>
                        <span>Complete the full course of antibiotics if prescribed</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-blue-600">•</span>
                        <span>Use over-the-counter pain relief as recommended (ibuprofen, acetaminophen)</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-blue-600">•</span>
                        <span>Do not exceed recommended dosages of any medication</span>
                      </li>
                    </ul>
                  </div>
                </div>

                {/* Warning Signs */}
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                    <AlertTriangle className="h-4 w-4 mr-2 text-red-600" />
                    ⚠️ When to Contact Your Dentist Immediately
                  </h4>
                  <div className="bg-red-100 border-l-4 border-red-500 p-4 rounded-lg">
                    <ul className="space-y-2 text-red-900">
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Severe or worsening pain after 48 hours</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Excessive bleeding that does not stop with gentle pressure</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Signs of infection: fever, excessive swelling, pus, or foul taste</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Numbness that persists beyond the expected timeframe</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Difficulty swallowing or breathing</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* General Care Instructions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calendar className="h-5 w-5 text-green-600" />
                <span>General Post-Operative Care</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-green-50 p-4 rounded-lg">
                <ul className="space-y-2 text-green-800">
                  <li className="flex items-start space-x-2">
                    <span className="font-bold text-green-600">•</span>
                    <span>Follow all post-operative care instructions carefully</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="font-bold text-green-600">•</span>
                    <span>Take prescribed medications as directed</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="font-bold text-green-600">•</span>
                    <span>Contact office if you experience any complications</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="font-bold text-green-600">•</span>
                    <span>Attend follow-up appointments as scheduled</span>
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Contact Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <User className="h-5 w-5 text-gray-600" />
                <span>Contact Information</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-700">
                  For questions or concerns about this procedure, please contact your dental office 
                  during regular business hours or follow the emergency contact instructions provided.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default SimpleProcedureView;
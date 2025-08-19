import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { ArrowLeft, FileText, User, Calendar, Download, Edit, Printer } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../hooks/use-toast';
import { generateProcedurePDF } from '../utils/pdfGenerator';

const ProcedureDetailsPage = () => {
  const { procedureId } = useParams();
  const navigate = useNavigate();
  const { practice } = useAuth();
  const { toast } = useToast();
  
  const [procedureData, setProcedureData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProcedureDetails();
  }, [procedureId]);

  const loadProcedureDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch real procedure assignment data
      const response = await practiceApi.getProcedureAssignment(procedureId);
      const data = response.data;
      
      // Transform the data to match our component structure
      const transformedData = {
        id: data.assignment.id,
        procedureName: data.assignment.procedureName,
        patientName: data.patient ? `${data.patient.firstName} ${data.patient.lastName}` : 'Unknown Patient',
        patientEmail: data.patient ? data.patient.email : '',
        dentistName: data.assignment.dentistName,
        performedDate: data.assignment.performedDate.split('T')[0], // Extract date part
        followUpDate: data.assignment.followUpDate ? data.assignment.followUpDate.split('T')[0] : null,
        status: data.assignment.status,
        practiceNotes: data.assignment.practiceNotes,
        customInstructions: data.assignment.customInstructions || [],
        procedureDetails: {
          specialty: data.procedure.specialtyName,
          duration: data.procedure.duration,
          overview: data.procedure.overview,
          immediateAftercare: data.procedure.immediateAftercare || [],
          dietRestrictions: data.procedure.dietRestrictions || [],
          warningSignsToCallDoctor: data.procedure.warningSignsToCallDoctor || [],
          recoveryTimeline: data.procedure.recoveryTimeline || [],
          medications: data.procedure.medications || []
        }
      };
      
      setProcedureData(transformedData);
    } catch (err) {
      console.error('Load procedure error:', err);
      setError(err.response?.data?.detail || 'Failed to load procedure details');
      toast({
        title: "Error",
        description: err.response?.data?.detail || "Failed to load procedure details",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePrintPDF = () => {
    if (procedureData && procedureData.procedureDetails) {
      const success = generateProcedurePDF({
        // Match the exact format from the procedure details page
        id: procedureData.id,
        name: procedureData.procedureName,
        specialty: procedureData.procedureDetails.specialty,
        specialtyName: procedureData.procedureDetails.specialty,
        overview: procedureData.procedureDetails.overview,
        immediateAftercare: procedureData.procedureDetails.immediateAftercare || [],
        dietRestrictions: procedureData.procedureDetails.dietRestrictions || [],
        warningSignsToCallDoctor: procedureData.procedureDetails.warningSignsToCallDoctor || [],
        recoveryTimeline: procedureData.procedureDetails.recoveryTimeline || [],
        medications: procedureData.procedureDetails.medications || [],
        // Assignment details - exactly as shown on the page
        patientName: procedureData.patientName,
        patientEmail: procedureData.patientEmail,
        dentistName: procedureData.dentistName,
        performedDate: new Date(procedureData.performedDate).toLocaleDateString(),
        followUpDate: procedureData.followUpDate ? new Date(procedureData.followUpDate).toLocaleDateString() : null,
        status: procedureData.status,
        practiceNotes: procedureData.practiceNotes,
        customInstructions: procedureData.customInstructions || [],
        // Practice info
        practiceName: practice?.name || 'Dental Practice',
        practicePhone: practice?.phone || '',
        practiceWebsite: practice?.website || ''
      });
      
      if (success) {
        toast({
          title: "PDF Generated",
          description: "Post-operative care document has been downloaded.",
          variant: "default",
        });
      } else {
        toast({
          title: "PDF Failed",
          description: "Failed to generate PDF. Please try again.",
          variant: "destructive",
        });
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (error || !procedureData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">
            <p className="text-red-600">{error || 'Procedure not found'}</p>
            <Button onClick={() => navigate('/')} className="mt-4">
              Back to Dashboard
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/')}
                className="flex items-center"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Procedure Details</h1>
                <p className="text-gray-600">
                  {procedureData.procedureName} for {procedureData.patientName}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                onClick={() => navigate(`/edit-procedure/${procedureId}`)}
                className="flex items-center"
              >
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
              <Button
                onClick={handlePrintPDF}
                className="bg-blue-600 hover:bg-blue-700 text-white flex items-center"
              >
                <Printer className="h-4 w-4 mr-2" />
                Print PDF
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Procedure Assignment Info */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="h-5 w-5 mr-2 text-blue-600" />
              Assignment Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Patient Details</h3>
                <p className="text-sm text-gray-600">
                  <User className="h-4 w-4 inline mr-2" />
                  {procedureData.patientName}
                </p>
                <p className="text-sm text-gray-600">{procedureData.patientEmail}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Treatment Details</h3>
                <p className="text-sm text-gray-600">
                  <Calendar className="h-4 w-4 inline mr-2" />
                  Performed: {new Date(procedureData.performedDate).toLocaleDateString()}
                </p>
                {procedureData.followUpDate && (
                  <p className="text-sm text-gray-600">
                    Follow-up: {new Date(procedureData.followUpDate).toLocaleDateString()}
                  </p>
                )}
                <p className="text-sm text-gray-600">Dentist: {procedureData.dentistName}</p>
                <Badge variant="outline" className="mt-2">{procedureData.status}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Practice Notes */}
        {procedureData.practiceNotes && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Practice Notes</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700">{procedureData.practiceNotes}</p>
            </CardContent>
          </Card>
        )}

        {/* Custom Instructions */}
        {procedureData.customInstructions && procedureData.customInstructions.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Custom Instructions</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-2">
                {procedureData.customInstructions.map((instruction, index) => (
                  <li key={index} className="text-gray-700">{instruction}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Procedure Details */}
        <Card>
          <CardHeader>
            <CardTitle>Post-Operative Care Instructions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Overview</h4>
                <p className="text-gray-700">{procedureData.procedureDetails.overview}</p>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Immediate Aftercare</h4>
                <ul className="list-disc list-inside space-y-1">
                  {procedureData.procedureDetails.immediateAftercare.map((instruction, index) => (
                    <li key={index} className="text-gray-700">{instruction}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="font-semibold text-red-600 mb-2">⚠️ Warning Signs - Call Your Dentist Immediately</h4>
                <ul className="list-disc list-inside space-y-1">
                  {procedureData.procedureDetails.warningSignsToCallDoctor.map((warning, index) => (
                    <li key={index} className="text-red-700">{warning}</li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ProcedureDetailsPage;
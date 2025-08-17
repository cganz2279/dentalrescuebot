import React, { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { 
  ArrowLeft, 
  Clock, 
  AlertTriangle, 
  Utensils, 
  Activity,
  Pill,
  Calendar,
  Phone,
  Download
} from 'lucide-react';
import LoadingSpinner, { ErrorMessage } from '../components/LoadingSpinner';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { dentalApi } from '../services/api';
import { generateProcedurePDF } from '../utils/pdfGenerator';
import { useToast } from '../hooks/use-toast';

const ProcedurePage = ({ procedureId, onBackToHome, onBackToSpecialty }) => {
  const [procedure, setProcedure] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { toast } = useToast();

  useEffect(() => {
    if (procedureId) {
      loadProcedure();
    }
  }, [procedureId]);

  const loadProcedure = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await dentalApi.getProcedure(procedureId);
      setProcedure(response.data);
    } catch (err) {
      setError(err.message);
      toast({
        title: "Error",
        description: "Failed to load procedure information. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = () => {
    const success = generateProcedurePDF(procedure);
    if (success) {
      toast({
        title: "PDF Generated",
        description: "Your post-operative care guide has been downloaded.",
        variant: "default",
      });
    } else {
      toast({
        title: "Download Failed",
        description: "Failed to generate PDF. Please try again.",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
        <Header 
          title="Loading..."
          subtitle="Loading procedure information..."
          showBackButton={true}
          onBackClick={onBackToHome}
          showBranding={false}
        />
        
        <div className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
          <div className="flex justify-center items-center py-32">
            <LoadingSpinner size="xl" />
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  if (error || !procedure) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full">
          <div className="flex items-center mb-4">
            <Button 
              variant="ghost" 
              onClick={onBackToHome}
              className="mr-4"
            >
              <ArrowLeft className="h-5 w-5" />
              Back to Home
            </Button>
          </div>
          <ErrorMessage 
            message={error || "Procedure not found"} 
            onRetry={loadProcedure}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <Button 
                variant="ghost" 
                onClick={onBackToHome}
                className="mr-4 p-2 hover:bg-gray-100 rounded-full"
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div className="flex-1">
                <Badge variant="secondary" className="mb-2">
                  {procedure.specialtyName}
                </Badge>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  {procedure.name}
                </h1>
                <p className="text-lg text-gray-600">
                  Post-Operative Care Guide
                </p>
              </div>
            </div>
            
            {/* PDF Download Button */}
            <Button 
              onClick={handleDownloadPDF}
              className="bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Download PDF
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* Overview */}
        <Card className="mb-8 border-l-4 border-l-blue-500">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="h-5 w-5 mr-2 text-blue-600" />
              Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 leading-relaxed">
              {procedure.overview}
            </p>
          </CardContent>
        </Card>

        {/* Emergency Alert */}
        <Alert className="mb-8 border-red-200 bg-red-50">
          <Phone className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <strong>Emergency:</strong> If you experience severe bleeding, difficulty breathing, 
            or signs of severe allergic reaction, call 911 immediately.
          </AlertDescription>
        </Alert>

        <div className="grid gap-8 lg:grid-cols-2">
          {/* Immediate Aftercare */}
          <Card className="border-l-4 border-l-green-500">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Activity className="h-5 w-5 mr-2 text-green-600" />
                Immediate Aftercare
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {procedure.immediateAftercare.map((instruction, index) => (
                  <li key={index} className="flex items-start">
                    <div className="w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-medium mr-3 mt-0.5 flex-shrink-0">
                      {index + 1}
                    </div>
                    <span className="text-gray-700">{instruction}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Diet Restrictions */}
          <Card className="border-l-4 border-l-orange-500">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Utensils className="h-5 w-5 mr-2 text-orange-600" />
                Diet Restrictions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {procedure.dietRestrictions.map((restriction, index) => (
                  <li key={index} className="flex items-start">
                    <div className="w-6 h-6 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center text-sm font-medium mr-3 mt-0.5 flex-shrink-0">
                      {index + 1}
                    </div>
                    <span className="text-gray-700">{restriction}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* Warning Signs */}
        <Card className="mt-8 border-l-4 border-l-red-500 bg-red-50">
          <CardHeader>
            <CardTitle className="flex items-center text-red-800">
              <AlertTriangle className="h-5 w-5 mr-2 text-red-600" />
              Warning Signs - Call Your Dentist
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-700 mb-4 font-medium">
              Contact your dental office immediately if you experience any of the following:
            </p>
            <ul className="space-y-2">
              {procedure.warningSignsToCallDoctor.map((sign, index) => (
                <li key={index} className="flex items-start">
                  <AlertTriangle className="h-4 w-4 text-red-500 mr-2 mt-1 flex-shrink-0" />
                  <span className="text-red-800">{sign}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <div className="grid gap-8 lg:grid-cols-2 mt-8">
          {/* Recovery Timeline */}
          <Card className="border-l-4 border-l-purple-500">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="h-5 w-5 mr-2 text-purple-600" />
                Recovery Timeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {procedure.recoveryTimeline.map((timeline, index) => (
                  <div key={index} className="flex items-start">
                    <div className="bg-purple-100 text-purple-600 px-3 py-1 rounded-full text-sm font-medium mr-4 flex-shrink-0">
                      Day {timeline.day}
                    </div>
                    <div className="flex-1">
                      <p className="text-gray-700 text-sm">{timeline.activity}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Medications */}
          <Card className="border-l-4 border-l-blue-500">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Pill className="h-5 w-5 mr-2 text-blue-600" />
                Medications
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {procedure.medications.map((medication, index) => (
                  <li key={index} className="flex items-start">
                    <Pill className="h-4 w-4 text-blue-500 mr-2 mt-1 flex-shrink-0" />
                    <span className="text-gray-700 text-sm">{medication}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-blue-800 text-sm">
                  <strong>Important:</strong> Always follow your dentist's specific medication instructions. 
                  These are general guidelines only.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Contact Information */}
        <Card className="mt-8 bg-gray-50 border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Phone className="h-5 w-5 mr-2 text-gray-600" />
              Need Help?
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">
              If you have questions about your recovery or need to speak with your dental team:
            </p>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="p-4 bg-white rounded-lg border">
                <h4 className="font-semibold text-gray-800 mb-2">Office Hours</h4>
                <p className="text-gray-600 text-sm">Contact your dental office during regular business hours</p>
              </div>
              <div className="p-4 bg-white rounded-lg border">
                <h4 className="font-semibold text-gray-800 mb-2">After Hours</h4>
                <p className="text-gray-600 text-sm">Follow your dentist's emergency contact instructions</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Footer */}
      <Footer />
    </div>
  );
};

export default ProcedurePage;
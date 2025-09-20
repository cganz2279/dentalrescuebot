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
import { generateProcedurePDF } from '../utils/rawOverviewOnly';
import { useToast } from '../hooks/use-toast';
import { useAuth } from '../contexts/AuthContext';

const ProcedurePage = ({ procedureId, onBackToHome, onBackToSpecialty }) => {
  const [procedure, setProcedure] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { toast } = useToast();
  const { practice } = useAuth();

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

  const handleDownloadPDF = async () => {
    try {
      toast({
        title: "Generating PDF...",
        description: "Please wait while we create your care guide.",
        variant: "default",
      });
      
      console.log('🏥 PDF Generation - Practice Context (ProcedurePage):', practice);
      console.log('📊 Practice officeHours:', practice?.officeHours);
      console.log('📞 Practice emergencyContact:', practice?.emergencyContact);
      
      // If practice data is not available, try to fetch it from dashboard API
      let practiceData = practice;
      if (!practice || !practice.officeHours || !practice.emergencyContact) {
        console.log('🔄 Practice data incomplete, fetching from dashboard API...');
        try {
          const practiceApi = (await import('../services/authApi')).practiceApi;
          const dashboardData = await practiceApi.getDashboard();
          
          if (dashboardData.success && dashboardData.data?.practice) {
            practiceData = dashboardData.data.practice;
            console.log('✅ Fetched complete practice data:', practiceData);
          } else {
            console.warn('⚠️ Dashboard fetch failed, using incomplete practice data');
          }
        } catch (error) {
          console.error('❌ Failed to fetch practice data from dashboard:', error);
        }
      }
      
      const procedureForPDF = {
        ...procedure,
        practiceName: practiceData?.name || 'Dental Practice',
        practiceAddress: practiceData?.address || practiceData?.location || '',
        practicePhone: practiceData?.phone || '',
        practiceWebsite: practiceData?.website || '',
        practiceOfficeHours: practiceData?.officeHours || '',
        practiceEmergencyContact: practiceData?.emergencyContact || ''
      };
      
      console.log('📄 Final procedure object for PDF (ProcedurePage):', {
        practiceName: procedureForPDF.practiceName,
        practiceOfficeHours: procedureForPDF.practiceOfficeHours,
        practiceEmergencyContact: procedureForPDF.practiceEmergencyContact
      });
      
      const success = await generateProcedurePDF(procedureForPDF);
      
      if (success) {
        toast({
          title: "PDF Downloaded",
          description: "Your post-operative care guide has been downloaded successfully.",
          variant: "default",
        });
      } else {
        toast({
          title: "Download Failed",
          description: "Failed to generate PDF. Please try again.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('PDF download error:', error);
      toast({
        title: "Download Error",
        description: "An error occurred while generating the PDF. Please try again.",
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
            <div className="text-gray-700 leading-relaxed">
              {procedure.overview.split('\n').map((line, index) => {
                const trimmedLine = line.trim();
                
                // Handle empty lines - create spacing
                if (trimmedLine === '') {
                  return <div key={index} className="mb-2"></div>;
                }
                
                // Handle bullet points
                if (trimmedLine.startsWith('•') || trimmedLine.startsWith('-')) {
                  const bulletText = trimmedLine.replace(/^[•-]\s*/, '');
                  return (
                    <div key={index} className="flex items-start mb-2 ml-4">
                      <span className="text-blue-600 mr-3 text-lg leading-none">•</span>
                      <span className="flex-1 text-gray-700">{bulletText}</span>
                    </div>
                  );
                }
                
                // Handle markdown-style headers - both single line and inline
                if (trimmedLine.includes('**')) {
                  // If it's a complete header (starts and ends with **)
                  if (trimmedLine.startsWith('**') && trimmedLine.endsWith('**') && trimmedLine.length > 4) {
                    const headerText = trimmedLine.replace(/\*\*/g, '');
                    return (
                      <h4 key={index} className="font-bold text-gray-900 mt-6 mb-3 text-lg">
                        {headerText}
                      </h4>
                    );
                  }
                  // Handle mixed content with headers inline
                  else {
                    const parts = trimmedLine.split(/(\*\*[^*]+\*\*)/);
                    return (
                      <p key={index} className="mb-3">
                        {parts.map((part, partIndex) => {
                          if (part.startsWith('**') && part.endsWith('**')) {
                            return (
                              <strong key={partIndex} className="font-semibold text-gray-900">
                                {part.replace(/\*\*/g, '')}
                              </strong>
                            );
                          }
                          return part;
                        })}
                      </p>
                    );
                  }
                }
                
                // Regular paragraphs - only if not empty
                if (trimmedLine.length > 0) {
                  return (
                    <p key={index} className="mb-3 text-gray-700 leading-relaxed">
                      {trimmedLine}
                    </p>
                  );
                }
                
                return null;
              }).filter(Boolean)}
            </div>
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
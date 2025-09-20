import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { 
  ArrowLeft, 
  Calendar, 
  User, 
  Clock, 
  AlertTriangle, 
  FileText, 
  Phone, 
  Download,
  Printer
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const PracticeProcedureView = () => {
  const { procedureId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { practice } = useAuth();
  
  const [procedure, setProcedure] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProcedure();
  }, [procedureId]);

  const loadProcedure = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/procedures/${procedureId}`);
      
      if (!response.ok) {
        throw new Error('Failed to load procedure');
      }
      
      const data = await response.json();
      setProcedure(data);
    } catch (error) {
      console.error('Load procedure error:', error);
      toast({
        title: "Error",
        description: "Failed to load procedure details",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = async () => {
    try {
      // FINAL RAW TEXT ONLY - CACHE BUSTED
      const { generateProcedurePDF } = await import('../utils/FINAL_RAW_TEXT_ONLY');
      
      if (!procedure) {
        console.error('No procedure data available for PDF generation');
        return;
      }

      // Prepare procedure data for PDF with practice information
      const procedureForPDF = {
        ...procedure,
        practiceName: practice?.name || 'Dental Practice',
        practiceAddress: practice?.address || practice?.location || '',
        practicePhone: practice?.phone || '',
        practiceWebsite: practice?.website || '',
        practiceOfficeHours: practice?.officeHours || '',
        practiceEmergencyContact: practice?.emergencyContact || '',
      };
      
      console.log('🏥 PracticeProcedureView - Generating PDF with practice data:', {
        practiceName: procedureForPDF.practiceName,
        practiceOfficeHours: procedureForPDF.practiceOfficeHours,
        practiceEmergencyContact: procedureForPDF.practiceEmergencyContact
      });

      const success = await generateProcedurePDF(procedureForPDF);
      
      if (success) {
        toast({
          title: "Success",
          description: "PDF generated successfully",
        });
      }
      
    } catch (error) {
      console.error('Print/PDF generation error:', error);
      toast({
        title: "Error",
        description: "Failed to generate PDF",
        variant: "destructive",
      });
      // Fallback to window.print if PDF generation fails
      window.print();
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (!procedure) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Procedure Not Found</h2>
          <p className="text-gray-600 mb-4">The requested procedure could not be found.</p>
          <Button onClick={() => navigate('/practice/library')}>
            Return to Library
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Print Styles */}
      <style>{`
        @media print {
          .no-print { display: none !important; }
          .print-only { display: block !important; }
          body { background: white !important; }
          .print-header { 
            display: flex !important; 
            align-items: center !important; 
            margin-bottom: 20px !important; 
            padding-bottom: 15px !important; 
            border-bottom: 2px solid #e5e7eb !important; 
          }
          .print-title { 
            font-size: 24px !important; 
            font-weight: bold !important; 
            margin-bottom: 10px !important; 
          }
        }
        .print-only { display: none; }
      `}</style>

      {/* Header - No Print */}
      <div className="bg-white shadow-sm border-b no-print">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/practice/library')}
                className="flex items-center"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Library
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Post-Operative Instructions
                </h1>
                <p className="text-gray-600">{practice?.name}</p>
              </div>
            </div>
            <Button onClick={handlePrint} className="bg-blue-600 hover:bg-blue-700">
              <Printer className="h-4 w-4 mr-2" />
              Print Instructions
            </Button>
          </div>
        </div>
      </div>

      {/* Print Header - Print Only */}
      <div className="print-only print-header max-w-4xl mx-auto px-4">
        {practice?.branding?.logo && (
          <img 
            src={practice.branding.logo} 
            alt={practice.name}
            className="h-16 w-16 rounded-lg object-cover mr-4"
          />
        )}
        <div>
          <h1 className="print-title">{practice?.name}</h1>
          {practice?.address && (
            <p className="text-gray-600">
              {practice.address.street}, {practice.address.city}, {practice.address.state} {practice.address.zipCode}
            </p>
          )}
          {practice?.phone && (
            <p className="text-gray-600">Phone: {practice.phone}</p>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Dental Rescue Notes Logo */}
        <div className="flex justify-center mb-6">
          <img 
            src="https://customer-assets.emergentagent.com/job_dental-portal-fix-1/artifacts/3xodewns_ChatGPT%20Image%20Sep%2018%2C%202025%2C%2004_21_15%20PM.png" 
            alt="Dental Rescue Notes"
            className="h-20 w-auto object-contain"
          />
        </div>
        {/* Procedure Header */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-2xl mb-2">{procedure.name}</CardTitle>
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <div className="flex items-center">
                    <Clock className="h-4 w-4 mr-2" />
                    Duration: {procedure.duration || 'Variable'}
                  </div>
                  <Badge className="bg-blue-100 text-blue-800">
                    {procedure.specialtyName || procedure.specialty}
                  </Badge>
                </div>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Overview Content */}
        {procedure.overview && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2 text-blue-600" />
                Post-Operative Care Instructions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose max-w-none">
                <div className="text-gray-700 text-base leading-relaxed whitespace-pre-wrap">
                  {procedure.overview}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Contact Information */}
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="flex items-center text-green-900">
              <Phone className="h-5 w-5 mr-2 text-green-600" />
              Contact Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold text-green-900">Emergency Contact</h4>
                <p className="text-green-800">
                  If you experience severe pain, excessive bleeding, or signs of infection, 
                  call immediately:
                </p>
                <p className="text-lg font-bold text-green-900 mt-2">
                  {practice?.phone || 'Contact your dental office'}
                </p>
              </div>
              {practice?.address && (
                <div>
                  <h4 className="font-semibold text-green-900">Office Address</h4>
                  <p className="text-green-800">
                    {practice.address.street}<br />
                    {practice.address.city}, {practice.address.state} {practice.address.zipCode}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PracticeProcedureView;
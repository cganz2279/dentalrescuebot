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
  Printer,
  CheckCircle,
  AlertCircle,
  Edit3,
  Save,
  X
} from 'lucide-react';
import { patientsApi } from '../services/authApi';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../hooks/use-toast';
import { useAuth } from '../contexts/AuthContext';

const PatientProcedureView = () => {
  const { assignmentId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [procedureData, setProcedureData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditingOverview, setIsEditingOverview] = useState(false);
  const [editedOverview, setEditedOverview] = useState('');
  const [savingOverview, setSavingOverview] = useState(false);

  useEffect(() => {
    loadProcedure();
  }, [assignmentId]);

  const loadProcedure = async () => {
    try {
      setLoading(true);
      const response = await patientsApi.getProcedure(assignmentId);
      setProcedureData(response.data);
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
      await patientsApi.trackDownload(assignmentId);
      
      // Generate proper PDF with Office Hours and Emergency Contact
      const { generateProcedurePDF } = await import('../utils/pdfGenerator');
      const { practice } = useAuth();
      
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
        // Include patient information
        patientName: procedure.patientName || 'Patient',
        patientEmail: procedure.patientEmail || '',
        dentistName: procedure.dentistName || '',
        performedDate: procedure.performedDate || '',
        followUpDate: procedure.followUpDate || null,
        status: procedure.status || '',
        practiceNotes: procedure.practiceNotes || '',
        customInstructions: procedure.customInstructions || []
      };
      
      console.log('🏥 PatientProcedureView - Generating PDF with practice data:', {
        practiceName: procedureForPDF.practiceName,
        practiceOfficeHours: procedureForPDF.practiceOfficeHours,
        practiceEmergencyContact: procedureForPDF.practiceEmergencyContact
      });

      await generateProcedurePDF(procedureForPDF);
      
    } catch (error) {
      console.error('Print tracking error:', error);
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

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'expired':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <Clock className="h-4 w-4" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (!procedureData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Procedure Not Found</h2>
          <p className="text-gray-600 mb-4">The requested procedure could not be found.</p>
          <Button onClick={() => navigate('/patient/dashboard')}>
            Return to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  const { assignment, procedure, practice } = procedureData;

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
                onClick={() => navigate('/patient/dashboard')}
                className="flex items-center"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
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
        {/* Procedure Header */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-2xl mb-2">{procedure.name}</CardTitle>
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <div className="flex items-center">
                    <Calendar className="h-4 w-4 mr-2" />
                    Performed: {formatDate(assignment.performedDate)}
                  </div>
                  <div className="flex items-center">
                    <User className="h-4 w-4 mr-2" />
                    {assignment.dentistName}
                  </div>
                  {assignment.followUpDate && (
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-2" />
                      Follow-up: {formatDate(assignment.followUpDate)}
                    </div>
                  )}
                </div>
              </div>
              <Badge className={getStatusColor(assignment.status)}>
                <div className="flex items-center space-x-1">
                  {getStatusIcon(assignment.status)}
                  <span className="capitalize">{assignment.status}</span>
                </div>
              </Badge>
            </div>
          </CardHeader>
        </Card>

        {/* Practice Notes */}
        {assignment.practiceNotes && (
          <Card className="mb-6 border-blue-200 bg-blue-50">
            <CardContent className="pt-6">
              <div className="flex items-start">
                <FileText className="h-5 w-5 text-blue-600 mr-3 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-blue-900 mb-2">Special Notes from Your Dentist</h3>
                  <p className="text-blue-800">{assignment.practiceNotes}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Custom Instructions */}
        {assignment.customInstructions && assignment.customInstructions.length > 0 && (
          <Card className="mb-6 border-green-200 bg-green-50">
            <CardContent className="pt-6">
              <div className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-600 mr-3 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-green-900 mb-2">Custom Instructions</h3>
                  <ul className="list-disc list-inside text-green-800 space-y-1">
                    {assignment.customInstructions.map((instruction, index) => (
                      <li key={index}>{instruction}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Overview */}
        {procedure.overview && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2 text-blue-600" />
                Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose max-w-none">
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
                  
                  // Regular paragraphs
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
        )}

        {/* Emergency Alert */}
        {procedure.emergencyAlert && (
          <Card className="mb-6 border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-start">
                <AlertTriangle className="h-6 w-6 text-red-600 mr-3 mt-0.5" />
                <div>
                  <h3 className="font-bold text-red-900 mb-2">⚠️ EMERGENCY ALERT</h3>
                  <p className="text-red-800 font-medium">{procedure.emergencyAlert}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Immediate Aftercare */}
        {procedure.immediateAftercare && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="h-5 w-5 mr-2 text-orange-600" />
                Immediate Aftercare (First 24 Hours)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside text-gray-700 space-y-2">
                {procedure.immediateAftercare.split('\n').map((item, index) => (
                  <li key={index}>{item.replace(/^[•\-\*]\s*/, '')}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Diet Restrictions */}
        {procedure.dietRestrictions && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center">
                <AlertCircle className="h-5 w-5 mr-2 text-yellow-600" />
                Diet Restrictions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside text-gray-700 space-y-2">
                {procedure.dietRestrictions.split('\n').map((item, index) => (
                  <li key={index}>{item.replace(/^[•\-\*]\s*/, '')}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Warning Signs */}
        {procedure.warningSigns && (
          <Card className="mb-6 border-red-200 bg-red-50">
            <CardHeader>
              <CardTitle className="flex items-center text-red-900">
                <AlertTriangle className="h-5 w-5 mr-2 text-red-600" />
                Warning Signs - Call Your Dentist Immediately
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside text-red-800 space-y-2">
                {procedure.warningSigns.split('\n').map((item, index) => (
                  <li key={index}>{item.replace(/^[•\-\*]\s*/, '')}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Recovery Timeline */}
        {procedure.recoveryTimeline && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="h-5 w-5 mr-2 text-green-600" />
                Recovery Timeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose max-w-none">
                {procedure.recoveryTimeline.split('\n').map((item, index) => (
                  <p key={index} className="text-gray-700 mb-2">{item}</p>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Medications */}
        {procedure.medications && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center">
                <AlertCircle className="h-5 w-5 mr-2 text-purple-600" />
                Medications & Pain Management
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside text-gray-700 space-y-2">
                {procedure.medications.split('\n').map((item, index) => (
                  <li key={index}>{item.replace(/^[•\-\*]\s*/, '')}</li>
                ))}
              </ul>
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

export default PatientProcedureView;
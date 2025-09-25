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
      // Initialize edited overview with current content
      if (response.data?.procedure?.overview) {
        setEditedOverview(response.data.procedure.overview);
      }
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

  // Function to save edited overview
  const saveOverview = async () => {
    try {
      setSavingOverview(true);
      
      // Call API to update procedure overview
      await patientsApi.updateProcedureOverview(procedureData.procedure.id, editedOverview);
      
      // Update local state
      setProcedureData(prev => ({
        ...prev,
        procedure: {
          ...prev.procedure,
          overview: editedOverview
        }
      }));
      
      setIsEditingOverview(false);
      
      toast({
        title: "Success",
        description: "Overview updated successfully",
      });
      
    } catch (error) {
      console.error('Save overview error:', error);
      toast({
        title: "Error",
        description: "Failed to save overview",
        variant: "destructive",
      });
    } finally {
      setSavingOverview(false);
    }
  };

  // Function to cancel editing
  const cancelEditing = () => {
    setEditedOverview(procedureData.procedure.overview);
    setIsEditingOverview(false);
  };

  // Function to format overview content into structured sections
  const formatOverviewContent = (overviewText) => {
    if (!overviewText) return null;

    const sections = [];
    
    // Split by section headers (Purpose:, First 24 Hours:, etc.)
    const sectionRegex = /(Purpose|First 24 Hours|Pain & Sensitivity|Oral Hygiene|Diet|Special Precautions|Follow-Up):\s*/g;
    let lastIndex = 0;
    let match;
    const matches = [];
    
    // Find all section headers
    while ((match = sectionRegex.exec(overviewText)) !== null) {
      matches.push({
        title: match[1],
        startIndex: match.index,
        headerEnd: match.index + match[0].length
      });
    }
    
    // Extract content for each section
    matches.forEach((currentMatch, index) => {
      const nextMatch = matches[index + 1];
      const endIndex = nextMatch ? nextMatch.startIndex : overviewText.length;
      
      const rawContent = overviewText.substring(currentMatch.headerEnd, endIndex).trim();
      
      if (rawContent) {
        // Parse content into items (handle bullet points and sentences)
        let contentItems = [];
        
        // Split by bullet points or sentences
        if (rawContent.includes(' - ')) {
          // Has bullet points
          const parts = rawContent.split(' - ');
          const intro = parts[0].trim();
          
          if (intro && !intro.match(/^-/)) {
            contentItems.push({ type: 'text', content: intro });
          }
          
          parts.slice(1).forEach(item => {
            if (item.trim()) {
              contentItems.push({ type: 'bullet', content: item.trim() });
            }
          });
        } else {
          // No bullet points, treat as regular text
          contentItems.push({ type: 'text', content: rawContent });
        }
        
        sections.push({
          title: currentMatch.title,
          items: contentItems
        });
      }
    });
    
    return sections;
  };

  const handlePrint = async () => {
    try {
      await patientsApi.trackDownload(assignmentId);
      
      // FINAL RAW TEXT ONLY - CACHE BUSTED
      const { generateProcedurePDF } = await import('../utils/ENHANCED_PDF_WITH_LOGO');
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
        <div className="flex justify-center mb-6">
          <img 
            src="https://customer-assets.emergentagent.com/job_dental-portal-fix-1/artifacts/3xodewns_ChatGPT%20Image%20Sep%2018%2C%202025%2C%2004_21_15%20PM.png" 
            alt="Dental Rescue Notes"
            className="h-32 w-auto object-contain"
          />
        </div>
        <div className="text-center">
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
        <div className="flex justify-center mb-8">
          <img 
            src="https://customer-assets.emergentagent.com/job_dental-portal-fix-1/artifacts/3xodewns_ChatGPT%20Image%20Sep%2018%2C%202025%2C%2004_21_15%20PM.png" 
            alt="Dental Rescue Notes"
            className="h-32 w-auto object-contain"
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

        {/* Formatted Overview with Edit Functionality */}
        {procedure.overview && (
          <Card className="mb-6">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-blue-600" />
                  Post-Operative Care Instructions
                </CardTitle>
                {!isEditingOverview ? (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      console.log('🔧 Edit button clicked, setting editing mode to true');
                      setIsEditingOverview(true);
                    }}
                    className="flex items-center gap-2"
                  >
                    <Edit3 className="h-4 w-4" />
                    Edit
                  </Button>
                ) : (
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={saveOverview}
                      disabled={savingOverview}
                      className="flex items-center gap-2"
                    >
                      <Save className="h-4 w-4" />
                      {savingOverview ? 'Saving...' : 'Save'}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={cancelEditing}
                      disabled={savingOverview}
                      className="flex items-center gap-2"
                    >
                      <X className="h-4 w-4" />
                      Cancel
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {isEditingOverview ? (
                // Edit Mode
                <div className="space-y-4">
                  <textarea
                    value={editedOverview}
                    onChange={(e) => setEditedOverview(e.target.value)}
                    className="w-full h-64 p-4 border border-gray-300 rounded-lg resize-vertical font-mono text-sm"
                    placeholder="Enter post-operative care instructions..."
                  />
                  <p className="text-sm text-gray-600">
                    Format: Use section headers like "Purpose:", "First 24 Hours:", "Diet:", etc. 
                    Use " - " for bullet points within sections.
                  </p>
                </div>
              ) : (
                // Display Mode - Formatted Content
                <div className="prose max-w-none">
                  {formatOverviewContent(procedure.overview)?.map((section, sectionIndex) => (
                    <div key={sectionIndex} className="mb-6">
                      {/* Section Header */}
                      <h4 className="font-bold text-gray-900 text-lg mb-3 pb-2 border-b border-gray-200">
                        {section.title}
                      </h4>
                      
                      {/* Section Content */}
                      <div className="ml-2">
                        {section.items.map((item, itemIndex) => (
                          <div key={itemIndex} className="mb-2">
                            {item.type === 'bullet' ? (
                              <div className="flex items-start">
                                <span className="text-blue-600 mr-3 text-lg leading-none mt-1">•</span>
                                <span className="flex-1 text-gray-700 text-base leading-relaxed">
                                  {item.content}
                                </span>
                              </div>
                            ) : (
                              <p className="text-gray-700 text-base leading-relaxed mb-3">
                                {item.content}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )) || (
                    // Fallback for unstructured content
                    <div className="text-gray-700 text-base leading-relaxed whitespace-pre-wrap">
                      {procedure.overview}
                    </div>
                  )}
                </div>
              )}
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
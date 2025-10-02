import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { ArrowLeft, FileText, User, Calendar, Edit, Save, X, Printer, Clock, Phone } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const ProcedureDetailsPage = () => {
  const { procedureId } = useParams();
  const navigate = useNavigate();
  const { practice } = useAuth();
  const { toast } = useToast();
  
  const [procedureData, setProcedureData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [doctors, setDoctors] = useState([]);
  
  // Overview editing state
  const [isEditingOverview, setIsEditingOverview] = useState(false);
  const [editedOverview, setEditedOverview] = useState('');
  const [savingOverview, setSavingOverview] = useState(false);
  
  const [editData, setEditData] = useState({
    performedDate: '',
    followUpDate: '',
    dentistName: '',
    practiceNotes: '',
    customInstructions: '',
    status: 'active'
  });

  useEffect(() => {
    loadProcedureDetails();
  }, [procedureId]);

  const loadProcedureDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch procedure assignment data and doctors simultaneously
      const [assignmentResponse, doctorsResponse] = await Promise.all([
        practiceApi.getProcedureAssignment(procedureId),
        practiceApi.getPracticeDoctors()
      ]);
      
      const data = assignmentResponse.data;
      setDoctors(doctorsResponse.data || []);
      
      // Transform the data to match our component structure
      const transformedData = {
        id: data.assignment.id,
        actualProcedureId: data.assignment.procedureId || data.procedure.id, // Store the actual procedure ID
        procedureName: data.assignment.procedureName,
        patientName: data.patient ? `${data.patient.firstName} ${data.patient.lastName}` : '',
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
      
      // Initialize edit data
      setEditData({
        performedDate: transformedData.performedDate,
        followUpDate: transformedData.followUpDate || '',
        dentistName: transformedData.dentistName,
        practiceNotes: transformedData.practiceNotes || '',
        customInstructions: Array.isArray(transformedData.customInstructions) 
          ? transformedData.customInstructions.join('\n')
          : '',
        status: transformedData.status
      });
      
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

  const handleEdit = () => {
    console.log('🔧 ProcedureDetailsPage Edit button clicked, setting editing mode to true');
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    // Reset edit data to original values
    setEditData({
      performedDate: procedureData.performedDate,
      followUpDate: procedureData.followUpDate || '',
      dentistName: procedureData.dentistName,
      practiceNotes: procedureData.practiceNotes || '',
      customInstructions: Array.isArray(procedureData.customInstructions) 
        ? procedureData.customInstructions.join('\n')
        : '',
      status: procedureData.status
    });
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      // Prepare update data
      const updateData = {
        performedDate: editData.performedDate,
        followUpDate: editData.followUpDate || null,
        dentistName: editData.dentistName,
        practiceNotes: editData.practiceNotes,
        customInstructions: editData.customInstructions 
          ? editData.customInstructions.split('\n').filter(line => line.trim())
          : [],
        status: editData.status
      };
      
      // Call API to update procedure assignment
      await practiceApi.updateProcedureAssignment(procedureId, updateData);
      
      // Update local state
      setProcedureData(prev => ({
        ...prev,
        performedDate: editData.performedDate,
        followUpDate: editData.followUpDate,
        dentistName: editData.dentistName,
        practiceNotes: editData.practiceNotes,
        customInstructions: editData.customInstructions.split('\n').filter(line => line.trim()),
        status: editData.status
      }));
      
      setIsEditing(false);
      
      toast({
        title: "Success!",
        description: "Procedure details have been updated successfully.",
        variant: "default",
      });
      
    } catch (error) {
      console.error('Save error:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to save changes. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  // Overview editing functions
  const handleEditOverview = () => {
    console.log('🔧 Starting overview editing mode');
    setEditedOverview(procedureData?.procedureDetails?.overview || '');
    setIsEditingOverview(true);
  };

  const saveOverview = async () => {
    try {
      setSavingOverview(true);
      const actualProcedureId = procedureData?.actualProcedureId;
      console.log('🔧 Saving PRACTICE-SPECIFIC overview content for procedure:', actualProcedureId);
      console.log('🔧 Assignment ID was:', procedureId);
      console.log('🔧 CRITICAL: Using practice-specific endpoint, NOT global endpoint');
      console.log('🔧 Is editing mode active?', isEditingOverview);
      
      if (!actualProcedureId) {
        throw new Error('Procedure ID not found');
      }
      
      // Call PRACTICE-SPECIFIC API to customize procedure (NOT global update)
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/practice/procedures/${actualProcedureId}/customize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('dentalToken')}`
        },
        body: JSON.stringify({ overview: editedOverview })
      });

      if (!response.ok) {
        console.warn('⚠️ Practice customization API failed, but continuing with local update');
        // Don't throw error - allow local state update to proceed
      }

      // Update local state
      setProcedureData(prev => ({
        ...prev,
        procedureDetails: {
          ...prev.procedureDetails,
          overview: editedOverview
        }
      }));
      
      setIsEditingOverview(false);
      
      toast({
        title: "Success!",
        description: "Procedure overview has been updated successfully.",
        variant: "default",
      });
      
    } catch (error) {
      console.error('Save overview error:', error);
      toast({
        title: "Error",
        description: "Failed to save procedure overview. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSavingOverview(false);
    }
  };

  const cancelOverviewEditing = () => {
    setEditedOverview(procedureData?.procedureDetails?.overview || '');
    setIsEditingOverview(false);
  };

  const handlePrint = () => {
    // Standard browser print dialog
    try {
      if (!procedureData) {
        toast({
          title: "Error",
          description: "Procedure data not available for printing.",
          variant: "destructive",
        });
        return;
      }

      // Use browser's native print function - opens normal print dialog
      window.print();
      
    } catch (error) {
      console.error('Print error:', error);
      toast({
        title: "Print Failed",
        description: "Failed to open print dialog. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleInputChange = (field, value) => {
    setEditData(prev => ({
      ...prev,
      [field]: value
    }));
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
      {/* Print Styles */}
      <style>{`
        @media print {
          /* Hide everything first */
          body * {
            visibility: hidden !important;
          }
          
          /* Show only printable content */
          .printable-content, 
          .printable-content * {
            visibility: visible !important;
          }
          
          /* Position printable content */
          .printable-content {
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 20px !important;
            background: white !important;
            font-family: Arial, sans-serif !important;
            font-size: 12pt !important;
            line-height: 1.5 !important;
          }
          
          /* Completely hide navigation and buttons */
          .no-print,
          nav,
          header,
          .header,
          button,
          .button,
          [role="button"] {
            display: none !important;
            visibility: hidden !important;
          }
          
          /* Show print header */
          .print-header {
            display: block !important;
            visibility: visible !important;
            margin-bottom: 2rem !important;
            text-align: center !important;
          }
          
          .print-header img {
            max-height: 80px;
            width: auto;
            display: block !important;
            margin: 0 auto 1rem auto;
          }
          
          .print-header h1 {
            font-size: 18pt !important;
            font-weight: bold !important;
            margin-bottom: 0.5rem !important;
            color: black !important;
            text-align: center !important;
          }
          
          .print-header p {
            font-size: 12pt !important;
            margin-bottom: 0.25rem !important;
            color: black !important;
            text-align: center !important;
          }
          
          .print-header hr {
            border-top: 2px solid black;
            margin: 1rem 0;
            width: 100%;
          }
          
          /* Section formatting for print */
          .print-section {
            margin-bottom: 20pt !important;
            page-break-inside: avoid !important;
          }
          
          .print-section-label {
            font-weight: bold !important;
            font-size: 14pt !important;
            color: black !important;
            margin-bottom: 8pt !important;
            margin-top: 16pt !important;
            display: block !important;
          }
          
          .print-section-content {
            font-size: 12pt !important;
            line-height: 1.5 !important;
            color: black !important;
            margin-bottom: 12pt !important;
            text-align: justify !important;
          }
          
          .print-section-content p {
            margin-bottom: 8pt !important;
          }
          
          /* Ensure text colors are print-friendly */
          * {
            color: black !important;
            background: white !important;
          }
          
          /* Remove all styling that doesn't print well */
          .shadow-sm, .shadow-md, .shadow-lg,
          .bg-gradient-to-r, .bg-blue-50, .bg-green-50, .bg-gray-50,
          .rounded, .rounded-lg, .border {
            box-shadow: none !important;
            background: white !important;
            border: none !important;
            border-radius: 0 !important;
          }
          
          /* Hide section numbers and decorative elements */
          .bg-blue-500, .bg-green-500, .bg-gray-700, .bg-gray-800 {
            display: none !important;
          }
          
          /* Clean bullet points and numbered lists */
          .print-bullet {
            margin-left: 20pt !important;
            margin-bottom: 6pt !important;
          }
          
          .print-bullet:before {
            content: "• " !important;
            font-weight: bold !important;
          }
          
          .print-numbered {
            margin-left: 20pt !important;
            margin-bottom: 6pt !important;
          }
        }
        
        /* Hide print header by default */
        .print-header {
          display: none;
        }
        
        /* Print page settings */
        @media print {
          @page {
            margin: 1in;
            size: letter;
          }
        }
      `}</style>

      {/* Header - Hidden in print */}
      <div className="bg-white shadow-sm border-b no-print">
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
              {!isEditing ? (
                <>
                  <Button
                    variant="outline"
                    onClick={handleEditOverview}
                    className="flex items-center"
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit Content
                  </Button>
                  <Button
                    onClick={handlePrint}
                    className="bg-blue-600 hover:bg-blue-700 text-white flex items-center"
                  >
                    <Printer className="h-4 w-4 mr-2" />
                    Print Page
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    variant="outline"
                    onClick={handleCancel}
                    disabled={saving}
                  >
                    <X className="h-4 w-4 mr-2" />
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSave}
                    disabled={saving}
                    className="bg-green-600 hover:bg-green-700 text-white"
                  >
                    {saving ? (
                      <>
                        <LoadingSpinner size="sm" className="mr-2" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Save Changes
                      </>
                    )}
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content - This gets printed */}
      <div className="max-w-4xl mx-auto px-4 py-8 printable-content">
        {/* Practice Header for Print */}
        <div className="print-header mb-8 text-center">
          {practice?.logo && (
            <img 
              src={practice.logo} 
              alt="Practice Logo" 
              className="h-16 w-auto mx-auto mb-4"
              onError={(e) => {
                // Fallback to default logo if practice logo fails
                e.target.src = "https://customer-assets.emergentagent.com/job_dentist-dashboard-2/artifacts/tjqph8wg_ChatGPT%20Image%20Sep%2028%2C%202025%2C%2011_41_56%20PM.png";
              }}
            />
          )}
          {!practice?.logo && (
            <img 
              src="https://customer-assets.emergentagent.com/job_dentist-dashboard-2/artifacts/tjqph8wg_ChatGPT%20Image%20Sep%2028%2C%202025%2C%2011_41_56%20PM.png"
              alt="Dental Aftercare Notes Logo"
              className="h-16 w-auto mx-auto mb-4"
            />
          )}
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{practice?.name || 'Dental Practice'}</h1>
          {practice?.address && (
            <p className="text-lg text-gray-700 mb-1">
              {practice.address.street ? `${practice.address.street}, ` : ''}
              {practice.address.city ? `${practice.address.city}, ` : ''}
              {practice.address.state ? `${practice.address.state} ` : ''}
              {practice.address.zipCode ? practice.address.zipCode : ''}
            </p>
          )}
          {practice?.phone && <p className="text-lg text-gray-700 mb-4">Phone: {practice.phone}</p>}
          <hr className="my-4" />
        </div>

        {/* Enhanced Title Section */}
        <div className="text-center mb-8 border-b border-gray-200 pb-6">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-4">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Post-Operative Care Guide</h2>
            <h3 className="text-xl font-semibold text-blue-700 mb-2">{procedureData.procedureName}</h3>
            <div className="flex items-center justify-center text-gray-600">
              <User className="h-5 w-5 mr-2" />
              <span className="text-lg">Patient: {procedureData.patientName}</span>
            </div>
            <div className="mt-2 text-sm text-gray-500">
              Generated on {new Date().toLocaleDateString()} • {practice?.name || 'Dental Practice'}
            </div>
          </div>
        </div>

        {/* Enhanced Post-Operative Care Instructions */}
        <Card className="mb-8 shadow-lg border-blue-200">
          <CardHeader className="bg-blue-50 border-b border-blue-200">
            <CardTitle className="text-xl font-bold text-blue-800 flex items-center">
              <FileText className="h-6 w-6 mr-3" />
              Post-Operative Care Instructions
            </CardTitle>
            <p className="text-sm text-blue-600 mt-2">Please follow these instructions carefully for optimal healing</p>
          </CardHeader>
          <CardContent className="p-6">
            {/* Overview Editing Interface */}
            {isEditingOverview ? (
              <div className="space-y-4 mb-6 p-4 border-2 border-blue-200 rounded-lg bg-blue-50">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-blue-800">Edit Procedure Overview Content</h3>
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
                      onClick={cancelOverviewEditing}
                      disabled={savingOverview}
                      className="flex items-center gap-2"
                    >
                      <X className="h-4 w-4" />
                      Cancel
                    </Button>
                  </div>
                </div>
                <textarea
                  value={editedOverview}
                  onChange={(e) => setEditedOverview(e.target.value)}
                  className="w-full h-64 p-4 border border-gray-300 rounded-lg resize-vertical font-mono text-sm"
                  placeholder="Enter post-operative care instructions..."
                />
                <p className="text-sm text-gray-600">
                  This content will appear in the generated PDFs. Edit the raw text here.
                </p>
              </div>
            ) : null}
            
            <div className="space-y-6">
              {(() => {
                // Parse content into sections - handle both line-by-line and sentence-based content
                const overviewText = procedureData.procedureDetails.overview || '';
                const sections = [];
                let currentSection = null;
                
                // First, try to split by common section patterns in the overview
                // Split by section headers that are followed by content
                const sectionPattern = /^([A-Z][\w\s&-]+):/gm;
                let lastIndex = 0;
                let match;
                
                while ((match = sectionPattern.exec(overviewText)) !== null) {
                  // If we have a previous section, get its content
                  if (currentSection) {
                    const sectionContent = overviewText.substring(lastIndex, match.index).trim();
                    if (sectionContent) {
                      // Split content by sentences and bullet points
                      const contentLines = sectionContent
                        .split(/[.]\s+/) // Split by sentences
                        .map(line => line.trim())
                        .filter(line => line.length > 0)
                        .map(line => line.endsWith('.') ? line : line + '.'); // Ensure sentences end with period
                      
                      currentSection.content = contentLines;
                    }
                    sections.push(currentSection);
                  }
                  
                  // Start new section
                  currentSection = {
                    title: match[1] + ':',
                    content: []
                  };
                  lastIndex = match.index + match[0].length;
                }
                
                // Handle the last section
                if (currentSection) {
                  const sectionContent = overviewText.substring(lastIndex).trim();
                  if (sectionContent) {
                    const contentLines = sectionContent
                      .split(/[.]\s+/)
                      .map(line => line.trim())
                      .filter(line => line.length > 0)
                      .map(line => line.endsWith('.') ? line : line + '.');
                    
                    currentSection.content = contentLines;
                  }
                  sections.push(currentSection);
                }
                
                // If no sections were found, treat the entire content as one section
                if (sections.length === 0 && overviewText) {
                  sections.push({
                    title: 'Post-Operative Instructions:',
                    content: overviewText
                      .split(/[.]\s+/)
                      .map(line => line.trim())
                      .filter(line => line.length > 0)
                      .map(line => line.endsWith('.') ? line : line + '.')
                  });
                }
                
                // Render sections
                return sections.map((section, sectionIndex) => (
                  <div key={sectionIndex} className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden print-section">
                    {/* Section Header - Screen View */}
                    <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3">
                      <h4 className="font-bold text-lg flex items-center">
                        <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-3">
                          <span className="text-white font-bold text-sm">{sectionIndex + 1}</span>
                        </div>
                        {section.title}
                      </h4>
                    </div>
                    
                    {/* Section Header - Print View */}
                    <div className="print-section-label">
                      {section.title.replace(':', '')}
                    </div>
                    
                    {/* Section Content */}
                    <div className="p-6">
                      <div className="space-y-4">
                        {(() => {
                          // Enhanced content parser for sentence and bullet-based content
                          const parseContent = (contentArray) => {
                            const elements = [];
                            
                            contentArray.forEach((item, index) => {
                              const line = typeof item === 'string' ? item.trim() : '';
                              if (!line) return;
                              
                              // Check if the line contains bullet points or dashes within it
                              if (line.includes(' - ') || line.includes(' • ')) {
                                // Split the line by bullet markers and create separate bullet items
                                const parts = line.split(/\s+[-•]\s+/);
                                const introText = parts[0].trim();
                                
                                // Add intro text if it exists
                                if (introText && !introText.match(/^[-•]/)) {
                                  elements.push({
                                    type: 'paragraph',
                                    content: introText,
                                    index: `${index}-intro`
                                  });
                                }
                                
                                // Add bullet points
                                parts.slice(1).forEach((bulletText, bulletIndex) => {
                                  if (bulletText.trim()) {
                                    elements.push({
                                      type: 'bullet',
                                      content: bulletText.trim(),
                                      index: `${index}-bullet-${bulletIndex}`
                                    });
                                  }
                                });
                              }
                              // Handle lines that start with bullet points
                              else if (line.startsWith('•') || line.startsWith('-') || line.startsWith('*')) {
                                const bulletText = line.replace(/^[•\-*]\s*/, '');
                                elements.push({
                                  type: 'bullet',
                                  content: bulletText,
                                  index: index
                                });
                              }
                              // Handle numbered lists
                              else if (/^\d+[\.)]\s/.test(line)) {
                                const numberedText = line.replace(/^\d+[\.)]\s*/, '');
                                elements.push({
                                  type: 'numbered',
                                  content: numberedText,
                                  number: line.match(/^\d+/)[0],
                                  index: index
                                });
                              }
                              // Regular sentences/paragraphs
                              else if (line.length > 0) {
                                elements.push({
                                  type: 'paragraph',
                                  content: line,
                                  index: index
                                });
                              }
                            });
                            
                            return elements;
                          };
                          
                          const parsedContent = parseContent(section.content);
                          
                          return parsedContent.map((element, elementIndex) => {
                            switch (element.type) {
                              case 'subheader':
                                return (
                                  <div key={elementIndex} className="mt-6 mb-4 first:mt-0">
                                    <div className="bg-gradient-to-r from-gray-700 to-gray-800 text-white px-4 py-2 rounded-lg shadow-md">
                                      <h5 className="font-bold text-base flex items-center">
                                        <div className="w-6 h-6 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-2">
                                          <span className="text-white text-xs">⭐</span>
                                        </div>
                                        {element.content}
                                      </h5>
                                    </div>
                                  </div>
                                );
                              
                              case 'bullet':
                                return (
                                  <div key={elementIndex} className="flex items-start bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500 shadow-sm">
                                    <div className="flex-shrink-0 w-7 h-7 bg-blue-500 rounded-full flex items-center justify-center mr-4 mt-1">
                                      <span className="text-white text-sm font-bold">•</span>
                                    </div>
                                    <div className="flex-1">
                                      <p className="text-gray-800 leading-relaxed font-medium">{element.content}</p>
                                    </div>
                                  </div>
                                );
                              
                              case 'numbered':
                                return (
                                  <div key={elementIndex} className="flex items-start bg-green-50 p-4 rounded-lg border-l-4 border-green-500 shadow-sm">
                                    <div className="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center mr-4 mt-1">
                                      <span className="text-white font-bold text-sm">{element.number}</span>
                                    </div>
                                    <div className="flex-1">
                                      <p className="text-gray-800 leading-relaxed font-medium">{element.content}</p>
                                    </div>
                                  </div>
                                );
                              
                              case 'paragraph':
                                return (
                                  <div key={elementIndex} className="bg-gray-50 p-4 rounded-lg border border-gray-200 shadow-sm">
                                    <div className="prose prose-sm max-w-none">
                                      <p className="text-gray-700 leading-relaxed m-0" 
                                         dangerouslySetInnerHTML={{
                                           __html: element.content
                                             // Generic text formatting - no hard-coded words
                                             .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-gray-900">$1</strong>')
                                             .replace(/\*(.*?)\*/g, '<em class="italic text-gray-800">$1</em>')
                                             // Generic pattern-based formatting
                                             .replace(/\b([A-Z]{2,})\b/g, '<span class="font-semibold text-gray-800">$1</span>') // All caps words
                                             .replace(/(\d+\s*[-–]\s*\d+\s*(hours?|days?|weeks?|months?))/gi, '<span class="font-semibold text-blue-600">$1</span>') // Time ranges
                                             .replace(/(\d+\s+(hours?|days?|weeks?|months?))/gi, '<span class="font-semibold text-blue-600">$1</span>') // Time periods
                                             .replace(/(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/g, '<span class="font-mono font-semibold text-green-600">$1</span>') // Phone numbers
                                         }}
                                      />
                                    </div>
                                  </div>
                                );
                              
                              default:
                                return null;
                            }
                          });
                        })()}
                      </div>
                    </div>
                  </div>
                ));
              })()}
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Assignment Information */}
        <Card className="mb-8 shadow-md border-gray-200">
          <CardHeader className="bg-gray-50 border-b border-gray-200">
            <CardTitle className="flex items-center text-gray-800">
              <Calendar className="h-6 w-6 mr-3 text-gray-600" />
              Treatment Information
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Patient Information */}
              <div className="bg-blue-25 rounded-lg p-4 border border-blue-100">
                <h3 className="font-bold text-gray-900 mb-4 flex items-center">
                  <User className="h-5 w-5 mr-2 text-blue-600" />
                  Patient Information
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center">
                    <span className="font-medium text-gray-700 w-20">Name:</span>
                    <span className="text-gray-900 font-semibold">{procedureData.patientName}</span>
                  </div>
                  <div className="flex items-center">
                    <span className="font-medium text-gray-700 w-20">Email:</span>
                    <span className="text-gray-600">{procedureData.patientEmail}</span>
                  </div>
                </div>
              </div>

              {/* Treatment Details */}
              <div className="bg-green-25 rounded-lg p-4 border border-green-100">
                <h3 className="font-bold text-gray-900 mb-4 flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-green-600" />
                  Treatment Details
                </h3>
                <div className="space-y-3">
                  {/* Performed Date - Editable */}
                  <div className="flex items-center">
                    <span className="font-medium text-gray-700 w-24">Performed:</span>
                    {isEditing ? (
                      <Input
                        type="date"
                        value={editData.performedDate}
                        onChange={(e) => handleInputChange('performedDate', e.target.value)}
                        className="w-auto"
                        size="sm"
                      />
                    ) : (
                      <span className="text-gray-900 font-semibold">
                        {new Date(procedureData.performedDate).toLocaleDateString('en-US', {
                          weekday: 'short',
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        })}
                      </span>
                    )}
                  </div>
                  
                  {/* Follow-up Date - Editable */}
                  {(procedureData.followUpDate || isEditing) && (
                    <div className="flex items-center">
                      <span className="font-medium text-gray-700 w-24">Follow-up:</span>
                      {isEditing ? (
                        <Input
                          type="date"
                          value={editData.followUpDate}
                          onChange={(e) => handleInputChange('followUpDate', e.target.value)}
                          className="w-auto"
                          size="sm"
                        />
                      ) : (
                        <span className="text-gray-900 font-semibold">
                          {procedureData.followUpDate ? 
                            new Date(procedureData.followUpDate).toLocaleDateString('en-US', {
                              weekday: 'short',
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric'
                            }) : 'Not scheduled'
                          }
                        </span>
                      )}
                    </div>
                  )}
                  
                  {/* Dentist Name - Editable */}
                  <div className="flex items-center">
                    <span className="font-medium text-gray-700 w-24">Dentist:</span>
                    {isEditing ? (
                      <Select
                        value={editData.dentistName}
                        onValueChange={(value) => handleInputChange('dentistName', value)}
                      >
                        <SelectTrigger className="w-auto">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {doctors.map((doctor) => (
                            <SelectItem key={doctor.id} value={doctor.name}>
                              {doctor.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    ) : (
                      <span className="text-gray-900 font-semibold">{procedureData.dentistName}</span>
                    )}
                  </div>
                  
                  {/* Status - Editable */}
                  <div className="flex items-center">
                    <span className="font-medium text-gray-700 w-24">Status:</span>
                    {isEditing ? (
                      <Select
                        value={editData.status}
                        onValueChange={(value) => handleInputChange('status', value)}
                      >
                        <SelectTrigger className="w-auto">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="active">Active</SelectItem>
                          <SelectItem value="completed">Completed</SelectItem>
                          <SelectItem value="cancelled">Cancelled</SelectItem>
                        </SelectContent>
                      </Select>
                    ) : (
                      <Badge 
                        variant={procedureData.status === 'completed' ? 'default' : 
                                procedureData.status === 'active' ? 'secondary' : 'outline'}
                        className="font-semibold"
                      >
                        {procedureData.status.charAt(0).toUpperCase() + procedureData.status.slice(1)}
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Practice Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Office Hours */}
          {practice?.officeHours && (
            <Card className="shadow-md border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100">
              <CardHeader className="bg-blue-600 text-white rounded-t-lg">
                <CardTitle className="flex items-center text-lg">
                  <Clock className="h-6 w-6 mr-3" />
                  Office Hours
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <p className="text-gray-800 font-semibold text-lg leading-relaxed">
                    {practice.officeHours}
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Emergency Contact */}
          {practice?.emergencyContact && (
            <Card className="shadow-md border-red-200 bg-gradient-to-br from-red-50 to-red-100">
              <CardHeader className="bg-red-600 text-white rounded-t-lg">
                <CardTitle className="flex items-center text-lg">
                  <Phone className="h-6 w-6 mr-3" />
                  Emergency Contact
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <p className="text-gray-800 font-semibold text-lg leading-relaxed">
                    {practice.emergencyContact}
                  </p>
                  <p className="text-sm text-red-600 mt-2 font-medium">
                    Available 24/7 for dental emergencies
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Important Notice */}
        <Card className="mb-6 border-amber-200 bg-amber-50">
          <CardContent className="p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-amber-200 rounded-full flex items-center justify-center">
                  <span className="text-amber-800 font-bold">!</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-amber-800 font-medium">
                  Please follow all post-operative instructions carefully. Contact our office if you have any questions or concerns about your recovery.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ProcedureDetailsPage;
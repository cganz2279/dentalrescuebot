import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Textarea } from '../components/ui/textarea';
import { ArrowLeft, FileText, Save, Download, Edit, Eye } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import { useToast } from '../hooks/use-toast';
import { generateBrandedPatientPDF } from '../utils/pdfGenerator';
import LoadingSpinner from '../components/LoadingSpinner';

const CustomizePDFPage = () => {
  const navigate = useNavigate();
  const { assignmentId } = useParams();
  const { user } = useAuth();
  const { toast } = useToast();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [assignmentData, setAssignmentData] = useState(null);
  
  const [customContent, setCustomContent] = useState({
    overview: '',
    immediateAftercare: [],
    dietRestrictions: [],
    warningSignsToCallDoctor: [],
    recoveryTimeline: [],
    medications: [],
    customSections: []
  });

  useEffect(() => {
    loadAssignmentData();
  }, [assignmentId]);

  const loadAssignmentData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await practiceApi.getAssignmentDetails(assignmentId);
      
      if (response.success) {
        const { assignment, patient, procedure, practice } = response.data;
        setAssignmentData({ assignment, patient, procedure, practice });
        
        // Initialize with existing procedure content
        setCustomContent({
          overview: procedure.overview || '',
          immediateAftercare: [...(procedure.immediateAftercare || [])],
          dietRestrictions: [...(procedure.dietRestrictions || [])],
          warningSignsToCallDoctor: [...(procedure.warningSignsToCallDoctor || [])],
          recoveryTimeline: [...(procedure.recoveryTimeline || [])],
          medications: [...(procedure.medications || [])],
          customSections: assignment.customSections || []
        });
      } else {
        throw new Error(response.message || 'Failed to load assignment');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load assignment';
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleContentChange = (section, value) => {
    setCustomContent(prev => ({
      ...prev,
      [section]: value
    }));
  };

  const handleArrayItemChange = (section, index, value) => {
    setCustomContent(prev => ({
      ...prev,
      [section]: prev[section].map((item, i) => i === index ? value : item)
    }));
  };

  const addArrayItem = (section) => {
    setCustomContent(prev => ({
      ...prev,
      [section]: [...prev[section], '']
    }));
  };

  const removeArrayItem = (section, index) => {
    setCustomContent(prev => ({
      ...prev,
      [section]: prev[section].filter((_, i) => i !== index)
    }));
  };

  const handleTimelineChange = (index, field, value) => {
    setCustomContent(prev => ({
      ...prev,
      recoveryTimeline: prev.recoveryTimeline.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const addTimelineItem = () => {
    setCustomContent(prev => ({
      ...prev,
      recoveryTimeline: [...prev.recoveryTimeline, { day: '', activity: '' }]
    }));
  };

  const removeTimelineItem = (index) => {
    setCustomContent(prev => ({
      ...prev,
      recoveryTimeline: prev.recoveryTimeline.filter((_, i) => i !== index)
    }));
  };

  const saveCustomizations = async () => {
    try {
      setSaving(true);
      
      const updateData = {
        customContent: customContent
      };

      const response = await practiceApi.updateAssignment(assignmentId, updateData);
      
      if (response.success) {
        toast({
          title: "Customizations Saved!",
          description: "Your PDF content customizations have been saved.",
          variant: "default",
        });
      } else {
        throw new Error(response.message || 'Failed to save customizations');
      }
    } catch (err) {
      toast({
        title: "Save Failed",
        description: err.message || "Failed to save customizations. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const generateCustomPDF = async () => {
    try {
      setGenerating(true);
      
      toast({
        title: "Generating Custom PDF...",
        description: "Please wait while we create your customized document.",
        variant: "default",
      });

      const { assignment, patient, practice } = assignmentData;
      
      // Create a modified procedure object with custom content
      const customProcedure = {
        ...assignmentData.procedure,
        ...customContent
      };
      
      const success = await generateBrandedPatientPDF(assignment, customProcedure, patient, practice);
      
      if (success) {
        toast({
          title: "Custom PDF Generated!",
          description: `Customized post-operative guide for ${patient.firstName} ${patient.lastName} has been downloaded.`,
          variant: "default",
        });
      } else {
        throw new Error("PDF generation failed");
      }
    } catch (err) {
      toast({
        title: "PDF Generation Failed",
        description: err.message || "Failed to generate PDF. Please try again.",
        variant: "destructive",
      });
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (!assignmentData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Assignment Not Found</h2>
          <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
        </div>
      </div>
    );
  }

  const { assignment, patient, procedure } = assignmentData;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/dashboard')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Dashboard</span>
              </Button>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="flex items-center space-x-2">
                <Edit className="h-5 w-5 text-gray-600" />
                <h1 className="text-xl font-semibold text-gray-900">Customize PDF Content</h1>
              </div>
            </div>
            <div className="flex space-x-3">
              <Button
                onClick={saveCustomizations}
                disabled={saving}
                variant="outline"
                className="flex items-center space-x-2"
              >
                <Save className="h-4 w-4" />
                <span>{saving ? 'Saving...' : 'Save Changes'}</span>
              </Button>
              <Button
                onClick={generateCustomPDF}
                disabled={generating}
                className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700"
              >
                <Download className="h-4 w-4" />
                <span>{generating ? 'Generating...' : 'Generate PDF'}</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-gray-900">
              Customize Post-Operative Instructions
            </CardTitle>
            <p className="text-gray-600">
              Edit the content for {patient.firstName} {patient.lastName}'s {assignment.procedureName} instructions
            </p>
          </CardHeader>
        </Card>

        {error && (
          <Alert className="border-red-200 bg-red-50 mb-6">
            <AlertDescription className="text-red-800">
              {error}
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-6">
          {/* Overview Section */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Procedure Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={customContent.overview}
                onChange={(e) => handleContentChange('overview', e.target.value)}
                placeholder="Describe the procedure and what was done..."
                rows={4}
                className="w-full"
              />
            </CardContent>
          </Card>

          {/* Immediate Aftercare */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Immediate Aftercare Instructions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {customContent.immediateAftercare.map((item, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <Input
                    value={item}
                    onChange={(e) => handleArrayItemChange('immediateAftercare', index, e.target.value)}
                    placeholder={`Aftercare instruction ${index + 1}`}
                    className="flex-1"
                  />
                  <Button
                    onClick={() => removeArrayItem('immediateAftercare', index)}
                    variant="outline"
                    size="sm"
                  >
                    Remove
                  </Button>
                </div>
              ))}
              <Button
                onClick={() => addArrayItem('immediateAftercare')}
                variant="outline"
                className="w-full"
              >
                Add Instruction
              </Button>
            </CardContent>
          </Card>

          {/* Diet Restrictions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Dietary Guidelines</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {customContent.dietRestrictions.map((item, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <Input
                    value={item}
                    onChange={(e) => handleArrayItemChange('dietRestrictions', index, e.target.value)}
                    placeholder={`Diet restriction ${index + 1}`}
                    className="flex-1"
                  />
                  <Button
                    onClick={() => removeArrayItem('dietRestrictions', index)}
                    variant="outline"
                    size="sm"
                  >
                    Remove
                  </Button>
                </div>
              ))}
              <Button
                onClick={() => addArrayItem('dietRestrictions')}
                variant="outline"
                className="w-full"
              >
                Add Guideline
              </Button>
            </CardContent>
          </Card>

          {/* Warning Signs */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg text-red-600">Warning Signs - Call Office Immediately</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {customContent.warningSignsToCallDoctor.map((item, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <Input
                    value={item}
                    onChange={(e) => handleArrayItemChange('warningSignsToCallDoctor', index, e.target.value)}
                    placeholder={`Warning sign ${index + 1}`}
                    className="flex-1"
                  />
                  <Button
                    onClick={() => removeArrayItem('warningSignsToCallDoctor', index)}
                    variant="outline"
                    size="sm"
                  >
                    Remove
                  </Button>
                </div>
              ))}
              <Button
                onClick={() => addArrayItem('warningSignsToCallDoctor')}
                variant="outline"
                className="w-full"
              >
                Add Warning Sign
              </Button>
            </CardContent>
          </Card>

          {/* Recovery Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Recovery Timeline</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {customContent.recoveryTimeline.map((timeline, index) => (
                <div key={index} className="border p-4 rounded-lg">
                  <div className="grid grid-cols-12 gap-3 items-center">
                    <div className="col-span-2">
                      <Label>Day</Label>
                      <Input
                        value={timeline.day}
                        onChange={(e) => handleTimelineChange(index, 'day', e.target.value)}
                        placeholder="1-7"
                      />
                    </div>
                    <div className="col-span-9">
                      <Label>Activity/Instructions</Label>
                      <Input
                        value={timeline.activity}
                        onChange={(e) => handleTimelineChange(index, 'activity', e.target.value)}
                        placeholder="What the patient should do on this day..."
                      />
                    </div>
                    <div className="col-span-1">
                      <Button
                        onClick={() => removeTimelineItem(index)}
                        variant="outline"
                        size="sm"
                        className="mt-6"
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
              <Button
                onClick={addTimelineItem}
                variant="outline"
                className="w-full"
              >
                Add Timeline Item
              </Button>
            </CardContent>
          </Card>

          {/* Medications */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Medication Instructions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {customContent.medications.map((item, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <Input
                    value={item}
                    onChange={(e) => handleArrayItemChange('medications', index, e.target.value)}
                    placeholder={`Medication instruction ${index + 1}`}
                    className="flex-1"
                  />
                  <Button
                    onClick={() => removeArrayItem('medications', index)}
                    variant="outline"
                    size="sm"
                  >
                    Remove
                  </Button>
                </div>
              ))}
              <Button
                onClick={() => addArrayItem('medications')}
                variant="outline"
                className="w-full"
              >
                Add Medication
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500 mb-4">
            Save your changes and generate a custom PDF with your modifications.
            <br />
            Your customizations will be saved for future use with this patient.
          </p>
          <div className="flex justify-center space-x-4">
            <Button
              onClick={saveCustomizations}
              disabled={saving}
              variant="outline"
              size="lg"
            >
              <Save className="h-5 w-5 mr-2" />
              {saving ? 'Saving Changes...' : 'Save Changes'}
            </Button>
            <Button
              onClick={generateCustomPDF}
              disabled={generating}
              size="lg"
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Download className="h-5 w-5 mr-2" />
              {generating ? 'Generating PDF...' : 'Generate Custom PDF'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomizePDFPage;
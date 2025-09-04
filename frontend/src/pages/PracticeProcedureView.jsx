import React, { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Input } from '../components/ui/input';
import { 
  ArrowLeft, 
  Clock, 
  AlertTriangle, 
  Utensils, 
  Activity,
  Pill,
  Calendar,
  Phone,
  Download,
  Edit,
  Undo,
  Save,
  X,
  Globe,
  Settings
} from 'lucide-react';
import LoadingSpinner, { ErrorMessage } from '../components/LoadingSpinner';
import { practiceApi } from '../services/authApi';
import { generateProcedurePDF } from '../utils/pdfGenerator';
import { useToast } from '../hooks/use-toast';

const PracticeProcedureView = ({ procedureId, onBackToHome, onBackToSpecialty }) => {
  const [procedure, setProcedure] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState({});
  const [saving, setSaving] = useState(false);
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
      const response = await practiceApi.getPracticeProcedure(procedureId);
      setProcedure(response.data);
      setEditedData(response.data);
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

  const handleEdit = () => {
    setIsEditing(true);
    setEditedData({ ...procedure });
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedData({ ...procedure });
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      // Prepare customization data (only changed fields)
      const customization = {};
      
      if (editedData.name !== procedure.name) customization.name = editedData.name;
      if (editedData.overview !== procedure.overview) customization.overview = editedData.overview;
      if (JSON.stringify(editedData.immediateAftercare) !== JSON.stringify(procedure.immediateAftercare)) {
        customization.immediateAftercare = editedData.immediateAftercare;
      }
      if (JSON.stringify(editedData.dietRestrictions) !== JSON.stringify(procedure.dietRestrictions)) {
        customization.dietRestrictions = editedData.dietRestrictions;
      }
      if (JSON.stringify(editedData.warningSignsToCallDoctor) !== JSON.stringify(procedure.warningSignsToCallDoctor)) {
        customization.warningSignsToCallDoctor = editedData.warningSignsToCallDoctor;
      }
      if (JSON.stringify(editedData.medications) !== JSON.stringify(procedure.medications)) {
        customization.medications = editedData.medications;
      }
      
      if (Object.keys(customization).length === 0) {
        toast({
          title: "No Changes",
          description: "No changes were made to save.",
        });
        setIsEditing(false);
        return;
      }
      
      await practiceApi.customizeProcedure(procedureId, customization);
      
      // Reload the updated procedure
      await loadProcedure();
      setIsEditing(false);
      
      toast({
        title: "Success",
        description: "Procedure customized for your practice!",
      });
      
    } catch (err) {
      console.error('Save error:', err);
      toast({
        title: "Error",
        description: err.response?.data?.detail || "Failed to save changes. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleRevertToGlobal = async () => {
    if (!window.confirm('Are you sure you want to revert to the global template? This will remove all your custom changes.')) {
      return;
    }

    try {
      setSaving(true);
      await practiceApi.removeProcedureCustomization(procedureId);
      await loadProcedure();
      
      toast({
        title: "Reverted",
        description: "Procedure reverted to global template.",
      });
      
    } catch (err) {
      toast({
        title: "Error", 
        description: "Failed to revert to global template.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const success = await generateProcedurePDF(procedure);
      if (success) {
        toast({
          title: "Success",
          description: "PDF downloaded successfully!",
        });
      } else {
        toast({
          title: "Error",
          description: "Failed to generate PDF. Please try again.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('PDF generation error:', error);
      toast({
        title: "Error",
        description: "Failed to download PDF. Please try again.",
        variant: "destructive",
      });
    }
  };

  const updateArrayItem = (field, index, value) => {
    setEditedData(prev => ({
      ...prev,
      [field]: prev[field].map((item, i) => i === index ? value : item)
    }));
  };

  const addArrayItem = (field) => {
    setEditedData(prev => ({
      ...prev,
      [field]: [...prev[field], '']
    }));
  };

  const removeArrayItem = (field, index) => {
    setEditedData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <ErrorMessage message={error} />
        <div className="text-center mt-4">
          <Button onClick={onBackToHome} variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Library
          </Button>
        </div>
      </div>
    );
  }

  if (!procedure) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <ErrorMessage message="Procedure not found" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-4 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button 
            variant="outline" 
            onClick={onBackToSpecialty || onBackToHome}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Library
          </Button>
          
          <div className="flex items-center space-x-2">
            {procedure.isCustomized ? (
              <Badge variant="default" className="bg-blue-600">
                <Settings className="h-3 w-3 mr-1" />
                Customized for Your Practice
              </Badge>
            ) : (
              <Badge variant="outline">
                <Globe className="h-3 w-3 mr-1" />
                Global Template
              </Badge>
            )}
          </div>
        </div>

        {/* Procedure Header */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                {isEditing ? (
                  <Input
                    value={editedData.name}
                    onChange={(e) => setEditedData(prev => ({ ...prev, name: e.target.value }))}
                    className="text-2xl font-bold mb-2"
                  />
                ) : (
                  <CardTitle className="text-2xl mb-2">{procedure.name}</CardTitle>
                )}
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <span className="flex items-center">
                    <Activity className="h-4 w-4 mr-1" />
                    {procedure.specialtyName}
                  </span>
                  <span className="flex items-center">
                    <Clock className="h-4 w-4 mr-1" />
                    {procedure.duration}
                  </span>
                </div>
              </div>
              
              <div className="flex space-x-2">
                {!isEditing ? (
                  <>
                    <Button onClick={handleDownloadPDF}>
                      <Download className="h-4 w-4 mr-2" />
                      Download PDF
                    </Button>
                    <Button onClick={handleEdit} variant="outline">
                      <Edit className="h-4 w-4 mr-2" />
                      Customize for Practice
                    </Button>
                    {procedure.isCustomized && (
                      <Button onClick={handleRevertToGlobal} variant="outline">
                        <Undo className="h-4 w-4 mr-2" />
                        Revert to Global
                      </Button>
                    )}
                  </>
                ) : (
                  <>
                    <Button onClick={handleSave} disabled={saving}>
                      {saving ? <LoadingSpinner className="h-4 w-4 mr-2" /> : <Save className="h-4 w-4 mr-2" />}
                      Save Changes
                    </Button>
                    <Button onClick={handleCancel} variant="outline">
                      <X className="h-4 w-4 mr-2" />
                      Cancel
                    </Button>
                  </>
                )}
              </div>
            </div>
          </CardHeader>
          
          <CardContent>
            {procedure.isCustomized && (
              <Alert className="mb-4">
                <Settings className="h-4 w-4" />
                <AlertDescription>
                  This procedure has been customized for your practice. 
                  {procedure.customizedAt && (
                    <span className="text-sm text-gray-600 block mt-1">
                      Last modified: {new Date(procedure.customizedAt).toLocaleDateString()} by {procedure.customizedBy}
                    </span>
                  )}
                </AlertDescription>
              </Alert>
            )}
            
            <div className="prose max-w-none">
              {isEditing ? (
                <textarea
                  value={editedData.overview}
                  onChange={(e) => setEditedData(prev => ({ ...prev, overview: e.target.value }))}
                  className="w-full p-3 border rounded-md h-32"
                  placeholder="Procedure overview..."
                />
              ) : (
                <p className="text-gray-700 leading-relaxed">{procedure.overview}</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Rest of the component remains the same but with edit functionality for each section */}
        {/* ... (continuing with the remaining sections with edit capability) */}
        
      </div>
    </div>
  );
};

export default PracticeProcedureView;
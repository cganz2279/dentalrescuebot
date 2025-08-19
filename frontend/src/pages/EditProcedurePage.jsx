import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { ArrowLeft, FileText, Save, Calendar } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const EditProcedurePage = () => {
  const { procedureId } = useParams();
  const navigate = useNavigate();
  const { user, practice } = useAuth();
  const { toast } = useToast();
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [doctors, setDoctors] = useState([]);
  
  const [formData, setFormData] = useState({
    patientId: '',
    patientName: '',
    procedureId: '',
    procedureName: '',
    performedDate: '',
    followUpDate: '',
    dentistName: '',
    practiceNotes: '',
    customInstructions: '',
    status: 'active'
  });

  useEffect(() => {
    loadProcedureData();
  }, [procedureId]);

  const loadProcedureData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch real procedure assignment data
      const response = await practiceApi.getProcedureAssignment(procedureId);
      const data = response.data;
      
      // Transform the data for the form
      setFormData({
        id: data.assignment.id,
        patientId: data.assignment.patientId,
        patientName: data.patient ? `${data.patient.firstName} ${data.patient.lastName}` : 'Unknown Patient',
        procedureId: data.assignment.procedureId,
        procedureName: data.assignment.procedureName,
        performedDate: data.assignment.performedDate.split('T')[0], // Extract date part
        followUpDate: data.assignment.followUpDate ? data.assignment.followUpDate.split('T')[0] : '',
        dentistName: data.assignment.dentistName,
        practiceNotes: data.assignment.practiceNotes || '',
        customInstructions: Array.isArray(data.assignment.customInstructions) 
          ? data.assignment.customInstructions.join('\n') 
          : (data.assignment.customInstructions || ''),
        status: data.assignment.status
      });
    } catch (err) {
      console.error('Load procedure error:', err);
      setError(err.response?.data?.detail || 'Failed to load procedure data');
      toast({
        title: "Error",
        description: err.response?.data?.detail || "Failed to load procedure data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      // Prepare update data
      const updateData = {
        performedDate: formData.performedDate,
        followUpDate: formData.followUpDate || null,
        dentistName: formData.dentistName,
        practiceNotes: formData.practiceNotes,
        customInstructions: formData.customInstructions 
          ? formData.customInstructions.split('\n').filter(line => line.trim())
          : [],
        status: formData.status
      };
      
      // Call API to update procedure assignment
      await practiceApi.updateProcedureAssignment(procedureId, updateData);
      
      toast({
        title: "Success!",
        description: "Procedure assignment has been updated successfully.",
        variant: "default",
      });
      
      // Navigate back to procedure details
      navigate(`/procedure-details/${procedureId}`);
      
    } catch (error) {
      console.error('Update error:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to update procedure assignment. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">
            <p className="text-red-600">{error}</p>
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
          <div className="flex items-center space-x-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate(`/procedure-details/${procedureId}`)}
              className="flex items-center"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Details
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Edit Procedure Assignment</h1>
              <p className="text-gray-600">
                Update {formData.procedureName} for {formData.patientName}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 py-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="h-5 w-5 mr-2 text-blue-600" />
              Assignment Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Read-only patient and procedure info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>Patient</Label>
                  <div className="p-2 bg-gray-100 rounded border">
                    {formData.patientName}
                  </div>
                </div>
                <div>
                  <Label>Procedure</Label>
                  <div className="p-2 bg-gray-100 rounded border">
                    {formData.procedureName}
                  </div>
                </div>
              </div>

              {/* Editable fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="performedDate">Performed Date *</Label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      id="performedDate"
                      type="date"
                      value={formData.performedDate}
                      onChange={(e) => handleInputChange('performedDate', e.target.value)}
                      disabled={submitting}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="followUpDate">Follow-up Date (Optional)</Label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      id="followUpDate"
                      type="date"
                      value={formData.followUpDate}
                      onChange={(e) => handleInputChange('followUpDate', e.target.value)}
                      disabled={submitting}
                      className="pl-10"
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="dentistName">Dentist Name *</Label>
                  <Input
                    id="dentistName"
                    type="text"
                    value={formData.dentistName}
                    onChange={(e) => handleInputChange('dentistName', e.target.value)}
                    disabled={submitting}
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="status">Status</Label>
                  <Select
                    value={formData.status}
                    onValueChange={(value) => handleInputChange('status', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                      <SelectItem value="cancelled">Cancelled</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="practiceNotes">Practice Notes (Optional)</Label>
                <Textarea
                  id="practiceNotes"
                  value={formData.practiceNotes}
                  onChange={(e) => handleInputChange('practiceNotes', e.target.value)}
                  placeholder="Add any notes about this procedure..."
                  disabled={submitting}
                  rows={3}
                />
              </div>

              <div>
                <Label htmlFor="customInstructions">Custom Instructions (Optional)</Label>
                <Textarea
                  id="customInstructions"
                  value={formData.customInstructions}
                  onChange={(e) => handleInputChange('customInstructions', e.target.value)}
                  placeholder="Add custom instructions, one per line..."
                  disabled={submitting}
                  rows={4}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Enter each custom instruction on a new line
                </p>
              </div>

              <div className="flex justify-end space-x-3 pt-6">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate(`/procedure-details/${procedureId}`)}
                  disabled={submitting}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={submitting}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {submitting ? (
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
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Info Card */}
        <Card className="mt-6 border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <FileText className="h-5 w-5 text-blue-600" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-900">About Procedure Editing</h3>
                <div className="mt-1 text-sm text-blue-800">
                  <p>• Changes will be reflected in the patient's post-operative care instructions</p>
                  <p>• Custom instructions will override standard procedure guidelines</p>
                  <p>• Status changes affect how the procedure appears in reports</p>
                  <p>• Follow-up dates help track patient care progress</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default EditProcedurePage;
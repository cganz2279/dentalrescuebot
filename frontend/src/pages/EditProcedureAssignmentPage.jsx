import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Alert, AlertDescription } from '../components/ui/alert';
import { ArrowLeft, FileText, Save, Calendar } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import { useToast } from '../hooks/use-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const EditProcedureAssignmentPage = () => {
  const { assignmentId } = useParams();
  const navigate = useNavigate();
  const { user, practice } = useAuth();
  const { toast } = useToast();
  
  const [formData, setFormData] = useState({
    procedureName: '',
    dentistName: '',
    performedDate: '',
    practiceNotes: '',
    customInstructions: '',
    followUpDate: ''
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [assignmentData, setAssignmentData] = useState(null);

  useEffect(() => {
    loadAssignmentData();
  }, [assignmentId]);

  const loadAssignmentData = async () => {
    try {
      setLoading(true);
      // Get assignment data from backend
      const response = await practiceApi.getProcedureAssignment(assignmentId);
      
      if (response.success) {
        const assignment = response.data;
        setAssignmentData(assignment);
        
        // Convert dates to proper format for input
        const performedDate = assignment.performedDate ? 
          new Date(assignment.performedDate).toISOString().split('T')[0] : '';
        const followUpDate = assignment.followUpDate ? 
          new Date(assignment.followUpDate).toISOString().split('T')[0] : '';
        
        setFormData({
          procedureName: assignment.procedureName || '',
          dentistName: assignment.dentistName || '',
          performedDate: performedDate,
          practiceNotes: assignment.practiceNotes || '',
          customInstructions: Array.isArray(assignment.customInstructions) 
            ? assignment.customInstructions.join('\n') 
            : assignment.customInstructions || '',
          followUpDate: followUpDate
        });
      } else {
        setError('Failed to load procedure assignment data');
      }
    } catch (err) {
      setError('Failed to load procedure assignment. Please try again.');
      console.error('Load assignment error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      // Prepare custom instructions as array
      const customInstructionsArray = formData.customInstructions
        .split('\n')
        .filter(instruction => instruction.trim() !== '');

      const updateData = {
        practiceNotes: formData.practiceNotes,
        customInstructions: customInstructionsArray,
        followUpDate: formData.followUpDate || null,
        performedDate: formData.performedDate
      };

      const response = await practiceApi.updateProcedureAssignment(assignmentId, updateData);
      
      if (response.success) {
        toast({
          title: "Procedure Assignment Updated!",
          description: `${formData.procedureName} assignment has been updated.`,
          variant: "default",
        });
        
        // Navigate back to dashboard
        navigate('/');
      } else {
        setError(response.message || 'Failed to update procedure assignment');
      }
    } catch (err) {
      console.error('Update assignment error:', err);
      
      let errorMessage = 'Failed to update procedure assignment. Please try again.';
      
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map(e => e.msg).join(', ');
        } else if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Dashboard</span>
              </Button>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-gray-600" />
                <h1 className="text-xl font-semibold text-gray-900">Edit Procedure Assignment</h1>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-gray-900">
              Edit Procedure Assignment
            </CardTitle>
            <p className="text-gray-600 mt-2">
              Update procedure notes and instructions for {practice?.name}
            </p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <Alert className="border-red-200 bg-red-50">
                  <AlertDescription className="text-red-800">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              {/* Procedure Information (Read-only) */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-blue-600" />
                  Procedure Information
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      Procedure Name
                    </label>
                    <Input
                      value={formData.procedureName}
                      disabled
                      className="bg-gray-50"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      Performing Dentist
                    </label>
                    <Input
                      value={formData.dentistName}
                      disabled
                      className="bg-gray-50"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      Performed Date
                    </label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        name="performedDate"
                        type="date"
                        value={formData.performedDate}
                        onChange={handleInputChange}
                        className="pl-10"
                        disabled={saving}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      Follow-up Date (Optional)
                    </label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        name="followUpDate"
                        type="date"
                        value={formData.followUpDate}
                        onChange={handleInputChange}
                        className="pl-10"
                        disabled={saving}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Editable Fields */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800">
                  Notes & Instructions
                </h3>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label htmlFor="practiceNotes" className="text-sm font-medium text-gray-700">
                      Practice Notes
                    </label>
                    <Textarea
                      id="practiceNotes"
                      name="practiceNotes"
                      value={formData.practiceNotes}
                      onChange={handleInputChange}
                      placeholder="Add any practice-specific notes about this procedure..."
                      rows={3}
                      disabled={saving}
                    />
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="customInstructions" className="text-sm font-medium text-gray-700">
                      Custom Instructions
                    </label>
                    <Textarea
                      id="customInstructions"
                      name="customInstructions"
                      value={formData.customInstructions}
                      onChange={handleInputChange}
                      placeholder="Add custom post-operative instructions (one per line)..."
                      rows={6}
                      disabled={saving}
                    />
                    <p className="text-xs text-gray-500">
                      Enter each custom instruction on a separate line. These will be added to the standard post-operative instructions.
                    </p>
                  </div>
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3"
                disabled={saving}
              >
                <Save className="h-4 w-4 mr-2" />
                {saving ? 'Updating Assignment...' : 'Update Procedure Assignment'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default EditProcedureAssignmentPage;
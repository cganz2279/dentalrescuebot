import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Textarea } from '../components/ui/textarea';
import { ArrowLeft, FileText, Calendar, Stethoscope, Save, Trash2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import { useToast } from '../hooks/use-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const EditAssignmentPage = () => {
  const navigate = useNavigate();
  const { assignmentId } = useParams();
  const { user } = useAuth();
  const { toast } = useToast();

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [assignmentData, setAssignmentData] = useState(null);

  const [formData, setFormData] = useState({
    performedDate: '',
    dentistName: '',
    practiceNotes: '',
    customInstructions: [''],
    followUpDate: ''
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
        const { assignment, patient, procedure } = response.data;
        setAssignmentData({ assignment, patient, procedure });
        
        // Populate form with existing data
        setFormData({
          performedDate: assignment.performedDate ? 
            new Date(assignment.performedDate).toISOString().split('T')[0] : '',
          dentistName: assignment.dentistName || '',
          practiceNotes: assignment.practiceNotes || '',
          customInstructions: assignment.customInstructions && assignment.customInstructions.length > 0 ? 
            assignment.customInstructions : [''],
          followUpDate: assignment.followUpDate ? 
            new Date(assignment.followUpDate).toISOString().split('T')[0] : ''
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

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleCustomInstructionChange = (index, value) => {
    const newInstructions = [...formData.customInstructions];
    newInstructions[index] = value;
    setFormData({
      ...formData,
      customInstructions: newInstructions
    });
  };

  const addCustomInstruction = () => {
    setFormData({
      ...formData,
      customInstructions: [...formData.customInstructions, '']
    });
  };

  const removeCustomInstruction = (index) => {
    const newInstructions = formData.customInstructions.filter((_, i) => i !== index);
    setFormData({
      ...formData,
      customInstructions: newInstructions.length > 0 ? newInstructions : ['']
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    // Validate required fields
    if (!formData.dentistName) {
      setError('Dentist name is required');
      setSubmitting(false);
      return;
    }

    try {
      // Filter out empty custom instructions
      const cleanInstructions = formData.customInstructions.filter(instruction => instruction.trim() !== '');
      
      const updateData = {
        performedDate: formData.performedDate ? formData.performedDate + 'T00:00:00Z' : null,
        dentistName: formData.dentistName,
        practiceNotes: formData.practiceNotes || null,
        customInstructions: cleanInstructions.length > 0 ? cleanInstructions : null,
        followUpDate: formData.followUpDate ? formData.followUpDate + 'T00:00:00Z' : null
      };

      const response = await practiceApi.updateAssignment(assignmentId, updateData);
      
      if (response.success) {
        toast({
          title: "Assignment Updated Successfully!",
          description: `Changes have been saved for ${assignmentData.patient.firstName} ${assignmentData.patient.lastName}.`,
          variant: "default",
        });

        // Navigate back to dashboard
        navigate('/dashboard');
      } else {
        setError(response.detail || response.message || 'Failed to update assignment');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to update assignment. Please try again.';
      setError(errorMessage);
      console.error('Update assignment error:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this procedure assignment? This action cannot be undone.')) {
      return;
    }

    try {
      setSubmitting(true);
      const response = await practiceApi.deleteAssignment(assignmentId);
      
      if (response.success) {
        toast({
          title: "Assignment Deleted",
          description: "The procedure assignment has been removed.",
          variant: "default",
        });
        navigate('/dashboard');
      } else {
        throw new Error(response.message || 'Failed to delete assignment');
      }
    } catch (err) {
      toast({
        title: "Delete Failed",
        description: err.message || "Failed to delete assignment. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
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
                <FileText className="h-5 w-5 text-gray-600" />
                <h1 className="text-xl font-semibold text-gray-900">Edit Procedure Assignment</h1>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-gray-900">
              Edit Assignment Details
            </CardTitle>
            <p className="text-gray-600 mt-2">
              Modify the post-operative care assignment for {patient.firstName} {patient.lastName}
            </p>
          </CardHeader>
          <CardContent>
            {/* Assignment Overview */}
            <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h3 className="font-semibold text-blue-900 mb-2">Current Assignment</h3>
              <p className="text-blue-800"><strong>Patient:</strong> {patient.firstName} {patient.lastName}</p>
              <p className="text-blue-800"><strong>Procedure:</strong> {assignment.procedureName}</p>
              <p className="text-blue-800"><strong>Specialty:</strong> {procedure.specialtyName}</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8">
              {error && (
                <Alert className="border-red-200 bg-red-50">
                  <AlertDescription className="text-red-800">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              {/* Procedure Details */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                  <Stethoscope className="h-5 w-5 mr-2 text-purple-600" />
                  Procedure Details
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="performedDate">Procedure Date</Label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        id="performedDate"
                        name="performedDate"
                        type="date"
                        value={formData.performedDate}
                        onChange={handleInputChange}
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="dentistName">Dentist Name *</Label>
                    <div className="relative">
                      <Stethoscope className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        id="dentistName"
                        name="dentistName"
                        type="text"
                        required
                        value={formData.dentistName}
                        onChange={handleInputChange}
                        className="pl-10"
                        placeholder="Dr. Smith"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="followUpDate">Follow-up Date (Optional)</Label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        id="followUpDate"
                        name="followUpDate"
                        type="date"
                        value={formData.followUpDate}
                        onChange={handleInputChange}
                        className="pl-10"
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="practiceNotes">Practice Notes (Optional)</Label>
                  <Textarea
                    id="practiceNotes"
                    name="practiceNotes"
                    value={formData.practiceNotes}
                    onChange={handleInputChange}
                    placeholder="Any additional notes for this procedure..."
                    rows={3}
                  />
                </div>
              </div>

              {/* Custom Instructions */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800">
                  Custom Instructions (Optional)
                </h3>
                <p className="text-sm text-gray-600">
                  Add any specific instructions for this patient beyond the standard procedure guidelines
                </p>
                
                {formData.customInstructions.map((instruction, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <Input
                      value={instruction}
                      onChange={(e) => handleCustomInstructionChange(index, e.target.value)}
                      placeholder={`Custom instruction ${index + 1}`}
                      className="flex-1"
                    />
                    {formData.customInstructions.length > 1 && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => removeCustomInstruction(index)}
                      >
                        Remove
                      </Button>
                    )}
                  </div>
                ))}
                
                <Button
                  type="button"
                  variant="outline"
                  onClick={addCustomInstruction}
                  className="w-full"
                >
                  Add Another Instruction
                </Button>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-4">
                <Button 
                  type="submit" 
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3"
                  disabled={submitting}
                >
                  <Save className="h-4 w-4 mr-2" />
                  {submitting ? 'Saving Changes...' : 'Save Changes'}
                </Button>
                
                <Button
                  type="button"
                  variant="destructive"
                  onClick={handleDelete}
                  disabled={submitting}
                  className="py-3"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Assignment
                </Button>
              </div>
            </form>

            <div className="mt-6 text-center">
              <p className="text-xs text-gray-500">
                After saving changes, you can generate a new PDF with the updated information.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default EditAssignmentPage;
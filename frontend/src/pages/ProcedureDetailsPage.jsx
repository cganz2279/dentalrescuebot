import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { ArrowLeft, FileText, User, Calendar, Edit, Save, X, Printer } from 'lucide-react';
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
        procedureName: data.assignment.procedureName,
        patientName: data.patient ? `${data.patient.firstName} ${data.patient.lastName}` : 'Unknown Patient',
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

  const handlePrint = () => {
    // Use browser's built-in print functionality to print this exact page
    window.print();
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
          body * {
            visibility: hidden;
          }
          .printable-content, .printable-content * {
            visibility: visible;
          }
          .printable-content {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
          }
          .no-print {
            display: none !important;
          }
          .print-header {
            display: block !important;
            margin-bottom: 2rem;
          }
          .print-header img {
            max-height: 80px;
            width: auto;
            display: block !important;
            margin: 0 auto 1rem auto;
          }
          .print-header h1 {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: black;
          }
          .print-header p {
            font-size: 1.125rem;
            margin-bottom: 0.25rem;
            color: black;
          }
          .print-header hr {
            border-top: 2px solid black;
            margin: 1rem 0;
          }
        }
        .print-header {
          display: none;
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
                    onClick={handleEdit}
                    className="flex items-center"
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
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
                e.target.src = "https://customer-assets.emergentagent.com/job_dental-healing/artifacts/j7ayzg7r_DentalRescueBotWithRoundedText.png";
              }}
            />
          )}
          {!practice?.logo && (
            <img 
              src="https://customer-assets.emergentagent.com/job_dental-healing/artifacts/j7ayzg7r_DentalRescueBotWithRoundedText.png"
              alt="DentalRescueBot Logo"
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

        {/* Title */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Procedure Details</h2>
          <h3 className="text-xl text-gray-700">{procedureData.procedureName} for {procedureData.patientName}</h3>
        </div>

        {/* Assignment Information */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="h-5 w-5 mr-2 text-blue-600" />
              Assignment Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Patient Details</h3>
                <p className="text-sm text-gray-600">
                  <User className="h-4 w-4 inline mr-2" />
                  {procedureData.patientName}
                </p>
                <p className="text-sm text-gray-600">{procedureData.patientEmail}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Treatment Details</h3>
                
                {/* Performed Date - Editable */}
                <div className="text-sm text-gray-600 mb-1">
                  <Calendar className="h-4 w-4 inline mr-2" />
                  Performed: {isEditing ? (
                    <Input
                      type="date"
                      value={editData.performedDate}
                      onChange={(e) => handleInputChange('performedDate', e.target.value)}
                      className="inline-block w-auto ml-2"
                      size="sm"
                    />
                  ) : (
                    new Date(procedureData.performedDate).toLocaleDateString()
                  )}
                </div>
                
                {/* Follow-up Date - Editable */}
                {(procedureData.followUpDate || isEditing) && (
                  <div className="text-sm text-gray-600 mb-1">
                    Follow-up: {isEditing ? (
                      <Input
                        type="date"
                        value={editData.followUpDate}
                        onChange={(e) => handleInputChange('followUpDate', e.target.value)}
                        className="inline-block w-auto ml-2"
                        size="sm"
                      />
                    ) : (
                      procedureData.followUpDate ? new Date(procedureData.followUpDate).toLocaleDateString() : 'Not set'
                    )}
                  </div>
                )}
                
                {/* Dentist Name - Editable */}
                <div className="text-sm text-gray-600 mb-2">
                  Dentist: {isEditing ? (
                    <Select
                      value={editData.dentistName}
                      onValueChange={(value) => handleInputChange('dentistName', value)}
                    >
                      <SelectTrigger className="inline-block w-auto ml-2 h-8">
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
                    procedureData.dentistName
                  )}
                </div>
                
                {/* Status - Editable */}
                <div>
                  Status: {isEditing ? (
                    <Select
                      value={editData.status}
                      onValueChange={(value) => handleInputChange('status', value)}
                    >
                      <SelectTrigger className="inline-block w-auto ml-2 h-8">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="completed">Completed</SelectItem>
                        <SelectItem value="cancelled">Cancelled</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                    <Badge variant="outline" className="ml-2">{procedureData.status}</Badge>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Practice Notes - Editable */}
        {(procedureData.practiceNotes || isEditing) && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Practice Notes</CardTitle>
            </CardHeader>
            <CardContent>
              {isEditing ? (
                <Textarea
                  value={editData.practiceNotes}
                  onChange={(e) => handleInputChange('practiceNotes', e.target.value)}
                  placeholder="Add practice notes..."
                  rows={3}
                />
              ) : (
                <p className="text-gray-700">{procedureData.practiceNotes}</p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Custom Instructions - Editable */}
        {(procedureData.customInstructions?.length > 0 || isEditing) && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Custom Instructions</CardTitle>
            </CardHeader>
            <CardContent>
              {isEditing ? (
                <Textarea
                  value={editData.customInstructions}
                  onChange={(e) => handleInputChange('customInstructions', e.target.value)}
                  placeholder="Add custom instructions, one per line..."
                  rows={4}
                />
              ) : (
                <ul className="list-disc list-inside space-y-2">
                  {procedureData.customInstructions.map((instruction, index) => (
                    <li key={index} className="text-gray-700">{instruction}</li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        )}

        {/* Post-Operative Care Instructions - Read Only */}
        <Card>
          <CardHeader>
            <CardTitle>Post-Operative Care Instructions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Overview</h4>
                <p className="text-gray-700">{procedureData.procedureDetails.overview}</p>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Immediate Aftercare</h4>
                <ul className="list-disc list-inside space-y-1">
                  {procedureData.procedureDetails.immediateAftercare.map((instruction, index) => (
                    <li key={index} className="text-gray-700">{instruction}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="font-semibold text-red-600 mb-2">⚠️ Warning Signs - Call Your Dentist Immediately</h4>
                <ul className="list-disc list-inside space-y-1">
                  {procedureData.procedureDetails.warningSignsToCallDoctor.map((warning, index) => (
                    <li key={index} className="text-red-700">{warning}</li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ProcedureDetailsPage;
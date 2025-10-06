import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { 
  Users, 
  FileText, 
  Calendar, 
  Settings,
  Plus,
  Download,
  Activity,
  Clock,
  AlertCircle,
  Search,
  X,
  UserPlus,
  Eye,
  User,
  Upload,
  BookOpen,
  CheckCircle,
  HelpCircle
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import LoadingSpinner, { LoadingCard, ErrorMessage } from './LoadingSpinner';
import { useToast } from '../hooks/use-toast';
import CSVImportModal from './CSVImportModal';
import SupportModal from './SupportModal';
import SupportHistory from './SupportHistory';
import TutorialsModal from './TutorialsModal';

const PracticeDashboard = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [realPatients, setRealPatients] = useState([]);  // Store real patients separately
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPatientId, setSelectedPatientId] = useState(null);
  const [patientSearchTerm, setPatientSearchTerm] = useState('');
  const [procedureSearchTerm, setProcedureSearchTerm] = useState('');
  const { user, practice, logout } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    loadDashboard();
  }, []);

  const [showDatePickerModal, setShowDatePickerModal] = useState(false);
  const [exportDateRange, setExportDateRange] = useState({
    startDate: '',
    endDate: '',
    format: 'csv' // csv or excel
  });
  const [followUpStats, setFollowUpStats] = useState(null);
  const [showFollowUpStats, setShowFollowUpStats] = useState(false);
  const [showCSVImportModal, setShowCSVImportModal] = useState(false);
  const [showSupportModal, setShowSupportModal] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard'); // dashboard, support
  const [showTutorialsModal, setShowTutorialsModal] = useState(false);

  const handleExportData = () => {
    setShowDatePickerModal(true);
  };

  const handleImportPatients = () => {
    setShowCSVImportModal(true);
  };

  const handleImportSuccess = (results) => {
    // Reload dashboard to show new patients
    loadDashboard();
    
    toast({
      title: "Import Successful",
      description: `${results.summary.successfulImports} patients have been imported and will appear in Recent Patients.`,
      variant: "default",
    });
  };

  const handleExportWithDateRange = async () => {
    try {
      console.log('🔍 Starting correspondence export with date range:', exportDateRange);
      
      // Prepare export request
      const exportRequest = {
        start_date: exportDateRange.startDate || null,
        end_date: exportDateRange.endDate || null,
        format: exportDateRange.format || 'csv'
      };
      
      console.log('🔍 Export request:', exportRequest);
      
      // Call the new correspondence export API
      const response = await practiceApi.exportCorrespondence(exportRequest);
      
      // Get filename from response headers
      const contentDisposition = response.headers['content-disposition'];
      let filename = `correspondence_export_${Date.now()}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=(.+)/);
        if (filenameMatch) {
          filename = filenameMatch[1].replace(/"/g, '');
        }
      } else {
        // Generate filename based on format and date range
        const startStr = exportDateRange.startDate ? new Date(exportDateRange.startDate).toISOString().split('T')[0] : 'all';
        const endStr = exportDateRange.endDate ? new Date(exportDateRange.endDate).toISOString().split('T')[0] : 'recent';
        const extension = exportDateRange.format === 'excel' ? 'xlsx' : 'csv';
        filename = `correspondence_export_${startStr}_to_${endStr}.${extension}`;
      }
      
      console.log('🔍 Generated filename:', filename);
      
      // Create blob from response data
      const blob = new Blob([response.data], { 
        type: exportDateRange.format === 'excel' 
          ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          : 'text/csv'
      });
      
      // Create download link
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.style.display = 'none';
      
      // Trigger download
      document.body.appendChild(link);
      console.log('🔍 Triggering download...');
      link.click();
      
      // Clean up
      setTimeout(() => {
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        console.log('🔍 Download cleaned up');
      }, 100);
      
      toast({
        title: "Export Complete",
        description: `Correspondence data exported successfully as ${exportDateRange.format.toUpperCase()} file: ${filename}`,
        variant: "default",
      });
      
      setShowDatePickerModal(false);
      
    } catch (error) {
      console.error('🔍 Export error:', error);
      
      let errorMessage = "Failed to export correspondence data. Please try again.";
      if (error.response?.status === 400) {
        errorMessage = "Invalid date range. Please check your dates and try again.";
      } else if (error.response?.status === 403) {
        errorMessage = "You don't have permission to export data.";
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      toast({
        title: "Export Failed",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  const handleOpenProcedure = (procedureId) => {
    // Navigate to procedure details page
    navigate(`/procedure-details/${procedureId}`);
  };

  const handleEditProcedure = (procedureId) => {
    console.log('🔧 handleEditProcedure called with ID:', procedureId);
    // Navigate to procedure details page where they can edit the actual procedure content
    navigate(`/procedure-details/${procedureId}`);
  };

  // Helper function to create printable HTML content
  const createPrintableHTML = (procedure, patient, practice, procedureContent) => {
    const patientName = patient ? `${patient.firstName} ${patient.lastName}` : procedure.patientName || 'Unknown Patient';
    const practiceName = practice?.name || 'Dental Practice';
    const practicePhone = practice?.phone || practice?.emergencyContact || 'Contact Number Not Available';
    const practiceOfficeHours = practice?.officeHours || 'Contact office for hours';
    const practiceEmergencyContact = practice?.emergencyContact || practice?.phone || 'Contact Number Not Available';
    
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Post-Operative Instructions - ${procedure.procedureName}</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 40px;
            color: #333;
          }
          .header {
            text-align: center;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
          }
          .practice-logo {
            max-height: 80px;
            margin-bottom: 10px;
          }
          .practice-name {
            font-size: 24px;
            font-weight: bold;
            color: #2563eb;
            margin: 10px 0;
          }
          .practice-info {
            font-size: 14px;
            color: #666;
          }
          .patient-info {
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
          }
          .procedure-title {
            font-size: 20px;
            font-weight: bold;
            color: #1e40af;
            margin-bottom: 20px;
          }
          .content {
            margin-bottom: 30px;
          }
          .emergency-contact {
            background: #fef2f2;
            border: 1px solid #fecaca;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
          }
          .emergency-title {
            font-weight: bold;
            color: #dc2626;
            margin-bottom: 10px;
          }
          @media print {
            body { margin: 20px; }
            .no-print { display: none; }
          }
        </style>
      </head>
      <body>
        <div class="header">
          ${practice?.branding?.logo ? `<img src="${practice.branding.logo}" alt="${practiceName} Logo" class="practice-logo">` : ''}
          <div class="practice-name">${practiceName}</div>
          <div class="practice-info">
            Phone: ${practicePhone}<br>
            Office Hours: ${practiceOfficeHours}
          </div>
        </div>
        
        <div class="patient-info">
          <strong>Patient:</strong> ${patientName}<br>
          <strong>Procedure:</strong> ${procedure.procedureName}<br>
          <strong>Doctor:</strong> ${patient?.primaryDentist || procedure.dentistName || 'Unknown Doctor'}<br>
          <strong>Date:</strong> ${new Date(procedure.performedDate).toLocaleDateString()}
        </div>
        
        <div class="procedure-title">Post-Operative Instructions: ${procedure.procedureName}</div>
        
        <div class="content">
          ${procedureContent || 'Please follow the standard post-operative care instructions provided by your dentist.'}
        </div>
        
        <div class="emergency-contact">
          <div class="emergency-title">Emergency Contact Information</div>
          <strong>Emergency Phone:</strong> ${practiceEmergencyContact}<br>
          <strong>Office Hours:</strong> ${practiceOfficeHours}
        </div>
      </body>
      </html>
    `;
  };

  const handlePrintProcedure = async (procedureId) => {
    try {
      const procedure = dashboardData?.recentProcedures?.find(p => p.id === procedureId);
      if (!procedure) {
        console.error('Procedure not found for printing');
        return;
      }

      // Find patient data for logging purposes
      const patient = procedure.patientId ? 
        dashboardData?.recentPatients?.find(p => p.id === procedure.patientId) : null;

      // Ensure we have the latest practice data with branding
      let currentPractice = practice;
      console.log('🔍 Current practice logo:', practice?.branding?.logo);
      
      if (!practice?.branding?.logo) {
        try {
          console.log('🔄 Refreshing practice branding data for printing...');
          const token = localStorage.getItem('dentalToken');
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/dashboard`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });
          if (response.ok) {
            const dashboardResponse = await response.json();
            if (dashboardResponse.success && dashboardResponse.data?.practice?.branding?.logo) {
              currentPractice = dashboardResponse.data.practice;
              console.log('✅ Updated practice branding for printing:', currentPractice.branding.logo);
            } else {
              console.log('⚠️ No branding data found in dashboard response');
            }
          }
        } catch (brandingError) {
          console.log('⚠️ Could not fetch updated branding data:', brandingError);
        }
      } else {
        console.log('✅ Using existing practice logo for printing');
      }

      // Get the full procedure content from API
      let procedureContent = '';
      try {
        const response = await practiceApi.getPracticeProcedures();
        if (response.success && response.procedures) {
          const fullProcedure = response.procedures.find(p => p.id === procedure.procedureId) ||
                               response.procedures.find(p => p.name === procedure.procedureName);
          if (fullProcedure) {
            procedureContent = fullProcedure.overview || fullProcedure.content || '';
          }
        }
      } catch (apiError) {
        console.error('Failed to fetch procedure content:', apiError);
      }

      // Create a printable HTML version with current practice data
      const printContent = createPrintableHTML(procedure, patient, currentPractice, procedureContent);
      
      // Create a new window for printing
      const printWindow = window.open('', '_blank');
      printWindow.document.write(printContent);
      printWindow.document.close();
      
      // Wait for content to load, then print
      printWindow.onload = () => {
        printWindow.print();
        printWindow.onafterprint = () => {
          printWindow.close();
        };
      };

      // Log the print activity
      try {
        await practiceApi.logActivity({
          patientId: procedure.patientId,
          patientName: patient ? `${patient.firstName} ${patient.lastName}` : procedure.patientName || 'Unknown Patient',
          patientEmail: patient?.email || 'Unknown Email',
          procedureId: procedure.id,
          procedureName: procedure.procedureName || procedure.name,
          dentistName: patient?.primaryDentist || procedure.dentistName || 'Unknown Doctor',
          activityType: 'print',
          additionalData: { directPrint: true }
        });
      } catch (logError) {
        console.error('Failed to log print activity:', logError);
        // Don't fail the main operation if logging fails
      }

      // Mark as delivered and schedule 24-hour follow-up
      try {
        await handleMarkAsDelivered(procedure.id, procedure.procedureName || procedure.name);
        
        toast({
          title: "Print Completed",
          description: "Instructions printed - Follow-up scheduled in 24 hours",
        });
      } catch (deliveredError) {
        console.error('Failed to mark as delivered after print:', deliveredError);
        // Still show success for the print operation
        toast({
          title: "Print Completed", 
          description: "Instructions printed successfully",
        });
      }

    } catch (error) {
      console.error('Print procedure error:', error);
      toast({
        title: "Print Failed",
        description: "Unable to print the procedure instructions. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleEmailPDF = async (procedureId) => {
    console.log('🔥 EMAIL BUTTON CLICKED:', procedureId);
    console.log('🔍 Dashboard data:', dashboardData);
    console.log('🔍 Available procedures:', dashboardData?.recentProcedures);
    
    try {
      const procedure = dashboardData?.recentProcedures?.find(p => p.id === procedureId);
      if (!procedure) {
        console.error('Procedure not found for email');
        console.log('🔍 Looking for procedureId:', procedureId);
        console.log('🔍 Available procedure IDs:', dashboardData?.recentProcedures?.map(p => p.id));
        return;
      }

      // Try to find patient email from recentPatients data using patientId
      let patientEmail = procedure.patientEmail;
      
      // Find patient data for logging purposes
      const patient = procedure.patientId ? 
        dashboardData?.recentPatients?.find(p => p.id === procedure.patientId) : null;
      
      if (!patientEmail && procedure.patientId) {
        console.log('🔍 Looking for patient email using patientId:', procedure.patientId);
        console.log('🔍 Available recentPatients:', dashboardData?.recentPatients);
        console.log('🔍 Found patient:', patient);
        
        if (patient) {
          patientEmail = patient.email;
          console.log('🔍 Patient email found:', patientEmail);
        }
      }

      if (!patientEmail) {
        console.log('🔍 Procedure object:', procedure);
        console.log('🔍 All procedure keys:', Object.keys(procedure));
        console.log('🔍 patientEmail field:', procedure.patientEmail);
        console.log('🔍 email field:', procedure.email);
        console.log('🔍 patient field:', procedure.patient);
        console.log('🔍 patientDetails field:', procedure.patientDetails);
        
        toast({
          title: "Error",
          description: "Patient email not available for this procedure",
          variant: "destructive",
        });
        return;
      }

      // Call backend API to send email
      console.log('📧 Calling email API with:', {
        patientEmail: patientEmail,
        procedureId: procedure.id,
        procedureName: procedure.procedureName || procedure.name
      });
      
      const response = await practiceApi.emailPDF({
        patientEmail: patientEmail,
        procedureId: procedure.id,
        procedureName: procedure.procedureName || procedure.name
      });

      console.log('📧 Email API response:', response);

      if (response.success) {
        // Log the email activity
        try {
          await practiceApi.logActivity({
            patientId: procedure.patientId,
            patientName: patient ? `${patient.firstName} ${patient.lastName}` : procedure.patientName || 'Unknown Patient',
            patientEmail: patientEmail,
            procedureId: procedure.id,
            procedureName: procedure.procedureName || procedure.name,
            dentistName: patient?.primaryDentist || procedure.dentistName || 'Unknown Doctor',
            activityType: 'email',
            additionalData: { emailAddress: patientEmail }
          });
        } catch (logError) {
          console.error('Failed to log email activity:', logError);
          // Don't fail the main operation if logging fails
        }

        // Mark as delivered and schedule 24-hour follow-up
        try {
          await handleMarkAsDelivered(procedure.id, procedure.procedureName || procedure.name);
        } catch (deliveredError) {
          console.error('Failed to mark as delivered after email:', deliveredError);
          // Don't fail the main operation if this fails
        }

        toast({
          title: "Email Sent",
          description: `PDF instructions sent to ${patientEmail} - Follow-up scheduled in 24 hours`,
          variant: "default",
        });
      }
      
    } catch (error) {
      console.error('Error sending PDF email:', error);
      toast({
        title: "Email Failed",
        description: error.response?.data?.detail || "Failed to send PDF email",
        variant: "destructive",
      });
    }
  };

  const handleSMSPDF = async (procedureId) => {
    console.log('📱 SMS BUTTON CLICKED:', procedureId);
    
    try {
      const procedure = dashboardData?.recentProcedures?.find(p => p.id === procedureId);
      if (!procedure) {
        console.error('Procedure not found for SMS');
        return;
      }

      console.log('🔍 Complete procedure object:', procedure);
      console.log('🔍 Procedure patientId:', procedure.patientId);
      console.log('🔍 Procedure patientName:', procedure.patientName);

      // Try to find patient cellphone from recentPatients data using patientId
      let patientCellphone = null;
      
      if (procedure.patientId) {
        console.log('🔍 Looking for patient cellphone using patientId:', procedure.patientId);
        console.log('🔍 Available patients in recentPatients:', dashboardData?.recentPatients?.map(p => ({id: p.id, name: `${p.firstName} ${p.lastName}`})));
        
        const patient = dashboardData?.recentPatients?.find(p => p.id === procedure.patientId);
        console.log('🔍 Found patient:', patient);
        
        if (patient) {
          patientCellphone = patient.cellphone || patient.phone; // Handle both field names
          console.log('🔍 Patient cellphone found:', patientCellphone);
          console.log('🔍 Complete patient object:', patient);
          console.log('🔍 Patient cellphone field specifically:', patient.cellphone);
          console.log('🔍 Patient phone field specifically:', patient.phone);
        }
      }

      if (!patientCellphone) {
        toast({
          title: "Error",
          description: "Patient cellphone number not available for this procedure",
          variant: "destructive",
        });
        return;
      }

      // Call backend API to send SMS
      console.log('📱 Calling SMS API with:', {
        patientCellphone: patientCellphone,
        procedureId: procedure.id,
        procedureName: procedure.procedureName || procedure.name
      });
      
      const response = await practiceApi.smsPDF({
        patientCellphone: patientCellphone,
        procedureId: procedure.id,
        procedureName: procedure.procedureName || procedure.name
      });

      console.log('📱 SMS API response:', response);

      if (response.success) {
        // Log the SMS activity
        try {
          await practiceApi.logActivity({
            patientId: procedure.patientId,
            patientName: patient ? `${patient.firstName} ${patient.lastName}` : procedure.patientName || 'Unknown Patient',
            patientEmail: patient?.email || 'Unknown Email',
            procedureId: procedure.id,
            procedureName: procedure.procedureName || procedure.name,
            dentistName: patient?.primaryDentist || procedure.dentistName || 'Unknown Doctor',
            activityType: 'sms',
            additionalData: { cellphone: patientCellphone }
          });
        } catch (logError) {
          console.error('Failed to log SMS activity:', logError);
          // Don't fail the main operation if logging fails
        }

        // Mark as delivered and schedule 24-hour follow-up
        try {
          await handleMarkAsDelivered(procedure.id, procedure.procedureName || procedure.name);
        } catch (deliveredError) {
          console.error('Failed to mark as delivered after SMS:', deliveredError);
          // Don't fail the main operation if this fails
        }

        toast({
          title: "SMS Sent",
          description: `PDF link sent to ${response.patientCellphone} - Follow-up scheduled in 24 hours`,
          variant: "default",
        });
      }
      
    } catch (error) {
      console.error('Error sending SMS:', error);
      console.log('🔍 Error response status:', error.response?.status);
      console.log('🔍 Error response data:', error.response?.data);
      console.log('🔍 Error response detail:', error.response?.data?.detail);
      
      // Check if it's a Twilio trial account limitation
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('Twilio trial account limitation')) {
        const errorDetail = error.response.data.detail;
        const linkMatch = errorDetail.match(/https:\/\/[^\s]+/);
        const secureLink = linkMatch ? linkMatch[0] : null;
        
        console.log('🔍 Detected Twilio trial limitation');
        console.log('🔍 Error detail:', errorDetail);
        console.log('🔍 Secure link extracted:', secureLink);
        
        toast({
          title: "SMS Limited (Trial Account)",
          description: secureLink ? 
            `SMS cannot be sent due to trial account restrictions. However, you can share this link directly: ${secureLink}` :
            errorDetail,
          variant: "default",
          duration: 10000, // Show longer for link copying
        });
      } else {
        toast({
          title: "SMS Failed",
          description: error.response?.data?.detail || "Failed to send SMS with PDF link",
          variant: "destructive",
        });
      }
    }
  };

  const handlePatientClick = (patientId) => {
    // Toggle patient selection - if same patient clicked, deselect
    if (selectedPatientId === patientId) {
      setSelectedPatientId(null);
    } else {
      setSelectedPatientId(patientId);
    }
    // Clear search when patient is selected
    setPatientSearchTerm('');
    setProcedureSearchTerm('');
  };

  const handleClearFilters = () => {
    setSelectedPatientId(null);
    setPatientSearchTerm('');
    setProcedureSearchTerm('');
  };

  const handleMarkAsDelivered = async (procedureId, procedureName) => {
    try {
      console.log('📦 Marking procedure as delivered:', procedureId, procedureName);
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/practice/assignment/${procedureId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ status: 'delivered' })
      });

      if (response.ok) {
        // Reload dashboard to update the count and status
        loadDashboard();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to update status');
      }
    } catch (error) {
      console.error('❌ Error marking as delivered:', error);
      toast({
        title: "Error",
        description: `Failed to mark ${procedureName} as delivered: ${error.message}`,
        variant: "destructive",
      });
    }
  };

  const loadFollowUpStats = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/practice/followup-stats`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setFollowUpStats(data.data);
        }
      } else {
        console.error('Failed to load follow-up stats');
      }
    } catch (error) {
      console.error('❌ Error loading follow-up stats:', error);
    }
  };

  // Filter and sort real patients only - search by patient name or email
  const filteredRealPatients = realPatients?.filter(patient => {
    if (patientSearchTerm) {
      const searchLower = patientSearchTerm.toLowerCase();
      return (
        patient.firstName?.toLowerCase().includes(searchLower) ||
        patient.lastName?.toLowerCase().includes(searchLower) ||
        patient.email?.toLowerCase().includes(searchLower)
      );
    }
    return true; // Show all real patients when no search term
  })
  .sort((a, b) => {
    // Sort by last name alphabetically
    return a.lastName.localeCompare(b.lastName);
  }) || [];

  // Filter procedures based on selected patient and search term
  const filteredProcedures = dashboardData?.recentProcedures?.filter(procedure => {
    // Filter by selected patient
    if (selectedPatientId && procedure.patientId !== selectedPatientId) {
      return false;
    }
    
    // Filter by search term
    if (procedureSearchTerm) {
      const searchLower = procedureSearchTerm.toLowerCase();
      return (
        procedure.procedureName.toLowerCase().includes(searchLower) ||
        procedure.dentistName.toLowerCase().includes(searchLower) ||
        (procedure.patientName && procedure.patientName.toLowerCase().includes(searchLower))
      );
    }
    
    return true;
  }) || [];

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load dashboard data and real patients separately
      const [dashboardResponse, patientsResponse] = await Promise.all([
        practiceApi.getDashboard(),
        practiceApi.getPatients()
      ]);
      
      setDashboardData(dashboardResponse.data);
      
      // Get all patients (removed Gmail restriction)
      const allPatients = patientsResponse.data;
      
      // Add status to all patients
      const allPatientsWithStatus = allPatients.map(patient => ({
        ...patient,
        status: patient.isActive !== false ? 'Active' : 'Inactive'
      }));
      
      setRealPatients(allPatientsWithStatus);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load dashboard');
      toast({
        title: "Error",
        description: "Failed to load dashboard data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex justify-center items-center py-32">
            <LoadingSpinner size="xl" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <ErrorMessage message={error} onRetry={loadDashboard} />
        </div>
      </div>
    );
  }

  const getSubscriptionStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'trial': return 'bg-blue-100 text-blue-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              {/* Practice Logo - use custom logo if available */}
              {(practice?.branding?.logo || practice?.logo) ? (
                <img 
                  src={practice.branding?.logo || practice.logo}
                  alt={`${practice.name || 'Practice'} Logo`}
                  className="h-12 w-auto object-contain"
                  onError={(e) => {
                    console.error('Custom logo failed to load, falling back to default');
                    e.target.src = "https://customer-assets.emergentagent.com/job_dentist-dashboard-2/artifacts/tjqph8wg_ChatGPT%20Image%20Sep%2028%2C%202025%2C%2011_41_56%20PM.png";
                  }}
                />
              ) : (
                <img 
                  src="https://customer-assets.emergentagent.com/job_dentist-dashboard-2/artifacts/tjqph8wg_ChatGPT%20Image%20Sep%2028%2C%202025%2C%2011_41_56%20PM.png"
                  alt="Dental Aftercare Notes Logo"
                  className="h-12 w-auto"
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              )}
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {dashboardData?.practice?.name || 'Practice Dashboard'}
                </h1>
                <p className="text-gray-600">
                  Welcome back, {user?.firstName}!
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge className={getSubscriptionStatusColor(dashboardData?.stats?.subscriptionStatus)}>
                {dashboardData?.stats?.subscriptionStatus?.toUpperCase() || ''}
              </Badge>
              <Button variant="outline" onClick={logout}>
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Export Correspondence Modal */}
      {showDatePickerModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Export Patient Correspondence</h3>
            <p className="text-sm text-gray-600 mb-4">
              Export all patient correspondence including patient name, email, date sent, procedure, doctor name, and status. Leave date fields empty to export all data.
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date (Optional)
                </label>
                <input
                  type="date"
                  value={exportDateRange.startDate}
                  onChange={(e) => setExportDateRange(prev => ({ ...prev, startDate: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Date (Optional)
                </label>
                <input
                  type="date"
                  value={exportDateRange.endDate}
                  onChange={(e) => setExportDateRange(prev => ({ ...prev, endDate: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Export Format
                </label>
                <select
                  value={exportDateRange.format}
                  onChange={(e) => setExportDateRange(prev => ({ ...prev, format: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="csv">CSV (.csv)</option>
                  <option value="excel">Excel (.xlsx)</option>
                </select>
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <Button
                onClick={handleExportWithDateRange}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
              >
                Export {exportDateRange.format.toUpperCase()}
              </Button>
              <Button
                onClick={() => setShowDatePickerModal(false)}
                variant="outline"
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* CSV Import Modal */}
      <CSVImportModal
        isOpen={showCSVImportModal}
        onClose={() => setShowCSVImportModal(false)}
        onSuccess={handleImportSuccess}
      />

      {/* Tutorials Modal */}
      <TutorialsModal
        isOpen={showTutorialsModal}
        onClose={() => setShowTutorialsModal(false)}
      />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {currentView === 'dashboard' && (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Patients</CardTitle>
              <Users className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats?.patientCount || 0}</div>
              <p className="text-xs text-gray-600">Registered patients</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Procedures</CardTitle>
              <FileText className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats?.activeProcedures || 0}</div>
              <p className="text-xs text-gray-600">Current post-op care</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Subscription</CardTitle>
              <Activity className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold capitalize">
                {dashboardData?.stats?.subscriptionStatus || ''}
              </div>
              <p className="text-xs text-gray-600">Current plan status</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-7 gap-4 mb-8">
          <Button 
            onClick={() => navigate('/add-patient')}
            className="bg-blue-600 hover:bg-blue-700 text-white h-20 flex flex-col"
          >
            <Plus className="h-6 w-6 mb-2" />
            Add Patient
          </Button>
          <Button 
            onClick={() => navigate('/assign-procedure')}
            variant="outline" 
            className="h-20 flex flex-col"
          >
            <FileText className="h-6 w-6 mb-2" />
            Assign Procedure
          </Button>
          <Button 
            onClick={() => navigate('/procedure-library')}
            className="bg-purple-600 hover:bg-purple-700 text-white h-20 flex flex-col"
          >
            <FileText className="h-6 w-6 mb-2" />
            <span className="font-medium">Procedure Library</span>
            <span className="text-xs opacity-90">View & Print Docs</span>
          </Button>
          <Button 
            onClick={() => setShowTutorialsModal(true)}
            className="bg-green-600 hover:bg-green-700 text-white h-20 flex flex-col"
          >
            <BookOpen className="h-6 w-6 mb-2" />
            <span className="font-medium">Tutorials</span>
            <span className="text-xs opacity-90">Learn the App</span>
          </Button>
          <Button 
            onClick={() => navigate('/practice-settings')}
            variant="outline" 
            className="h-20 flex flex-col"
          >
            <Settings className="h-6 w-6 mb-2" />
            Practice Settings
          </Button>
          <Button 
            onClick={() => navigate('/practice-settings')}
            className="bg-indigo-600 hover:bg-indigo-700 text-white h-20 flex flex-col"
          >
            <Users className="h-6 w-6 mb-2" />
            <span className="font-medium">Manage Dentists</span>
            <span className="text-xs opacity-90">Add & Edit Dentists</span>
          </Button>
          <Button 
            onClick={() => navigate('/patient-management')}
            className="bg-green-600 hover:bg-green-700 text-white h-20 flex flex-col"
          >
            <Users className="h-6 w-6 mb-2" />
            <span className="font-medium">Manage Patients</span>
            <span className="text-xs opacity-90">Search & View Records</span>
          </Button>
          <Button 
            onClick={handleImportPatients}
            className="bg-green-600 hover:bg-green-700 text-white h-20 flex flex-col"
          >
            <Upload className="h-6 w-6 mb-2" />
            <span className="font-medium">Import Patients</span>
            <span className="text-xs opacity-90">Upload CSV File</span>
          </Button>
          <Button 
            onClick={handleExportData}
            variant="outline" 
            className="h-20 flex flex-col"
          >
            <Download className="h-6 w-6 mb-2" />
            <span className="font-medium">Export Data</span>
            <span className="text-xs text-gray-600">CSV & Excel</span>
          </Button>
          <Button 
            onClick={() => {
              setShowFollowUpStats(!showFollowUpStats);
              if (!showFollowUpStats && !followUpStats) {
                loadFollowUpStats();
              }
            }} 
            variant="outline" 
            className="h-20 flex flex-col"
          >
            <Activity className="h-6 w-6 mb-2" />
            <span className="font-medium">Follow-up Stats</span>
            <span className="text-xs text-gray-600">{showFollowUpStats ? 'Hide Stats' : 'View Stats'}</span>
          </Button>
          <Button 
            onClick={() => setShowSupportModal(true)}
            className="bg-orange-600 hover:bg-orange-700 text-white h-20 flex flex-col"
          >
            <HelpCircle className="h-6 w-6 mb-2" />
            <span className="font-medium">Get Help</span>
            <span className="text-xs opacity-90">Support & Suggestions</span>
          </Button>
          <Button 
            onClick={() => setCurrentView(currentView === 'support' ? 'dashboard' : 'support')}
            variant="outline"
            className="h-20 flex flex-col"
          >
            <FileText className="h-6 w-6 mb-2" />
            <span className="font-medium">Support History</span>
            <span className="text-xs text-gray-600">{currentView === 'support' ? 'Back to Dashboard' : 'View Requests'}</span>
          </Button>
        </div>

        {/* Follow-up Stats Section */}
        {showFollowUpStats && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Activity className="h-5 w-5 mr-2 text-purple-600" />
                Follow-up Statistics
              </CardTitle>
            </CardHeader>
            <CardContent>
              {followUpStats ? (
                <div className="space-y-6">
                  {/* Follow-up Email Stats */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-3">Follow-up Email Status</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-yellow-800">Scheduled</p>
                            <p className="text-2xl font-bold text-yellow-900">{followUpStats.scheduled || 0}</p>
                          </div>
                          <div className="h-8 w-8 bg-yellow-100 rounded-full flex items-center justify-center">
                            <Clock className="h-4 w-4 text-yellow-600" />
                          </div>
                        </div>
                      </div>
                      
                      <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-green-800">Sent Successfully</p>
                            <p className="text-2xl font-bold text-green-900">{followUpStats.sent || 0}</p>
                          </div>
                          <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                            <Activity className="h-4 w-4 text-green-600" />
                          </div>
                        </div>
                      </div>
                      
                      <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-red-800">Failed</p>
                            <p className="text-2xl font-bold text-red-900">{followUpStats.failed || 0}</p>
                          </div>
                          <div className="h-8 w-8 bg-red-100 rounded-full flex items-center justify-center">
                            <AlertCircle className="h-4 w-4 text-red-600" />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Procedure Sequence Status */}
                  {followUpStats.procedure_stats && (
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 mb-3">Procedure Sequence Status</h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-blue-800">Active</p>
                              <p className="text-xs text-blue-600">Not delivered yet</p>
                              <p className="text-2xl font-bold text-blue-900">{followUpStats.procedure_stats.active || 0}</p>
                            </div>
                            <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                              <Activity className="h-4 w-4 text-blue-600" />
                            </div>
                          </div>
                        </div>
                        
                        <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-indigo-800">Delivered</p>
                              <p className="text-xs text-indigo-600">Follow-up scheduled</p>
                              <p className="text-2xl font-bold text-indigo-900">{followUpStats.procedure_stats.delivered || 0}</p>
                            </div>
                            <div className="h-8 w-8 bg-indigo-100 rounded-full flex items-center justify-center">
                              <Clock className="h-4 w-4 text-indigo-600" />
                            </div>
                          </div>
                        </div>
                        
                        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-purple-800">Second</p>
                              <p className="text-xs text-purple-600">Follow-up sent</p>
                              <p className="text-2xl font-bold text-purple-900">{followUpStats.procedure_stats.second || 0}</p>
                            </div>
                            <div className="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center">
                              <CheckCircle className="h-4 w-4 text-purple-600" />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center py-8">
                  <div className="text-center">
                    <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">Loading follow-up statistics...</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Patients */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <Users className="h-5 w-5 mr-2 text-blue-600" />
                  Recent Patients
                  {patientSearchTerm && (
                    <Badge variant="outline" className="ml-2">
                      Search: "{patientSearchTerm}"
                    </Badge>
                  )}
                </CardTitle>
                {patientSearchTerm && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPatientSearchTerm('')}
                    className="text-xs"
                  >
                    <X className="h-3 w-3 mr-1" />
                    Clear Search
                  </Button>
                )}
              </div>
              
              {/* Search Box */}
              <div className="relative mt-4">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Search patients by name or email..."
                  value={patientSearchTerm}
                  onChange={(e) => setPatientSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              
              {/* Filter Info */}
              <div className="flex items-center justify-end mt-3">
                <div className="text-xs text-gray-500">
                  {filteredRealPatients.length} patients shown
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {filteredRealPatients.length > 0 ? (
                <div className="space-y-4">
                  {filteredRealPatients.map((patient) => (
                    <div 
                      key={patient.id} 
                      onClick={() => handlePatientClick(patient.id)}
                      className={`flex justify-between items-center p-4 rounded-lg cursor-pointer transition-colors border ${
                        selectedPatientId === patient.id 
                          ? 'bg-blue-100 border-2 border-blue-300' 
                          : 'bg-gray-50 hover:bg-gray-100'
                      }`}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-lg">{patient.firstName} {patient.lastName}</h4>
                          <Badge 
                            variant={patient.status === 'Active' ? 'default' : 'secondary'}
                            className={`text-xs ${
                              patient.status === 'Active' 
                                ? 'bg-green-100 text-green-800 border-green-200' 
                                : 'bg-gray-100 text-gray-600 border-gray-200'
                            }`}
                          >
                            {patient.status || 'Active'}
                          </Badge>
                          {/* Real Patient badge removed - all patients are real */}
                        </div>
                        
                        <div className="space-y-1 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <User className="h-4 w-4" />
                            <span>{patient.email}</span>
                          </div>
                          
                          {patient.lastLoginAt && (
                            <div className="flex items-center gap-1">
                              <Calendar className="h-4 w-4" />
                              <span>Last login: {new Date(patient.lastLoginAt).toLocaleDateString()}</span>
                            </div>
                          )}
                          
                          {patient.status === 'Inactive' && patient.deactivatedAt && (
                            <div className="flex items-center gap-1 text-red-600">
                              <AlertCircle className="h-4 w-4" />
                              <span>Deactivated: {new Date(patient.deactivatedAt).toLocaleDateString()}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center">
                        <div className={`flex items-center ${selectedPatientId === patient.id ? 'text-blue-600' : 'text-gray-400'}`}>
                          <Users className="h-5 w-5" />
                          {selectedPatientId === patient.id && (
                            <span className="ml-2 text-xs font-medium">Selected</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-lg mb-2">No patients found</p>
                  <p className="text-sm">
                    {patientSearchTerm 
                      ? `No patients match "${patientSearchTerm}"`
                      : "No patients found"
                    }
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Procedures */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-green-600" />
                  Recent Procedures
                  {selectedPatientId && (
                    <Badge variant="outline" className="ml-2">
                      Patient Filtered
                    </Badge>
                  )}
                </CardTitle>
                {selectedPatientId && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleClearFilters}
                    className="text-xs"
                  >
                    <X className="h-3 w-3 mr-1" />
                    Clear Filter
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {filteredProcedures.length > 0 ? (
                <div className="space-y-4">
                  {filteredProcedures.map((procedure) => (
                    <div key={procedure.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <p className="font-medium">{procedure.procedureName}</p>
                        <p className="text-sm text-gray-600">
                          {procedure.dentistName && procedure.dentistName.startsWith('Dr.') 
                            ? procedure.dentistName 
                            : `Dr. ${procedure.dentistName}`}
                        </p>
                        <p className="text-xs text-gray-500">
                          Patient: {procedure.patientName || ''}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="text-right mr-3">
                          <Badge 
                            variant="outline" 
                            className={`mb-1 ${
                              procedure.status === 'second' 
                                ? 'bg-purple-100 text-purple-800 border-purple-300'
                                : procedure.status === 'delivered' 
                                ? 'bg-blue-100 text-blue-800 border-blue-300' 
                                : 'bg-green-100 text-green-800 border-green-300'
                            }`}
                          >
                            {procedure.status === 'second' ? 'Second' : 
                             procedure.status === 'delivered' ? 'Delivered' : 'Active'}
                          </Badge>
                          {procedure.followUpStatus && (
                            <Badge 
                              variant="outline" 
                              className={`mb-1 ml-1 text-xs ${
                                procedure.followUpStatus === 'sent' 
                                  ? 'bg-purple-100 text-purple-800 border-purple-300' 
                                  : procedure.followUpStatus === 'scheduled'
                                  ? 'bg-yellow-100 text-yellow-800 border-yellow-300'
                                  : 'bg-gray-100 text-gray-800 border-gray-300'
                              }`}
                            >
                              {procedure.followUpStatus === 'sent' ? 'Follow-up Sent' : 
                               procedure.followUpStatus === 'scheduled' ? 'Follow-up Scheduled' : 
                               'Follow-up Failed'}
                            </Badge>
                          )}
                          <p className="text-xs text-gray-400">
                            {new Date(procedure.performedDate).toLocaleDateString()}
                          </p>
                          {procedure.followUpSentAt && (
                            <p className="text-xs text-purple-500">
                              Follow-up: {new Date(procedure.followUpSentAt).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                        <div className="flex flex-col space-y-1">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleOpenProcedure(procedure.id)}
                            className="text-xs px-2 py-1 h-7"
                          >
                            Open
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleEditProcedure(procedure.id)}
                            className="text-xs px-2 py-1 h-7"
                          >
                            Edit
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handlePrintProcedure(procedure.id)}
                            className="text-xs px-2 py-1 h-7"
                          >
                            Print
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleEmailPDF(procedure.id)}
                            className="text-xs px-2 py-1 h-7"
                          >
                            Email
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleSMSPDF(procedure.id)}
                            className="text-xs px-2 py-1 h-7 bg-green-50 text-green-700 hover:bg-green-100"
                          >
                            Text
                          </Button>
                          {/* Mark Delivered button removed - status changes automatically when Print/Email/SMS is used */}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  {selectedPatientId ? (
                    <div>
                      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p>No procedures found for selected patient</p>
                      <Button
                        onClick={() => navigate('/assign-procedure')}
                        className="mt-2"
                        size="sm"
                      >
                        Assign Procedure
                      </Button>
                    </div>
                  ) : (
                    <div>
                      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p>No procedures assigned yet</p>
                      <Button
                        onClick={() => navigate('/assign-procedure')}
                        className="mt-2"
                        size="sm"
                      >
                        Assign First Procedure
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
          </>
        )}

        {/* Support History Section */}
        {currentView === 'support' && (
          <div className="mt-8">
            <SupportHistory />
          </div>
        )}

        {/* Trial Notice - only show on dashboard view */}
        {currentView === 'dashboard' && dashboardData?.stats?.subscriptionStatus === 'trial' && (
          <Card className="mt-8 border-blue-200 bg-blue-50">
            <CardContent className="pt-6">
              <div className="flex items-center">
                <AlertCircle className="h-5 w-5 text-blue-600 mr-3" />
                <div className="flex-1">
                  <h3 className="font-semibold text-blue-900">Free Trial Active</h3>
                  <p className="text-blue-800 text-sm">
                    Your 15-day free trial is active. Subscribe to continue using DentalRescueBot after your trial ends.
                  </p>
                </div>
                <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                  Subscribe for $49/month
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
      
      {/* Support Modal */}
      <SupportModal
        isOpen={showSupportModal}
        onClose={() => setShowSupportModal(false)}
        practiceData={practice}
      />
    </div>
  );
};

export default PracticeDashboard;
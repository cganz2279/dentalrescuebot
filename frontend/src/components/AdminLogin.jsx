import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { 
  Building2, 
  Users, 
  DollarSign, 
  AlertTriangle, 
  Eye, 
  EyeOff,
  UserX, 
  CheckCircle, 
  XCircle,
  Settings,
  BarChart3,
  FileText,
  Download,
  RefreshCw,
  Search,
  Edit,
  Lock,
  Trash2,
  Plus,
  BookOpen,
  Stethoscope
} from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

// Error Boundary to catch React errors
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error: error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error Boundary caught error:', error);
    console.error('Error Info:', errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          <h3 className="font-bold">React Error Caught:</h3>
          <p>Error: {this.state.error?.message || 'Unknown error'}</p>
          <button 
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-2 bg-red-500 text-white px-3 py-1 rounded text-sm"
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Simple custom Tabs component to avoid Radix UI issues
const CustomTabs = ({ children, value, onValueChange, className }) => {
  return <div className={className || ''}>{children}</div>;
};

const CustomTabsList = ({ children, className }) => {
  return (
    <div className={`flex border-b border-gray-200 ${className || ''}`}>
      {children}
    </div>
  );
};

const CustomTabsTrigger = ({ children, value, activeTab, onTabChange, className }) => {
  const isActive = value === activeTab;
  return (
    <button
      type="button"
      className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 ${
        isActive 
          ? 'border-red-500 text-red-600 bg-red-50' 
          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
      } ${className || ''}`}
      onClick={() => onTabChange && onTabChange(value)}
    >
      {children}
    </button>
  );
};

const CustomTabsContent = ({ children, value, activeTab, className }) => {
  if (value !== activeTab) return null;
  return <div className={className || ''}>{children}</div>;
};

const AdminDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [errorState, setErrorState] = useState('');
  const [adminToken] = useState(localStorage.getItem('adminToken'));
  
  // Safe error setter that ensures error is always a string
  const setError = (errorValue) => {
    console.log('setError called with:', errorValue, 'Type:', typeof errorValue);
    const safeError = typeof errorValue === 'string' ? errorValue : 
                     typeof errorValue === 'object' && errorValue !== null ? JSON.stringify(errorValue) : 
                     String(errorValue || '');
    console.log('Setting error state to safe error:', safeError); // Debug log
    setErrorState(safeError);
  };
  
  const error = errorState;
  const [dashboardData, setDashboardData] = useState(null);
  const [practices, setPractices] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedPractice, setSelectedPractice] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Procedures state
  const [procedures, setProcedures] = useState([]);
  const [specialties, setSpecialties] = useState([]);
  const [editingProcedure, setEditingProcedure] = useState(null);
  const [showAddProcedureForm, setShowAddProcedureForm] = useState(false);
  const [showAddPracticeForm, setShowAddPracticeForm] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showTempPassword, setShowTempPassword] = useState(false);
  const [newPractice, setNewPractice] = useState({
    practiceName: '',
    adminEmail: '',
    adminFirstName: '',
    adminLastName: '',
    phone: '',
    address: '',
    tempPassword: '',
    subscriptionType: 'trial',
    trialDays: 15
  });
  const [newProcedure, setNewProcedure] = useState({
    name: '',
    specialty: '',
    specialtyName: '',
    duration: '',
    overview: '',
    recoveryTimeline: '',
    immediateAftercare: [''],
    dietRestrictions: [''],
    warningSignsToCallDoctor: [''],
    medications: ['']
  });

  // Registrations state
  const [registrations, setRegistrations] = useState([]);
  const [registrationsLoading, setRegistrationsLoading] = useState(false);

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}/api/admin`;

  // Helper function to handle API error responses
  const handleApiError = (errorData, fallbackMessage) => {
    console.log('handleApiError called with errorData:', errorData);
    try {
      // Handle FastAPI validation errors
      if (errorData && errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          console.log('Processing array of validation errors');
          const errorMessages = errorData.detail.map(err => {
            if (typeof err === 'object' && err.msg) {
              const location = err.loc ? err.loc.join(' -> ') + ': ' : '';
              return `${location}${err.msg}`;
            }
            return String(err);
          });
          const result = errorMessages.join(', ');
          console.log('Array processing result:', result);
          return result;
        } else if (typeof errorData.detail === 'string') {
          console.log('String detail found:', errorData.detail);
          return errorData.detail;
        } else if (typeof errorData.detail === 'object' && errorData.detail.msg) {
          console.log('Object detail with msg found:', errorData.detail.msg);
          return errorData.detail.msg;
        }
      }
      
      if (typeof errorData === 'string') {
        console.log('String errorData found:', errorData);
        return errorData;
      }
      
      console.log('Using fallback message:', fallbackMessage);
      return fallbackMessage;
    } catch (e) {
      console.error('Error in handleApiError:', e);
      return fallbackMessage;
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    if (!adminToken) return;
    
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/dashboard`, {
        headers: { 'Authorization': `Bearer ${adminToken}` }
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else {
        setError('Failed to load admin dashboard');
      }
    } catch (error) {
      setError('Network error while loading dashboard');
    } finally {
      setLoading(false);
    }
  };

  const loadPractices = async () => {
    try {
      const response = await fetch(`${API_BASE}/practices`, {
        headers: { 'Authorization': `Bearer ${adminToken}` }
      });

      if (response.ok) {
        const data = await response.json();
        setPractices(data.practices || []);
      }
    } catch (error) {
      console.error('Failed to load practices:', error);
    }
  };

  const loadUsers = async (practiceId) => {
    try {
      const response = await fetch(`${API_BASE}/users/${practiceId}`, {
        headers: { 'Authorization': `Bearer ${adminToken}` }
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
      }
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  };

  const loadRegistrations = async () => {
    try {
      setRegistrationsLoading(true);
      const response = await fetch(`${API_BASE}/registration-attempts`, {
        headers: { 'Authorization': `Bearer ${adminToken}` }
      });

      if (response.ok) {
        const data = await response.json();
        setRegistrations(data.data || []);
      } else {
        console.error('Failed to load registrations');
      }
    } catch (error) {
      console.error('Failed to load registrations:', error);
    } finally {
      setRegistrationsLoading(false);
    }
  };

  const createPractice = async () => {
    try {
      // Validate required fields
      if (!newPractice.practiceName.trim()) {
        alert('Practice name is required');
        return;
      }
      if (!newPractice.adminEmail.trim()) {
        alert('Admin email is required');
        return;
      }
      if (!newPractice.adminFirstName.trim()) {
        alert('Admin first name is required');
        return;
      }
      if (!newPractice.adminLastName.trim()) {
        alert('Admin last name is required');
        return;
      }
      if (!newPractice.tempPassword || newPractice.tempPassword.length < 8) {
        alert('Temporary password must be at least 8 characters long');
        return;
      }

      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/admin/create-practice`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newPractice)
      });
      
      const data = await response.json();
      
      if (data.success) {
        alert(`Practice "${newPractice.practiceName}" created successfully!\n\nAdmin login:\nEmail: ${newPractice.adminEmail}\nPassword: ${newPractice.tempPassword}`);
        
        // Reset form
        setNewPractice({
          practiceName: '',
          adminEmail: '',
          adminFirstName: '',
          adminLastName: '',
          phone: '',
          address: '',
          tempPassword: '',
          subscriptionType: 'trial',
          trialDays: 15
        });
        setShowAddPracticeForm(false);
        loadPractices(); // Refresh the practices list
      } else {
        alert(`Failed to create practice: ${data.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Create practice error:', error);
      alert(`Error creating practice: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const managePractice = async (practiceId, action, reason = '') => {
    try {
      const response = await fetch(`${API_BASE}/manage-practice`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${adminToken}`
        },
        body: JSON.stringify({
          practice_id: practiceId,
          action: action,
          reason: reason
        })
      });

      if (response.ok) {
        loadPractices();
        loadDashboardData();
      }
    } catch (error) {
      console.error('Failed to manage practice:', error);
    }
  };

  const deletePractice = async (practiceId, practiceName) => {
    if (!adminToken) return;
    
    const confirmed = window.confirm(
      `⚠️ WARNING: Are you sure you want to PERMANENTLY DELETE the practice "${practiceName}"?\n\nThis will delete:\n- The practice record\n- All users (dentists/staff)\n- All patients\n- All procedure assignments\n- All practice data\n\nThis action CANNOT be undone!`
    );
    
    if (!confirmed) return;
    
    // Double confirmation for safety
    const doubleConfirmed = window.confirm(
      `FINAL CONFIRMATION: Type "${practiceName}" to confirm deletion.\n\nAre you absolutely sure you want to delete "${practiceName}" and ALL its data permanently?`
    );
    
    if (!doubleConfirmed) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/practices/${practiceId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${adminToken}`
        }
      });

      if (response.ok) {
        await loadPractices();
        await loadDashboardData();
        alert(`Practice "${practiceName}" has been permanently deleted.`);
        
        // Clear selected practice if it was the deleted one
        if (selectedPractice?.id === practiceId) {
          setSelectedPractice(null);
          setUsers([]);
        }
      } else {
        const errorData = await response.json();
        setError(handleApiError(errorData, 'Failed to delete practice'));
      }
    } catch (error) {
      console.error('Failed to delete practice:', error);
      setError('Failed to delete practice');
    }
    setLoading(false);
  };

  const resetUserPassword = async (userId, newPassword) => {
    try {
      const response = await fetch(`${API_BASE}/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${adminToken}`
        },
        body: JSON.stringify({
          user_id: userId,
          new_password: newPassword
        })
      });

      return response.ok;
    } catch (error) {
      console.error('Failed to reset password:', error);
      return false;
    }
  };

  const deleteUser = async (userId, userName) => {
    if (!adminToken) return;
    
    const confirmed = window.confirm(
      `Are you sure you want to delete user "${userName}"? This action cannot be undone.`
    );
    
    if (!confirmed) return;
    
    try {
      const response = await fetch(`${API_BASE}/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${adminToken}`
        }
      });

      if (response.ok) {
        // Reload users for the current practice
        if (selectedPractice) {
          await loadUsers(selectedPractice.id);
        }
        alert(`User "${userName}" has been deleted successfully.`);
      } else {
        const errorData = await response.json();
        setError(handleApiError(errorData, 'Failed to delete user'));
      }
    } catch (error) {
      console.error('Failed to delete user:', error);
      setError('Failed to delete user');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('adminToken');
    window.location.reload();
  };

  // Load practices when switching to practices tab
  useEffect(() => {
    if (activeTab === 'practices') {
      loadPractices();
    } else if (activeTab === 'procedures') {
      loadProcedures();
    } else if (activeTab === 'users') {
      // Load practices for the users tab so user can select a practice
      loadPractices();
    } else if (activeTab === 'registrations') {
      loadRegistrations();
    }
  }, [activeTab]);

  // Procedures management functions
  const loadProcedures = async () => {
    if (!adminToken) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/procedures`, {
        headers: {
          'Authorization': `Bearer ${adminToken}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setProcedures(data.procedures || []);
        setSpecialties(data.specialties || []);
      }
    } catch (error) {
      console.error('Failed to load procedures:', error);
      setError('Failed to load procedures');
    }
    setLoading(false);
  };

  // Create a separate handler function as recommended by troubleshoot agent
  const handleCreateProcedure = async () => {
    console.log('🚀 HANDLE CREATE PROCEDURE CALLED - React 19 Fix');
    try {
      await createProcedure();
    } catch (error) {
      console.error('❌ Error in handleCreateProcedure:', error);
      setError(`Unexpected error: ${error.message || error}`);
    }
  };

  const createProcedure = async () => {
    if (!adminToken) return;
    
    setLoading(true);
    setError(''); // Clear any previous errors
    
    try {
      const response = await fetch(`${API_BASE}/procedures`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${adminToken}`
        },
        body: JSON.stringify({
          ...newProcedure,
          immediateAftercare: newProcedure.immediateAftercare.filter(item => item.trim()),
          dietRestrictions: newProcedure.dietRestrictions.filter(item => item.trim()),
          medications: newProcedure.medications.filter(item => item.trim()),
          warningSignsToCallDoctor: newProcedure.warningSignsToCallDoctor.filter(item => item.trim())
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Procedure created successfully:', data);
        
        // Reset form and close
        setShowAddProcedureForm(false);
        setNewProcedure({
          name: '',
          specialty: '',
          specialtyName: '',
          duration: '',
          overview: '',
          recoveryTimeline: '',
          immediateAftercare: [''],
          dietRestrictions: [''],
          medications: [''],
          warningSignsToCallDoctor: ['']
        });
        
        // Refresh procedures list
        await loadProcedures();
        
      } else {
        // Handle error responses - FIX: Convert objects to strings
        console.log('API Error - Response status:', response.status);
        try {
          const errorData = await response.json();
          console.log('Raw error data:', errorData);
          
          // CRITICAL FIX: Always convert error objects to strings
          let errorMessage;
          if (Array.isArray(errorData.detail)) {
            // Handle FastAPI validation errors
            const errors = errorData.detail.map(err => `${err.loc?.join('.')||'field'}: ${err.msg}`);
            errorMessage = `Validation errors: ${errors.join(', ')}`;
          } else if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (errorData.message) {
            errorMessage = errorData.message;
          } else {
            errorMessage = `Server error (${response.status}): Please check all required fields`;
          }
          
          console.log('Processed error message:', errorMessage);
          setError(errorMessage);
        } catch (parseError) {
          console.error('Failed to parse error response:', parseError);
          const errorMessage = `Server error (${response.status}): Failed to create procedure`;
          setError(errorMessage);
        }
      }
    } catch (networkError) {
      console.error('Network error during procedure creation:', networkError);
      const errorMessage = `Network error: ${networkError.message || 'Failed to create procedure'}`;
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const updateProcedure = async (procedureId, updates) => {
    if (!adminToken) return;
    
    try {
      const response = await fetch(`${API_BASE}/procedures/${procedureId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${adminToken}`
        },
        body: JSON.stringify(updates)
      });

      if (response.ok) {
        await loadProcedures();
        setEditingProcedure(null);
      } else {
        const errorData = await response.json();
        setError(handleApiError(errorData, 'Failed to update procedure'));
      }
    } catch (error) {
      console.error('Failed to update procedure:', error);
      setError('Failed to update procedure');
    }
  };

  const deleteProcedure = async (procedureId) => {
    if (!adminToken) return;
    if (!window.confirm('Are you sure you want to delete this procedure?')) return;
    
    try {
      const response = await fetch(`${API_BASE}/procedures/${procedureId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${adminToken}`
        }
      });

      if (response.ok) {
        await loadProcedures();
      } else {
        const errorData = await response.json();
        setError(handleApiError(errorData, 'Failed to delete procedure'));
      }
    } catch (error) {
      console.error('Failed to delete procedure:', error);
      setError('Failed to delete procedure');
    }
  };

  const deployProcedures = async (procedureIds, deploymentType) => {
    if (!adminToken) return;
    
    try {
      const response = await fetch(`${API_BASE}/procedures/deploy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${adminToken}`
        },
        body: JSON.stringify({
          procedure_ids: procedureIds,
          deployment_type: deploymentType
        })
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Successfully deployed ${procedureIds.length} procedures to ${data.deployment_result.deployed_to_practices} practices`);
      } else {
        const errorData = await response.json();
        setError(handleApiError(errorData, 'Failed to deploy procedures'));
      }
    } catch (error) {
      console.error('Failed to deploy procedures:', error);
      setError('Failed to deploy procedures');
    }
  };

  const addArrayItem = (field, index = null) => {
    setNewProcedure(prev => ({
      ...prev,
      [field]: [...prev[field], '']
    }));
  };

  const updateArrayItem = (field, index, value) => {
    setNewProcedure(prev => ({
      ...prev,
      [field]: prev[field].map((item, i) => i === index ? value : item)
    }));
  };

  const removeArrayItem = (field, index) => {
    setNewProcedure(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }));
  };

  if (loading && !dashboardData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-red-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-red-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-600 to-red-700 text-white p-6 rounded-lg mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold flex items-center">
              <Settings className="h-8 w-8 mr-3" />
              Admin Dashboard
            </h1>
            <p className="opacity-90 mt-1">System Administration & Management</p>
          </div>
          <Button 
            onClick={handleLogout}
            variant="outline"
            className="bg-white/20 border-white/30 text-white hover:bg-white/30"
          >
            Logout
          </Button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {typeof error === 'string' ? error : JSON.stringify(error)}
          </div>
        )}

        <CustomTabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <CustomTabsList className="grid w-full grid-cols-7 gap-1">
            <CustomTabsTrigger value="dashboard" activeTab={activeTab} onTabChange={setActiveTab}>Dashboard</CustomTabsTrigger>
            <CustomTabsTrigger value="practices" activeTab={activeTab} onTabChange={setActiveTab}>Practices</CustomTabsTrigger>
            <CustomTabsTrigger value="users" activeTab={activeTab} onTabChange={setActiveTab}>Users</CustomTabsTrigger>
            <CustomTabsTrigger value="procedures" activeTab={activeTab} onTabChange={setActiveTab}>Procedures</CustomTabsTrigger>
            <CustomTabsTrigger value="registrations" activeTab={activeTab} onTabChange={setActiveTab}>New Registrations</CustomTabsTrigger>
            <CustomTabsTrigger value="analytics" activeTab={activeTab} onTabChange={setActiveTab}>Analytics</CustomTabsTrigger>
            <CustomTabsTrigger value="system" activeTab={activeTab} onTabChange={setActiveTab}>System</CustomTabsTrigger>
          </CustomTabsList>

          <CustomTabsContent value="dashboard" activeTab={activeTab} className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Practices</CardTitle>
                  <Building2 className="h-4 w-4 text-blue-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{dashboardData?.stats?.total_practices || 0}</div>
                  <p className="text-xs text-gray-600">All registered practices</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Practices</CardTitle>
                  <CheckCircle className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{dashboardData?.stats?.active_practices || 0}</div>
                  <p className="text-xs text-gray-600">Currently subscribed</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                  <DollarSign className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">${dashboardData?.stats?.total_revenue || 0}</div>
                  <p className="text-xs text-gray-600">All-time earnings</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
                  <BarChart3 className="h-4 w-4 text-purple-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">${dashboardData?.stats?.monthly_revenue || 0}</div>
                  <p className="text-xs text-gray-600">This month</p>
                </CardContent>
              </Card>
            </div>

            {/* Recent Practices & Alerts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Practices</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {dashboardData?.recent_practices?.slice(0, 5).map((practice) => (
                      <div key={practice.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium">{practice.name}</p>
                          <p className="text-sm text-gray-600">{practice.email}</p>
                        </div>
                        <Badge 
                          variant={practice.subscription?.status === 'active' ? 'default' : 'secondary'}
                        >
                          {practice.subscription?.status || 'unknown'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <AlertTriangle className="h-5 w-5 mr-2 text-orange-500" />
                    Expiring Trials
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {dashboardData?.expiring_trials?.slice(0, 5).map((practice) => (
                      <div key={practice.id} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                        <div>
                          <p className="font-medium">{practice.name}</p>
                          <p className="text-sm text-gray-600">Expires soon</p>
                        </div>
                        <Button 
                          size="sm" 
                          onClick={() => managePractice(practice.id, 'extend_trial')}
                        >
                          Extend
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </CustomTabsContent>

          <CustomTabsContent value="practices" activeTab={activeTab} className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Practice Management</h2>
              <div className="flex space-x-2">
                <Button onClick={loadPractices}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
                <Button onClick={() => setShowAddPracticeForm(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Practice
                </Button>
              </div>
            </div>

            {/* Add Practice Form */}
            {showAddPracticeForm && (
              <Card>
                <CardHeader>
                  <CardTitle>Add New Dental Practice</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Practice Name <span className="text-red-500">*</span>
                      </label>
                      <Input 
                        value={newPractice.practiceName}
                        onChange={(e) => setNewPractice(prev => ({...prev, practiceName: e.target.value}))}
                        placeholder="e.g., Smith Family Dental"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Admin Email <span className="text-red-500">*</span>
                      </label>
                      <Input 
                        type="email"
                        value={newPractice.adminEmail}
                        onChange={(e) => setNewPractice(prev => ({...prev, adminEmail: e.target.value}))}
                        placeholder="admin@example.com"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Admin First Name <span className="text-red-500">*</span>
                      </label>
                      <Input 
                        value={newPractice.adminFirstName}
                        onChange={(e) => setNewPractice(prev => ({...prev, adminFirstName: e.target.value}))}
                        placeholder="John"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Admin Last Name <span className="text-red-500">*</span>
                      </label>
                      <Input 
                        value={newPractice.adminLastName}
                        onChange={(e) => setNewPractice(prev => ({...prev, adminLastName: e.target.value}))}
                        placeholder="Smith"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Phone (Optional)
                      </label>
                      <Input 
                        value={newPractice.phone}
                        onChange={(e) => setNewPractice(prev => ({...prev, phone: e.target.value}))}
                        placeholder="(555) 123-4567"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Temporary Password <span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <Input 
                          type={showTempPassword ? "text" : "password"}
                          value={newPractice.tempPassword}
                          onChange={(e) => setNewPractice(prev => ({...prev, tempPassword: e.target.value}))}
                          placeholder="Minimum 8 characters"
                          className="pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => setShowTempPassword(!showTempPassword)}
                          className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-gray-700"
                        >
                          {showTempPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </button>
                      </div>
                      <div className="mt-1 text-xs text-gray-600">
                        <p className="font-medium">Password requirements:</p>
                        <ul className="list-disc list-inside mt-1 space-y-1">
                          <li>At least 8 characters</li>
                          <li>Must include uppercase letter</li>
                          <li>Must include lowercase letter</li>
                          <li>Must include number</li>
                          <li>Must include special character (!@#$%^&*)</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Address (Optional)
                    </label>
                    <Input 
                      value={newPractice.address}
                      onChange={(e) => setNewPractice(prev => ({...prev, address: e.target.value}))}
                      placeholder="123 Main St, City, State 12345"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Subscription Type
                      </label>
                      <select
                        className="w-full p-2 border rounded-md"
                        value={newPractice.subscriptionType}
                        onChange={(e) => setNewPractice(prev => ({...prev, subscriptionType: e.target.value}))}
                      >
                        <option value="trial">Trial</option>
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                      </select>
                    </div>
                    {newPractice.subscriptionType === 'trial' && (
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Trial Days
                        </label>
                        <Input 
                          type="number"
                          value={newPractice.trialDays}
                          onChange={(e) => setNewPractice(prev => ({...prev, trialDays: parseInt(e.target.value) || 15}))}
                          min="1"
                          max="365"
                        />
                      </div>
                    )}
                  </div>

                  <div className="flex justify-end space-x-2">
                    <Button 
                      variant="outline" 
                      onClick={() => setShowAddPracticeForm(false)}
                    >
                      Cancel
                    </Button>
                    <Button 
                      onClick={createPractice} 
                      disabled={loading}
                    >
                      {loading ? <LoadingSpinner className="h-4 w-4 mr-2" /> : null}
                      Create Practice
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <Search className="h-4 w-4" />
                  <Input
                    placeholder="Search practices..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="max-w-sm"
                  />
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {practices
                    .filter(practice => 
                      practice.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                      practice.email?.toLowerCase().includes(searchTerm.toLowerCase())
                    )
                    .map((practice) => (
                    <div key={practice.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h3 className="font-semibold">{practice.name}</h3>
                        <p className="text-sm text-gray-600">{practice.email}</p>
                        <p className="text-sm text-gray-500">
                          Created: {new Date(practice.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge 
                          variant={practice.subscription?.status === 'active' ? 'default' : 
                                   practice.subscription?.status === 'trial' ? 'secondary' : 'destructive'}
                        >
                          {practice.subscription?.status || 'unknown'}
                        </Badge>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            setSelectedPractice(practice);
                            loadUsers(practice.id);
                            setActiveTab('users');
                          }}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => managePractice(practice.id, 
                            practice.subscription?.status === 'active' ? 'deactivate' : 'activate'
                          )}
                        >
                          {practice.subscription?.status === 'active' ? (
                            <UserX className="h-4 w-4" />
                          ) : (
                            <CheckCircle className="h-4 w-4" />
                          )}
                        </Button>
                        <Button 
                          size="sm" 
                          variant="destructive"
                          onClick={() => deletePractice(practice.id, practice.name)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </CustomTabsContent>

          <CustomTabsContent value="users" activeTab={activeTab} className="space-y-6">
            {selectedPractice ? (
              <Card>
                <CardHeader>
                  <CardTitle>Users for {selectedPractice.name}</CardTitle>
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setSelectedPractice(null);
                      setUsers([]);
                    }}
                  >
                    Back to Practices List
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {users.map((user) => (
                      <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                          <h3 className="font-semibold">{user.firstName} {user.lastName}</h3>
                          <p className="text-sm text-gray-600">{user.email}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            <Badge variant="outline">{user.role}</Badge>
                            {user.specialties && user.specialties.length > 0 && (
                              <Badge variant="secondary">{user.specialties.join(', ')}</Badge>
                            )}
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            Created: {new Date(user.createdAt).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex space-x-2">
                          <Button 
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              const newPassword = prompt('Enter new password:');
                              if (newPassword) {
                                resetUserPassword(user.id, newPassword);
                              }
                            }}
                          >
                            <Lock className="h-4 w-4 mr-2" />
                            Reset Password
                          </Button>
                          <Button 
                            size="sm"
                            variant="destructive"
                            onClick={() => deleteUser(user.id, user.firstName + ' ' + user.lastName)}
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete User
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {users.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>No users found for this practice.</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Users className="h-5 w-5 mr-2" />
                    Practice User Management
                  </CardTitle>
                  <p className="text-sm text-gray-600">Select a practice to view and manage their users (dentists and staff)</p>
                </CardHeader>
                <CardContent>
                  <div className="mb-4">
                    <div className="flex items-center space-x-2">
                      <Search className="h-4 w-4" />
                      <Input
                        placeholder="Search practices..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="max-w-md"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    {practices
                      .filter(practice => 
                        practice.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        practice.email?.toLowerCase().includes(searchTerm.toLowerCase())
                      )
                      .map((practice) => (
                      <div key={practice.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                        <div>
                          <h3 className="font-semibold">{practice.name}</h3>
                          <p className="text-sm text-gray-600">{practice.email}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            <Badge 
                              variant={practice.subscription?.status === 'active' ? 'default' : 
                                       practice.subscription?.status === 'trial' ? 'secondary' : 'destructive'}
                            >
                              {practice.subscription?.status || 'unknown'}
                            </Badge>
                            <span className="text-xs text-gray-500">
                              {practice.user_count || 0} users
                            </span>
                          </div>
                        </div>
                        <Button 
                          size="sm" 
                          onClick={() => {
                            setSelectedPractice(practice);
                            loadUsers(practice.id);
                          }}
                        >
                          <Users className="h-4 w-4 mr-2" />
                          View Users
                        </Button>
                      </div>
                    ))}
                  </div>
                  
                  {practices.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <Building2 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>No practices found. Load practices from the Practices tab first.</p>
                      <Button 
                        className="mt-4" 
                        onClick={() => {
                          loadPractices();
                        }}
                      >
                        Load Practices
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </CustomTabsContent>

          <CustomTabsContent value="analytics" activeTab={activeTab} className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>System Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">{dashboardData?.stats?.trial_practices || 0}</div>
                    <p className="text-sm text-gray-600">Trial Practices</p>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-red-600">{dashboardData?.stats?.cancelled_practices || 0}</div>
                    <p className="text-sm text-gray-600">Cancelled Practices</p>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">
                      {dashboardData?.stats?.active_practices && dashboardData?.stats?.total_practices 
                        ? Math.round((dashboardData.stats.active_practices / dashboardData.stats.total_practices) * 100)
                        : 0}%
                    </div>
                    <p className="text-sm text-gray-600">Conversion Rate</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </CustomTabsContent>

          <CustomTabsContent value="procedures" activeTab={activeTab} className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Global Procedure Management</h2>
              <div className="flex space-x-2">
                <Button onClick={loadProcedures}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
                <Button onClick={() => setShowAddProcedureForm(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Procedure
                </Button>
              </div>
            </div>

            {/* Add Procedure Form */}
            {showAddProcedureForm && (
              <ErrorBoundary>
                <Card>
                <CardHeader>
                  <CardTitle>Add New Global Procedure</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <form onSubmit={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('🚨 FORM SUBMIT INTERCEPTED - This should not happen!');
                    alert('Form submitted! This should be prevented.');
                    return false;
                  }} onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      e.stopPropagation();
                      console.log('🚨 ENTER KEY INTERCEPTED');
                      alert('Enter key pressed! This might be causing auto-submission.');
                      return false;
                    }
                  }}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Procedure Name <span className="text-red-500">*</span>
                      </label>
                      <Input 
                        value={newProcedure.name}
                        onChange={(e) => setNewProcedure(prev => ({...prev, name: e.target.value}))}
                        placeholder="e.g., Root Canal Therapy"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Specialty <span className="text-red-500">*</span>
                      </label>
                      <select
                        className="w-full p-2 border rounded-md"
                        value={newProcedure.specialty}
                        onChange={(e) => {
                          const specialty = specialties.find(s => s.id === e.target.value);
                          setNewProcedure(prev => ({
                            ...prev, 
                            specialty: e.target.value,
                            specialtyName: specialty?.name || ''
                          }));
                        }}
                      >
                        <option value="">Select Specialty</option>
                        {specialties.map(specialty => (
                          <option key={specialty.id} value={specialty.id}>
                            {specialty.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Duration <span className="text-red-500">*</span>
                      </label>
                      <Input 
                        value={newProcedure.duration}
                        onChange={(e) => setNewProcedure(prev => ({...prev, duration: e.target.value}))}
                        placeholder="e.g., 3-7 days recovery"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Overview <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      className="w-full p-2 border rounded-md h-24"
                      value={newProcedure.overview}
                      onChange={(e) => setNewProcedure(prev => ({...prev, overview: e.target.value}))}
                      placeholder="Detailed description of the procedure and its purpose..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Recovery Timeline</label>
                    <textarea
                      className="w-full p-2 border rounded-md h-20"
                      value={newProcedure.recoveryTimeline}
                      onChange={(e) => setNewProcedure(prev => ({...prev, recoveryTimeline: e.target.value}))}
                      placeholder="Expected recovery timeline and milestones (optional)..."
                    />
                  </div>

                  {/* Immediate Aftercare */}
                  <div>
                    <label className="block text-sm font-medium mb-1">Immediate Aftercare Instructions</label>
                    {newProcedure.immediateAftercare.map((item, index) => (
                      <div key={index} className="flex items-center space-x-2 mb-2">
                        <Input
                          value={item}
                          onChange={(e) => updateArrayItem('immediateAftercare', index, e.target.value)}
                          placeholder="Aftercare instruction..."
                        />
                        <Button 
                          type="button" 
                          size="sm" 
                          variant="outline" 
                          onClick={() => removeArrayItem('immediateAftercare', index)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                    <Button type="button" size="sm" variant="outline" onClick={() => addArrayItem('immediateAftercare')}>
                      <Plus className="h-4 w-4 mr-1" /> Add Instruction
                    </Button>
                  </div>

                  {/* Diet Restrictions */}
                  <div>
                    <label className="block text-sm font-medium mb-1">Diet Restrictions</label>
                    {newProcedure.dietRestrictions.map((item, index) => (
                      <div key={index} className="flex items-center space-x-2 mb-2">
                        <Input
                          value={item}
                          onChange={(e) => updateArrayItem('dietRestrictions', index, e.target.value)}
                          placeholder="Diet restriction..."
                        />
                        <Button 
                          type="button" 
                          size="sm" 
                          variant="outline" 
                          onClick={() => removeArrayItem('dietRestrictions', index)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                    <Button type="button" size="sm" variant="outline" onClick={() => addArrayItem('dietRestrictions')}>
                      <Plus className="h-4 w-4 mr-1" /> Add Restriction
                    </Button>
                  </div>

                  {/* Warning Signs */}
                  <div>
                    <label className="block text-sm font-medium mb-1">Warning Signs to Call Doctor</label>
                    {newProcedure.warningSignsToCallDoctor.map((item, index) => (
                      <div key={index} className="flex items-center space-x-2 mb-2">
                        <Input
                          value={item}
                          onChange={(e) => updateArrayItem('warningSignsToCallDoctor', index, e.target.value)}
                          placeholder="Warning sign..."
                        />
                        <Button 
                          type="button" 
                          size="sm" 
                          variant="outline" 
                          onClick={() => removeArrayItem('warningSignsToCallDoctor', index)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                    <Button type="button" size="sm" variant="outline" onClick={() => addArrayItem('warningSignsToCallDoctor')}>
                      <Plus className="h-4 w-4 mr-1" /> Add Warning Sign
                    </Button>
                  </div>

                  <div className="flex justify-end space-x-2">
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={() => setShowAddProcedureForm(false)}
                    >
                      Cancel
                    </Button>
                    <Button 
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('🚀 SAVE PROCEDURE BUTTON CLICKED!');
                        handleCreateProcedure();
                      }} 
                      disabled={loading}
                      type="button"
                    >
                      {loading ? <LoadingSpinner className="h-4 w-4 mr-2" /> : null}
                      Save
                    </Button>
                  </div>
                  </form>
                </CardContent>
              </Card>
              </ErrorBoundary>
            )}

            {/* Organized Procedures List by Specialty with Color Coding */}
            <div className="grid grid-cols-1 gap-6">
              {specialties
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((specialty) => {
                  const specialtyProcedures = procedures
                    .filter(proc => proc.specialty === specialty.id)
                    .sort((a, b) => a.name.localeCompare(b.name));
                  
                  if (specialtyProcedures.length === 0) return null;
                  
                  // Color scheme for each specialty
                  const getSpecialtyColors = (specialtyId) => {
                    const colorMap = {
                      'endodontics': {
                        card: 'bg-blue-50 border-blue-200',
                        header: 'bg-blue-100 border-blue-300',
                        icon: 'text-blue-600',
                        badge: 'bg-blue-600 text-white',
                        procedures: 'border-blue-200 hover:bg-blue-25'
                      },
                      'oral-surgery': {
                        card: 'bg-red-50 border-red-200',
                        header: 'bg-red-100 border-red-300',
                        icon: 'text-red-600',
                        badge: 'bg-red-600 text-white',
                        procedures: 'border-red-200 hover:bg-red-25'
                      },
                      'prosthodontics': {
                        card: 'bg-purple-50 border-purple-200',
                        header: 'bg-purple-100 border-purple-300',
                        icon: 'text-purple-600',
                        badge: 'bg-purple-600 text-white',
                        procedures: 'border-purple-200 hover:bg-purple-25'
                      },
                      'periodontics': {
                        card: 'bg-green-50 border-green-200',
                        header: 'bg-green-100 border-green-300',
                        icon: 'text-green-600',
                        badge: 'bg-green-600 text-white',
                        procedures: 'border-green-200 hover:bg-green-25'
                      },
                      'general-dentistry': {
                        card: 'bg-orange-50 border-orange-200',
                        header: 'bg-orange-100 border-orange-300',
                        icon: 'text-orange-600',
                        badge: 'bg-orange-600 text-white',
                        procedures: 'border-orange-200 hover:bg-orange-25'
                      },
                      'orthodontics': {
                        card: 'bg-teal-50 border-teal-200',
                        header: 'bg-teal-100 border-teal-300',
                        icon: 'text-teal-600',
                        badge: 'bg-teal-600 text-white',
                        procedures: 'border-teal-200 hover:bg-teal-25'
                      },
                      'oral-medicine': {
                        card: 'bg-indigo-50 border-indigo-200',
                        header: 'bg-indigo-100 border-indigo-300',
                        icon: 'text-indigo-600',
                        badge: 'bg-indigo-600 text-white',
                        procedures: 'border-indigo-200 hover:bg-indigo-25'
                      }
                    };
                    return colorMap[specialtyId] || colorMap['general-dentistry'];
                  };
                  
                  const colors = getSpecialtyColors(specialty.id);
                  
                  return (
                    <Card key={specialty.id} className={`${colors.card} border-2`}>
                      <CardHeader className={`${colors.header} rounded-t-lg border-b-2`}>
                        <CardTitle className="flex items-center justify-between">
                          <div className="flex items-center">
                            <Stethoscope className={`h-5 w-5 mr-2 ${colors.icon}`} />
                            <span className={`font-bold ${colors.icon}`}>{specialty.name}</span>
                            <Badge className={`ml-2 ${colors.badge}`}>
                              {specialtyProcedures.length} procedures
                            </Badge>
                          </div>
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="pt-4">
                        <div className="space-y-3">
                          {specialtyProcedures.map((procedure) => (
                            <div key={procedure.id} className={`border-2 rounded-lg p-4 ${colors.procedures} transition-colors duration-200`}>
                              <div className="flex items-center justify-between">
                                <div className="flex-1">
                                  <h3 className={`font-semibold text-lg ${colors.icon}`}>{procedure.name}</h3>
                                  <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                                    <span className="font-medium">{procedure.duration}</span>
                                    <span className="text-xs text-gray-500">
                                      ID: {procedure.id}
                                    </span>
                                  </div>
                                  <p className="text-sm text-gray-700 mt-2 line-clamp-2">
                                    {procedure.overview}
                                  </p>
                                </div>
                                <div className="flex flex-col space-y-2 ml-4">
                                  <Button 
                                    size="sm" 
                                    variant="outline"
                                    className={`border-2 ${colors.icon.replace('text-', 'border-')} hover:${colors.card}`}
                                    onClick={() => setEditingProcedure(procedure.id === editingProcedure ? null : procedure.id)}
                                  >
                                    <Edit className="h-4 w-4 mr-1" />
                                    {editingProcedure === procedure.id ? 'Cancel' : 'Edit'}
                                  </Button>
                                  <Button 
                                    size="sm" 
                                    variant="destructive"
                                    onClick={() => deleteProcedure(procedure.id)}
                                  >
                                    <Trash2 className="h-4 w-4 mr-1" />
                                    Delete
                                  </Button>
                                </div>
                              </div>

                              {editingProcedure === procedure.id && (
                                <div className={`mt-4 pt-4 border-t-2 ${colors.icon.replace('text-', 'border-')} space-y-4 bg-white rounded-lg p-4 shadow-sm`}>
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                      <label className="block text-sm font-medium mb-1">Procedure Name</label>
                                      <Input
                                        defaultValue={procedure.name}
                                        className={`border-2 ${colors.icon.replace('text-', 'border-')} focus:${colors.card}`}
                                        onBlur={(e) => updateProcedure(procedure.id, { name: e.target.value })}
                                      />
                                    </div>
                                    <div>
                                      <label className="block text-sm font-medium mb-1">Duration</label>
                                      <Input
                                        defaultValue={procedure.duration}
                                        className={`border-2 ${colors.icon.replace('text-', 'border-')} focus:${colors.card}`}
                                        onBlur={(e) => updateProcedure(procedure.id, { duration: e.target.value })}
                                      />
                                    </div>
                                  </div>
                                  <div>
                                    <label className="block text-sm font-medium mb-1">Overview</label>
                                    <textarea
                                      className={`w-full p-2 border-2 rounded-md h-24 ${colors.icon.replace('text-', 'border-')} focus:${colors.card}`}
                                      defaultValue={procedure.overview}
                                      onBlur={(e) => updateProcedure(procedure.id, { overview: e.target.value })}
                                    />
                                  </div>
                                  <div>
                                    <label className="block text-sm font-medium mb-1">Specialty</label>
                                    <select
                                      className={`w-full p-2 border-2 rounded-md ${colors.icon.replace('text-', 'border-')} focus:${colors.card}`}
                                      defaultValue={procedure.specialty}
                                      onChange={(e) => {
                                        const newSpecialty = specialties.find(s => s.id === e.target.value);
                                        updateProcedure(procedure.id, { 
                                          specialty: e.target.value,
                                          specialtyName: newSpecialty?.name || ''
                                        });
                                      }}
                                    >
                                      {specialties.map(spec => (
                                        <option key={spec.id} value={spec.id}>
                                          {spec.name}
                                        </option>
                                      ))}
                                    </select>
                                  </div>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
            </div>

            {/* Summary Card */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BookOpen className="h-5 w-5 mr-2" />
                  Procedure Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{procedures.length}</div>
                    <p className="text-sm text-gray-600">Total Procedures</p>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{specialties.length}</div>
                    <p className="text-sm text-gray-600">Specialties</p>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {Math.round(procedures.length / specialties.length) || 0}
                    </div>
                    <p className="text-sm text-gray-600">Avg per Specialty</p>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {specialties.length > 0 ? Math.max(...specialties.map(s => 
                        procedures.filter(p => p.specialty === s.id).length
                      )) : 0}
                    </div>
                    <p className="text-sm text-gray-600">Largest Specialty</p>
                  </div>
                </div>

                {procedures.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <BookOpen className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No procedures found. Add your first global procedure.</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Deployment Controls */}
            {procedures.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Deploy Procedures to Practices</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-gray-600">
                    Procedures are automatically available to all practices. Use these controls for manual deployments.
                  </p>
                  <div className="flex space-x-2">
                    <Button 
                      onClick={() => deployProcedures(procedures.map(p => p.id), 'all_practices')}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      Deploy to All Practices
                    </Button>
                    <Button 
                      onClick={() => deployProcedures(procedures.map(p => p.id), 'active_only')}
                      variant="outline"
                    >
                      Deploy to Active Only
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </CustomTabsContent>

          <CustomTabsContent value="registrations" activeTab={activeTab} className="space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <UserX className="h-5 w-5 text-blue-600" />
                  <span>New Registrations</span>
                </CardTitle>
                <Button onClick={loadRegistrations} variant="outline" size="sm">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              </CardHeader>
              <CardContent>
                {registrationsLoading ? (
                  <div className="flex justify-center py-8">
                    <LoadingSpinner />
                  </div>
                ) : registrations.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <UserX className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg font-medium">No registration attempts found</p>
                    <p className="text-sm">Registration attempts will appear here</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {registrations.map((registration, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <h3 className="font-semibold text-lg">{registration.practiceName}</h3>
                              <Badge 
                                variant={registration.status === 'success' ? 'default' : 
                                        registration.status === 'blocked' ? 'destructive' : 'secondary'}
                                className={
                                  registration.status === 'success' ? 'bg-green-100 text-green-800 border-green-200' :
                                  registration.status === 'blocked' ? 'bg-red-100 text-red-800 border-red-200' :
                                  'bg-yellow-100 text-yellow-800 border-yellow-200'
                                }
                              >
                                {registration.status === 'success' ? '✅ PAID' : 
                                 registration.status === 'blocked' ? '❌ BLOCKED' : 
                                 registration.status === 'trial_registered' ? '⚠️ TRIAL' : registration.status}
                              </Badge>
                              {registration.registration_type === 'samcart' && (
                                <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                                  SamCart
                                </Badge>
                              )}
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                              <div>
                                <span className="font-medium text-gray-600">Email:</span> {registration.email}
                              </div>
                              <div>
                                <span className="font-medium text-gray-600">Date:</span> {
                                  new Date(registration.attempted_at).toLocaleString()
                                }
                              </div>
                              <div>
                                <span className="font-medium text-gray-600">Payment Verified:</span> {
                                  registration.payment_verified ? (
                                    <span className="text-green-600 font-medium">✅ Yes</span>
                                  ) : (
                                    <span className="text-red-600 font-medium">❌ No</span>
                                  )
                                }
                              </div>
                              {registration.registration_type && (
                                <div>
                                  <span className="font-medium text-gray-600">Type:</span> {
                                    registration.registration_type === 'samcart' ? 'SamCart Payment' : 'Trial Registration'
                                  }
                                </div>
                              )}
                              {registration.reason && (
                                <div className="md:col-span-2">
                                  <span className="font-medium text-gray-600">Reason:</span> 
                                  <span className="text-red-600 ml-1">{registration.reason}</span>
                                </div>
                              )}
                            </div>
                            
                            {registration.practice_id && (
                              <div className="mt-2 text-xs text-gray-500">
                                Practice ID: {registration.practice_id}
                              </div>
                            )}
                          </div>
                          
                          <div className="ml-4">
                            {registration.status === 'success' ? (
                              <CheckCircle className="h-6 w-6 text-green-500" />
                            ) : registration.status === 'blocked' ? (
                              <XCircle className="h-6 w-6 text-red-500" />
                            ) : (
                              <AlertTriangle className="h-6 w-6 text-yellow-500" />
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </CustomTabsContent>

          <CustomTabsContent value="system" activeTab={activeTab} className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>System Management</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button onClick={loadDashboardData} className="w-full">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh All Data
                </Button>
                <Button variant="outline" className="w-full">
                  <Download className="h-4 w-4 mr-2" />
                  Download System Report
                </Button>
                <Button variant="outline" className="w-full">
                  <FileText className="h-4 w-4 mr-2" />
                  View System Logs
                </Button>
              </CardContent>
            </Card>
          </CustomTabsContent>
        </CustomTabs>
      </div>
    </div>
  );
};

const AdminLogin = () => {
  const [credentials, setCredentials] = useState({ email: 'cganz@admin.com', password: 'Dentist1#' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [adminToken, setAdminToken] = useState(localStorage.getItem('adminToken'));

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}/api/admin`;

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.token) {
          localStorage.setItem('adminToken', data.token);
          setAdminToken(data.token);
        } else {
          setError('Invalid login response');
        }
      } else {
        setError('Invalid admin credentials');
      }
    } catch (error) {
      setError('Network error during login');
    } finally {
      setLoading(false);
    }
  };

  // If logged in, show admin dashboard
  if (adminToken) {
    return <AdminDashboard />;
  }

  // Show login form
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-red-50 flex items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center flex items-center justify-center">
            <Settings className="h-6 w-6 mr-2 text-red-600" />
            Admin Login
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-3 py-2 rounded text-sm">
                {typeof error === 'string' ? error : JSON.stringify(error)}
              </div>
            )}
            
            <div>
              <Input
                type="email"
                placeholder="Admin Email"
                value={credentials.email}
                onChange={(e) => setCredentials(prev => ({ ...prev, email: e.target.value }))}
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Admin Password</label>
              <div className="relative">
                <Input
                  type={showPassword ? "text" : "password"}
                  placeholder="Admin Password"
                  value={credentials.password}
                  onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
                  required
                  className="pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-gray-700"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              <div className="mt-2 text-xs text-gray-600">
                <p className="font-medium">Password requirements:</p>
                <ul className="list-disc list-inside mt-1 space-y-1">
                  <li>At least 8 characters</li>
                  <li>Must include uppercase letter</li>
                  <li>Must include lowercase letter</li>
                  <li>Must include number</li>
                  <li>Must include special character (!@#$%^&*)</li>
                </ul>
              </div>
            </div>
            
            <Button 
              type="submit" 
              className="w-full bg-red-600 hover:bg-red-700"
              disabled={loading}
            >
              {loading ? <LoadingSpinner className="h-4 w-4 mr-2" /> : null}
              {loading ? 'Logging in...' : 'Login as Admin'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminLogin;
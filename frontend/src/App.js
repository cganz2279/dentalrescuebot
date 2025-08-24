import React, { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import HomePage from "./pages/HomePage";
import SpecialtyPage from "./pages/SpecialtyPage";
import ProcedurePage from "./pages/ProcedurePage";
import RegistrationPage from "./pages/RegistrationPage";
import PracticeSettingsPage from "./pages/PracticeSettingsPage";
import AddPatientPage from "./pages/AddPatientPage";
import AssignProcedurePage from "./pages/AssignProcedurePage";
import ProcedureLibraryPage from "./pages/ProcedureLibraryPage";
import AddStaffPage from "./pages/AddStaffPage";
import EditPatientPage from "./pages/EditPatientPage";
import EditProcedureAssignmentPage from "./pages/EditProcedureAssignmentPage";
import SimpleProcedureView from "./pages/SimpleProcedureView";
import RequestProcedurePage from "./pages/RequestProcedurePage";
import AdminRequestsPage from "./pages/AdminRequestsPage";
import LoginForm from "./components/LoginForm";
import PracticeRegistrationForm from "./components/PracticeRegistrationForm";
import AdminDashboard from "./components/AdminDashboard";
import PracticeDashboard from "./components/PracticeDashboard";
import { Toaster } from "./components/ui/toaster";
import LoadingSpinner from "./components/LoadingSpinner";

// Main App Content Component - for practice access
const AppContent = () => {
  const { user, loading, isAuthenticated, isPracticeStaff } = useAuth();
  const [authMode, setAuthMode] = useState('login'); // 'login' or 'register'
  
  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  // If user is authenticated and is practice staff - show practice dashboard
  if (isAuthenticated() && isPracticeStaff()) {
    return <PracticeDashboard />;
  }

  // Not authenticated - show practice login/register forms
  return (
    <>
      {authMode === 'login' && (
        <LoginForm 
          onSwitchToRegister={() => setAuthMode('register')}
        />
      )}
      {authMode === 'register' && (
        <PracticeRegistrationForm 
          onSwitchToLogin={() => setAuthMode('login')} 
        />
      )}
    </>
  );
};

// Admin App Content Component - for admin access
const AdminContent = () => {
  const { user, loading, isAuthenticated } = useAuth();
  
  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  // If user is authenticated and has admin role - show admin dashboard
  if (isAuthenticated() && (user?.role === 'super_admin' || user?.role === 'admin')) {
    return <AdminDashboard />;
  }

  // Not authenticated or not admin - show admin login form
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg max-width-md">
        <h1 className="text-2xl font-bold mb-4 text-center">Admin Access Required</h1>
        <p className="text-gray-600 mb-4 text-center">Please contact system administrator for access.</p>
        <div className="text-center">
          <button 
            onClick={() => window.location.href = '/'}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Go to Practice Portal
          </button>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Main routes */}
            <Route path="/" element={<AppContent />} />
            <Route path="/admin" element={<AppContent />} />
            
            {/* Public procedure routes */}
            <Route path="/specialties/:specialtyId" element={<SpecialtyPage />} />
            <Route path="/procedure/:procedureId" element={<ProcedurePage />} />
            <Route path="/library" element={<ProcedureLibraryPage />} />
            
            {/* Protected routes - will redirect to login if not authenticated */}
            <Route path="/practice-settings" element={<PracticeSettingsPage />} />
            <Route path="/add-patient" element={<AddPatientPage />} />
            <Route path="/assign-procedure" element={<AssignProcedurePage />} />
            <Route path="/add-staff" element={<AddStaffPage />} />
            <Route path="/edit-patient/:patientId" element={<EditPatientPage />} />
            <Route path="/edit-procedure/:assignmentId" element={<EditProcedureAssignmentPage />} />
            <Route path="/view-assignment/:assignmentId" element={<SimpleProcedureView />} />
            <Route path="/request-procedure" element={<RequestProcedurePage />} />
            <Route path="/admin-requests" element={<AdminRequestsPage />} />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </AuthProvider>
    </div>
  );
}

export default App;
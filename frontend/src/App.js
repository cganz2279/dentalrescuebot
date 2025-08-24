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
import PracticeRegistrationForm from "./components/PracticeRegistrationForm";
import LoginForm from "./components/LoginForm";
import AdminDashboard from "./components/AdminDashboard";
import PracticeDashboard from "./components/PracticeDashboard";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";
import { Toaster } from "./components/ui/toaster";
import LoadingSpinner from "./components/LoadingSpinner";

// Main App Content Component
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

  // Not authenticated - show login/register forms (dentist/practice only)
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

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<AppContent />} />
            <Route path="/admin" element={<AdminRoute />} />
            
            {/* Protected routes that require authentication */}
            <Route path="/practice-settings" element={<ProtectedRoute><PracticeSettingsPage /></ProtectedRoute>} />
            <Route path="/add-patient" element={<ProtectedRoute><AddPatientPage /></ProtectedRoute>} />
            <Route path="/assign-procedure" element={<ProtectedRoute><AssignProcedurePage /></ProtectedRoute>} />
            <Route path="/add-staff" element={<ProtectedRoute><AddStaffPage /></ProtectedRoute>} />
            <Route path="/edit-patient/:patientId" element={<ProtectedRoute><EditPatientPage /></ProtectedRoute>} />
            <Route path="/edit-procedure/:assignmentId" element={<ProtectedRoute><EditProcedureAssignmentPage /></ProtectedRoute>} />
            <Route path="/view-assignment/:assignmentId" element={<ProtectedRoute><SimpleProcedureView /></ProtectedRoute>} />
            <Route path="/request-procedure" element={<ProtectedRoute><RequestProcedurePage /></ProtectedRoute>} />
            <Route path="/admin-requests" element={<ProtectedRoute><AdminRequestsPage /></ProtectedRoute>} />
            
            {/* Public procedure routes */}
            <Route path="/specialties/:specialtyId" element={<SpecialtyPage />} />
            <Route path="/procedure/:procedureId" element={<ProcedurePage />} />
            <Route path="/library" element={<ProcedureLibraryPage />} />
            
            {/* Keep existing register route */}
            <Route path="/register" element={<RegistrationPage />} />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </AuthProvider>
    </div>
  );
}

export default App;
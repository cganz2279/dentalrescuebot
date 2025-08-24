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
import AdminDashboard from "./components/AdminDashboard";
import PracticeDashboard from "./components/PracticeDashboard";
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

  // If user is authenticated - show practice dashboard (dentist only)
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
            <Route path="/register" element={<RegistrationPage />} />
            <Route path="/practice-settings" element={<PracticeSettingsPage />} />
            <Route path="/add-patient" element={<AddPatientPage />} />
            <Route path="/assign-procedure" element={<AssignProcedurePage />} />
            <Route path="/library" element={<ProcedureLibraryPage />} />
            <Route path="/add-staff" element={<AddStaffPage />} />
            <Route path="/edit-patient/:patientId" element={<EditPatientPage />} />
            <Route path="/edit-procedure/:assignmentId" element={<EditProcedureAssignmentPage />} />
            <Route path="/view-assignment/:assignmentId" element={<SimpleProcedureView />} />
            <Route path="/request-procedure" element={<RequestProcedurePage />} />
            <Route path="/admin-requests" element={<AdminRequestsPage />} />
            <Route path="/procedure/:procedureId" element={<ProcedurePage />} />
            <Route path="/specialty/:specialtyId" element={<SpecialtyPage />} />
            <Route path="/*" element={<AppContent />} />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </AuthProvider>
    </div>
  );
}

export default App;
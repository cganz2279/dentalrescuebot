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
import ProcedureDetailsPage from "./pages/ProcedureDetailsPage";
import EditProcedurePage from "./pages/EditProcedurePage";
import EditPatientPage from "./pages/EditPatientPage";
import PatientManagementPage from "./pages/PatientManagementPage";
import RequestProcedurePage from "./pages/RequestProcedurePage";
import PracticeLibraryPage from "./pages/PracticeLibraryPage";
import DentistManagementPage from "./pages/DentistManagementPage";
import PatientLoginPage from "./pages/PatientLoginPage";
import PatientProcedureView from "./pages/PatientProcedureView";
import ProcedureViewPage from "./pages/ProcedureViewPage";
import PracticeProcedureView from "./pages/PracticeProcedureView";
import LoginForm from "./components/LoginForm";
import PracticeRegistrationForm from "./components/PracticeRegistrationForm";
import PracticeDashboard from "./components/PracticeDashboard";
import PatientDashboard from "./components/PatientDashboard";
import AdminLogin from "./components/AdminLogin";
import { Toaster } from "./components/ui/toaster";
import LoadingSpinner from "./components/LoadingSpinner";

// Main App Content Component
const AppContent = () => {
  const { user, loading, isAuthenticated, isPracticeStaff, isPatient } = useAuth();
  const [authMode, setAuthMode] = useState('login'); // 'login' or 'register'
  
  // Navigation state for public library
  const [currentView, setCurrentView] = useState('home');
  const [selectedSpecialty, setSelectedSpecialty] = useState(null);
  const [selectedProcedure, setSelectedProcedure] = useState(null);

  const handleSelectSpecialty = (specialtyId) => {
    setSelectedSpecialty(specialtyId);
    setCurrentView('specialty');
  };

  const handleSelectProcedure = (procedureId) => {
    setSelectedProcedure(procedureId);
    setCurrentView('procedure');
  };

  const handleBackToHome = () => {
    setCurrentView('home');
    setSelectedSpecialty(null);
    setSelectedProcedure(null);
  };

  const handleBackToSpecialty = () => {
    setCurrentView('specialty');
    setSelectedProcedure(null);
  };

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  // If user is authenticated
  if (isAuthenticated()) {
    // Practice staff/admin see the dashboard
    if (isPracticeStaff()) {
      return <PracticeDashboard />;
    }
    
    // Patients see the public library (for now)
    if (isPatient()) {
      return (
        <>
          {currentView === 'home' && (
            <HomePage 
              onSelectSpecialty={handleSelectSpecialty}
              onSelectProcedure={handleSelectProcedure}
            />
          )}
          {currentView === 'specialty' && (
            <SpecialtyPage 
              specialtyId={selectedSpecialty}
              onSelectProcedure={handleSelectProcedure}
              onBackToHome={handleBackToHome}
            />
          )}
          {currentView === 'procedure' && (
            <ProcedurePage 
              procedureId={selectedProcedure}
              onBackToHome={handleBackToHome}
              onBackToSpecialty={handleBackToSpecialty}
            />
          )}
        </>
      );
    }
  }

  // Not authenticated - show login/register forms
  return (
    <>
      {authMode === 'login' && (
        <LoginForm onSwitchToRegister={() => setAuthMode('register')} />
      )}
      {authMode === 'register' && (
        <PracticeRegistrationForm onSwitchToLogin={() => setAuthMode('login')} />
      )}
    </>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          {/* Admin Route - Must be EXACT path, not wildcard */}
          <Route path="/admin" element={<AdminLogin />} />
          
          {/* All other specific routes within AuthProvider */}
          <Route path="/register" element={
            <AuthProvider>
              <RegistrationPage />
            </AuthProvider>
          } />
          <Route path="/practice-settings" element={
            <AuthProvider>
              <PracticeSettingsPage />
            </AuthProvider>
          } />
          <Route path="/dentist-management" element={
            <AuthProvider>
              <DentistManagementPage />
            </AuthProvider>
          } />
          <Route path="/add-patient" element={
            <AuthProvider>
              <AddPatientPage />
            </AuthProvider>
          } />
          <Route path="/assign-procedure" element={
            <AuthProvider>
              <AssignProcedurePage />
            </AuthProvider>
          } />
          <Route path="/request-procedure" element={
            <AuthProvider>
              <RequestProcedurePage />
            </AuthProvider>
          } />
          <Route path="/patient-management" element={
            <AuthProvider>
              <PatientManagementPage />
            </AuthProvider>
          } />
          <Route path="/edit-patient" element={
            <AuthProvider>
              <EditPatientPage />
            </AuthProvider>
          } />
          <Route path="/procedure-details/:procedureId" element={
            <AuthProvider>
              <ProcedureDetailsPage />
            </AuthProvider>
          } />
          <Route path="/procedure-view/:procedureId" element={
            <AuthProvider>
              <ProcedureViewPage />
            </AuthProvider>
          } />
          <Route path="/practice-procedure/:procedureId" element={
            <AuthProvider>
              <PracticeProcedureView />
            </AuthProvider>
          } />
          <Route path="/edit-procedure/:procedureId" element={
            <AuthProvider>
              <EditProcedurePage />
            </AuthProvider>
          } />
          <Route path="/procedure-library" element={
            <AuthProvider>
              <PracticeLibraryPage />
            </AuthProvider>
          } />
          
          {/* Practice Notes Route - Main Login */}
          <Route path="/practice-notes" element={
            <AuthProvider>
              <AppContent />
            </AuthProvider>
          } />
          
          {/* Patient Routes */}
          <Route path="/patient/login" element={
            <AuthProvider>
              <PatientLoginPage />
            </AuthProvider>
          } />
          <Route path="/patient/dashboard" element={
            <AuthProvider>
              <PatientDashboard />
            </AuthProvider>
          } />
          <Route path="/patient/procedure/:assignmentId" element={
            <AuthProvider>
              <PatientProcedureView />
            </AuthProvider>
          } />
          
          <Route path="/dashboard" element={
            <AuthProvider>
              <AppContent />
            </AuthProvider>
          } />
          <Route path="/practice" element={
            <AuthProvider>
              <AppContent />
            </AuthProvider>
          } />
          <Route path="/" element={
            <AuthProvider>
              <AppContent />
            </AuthProvider>
          } />
          
          {/* Catch-all route - MUST BE LAST */}
          <Route path="*" element={
            <AuthProvider>
              <AppContent />
            </AuthProvider>
          } />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;
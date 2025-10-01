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
          {/* Admin Route - Outside AuthProvider */}
          <Route path="/admin/*" element={<AdminLogin />} />
          
          {/* All other routes within AuthProvider */}
          <Route path="*" element={
            <AuthProvider>
              <Routes>
                <Route path="/register" element={<RegistrationPage />} />
                <Route path="/practice-settings" element={<PracticeSettingsPage />} />
                <Route path="/dentist-management" element={<DentistManagementPage />} />
                <Route path="/add-patient" element={<AddPatientPage />} />
                <Route path="/assign-procedure" element={<AssignProcedurePage />} />
                <Route path="/request-procedure" element={<RequestProcedurePage />} />
                <Route path="/patient-management" element={<PatientManagementPage />} />
                <Route path="/edit-patient" element={<EditPatientPage />} />
                <Route path="/procedure-details/:procedureId" element={<ProcedureDetailsPage />} />
                <Route path="/procedure-view/:procedureId" element={<ProcedureViewPage />} />
                <Route path="/practice-procedure/:procedureId" element={<PracticeProcedureView />} />
                <Route path="/edit-procedure/:procedureId" element={<EditProcedurePage />} />
                <Route path="/procedure-library" element={<PracticeLibraryPage />} />
                
                {/* Practice Notes Route - Main Login */}
                <Route path="/practice-notes" element={<AppContent />} />
                
                {/* Patient Routes */}
                <Route path="/patient/login" element={<PatientLoginPage />} />
                <Route path="/patient/dashboard" element={<PatientDashboard />} />
                <Route path="/patient/procedure/:assignmentId" element={<PatientProcedureView />} />
                
                <Route path="/dashboard" element={<AppContent />} />
                <Route path="/practice" element={<AppContent />} />
                <Route path="*" element={<AppContent />} />
              </Routes>
            </AuthProvider>
          } />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;
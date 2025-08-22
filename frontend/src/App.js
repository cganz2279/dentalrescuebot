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
import AddStaffPage from "./pages/AddStaffPage";
import EditPatientPage from "./pages/EditPatientPage";
import RequestProcedurePage from "./pages/RequestProcedurePage";
import AdminRequestsPage from "./pages/AdminRequestsPage";
import LoginForm from "./components/LoginForm";
import PracticeRegistrationForm from "./components/PracticeRegistrationForm";
import PracticeDashboard from "./components/PracticeDashboard";
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

  // If user is authenticated - always show practice dashboard for dentists
  if (isAuthenticated()) {
    // Practice staff/admin see the dashboard
    if (isPracticeStaff()) {
      return <PracticeDashboard />;
    }
    
    // Fallback: any authenticated user sees practice dashboard
    return <PracticeDashboard />;
  }

  // Not authenticated - show login/register forms (practice staff only)
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
            <Route path="/add-staff" element={<AddStaffPage />} />
            <Route path="/edit-patient/:patientId" element={<EditPatientPage />} />
            <Route path="/request-procedure" element={<RequestProcedurePage />} />
            <Route path="/*" element={<AppContent />} />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </AuthProvider>
    </div>
  );
}

export default App;
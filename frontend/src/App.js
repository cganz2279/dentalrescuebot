import React, { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SpecialtyPage from "./pages/SpecialtyPage";
import ProcedurePage from "./pages/ProcedurePage";
import { Toaster } from "./components/ui/toaster";

function App() {
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

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
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
              <Toaster />
            </>
          } />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
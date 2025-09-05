import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Search, BookOpen, ArrowLeft, Eye, Download } from 'lucide-react';
import SpecialtyCard from '../components/SpecialtyCard';
import ProcedureCard from '../components/ProcedureCard';
import SpecialtyPage from './SpecialtyPage';
import LoadingSpinner, { LoadingCard, ErrorMessage } from '../components/LoadingSpinner';
import { dentalApi } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { generateProcedurePDF } from '../utils/pdfGenerator';
import { useAuth } from '../contexts/AuthContext';

const PracticeLibraryPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [specialties, setSpecialties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [selectedSpecialty, setSelectedSpecialty] = useState(null);
  const [selectedProcedure, setSelectedProcedure] = useState(null);
  const [currentView, setCurrentView] = useState('home');

  // Load specialties on component mount
  useEffect(() => {
    loadSpecialties();
  }, []);

  const loadSpecialties = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await dentalApi.getSpecialties();
      setSpecialties(response.data);
    } catch (err) {
      setError(err.message);
      toast({
        title: "Error",
        description: "Failed to load dental specialties. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    
    if (query.trim()) {
      setIsSearching(true);
      setSearchLoading(true);
      try {
        const response = await dentalApi.searchProcedures(query.trim());
        setSearchResults(response.data);
      } catch (err) {
        toast({
          title: "Search Error",
          description: "Failed to search procedures. Please try again.",
          variant: "destructive",
        });
        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    } else {
      setIsSearching(false);
      setSearchResults([]);
    }
  };

  const handleSelectSpecialty = (specialtyId) => {
    setSelectedSpecialty(specialtyId);
    setCurrentView('specialty');
  };

  const handleSelectProcedure = (procedureId) => {
    // Navigate to procedure view page for general procedure information
    navigate(`/procedure-view/${procedureId}`);
  };

  const handleBackToHome = () => {
    setCurrentView('home');
    setSelectedSpecialty(null);
    setSelectedProcedure(null);
    setIsSearching(false);
    setSearchQuery('');
  };

  const handleBackToSpecialty = () => {
    setCurrentView('specialty');
    setSelectedProcedure(null);
  };

  const handleViewProcedure = (procedure) => {
    // Navigate to procedure details page for viewing
    navigate(`/procedure-details/${procedure.id}`);
  };

  const handleDownloadPDF = async (procedure) => {
    try {
      toast({
        title: "Generating PDF...",
        description: "Please wait while we create your care guide.",
        variant: "default",
      });
      
      // Fetch complete procedure details for PDF generation
      const procedureResponse = await dentalApi.getProcedure(procedure.id);
      const fullProcedure = procedureResponse.data;
      
      // Add practice and user context from AuthContext
      const { user, practice } = authContext;
      
      // Add practice and user context to the procedure data
      const personalizedProcedure = {
        ...fullProcedure,
        practiceName: practice?.name || 'Your Dental Practice',
        practicePhone: practice?.phone || practice?.contactInfo?.phone,
        practiceAddress: practice?.address,
        // If this is for a specific dentist, include their info
        dentistName: user?.firstName && user?.lastName ? `Dr. ${user.firstName} ${user.lastName}` : null,
        // Add current user as the treating dentist if they're a dentist
        treatingDentist: user?.role === 'dentist' ? `${user.firstName} ${user.lastName}` : null
      };
      
      const success = await generateProcedurePDF(personalizedProcedure);
      
      if (success) {
        toast({
          title: "PDF Downloaded",
          description: `${procedure.name} care guide downloaded successfully.`,
          variant: "default",
        });
      } else {
        toast({
          title: "Download Failed",
          description: "Failed to generate PDF. Please try again.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('PDF download error:', error);
      toast({
        title: "Download Error",
        description: "An error occurred while generating the PDF. Please try again.",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="flex justify-center items-center py-32">
            <LoadingSpinner size="xl" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center mb-4">
            <Button 
              onClick={() => navigate('/dashboard')}
              variant="outline" 
              className="mr-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Procedure Library</h1>
              <p className="text-gray-600 mt-1">Browse and access post-operative care documents</p>
            </div>
          </div>

          {/* Search Bar */}
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Search procedures..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Content */}
        {isSearching ? (
          // Search Results
          <div>
            <h2 className="text-xl font-semibold mb-4">
              Search Results ({searchResults.length})
            </h2>
            {searchLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {Array.from({ length: 6 }).map((_, i) => (
                  <LoadingCard key={i} />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {searchResults.map((procedure) => (
                  <Card key={procedure.id} className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardHeader>
                      <CardTitle className="text-lg">{procedure.name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 mb-4">{procedure.description}</p>
                      <div className="flex gap-2">
                        <Button 
                          onClick={() => handleViewProcedure(procedure)}
                          size="sm"
                          className="flex-1"
                        >
                          <Eye className="h-4 w-4 mr-2" />
                          View
                        </Button>
                        <Button 
                          onClick={() => handleDownloadPDF(procedure)}
                          variant="outline"
                          size="sm"
                          className="flex-1"
                        >
                          <Download className="h-4 w-4 mr-2" />
                          PDF
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        ) : currentView === 'home' ? (
          // Specialties Grid
          <div>
            <h2 className="text-xl font-semibold mb-6 flex items-center">
              <BookOpen className="h-5 w-5 mr-2" />
              Browse by Specialty
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {specialties.map((specialty) => (
                <SpecialtyCard
                  key={specialty.id}
                  specialty={specialty}
                  onClick={() => handleSelectSpecialty(specialty.id)}
                />
              ))}
            </div>
          </div>
        ) : currentView === 'specialty' ? (
          // Show specialty page with procedures
          <SpecialtyPage
            specialtyId={selectedSpecialty}
            onSelectProcedure={handleSelectProcedure}
            onBackToHome={handleBackToHome}
          />
        ) : (
          // Individual Procedure View (handled by navigation to procedure-details)
          null
        )}

        {error && (
          <ErrorMessage 
            message={error} 
            onRetry={loadSpecialties}
          />
        )}
      </div>
    </div>
  );
};

export default PracticeLibraryPage;
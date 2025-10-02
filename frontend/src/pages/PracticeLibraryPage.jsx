import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { useToast } from '../hooks/use-toast';
import { 
  ArrowLeft, Search, BookOpen, Clock, AlertTriangle, 
  FileText, Download, User, Calendar, Mail, Phone
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';

const PracticeLibraryPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { practice, user } = useAuth();
  const [procedures, setProcedures] = useState([]);
  const [filteredProcedures, setFilteredProcedures] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedProcedure, setSelectedProcedure] = useState(null);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    fetchProcedures();
  }, []);

  useEffect(() => {
    const searchLower = searchQuery.toLowerCase().trim();
    
    if (!searchLower) {
      setFilteredProcedures(procedures);
      return;
    }
    
    // Alternative terms mapping (same as backend)
    const alternatives = {
      'zirconium': 'zirconia',
      'zircon': 'zirconia',
      'all-on-x': 'all on x',
      'allonx': 'all on x',
      'all-on-4': 'all on x',
      'all-on-6': 'all on x',
      'deep cleaning': 'scaling',
      'wisdom tooth': 'wisdom',
      'wisdom teeth': 'wisdom',
      'third molar': 'wisdom',
      'root canal': 'root canal',
      'rct': 'root canal',
      'implant': 'implant',
      'extraction': 'extraction',
      'filling': 'filling'
    };
    
    // Get search terms
    const searchTerms = [searchLower];
    if (alternatives[searchLower]) {
      searchTerms.push(alternatives[searchLower]);
    }
    
    const filtered = procedures.filter(procedure => {
      const name = procedure.name.toLowerCase();
      const specialtyName = (procedure.specialtyName || '').toLowerCase();
      const overview = (procedure.overview || '').toLowerCase();
      
      // Check each search term
      for (const term of searchTerms) {
        // Simple substring match
        if (name.includes(term) || specialtyName.includes(term) || overview.includes(term)) {
          return true;
        }
        
        // For multi-word terms, check if all words are present in name
        const words = term.split(' ');
        if (words.length > 1) {
          if (words.every(word => name.includes(word))) {
            return true;
          }
        }
      }
      
      return false;
    });
    
    // Sort by relevance (exact name matches first)
    filtered.sort((a, b) => {
      const aName = a.name.toLowerCase();
      const bName = b.name.toLowerCase();
      
      // Exact matches first
      if (aName.includes(searchLower) && !bName.includes(searchLower)) return -1;
      if (!aName.includes(searchLower) && bName.includes(searchLower)) return 1;
      
      // Alphabetical
      return aName.localeCompare(bName);
    });
    
    setFilteredProcedures(filtered);
  }, [searchQuery, procedures]);

  const fetchProcedures = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/procedures`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch procedures');
      }
      
      const result = await response.json();
      const data = result.success ? result.data : result;
      setProcedures(data);
      setFilteredProcedures(data);
    } catch (error) {
      console.error('Fetch procedures error:', error);
      toast({
        title: "Error",
        description: "Failed to load procedures",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleProcedureSelect = (procedure) => {
    setSelectedProcedure(procedure);
    setShowPreview(true);
  };

  const handleDownloadPDF = async (procedure) => {
    try {
      // FINAL RAW TEXT ONLY - CACHE BUSTED
      const { generateProcedurePDF } = await import('../utils/ENHANCED_PDF_WITH_LOGO');
      
      if (!procedure) {
        console.error('No procedure selected for PDF generation');
        return;
      }

      // Add practice information to procedure data
      const procedureForPDF = {
        ...procedure,
        practiceName: practice?.name || 'Dental Practice',
        practiceAddress: practice?.address || practice?.location || '',
        practicePhone: practice?.phone || '',
        practiceWebsite: practice?.website || '',
        practiceOfficeHours: practice?.officeHours || '',
        practiceEmergencyContact: practice?.emergencyContact || '',
      };

      console.log('🏥 PracticeLibraryPage - Generating PDF with practice data:', {
        practiceName: procedureForPDF.practiceName,
        practiceOfficeHours: procedureForPDF.practiceOfficeHours,
        practiceEmergencyContact: procedureForPDF.practiceEmergencyContact
      });

      const success = await generateProcedurePDF(procedureForPDF);
      
      if (success) {
        toast({
          title: "Success",
          description: `PDF generated for ${procedure.name}`,
        });
      }
    } catch (error) {
      console.error('PDF generation error:', error);
      toast({
        title: "Error",
        description: "Failed to generate PDF",
        variant: "destructive",
      });
    }
  };

  // Functions removed - Email and SMS buttons not needed in procedure library

  const formatDuration = (duration) => {
    if (!duration) return 'Variable';
    return duration;
  };

  const getSpecialtyColor = (specialty) => {
    const colors = {
      'oral-surgery': 'bg-red-100 text-red-800',
      'general-dentistry': 'bg-blue-100 text-blue-800',
      'periodontics': 'bg-green-100 text-green-800',
      'endodontics': 'bg-purple-100 text-purple-800',
      'orthodontics': 'bg-pink-100 text-pink-800',
      'prosthodontics': 'bg-orange-100 text-orange-800',
    };
    return colors[specialty] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading procedures...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/practice/dashboard')}
                className="flex items-center"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Procedure Library</h1>
                <p className="text-gray-600">Browse and access post-operative care documents</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">{practice?.name}</p>
              <p className="text-xs text-gray-500">Practice Administrator</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            type="text"
            placeholder="Search procedures..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Procedures Grid */}
      <div className="max-w-7xl mx-auto px-4 pb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProcedures.map((procedure) => (
            <Card key={procedure.id} className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg">{procedure.name}</CardTitle>
                  <Badge className={getSpecialtyColor(procedure.specialty)}>
                    {procedure.specialtyName || procedure.specialty}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {/* Duration removed - not needed */}
                  
                  <p className="text-sm text-gray-700 line-clamp-3">
                    {procedure.overview?.substring(0, 120)}...
                  </p>
                  
                  <div className="flex gap-2 pt-2">
                    <Button
                      size="sm"
                      onClick={() => handleProcedureSelect(procedure)}
                      className="flex-1"
                    >
                      <BookOpen className="h-4 w-4 mr-2" />
                      View Details
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDownloadPDF(procedure)}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      PDF
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredProcedures.length === 0 && !loading && (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No procedures found</h3>
            <p className="text-gray-600">
              {searchQuery ? 'Try adjusting your search terms' : 'No procedures available'}
            </p>
          </div>
        )}
      </div>

      {/* Procedure Preview Modal */}
      {showPreview && selectedProcedure && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 mb-2">
                    {selectedProcedure.name}
                  </h2>
                  <Badge className={getSpecialtyColor(selectedProcedure.specialty)}>
                    {selectedProcedure.specialtyName || selectedProcedure.specialty}
                  </Badge>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowPreview(false)}
                >
                  ×
                </Button>
              </div>
              
              <div className="space-y-4">
                {/* Duration removed - not needed */}
                
                <div>
                  <h3 className="font-semibold mb-2">Overview:</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">
                    {selectedProcedure.overview}
                  </p>
                </div>
              </div>
              
              <div className="flex gap-2 mt-6">
                <Button
                  onClick={() => handleDownloadPDF(selectedProcedure)}
                  className="flex-1"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download PDF
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowPreview(false)}
                >
                  Close
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PracticeLibraryPage;
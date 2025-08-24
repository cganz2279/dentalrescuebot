import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { ArrowLeft, FileText, Search, Eye, BookOpen } from 'lucide-react';
import { dentalApi } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const ProcedureLibraryPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [procedures, setProcedures] = useState([]);
  const [filteredProcedures, setFilteredProcedures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSpecialty, setSelectedSpecialty] = useState('all');
  const [specialties, setSpecialties] = useState([]);

  useEffect(() => {
    loadProcedures();
    loadSpecialties();
  }, []);

  useEffect(() => {
    filterProcedures();
  }, [procedures, searchTerm, selectedSpecialty]);

  const loadProcedures = async () => {
    try {
      setLoading(true);
      const response = await dentalApi.getProcedures();
      // Sort procedures alphabetically by name
      const sortedProcedures = response.data.sort((a, b) => a.name.localeCompare(b.name));
      setProcedures(sortedProcedures);
      console.log(`Loaded ${sortedProcedures.length} procedures for library`);
    } catch (err) {
      console.error('Failed to load procedures:', err);
      toast({
        title: "Error",
        description: "Failed to load procedures library",
        variant: "destructive", 
      });
    } finally {
      setLoading(false);
    }
  };

  const loadSpecialties = async () => {
    try {
      const response = await dentalApi.getSpecialties();
      setSpecialties(response.data);
    } catch (err) {
      console.error('Failed to load specialties:', err);
    }
  };

  const filterProcedures = () => {
    let filtered = procedures;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(procedure =>
        procedure.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        procedure.specialtyName?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by specialty
    if (selectedSpecialty !== 'all') {
      filtered = filtered.filter(procedure => procedure.specialty === selectedSpecialty);
    }

    setFilteredProcedures(filtered);
  };

  const handleProcedurePreview = (procedure) => {
    // Navigate to the procedure preview page
    navigate(`/procedure/${procedure.id}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Dashboard</span>
              </Button>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="flex items-center space-x-2">
                <BookOpen className="h-5 w-5 text-gray-600" />
                <h1 className="text-xl font-semibold text-gray-900">Procedure Library</h1>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Search and Filter */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search procedures..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <div className="w-full sm:w-48">
                <select
                  value={selectedSpecialty}
                  onChange={(e) => setSelectedSpecialty(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Specialties</option>
                  {specialties.map((specialty) => (
                    <option key={specialty.id} value={specialty.id}>
                      {specialty.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results Summary */}
        <div className="mb-6">
          <p className="text-gray-600">
            Showing {filteredProcedures.length} of {procedures.length} procedures
          </p>
        </div>

        {/* Procedures Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProcedures.map((procedure) => (
            <Card key={procedure.id} className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {procedure.name}
                    </h3>
                    <Badge variant="outline" className="text-xs">
                      {procedure.specialtyName}
                    </Badge>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {procedure.overview && (
                    <p className="text-sm text-gray-600 line-clamp-3">
                      {procedure.overview.substring(0, 120)}...
                    </p>
                  )}
                  
                  <div className="flex items-center justify-between">
                    <div className="text-xs text-gray-500">
                      Duration: {procedure.duration || 'Variable'}
                    </div>
                    <Button
                      size="sm"
                      onClick={() => handleProcedurePreview(procedure)}
                      className="flex items-center space-x-1"
                    >
                      <Eye className="h-3 w-3" />
                      <span>Preview</span>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Empty State */}
        {filteredProcedures.length === 0 && !loading && (
          <div className="text-center py-12">
            <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No procedures found</h3>
            <p className="text-gray-600">
              {searchTerm || selectedSpecialty !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : 'No procedures available in the library'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcedureLibraryPage;
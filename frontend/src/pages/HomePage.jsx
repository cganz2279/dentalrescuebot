import React, { useState, useEffect } from 'react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Search, BookOpen, Shield, Users } from 'lucide-react';
import SpecialtyCard from '../components/SpecialtyCard';
import ProcedureCard from '../components/ProcedureCard';
import LoadingSpinner, { LoadingCard, ErrorMessage } from '../components/LoadingSpinner';
import { dentalApi } from '../services/api';
import { useToast } from '../components/ui/use-toast';

const HomePage = ({ onSelectSpecialty, onSelectProcedure }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = (query) => {
    setSearchQuery(query);
    if (query.trim()) {
      setIsSearching(true);
      const results = searchProcedures(query);
      setSearchResults(results);
    } else {
      setIsSearching(false);
      setSearchResults([]);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Hero Section */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <div className="p-4 bg-blue-100 rounded-full">
                <BookOpen className="h-12 w-12 text-blue-600" />
              </div>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Post-Operative Dental Care Guide
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
              Your comprehensive resource for post-procedure care instructions, warning signs, 
              and recovery guidelines for all dental treatments.
            </p>
            
            {/* Search Bar */}
            <div className="max-w-md mx-auto mb-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <Input
                  type="text"
                  placeholder="Search procedures (e.g., root canal, extraction...)"
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="pl-10 pr-4 py-3 text-base border-2 border-gray-200 focus:border-blue-500 rounded-lg"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* Search Results */}
        {isSearching && (
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Search Results ({searchResults.length})
            </h2>
            {searchResults.length > 0 ? (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {searchResults.map((procedure) => (
                  <ProcedureCard
                    key={procedure.id}
                    procedure={procedure}
                    showSpecialty={true}
                    onViewDetails={() => onSelectProcedure(procedure.id)}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <Search className="h-16 w-16 mx-auto" />
                </div>
                <h3 className="text-lg font-semibold text-gray-600">No procedures found</h3>
                <p className="text-gray-500">Try searching with different keywords</p>
              </div>
            )}
          </div>
        )}

        {/* Features Section */}
        {!isSearching && (
          <div className="mb-16">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Everything You Need for Recovery
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Get detailed, professional guidance for your post-operative care
              </p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8 mb-16">
              <div className="text-center p-6 bg-white rounded-xl shadow-md border border-gray-100">
                <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mb-4 mx-auto">
                  <Shield className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold mb-3 text-gray-800">Step-by-Step Instructions</h3>
                <p className="text-gray-600">Detailed care instructions for every procedure to ensure proper healing</p>
              </div>
              
              <div className="text-center p-6 bg-white rounded-xl shadow-md border border-gray-100">
                <div className="bg-red-100 w-16 h-16 rounded-full flex items-center justify-center mb-4 mx-auto">
                  <Search className="h-8 w-8 text-red-600" />
                </div>
                <h3 className="text-xl font-semibold mb-3 text-gray-800">Warning Signs</h3>
                <p className="text-gray-600">Know when to contact your dentist with clear warning sign indicators</p>
              </div>
              
              <div className="text-center p-6 bg-white rounded-xl shadow-md border border-gray-100">
                <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mb-4 mx-auto">
                  <Users className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold mb-3 text-gray-800">Professional Guidance</h3>
                <p className="text-gray-600">Evidence-based recommendations from dental professionals</p>
              </div>
            </div>
          </div>
        )}

        {/* Dental Specialties */}
        {!isSearching && (
          <>
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Browse by Dental Specialty
              </h2>
              <p className="text-lg text-gray-600">
                Select your procedure category for specific post-operative care instructions
              </p>
            </div>
            
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {dentalSpecialties.map((specialty) => (
                <SpecialtyCard
                  key={specialty.id}
                  specialty={specialty}
                  onClick={() => onSelectSpecialty(specialty.id)}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default HomePage;
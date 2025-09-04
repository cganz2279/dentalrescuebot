import React, { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { ArrowLeft } from 'lucide-react';
import ProcedureCard from '../components/ProcedureCard';
import LoadingSpinner, { LoadingCard, ErrorMessage } from '../components/LoadingSpinner';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { dentalApi } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { generateProcedurePDF } from '../utils/pdfGenerator';

const SpecialtyPage = ({ specialtyId, onSelectProcedure, onBackToHome }) => {
  const [specialty, setSpecialty] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { toast } = useToast();

  useEffect(() => {
    if (specialtyId) {
      loadSpecialty();
    }
  }, [specialtyId]);

  const loadSpecialty = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await dentalApi.getSpecialty(specialtyId);
      setSpecialty(response.data);
    } catch (err) {
      setError(err.message);
      toast({
        title: "Error",
        description: "Failed to load specialty information. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
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
      
      const success = await generateProcedurePDF(fullProcedure);
      
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
        <Header 
          title="Loading..."
          subtitle="Loading specialty information..."
          showBackButton={true}
          onBackClick={onBackToHome}
          showBranding={false}
        />
        
        <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
          <div className="mb-8">
            <div className="h-6 bg-gray-200 rounded animate-pulse w-64 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded animate-pulse w-full mb-2"></div>
            <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4"></div>
          </div>
          
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <LoadingCard key={i} />
            ))}
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  if (error || !specialty) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full">
          <div className="flex items-center mb-4">
            <Button 
              variant="ghost" 
              onClick={onBackToHome}
              className="mr-4"
            >
              <ArrowLeft className="h-5 w-5" />
              Back to Home
            </Button>
          </div>
          <ErrorMessage 
            message={error || "Specialty not found"} 
            onRetry={loadSpecialty}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <Header
        title={specialty.name}
        subtitle={specialty.description}
        showBackButton={true}
        onBackClick={onBackToHome}
        showBranding={false}
      />

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Post-Operative Care Guides
          </h2>
          <p className="text-gray-600 mb-8">
            Select a procedure to view detailed post-operative care instructions, 
            warning signs, and recovery guidelines.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {specialty.procedures?.map((procedure) => (
            <ProcedureCard
              key={procedure.id}
              procedure={procedure}
              onViewDetails={() => onSelectProcedure(procedure.id)}
              onDownloadPDF={handleDownloadPDF}
              showPDFDownload={true}
            />
          ))}
        </div>

        {(!specialty.procedures || specialty.procedures.length === 0) && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <svg className="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-600">No procedures available</h3>
            <p className="text-gray-500">Check back later for more procedures in this specialty</p>
          </div>
        )}
      </div>
      
      {/* Footer */}
      <Footer />
    </div>
  );
};

export default SpecialtyPage;
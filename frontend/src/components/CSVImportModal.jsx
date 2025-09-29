import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { 
  Upload, 
  Download, 
  Users, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  FileText,
  X
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import { practiceApi } from '../services/authApi';
import LoadingSpinner from '../components/LoadingSpinner';

const CSVImportModal = ({ isOpen, onClose, onSuccess }) => {
  const { toast } = useToast();
  const [selectedFile, setSelectedFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [importResults, setImportResults] = useState(null);

  const handleDownloadTemplate = async () => {
    try {
      const blob = await practiceApi.downloadPatientCSVTemplate();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'patient_import_template.csv';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast({
        title: "Template Downloaded",
        description: "CSV template has been downloaded to your Downloads folder.",
        variant: "default",
      });
      
    } catch (error) {
      console.error('Template download error:', error);
      toast({
        title: "Download Failed",
        description: "Failed to download template. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith('.csv')) {
        toast({
          title: "Invalid File Type",
          description: "Please select a CSV file (.csv)",
          variant: "destructive",
        });
        return;
      }
      setSelectedFile(file);
      setImportResults(null);
    }
  };

  const handleImport = async () => {
    if (!selectedFile) {
      toast({
        title: "No File Selected",
        description: "Please select a CSV file to import.",
        variant: "destructive",
      });
      return;
    }

    setImporting(true);
    
    try {
      const results = await practiceApi.importPatientsCSV(selectedFile);
      
      setImportResults(results);
      
      // Show success toast
      const { summary } = results;
      let message = `Import completed: ${summary.successfulImports} patients added`;
      
      if (summary.failedImports > 0 || summary.duplicateEmails > 0) {
        message += `, ${summary.failedImports} failed`;
        if (summary.duplicateEmails > 0) {
          message += `, ${summary.duplicateEmails} duplicates skipped`;
        }
      }
      
      toast({
        title: summary.successfulImports > 0 ? "Import Completed" : "Import Issues Found",
        description: message,
        variant: summary.successfulImports > 0 ? "default" : "destructive",
      });
      
      // If successful imports, call onSuccess callback
      if (summary.successfulImports > 0) {
        onSuccess && onSuccess(results);
      }
      
    } catch (error) {
      console.error('CSV import error:', error);
      toast({
        title: "Import Failed",
        description: error.response?.data?.detail || "Failed to import CSV file. Please check the format and try again.",
        variant: "destructive",
      });
    } finally {
      setImporting(false);
    }
  };

  const handleClose = () => {
    setSelectedFile(null);
    setImportResults(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center">
            <Upload className="h-6 w-6 mr-3 text-blue-600" />
            <h2 className="text-xl font-semibold">Import Patients from CSV</h2>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="p-6">
          {!importResults ? (
            <>
              {/* Instructions */}
              <Alert className="mb-6 border-blue-200 bg-blue-50">
                <FileText className="h-4 w-4" />
                <AlertDescription>
                  <div className="space-y-2">
                    <p className="font-medium">CSV Import Instructions:</p>
                    <ul className="list-disc pl-4 space-y-1 text-sm">
                      <li><strong>Required columns:</strong> firstName, lastName, email, cellphone</li>
                      <li><strong>Optional columns:</strong> primaryDentist (e.g., "Dr. Smith")</li>
                      <li>Email addresses must be unique within your practice</li>
                      <li>Download the template below for the correct format</li>
                    </ul>
                  </div>
                </AlertDescription>
              </Alert>

              {/* Download Template */}
              <Card className="mb-6">
                <CardHeader>
                  <CardTitle className="flex items-center text-lg">
                    <Download className="h-5 w-5 mr-2 text-green-600" />
                    Step 1: Download Template
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-4">
                    Download our CSV template with sample data and the correct column headers.
                  </p>
                  <Button
                    onClick={handleDownloadTemplate}
                    variant="outline"
                    className="bg-green-50 text-green-700 border-green-200 hover:bg-green-100"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download CSV Template
                  </Button>
                </CardContent>
              </Card>

              {/* Upload File */}
              <Card className="mb-6">
                <CardHeader>
                  <CardTitle className="flex items-center text-lg">
                    <Upload className="h-5 w-5 mr-2 text-blue-600" />
                    Step 2: Upload Your CSV File
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="csvFile">Select CSV File</Label>
                      <Input
                        id="csvFile"
                        type="file"
                        accept=".csv"
                        onChange={handleFileSelect}
                        className="mt-1"
                      />
                    </div>
                    
                    {selectedFile && (
                      <Alert className="border-blue-200 bg-blue-50">
                        <CheckCircle className="h-4 w-4 text-blue-600" />
                        <AlertDescription>
                          <strong>File selected:</strong> {selectedFile.name} ({Math.round(selectedFile.size / 1024)} KB)
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Import Actions */}
              <div className="flex justify-end space-x-3">
                <Button
                  variant="outline"
                  onClick={handleClose}
                  disabled={importing}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleImport}
                  disabled={!selectedFile || importing}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {importing ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Importing...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Import Patients
                    </>
                  )}
                </Button>
              </div>
            </>
          ) : (
            /* Import Results */
            <div className="space-y-6">
              {/* Summary */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Users className="h-5 w-5 mr-2 text-blue-600" />
                    Import Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900">{importResults.summary.totalRows}</div>
                      <div className="text-sm text-gray-600">Total Rows</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{importResults.summary.successfulImports}</div>
                      <div className="text-sm text-gray-600">Successful</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">{importResults.summary.failedImports}</div>
                      <div className="text-sm text-gray-600">Failed</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">{importResults.summary.duplicateEmails}</div>
                      <div className="text-sm text-gray-600">Duplicates</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Successful Imports */}
              {importResults.details.successful.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-green-700">
                      <CheckCircle className="h-5 w-5 mr-2" />
                      Successfully Imported ({importResults.details.successful.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="max-h-40 overflow-y-auto">
                      {importResults.details.successful.map((patient, index) => (
                        <div key={index} className="flex justify-between items-center py-2 border-b last:border-b-0">
                          <span>{patient.name}</span>
                          <span className="text-sm text-gray-600">{patient.email}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Failed Imports */}
              {importResults.details.failed.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-red-700">
                      <XCircle className="h-5 w-5 mr-2" />
                      Failed Imports ({importResults.details.failed.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="max-h-40 overflow-y-auto space-y-2">
                      {importResults.details.failed.map((failure, index) => (
                        <Alert key={index} className="border-red-200 bg-red-50">
                          <AlertDescription>
                            <div className="space-y-1">
                              <p><strong>Row {failure.row}:</strong> {JSON.stringify(failure.data)}</p>
                              <p className="text-sm text-red-600">Errors: {failure.errors.join(', ')}</p>
                            </div>
                          </AlertDescription>
                        </Alert>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Duplicate Emails */}
              {importResults.details.duplicates.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-orange-700">
                      <AlertTriangle className="h-5 w-5 mr-2" />
                      Duplicate Emails Skipped ({importResults.details.duplicates.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="max-h-40 overflow-y-auto">
                      {importResults.details.duplicates.map((duplicate, index) => (
                        <div key={index} className="flex justify-between items-center py-2 border-b last:border-b-0">
                          <span>{duplicate.name}</span>
                          <span className="text-sm text-gray-600">{duplicate.email}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Close Button */}
              <div className="flex justify-end">
                <Button
                  onClick={handleClose}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Close
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CSVImportModal;
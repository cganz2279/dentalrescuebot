import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { ArrowLeft, FileText, Calendar, User, Clock, Download, AlertTriangle } from 'lucide-react';
import { practiceApi } from '../services/authApi';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const SimpleProcedureView = () => {
  const { procedureId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [procedure, setProcedure] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (procedureId) {
      loadProcedureData();
    }
  }, [procedureId]);

  const loadProcedureData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to get procedure assignment data
      const response = await practiceApi.getProcedureAssignment(procedureId);
      
      if (response.success && response.data) {
        setProcedure(response.data);
      } else {
        setError('Procedure not found');
      }
    } catch (err) {
      console.error('Failed to load procedure:', err);
      setError('Failed to load procedure data');
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = async () => {
    if (!procedure) return;
    
    try {
      // Import html2canvas and jsPDF for HTML-to-PDF conversion
      const html2canvas = (await import('html2canvas')).default;
      const { jsPDF } = await import('jspdf');
      
      // Create a printable version of the current page
      const printElement = document.createElement('div');
      printElement.innerHTML = `
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; padding: 20px; background: white; max-width: 800px; margin: 0 auto;">
          <!-- Header -->
          <div style="text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #000;">
            <h1 style="font-size: 24px; font-weight: bold; margin: 0 0 10px 0; color: #000;">POST-OPERATIVE CARE INSTRUCTIONS</h1>
            ${practice?.name ? `<h2 style="font-size: 16px; font-weight: bold; margin: 5px 0; color: #000;">${practice.name}</h2>` : ''}
            ${practice?.phone ? `<p style="font-size: 12px; margin: 5px 0; color: #666;">Phone: ${practice.phone}</p>` : ''}
          </div>

          <!-- Procedure Information -->
          <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
            <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 15px 0; color: #000;">PROCEDURE INFORMATION</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
              <div>
                <p style="font-size: 12px; font-weight: 500; color: #6b7280; margin: 0 0 5px 0;">Procedure Name</p>
                <p style="font-size: 16px; font-weight: bold; margin: 0; color: #000;">${procedure.procedureName}</p>
              </div>
              <div>
                <p style="font-size: 12px; font-weight: 500; color: #6b7280; margin: 0 0 5px 0;">Performing Dentist</p>
                <p style="font-size: 16px; margin: 0; color: #000;">Dr. ${procedure.dentistName}</p>
              </div>
              <div>
                <p style="font-size: 12px; font-weight: 500; color: #6b7280; margin: 0 0 5px 0;">Performed Date</p>
                <p style="font-size: 16px; margin: 0; color: #000;">${new Date(procedure.performedDate).toLocaleDateString()}</p>
              </div>
              <div>
                <p style="font-size: 12px; font-weight: 500; color: #6b7280; margin: 0 0 5px 0;">Status</p>
                <span style="background: #f0fdf4; color: #166534; padding: 4px 8px; border-radius: 4px; font-size: 12px; border: 1px solid #bbf7d0;">${procedure.status || 'active'}</span>
              </div>
            </div>
          </div>

          ${procedure.practiceNotes && procedure.practiceNotes.trim() ? `
          <!-- Practice Notes -->
          <div style="background: #f3e8ff; border: 1px solid #d8b4fe; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
            <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 15px 0; color: #7c3aed;">👤 Practice Notes</h3>
            <div style="background: #faf5ff; padding: 15px; border-radius: 6px;">
              <p style="color: #6b21a8; margin: 0; white-space: pre-wrap;">${procedure.practiceNotes}</p>
            </div>
          </div>
          ` : ''}

          ${procedure.customInstructions && procedure.customInstructions.length > 0 ? `
          <!-- Custom Instructions -->
          <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
            <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 15px 0; color: #2563eb;">📋 Custom Post-Operative Instructions</h3>
            <div style="background: #dbeafe; padding: 15px; border-radius: 6px;">
              <ul style="margin: 0; padding-left: 0; list-style: none;">
                ${procedure.customInstructions.map(instruction => `
                  <li style="margin-bottom: 8px; color: #1e40af;">
                    <span style="font-weight: bold; color: #2563eb;">•</span> ${instruction}
                  </li>
                `).join('')}
              </ul>
            </div>
          </div>
          ` : ''}

          <!-- Detailed Post-Operative Care Instructions -->
          <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
            <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 20px 0; color: #16a34a;">📄 Detailed Post-Operative Care Instructions</h3>
            
            <!-- Immediate Aftercare -->
            <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin-bottom: 15px; border-radius: 6px;">
              <h4 style="font-size: 14px; font-weight: bold; margin: 0 0 10px 0; color: #dc2626;">🕐 IMMEDIATE AFTERCARE (First 24 Hours)</h4>
              <ul style="margin: 0; padding-left: 0; list-style: none;">
                <li style="margin-bottom: 6px; color: #991b1b;"><span style="font-weight: bold; color: #dc2626;">•</span> Apply ice to the treated area for 15 minutes every hour for the first 24 hours to reduce swelling</li>
                <li style="margin-bottom: 6px; color: #991b1b;"><span style="font-weight: bold; color: #dc2626;">•</span> Keep gauze in place for 30-60 minutes after treatment, then remove gently</li>
                <li style="margin-bottom: 6px; color: #991b1b;"><span style="font-weight: bold; color: #dc2626;">•</span> Do not rinse or spit forcefully for the first 24 hours</li>
                <li style="margin-bottom: 6px; color: #991b1b;"><span style="font-weight: bold; color: #dc2626;">•</span> Take prescribed medications as directed by your dentist</li>
              </ul>
            </div>

            <!-- Diet Instructions -->
            <div style="background: #fff7ed; border-left: 4px solid #f97316; padding: 15px; margin-bottom: 15px; border-radius: 6px;">
              <h4 style="font-size: 14px; font-weight: bold; margin: 0 0 10px 0; color: #ea580c;">🍽️ DIET AND EATING INSTRUCTIONS</h4>
              <ul style="margin: 0; padding-left: 0; list-style: none;">
                <li style="margin-bottom: 6px; color: #9a3412;"><span style="font-weight: bold; color: #ea580c;">•</span> Stick to soft foods for the first 24-48 hours (yogurt, soup, mashed potatoes)</li>
                <li style="margin-bottom: 6px; color: #9a3412;"><span style="font-weight: bold; color: #ea580c;">•</span> Avoid hot liquids and foods until numbness wears off</li>
                <li style="margin-bottom: 6px; color: #9a3412;"><span style="font-weight: bold; color: #ea580c;">•</span> No alcohol while taking prescribed medications</li>
                <li style="margin-bottom: 6px; color: #9a3412;"><span style="font-weight: bold; color: #ea580c;">•</span> Avoid using straws for the first few days to prevent dry socket</li>
              </ul>
            </div>

            <!-- Medications -->
            <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 15px; margin-bottom: 15px; border-radius: 6px;">
              <h4 style="font-size: 14px; font-weight: bold; margin: 0 0 10px 0; color: #2563eb;">💊 MEDICATION GUIDELINES</h4>
              <ul style="margin: 0; padding-left: 0; list-style: none;">
                <li style="margin-bottom: 6px; color: #1e3a8a;"><span style="font-weight: bold; color: #2563eb;">•</span> Take all prescribed medications exactly as directed</li>
                <li style="margin-bottom: 6px; color: #1e3a8a;"><span style="font-weight: bold; color: #2563eb;">•</span> Complete the full course of antibiotics if prescribed</li>
                <li style="margin-bottom: 6px; color: #1e3a8a;"><span style="font-weight: bold; color: #2563eb;">•</span> Use over-the-counter pain relief as recommended (ibuprofen, acetaminophen)</li>
                <li style="margin-bottom: 6px; color: #1e3a8a;"><span style="font-weight: bold; color: #2563eb;">•</span> Do not exceed recommended dosages of any medication</li>
              </ul>
            </div>

            <!-- Warning Signs -->
            <div style="background: #fef2f2; border: 2px solid #ef4444; padding: 15px; margin-bottom: 15px; border-radius: 6px;">
              <h4 style="font-size: 14px; font-weight: bold; margin: 0 0 10px 0; color: #dc2626;">⚠️ WHEN TO CONTACT YOUR DENTIST IMMEDIATELY</h4>
              <ul style="margin: 0; padding-left: 0; list-style: none;">
                <li style="margin-bottom: 6px; color: #7f1d1d;"><span style="font-weight: bold; color: #dc2626;">•</span> Severe or worsening pain after 48 hours</li>
                <li style="margin-bottom: 6px; color: #7f1d1d;"><span style="font-weight: bold; color: #dc2626;">•</span> Excessive bleeding that does not stop with gentle pressure</li>
                <li style="margin-bottom: 6px; color: #7f1d1d;"><span style="font-weight: bold; color: #dc2626;">•</span> Signs of infection: fever, excessive swelling, pus, or foul taste</li>
                <li style="margin-bottom: 6px; color: #7f1d1d;"><span style="font-weight: bold; color: #dc2626;">•</span> Numbness that persists beyond the expected timeframe</li>
                <li style="margin-bottom: 6px; color: #7f1d1d;"><span style="font-weight: bold; color: #dc2626;">•</span> Difficulty swallowing or breathing</li>
              </ul>
            </div>
          </div>

          <!-- General Post-Operative Care -->
          <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
            <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 15px 0; color: #16a34a;">📋 General Post-Operative Care</h3>
            <div style="background: #dcfce7; padding: 15px; border-radius: 6px;">
              <ul style="margin: 0; padding-left: 0; list-style: none;">
                <li style="margin-bottom: 8px; color: #166534;"><span style="font-weight: bold; color: #16a34a;">•</span> Follow all post-operative care instructions carefully</li>
                <li style="margin-bottom: 8px; color: #166534;"><span style="font-weight: bold; color: #16a34a;">•</span> Take prescribed medications as directed</li>
                <li style="margin-bottom: 8px; color: #166534;"><span style="font-weight: bold; color: #16a34a;">•</span> Contact office if you experience any complications</li>
                <li style="margin-bottom: 8px; color: #166534;"><span style="font-weight: bold; color: #16a34a;">•</span> Attend follow-up appointments as scheduled</li>
              </ul>
            </div>
          </div>

          <!-- Contact Information -->
          <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 30px;">
            <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 15px 0; color: #374151;">📞 Contact Information</h3>
            <div style="background: #f3f4f6; padding: 15px; border-radius: 6px;">
              <p style="color: #374151; margin: 0 0 10px 0;">For questions or concerns about this procedure, please contact your dental office during regular business hours or follow the emergency contact instructions provided.</p>
            </div>
          </div>

          <!-- Patient Acknowledgment -->
          <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
            <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 15px 0; color: #000;">PATIENT ACKNOWLEDGMENT</h3>
            <p style="margin: 0 0 20px 0; color: #374151;">I acknowledge that I have received and understand these post-operative care instructions. I will follow these instructions carefully and contact my dental office if I have any questions or concerns.</p>
            
            <div style="display: flex; justify-content: space-between; margin-top: 30px;">
              <div style="width: 45%;">
                <div style="border-bottom: 1px solid #000; height: 1px; margin-bottom: 8px;"></div>
                <p style="font-size: 12px; margin: 0; color: #666;">Patient Signature</p>
              </div>
              <div style="width: 30%;">
                <div style="border-bottom: 1px solid #000; height: 1px; margin-bottom: 8px;"></div>
                <p style="font-size: 12px; margin: 0; color: #666;">Date</p>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div style="text-align: center; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 10px; color: #666;">
            <p style="margin: 0 0 5px 0;">DISCLAIMER: This information is for educational purposes only and does not replace professional medical advice.</p>
            <p style="margin: 0 0 5px 0;">Always consult your dentist or physician for specific medical concerns.</p>
            <p style="margin: 0;">Generated on: ${new Date().toLocaleDateString()} | DentalRescueBot - www.theoncallbot.com</p>
          </div>
        </div>
      `;
      
      // Append to body temporarily
      printElement.style.position = 'absolute';
      printElement.style.left = '-9999px';
      printElement.style.top = '-9999px';
      printElement.style.width = '800px';
      document.body.appendChild(printElement);
      
      // Convert HTML to canvas
      const canvas = await html2canvas(printElement, {
        scale: 2,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff',
        width: 800,
        height: printElement.offsetHeight
      });
      
      // Remove temporary element
      document.body.removeChild(printElement);
      
      // Create PDF
      const pdf = new jsPDF('p', 'mm', 'a4');
      const imgData = canvas.toDataURL('image/png');
      
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = pdfWidth - 20; // 10mm margin on each side
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      
      let heightLeft = imgHeight;
      let position = 10; // 10mm top margin
      
      // Add first page
      pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
      heightLeft -= pdfHeight - 20; // Account for margins
      
      // Add additional pages if needed
      while (heightLeft >= 0) {
        position = heightLeft - imgHeight + 10;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
        heightLeft -= pdfHeight - 20;
      }
      
      // Save the PDF
      const fileName = `${procedure.procedureName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_post_op_instructions.pdf`;
      pdf.save(fileName);
      
      toast({
        title: "Success",
        description: `PDF for ${procedure.procedureName} downloaded successfully`,
        variant: "default",
      });
    } catch (err) {
      console.error('Print error:', err);
      toast({
        title: "Error", 
        description: "Failed to generate PDF: " + (err.message || 'Unknown error'),
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (error || !procedure) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Dashboard</span>
              </Button>
            </div>
          </div>
        </div>
        <div className="max-w-4xl mx-auto py-8 px-4 text-center">
          <p className="text-red-600">{error || 'Procedure not found'}</p>
        </div>
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
                <FileText className="h-5 w-5 text-gray-600" />
                <h1 className="text-xl font-semibold text-gray-900">{procedure.procedureName}</h1>
              </div>
            </div>
            <Button onClick={handlePrint} className="flex items-center space-x-2">
              <Download className="h-4 w-4" />
              <span>Download PDF</span>
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* Procedure Info */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-6 w-6 text-blue-600" />
                <span>Procedure Information</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Procedure Name</h3>
                  <p className="text-lg font-semibold">{procedure.procedureName}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Performing Dentist</h3>
                  <p className="text-lg">Dr. {procedure.dentistName}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Performed Date</h3>
                  <p className="text-lg flex items-center">
                    <Calendar className="h-4 w-4 mr-2 text-green-600" />
                    {new Date(procedure.performedDate).toLocaleDateString()}
                  </p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Status</h3>
                  <Badge variant="outline" className="text-green-600 border-green-600">
                    {procedure.status || 'Active'}
                  </Badge>
                </div>

                {procedure.followUpDate && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Follow-up Date</h3>
                    <p className="text-lg flex items-center">
                      <Clock className="h-4 w-4 mr-2 text-orange-600" />
                      {new Date(procedure.followUpDate).toLocaleDateString()}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Practice Notes */}
          {procedure.practiceNotes && procedure.practiceNotes.trim() && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="h-5 w-5 text-purple-600" />
                  <span>Practice Notes</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <p className="text-purple-800 whitespace-pre-wrap">{procedure.practiceNotes}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Custom Instructions */}
          {procedure.customInstructions && procedure.customInstructions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <FileText className="h-5 w-5 text-blue-600" />
                  <span>Custom Post-Operative Instructions</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <ul className="space-y-2">
                    {procedure.customInstructions.map((instruction, index) => (
                      <li key={index} className="flex items-start space-x-2 text-blue-800">
                        <span className="font-bold text-blue-600">•</span>
                        <span>{instruction}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Comprehensive Post-Operative Care Instructions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-green-600" />
                <span>Detailed Post-Operative Care Instructions</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Immediate Aftercare */}
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                    <Clock className="h-4 w-4 mr-2 text-red-600" />
                    Immediate Aftercare (First 24 Hours)
                  </h4>
                  <div className="bg-red-50 p-4 rounded-lg">
                    <ul className="space-y-2 text-red-800">
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Apply ice to the treated area for 15 minutes every hour for the first 24 hours to reduce swelling</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Keep gauze in place for 30-60 minutes after treatment, then remove gently</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Do not rinse or spit forcefully for the first 24 hours</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Take prescribed medications as directed by your dentist</span>
                      </li>
                    </ul>
                  </div>
                </div>

                {/* Diet Instructions */}
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                    <User className="h-4 w-4 mr-2 text-orange-600" />
                    Diet and Eating Instructions
                  </h4>
                  <div className="bg-orange-50 p-4 rounded-lg">
                    <ul className="space-y-2 text-orange-800">
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-orange-600">•</span>
                        <span>Stick to soft foods for the first 24-48 hours (yogurt, soup, mashed potatoes)</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-orange-600">•</span>
                        <span>Avoid hot liquids and foods until numbness wears off</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-orange-600">•</span>
                        <span>No alcohol while taking prescribed medications</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-orange-600">•</span>
                        <span>Avoid using straws for the first few days to prevent dry socket</span>
                      </li>
                    </ul>
                  </div>
                </div>

                {/* Medication Instructions */}
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                    <Calendar className="h-4 w-4 mr-2 text-blue-600" />
                    Medication Guidelines
                  </h4>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <ul className="space-y-2 text-blue-800">
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-blue-600">•</span>
                        <span>Take all prescribed medications exactly as directed</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-blue-600">•</span>
                        <span>Complete the full course of antibiotics if prescribed</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-blue-600">•</span>
                        <span>Use over-the-counter pain relief as recommended (ibuprofen, acetaminophen)</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-blue-600">•</span>
                        <span>Do not exceed recommended dosages of any medication</span>
                      </li>
                    </ul>
                  </div>
                </div>

                {/* Warning Signs */}
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                    <AlertTriangle className="h-4 w-4 mr-2 text-red-600" />
                    ⚠️ When to Contact Your Dentist Immediately
                  </h4>
                  <div className="bg-red-100 border-l-4 border-red-500 p-4 rounded-lg">
                    <ul className="space-y-2 text-red-900">
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Severe or worsening pain after 48 hours</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Excessive bleeding that does not stop with gentle pressure</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Signs of infection: fever, excessive swelling, pus, or foul taste</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Numbness that persists beyond the expected timeframe</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="font-bold text-red-600">•</span>
                        <span>Difficulty swallowing or breathing</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* General Care Instructions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calendar className="h-5 w-5 text-green-600" />
                <span>General Post-Operative Care</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-green-50 p-4 rounded-lg">
                <ul className="space-y-2 text-green-800">
                  <li className="flex items-start space-x-2">
                    <span className="font-bold text-green-600">•</span>
                    <span>Follow all post-operative care instructions carefully</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="font-bold text-green-600">•</span>
                    <span>Take prescribed medications as directed</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="font-bold text-green-600">•</span>
                    <span>Contact office if you experience any complications</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="font-bold text-green-600">•</span>
                    <span>Attend follow-up appointments as scheduled</span>
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Contact Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <User className="h-5 w-5 text-gray-600" />
                <span>Contact Information</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-700">
                  For questions or concerns about this procedure, please contact your dental office 
                  during regular business hours or follow the emergency contact instructions provided.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default SimpleProcedureView;
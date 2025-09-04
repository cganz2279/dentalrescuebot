import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Clock, AlertTriangle, Utensils, Activity, Eye, Download } from 'lucide-react';
import { Button } from './ui/button';

const ProcedureCard = ({ 
  procedure, 
  onViewDetails, 
  onDownloadPDF, 
  showSpecialty = false,
  showPDFDownload = false 
}) => {
  return (
    <Card className="hover:shadow-lg transition-all duration-300 border-l-4 border-l-blue-500 bg-white">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg font-semibold text-gray-800 leading-tight">
            {procedure.name}
          </CardTitle>
          {showSpecialty && (
            <Badge variant="secondary" className="ml-2 text-xs">
              {procedure.specialtyName}
            </Badge>
          )}
        </div>
        <div className="flex items-center text-sm text-gray-600 mt-2">
          <Clock className="h-4 w-4 mr-1 text-blue-500" />
          {procedure.duration}
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-3">
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="flex items-center text-gray-600">
              <Activity className="h-3 w-3 mr-1 text-green-500" />
              <span>Instructions</span>
            </div>
            <div className="flex items-center text-gray-600">
              <Utensils className="h-3 w-3 mr-1 text-orange-500" />
              <span>Diet Guide</span>
            </div>
            <div className="flex items-center text-gray-600">
              <AlertTriangle className="h-3 w-3 mr-1 text-red-500" />
              <span>Warning Signs</span>
            </div>
          </div>
          
          {showPDFDownload ? (
            <div className="flex gap-2">
              <Button 
                onClick={onViewDetails}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white transition-colors duration-200"
                size="sm"
              >
                <Eye className="h-4 w-4 mr-2" />
                View
              </Button>
              <Button 
                onClick={() => onDownloadPDF && onDownloadPDF(procedure)}
                variant="outline"
                className="flex-1 border-blue-200 hover:bg-blue-50 transition-colors duration-200"
                size="sm"
              >
                <Download className="h-4 w-4 mr-2" />
                PDF
              </Button>
            </div>
          ) : (
            <Button 
              onClick={onViewDetails}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white transition-colors duration-200"
            >
              View Post-Op Guide
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ProcedureCard;
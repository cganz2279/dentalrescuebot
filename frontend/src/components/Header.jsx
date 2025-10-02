import React from 'react';
import { Button } from './ui/button';
import { ArrowLeft } from 'lucide-react';

const Header = ({ 
  title, 
  subtitle, 
  showBackButton = false, 
  onBackClick,
  showBranding = true 
}) => {
  return (
    <div className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Company Logo */}
        {showBranding && (
          <div className="flex justify-center mb-6">
            <img 
              src="https://customer-assets.emergentagent.com/job_dentist-dashboard-2/artifacts/tjqph8wg_ChatGPT%20Image%20Sep%2028%2C%202025%2C%2011_41_56%20PM.png"
              alt="Dental Aftercare Notes Logo"
              className="h-16 w-auto"
              onError={(e) => {
                console.error('Logo failed to load');
                e.target.style.display = 'none';
              }}
            />
          </div>
        )}
        
        {/* Navigation and Title */}
        <div className="flex items-center">
          {showBackButton && onBackClick && (
            <Button 
              variant="ghost" 
              onClick={onBackClick}
              className="mr-4 p-2 hover:bg-gray-100 rounded-full"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
          )}
          
          <div className="flex-1">
            {title && (
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {title}
              </h1>
            )}
            {subtitle && (
              <p className="text-lg text-gray-600">
                {subtitle}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;
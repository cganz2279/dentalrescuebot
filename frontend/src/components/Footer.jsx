import React from 'react';
import { ExternalLink } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-16">
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="text-center space-y-4">
          {/* Company URL */}
          <div>
            <a 
              href="https://www.theoncallbot.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium transition-colors duration-200"
            >
              www.theoncallbot.com
              <ExternalLink className="h-4 w-4 ml-1" />
            </a>
          </div>
          
          {/* Copyright Notice */}
          <div className="text-sm text-gray-600">
            Copyright © The OnCall Bot LLC 2025. All rights reserved.
          </div>
          
          {/* Additional Info */}
          <div className="text-xs text-gray-500">
            Professional dental post-operative care guidance
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
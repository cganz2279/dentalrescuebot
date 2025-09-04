import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { 
  Activity, 
  Scissors, 
  Crown, 
  Heart, 
  Shield, 
  Zap, 
  Baby 
} from 'lucide-react';

const iconMap = {
  Activity,
  Scissors,
  Crown,
  Heart,
  Shield,
  Zap,
  Baby
};

const SpecialtyCard = ({ specialty, onClick }) => {
  const IconComponent = iconMap[specialty.icon] || Activity;
  
  return (
    <Card 
      className={`cursor-pointer hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 ${specialty.color} border-2`}
      onClick={onClick}
    >
      <CardHeader className="text-center pb-3">
        <div className="flex justify-center mb-3">
          <div className="p-3 rounded-full bg-white shadow-md">
            <IconComponent className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <CardTitle className="text-xl font-bold text-gray-800">
          {specialty.name}
        </CardTitle>
      </CardHeader>
      <CardContent className="text-center pt-0">
        <p className="text-gray-600 text-sm mb-4 leading-relaxed">
          {specialty.description}
        </p>
        <Badge variant="outline" className="text-xs font-medium">
          {specialty.procedureCount || 0} procedures
        </Badge>
      </CardContent>
    </Card>
  );
};

export default SpecialtyCard;
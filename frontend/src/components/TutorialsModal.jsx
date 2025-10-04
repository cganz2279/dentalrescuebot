import React, { useState, useEffect } from 'react';
import { X, Play, Clock, BookOpen } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import LoadingSpinner, { ErrorMessage } from './LoadingSpinner';

const TutorialsModal = ({ isOpen, onClose }) => {
  const [tutorials, setTutorials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTutorial, setSelectedTutorial] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    if (isOpen) {
      loadTutorials();
    }
  }, [isOpen]);

  const loadTutorials = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tutorials`);
      
      if (response.ok) {
        const data = await response.json();
        setTutorials(data);
      } else {
        setError('Failed to load tutorials');
      }
    } catch (err) {
      console.error('Error loading tutorials:', err);
      setError('Failed to load tutorials');
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'Unknown duration';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const categories = [...new Set(tutorials.map(t => t.category))];
  const filteredTutorials = selectedCategory === 'all' 
    ? tutorials 
    : tutorials.filter(t => t.category === selectedCategory);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden flex">
        {/* Sidebar with tutorial list */}
        <div className="w-1/3 border-r bg-gray-50 flex flex-col">
          <div className="p-4 border-b bg-white">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold flex items-center">
                <BookOpen className="h-5 w-5 mr-2" />
                Tutorials
              </h2>
              <Button variant="ghost" size="sm" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            {/* Category filter */}
            <div className="flex flex-wrap gap-2">
              <Badge 
                variant={selectedCategory === 'all' ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => setSelectedCategory('all')}
              >
                All
              </Badge>
              {categories.map(category => (
                <Badge 
                  key={category}
                  variant={selectedCategory === category ? 'default' : 'outline'}
                  className="cursor-pointer capitalize"
                  onClick={() => setSelectedCategory(category)}
                >
                  {category}
                </Badge>
              ))}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {loading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner />
              </div>
            ) : error ? (
              <ErrorMessage message={error} onRetry={loadTutorials} />
            ) : filteredTutorials.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <BookOpen className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No tutorials available</p>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredTutorials.map(tutorial => (
                  <Card 
                    key={tutorial.id} 
                    className={`cursor-pointer transition-colors hover:bg-blue-50 ${
                      selectedTutorial?.id === tutorial.id ? 'bg-blue-100 border-blue-300' : ''
                    }`}
                    onClick={() => setSelectedTutorial(tutorial)}
                  >
                    <CardContent className="p-3">
                      <h3 className="font-medium text-sm mb-1 line-clamp-2">{tutorial.title}</h3>
                      <p className="text-xs text-gray-600 mb-2 line-clamp-2">{tutorial.description}</p>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span className="flex items-center">
                          <Clock className="h-3 w-3 mr-1" />
                          {formatDuration(tutorial.duration)}
                        </span>
                        <Badge variant="outline" className="text-xs">
                          {tutorial.category}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Main content area */}
        <div className="flex-1 flex flex-col">
          {selectedTutorial ? (
            <>
              <div className="p-4 border-b">
                <h1 className="text-2xl font-bold mb-2">{selectedTutorial.title}</h1>
                <p className="text-gray-600 mb-3">{selectedTutorial.description}</p>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span className="flex items-center">
                    <Clock className="h-4 w-4 mr-1" />
                    Duration: {formatDuration(selectedTutorial.duration)}
                  </span>
                  <Badge variant="outline" className="capitalize">
                    {selectedTutorial.category}
                  </Badge>
                </div>
              </div>
              
              <div className="flex-1 p-4">
                <div className="bg-black rounded-lg overflow-hidden h-full flex items-center justify-center">
                  <video
                    key={selectedTutorial.id}
                    controls
                    className="w-full h-full max-h-[500px]"
                    poster={selectedTutorial.thumbnail_url}
                  >
                    <source src={`${process.env.REACT_APP_BACKEND_URL}/api/video/tutorial/${selectedTutorial.video_url.split('/').pop()}`} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center text-gray-500">
                <Play className="h-16 w-16 mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-medium mb-2">Select a Tutorial</h3>
                <p>Choose a tutorial from the list to start learning</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TutorialsModal;
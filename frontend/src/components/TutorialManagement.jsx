import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Upload, 
  Play, 
  Eye, 
  EyeOff,
  Clock,
  BookOpen,
  X,
  Save
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Label } from './ui/label';
import LoadingSpinner, { ErrorMessage } from './LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const TutorialManagement = ({ isOpen, onClose, adminToken }) => {
  const [tutorials, setTutorials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTutorial, setEditingTutorial] = useState(null);
  const [uploading, setUploading] = useState(false);
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'general',
    order: 0,
    video: null
  });

  const [editFormData, setEditFormData] = useState({
    title: '',
    description: '',
    category: 'general',
    order: 0,
    is_active: true
  });

  useEffect(() => {
    if (isOpen) {
      loadTutorials();
    }
  }, [isOpen]);

  const loadTutorials = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/tutorials`, {
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        }
      });
      
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

  const handleCreateTutorial = async (e) => {
    e.preventDefault();
    
    if (!formData.video) {
      toast({
        title: "Error",
        description: "Please select a video file",
        variant: "destructive"
      });
      return;
    }

    try {
      setUploading(true);
      
      const form = new FormData();
      form.append('title', formData.title);
      form.append('description', formData.description);
      form.append('category', formData.category);
      form.append('order', formData.order.toString());
      form.append('video', formData.video);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/tutorials`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${adminToken}`
        },
        body: form
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Tutorial created successfully"
        });
        setShowAddForm(false);
        setFormData({
          title: '',
          description: '',
          category: 'general',
          order: 0,
          video: null
        });
        loadTutorials();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create tutorial');
      }
    } catch (err) {
      console.error('Error creating tutorial:', err);
      toast({
        title: "Error",
        description: err.message || "Failed to create tutorial",
        variant: "destructive"
      });
    } finally {
      setUploading(false);
    }
  };

  const handleUpdateTutorial = async (tutorialId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/tutorials/${tutorialId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(editFormData)
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Tutorial updated successfully"
        });
        setEditingTutorial(null);
        loadTutorials();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update tutorial');
      }
    } catch (err) {
      console.error('Error updating tutorial:', err);
      toast({
        title: "Error",
        description: err.message || "Failed to update tutorial",
        variant: "destructive"
      });
    }
  };

  const handleDeleteTutorial = async (tutorialId) => {
    if (!window.confirm('Are you sure you want to delete this tutorial? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/tutorials/${tutorialId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${adminToken}`
        }
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Tutorial deleted successfully"
        });
        loadTutorials();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete tutorial');
      }
    } catch (err) {
      console.error('Error deleting tutorial:', err);
      toast({
        title: "Error",
        description: err.message || "Failed to delete tutorial",
        variant: "destructive"
      });
    }
  };

  const startEditing = (tutorial) => {
    setEditingTutorial(tutorial.id);
    setEditFormData({
      title: tutorial.title,
      description: tutorial.description,
      category: tutorial.category,
      order: tutorial.order,
      is_active: tutorial.is_active
    });
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'Unknown';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold flex items-center">
              <BookOpen className="h-6 w-6 mr-3" />
              Tutorial Management
            </h2>
            <div className="flex gap-2">
              <Button onClick={() => setShowAddForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add Tutorial
              </Button>
              <Button variant="ghost" size="sm" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex justify-center py-8">
              <LoadingSpinner />
            </div>
          ) : error ? (
            <ErrorMessage message={error} onRetry={loadTutorials} />
          ) : (
            <div className="grid gap-4">
              {tutorials.map(tutorial => (
                <Card key={tutorial.id}>
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        {editingTutorial === tutorial.id ? (
                          <div className="space-y-3">
                            <Input
                              value={editFormData.title}
                              onChange={(e) => setEditFormData({...editFormData, title: e.target.value})}
                              placeholder="Tutorial Title"
                            />
                            <Textarea
                              value={editFormData.description}
                              onChange={(e) => setEditFormData({...editFormData, description: e.target.value})}
                              placeholder="Tutorial Description"
                              rows={2}
                            />
                            <div className="flex gap-3">
                              <Input
                                value={editFormData.category}
                                onChange={(e) => setEditFormData({...editFormData, category: e.target.value})}
                                placeholder="Category"
                                className="w-32"
                              />
                              <Input
                                type="number"
                                value={editFormData.order}
                                onChange={(e) => setEditFormData({...editFormData, order: parseInt(e.target.value)})}
                                placeholder="Order"
                                className="w-24"
                              />
                              <label className="flex items-center gap-2 text-sm">
                                <input
                                  type="checkbox"
                                  checked={editFormData.is_active}
                                  onChange={(e) => setEditFormData({...editFormData, is_active: e.target.checked})}
                                />
                                Active
                              </label>
                            </div>
                          </div>
                        ) : (
                          <>
                            <CardTitle className="flex items-center gap-2 mb-1">
                              {tutorial.title}
                              <Badge variant={tutorial.is_active ? 'default' : 'secondary'}>
                                {tutorial.is_active ? 'Active' : 'Inactive'}
                              </Badge>
                            </CardTitle>
                            <p className="text-gray-600 text-sm mb-2">{tutorial.description}</p>
                            <div className="flex items-center gap-4 text-xs text-gray-500">
                              <span className="flex items-center">
                                <Clock className="h-3 w-3 mr-1" />
                                {formatDuration(tutorial.duration)}
                              </span>
                              <Badge variant="outline" className="text-xs">
                                {tutorial.category}
                              </Badge>
                              <span>Order: {tutorial.order}</span>
                            </div>
                          </>
                        )}
                      </div>
                      
                      <div className="flex gap-2 ml-4">
                        {editingTutorial === tutorial.id ? (
                          <>
                            <Button 
                              size="sm" 
                              onClick={() => handleUpdateTutorial(tutorial.id)}
                            >
                              <Save className="h-4 w-4" />
                            </Button>
                            <Button 
                              size="sm" 
                              variant="ghost"
                              onClick={() => setEditingTutorial(null)}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </>
                        ) : (
                          <>
                            <Button size="sm" variant="ghost" onClick={() => startEditing(tutorial)}>
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button 
                              size="sm" 
                              variant="ghost" 
                              onClick={() => handleDeleteTutorial(tutorial.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    <div className="bg-black rounded overflow-hidden">
                      <video
                        controls
                        className="w-full h-48 object-cover"
                        poster={tutorial.thumbnail_url}
                      >
                        <source src={`${process.env.REACT_APP_BACKEND_URL}${tutorial.video_url}`} type="video/mp4" />
                      </video>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {tutorials.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <BookOpen className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-medium mb-2">No Tutorials Yet</h3>
                  <p>Create your first tutorial to help users learn the application</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Add Tutorial Form Modal */}
        {showAddForm && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Add New Tutorial</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateTutorial} className="space-y-4">
                  <div>
                    <Label htmlFor="title">Title</Label>
                    <Input
                      id="title"
                      value={formData.title}
                      onChange={(e) => setFormData({...formData, title: e.target.value})}
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      rows={3}
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label htmlFor="category">Category</Label>
                      <Input
                        id="category"
                        value={formData.category}
                        onChange={(e) => setFormData({...formData, category: e.target.value})}
                        placeholder="e.g., general, setup, features"
                      />
                    </div>
                    <div>
                      <Label htmlFor="order">Order</Label>
                      <Input
                        id="order"
                        type="number"
                        value={formData.order}
                        onChange={(e) => setFormData({...formData, order: parseInt(e.target.value)})}
                        min="0"
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="video">Video File (MP4)</Label>
                    <Input
                      id="video"
                      type="file"
                      accept="video/*"
                      onChange={(e) => setFormData({...formData, video: e.target.files[0]})}
                      required
                    />
                  </div>

                  <div className="flex gap-2 pt-4">
                    <Button type="submit" disabled={uploading} className="flex-1">
                      {uploading ? (
                        <>
                          <LoadingSpinner className="h-4 w-4 mr-2" />
                          Uploading...
                        </>
                      ) : (
                        <>
                          <Upload className="h-4 w-4 mr-2" />
                          Create Tutorial
                        </>
                      )}
                    </Button>
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={() => setShowAddForm(false)}
                      disabled={uploading}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default TutorialManagement;
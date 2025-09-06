import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Separator } from '../components/ui/separator';
import { 
  ArrowLeft, 
  Upload, 
  Settings, 
  Building, 
  Phone, 
  Globe, 
  MapPin, 
  Mail, 
  Palette, 
  MessageSquare,
  Lock,
  Save,
  Eye,
  EyeOff,
  UserPlus,
  Users,
  Edit,
  Trash2,
  X
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { practiceApi } from '../services/authApi';
import { useToast } from '../hooks/use-toast';

const PracticeSettingsPage = () => {
  const navigate = useNavigate();
  const { user, practice, logout } = useAuth();
  const { toast } = useToast();

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const [formData, setFormData] = useState({
    // Practice Info
    name: '',
    phone: '',
    website: '',
    street: '',
    city: '',
    state: '',
    zipCode: '',
    officeHours: '',
    emergencyContact: '',
    
    // Branding
    logo: '',
    primaryColor: '#2563eb',
    secondaryColor: '#1e40af',
    
    // Settings
    autoEmailReminders: true,
    customBranding: false,
    
    // Password Change
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [dentists, setDentists] = useState([]);
  const [newDentist, setNewDentist] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    licenseNumber: '',
    specialties: []
  });
  const [showAddDentist, setShowAddDentist] = useState(false);

  useEffect(() => {
    if (practice) {
      setFormData({
        name: practice.name || '',
        phone: practice.phone || '',
        website: practice.website || '',
        street: practice.address?.street || '',
        city: practice.address?.city || '',
        state: practice.address?.state || '',
        zipCode: practice.address?.zipCode || '',
        officeHours: practice.officeHours || '',
        emergencyContact: practice.emergencyContact || '',
        logo: practice.branding?.logo || '',
        primaryColor: practice.branding?.primaryColor || '#2563eb',
        secondaryColor: practice.branding?.secondaryColor || '#1e40af',
        autoEmailReminders: practice.settings?.autoEmailReminders !== false,
        customBranding: practice.settings?.customBranding === true,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      
      // Load dentists for this practice
      loadDentists();
    }
  }, [practice]);

  const loadDentists = async () => {
    try {
      const response = await practiceApi.getDentists();
      setDentists(response.data || []);
    } catch (error) {
      console.error('Failed to load dentists:', error);
      // If API doesn't exist yet, initialize with empty array
      setDentists([]);
    }
  };

  const handleAddDentist = async () => {
    if (!newDentist.firstName || !newDentist.lastName || !newDentist.email) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields (First Name, Last Name, Email)",
        variant: "destructive",
      });
      return;
    }

    setSaving(true);
    try {
      if (newDentist.id) {
        // Update existing dentist
        await practiceApi.updateDentist(newDentist.id, {
          firstName: newDentist.firstName,
          lastName: newDentist.lastName,
          email: newDentist.email,
          phone: newDentist.phone,
          licenseNumber: newDentist.licenseNumber,
          specialties: newDentist.specialties
        });
        toast({
          title: "Success",
          description: "Dentist updated successfully!",
        });
      } else {
        // Add new dentist
        await practiceApi.addDentist(newDentist);
        toast({
          title: "Success",
          description: "Dentist added successfully!",
        });
      }
      
      setNewDentist({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        licenseNumber: '',
        specialties: []
      });
      setShowAddDentist(false);
      loadDentists(); // Reload the list
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to save dentist",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleRemoveDentist = async (dentistId) => {
    if (!confirm('Are you sure you want to remove this dentist?')) return;

    try {
      await practiceApi.removeDentist(dentistId);
      toast({
        title: "Success",
        description: "Dentist removed successfully",
      });
      loadDentists();
    } catch (error) {
      toast({
        title: "Error", 
        description: "Failed to remove dentist",
        variant: "destructive",
      });
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleLogoUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      console.log('File selected:', file.name, file.size, file.type);
      
      if (file.size > 2 * 1024 * 1024) { // 2MB limit
        toast({
          title: "File Too Large",
          description: "Please select an image under 2MB",
          variant: "destructive",
        });
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        console.log('File loaded, data URL length:', e.target.result.length);
        setFormData({
          ...formData,
          logo: e.target.result
        });
        
        toast({
          title: "Logo Uploaded",
          description: "Logo uploaded successfully! Click 'Save Branding' to save changes.",
          variant: "default",
        });
      };
      
      reader.onerror = (e) => {
        console.error('FileReader error:', e);
        toast({
          title: "Upload Failed",
          description: "Failed to read the selected file.",
          variant: "destructive",
        });
      };
      
      reader.readAsDataURL(file);
    }
  };

  const handleSave = async (section) => {
    setSaving(true);
    
    try {
      let updateData = {};
      
      if (section === 'practice') {
        updateData = {
          name: formData.name,
          phone: formData.phone,
          website: formData.website,
          officeHours: formData.officeHours,
          emergencyContact: formData.emergencyContact,
          address: {
            street: formData.street,
            city: formData.city,
            state: formData.state,
            zipCode: formData.zipCode
          }
        };
      } else if (section === 'branding') {
        updateData = {
          branding: {
            logo: formData.logo,
            primaryColor: formData.primaryColor,
            secondaryColor: formData.secondaryColor,
            welcomeMessage: formData.welcomeMessage
          }
        };
        console.log('Sending branding update:', updateData);
      } else if (section === 'password') {
        if (!formData.newPassword) {
          toast({
            title: "Password Required",
            description: "Please enter a new password",
            variant: "destructive",
          });
          setSaving(false);
          return;
        }
        
        if (formData.newPassword !== formData.confirmPassword) {
          toast({
            title: "Password Mismatch",
            description: "Passwords do not match",
            variant: "destructive",
          });
          setSaving(false);
          return;
        }

        updateData = {
          newPassword: formData.newPassword
        };
      }

      const response = await practiceApi.updatePractice(updateData);
      
      if (response.success) {
        toast({
          title: "Settings Updated",
          description: "Your practice settings have been saved successfully",
          variant: "default",
        });
        
        if (section === 'password') {
          setFormData({
            ...formData,
            newPassword: '',
            confirmPassword: ''
          });
        }
      }
    } catch (error) {
      toast({
        title: "Update Failed",
        description: error.response?.data?.detail || "Failed to update settings",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/dashboard')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Dashboard</span>
              </Button>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="flex items-center space-x-2">
                <Settings className="h-5 w-5 text-gray-600" />
                <h1 className="text-xl font-semibold text-gray-900">Practice Settings</h1>
              </div>
            </div>
            <Button 
              variant="outline" 
              onClick={logout}
              className="text-gray-600 hover:text-gray-900"
            >
              Sign Out
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="space-y-8">
          
          {/* Practice Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Building className="h-5 w-5 text-blue-600" />
                <span>Practice Information</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Practice Name *</label>
                  <Input
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="Your Practice Name"
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Phone Number</label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="(555) 123-4567"
                    />
                  </div>
                </div>
                
                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium text-gray-700">Website</label>
                  <div className="relative">
                    <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      name="website"
                      value={formData.website}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="www.yourpractice.com"
                    />
                  </div>
                </div>
                
                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium text-gray-700">Office Hours</label>
                  <Input
                    name="officeHours"
                    value={formData.officeHours || ''}
                    onChange={handleInputChange}
                    placeholder="Mon-Fri: 8:00 AM - 5:00 PM, Sat: 9:00 AM - 2:00 PM"
                  />
                  <p className="text-xs text-gray-500">These will appear at the bottom of PDF care guides</p>
                </div>
                
                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium text-gray-700">Emergency Contact Number</label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      name="emergencyContact"
                      value={formData.emergencyContact || ''}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="(555) 123-4567"
                    />
                  </div>
                  <p className="text-xs text-gray-500">After-hours emergency contact for urgent situations</p>
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center space-x-2">
                  <MapPin className="h-4 w-4 text-blue-600" />
                  <span>Practice Address</span>
                </h3>
                
                <div className="grid grid-cols-1 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">Street Address</label>
                    <Input
                      name="street"
                      value={formData.street}
                      onChange={handleInputChange}
                      placeholder="123 Main Street"
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">City</label>
                      <Input
                        name="city"
                        value={formData.city}
                        onChange={handleInputChange}
                        placeholder="City"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">State</label>
                      <Input
                        name="state"
                        value={formData.state}
                        onChange={handleInputChange}
                        placeholder="State"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">ZIP Code</label>
                      <Input
                        name="zipCode"
                        value={formData.zipCode}
                        onChange={handleInputChange}
                        placeholder="12345"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <Button 
                  onClick={() => handleSave('practice')}
                  disabled={saving}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {saving ? 'Saving...' : 'Save Practice Info'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Branding */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Palette className="h-5 w-5 text-purple-600" />
                <span>Practice Branding</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              
              {/* Logo Upload */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Practice Logo</h3>
                <div className="flex items-center space-x-4">
                  {formData.logo && (
                    <div className="w-20 h-20 border border-gray-300 rounded-lg overflow-hidden">
                      <img 
                        src={formData.logo} 
                        alt="Practice Logo" 
                        className="w-full h-full object-contain"
                      />
                    </div>
                  )}
                  <div>
                    <input
                      type="file"
                      id="logo-upload"
                      accept="image/*"
                      onChange={handleLogoUpload}
                      className="hidden"
                    />
                    <Button 
                      variant="outline" 
                      type="button"
                      onClick={() => document.getElementById('logo-upload').click()}
                      className="cursor-pointer"
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      {formData.logo ? 'Change Logo' : 'Upload Logo'}
                    </Button>
                    <p className="text-sm text-gray-600 mt-1">PNG, JPG up to 2MB. This appears on all patient instructions.</p>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Brand Colors */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Brand Colors</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">Primary Color</label>
                    <div className="flex items-center space-x-3">
                      <input
                        type="color"
                        name="primaryColor"
                        value={formData.primaryColor}
                        onChange={handleInputChange}
                        className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                      />
                      <Input
                        name="primaryColor"
                        value={formData.primaryColor}
                        onChange={handleInputChange}
                        className="font-mono text-sm"
                        placeholder="#2563eb"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">Secondary Color</label>
                    <div className="flex items-center space-x-3">
                      <input
                        type="color"
                        name="secondaryColor"
                        value={formData.secondaryColor}
                        onChange={handleInputChange}
                        className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                      />
                      <Input
                        name="secondaryColor"
                        value={formData.secondaryColor}
                        onChange={handleInputChange}
                        className="font-mono text-sm"
                        placeholder="#1e40af"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Welcome Message */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center space-x-2">
                  <MessageSquare className="h-4 w-4 text-purple-600" />
                  <span>Welcome Message</span>
                </h3>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Custom message for patients</label>
                  <textarea
                    name="welcomeMessage"
                    value={formData.welcomeMessage}
                    onChange={handleInputChange}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Welcome to our practice's post-operative care portal"
                  />
                  <p className="text-sm text-gray-600">This message appears when patients access their post-op instructions.</p>
                </div>
              </div>

              <div className="flex justify-end">
                <Button 
                  onClick={() => handleSave('branding')}
                  disabled={saving}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {saving ? 'Saving...' : 'Save Branding'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Account Security */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Lock className="h-5 w-5 text-green-600" />
                <span>Account Security</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">New Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      name="newPassword"
                      type={showPassword ? "text" : "password"}
                      value={formData.newPassword}
                      onChange={handleInputChange}
                      className="pl-10 pr-10"
                      placeholder="Enter new password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Confirm Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      name="confirmPassword"
                      type={showPassword ? "text" : "password"}
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="Confirm new password"
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <Button 
                  onClick={() => handleSave('password')}
                  disabled={saving || !formData.newPassword}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {saving ? 'Updating...' : 'Update Password'}
                </Button>
              </div>
            </CardContent>
          </Card>



          {/* Quick Dentist Management - Simplified */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Users className="h-5 w-5 text-indigo-600" />
                  <span>Dentist Management</span>
                </div>
                <Button 
                  onClick={() => setShowAddDentist(true)}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  <UserPlus className="h-4 w-4 mr-2" />
                  Add Dentist
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              
              {/* Current Dentists List */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Practice Dentists</h3>
                
                {dentists.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg font-medium">No dentists added yet</p>
                    <p className="text-sm">Add dentists to your practice to assign procedures</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {dentists.map((dentist) => (
                      <div key={dentist.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center space-x-4">
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900">
                                Dr. {dentist.firstName} {dentist.lastName}
                              </h4>
                              <p className="text-sm text-gray-600">{dentist.email}</p>
                              {dentist.phone && (
                                <p className="text-sm text-gray-500">{dentist.phone}</p>
                              )}
                              {dentist.licenseNumber && (
                                <p className="text-sm text-gray-500">License: {dentist.licenseNumber}</p>
                              )}
                              {dentist.specialties && dentist.specialties.length > 0 && (
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {dentist.specialties.map((specialty, index) => (
                                    <span key={index} className="inline-block bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded">
                                      {specialty}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setNewDentist({
                                ...dentist,
                                specialties: dentist.specialties || []
                              });
                              setShowAddDentist(true);
                            }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleRemoveDentist(dentist.id)}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Add/Edit Dentist Form */}
              {showAddDentist && (
                <div className="border border-gray-200 rounded-lg p-6 bg-gray-50">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      {newDentist.id ? 'Edit Dentist' : 'Add New Dentist'}
                    </h3>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setShowAddDentist(false);
                        setNewDentist({
                          firstName: '',
                          lastName: '',
                          email: '',
                          phone: '',
                          licenseNumber: '',
                          specialties: []
                        });
                      }}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">First Name *</label>
                      <Input
                        value={newDentist.firstName}
                        onChange={(e) => setNewDentist({...newDentist, firstName: e.target.value})}
                        placeholder="Enter first name"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">Last Name *</label>
                      <Input
                        value={newDentist.lastName}
                        onChange={(e) => setNewDentist({...newDentist, lastName: e.target.value})}
                        placeholder="Enter last name"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">Email Address *</label>
                      <Input
                        type="email"
                        value={newDentist.email}
                        onChange={(e) => setNewDentist({...newDentist, email: e.target.value})}
                        placeholder="Enter email address"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">Phone Number</label>
                      <Input
                        value={newDentist.phone}
                        onChange={(e) => setNewDentist({...newDentist, phone: e.target.value})}
                        placeholder="(555) 123-4567"
                      />
                    </div>
                    
                    <div className="space-y-2 md:col-span-2">
                      <label className="text-sm font-medium text-gray-700">License Number</label>
                      <Input
                        value={newDentist.licenseNumber}
                        onChange={(e) => setNewDentist({...newDentist, licenseNumber: e.target.value})}
                        placeholder="Enter license number"
                      />
                    </div>
                    
                    <div className="space-y-2 md:col-span-2">
                      <label className="text-sm font-medium text-gray-700">Specialties</label>
                      <Input
                        value={newDentist.specialties?.join(', ')}
                        onChange={(e) => setNewDentist({
                          ...newDentist, 
                          specialties: e.target.value.split(',').map(s => s.trim()).filter(s => s)
                        })}
                        placeholder="Enter specialties separated by commas (e.g., Oral Surgery, Endodontics)"
                      />
                      <p className="text-sm text-gray-500">Separate multiple specialties with commas</p>
                    </div>
                  </div>
                  
                  <div className="flex justify-end space-x-3 mt-6">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setShowAddDentist(false);
                        setNewDentist({
                          firstName: '',
                          lastName: '',
                          email: '',
                          phone: '',
                          licenseNumber: '',
                          specialties: []
                        });
                      }}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleAddDentist}
                      disabled={saving}
                      className="bg-indigo-600 hover:bg-indigo-700"
                    >
                      <Save className="h-4 w-4 mr-2" />
                      {saving ? 'Saving...' : (newDentist.id ? 'Update Dentist' : 'Add Dentist')}
                    </Button>
                  </div>
                </div>
              )}

            </CardContent>
          </Card>

          {/* Billing & Support */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Mail className="h-5 w-5 text-blue-600" />
                <span>Billing & Support</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  <strong>Billing Questions:</strong> For subscription changes, payment issues, or cancellations, please email{' '}
                  <a href="mailto:admin@theoncallbot.com" className="text-blue-600 underline">
                    admin@theoncallbot.com
                  </a>
                </AlertDescription>
              </Alert>
              
              <div className="mt-4 pt-4 border-t">
                <p className="text-sm text-gray-600">
                  <strong>Current Subscription:</strong> DRB Post Operative Library - $49/month
                  <br />
                  <strong>Status:</strong> {practice?.subscription?.status === 'active' ? '✅ Active' : '⚠️ Inactive'}
                  <br />
                  <strong>Need Help?</strong> Contact support@theoncallbot.com
                </p>
              </div>
            </CardContent>
          </Card>

          {/* SIMPLE DENTIST MANAGEMENT - DIRECT IMPLEMENTATION */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-indigo-600" />
                <span>Dentist Management</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                <h3 className="font-medium text-indigo-900 mb-2">Manage Practice Dentists</h3>
                <p className="text-indigo-800 text-sm mb-4">Add, edit, and manage dentists for procedure assignments in your practice.</p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-indigo-900">First Name</label>
                    <Input 
                      placeholder="Enter first name"
                      className="border-indigo-300 focus:border-indigo-500"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-indigo-900">Last Name</label>
                    <Input 
                      placeholder="Enter last name" 
                      className="border-indigo-300 focus:border-indigo-500"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-indigo-900">Email Address</label>
                    <Input 
                      type="email"
                      placeholder="Enter email" 
                      className="border-indigo-300 focus:border-indigo-500"
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-indigo-900">Phone Number</label>
                    <Input 
                      placeholder="(555) 123-4567" 
                      className="border-indigo-300 focus:border-indigo-500"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-indigo-900">License Number</label>
                    <Input 
                      placeholder="Enter license number" 
                      className="border-indigo-300 focus:border-indigo-500"
                    />
                  </div>
                </div>
                
                <div className="space-y-2 mt-4">
                  <label className="text-sm font-medium text-indigo-900">Specialties</label>
                  <Input 
                    placeholder="General Dentistry, Oral Surgery (comma-separated)" 
                    className="border-indigo-300 focus:border-indigo-500"
                  />
                </div>
                
                <div className="flex justify-end space-x-3 mt-6">
                  <Button variant="outline" className="border-indigo-300 text-indigo-700 hover:bg-indigo-50">
                    Clear Form
                  </Button>
                  <Button className="bg-indigo-600 hover:bg-indigo-700 text-white">
                    <UserPlus className="h-4 w-4 mr-2" />
                    Add Dentist
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
};

export default PracticeSettingsPage;
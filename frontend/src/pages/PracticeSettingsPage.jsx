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
  EyeOff
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
    
    // Branding
    logo: '',
    primaryColor: '#2563eb',
    secondaryColor: '#1e40af',
    welcomeMessage: '',
    
    // Account
    newPassword: '',
    confirmPassword: ''
  });

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
        logo: practice.branding?.logo || '',
        primaryColor: practice.branding?.primaryColor || '#2563eb',
        secondaryColor: practice.branding?.secondaryColor || '#1e40af',
        welcomeMessage: practice.branding?.welcomeMessage || `Welcome to ${practice.name || 'our practice'}'s post-operative care portal`,
        newPassword: '',
        confirmPassword: ''
      });
    }
  }, [practice]);

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
                    <label htmlFor="logo-upload">
                      <Button variant="outline" className="cursor-pointer" type="button">
                        <Upload className="h-4 w-4 mr-2" />
                        {formData.logo ? 'Change Logo' : 'Upload Logo'}
                      </Button>
                    </label>
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

        </div>
      </div>
    </div>
  );
};

export default PracticeSettingsPage;
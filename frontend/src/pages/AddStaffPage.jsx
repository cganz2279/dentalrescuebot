import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Alert, AlertDescription } from '../components/ui/alert';
import { ArrowLeft, UserPlus, Mail, User, Key, Copy } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const AddStaffPage = () => {
  const navigate = useNavigate();
  const { user, practice } = useAuth();
  const { toast } = useToast();
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [tempPassword, setTempPassword] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validate required fields
    if (!formData.firstName || !formData.lastName || !formData.email) {
      setError('Please fill in all required fields');
      setLoading(false);
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('dentalToken');
      const response = await fetch(`${import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL}/api/practice/add-staff`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        setTempPassword(data.temporaryPassword);
        setShowSuccess(true);
        
        toast({
          title: "Staff Member Added Successfully!",
          description: `${formData.firstName} ${formData.lastName} has been added to your practice.`,
          variant: "default",
        });
        
        // Reset form
        setFormData({ firstName: '', lastName: '', email: '' });
      } else {
        setError(data.detail || data.message || 'Failed to add staff member');
      }
    } catch (err) {
      setError('Failed to add staff member. Please try again.');
      console.error('Add staff error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const copyPassword = () => {
    navigator.clipboard.writeText(tempPassword);
    toast({
      title: "Password Copied!",
      description: "Temporary password has been copied to clipboard.",
      variant: "default",
    });
  };

  const handleAddAnother = () => {
    setShowSuccess(false);
    setTempPassword('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center space-x-4">
            <Button
              onClick={() => navigate('/')}
              variant="outline"
              size="sm"
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Dashboard</span>
            </Button>
            <div className="flex items-center space-x-2">
              <img 
                src="https://customer-assets.emergentagent.com/job_dental-healing/artifacts/j7ayzg7r_DentalRescueBotWithRoundedText.png"
                alt="DentalRescueBot Logo"
                className="h-8 w-auto"
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
              <h1 className="text-2xl font-bold text-gray-900">Add Staff Member</h1>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 py-8">
        {!showSuccess ? (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-xl">
                <UserPlus className="h-6 w-6 mr-2 text-blue-600" />
                Add Staff Member to {practice?.name}
              </CardTitle>
              <p className="text-gray-600">
                Add another dentist or staff member who can access your practice dashboard
              </p>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertDescription className="text-red-800">
                      {error}
                    </AlertDescription>
                  </Alert>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label htmlFor="firstName" className="text-sm font-medium text-gray-700">
                      First Name *
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        id="firstName"
                        name="firstName"
                        type="text"
                        required
                        value={formData.firstName}
                        onChange={handleInputChange}
                        className="pl-10"
                        placeholder="First name"
                        disabled={loading}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="lastName" className="text-sm font-medium text-gray-700">
                      Last Name *
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        id="lastName"
                        name="lastName"
                        type="text"
                        required
                        value={formData.lastName}
                        onChange={handleInputChange}
                        className="pl-10"
                        placeholder="Last name"
                        disabled={loading}
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium text-gray-700">
                    Email Address *
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      required
                      value={formData.email}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="staff@example.com"
                      disabled={loading}
                    />
                  </div>
                  <p className="text-xs text-gray-500">
                    This staff member will use this email to log in to the practice dashboard
                  </p>
                </div>

                <div className="flex justify-end space-x-4 pt-6">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => navigate('/')}
                    disabled={loading}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <LoadingSpinner size="sm" className="mr-2" />
                        Adding Staff Member...
                      </>
                    ) : (
                      <>
                        <UserPlus className="h-4 w-4 mr-2" />
                        Add Staff Member
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        ) : (
          <Card className="border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="flex items-center text-xl text-green-900">
                <UserPlus className="h-6 w-6 mr-2 text-green-600" />
                Staff Member Added Successfully!
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="bg-white p-4 border border-green-200 rounded-lg">
                  <h3 className="font-semibold text-green-900 mb-2">Login Information</h3>
                  <div className="space-y-2">
                    <div>
                      <span className="text-sm font-medium text-gray-700">Email: </span>
                      <span className="text-sm text-gray-900">{formData.email}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-700">Temporary Password: </span>
                      <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono">{tempPassword}</code>
                      <Button
                        onClick={copyPassword}
                        size="sm"
                        variant="outline"
                        className="h-8 w-8 p-0"
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>

                <div className="bg-amber-50 border border-amber-200 p-4 rounded-lg">
                  <h4 className="font-semibold text-amber-900 mb-2">Important Instructions:</h4>
                  <ul className="text-sm text-amber-800 space-y-1">
                    <li>• Share these login credentials with the staff member</li>
                    <li>• They should log in at: www.theoncallbot.com/practice-notes</li>
                    <li>• They will be prompted to change their password on first login</li>
                    <li>• This temporary password will expire after first use</li>
                  </ul>
                </div>

                <div className="flex justify-end space-x-4">
                  <Button
                    onClick={handleAddAnother}
                    variant="outline"
                  >
                    Add Another Staff Member
                  </Button>
                  <Button
                    onClick={() => navigate('/')}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    Return to Dashboard
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Info Card */}
        <Card className="mt-6 border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-3">
              <div className="bg-blue-100 rounded-full p-2">
                <UserPlus className="h-4 w-4 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-blue-900 mb-2">Staff Access Permissions</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Full access to practice dashboard and all features</li>
                  <li>• Can add patients, assign procedures, and manage practice data</li>
                  <li>• Cannot change practice settings or add other staff members</li>
                  <li>• Each staff member has their own login credentials</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AddStaffPage;
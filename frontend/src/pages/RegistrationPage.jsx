import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Building, Mail, Phone, Globe, User, Lock, MapPin, Eye, EyeOff } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const RegistrationPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();

  // Get data from URL parameters (from SamCart)
  const paymentVerified = searchParams.get('payment_verified');
  const customerEmail = searchParams.get('email');
  const customerFirstName = searchParams.get('first_name');
  const customerLastName = searchParams.get('last_name');

  const [formData, setFormData] = useState({
    // Practice information
    practiceName: '',
    email: customerEmail || '',
    phone: '',
    website: '',
    
    // Admin user information (from SamCart)
    adminFirstName: customerFirstName || '',
    adminLastName: customerLastName || '',
    adminPassword: '',
    confirmPassword: '',
    
    // Address information
    street: '',
    city: '',
    state: '',
    zipCode: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Check if payment was verified
  useEffect(() => {
    if (paymentVerified !== 'true') {
      setError('Payment verification required. Please complete payment first.');
    }
  }, [paymentVerified]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validate required fields
    if (!formData.practiceName || !formData.email || !formData.adminFirstName || 
        !formData.adminLastName || !formData.adminPassword) {
      setError('Please fill in all required fields');
      setLoading(false);
      return;
    }

    // Validate passwords match
    if (formData.adminPassword !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    // Validate password strength
    if (formData.adminPassword.length < 6) {
      setError('Password must be at least 6 characters long');
      setLoading(false);
      return;
    }

    try {
      console.log('Submitting registration data:', formData);
      
      // Get backend URL with fallback
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 
                        'https://careflow-dental.preview.emergentagent.com';
      
      console.log('Using backend URL:', backendUrl);
      
      const response = await fetch(`${backendUrl}/api/auth/register-practice-samcart`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          paymentVerified: true,
          paymentSource: 'samcart'
        })
      });

      const data = await response.json();
      console.log('Registration response:', response.status, data);

      if (response.ok && data.success) {
        toast({
          title: "Registration Successful!",
          description: `Welcome to DRB Post Operative Library, ${formData.adminFirstName}! Please log in to access your account.`,
          variant: "default",
        });

        // Redirect to main page (which will show login form)
        navigate('/?registered=true');
      } else {
        setError(data.detail || data.message || 'Registration failed');
      }
    } catch (err) {
      setError('Registration failed. Please try again.');
      console.error('Registration error:', err);
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

  if (paymentVerified !== 'true') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <Alert className="border-red-200 bg-red-50">
              <AlertDescription className="text-red-800">
                Payment verification required. Please complete your payment first.
              </AlertDescription>
            </Alert>
            <div className="mt-4 text-center">
              <Button 
                onClick={() => window.location.href = 'https://theoncallbot.com/post-op-care-library/'}
                variant="outline"
              >
                Return to Payment Page
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <img 
              src="https://customer-assets.emergentagent.com/job_dental-healing/artifacts/j7ayzg7r_DentalRescueBotWithRoundedText.png"
              alt="DentalRescueBot Logo"
              className="h-16 w-auto"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">
            Complete Your Registration
          </CardTitle>
          <p className="text-gray-600 mt-2">
            🎉 Payment Successful! Setup your DRB Post Operative Library account
          </p>
          {customerEmail && (
            <p className="text-sm text-green-600 mt-1">
              ✓ Payment verified for {customerEmail}
            </p>
          )}
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

            {/* Practice Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                <Building className="h-5 w-5 mr-2 text-blue-600" />
                Practice Information
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="practiceName" className="text-sm font-medium text-gray-700">
                    Practice Name *
                  </label>
                  <Input
                    id="practiceName"
                    name="practiceName"
                    type="text"
                    required
                    value={formData.practiceName}
                    onChange={handleInputChange}
                    placeholder="Your Dental Practice"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium text-gray-700">
                    Practice Email *
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
                      placeholder="practice@example.com"
                      disabled={!!customerEmail}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label htmlFor="phone" className="text-sm font-medium text-gray-700">
                    Phone Number
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="phone"
                      name="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="(555) 123-4567"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label htmlFor="website" className="text-sm font-medium text-gray-700">
                    Website
                  </label>
                  <div className="relative">
                    <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="website"
                      name="website"
                      type="text"
                      value={formData.website}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="yourpractice.com"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Address Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                <MapPin className="h-5 w-5 mr-2 text-blue-600" />
                Practice Address
              </h3>
              
              <div className="space-y-2">
                <label htmlFor="street" className="text-sm font-medium text-gray-700">
                  Street Address
                </label>
                <Input
                  id="street"
                  name="street"
                  type="text"
                  value={formData.street}
                  onChange={handleInputChange}
                  placeholder="123 Main Street"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label htmlFor="city" className="text-sm font-medium text-gray-700">
                    City
                  </label>
                  <Input
                    id="city"
                    name="city"
                    type="text"
                    value={formData.city}
                    onChange={handleInputChange}
                    placeholder="City"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="state" className="text-sm font-medium text-gray-700">
                    State
                  </label>
                  <Input
                    id="state"
                    name="state"
                    type="text"
                    value={formData.state}
                    onChange={handleInputChange}
                    placeholder="State"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="zipCode" className="text-sm font-medium text-gray-700">
                    ZIP Code
                  </label>
                  <Input
                    id="zipCode"
                    name="zipCode"
                    type="text"
                    value={formData.zipCode}
                    onChange={handleInputChange}
                    placeholder="12345"
                  />
                </div>
              </div>
            </div>

            {/* Admin User Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                <User className="h-5 w-5 mr-2 text-blue-600" />
                Administrator Account
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="adminFirstName" className="text-sm font-medium text-gray-700">
                    First Name *
                  </label>
                  <Input
                    id="adminFirstName"
                    name="adminFirstName"
                    type="text"
                    required
                    value={formData.adminFirstName}
                    onChange={handleInputChange}
                    placeholder="John"
                    disabled={!!customerFirstName}
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="adminLastName" className="text-sm font-medium text-gray-700">
                    Last Name *
                  </label>
                  <Input
                    id="adminLastName"
                    name="adminLastName"
                    type="text"
                    required
                    value={formData.adminLastName}
                    onChange={handleInputChange}
                    placeholder="Smith"
                    disabled={!!customerLastName}
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="adminPassword" className="text-sm font-medium text-gray-700">
                    Create Password *
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="adminPassword"
                      name="adminPassword"
                      type={showPassword ? "text" : "password"}
                      required
                      value={formData.adminPassword}
                      onChange={handleInputChange}
                      className="pl-10 pr-10"
                      placeholder="At least 6 characters"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
                    Confirm Password *
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      required
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      className="pl-10 pr-10"
                      placeholder="Confirm password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3"
              disabled={loading}
            >
              {loading ? 'Creating Account...' : 'Complete Registration & Access Library'}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              Your payment has been processed successfully.
              <br />
              Complete registration to access your DRB Post Operative Library.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RegistrationPage;
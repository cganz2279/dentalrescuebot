import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Eye, EyeOff, Mail, Lock } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { authApi } from '../services/authApi';
import { useToast } from '../hooks/use-toast';

const LoginForm = ({ onSwitchToRegister }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [showForgotUsername, setShowForgotUsername] = useState(false);

  const { login } = useAuth();
  const { toast } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Make API call to login
      const response = await authApi.login(formData.email, formData.password);
      
      if (response.success) {
        // Pass the user data, token, and practice to AuthContext
        await login(response.user, response.token, response.practice);
        
        toast({
          title: "Login Successful",
          description: `Welcome back, ${response.user.firstName}!`,
          variant: "default",
        });
      } else {
        setError(response.error || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError(
        error.response?.data?.detail || 
        'Login failed. Please check your email and password.'
      );
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

  const ForgotPasswordModal = () => {
    const [forgotEmail, setForgotEmail] = useState('');
    const [recoveryMethod, setRecoveryMethod] = useState('email');
    const [forgotLoading, setForgotLoading] = useState(false);
    const [forgotMessage, setForgotMessage] = useState('');

    const handleForgotPassword = async (e) => {
      e.preventDefault();
      setForgotLoading(true);
      setForgotMessage('');

      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'https://dentist-dashboard-2.preview.emergentagent.com'}/api/auth/forgot-password`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: forgotEmail,
            recovery_method: recoveryMethod
          }),
        });

        const data = await response.json();

        if (response.ok) {
          setForgotMessage(data.message);
          toast({
            title: "Password Reset Sent",
            description: data.message,
            variant: "default",
          });
        } else {
          setForgotMessage(data.detail || 'Password reset request failed');
        }
      } catch (error) {
        setForgotMessage('Network error. Please try again.');
      } finally {
        setForgotLoading(false);
      }
    };

    if (!showForgotPassword) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-md w-full p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">Reset Password</h2>
            <button
              onClick={() => {
                setShowForgotPassword(false);
                setForgotEmail('');
                setForgotMessage('');
              }}
              className="text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>

          <form onSubmit={handleForgotPassword} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <Input
                type="email"
                value={forgotEmail}
                onChange={(e) => setForgotEmail(e.target.value)}
                placeholder="Enter your email address"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Recovery Method
              </label>
              <select
                value={recoveryMethod}
                onChange={(e) => setRecoveryMethod(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="email">Email Only</option>
                <option value="sms">SMS Only</option>
                <option value="both">Both Email and SMS</option>
              </select>
            </div>

            {forgotMessage && (
              <div className="p-3 rounded-md bg-blue-50 border border-blue-200">
                <p className="text-blue-800 text-sm">{forgotMessage}</p>
              </div>
            )}

            <Button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700"
              disabled={forgotLoading}
            >
              {forgotLoading ? 'Sending...' : 'Send Reset Instructions'}
            </Button>
          </form>
        </div>
      </div>
    );
  };

  const ForgotUsernameModal = () => {
    const [practiceName, setPracticeName] = useState('');
    const [phone, setPhone] = useState('');
    const [adminPassword, setAdminPassword] = useState('');
    const [usernameLoading, setUsernameLoading] = useState(false);
    const [usernameMessage, setUsernameMessage] = useState('');

    const handleForgotUsername = async (e) => {
      e.preventDefault();
      setUsernameLoading(true);
      setUsernameMessage('');

      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'https://dentist-dashboard-2.preview.emergentagent.com'}/api/auth/forgot-username`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            practice_name: practiceName,
            phone: phone,
            adminPassword: adminPassword
          }),
        });

        const data = await response.json();

        if (response.ok) {
          setUsernameMessage(data.message);
          toast({
            title: "Username Recovery",
            description: data.message,
            variant: "default",
          });
        } else {
          setUsernameMessage(data.detail || 'Username recovery failed');
        }
      } catch (error) {
        setUsernameMessage('Network error. Please try again.');
      } finally {
        setUsernameLoading(false);
      }
    };

    if (!showForgotUsername) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-md w-full p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">Recover Username</h2>
            <button
              onClick={() => {
                setShowForgotUsername(false);
                setPracticeName('');
                setPhone('');
                setAdminPassword('');
                setUsernameMessage('');
              }}
              className="text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>

          <form onSubmit={handleForgotUsername} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Practice Name
              </label>
              <Input
                type="text"
                value={practiceName}
                onChange={(e) => setPracticeName(e.target.value)}
                placeholder="Enter your practice name"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number (optional)
              </label>
              <Input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="Enter practice phone number"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Admin Password
              </label>
              <Input
                type="password"
                value={adminPassword}
                onChange={(e) => setAdminPassword(e.target.value)}
                placeholder="Enter admin password for verification"
                required
              />
            </div>

            {usernameMessage && (
              <div className="p-3 rounded-md bg-blue-50 border border-blue-200">
                <p className="text-blue-800 text-sm">{usernameMessage}</p>
              </div>
            )}

            <Button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700"
              disabled={usernameLoading}
            >
              {usernameLoading ? 'Recovering...' : 'Recover Username'}
            </Button>
          </form>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
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
            Welcome
          </CardTitle>
          <p className="text-gray-600 mt-2">
            Sign in to your dental practice account
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert className="border-red-200 bg-red-50">
                <AlertDescription className="text-red-800">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-gray-700">
                Email Address
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
                  placeholder="Enter your email"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  className="pl-10 pr-10"
                  placeholder="Enter your password"
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

            <Button 
              type="submit" 
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              disabled={loading}
            >
              {loading ? 'Signing In...' : 'Sign In'}
            </Button>
          </form>

          {/* Forgot Password and Forgot Username Links */}
          <div className="mt-4 text-center space-y-2">
            <p className="text-sm">
              <button 
                type="button"
                onClick={() => setShowForgotPassword(true)}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Forgot Password?
              </button>
              {' | '}
              <button 
                type="button"
                onClick={() => setShowForgotUsername(true)}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Forgot Username?
              </button>
            </p>
          </div>

          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">
              Don't have a practice account?{' '}
              <button
                onClick={onSwitchToRegister}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Register Your Practice
              </button>
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Password Recovery Modals */}
      <ForgotPasswordModal />
      <ForgotUsernameModal />
    </div>
  );
};

export default LoginForm;
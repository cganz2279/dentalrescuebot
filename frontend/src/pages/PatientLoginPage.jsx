import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Eye, EyeOff, Mail, Lock, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { authApi, patientsApi } from '../services/authApi';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../hooks/use-toast';

const PatientLoginPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const { toast } = useToast();

  // Check if this is first-time setup
  const setupMode = searchParams.get('setup') === 'true';
  const invitationEmail = searchParams.get('email');

  const [mode, setMode] = useState(setupMode ? 'setup' : 'login');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [loginData, setLoginData] = useState({
    email: invitationEmail || '',
    password: ''
  });

  const [setupData, setSetupData] = useState({
    email: invitationEmail || '',
    password: '',
    confirmPassword: ''
  });

  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authApi.login(loginData.email, loginData.password);
      
      if (response.success && response.user.role === 'patient') {
        login(response.user, response.token, response.practice);
        toast({
          title: "Welcome back!",
          description: "Successfully logged into your patient portal.",
        });
        navigate('/patient/dashboard');
      } else if (response.user.role !== 'patient') {
        setError('This is the patient portal. Please use the practice login for staff access.');
      } else {
        setError('Login failed. Please check your credentials.');
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

  const handleSetup = async (e) => {
    e.preventDefault();
    setError('');

    // Validate password
    if (setupData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    if (setupData.password !== setupData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await patientsApi.setupPassword({
        email: setupData.email,
        password: setupData.password
      });

      toast({
        title: "Password Set Successfully!",
        description: "You can now log in with your new password.",
      });

      // Switch to login mode
      setMode('login');
      setLoginData({
        email: setupData.email,
        password: ''
      });
      setSetupData({
        email: setupData.email,
        password: '',
        confirmPassword: ''
      });

    } catch (error) {
      console.error('Setup error:', error);
      setError(
        error.response?.data?.detail || 
        'Failed to set up password. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
            <User className="h-6 w-6 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold">
            {mode === 'setup' ? 'Set Up Your Password' : 'Patient Portal Login'}
          </CardTitle>
          <p className="text-gray-600">
            {mode === 'setup' 
              ? 'Create a password to access your post-operative instructions'
              : 'Access your personalized post-operative care instructions'
            }
          </p>
        </CardHeader>

        <CardContent>
          {error && (
            <Alert className="mb-4 border-red-200 bg-red-50">
              <AlertDescription className="text-red-700">
                {error}
              </AlertDescription>
            </Alert>
          )}

          {mode === 'setup' ? (
            <form onSubmit={handleSetup} className="space-y-4">
              <div>
                <Label htmlFor="setup-email">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="setup-email"
                    type="email"
                    value={setupData.email}
                    onChange={(e) => setSetupData(prev => ({ ...prev, email: e.target.value }))}
                    className="pl-10"
                    placeholder="your.email@example.com"
                    required
                    disabled={!!invitationEmail}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="setup-password">Create Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="setup-password"
                    type={showPassword ? "text" : "password"}
                    value={setupData.password}
                    onChange={(e) => setSetupData(prev => ({ ...prev, password: e.target.value }))}
                    className="pl-10 pr-10"
                    placeholder="Create a secure password"
                    required
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 transform -translate-y-1/2"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Password must be at least 6 characters long
                </p>
              </div>

              <div>
                <Label htmlFor="confirm-password">Confirm Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="confirm-password"
                    type={showConfirmPassword ? "text" : "password"}
                    value={setupData.confirmPassword}
                    onChange={(e) => setSetupData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    className="pl-10 pr-10"
                    placeholder="Confirm your password"
                    required
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 transform -translate-y-1/2"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    Setting up...
                  </>
                ) : (
                  'Set Up Password'
                )}
              </Button>
            </form>
          ) : (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <Label htmlFor="email">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    value={loginData.email}
                    onChange={(e) => setLoginData(prev => ({ ...prev, email: e.target.value }))}
                    className="pl-10"
                    placeholder="your.email@example.com"
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={loginData.password}
                    onChange={(e) => setLoginData(prev => ({ ...prev, password: e.target.value }))}
                    className="pl-10 pr-10"
                    placeholder="Enter your password"
                    required
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 transform -translate-y-1/2"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>
          )}

          {mode === 'login' && !setupMode && (
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                First time logging in?{' '}
                <button
                  type="button"
                  onClick={() => setMode('setup')}
                  className="text-blue-600 hover:text-blue-700 font-medium"
                >
                  Set up your password
                </button>
              </p>
            </div>
          )}

          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              For practice staff login,{' '}
              <button
                type="button"
                onClick={() => navigate('/')}
                className="text-blue-600 hover:text-blue-700"
              >
                click here
              </button>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PatientLoginPage;
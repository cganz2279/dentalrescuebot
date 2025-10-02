import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Eye, EyeOff, Lock, CheckCircle, XCircle } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const PasswordReset = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const token = searchParams.get('token');

  const [formData, setFormData] = useState({
    newPassword: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [userInfo, setUserInfo] = useState(null);

  // Validate token on component mount
  useEffect(() => {
    if (!token) {
      setError('Invalid or missing reset token');
      setValidating(false);
      return;
    }

    validateToken();
  }, [token]);

  const validateToken = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/auth/validate-reset-token/${token}`,
        {
          method: 'GET',
        }
      );

      const data = await response.json();

      if (response.ok && data.valid) {
        setTokenValid(true);
        setUserInfo(data.user);
      } else {
        setError(data.detail || 'Invalid or expired reset token');
      }
    } catch (error) {
      setError('Failed to validate reset token');
    } finally {
      setValidating(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate passwords
    if (formData.newPassword.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    if (formData.newPassword !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/auth/reset-password`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            reset_token: token,
            new_password: formData.newPassword,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
        toast({
          title: "Password Reset Successful",
          description: "Your password has been updated successfully.",
          variant: "default",
        });
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/');
        }, 3000);
      } else {
        setError(data.detail || 'Password reset failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
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

  // Loading state while validating token
  if (validating) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Validating reset token...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Invalid token state
  if (!tokenValid) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <XCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
            <CardTitle className="text-2xl font-bold text-red-600">
              Invalid Reset Link
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <Alert className="border-red-200 bg-red-50 mb-4">
              <AlertDescription className="text-red-800">
                {error}
              </AlertDescription>
            </Alert>
            <p className="text-gray-600 mb-4">
              This password reset link is invalid or has expired. Please request a new one.
            </p>
            <Button 
              onClick={() => navigate('/')}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              Back to Login
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Success state
  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
            <CardTitle className="text-2xl font-bold text-green-600">
              Password Reset Successful!
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-gray-600 mb-4">
              Your password has been updated successfully. You will be redirected to the login page in a few seconds.
            </p>
            <Button 
              onClick={() => navigate('/')}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              Continue to Login
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Password reset form
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
            <Lock className="h-6 w-6 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">
            Reset Password
          </CardTitle>
          <p className="text-gray-600 mt-2">
            {userInfo ? `Welcome ${userInfo.firstName} ${userInfo.lastName}` : 'Enter your new password'}
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
              <label htmlFor="newPassword" className="text-sm font-medium text-gray-700">
                New Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  id="newPassword"
                  name="newPassword"
                  type={showPassword ? 'text' : 'password'}
                  required
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
              <p className="text-xs text-gray-500">
                Password must be at least 8 characters long
              </p>
            </div>

            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="pl-10 pr-10"
                  placeholder="Confirm new password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              disabled={loading}
            >
              {loading ? 'Updating Password...' : 'Update Password'}
            </Button>
          </form>

          <div className="mt-4 text-center">
            <button
              onClick={() => navigate('/')}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Back to Login
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PasswordReset;
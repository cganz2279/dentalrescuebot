import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import AdminDashboard from './AdminDashboard';
import LoginForm from './LoginForm';
import LoadingSpinner from './LoadingSpinner';

const AdminRoute = () => {
  const { user, isAuthenticated, loading } = useAuth();

  // Debug logging
  console.log('AdminRoute Debug:', {
    user,
    isAuthenticated: isAuthenticated(),
    loading,
    userRole: user?.role,
    localStorage: {
      token: localStorage.getItem('dentalToken'),
      user: localStorage.getItem('dentalUser')
    }
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
        <div className="absolute bottom-10 text-sm text-gray-500">Loading admin route...</div>
      </div>
    );
  }

  if (!isAuthenticated()) {
    return (
      <div>
        <div className="bg-yellow-100 p-4 mb-4">
          <h3>Debug: Not Authenticated</h3>
          <p>User: {JSON.stringify(user)}</p>
          <p>Token: {localStorage.getItem('dentalToken') ? 'Present' : 'Missing'}</p>
        </div>
        <LoginForm />
      </div>
    );
  }

  // Check if user has admin privileges
  if (user?.role === 'super_admin' || user?.role === 'admin') {
    return (
      <div>
        <div className="bg-green-100 p-4 mb-4">
          <h3>Debug: Admin Access Granted</h3>
          <p>User Role: {user?.role}</p>
          <p>User: {JSON.stringify(user)}</p>
        </div>
        <AdminDashboard />
      </div>
    );
  }

  // If authenticated but not admin
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md">
        <h2 className="text-xl font-bold text-red-600 mb-4">Access Denied</h2>
        <p>Admin privileges required.</p>
        <div className="bg-gray-100 p-4 mt-4 rounded">
          <h4>Debug Info:</h4>
          <p><strong>User Role:</strong> {user?.role || 'No role'}</p>
          <p><strong>User Data:</strong></p>
          <pre className="text-xs">{JSON.stringify(user, null, 2)}</pre>
        </div>
        <button 
          onClick={() => window.location.href = '/'}
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded"
        >
          Go to Main Dashboard
        </button>
      </div>
    </div>
  );
};

export default AdminRoute;
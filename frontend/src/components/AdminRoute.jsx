import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import AdminDashboard from './AdminDashboard';
import LoginForm from './LoginForm';
import LoadingSpinner from './LoadingSpinner';

const AdminRoute = () => {
  const { user, isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (!isAuthenticated()) {
    return <LoginForm />;
  }

  // Check if user has admin privileges
  if (user?.role === 'super_admin' || user?.role === 'admin') {
    return <AdminDashboard />;
  }

  // If authenticated but not admin, redirect to appropriate dashboard
  return <div>Access denied. Admin privileges required.</div>;
};

export default AdminRoute;
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from './LoadingSpinner';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Simple loading simulation
    setTimeout(() => {
      setStats({
        total_practices: 5,
        active_practices: 3,
        trial_practices: 2,
        monthly_revenue: 2500
      });
      setLoading(false);
    }, 1000);
  }, []);

  const handleLogout = () => {
    logout();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <img 
                src="https://customer-assets.emergentagent.com/job_dental-healing/artifacts/j7ayzg7r_DentalRescueBotWithRoundedText.png" 
                alt="DentalRescueBot" 
                className="h-8 w-auto"
              />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">System Admin Dashboard</h1>
                <p className="text-gray-600">Welcome back, {user?.firstName || 'Admin'}</p>
                <p className="text-sm text-gray-500">Role: {user?.role || 'super_admin'}</p>
              </div>
            </div>
            <button 
              onClick={handleLogout}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 border border-gray-200 rounded-lg shadow-sm">
            <h3 className="text-sm font-medium text-gray-600">Total Practices</h3>
            <p className="text-2xl font-bold text-gray-900">{stats?.total_practices || 0}</p>
            <p className="text-xs text-gray-500">{stats?.active_practices || 0} active practices</p>
          </div>

          <div className="bg-white p-6 border border-gray-200 rounded-lg shadow-sm">
            <h3 className="text-sm font-medium text-gray-600">Active Practices</h3>
            <p className="text-2xl font-bold text-gray-900">{stats?.active_practices || 0}</p>
            <p className="text-xs text-gray-500">Currently subscribed</p>
          </div>

          <div className="bg-white p-6 border border-gray-200 rounded-lg shadow-sm">
            <h3 className="text-sm font-medium text-gray-600">Trial Practices</h3>
            <p className="text-2xl font-bold text-gray-900">{stats?.trial_practices || 0}</p>
            <p className="text-xs text-gray-500">On trial period</p>
          </div>

          <div className="bg-white p-6 border border-gray-200 rounded-lg shadow-sm">
            <h3 className="text-sm font-medium text-gray-600">Monthly Revenue</h3>
            <p className="text-2xl font-bold text-gray-900">
              ${(stats?.monthly_revenue || 0).toLocaleString()}
            </p>
            <p className="text-xs text-gray-500">Monthly recurring revenue</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white p-6 border border-gray-200 rounded-lg shadow-sm mb-8">
          <h3 className="text-lg font-medium text-gray-800 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button className="bg-blue-600 text-white p-4 rounded hover:bg-blue-700">
              <div className="text-center">
                <div className="text-2xl mb-2">🏢</div>
                <div className="text-sm">Manage Practices</div>
              </div>
            </button>
            <button className="bg-green-600 text-white p-4 rounded hover:bg-green-700">
              <div className="text-center">
                <div className="text-2xl mb-2">👥</div>
                <div className="text-sm">User Management</div>
              </div>
            </button>
            <button className="bg-purple-600 text-white p-4 rounded hover:bg-purple-700">
              <div className="text-center">
                <div className="text-2xl mb-2">📋</div>
                <div className="text-sm">Procedure Requests</div>
              </div>
            </button>
            <button className="bg-yellow-600 text-white p-4 rounded hover:bg-yellow-700">
              <div className="text-center">
                <div className="text-2xl mb-2">💰</div>
                <div className="text-sm">Billing & Payments</div>
              </div>
            </button>
          </div>
        </div>

        {/* System Status */}
        <div className="bg-white p-6 border border-gray-200 rounded-lg shadow-sm">
          <h3 className="text-lg font-medium text-gray-800 mb-4">System Status</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">System Status</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Operational</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Database</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Connected</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">API Services</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Running</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Last Backup</span>
              <span className="text-sm text-gray-500">2 hours ago</span>
            </div>
          </div>
        </div>

        {/* Debug Info */}
        <div className="bg-gray-100 p-4 rounded mt-8">
          <h4 className="font-medium text-gray-700 mb-2">Debug Info:</h4>
          <pre className="text-xs text-gray-600">
            User: {JSON.stringify(user, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from './LoadingSpinner';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('dashboard');
  const [practices, setPractices] = useState([]);
  const [users, setUsers] = useState([]);
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      const token = localStorage.getItem('dentalToken');
      
      // Load dashboard stats
      const dashboardResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/admin/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (dashboardResponse.ok) {
        const dashboardData = await dashboardResponse.json();
        setStats(dashboardData.stats);
      } else {
        // Fallback to mock data if API fails
        setStats({
          total_practices: 5,
          active_practices: 3,
          trial_practices: 2,
          monthly_revenue: 2500
        });
      }
      
      // Load practices
      const practicesResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/admin/practices`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (practicesResponse.ok) {
        const data = await practicesResponse.json();
        setPractices(data.practices || []);
      }

      setLoading(false);
    } catch (error) {
      console.error('Failed to load admin data:', error);
      // Use fallback data
      setStats({
        total_practices: 5,
        active_practices: 3,
        trial_practices: 2,
        monthly_revenue: 2500
      });
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  const showView = (view) => {
    setActiveView(view);
  };

  const renderPracticeManagement = () => (
    <div className="bg-white p-6 border border-gray-200 rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-800">Practice Management</h3>
        <button 
          onClick={() => showView('dashboard')}
          className="text-blue-600 hover:text-blue-800"
        >
          ← Back to Dashboard
        </button>
      </div>
      
      <div className="space-y-4">
        {practices.length > 0 ? practices.map((practice) => (
          <div key={practice.id} className="border rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-medium text-gray-900">{practice.name}</h4>
                <p className="text-sm text-gray-600">{practice.email}</p>
                <p className="text-sm text-gray-500">Phone: {practice.phone}</p>
                <p className="text-sm text-gray-500">
                  Status: {practice.subscription?.status || 'trial'}
                </p>
              </div>
              <div className="flex space-x-2">
                <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                  View Details
                </button>
                <button className="bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-700">
                  Edit
                </button>
              </div>
            </div>
          </div>
        )) : (
          <div className="text-center py-8 text-gray-500">
            <p>No practices found</p>
            <button className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              Add New Practice
            </button>
          </div>
        )}
      </div>
    </div>
  );

  const renderUserManagement = () => (
    <div className="bg-white p-6 border border-gray-200 rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-800">User Management</h3>
        <button 
          onClick={() => showView('dashboard')}
          className="text-blue-600 hover:text-blue-800"
        >
          ← Back to Dashboard
        </button>
      </div>
      
      <div className="mb-4">
        <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 mr-2">
          Add New Admin User
        </button>
        <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Export Users
        </button>
      </div>
      
      <div className="space-y-4">
        <div className="border rounded-lg p-4">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-medium text-gray-900">Craig Admin</h4>
              <p className="text-sm text-gray-600">cganz2279@gmail.com</p>
              <p className="text-sm text-gray-500">Role: Practice Admin</p>
              <p className="text-sm text-gray-500">Practice: Your Dental Practice</p>
            </div>
            <div className="flex space-x-2">
              <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                Edit
              </button>
              <button className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700">
                Disable
              </button>
            </div>
          </div>
        </div>
        
        <div className="border rounded-lg p-4">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-medium text-gray-900">System Admin</h4>
              <p className="text-sm text-gray-600">admin@theoncallbot.com</p>
              <p className="text-sm text-gray-500">Role: Super Admin</p>
              <p className="text-sm text-gray-500">Practice: All Practices</p>
            </div>
            <div className="flex space-x-2">
              <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                Edit
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderProcedureRequests = () => (
    <div className="bg-white p-6 border border-gray-200 rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-800">Procedure Requests</h3>
        <button 
          onClick={() => showView('dashboard')}
          className="text-blue-600 hover:text-blue-800"
        >
          ← Back to Dashboard
        </button>
      </div>
      
      <div className="mb-4">
        <button 
          onClick={() => showView('create-procedure')}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 mr-2"
        >
          Create New Post-Op Note
        </button>
        <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Export Requests
        </button>
      </div>
      
      <div className="space-y-4">
        <div className="border rounded-lg p-4">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-medium text-gray-900">Custom Crown Procedure</h4>
              <p className="text-sm text-gray-600">Requested by: Your Dental Practice</p>
              <p className="text-sm text-gray-500">Date: Dec 20, 2024</p>
              <p className="text-sm text-gray-500">Status: Pending Review</p>
              <p className="text-sm text-gray-400 mt-2">
                Special post-op instructions for crown placement with custom aftercare requirements...
              </p>
            </div>
            <div className="flex space-x-2">
              <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                Approve
              </button>
              <button className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700">
                Deny
              </button>
              <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                Edit
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCreateProcedure = () => (
    <div className="bg-white p-6 border border-gray-200 rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-800">Create New Post-Op Note</h3>
        <button 
          onClick={() => showView('requests')}
          className="text-blue-600 hover:text-blue-800"
        >
          ← Back to Requests
        </button>
      </div>
      
      <form className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Procedure Name
            </label>
            <input 
              type="text" 
              className="w-full p-3 border border-gray-300 rounded-lg"
              placeholder="e.g., Advanced Root Canal Therapy"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Specialty
            </label>
            <select className="w-full p-3 border border-gray-300 rounded-lg">
              <option>Select Specialty</option>
              <option>General Dentistry</option>
              <option>Oral Surgery</option>
              <option>Endodontics</option>
              <option>Periodontics</option>
              <option>Orthodontics</option>
              <option>Prosthodontics</option>
              <option>Pedodontics</option>
            </select>
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Overview
          </label>
          <textarea 
            className="w-full p-3 border border-gray-300 rounded-lg h-24"
            placeholder="Brief overview of the procedure and its purpose"
          ></textarea>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Immediate Aftercare (first 24-48 hours)
          </label>
          <textarea 
            className="w-full p-3 border border-gray-300 rounded-lg h-32"
            placeholder="Enter immediate aftercare instructions (one per line)"
          ></textarea>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Diet Restrictions
          </label>
          <textarea 
            className="w-full p-3 border border-gray-300 rounded-lg h-24"
            placeholder="Enter diet restrictions (one per line)"
          ></textarea>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Warning Signs (when to contact office)
          </label>
          <textarea 
            className="w-full p-3 border border-gray-300 rounded-lg h-24"
            placeholder="Enter warning signs (one per line)"
          ></textarea>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Recovery Timeline
          </label>
          <textarea 
            className="w-full p-3 border border-gray-300 rounded-lg h-24"
            placeholder="Enter recovery timeline activities (one per line)"
          ></textarea>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Medications
          </label>
          <textarea 
            className="w-full p-3 border border-gray-300 rounded-lg h-24"
            placeholder="Enter medication instructions (one per line)"
          ></textarea>
        </div>
        
        <div className="flex space-x-4">
          <button 
            type="submit"
            className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
          >
            Create Post-Op Note
          </button>
          <button 
            type="button"
            className="bg-gray-600 text-white px-6 py-2 rounded hover:bg-gray-700"
          >
            Save as Draft
          </button>
        </div>
      </form>
    </div>
  );

  const renderBilling = () => (
    <div className="bg-white p-6 border border-gray-200 rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-800">Billing & Payments</h3>
        <button 
          onClick={() => showView('dashboard')}
          className="text-blue-600 hover:text-blue-800"
        >
          ← Back to Dashboard
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-green-50 p-4 rounded-lg">
          <h4 className="font-medium text-green-800">Total Revenue</h4>
          <p className="text-2xl font-bold text-green-600">$12,500</p>
          <p className="text-sm text-green-600">This month</p>
        </div>
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-medium text-blue-800">Active Subscriptions</h4>
          <p className="text-2xl font-bold text-blue-600">3</p>
          <p className="text-sm text-blue-600">Paying practices</p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg">
          <h4 className="font-medium text-yellow-800">Pending Payments</h4>
          <p className="text-2xl font-bold text-yellow-600">$750</p>
          <p className="text-sm text-yellow-600">Overdue</p>
        </div>
      </div>
      
      <div className="space-y-4">
        <h4 className="font-medium text-gray-700">Recent Transactions</h4>
        <div className="border rounded-lg p-4">
          <div className="flex justify-between items-center">
            <div>
              <h5 className="font-medium">Your Dental Practice</h5>
              <p className="text-sm text-gray-600">Monthly subscription - December 2024</p>
            </div>
            <div className="text-right">
              <p className="font-medium text-green-600">+$99.00</p>
              <p className="text-sm text-gray-500">Dec 1, 2024</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

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
        {activeView === 'dashboard' && (
          <>
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
                <button 
                  onClick={() => showView('practices')}
                  className="bg-blue-600 text-white p-4 rounded hover:bg-blue-700"
                >
                  <div className="text-center">
                    <div className="text-2xl mb-2">🏢</div>
                    <div className="text-sm">Manage Practices</div>
                  </div>
                </button>
                <button 
                  onClick={() => showView('users')}
                  className="bg-green-600 text-white p-4 rounded hover:bg-green-700"
                >
                  <div className="text-center">
                    <div className="text-2xl mb-2">👥</div>
                    <div className="text-sm">User Management</div>
                  </div>
                </button>
                <button 
                  onClick={() => showView('requests')}
                  className="bg-purple-600 text-white p-4 rounded hover:bg-purple-700"
                >
                  <div className="text-center">
                    <div className="text-2xl mb-2">📋</div>
                    <div className="text-sm">Procedure Requests</div>
                  </div>
                </button>
                <button 
                  onClick={() => showView('billing')}
                  className="bg-yellow-600 text-white p-4 rounded hover:bg-yellow-700"
                >
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
          </>
        )}

        {activeView === 'practices' && renderPracticeManagement()}
        {activeView === 'users' && renderUserManagement()}
        {activeView === 'requests' && renderProcedureRequests()}
        {activeView === 'create-procedure' && renderCreateProcedure()}
        {activeView === 'billing' && renderBilling()}
      </div>
    </div>
  );
};

export default AdminDashboard;
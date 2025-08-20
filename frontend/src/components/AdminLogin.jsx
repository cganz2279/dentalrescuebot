import React, { useState, useEffect } from 'react';

const AdminLogin = () => {
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [adminToken, setAdminToken] = useState(localStorage.getItem('adminToken'));
  const [dashboardData, setDashboardData] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [practicesData, setPracticesData] = useState([]);
  const [procedureRequests, setProcedureRequests] = useState([]);
  const [paymentsData, setPaymentsData] = useState([]);

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL || 'https://practice-notes.preview.emergentagent.com'}/api`;

  useEffect(() => {
    if (adminToken) {
      loadDashboard();
      loadPractices();
      loadProcedureRequests();  
      loadPayments();
    }
  }, [adminToken]);

  const apiRequest = async (endpoint, options = {}) => {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${adminToken}`,
        ...options.headers
      }
    });

    if (response.status === 401) {
      handleLogout();
      return null;
    }

    return await response.json();
  };

  const handleInputChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE}/admin/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setAdminToken(data.token);
        localStorage.setItem('adminToken', data.token);
        await loadDashboard();
      } else {
        setError(data.detail || 'Invalid admin credentials');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadDashboard = async () => {
    try {
      const data = await apiRequest('/admin/dashboard');
      if (data && data.success) {
        setDashboardData(data);
      }
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    }
  };

  const loadPractices = async () => {
    try {
      const data = await apiRequest('/admin/practices?limit=100');
      if (data && data.success) {
        setPracticesData(data.practices);
      }
    } catch (err) {
      console.error('Failed to load practices:', err);
    }
  };

  const loadProcedureRequests = async () => {
    try {
      const data = await apiRequest('/admin/procedure-requests');
      if (data && data.success) {
        setProcedureRequests(data.data);
      }
    } catch (err) {
      console.error('Failed to load procedure requests:', err);
    }
  };

  const loadPayments = async () => {
    try {
      const data = await apiRequest('/admin/payments?limit=50');
      if (data && data.success) {
        setPaymentsData(data.transactions);
      }
    } catch (err) {
      console.error('Failed to load payments:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('adminToken');
    setAdminToken(null);
    setDashboardData(null);
    setCredentials({ email: '', password: '' });
    setActiveTab('dashboard');
  };

  const managePractice = async (practiceId, action) => {
    try {
      const data = await apiRequest('/admin/manage-practice', {
        method: 'POST',
        body: JSON.stringify({
          practice_id: practiceId,
          action: action
        })
      });

      if (data && data.success) {
        alert(`Practice ${action} successful!`);
        loadPractices(); // Reload practices
      } else {
        alert(`Failed to ${action} practice`);
      }
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const updateRequestStatus = async (requestId, status) => {
    try {
      const data = await apiRequest(`/admin/procedure-requests/${requestId}`, {
        method: 'PUT',
        body: JSON.stringify({
          status: status,
          adminNotes: `Request ${status} by admin`
        })
      });

      if (data && data.success) {
        alert(`Request ${status} successfully!`);
        loadProcedureRequests(); // Reload requests
      } else {
        alert(`Failed to ${status} request`);
      }
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const viewPracticeDetails = (practice) => {
    // Handle address object properly
    let addressText = 'Not provided';
    if (practice.address) {
      if (typeof practice.address === 'string') {
        addressText = practice.address;
      } else if (typeof practice.address === 'object') {
        // Handle address as object
        const addressParts = [];
        if (practice.address.street) addressParts.push(practice.address.street);
        if (practice.address.city) addressParts.push(practice.address.city);
        if (practice.address.state) addressParts.push(practice.address.state);
        if (practice.address.zipCode || practice.address.zip) addressParts.push(practice.address.zipCode || practice.address.zip);
        if (practice.address.country) addressParts.push(practice.address.country);
        
        if (addressParts.length > 0) {
          addressText = addressParts.join(', ');
        } else {
          // If object but no recognizable fields, show formatted object
          addressText = JSON.stringify(practice.address, null, 2).replace(/[{}",]/g, '').trim();
        }
      }
    }

    const details = [
      `🏥 PRACTICE INFORMATION`,
      `Name: ${practice.name || 'Not provided'}`,
      `Email: ${practice.email || 'Not provided'}`,
      `Phone: ${practice.phone || 'Not provided'}`,
      `Address: ${addressText}`,
      `Website: ${practice.website || 'Not provided'}`,
      ``,
      `📊 STATUS & SUBSCRIPTION`,
      `Active: ${practice.isActive ? 'Yes' : 'No'}`,
      `Subscription Status: ${practice.subscription?.status || 'Unknown'}`,
      `Subscription Plan: ${practice.subscription?.plan || 'Not specified'}`,
      `Auto Renew: ${practice.subscription?.autoRenew ? 'Yes' : 'No'}`,
      `Trial Ends: ${practice.subscription?.trialEndsAt ? formatDate(practice.subscription.trialEndsAt) : 'N/A'}`,
      `Next Billing: ${practice.subscription?.nextBillingDate ? formatDate(practice.subscription.nextBillingDate) : 'N/A'}`,
      ``,
      `📅 DATES`,
      `Created: ${formatDate(practice.createdAt)}`,
      `Last Updated: ${formatDate(practice.updatedAt)}`,
      ``,
      `🔧 TECHNICAL INFO`,
      `Practice ID: ${practice.id}`,
      `Database ID: ${practice._id || 'N/A'}`,
      ``,
      `💼 ADMIN INFO`,
      `Admin Password Set: ${practice.adminPassword ? 'Yes' : 'No'}`,
      `Email Verified: ${practice.emailVerified ? 'Yes' : 'No'}`,
      `Setup Complete: ${practice.setupComplete ? 'Yes' : 'No'}`
    ];
    
    alert(details.join('\n'));
  };

  // If logged in, show dashboard
  if (adminToken && dashboardData) {
    const { stats, recent_practices, expiring_trials } = dashboardData;
    
    return (
      <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ 
          background: 'linear-gradient(135deg, #3c7ab7 0%, #2c5a87 100%)',
          color: 'white',
          padding: '20px',
          borderRadius: '10px',
          marginBottom: '30px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h1 style={{ fontSize: '28px', fontWeight: '700', margin: 0 }}>
            Practice Notes Admin Dashboard
          </h1>
          <button 
            onClick={handleLogout}
            style={{
              background: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              padding: '10px 20px',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>

        {/* Stats Grid */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '20px',
          marginBottom: '30px'
        }}>
          <div style={{ 
            background: 'white', 
            borderRadius: '10px', 
            padding: '25px', 
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '36px', fontWeight: '700', color: '#3c7ab7', marginBottom: '5px' }}>
              {stats.total_practices}
            </div>
            <div style={{ fontSize: '16px', color: '#666', fontWeight: '500' }}>Total Practices</div>
          </div>
          
          <div style={{ 
            background: 'white', 
            borderRadius: '10px', 
            padding: '25px', 
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '36px', fontWeight: '700', color: '#3c7ab7', marginBottom: '5px' }}>
              {stats.active_practices}
            </div>
            <div style={{ fontSize: '16px', color: '#666', fontWeight: '500' }}>Active Practices</div>
          </div>
          
          <div style={{ 
            background: 'white', 
            borderRadius: '10px', 
            padding: '25px', 
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '36px', fontWeight: '700', color: '#3c7ab7', marginBottom: '5px' }}>
              {stats.trial_practices}
            </div>
            <div style={{ fontSize: '16px', color: '#666', fontWeight: '500' }}>Trial Practices</div>
          </div>
          
          <div style={{ 
            background: 'white', 
            borderRadius: '10px', 
            padding: '25px', 
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '36px', fontWeight: '700', color: '#28a745', marginBottom: '5px' }}>
              {formatCurrency(stats.total_revenue)}
            </div>
            <div style={{ fontSize: '16px', color: '#666', fontWeight: '500' }}>Total Revenue</div>
          </div>
          
          <div style={{ 
            background: 'white', 
            borderRadius: '10px', 
            padding: '25px', 
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '36px', fontWeight: '700', color: '#28a745', marginBottom: '5px' }}>
              {formatCurrency(stats.monthly_revenue)}
            </div>
            <div style={{ fontSize: '16px', color: '#666', fontWeight: '500' }}>Monthly Revenue</div>
          </div>
        </div>

        {/* Recent Practices */}
        <div style={{ 
          background: 'white', 
          borderRadius: '10px', 
          padding: '20px', 
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
          marginBottom: '20px'
        }}>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>Recent Practices</h3>
          {recent_practices && recent_practices.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: '#f8f9fa' }}>
                    <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e9ecef' }}>
                      Practice Name
                    </th>
                    <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e9ecef' }}>
                      Email
                    </th>
                    <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e9ecef' }}>
                      Status
                    </th>
                    <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e9ecef' }}>
                      Created
                    </th>
                    <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e9ecef' }}>
                      Actions
                    </th>
                    <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e9ecef' }}>
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {recent_practices.slice(0, 10).map((practice, index) => (
                    <tr key={index} style={{ ':hover': { background: '#f8f9fa' } }}>
                      <td style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>
                        {practice.name}
                      </td>
                      <td style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>
                        {practice.email}
                      </td>
                      <td style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>
                        <span style={{
                          padding: '4px 12px',
                          borderRadius: '20px',
                          fontSize: '12px',
                          fontWeight: '500',
                          textTransform: 'uppercase',
                          background: practice.subscription?.status === 'active' ? '#d4edda' : '#fff3cd',
                          color: practice.subscription?.status === 'active' ? '#155724' : '#856404'
                        }}>
                          {practice.subscription?.status || 'unknown'}
                        </span>
                      </td>
                      <td style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>
                        {formatDate(practice.createdAt)}
                      </td>
                      <td style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>
                        <button 
                          onClick={() => viewPracticeDetails(practice)}
                          style={{
                            padding: '6px 12px',
                            background: '#3c7ab7',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '12px',
                            marginRight: '5px'
                          }}
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No recent practices found.</p>
          )}
        </div>

        {/* Expiring Trials */}
        {expiring_trials && expiring_trials.length > 0 && (
          <div style={{ 
            background: 'white', 
            borderRadius: '10px', 
            padding: '20px', 
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)'
          }}>
            <h3 style={{ marginBottom: '20px', color: '#dc3545' }}>Expiring Trials (Next 3 Days)</h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: '#f8f9fa' }}>
                    <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e9ecef' }}>
                      Practice Name
                    </th>
                    <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e9ecef' }}>
                      Email
                    </th>
                    <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e9ecef' }}>
                      Trial Ends
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {expiring_trials.map((practice, index) => (
                    <tr key={index}>
                      <td style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>
                        {practice.name}
                      </td>
                      <td style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>
                        {practice.email}
                      </td>
                      <td style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>
                        {formatDate(practice.subscription?.trialEndsAt)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <div style={{ 
          background: '#fff3cd', 
          color: '#856404', 
          padding: '15px', 
          borderRadius: '6px',
          marginTop: '20px',
          textAlign: 'center'
        }}>
          <strong>Admin Dashboard</strong> - This is a simplified view. The full admin dashboard with practice management, payments, and procedure requests is available in the complete HTML version.
        </div>
      </div>
    );
  }

  // Show login form
  return (
    <div style={{ 
      maxWidth: '400px', 
      margin: '100px auto', 
      background: 'white', 
      padding: '40px', 
      borderRadius: '10px',
      boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)'
    }}>
      <h2 style={{ 
        textAlign: 'center', 
        fontSize: '24px', 
        fontWeight: '700', 
        color: '#3c7ab7', 
        marginBottom: '30px' 
      }}>
        Admin Login
      </h2>
      
      {error && (
        <div style={{ 
          background: '#f8d7da', 
          color: '#721c24', 
          padding: '15px', 
          borderRadius: '6px', 
          marginBottom: '20px' 
        }}>
          {error}
        </div>
      )}
      
      <form onSubmit={handleLogin}>
        <div style={{ marginBottom: '20px' }}>
          <label style={{ 
            display: 'block', 
            marginBottom: '8px', 
            fontWeight: '500', 
            color: '#333' 
          }}>
            Admin Email:
          </label>
          <input
            type="email"
            name="email"
            value={credentials.email}
            onChange={handleInputChange}
            required
            style={{ 
              width: '100%', 
              padding: '12px', 
              border: '1px solid #ddd', 
              borderRadius: '6px', 
              fontSize: '16px',
              boxSizing: 'border-box'
            }}
          />
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <label style={{ 
            display: 'block', 
            marginBottom: '8px', 
            fontWeight: '500', 
            color: '#333' 
          }}>
            Password:
          </label>
          <input
            type="password"
            name="password"
            value={credentials.password}
            onChange={handleInputChange}
            required
            style={{ 
              width: '100%', 
              padding: '12px', 
              border: '1px solid #ddd', 
              borderRadius: '6px', 
              fontSize: '16px',
              boxSizing: 'border-box'
            }}
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading}
          style={{ 
            width: '100%', 
            padding: '12px', 
            background: loading ? '#ccc' : '#3c7ab7',
            color: 'white', 
            border: 'none', 
            borderRadius: '6px', 
            fontSize: '16px', 
            fontWeight: '600', 
            cursor: loading ? 'not-allowed' : 'pointer',
            marginTop: '10px'
          }}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};

export default AdminLogin;
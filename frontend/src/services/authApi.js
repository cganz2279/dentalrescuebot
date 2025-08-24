import axios from 'axios';

// Create axios instances with comprehensive error handling and cache busting
const createAxiosInstance = (baseURL) => {
  const instance = axios.create({
    baseURL,
    timeout: 20000, // Increased to 20 seconds
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-cache',
      'Pragma': 'no-cache',
      'X-Requested-With': 'XMLHttpRequest'
    },
    // Add cache busting
    params: {
      '_t': Date.now()
    }
  });

  // Add request interceptor with comprehensive debugging
  instance.interceptors.request.use(
    (config) => {
      // Add DNS cache buster from global variable
      if (window.DNS_CACHE_BUSTER) {
        config.params = { ...config.params, _dns: window.DNS_CACHE_BUSTER };
      }
      
      console.log(`🚀 Making request to: ${config.baseURL}${config.url}`);
      console.log('Request config:', { 
        method: config.method, 
        url: config.url, 
        headers: config.headers,
        params: config.params 
      });
      
      const token = localStorage.getItem('dentalToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        console.log('✅ Token added to request');
      } else {
        console.log('⚠️ No token found in localStorage');
      }
      return config;
    },
    (error) => {
      console.error('❌ Request interceptor error:', error);
      return Promise.reject(error);
    }
  );

  // Enhanced response interceptor with multiple retry strategies
  instance.interceptors.response.use(
    (response) => {
      console.log('✅ Response received:', response.status, response.statusText);
      return response;
    },
    async (error) => {
      console.error('❌ API Error Details:', {
        message: error.message,
        code: error.code,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      });
      
      const config = error.config;
      
      // Handle different types of network errors
      if (!config._retryCount) config._retryCount = 0;
      
      // Retry logic for various error types
      if (config._retryCount < 3) {
        const shouldRetry = 
          error.message === 'Network Error' ||
          error.code === 'ERR_NETWORK' ||
          error.code === 'ECONNREFUSED' ||
          error.code === 'ETIMEDOUT' ||
          (error.response?.status >= 500 && error.response?.status < 600);
          
        if (shouldRetry) {
          config._retryCount += 1;
          console.warn(`🔄 Retrying request (attempt ${config._retryCount}/3)...`);
          
          // Add different retry strategies
          const retryDelay = config._retryCount * 1000; // Exponential backoff
          
          // Update headers for retry
          config.headers = {
            ...config.headers,
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'X-Retry-Attempt': config._retryCount
          };
          
          // Add new cache buster for retry
          config.params = {
            ...config.params,
            _retry: Date.now(),
            _attempt: config._retryCount
          };
          
          // Wait before retry
          await new Promise(resolve => setTimeout(resolve, retryDelay));
          
          return instance.request(config);
        }
      }
      
      // If all retries failed, provide helpful error message
      if (error.message === 'Network Error' || error.code === 'ERR_NETWORK') {
        console.error('🔥 Network connectivity issue detected. All retry attempts failed.');
        error.userMessage = 'Unable to connect to server. Please check your internet connection and try again.';
      }
      
      return Promise.reject(error);
    }
  );

  return instance;
};

// Get backend URL - use current domain if no specific URL provided
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || window.location.origin;

const AUTH_BASE_URL = `${BACKEND_URL}/api/auth`;
const PRACTICE_BASE_URL = `${BACKEND_URL}/api/practice`;

console.log('Auth API using backend URL:', BACKEND_URL);

// Create instances with retry logic
const authAxios = createAxiosInstance(AUTH_BASE_URL);
const practiceAxios = createAxiosInstance(PRACTICE_BASE_URL);

// Additional response interceptor for auth-specific error handling
const handleAuthError = (error) => {
  if (error.response?.status === 401) {
    // Token expired or invalid
    localStorage.removeItem('dentalToken');
    window.location.href = '/login';
  }
  return Promise.reject(error);
};

// Add auth-specific error handling to both instances
authAxios.interceptors.response.use(
  (response) => response,
  handleAuthError
);

practiceAxios.interceptors.response.use(
  (response) => response,
  handleAuthError
);

export const authApi = {
  // Authentication endpoints
  login: async (email, password) => {
    const response = await authAxios.post('/login', { email, password });
    return response.data;
  },

  // Admin login endpoint
  adminLogin: async (email, password) => {
    try {
      // Try super admin login first
      const adminResponse = await authAxios.post('/admin/login', { email, password });
      return adminResponse.data;
    } catch (adminError) {
      // If admin login fails, try regular login and check role
      console.log('Admin login failed, trying regular login...');
      try {
        const regularResponse = await authAxios.post('/login', { email, password });
        const userData = regularResponse.data;
        
        // Check if user has admin role
        if (userData.user && (userData.user.role === 'super_admin' || userData.user.role === 'admin' || userData.user.role === 'practice_admin')) {
          return userData;
        } else {
          throw new Error('Admin access required');
        }
      } catch (regularError) {
        throw adminError; // Return original admin error
      }
    }
  },

  registerPractice: async (practiceData) => {
    const response = await authAxios.post('/register-practice', {
      practiceName: practiceData.practiceName,
      email: practiceData.email,
      phone: practiceData.phone,
      website: practiceData.website,
      adminFirstName: practiceData.adminFirstName,
      adminLastName: practiceData.adminLastName,
      adminPassword: practiceData.adminPassword,
      street: practiceData.street,
      city: practiceData.city,
      state: practiceData.state,
      zipCode: practiceData.zipCode
    });
    return response.data;
  },

  getCurrentUser: async (token) => {
    const response = await authAxios.get('/me', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },

  invitePatient: async (email, firstName, lastName) => {
    const token = localStorage.getItem('dentalToken');
    const response = await authAxios.post('/invite-patient', 
      { email, firstName, lastName },
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );
    return response.data;
  },

  getPatientDashboard: async () => {
    // REMOVED - Patients do not use this app
    throw new Error('Patients do not have access to this system');
  }
};

export const practiceApi = {
  // Practice management endpoints
  getDashboard: async () => {
    const response = await practiceAxios.get('/dashboard');
    return response.data;
  },

  getPatients: async () => {
    const response = await practiceAxios.get('/patients');
    return response.data;
  },

  createPatient: async (patientData) => {
    const response = await practiceAxios.post('/patients', patientData);
    return response.data;
  },

  assignProcedure: async (assignmentData) => {
    const response = await practiceAxios.post('/assign-procedure', assignmentData);
    return response.data;
  },

  getStaff: async () => {
    const response = await practiceAxios.get('/staff');
    return response.data;
  },

  addStaff: async (staffData) => {
    try {
      console.log('Adding staff with data:', staffData);
      const params = new URLSearchParams({
        firstName: staffData.firstName,
        lastName: staffData.lastName,
        email: staffData.email
      });
      console.log('Request URL:', `/add-staff?${params}`);
      const response = await practiceAxios.post(`/add-staff?${params}`);
      console.log('Add staff response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Add staff error:', error.response?.data || error.message);
      throw error;
    }
  },

  getPatient: async (patientId) => {
    const response = await practiceAxios.get(`/patients/${patientId}`);
    return response.data;
  },

  updatePatient: async (patientId, patientData) => {
    const params = new URLSearchParams({
      firstName: patientData.firstName,
      lastName: patientData.lastName,
      email: patientData.email,
      phone: patientData.phone || '',
      assignedDentistId: patientData.assignedDentistId || ''
    });
    const response = await practiceAxios.put(`/patients/${patientId}?${params}`);
    return response.data;
  },

  requestProcedure: async (requestData) => {
    const response = await practiceAxios.post('/request-procedure', requestData);
    return response.data;
  },

  updateBranding: async (brandingData) => {
    const response = await practiceAxios.put('/branding', brandingData);
    return response.data;
  },

  updatePractice: async (updateData) => {
    const response = await practiceAxios.put('/update', updateData);
    return response.data;
  },

  getProcedureAssignment: async (assignmentId) => {
    console.log('Getting procedure assignment:', assignmentId);
    const response = await practiceAxios.get(`/procedure-assignments/${assignmentId}`);
    console.log('Get procedure assignment response:', response.data);
    return response.data;
  },

  updateProcedureAssignment: async (assignmentId, updateData) => {
    console.log('Updating procedure assignment:', assignmentId, updateData);
    const response = await practiceAxios.put(`/procedure-assignments/${assignmentId}`, updateData);
    console.log('Update procedure assignment response:', response.data);
    return response.data;
  }
};
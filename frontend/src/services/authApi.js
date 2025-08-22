import axios from 'axios';

// Get backend URL with proper fallback that works in all environments
const BACKEND_URL = import.meta.env?.REACT_APP_BACKEND_URL || 
                    process.env?.REACT_APP_BACKEND_URL || 
                    window.location.origin; // Use current domain instead of hardcoded preview

const AUTH_BASE_URL = `${BACKEND_URL}/api/auth`;
const PRACTICE_BASE_URL = `${BACKEND_URL}/api/practice`;

console.log('Auth API using backend URL:', BACKEND_URL);

// Create axios instance for auth
const authAxios = axios.create({
  baseURL: AUTH_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create axios instance for practice management
const practiceAxios = axios.create({
  baseURL: PRACTICE_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to practice requests
practiceAxios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('dentalToken');
    console.log('Token from localStorage:', token ? token.substring(0, 50) + '...' : 'No token found');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
const handleApiError = (error) => {
  if (error.response?.status === 401) {
    // Token expired or invalid
    localStorage.removeItem('dentalToken');
    window.location.href = '/login';
  }
  return Promise.reject(error);
};

authAxios.interceptors.response.use(
  (response) => response,
  handleApiError
);

practiceAxios.interceptors.response.use(
  (response) => response,
  handleApiError
);

export const authApi = {
  // Authentication endpoints
  login: async (email, password) => {
    const response = await authAxios.post('/login', { email, password });
    return response.data;
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
    const token = localStorage.getItem('dentalToken');
    const response = await authAxios.get('/patient-dashboard', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
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

  updateBranding: async (brandingData) => {
    const response = await practiceAxios.put('/branding', brandingData);
    return response.data;
  },

  updatePractice: async (updateData) => {
    const response = await practiceAxios.put('/update', updateData);
    return response.data;
  }
};
import axios from 'axios';

// Get backend URL with fallback
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

console.log('Auth API using backend URL:', BACKEND_URL);
console.log('Environment REACT_APP_BACKEND_URL:', process.env.REACT_APP_BACKEND_URL);
console.log('All environment variables:', process.env);

// Create axios instance for auth
const authAxios = axios.create({
  baseURL: BACKEND_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create axios instance for practice management
const practiceAxios = axios.create({
  baseURL: BACKEND_URL,
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
    console.log('Login attempt - Backend URL:', BACKEND_URL);
    console.log('Login attempt - Full URL:', `${BACKEND_URL}/api/auth/login`);
    try {
      const response = await authAxios.post('/api/auth/login', { email, password });
      console.log('Login successful:', response.data);
      return response.data;
    } catch (error) {
      console.error('Login error:', error.response?.data || error.message);
      console.error('Login error - URL attempted:', error.config?.url);
      throw error;
    }
  },

  registerPractice: async (practiceData) => {
    const response = await authAxios.post('/api/auth/register-practice', {
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
    const response = await authAxios.get('/api/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },

  invitePatient: async (email, firstName, lastName) => {
    const token = localStorage.getItem('dentalToken');
    const response = await authAxios.post('/api/auth/invite-patient', 
      { email, firstName, lastName },
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );
    return response.data;
  },

  getProcedures: async (specialty = null) => {
    // This endpoint doesn't require authentication - use direct axios
    const url = specialty ? `/api/procedures?specialty=${specialty}` : '/api/procedures';
    const response = await axios.get(`${BACKEND_URL}${url}`);
    return response.data;
  }
};

export const practiceApi = {
  // Practice management endpoints
  getDashboard: async () => {
    const response = await practiceAxios.get('/api/practice/dashboard');
    return response.data;
  },

  getPatients: async () => {
    const response = await practiceAxios.get('/api/practice/patients');
    return response.data;
  },

  createPatient: async (patientData) => {
    const response = await practiceAxios.post('/api/practice/patients', patientData);
    return response.data;
  },

  assignProcedure: async (assignmentData) => {
    const response = await practiceAxios.post('/api/practice/assign-procedure', assignmentData);
    return response.data;
  },

  updateBranding: async (brandingData) => {
    const response = await practiceAxios.put('/api/practice/branding', brandingData);
    return response.data;
  },

  updatePractice: async (updateData) => {
    const response = await practiceAxios.put('/api/practice/update', updateData);
    return response.data;
  },

  getExportData: async () => {
    const response = await practiceAxios.get('/api/practice/export-data');
    return response.data;
  },

  getProcedureAssignment: async (assignmentId) => {
    const response = await practiceAxios.get(`/api/practice/assignment/${assignmentId}`);
    return response.data;
  },

  updateProcedureAssignment: async (assignmentId, updateData) => {
    const response = await practiceAxios.put(`/api/practice/assignment/${assignmentId}`, updateData);
    return response.data;
  },

  getPracticeDoctors: async () => {
    const response = await practiceAxios.get('/api/practice/doctors');
    return response.data;
  },

  requestNewProcedure: async (requestData) => {
    const response = await practiceAxios.post('/api/practice/request-procedure', requestData);
    return response.data;
  },

  updatePatient: async (patientId, patientData) => {
    const response = await practiceAxios.put(`/api/practice/patients/${patientId}`, patientData);
    return response.data;
  },

  deletePatient: async (patientId, hardDelete = false) => {
    const response = await practiceAxios.put(`/api/practice/patients/${patientId}`, {
      action: hardDelete ? "remove" : "deactivate",
      confirmDelete: true
    });
    return response.data;
  },

  // Dentist management
  getDentists: async () => {
    const response = await practiceAxios.get('/api/practice/dentists');
    return response.data;
  },

  addDentist: async (dentistData) => {
    const response = await practiceAxios.post('/api/practice/dentists', dentistData);
    return response.data;
  },

  updateDentist: async (dentistId, dentistData) => {
    const response = await practiceAxios.put(`/api/practice/dentists/${dentistId}`, dentistData);
    return response.data;
  },

  removeDentist: async (dentistId) => {
    const response = await practiceAxios.delete(`/api/practice/dentists/${dentistId}`);
    return response.data;
  },

  // Practice-specific procedure management
  getPracticeProcedures: async () => {
    const response = await practiceAxios.get('/api/practice/procedures');
    return response.data;
  },

  getPracticeProcedure: async (procedureId) => {
    const response = await practiceAxios.get(`/api/practice/procedures/${procedureId}`);
    return response.data;
  },

  customizeProcedure: async (procedureId, customization) => {
    const response = await practiceAxios.post(`/api/practice/procedures/${procedureId}/customize`, customization);
    return response.data;
  },

  removeProcedureCustomization: async (procedureId) => {
    const response = await practiceAxios.delete(`/api/practice/procedures/${procedureId}/customize`);
    return response.data;
  },

  emailPDF: async (emailData) => {
    const response = await practiceAxios.post('/api/practice/email-pdf', emailData);
    return response.data;
  },

  smsPDF: async (smsData) => {
    const response = await practiceAxios.post('/api/practice/sms-pdf', smsData);
    return response.data;
  },

  getExportActivities: async (queryParams = '') => {
    const response = await practiceAxios.get(`/api/practice/export-activities?${queryParams}`);
    return response.data;
  },

  logActivity: async (activityData) => {
    const response = await practiceAxios.post('/api/practice/log-activity', activityData);
    return response.data;
  }
};

export const patientsApi = {
  // Patient-specific endpoints
  getDashboard: async () => {
    const token = localStorage.getItem('dentalToken');
    const response = await axios.get(`${BACKEND_URL}/api/patients/dashboard`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },

  getProcedure: async (assignmentId) => {
    const token = localStorage.getItem('dentalToken');
    const response = await axios.get(`${BACKEND_URL}/api/patients/procedures/${assignmentId}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },

  trackDownload: async (assignmentId) => {
    const token = localStorage.getItem('dentalToken');
    const response = await axios.post(`${BACKEND_URL}/api/patients/procedures/${assignmentId}/download`, {}, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },

  updateProcedureOverview: async (procedureId, overview) => {
    const token = localStorage.getItem('dentalToken');
    const response = await axios.put(`${BACKEND_URL}/api/public/procedures/${procedureId}/overview`, 
      { overview }, 
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    return response.data;
  },

  setupPassword: async (setupData) => {
    const response = await axios.post(`${BACKEND_URL}/api/auth/patient-setup`, setupData);
    return response.data;
  }
};
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Create axios instance with default config
const api = axios.create({
  baseURL: BACKEND_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for consistent error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API service functions
export const dentalApi = {
  // Get all specialties with procedure counts
  getSpecialties: async () => {
    try {
      const response = await api.get('/api/specialties');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch specialties');
    }
  },

  // Get specific specialty with its procedures
  getSpecialty: async (specialtyId) => {
    try {
      const response = await api.get(`/api/specialties/${specialtyId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch specialty');
    }
  },

  // Get all procedures or filter by specialty
  getProcedures: async (specialtyFilter = null) => {
    try {
      const params = specialtyFilter ? { specialty: specialtyFilter } : {};
      const response = await api.get('/api/procedures', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch procedures');
    }
  },

  // Get specific procedure details
  getProcedure: async (procedureId) => {
    try {
      const response = await api.get(`/api/procedures/${procedureId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch procedure');
    }
  },

  // Search procedures
  searchProcedures: async (query) => {
    try {
      const response = await api.get('/api/procedures/search', {
        params: { q: query }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to search procedures');
    }
  }
};

export default api;
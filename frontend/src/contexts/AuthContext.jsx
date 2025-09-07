import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/authApi';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [practice, setPractice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('dentalToken'));

  // Initialize authentication state
  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('dentalToken');
      if (savedToken) {
        try {
          const response = await authApi.getCurrentUser(savedToken);
          setUser(response.user);
          setPractice(response.practice);
          setToken(savedToken);
        } catch (error) {
          console.error('Token validation failed:', error);
          localStorage.removeItem('dentalToken');
          setToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (userData, authToken, practiceData = null) => {
    console.log('🔐 Login called with:', { userData: userData?.email, authToken: authToken ? 'TOKEN_PROVIDED' : 'NO_TOKEN', practiceData: practiceData ? 'PRACTICE_PROVIDED' : 'NO_PRACTICE' });
    setUser(userData);
    setToken(authToken);
    localStorage.setItem('dentalToken', authToken);
    
    // Fetch complete practice data from dashboard API
    console.log('🔍 Checking if should fetch practice data:', { hasToken: !!authToken, hasPracticeData: !!practiceData });
    
    if (authToken && !practiceData) {
      try {
        console.log('🏥 Fetching practice data from dashboard API...');
        const practiceApi = (await import('../services/authApi')).practiceApi;
        const dashboardData = await practiceApi.getDashboard();
        console.log('📊 Dashboard data received:', dashboardData);
        
        if (dashboardData.success && dashboardData.data?.practice) {
          const fullPracticeData = dashboardData.data.practice;
          console.log('✅ Setting complete practice data:', fullPracticeData);
          console.log('🏢 Practice has officeHours:', !!fullPracticeData.officeHours);
          console.log('📞 Practice has emergencyContact:', !!fullPracticeData.emergencyContact);
          setPractice(fullPracticeData);
        } else {
          console.warn('⚠️ No practice data in dashboard response:', dashboardData);
          setPractice(practiceData);
        }
      } catch (error) {
        console.error('❌ Failed to fetch practice data:', error);
        setPractice(practiceData);
      }
    } else {
      console.log('⏭️ Skipping dashboard fetch, using provided practice data');
      setPractice(practiceData);
    }
    
    // Force a small delay to ensure state updates are processed
    setTimeout(() => {
      console.log('✅ After login - user:', userData?.email, 'token exists:', !!authToken);
    }, 100);
    
    return { success: true };
  };

  const registerPractice = async (practiceData) => {
    try {
      const response = await authApi.registerPractice(practiceData);
      
      setUser(response.user);
      setPractice(response.practice);
      setToken(response.token);
      
      localStorage.setItem('dentalToken', response.token);
      
      return { success: true, user: response.user, practice: response.practice };
    } catch (error) {
      console.error('Practice registration failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    setUser(null);
    setPractice(null);
    setToken(null);
    localStorage.removeItem('dentalToken');
  };

  const isAuthenticated = () => {
    return !!user && !!token;
  };

  const isPracticeAdmin = () => {
    return user?.role === 'practice_admin';
  };

  const isPracticeStaff = () => {
    return user?.role === 'practice_admin' || user?.role === 'practice_staff';
  };

  const isPatient = () => {
    return user?.role === 'patient';
  };

  const value = {
    user,
    practice,
    token,
    loading,
    login,
    registerPractice,
    logout,
    isAuthenticated,
    isPracticeAdmin,
    isPracticeStaff,
    isPatient
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
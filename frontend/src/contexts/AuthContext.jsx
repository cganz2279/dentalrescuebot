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
      // Check for auto-login from WordPress redirect
      const urlParams = new URLSearchParams(window.location.search);
      const urlToken = urlParams.get('token');
      const autoLogin = urlParams.get('auto');
      
      if (urlToken && autoLogin === 'true') {
        // Use token from URL for auto-login
        localStorage.setItem('dentalToken', urlToken);
        try {
          const response = await authApi.getCurrentUser(urlToken);
          setUser(response.user);
          setPractice(response.practice);
          setToken(urlToken);
          
          // Clean up URL parameters
          window.history.replaceState({}, document.title, window.location.pathname);
        } catch (error) {
          console.error('Auto-login failed:', error);
          localStorage.removeItem('dentalToken');
          setToken(null);
        }
      } else {
        // Normal token check
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
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await authApi.login(email, password);
      
      setUser(response.user);
      setPractice(response.practice);
      setToken(response.token);
      
      localStorage.setItem('dentalToken', response.token);
      
      return { success: true, user: response.user };
    } catch (error) {
      console.error('Login failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
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
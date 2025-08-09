/* eslint-disable react-hooks/exhaustive-deps */
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { useAlert } from '../context/AlertContext';

const AuthContext = createContext(null);

const TOKEN_KEY = 'auth_token';

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [isAuthenticated, setIsAuthenticated] = useState(() => !!localStorage.getItem(TOKEN_KEY));

  const { showAlert } = useAlert();

  // Save token to localStorage when it changes
  useEffect(() => {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
      setIsAuthenticated(true);
    } else {
      localStorage.removeItem(TOKEN_KEY);
      setIsAuthenticated(false);
    }
  }, [token]);

  const login = useCallback((newToken) => {
    setToken(newToken);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
  }, []);

  // Inactivity logout effect
  useEffect(() => {
    if (!isAuthenticated) return;

    const checkInactivity = () => {
      const lastActivity = parseInt(localStorage.getItem('last_api_activity'), 10);
      const now = Date.now();
      // 1 hour = 3600000 ms
      if (lastActivity && now - lastActivity > 3600000) {
        logout();
        showAlert('You have been logged out due to inactivity.', 'warning');
      }
    };

    // Check every minute
    const interval = setInterval(checkInactivity, 60000);
    return () => clearInterval(interval);
  }, [isAuthenticated, logout]);

  const value = {
    isAuthenticated,
    token,
    setToken,
    login,
    logout,
    setIsAuthenticated,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

// Move useAuth to a separate file if you want to avoid the fast refresh warning, but for now, this is safe for most apps.
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
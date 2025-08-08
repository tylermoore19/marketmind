import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';

const AuthContext = createContext(null);

const TOKEN_KEY = 'auth_token';

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [isAuthenticated, setIsAuthenticated] = useState(() => !!localStorage.getItem(TOKEN_KEY));

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

  const value = {
    isAuthenticated,
    token,
    login,
    logout,
    setIsAuthenticated, // for legacy compatibility
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
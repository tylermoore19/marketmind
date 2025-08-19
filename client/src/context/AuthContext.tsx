/* eslint-disable react-hooks/exhaustive-deps */
import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useAlert } from './AlertContext';

const TOKEN_KEY = 'auth_token';

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  setToken: (token: string | null) => void;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

interface Props {
  children: ReactNode;
}

export const AuthProvider = ({ children }: Props) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => !!localStorage.getItem(TOKEN_KEY));

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

  const login = useCallback((newToken: string) => {
    setToken(newToken);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
  }, []);

  // Inactivity logout effect
  useEffect(() => {
    if (!isAuthenticated) return;

    const checkInactivity = () => {
      const lastActivity = parseInt(localStorage.getItem("last_api_activity") || "0", 10);
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

  const value: AuthContextType = {
    isAuthenticated,
    token,
    setToken,
    login,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Move useAuth to a separate file if you want to avoid the fast refresh warning, but for now, this is safe for most apps.
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
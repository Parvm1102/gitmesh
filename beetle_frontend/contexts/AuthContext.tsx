"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: number;
  login: string;
  name: string;
  email: string;
  avatar_url: string;
  bio: string;
  location: string;
  company: string;
  blog: string;
  twitter_username: string;
  public_repos: number;
  followers: number;
  following: number;
  created_at: string;
  lastLogin: string;
  analytics?: {
    totalCommits: number;
    totalPRs: number;
    totalIssues: number;
    activeRepositories: number;
  };
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  login: () => void;
  loginDemo: () => void;
  logout: () => void;
  forceLogout: () => void;
  validateToken: () => Promise<boolean>;
  setUserFromCallback: (userData: User, authToken: string) => void;
  enableAutoDemo: () => void;
  disableAutoDemo: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Use environment variable for backend URL or fallback to default
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL 
  ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1` 
  : 'http://localhost:3001/api/v1';

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Initialize auth state from localStorage
  useEffect(() => {
    console.log('AuthContext: Initializing auth state');
    const storedToken = localStorage.getItem('beetle_token');
    console.log('Stored token:', storedToken ? 'Available' : 'Not available');
    
    // Check if we're in demo mode and should skip it
    const autoDemo = localStorage.getItem('auto_demo_mode');
    console.log('Auto demo mode:', autoDemo);
    
    if (storedToken && storedToken !== 'demo-token') {
      console.log('Found real GitHub token, validating...');
      setToken(storedToken);
      validateToken(storedToken);
    } else if (storedToken === 'demo-token') {
      console.log('Demo token found, checking if we should use it');
      // Only use demo token if auto demo is explicitly enabled
      if (autoDemo === 'true') {
        console.log('Auto demo enabled, using demo mode');
        loginDemo();
      } else {
        console.log('Auto demo not enabled, clearing demo token');
        localStorage.removeItem('beetle_token');
        setLoading(false);
      }
    } else {
      console.log('No valid token found');
      setLoading(false);
    }
  }, []);

  const validateToken = async (authToken?: string) => {
    try {
      const tokenToUse = authToken || token;
      console.log('Validating token:', tokenToUse ? 'Available' : 'Not available');
      
      if (!tokenToUse) {
        console.log('No token to validate');
        setIsAuthenticated(false);
        setUser(null);
        setLoading(false);
        return false;
      }

      console.log('Making validation request to:', `${API_BASE_URL}/auth/validate`);
      const response = await fetch(`${API_BASE_URL}/auth/validate`, {
        headers: {
          'Authorization': `Bearer ${tokenToUse}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('Validation response status:', response.status);
      console.log('Validation response ok:', response.ok);

      if (response.ok) {
        const data = await response.json();
        console.log('Validation successful, user data:', data.user);
        setIsAuthenticated(true);
        setUser(data.user);
        setToken(tokenToUse);
        localStorage.setItem('beetle_token', tokenToUse);
        setLoading(false);
        return true;
      } else {
        console.log('Token validation failed');
        const errorText = await response.text();
        console.error('Validation error response:', errorText);
        // Token is invalid, clear everything
        setIsAuthenticated(false);
        setUser(null);
        setToken(null);
        localStorage.removeItem('beetle_token');
        setLoading(false);
        return false;
      }
    } catch (error) {
      console.error('Token validation error:', error);
      setIsAuthenticated(false);
      setUser(null);
      setToken(null);
      localStorage.removeItem('beetle_token');
      setLoading(false);
      return false;
    }
  };

  // Function to set user data from OAuth callback
  const setUserFromCallback = (userData: User, authToken: string) => {
    setUser(userData);
    setToken(authToken);
    setIsAuthenticated(true);
    localStorage.setItem('beetle_token', authToken);
    setLoading(false);
  };

  const login = async () => {
    try {
      console.log('Starting GitHub login flow');
      console.log('Getting GitHub OAuth URL from:', `${API_BASE_URL}/auth/github/url`);
      
      // Get GitHub OAuth URL from backend
      const response = await fetch(`${API_BASE_URL}/auth/github/url`);
      
      if (!response.ok) {
        console.error('Failed to get GitHub OAuth URL:', response.status, response.statusText);
        throw new Error(`Failed to get GitHub OAuth URL: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Received GitHub OAuth URL:', data.auth_url);
      
      // Disable auto demo mode
      localStorage.removeItem('auto_demo_mode');
      
      // Redirect to GitHub OAuth
      window.location.href = data.auth_url;
    } catch (error) {
      console.error('Login error:', error);
      alert('Failed to connect to GitHub. Please check the console for more details.');
      
      // Only fallback to demo mode in development
      if (process.env.NODE_ENV === 'development') {
        console.log('Using mock login for development due to error');
        loginDemo();
      } else {
        setLoading(false);
      }
    }
  };

  // Demo mode login function
  const loginDemo = () => {
    console.log('Logging in with demo mode');
    console.log('✅ Demo authentication successful');
    setIsAuthenticated(true);
    setUser({
      id: 1,
      login: 'demo-user',
      name: 'Demo User',
      email: 'demo@example.com',
      avatar_url: 'https://github.com/github.png',
      bio: 'Demo user for development',
      location: 'Demo City',
      company: 'Demo Corp',
      blog: 'https://demo.com',
      twitter_username: 'demo',
      public_repos: 2,
      followers: 50,
      following: 25,
      created_at: '2023-01-01T00:00:00Z',
      lastLogin: new Date().toISOString(),
      analytics: {
        totalCommits: 45,
        totalPRs: 2,
        totalIssues: 3,
        activeRepositories: 2
      }
    });
    setToken('demo-token');
    localStorage.setItem('beetle_token', 'demo-token');
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('auto_demo_mode', 'true'); // Enable auto demo mode
  };

  const logout = async () => {
    try {
      if (token) {
        // Call backend logout endpoint
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local state regardless of backend response
      setIsAuthenticated(false);
      setUser(null);
      setToken(null);
      localStorage.removeItem('beetle_token');
      localStorage.removeItem('isAuthenticated');
    }
  };

  // Force logout and clear all demo mode settings
  const forceLogout = () => {
    console.log('Force logout - clearing all data including demo mode');
    setIsAuthenticated(false);
    setUser(null);
    setToken(null);
    localStorage.removeItem('beetle_token');
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('auto_demo_mode');
    setLoading(false);
  };

  // Enable auto demo mode for development
  const enableAutoDemo = () => {
    localStorage.setItem('auto_demo_mode', 'true');
    console.log('Auto demo mode enabled');
  };

  // Disable auto demo mode
  const disableAutoDemo = () => {
    localStorage.removeItem('auto_demo_mode');
    console.log('Auto demo mode disabled');
  };

  // OAuth callback is now handled by the dedicated callback page

  return (
    <AuthContext.Provider value={{ 
      isAuthenticated, 
      user, 
      token, 
      login, 
      loginDemo,
      logout, 
      forceLogout,
      validateToken,
      setUserFromCallback,
      enableAutoDemo,
      disableAutoDemo,
      loading 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

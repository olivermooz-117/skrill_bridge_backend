import { useState, useEffect, useContext, createContext } from 'react';
import { authService } from '../services/auth';

// Create Auth Context
const AuthContext = createContext(null);

// Auth Provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    setLoading(true);
    try {
      // Check if we have a stored user
      const storedUser = authService.getStoredUser();
      const token = localStorage.getItem('access_token');
      
      if (token && storedUser) {
        setUser(storedUser);
      } else if (token) {
        // If we have token but no user, fetch user
        const result = await authService.getCurrentUser();
        if (result.success) {
          setUser(result.user);
          authService.storeUser(result.user);
        } else {
          // Token might be invalid
          authService.logout();
          setUser(null);
        }
      } else {
        setUser(null);
      }
    } catch (err) {
      console.error('Auth check error:', err);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  // Register function
  const register = async (userData) => {
    setError(null);
    setLoading(true);
    
    try {
      const result = await authService.register(userData);
      if (result.success) {
        // Store token and user
        localStorage.setItem('access_token', result.accessToken);
        setUser(result.user);
        authService.storeUser(result.user);
        return { success: true, user: result.user };
      } else {
        setError(result.error);
        return { success: false, error: result.error };
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Registration failed';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  };

  // Login function
  const login = async (email, password) => {
    setError(null);
    setLoading(true);
    
    try {
      const result = await authService.login(email, password);
      if (result.success) {
        // Store token and user
        localStorage.setItem('access_token', result.accessToken);
        setUser(result.user);
        authService.storeUser(result.user);
        return { success: true, user: result.user };
      } else {
        setError(result.error);
        return { success: false, error: result.error };
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Login failed';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    authService.logout();
    setUser(null);
  };

  // Reset password request
  const requestPasswordReset = async (email) => {
    setError(null);
    try {
      const result = await authService.requestPasswordReset(email);
      return result;
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Failed to send reset link';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    }
  };

  // Confirm password reset
  const confirmPasswordReset = async (token, newPassword) => {
    setError(null);
    try {
      const result = await authService.confirmPasswordReset(token, newPassword);
      return result;
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Failed to reset password';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    }
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    requestPasswordReset,
    confirmPasswordReset,
    isAuthenticated: !!user,
    isFreelancer: user?.role === 'freelancer',
    isClient: user?.role === 'client',
    checkAuth
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export default useAuth;
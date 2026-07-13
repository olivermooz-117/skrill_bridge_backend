import api from './api';

// Authentication service
export const authService = {
  // Register a new user
  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData);
      return {
        success: true,
        user: response.data.user,
        accessToken: response.data.access_token
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Registration failed',
        status: error.response?.status
      };
    }
  },

  // Login user
  async login(email, password) {
    try {
      const response = await api.post('/auth/login', { email, password });
      return {
        success: true,
        user: response.data.user,
        accessToken: response.data.access_token
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed',
        status: error.response?.status
      };
    }
  },

  // Get current user
  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me');
      return {
        success: true,
        user: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to get user',
        status: error.response?.status
      };
    }
  },

  // Request password reset
  async requestPasswordReset(email) {
    try {
      const response = await api.post('/auth/password-reset/request', { email });
      return {
        success: true,
        message: response.data.message,
        resetLink: response.data.reset_link
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to send reset link'
      };
    }
  },

  // Confirm password reset
  async confirmPasswordReset(token, newPassword) {
    try {
      const response = await api.post('/auth/password-reset/confirm', {
        token,
        new_password: newPassword
      });
      return {
        success: true,
        message: response.data.message
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to reset password'
      };
    }
  },

  // Logout (clear local storage)
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  // Check if user is authenticated
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },

  // Get stored user
  getStoredUser() {
    try {
      const user = localStorage.getItem('user');
      return user ? JSON.parse(user) : null;
    } catch {
      return null;
    }
  },

  // Store user data
  storeUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
  }
};

export default authService;
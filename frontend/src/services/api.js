import axios from 'axios';

// API base URL - HARDCODED for Render
const API_BASE = 'https://hr-comply360-statutory-compliance-suite-2.onrender.com/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============ FIX: Add token to EVERY request ============
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = localStorage.getItem('access_token');
    
    // ALWAYS add token if it exists
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('✅ Token added to:', config.url);
    } else {
      console.log('❌ NO token for:', config.url);
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request error:', error);
    return Promise.reject(error);
  }
);

// ============ Response interceptor ============
api.interceptors.response.use(
  (response) => {
    console.log('✅ Response:', response.config.url, response.status);
    return response;
  },
  (error) => {
    console.error('❌ Error:', error.response?.status, error.response?.data);
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============ AUTH APIs ============
export const authAPI = {
  login: (email, password) => {
    console.log('🔐 Login:', email);
    return api.post('/auth/login', { email, password });
  },
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },
};

// ============ COMPLIANCE APIs ============
export const complianceAPI = {
  getStats: () => {
    console.log('📊 Fetching stats...');
    return api.get('/compliance/stats');
  },
  getAll: (params) => {
    console.log('📋 Fetching compliance list...');
    return api.get('/compliance', { params });
  },
  getById: (id) => api.get(`/compliance/${id}`),
  create: (data) => api.post('/compliance', data),
  update: (id, data) => api.put(`/compliance/${id}`, data),
  delete: (id) => api.delete(`/compliance/${id}`),
};

// ============ NOTIFICATION APIs ============
export const notificationAPI = {
  getUnreadCount: () => {
    console.log('🔔 Fetching unread count...');
    return api.get('/notifications/unread-count');
  },
  getAll: () => api.get('/notifications'),
  markRead: (id) => api.put(`/notifications/${id}/read`),
  markAllRead: () => api.put('/notifications/read-all'),
};

// ============ UPLOAD APIs ============
export const uploadAPI = {
  uploadExcel: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload/excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export default api;
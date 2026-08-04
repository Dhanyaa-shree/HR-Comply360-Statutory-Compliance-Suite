import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { authAPI } from '../services/api';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  // If already logged in, redirect to dashboard
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      navigate('/app/dashboard');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      console.log('🔐 Logging in...');
      const response = await authAPI.login(email, password);
      const { access_token, user } = response.data;
      
      console.log('✅ Login successful!');
      
      // Store token
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Verify token is stored
      const storedToken = localStorage.getItem('access_token');
      console.log('💾 Token stored:', storedToken ? 'Yes' : 'No');
      console.log('💾 Token length:', storedToken?.length);
      
      toast.success('Login successful!');
      
      // ✅ FIX: Redirect to /app/dashboard instead of /dashboard
      navigate('/app/dashboard');
    } catch (error) {
      console.error('❌ Login error:', error);
      toast.error(error.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="card shadow-lg" style={{ maxWidth: '400px', width: '100%' }}>
        <div className="card-body p-5">
          <div className="text-center mb-4">
            <h2 className="fw-bold text-primary">HR Comply360</h2>
            <p className="text-muted">Centralized HR Compliance Portal</p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label">Email Address</label>
              <input
                type="email"
                className="form-control"
                placeholder="hr@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-control"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary w-100 py-2"
              disabled={loading}
            >
              {loading ? (
                <span className="spinner-border spinner-border-sm me-2" role="status" />
              ) : null}
              {loading ? 'Loading...' : 'Sign In'}
            </button>
          </form>

          <div className="text-center mt-3">
            <small className="text-muted">
              Default: hr@company.com / password123
            </small>
          </div>
          
          <div className="text-center mt-3">
            <small>
              <a href="/" className="text-decoration-none">← Back to Home</a>
            </small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { 
  FaTachometerAlt, FaList, FaUpload, FaCalendarAlt, 
  FaChartBar, FaFolderOpen, FaBell, FaCog, FaSignOutAlt,
  FaBars, FaTimes
} from 'react-icons/fa';
import { notificationAPI } from '../services/api';

const Layout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const [user, setUser] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    try {
      const userData = localStorage.getItem('user');
      if (userData) {
        setUser(JSON.parse(userData));
      }
    } catch (error) {
      console.error('Error parsing user data:', error);
    }
    fetchUnreadCount();
  }, []);

  const fetchUnreadCount = async () => {
    try {
      const response = await notificationAPI.getUnreadCount();
      if (response && response.data) {
        setUnreadCount(response.data.unread_count || 0);
      }
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
      setUnreadCount(0);
    }
  };

  const menuItems = [
    { path: '/app/dashboard', icon: FaTachometerAlt, label: 'Dashboard' },
    { path: '/app/compliance', icon: FaList, label: 'Compliance' },
    { path: '/app/import', icon: FaUpload, label: 'Import Excel' },
    { path: '/app/calendar', icon: FaCalendarAlt, label: 'Calendar' },
    { path: '/app/analytics', icon: FaChartBar, label: 'Analytics' },
    { path: '/app/documents', icon: FaFolderOpen, label: 'Documents' },
    { path: '/app/notifications', icon: FaBell, label: 'Notifications', badge: unreadCount },
    { path: '/app/settings', icon: FaCog, label: 'Settings' },
  ];

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  const sidebarStyle = {
    background: 'linear-gradient(180deg, #1a1a2e 0%, #16213e 100%)',
    width: '260px', 
    minHeight: '100vh',
    position: 'fixed',
    left: 0,
    top: 0,
    zIndex: 999,
    overflowY: 'auto'
  };

  const navLinkStyle = {
    color: '#c8d6e5',
    padding: '12px 16px',
    borderRadius: '8px',
    transition: 'all 0.3s ease',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    textDecoration: 'none',
    border: 'none',
    background: 'transparent',
    width: '100%',
    fontSize: '14px',
    position: 'relative'
  };

  const activeNavLinkStyle = {
    ...navLinkStyle,
    background: '#2563EB',
    color: '#ffffff'
  };

  return (
    <div className="d-flex" style={{ minHeight: '100vh', background: '#E8FFFF' }}>
      {/* Mobile Toggle */}
      <button 
        className="btn btn-primary d-lg-none position-fixed" 
        style={{ 
          top: '10px', 
          left: '10px', 
          zIndex: 1000,
          background: '#2563EB',
          border: 'none'
        }}
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        {sidebarOpen ? <FaTimes /> : <FaBars />}
      </button>

      {/* Sidebar */}
      <div 
        className={`sidebar ${sidebarOpen ? 'd-block' : 'd-none d-lg-block'}`}
        style={sidebarStyle}
      >
        <div className="p-4">
          <h4 className="text-white">HR Comply360</h4>
          <small style={{ color: '#c8d6e5' }}>Compliance Portal</small>
        </div>
        <hr className="mx-3" style={{ borderColor: 'rgba(255,255,255,0.1)' }} />
        <nav className="nav flex-column px-3">
          {menuItems.map((item) => (
            <button
              key={item.path}
              style={isActive(item.path) ? activeNavLinkStyle : navLinkStyle}
              onClick={() => navigate(item.path)}
              className="mb-1"
            >
              <item.icon />
              {item.label}
              {item.badge > 0 && (
                <span className="badge bg-danger rounded-pill ms-auto">
                  {item.badge}
                </span>
              )}
            </button>
          ))}
        </nav>
        <hr className="mx-3" style={{ borderColor: 'rgba(255,255,255,0.1)' }} />
        <div className="px-3">
          <div className="d-flex align-items-center gap-3 mb-3">
            <div 
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: '#2563EB',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontSize: '18px',
                fontWeight: 'bold'
              }}
            >
              {user?.name?.charAt(0) || 'H'}
            </div>
            <div>
              <div style={{ color: '#fff', fontSize: '14px' }}>{user?.name || 'HR User'}</div>
              <div style={{ color: '#c8d6e5', fontSize: '12px' }}>{user?.email || ''}</div>
            </div>
          </div>
          <button
            className="btn w-100"
            style={{
              background: 'rgba(255,255,255,0.1)',
              color: '#fff',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '8px',
              padding: '10px',
              transition: 'all 0.3s ease'
            }}
            onClick={handleLogout}
            onMouseEnter={(e) => e.target.style.background = 'rgba(255,255,255,0.2)'}
            onMouseLeave={(e) => e.target.style.background = 'rgba(255,255,255,0.1)'}
          >
            <FaSignOutAlt className="me-2" />
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div 
        className="flex-grow-1 p-4"
        style={{ 
          marginLeft: sidebarOpen ? '260px' : '0',
          transition: 'margin-left 0.3s ease',
          background: '#E8FFFF',
          minHeight: '100vh'
        }}
      >
        <Outlet />
      </div>
    </div>
  );
};

export default Layout;
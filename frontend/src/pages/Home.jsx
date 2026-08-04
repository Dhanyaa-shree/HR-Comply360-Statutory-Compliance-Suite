import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FaShieldAlt, 
  FaBell, 
  FaCalendarCheck, 
  FaChartLine,
  FaFileAlt,
  FaUsers,
  FaRocket,
  FaArrowRight,
  FaCheckCircle,
  FaClock,
  FaExclamationTriangle,
  FaInfinity,
  FaUserCheck,
  FaBolt
} from 'react-icons/fa';
import './Home.css';

const Home = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: FaShieldAlt,
      title: 'Statutory Compliance',
      description: 'Track and manage all statutory compliance requirements in one place'
    },
    {
      icon: FaBell,
      title: 'Smart Reminders',
      description: 'Get automated reminders before deadlines with customizable alerts'
    },
    {
      icon: FaCalendarCheck,
      title: 'Deadline Management',
      description: 'Never miss a deadline with our intelligent calendar system'
    },
    {
      icon: FaChartLine,
      title: 'Analytics & Reports',
      description: 'Visual insights and reports to track compliance performance'
    },
    {
      icon: FaFileAlt,
      title: 'Document Management',
      description: 'Store and manage all compliance documents securely'
    },
    {
      icon: FaUsers,
      title: 'Team Collaboration',
      description: 'Work together with your team on compliance tasks'
    }
  ];

  const stats = [
    { value: '98%', label: 'Compliance Rate', icon: FaCheckCircle, color: '#10B981' },
    { value: '500+', label: 'Compliance Tracked', icon: FaFileAlt, color: '#3B82F6' },
    { value: '24/7', label: 'Real-time Monitoring', icon: FaClock, color: '#F59E0B' },
    { value: '99.9%', label: 'On-time Delivery', icon: FaExclamationTriangle, color: '#EF4444' }
  ];

  return (
    <div className="home-container">
      {/* Animated Background */}
      <div className="bg-animation">
        <div className="orb orb1"></div>
        <div className="orb orb2"></div>
        <div className="orb orb3"></div>
      </div>

      {/* Navigation */}
      <nav className="glass-nav">
        <div className="nav-content">
          <div className="logo">
            <FaShieldAlt className="logo-icon" />
            <span>HR Comply360</span>
          </div>
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#stats">Stats</a>
            <a href="#about">About</a>
            <button 
              className="btn-login"
              onClick={() => navigate('/login')}
            >
              Sign In
            </button>
            <button 
              className="btn-get-started"
              onClick={() => navigate('/login')}
            >
              Get Started
              <FaArrowRight />
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <FaRocket className="badge-icon" />
            <span>Version 2.0 Released</span>
          </div>
          
          <h1 className="hero-title">
            {/* ✅ Removed dots from STAY AHEAD and STAY COMPLIANT */}
            <span className="hero-title-main">STAY AHEAD</span>
            <span className="hero-title-highlight">STAY COMPLIANT</span>
          </h1>
          
          {/* ✅ Made this bold with strong tag */}
          <p className="hero-subtitle-text">
            <strong>HR Comply360 - Statutory Compliance Suite</strong>
          </p>
          
          <p className="hero-description">
            Centralize, track, and manage all your statutory compliance requirements 
            with automated reminders and real-time insights. Never miss a deadline again.
          </p>
          
          <div className="hero-actions">
            <button 
              className="btn-primary-hero"
              onClick={() => navigate('/login')}
            >
              Start Free Trial
              <FaArrowRight />
            </button>
            <span className="stay-ahead-text">STAY AHEAD</span>
          </div>
          
          <div className="hero-trust">
            <span>
              <FaInfinity className="trust-icon" style={{ color: '#10B981' }} />
              Free forever
            </span>
            <span>
              <FaUserCheck className="trust-icon" style={{ color: '#3B82F6' }} />
              No credit card
            </span>
            <span>
              <FaBolt className="trust-icon" style={{ color: '#8B5CF6' }} />
              Intelligent Alerts
            </span>
          </div>
        </div>
        
        <div className="hero-visual">
          <div className="glass-card-hero">
            <div className="hero-stats-preview">
              <div className="stat-item">
                <span className="stat-value">98%</span>
                <span className="stat-label">Compliance Rate</span>
              </div>
              <div className="stat-divider"></div>
              <div className="stat-item">
                <span className="stat-value">12</span>
                <span className="stat-label">Active Deadlines</span>
              </div>
              <div className="stat-divider"></div>
              <div className="stat-item">
                <span className="stat-value">5</span>
                <span className="stat-label">Overdue</span>
              </div>
            </div>
            <div className="hero-reminder-preview">
              <div className="reminder-item">
                <FaBell className="reminder-icon" />
                <div>
                  <p className="reminder-title">EPF Payment Due</p>
                  <p className="reminder-date">In 3 days</p>
                </div>
              </div>
              <div className="reminder-item">
                <FaBell className="reminder-icon" />
                <div>
                  <p className="reminder-title">Factory License Renewal</p>
                  <p className="reminder-date">In 7 days</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section" id="stats">
        <div className="stats-grid">
          {stats.map((stat, index) => (
            <div key={index} className="stat-card glass">
              <stat.icon className="stat-icon" style={{ color: stat.color }} />
              <div className="stat-value">{stat.value}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section" id="features">
        <div className="section-header">
          <h2>Everything You Need</h2>
          <p>Complete compliance management solution for modern businesses</p>
        </div>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card glass">
              <div className="feature-icon-wrapper">
                <feature.icon className="feature-icon" />
              </div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content glass">
          <h2>Ready to Simplify Compliance?</h2>
          <p>Join thousands of businesses using HR Comply360 to manage their compliance</p>
          <button 
            className="btn-cta"
            onClick={() => navigate('/login')}
          >
            Get Started Now
            <FaArrowRight />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-logo">
            <FaShieldAlt className="footer-logo-icon" />
            <span>HR Comply360</span>
          </div>
          <p className="footer-text">
            © 2026 HR Comply360. All rights reserved.
          </p>
          <div className="footer-links">
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Support</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;
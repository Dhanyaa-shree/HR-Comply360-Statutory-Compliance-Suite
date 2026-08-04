import React, { useState, useEffect, useRef } from 'react';
import { FaUser, FaEnvelope, FaLock, FaCamera, FaSave, FaTimes } from 'react-icons/fa';
import { toast } from 'react-toastify';

const Settings = () => {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('user') || '{}');
    } catch {
      return {};
    }
  });

  const [formData, setFormData] = useState({
    name: '',
    email: '',
  });
  const [profileImage, setProfileImage] = useState(null);
  const [profileImagePreview, setProfileImagePreview] = useState(null);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        email: user.email || '',
      });
    }
  }, [user]);

  // Handle profile update (name & email)
  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    try {
      // Update user in localStorage
      const updatedUser = { ...user, name: formData.name, email: formData.email };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      setUser(updatedUser);
      setIsEditing(false);
      toast.success('Profile updated successfully!');
    } catch (error) {
      toast.error('Failed to update profile');
    }
  };

  // Handle profile picture upload
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast.error('Please select an image file');
        return;
      }
      // Validate file size (max 2MB)
      if (file.size > 2 * 1024 * 1024) {
        toast.error('Image size should be less than 2MB');
        return;
      }
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfileImagePreview(reader.result);
        // Save to localStorage
        try {
          const updatedUser = { ...user, avatar: reader.result };
          localStorage.setItem('user', JSON.stringify(updatedUser));
          setUser(updatedUser);
          toast.success('Profile picture updated!');
        } catch (error) {
          toast.error('Failed to save profile picture');
        }
      };
      reader.readAsDataURL(file);
    }
  };

  // Handle password change
  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    if (newPassword.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }
    if (!currentPassword) {
      toast.error('Please enter current password');
      return;
    }
    
    try {
      // In a real app, call API to change password
      toast.success('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error) {
      toast.error('Failed to change password');
    }
  };

  const handleCancelEdit = () => {
    setFormData({
      name: user.name || '',
      email: user.email || '',
    });
    setIsEditing(false);
  };

  const getInitials = () => {
    if (user?.name) {
      return user.name.charAt(0).toUpperCase();
    }
    return 'H';
  };

  return (
    <div className="fade-in">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h4 style={{ color: '#1A1A2E', marginBottom: '2px' }}>Settings</h4>
          <small style={{ color: '#4B5563' }}>Manage your account settings</small>
        </div>
      </div>

      <div className="row g-3">
        {/* Profile Picture & Basic Info - Compact Row */}
        <div className="col-12">
          <div className="card dashboard-card">
            <div className="card-body p-3">
              <div className="row align-items-center">
                {/* Profile Picture */}
                <div className="col-md-2 text-center">
                  <div 
                    className="position-relative d-inline-block"
                    style={{ cursor: 'pointer' }}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    {profileImagePreview || user?.avatar ? (
                      <img
                        src={profileImagePreview || user?.avatar}
                        alt="Profile"
                        style={{
                          width: '80px',
                          height: '80px',
                          borderRadius: '50%',
                          objectFit: 'cover',
                          border: '3px solid #2563EB'
                        }}
                      />
                    ) : (
                      <div
                        style={{
                          width: '80px',
                          height: '80px',
                          borderRadius: '50%',
                          background: '#2563EB',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '32px',
                          color: '#fff',
                          fontWeight: 'bold',
                          border: '3px solid #2563EB'
                        }}
                      >
                        {getInitials()}
                      </div>
                    )}
                    <div
                      style={{
                        position: 'absolute',
                        bottom: '0',
                        right: '0',
                        background: '#2563EB',
                        borderRadius: '50%',
                        padding: '6px',
                        border: '2px solid #fff'
                      }}
                    >
                      <FaCamera size={12} color="#fff" />
                    </div>
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    style={{ display: 'none' }}
                    onChange={handleImageUpload}
                  />
                  <small style={{ color: '#4B5563', display: 'block', marginTop: '4px' }}>Click to change photo</small>
                </div>

                {/* Name & Email - Compact */}
                <div className="col-md-8">
                  {isEditing ? (
                    <form onSubmit={handleProfileUpdate}>
                      <div className="row g-2">
                        <div className="col-md-6">
                          <label className="form-label small" style={{ color: '#4B5563', marginBottom: '2px' }}>Full Name</label>
                          <input
                            type="text"
                            className="form-control form-control-sm"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            required
                          />
                        </div>
                        <div className="col-md-6">
                          <label className="form-label small" style={{ color: '#4B5563', marginBottom: '2px' }}>Email Address</label>
                          <input
                            type="email"
                            className="form-control form-control-sm"
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            required
                          />
                        </div>
                        <div className="col-12">
                          <button type="submit" className="btn btn-primary btn-sm me-2">
                            <FaSave className="me-1" size={12} /> Save
                          </button>
                          <button type="button" className="btn btn-secondary btn-sm" onClick={handleCancelEdit}>
                            <FaTimes className="me-1" size={12} /> Cancel
                          </button>
                        </div>
                      </div>
                    </form>
                  ) : (
                    <div className="row">
                      <div className="col-md-6">
                        <label className="form-label small" style={{ color: '#4B5563', marginBottom: '2px' }}>Full Name</label>
                        <p className="fw-bold" style={{ color: '#1A1A2E', marginBottom: '4px' }}>{user?.name || 'HR Admin'}</p>
                      </div>
                      <div className="col-md-6">
                        <label className="form-label small" style={{ color: '#4B5563', marginBottom: '2px' }}>Email Address</label>
                        <p className="fw-bold" style={{ color: '#1A1A2E', marginBottom: '4px' }}>{user?.email || 'hr@company.com'}</p>
                      </div>
                      <div className="col-12 mt-1">
                        <button className="btn btn-outline-primary btn-sm" onClick={() => setIsEditing(true)}>
                          <FaUser className="me-1" size={12} /> Edit Profile
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Role Badge - Compact */}
                <div className="col-md-2 text-end">
                  <span className="badge" style={{ background: '#E8FFFF', color: '#2563EB', padding: '6px 12px' }}>
                    HR Administrator
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Change Password - Compact */}
        <div className="col-md-6">
          <div className="card dashboard-card h-100">
            <div className="card-body p-3">
              <h6 className="card-title mb-2" style={{ color: '#1A1A2E' }}>
                <FaLock className="me-2" style={{ color: '#4F46E5' }} size={14} />
                Change Password
              </h6>
              <hr className="my-2" />
              <form onSubmit={handlePasswordChange}>
                <div className="mb-2">
                  <label className="form-label small" style={{ color: '#4B5563', marginBottom: '2px' }}>Current Password</label>
                  <input
                    type="password"
                    className="form-control form-control-sm"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    required
                  />
                </div>
                <div className="row g-2">
                  <div className="col-6">
                    <label className="form-label small" style={{ color: '#4B5563', marginBottom: '2px' }}>New Password</label>
                    <input
                      type="password"
                      className="form-control form-control-sm"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      required
                    />
                  </div>
                  <div className="col-6">
                    <label className="form-label small" style={{ color: '#4B5563', marginBottom: '2px' }}>Confirm Password</label>
                    <input
                      type="password"
                      className="form-control form-control-sm"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>
                <button type="submit" className="btn btn-primary btn-sm mt-2">
                  <FaLock className="me-1" size={12} /> Update Password
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Account Info - Compact */}
        <div className="col-md-6">
          <div className="card dashboard-card h-100">
            <div className="card-body p-3">
              <h6 className="card-title mb-2" style={{ color: '#1A1A2E' }}>
                <FaUser className="me-2" style={{ color: '#2563EB' }} size={14} />
                Account Information
              </h6>
              <hr className="my-2" />
              <div className="row g-2">
                <div className="col-6">
                  <label className="form-label small" style={{ color: '#4B5563', marginBottom: '2px' }}>User ID</label>
                  <p className="fw-bold" style={{ color: '#1A1A2E', marginBottom: '4px', fontSize: '14px' }}>#{user?.id || '001'}</p>
                </div>
                <div className="col-6">
                  <label className="form-label small" style={{ color: '#4B5563', marginBottom: '2px' }}>Role</label>
                  <p className="fw-bold" style={{ color: '#1A1A2E', marginBottom: '4px', fontSize: '14px' }}>HR Administrator</p>
                </div>
                <div className="col-6">
                  <label className="form-label small" style={{ color: '#4B5563', marginBottom: '2px' }}>Member Since</label>
                  <p className="fw-bold" style={{ color: '#1A1A2E', marginBottom: '4px', fontSize: '14px' }}>{new Date().toLocaleDateString()}</p>
                </div>
                <div className="col-6">
                  <label className="form-label small" style={{ color: '#4B5563', marginBottom: '2px' }}>Status</label>
                  <p className="fw-bold" style={{ color: '#10B981', marginBottom: '4px', fontSize: '14px' }}>Active</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .form-control-sm {
          font-size: 13px;
          padding: 4px 10px;
          height: 32px;
        }
        .btn-sm {
          font-size: 13px;
          padding: 4px 12px;
        }
        .card-body {
          padding: 12px 16px !important;
        }
        .card {
          border-radius: 10px !important;
        }
        hr {
          margin: 6px 0 !important;
        }
        .form-label {
          font-size: 12px !important;
        }
      `}</style>
    </div>
  );
};

export default Settings;
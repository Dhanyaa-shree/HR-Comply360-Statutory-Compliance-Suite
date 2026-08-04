import React, { useState, useEffect } from 'react';
import { FaBell, FaCheck, FaTimes, FaCircle } from 'react-icons/fa';
import { notificationAPI } from '../services/api';
import { toast } from 'react-toastify';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await notificationAPI.getAll();
      setNotifications(response.data);
    } catch (error) {
      toast.error('Failed to fetch notifications');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkRead = async (id) => {
    try {
      await notificationAPI.markRead(id);
      setNotifications(notifications.map(n => 
        n.id === id ? { ...n, is_read: true } : n
      ));
    } catch (error) {
      toast.error('Failed to mark notification as read');
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationAPI.markAllRead();
      setNotifications(notifications.map(n => ({ ...n, is_read: true })));
      toast.success('All notifications marked as read');
    } catch (error) {
      toast.error('Failed to mark all as read');
    }
  };

  const getTypeIcon = (type) => {
    switch(type) {
      case 'Reminder': return '🔔';
      case 'Overdue': return '⚠️';
      case 'Complete': return '✅';
      default: return '📋';
    }
  };

  return (
    <div className="fade-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2>Notifications</h2>
          <p className="text-muted">Stay updated with compliance alerts</p>
        </div>
        <button 
          className="btn btn-outline-primary"
          onClick={handleMarkAllRead}
        >
          <FaCheck className="me-2" />
          Mark All Read
        </button>
      </div>

      <div className="card dashboard-card">
        <div className="card-body">
          {loading ? (
            <div className="text-center py-4">
              <div className="spinner-border text-primary" role="status" />
            </div>
          ) : notifications.length === 0 ? (
            <div className="text-center py-4 text-muted">
              <FaBell size={48} className="mb-3 text-muted" />
              <p>No notifications</p>
            </div>
          ) : (
            notifications.map((notification) => (
              <div 
                key={notification.id}
                className={`p-3 border-bottom ${!notification.is_read ? 'bg-light' : ''}`}
              >
                <div className="d-flex align-items-start gap-3">
                  <div className="mt-1">
                    <span style={{ fontSize: '20px' }}>
                      {getTypeIcon(notification.type)}
                    </span>
                  </div>
                  <div className="flex-grow-1">
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 className="mb-1">{notification.title}</h6>
                        <p className="mb-1 text-muted small">{notification.message}</p>
                        <small className="text-muted">
                          {new Date(notification.created_at).toLocaleString()}
                        </small>
                      </div>
                      <div className="d-flex gap-2">
                        {!notification.is_read && (
                          <button
                            className="btn btn-sm btn-outline-primary"
                            onClick={() => handleMarkRead(notification.id)}
                          >
                            <FaCheck size={12} />
                          </button>
                        )}
                        {notification.is_read && (
                          <span className="text-muted small">Read</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Notifications;
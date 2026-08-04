import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import { complianceAPI } from '../services/api';
import { FaArrowLeft, FaEdit, FaTrash } from 'react-icons/fa';

const ComplianceView = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [compliance, setCompliance] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCompliance();
  }, [id]);

  const fetchCompliance = async () => {
    try {
      setLoading(true);
      console.log('👁️ Fetching compliance details for ID:', id);
      const response = await complianceAPI.getById(id);
      console.log('📋 Response:', response.data);
      setCompliance(response.data);
    } catch (error) {
      console.error('❌ Failed to fetch compliance:', error);
      toast.error('Failed to fetch compliance details');
      navigate('/app/compliance');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this compliance?')) return;
    
    try {
      await complianceAPI.delete(id);
      toast.success('Compliance deleted successfully');
      navigate('/app/compliance');
    } catch (error) {
      toast.error('Failed to delete compliance');
    }
  };

  const getStatusBadge = (status) => {
    const classes = {
      'Completed': 'badge-status-completed',
      'Ongoing': 'badge-status-ongoing',
      'Planned': 'badge-status-planned',
      'Overdue': 'badge-status-overdue'
    };
    return `badge-status ${classes[status] || ''}`;
  };

  const getPriorityBadge = (priority) => {
    const classes = {
      'High': 'badge-priority-high',
      'Medium': 'badge-priority-medium',
      'Low': 'badge-priority-low'
    };
    return `badge-priority ${classes[priority] || ''}`;
  };

  // ✅ Helper function to format date
  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (!compliance) {
    return (
      <div className="text-center py-5">
        <h5 className="text-muted">Compliance not found</h5>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <button 
            className="btn btn-outline-secondary me-2"
            onClick={() => navigate('/app/compliance')}
          >
            <FaArrowLeft className="me-2" />
            Back
          </button>
          <h2 className="d-inline">Compliance Details</h2>
        </div>
        <div className="d-flex gap-2">
          <button 
            className="btn btn-outline-primary"
            onClick={() => navigate(`/app/compliance/edit/${id}`)}
          >
            <FaEdit className="me-2" />
            Edit
          </button>
          <button 
            className="btn btn-outline-danger"
            onClick={handleDelete}
          >
            <FaTrash className="me-2" />
            Delete
          </button>
        </div>
      </div>

      <div className="card dashboard-card">
        <div className="card-body">
          <div className="row">
            <div className="col-md-6">
              <div className="mb-3">
                <label className="text-muted small">Authority</label>
                <p className="fw-bold fs-5">{compliance.authority}</p>
              </div>
              <div className="mb-3">
                <label className="text-muted small">Compliance Name</label>
                <p className="fw-bold fs-5">{compliance.compliance_name}</p>
              </div>
              <div className="mb-3">
                <label className="text-muted small">Category</label>
                <p className="fw-bold">{compliance.category}</p>
              </div>
              <div className="mb-3">
                <label className="text-muted small">Status</label>
                <p>
                  <span className={`badge ${getStatusBadge(compliance.status)}`}>
                    {compliance.status}
                  </span>
                </p>
              </div>
            </div>
            <div className="col-md-6">
              <div className="mb-3">
                <label className="text-muted small">Valid Date</label>
                <p className="fw-bold">{formatDate(compliance.valid_date)}</p>
              </div>
              
              {/* ✅ NEW: Reminder Dates Section */}
              <div className="mb-3">
                <label className="text-muted small">Reminder Schedule</label>
                <div className="mt-1">
                  {/* Reminder 1 */}
                  <div className="d-flex align-items-center gap-2 mb-1 p-1 rounded" style={{ background: '#f8f9fa' }}>
                    <span className="badge bg-primary" style={{ minWidth: '40px' }}>1st</span>
                    <span className="fw-bold flex-grow-1">
                      {compliance.reminder_1_date ? formatDate(compliance.reminder_1_date) : 'Not set'}
                    </span>
                    {compliance.reminder_1_sent ? (
                      <span className="badge bg-success">✓ Sent</span>
                    ) : (
                      compliance.reminder_1_date && (
                        <span className="badge bg-warning text-dark">Pending</span>
                      )
                    )}
                  </div>
                  
                  {/* Reminder 2 */}
                  <div className="d-flex align-items-center gap-2 mb-1 p-1 rounded" style={{ background: '#f8f9fa' }}>
                    <span className="badge bg-info" style={{ minWidth: '40px' }}>2nd</span>
                    <span className="fw-bold flex-grow-1">
                      {compliance.reminder_2_date ? formatDate(compliance.reminder_2_date) : 'Auto: 5 days before'}
                    </span>
                    {compliance.reminder_2_sent ? (
                      <span className="badge bg-success">✓ Sent</span>
                    ) : (
                      compliance.reminder_2_date && (
                        <span className="badge bg-warning text-dark">Pending</span>
                      )
                    )}
                  </div>
                  
                  {/* Reminder 3 */}
                  <div className="d-flex align-items-center gap-2 p-1 rounded" style={{ background: '#f8f9fa' }}>
                    <span className="badge bg-danger" style={{ minWidth: '40px' }}>3rd</span>
                    <span className="fw-bold flex-grow-1">
                      {compliance.reminder_3_date ? formatDate(compliance.reminder_3_date) : 'Auto: 2 days before'}
                    </span>
                    {compliance.reminder_3_sent ? (
                      <span className="badge bg-success">✓ Sent</span>
                    ) : (
                      compliance.reminder_3_date && (
                        <span className="badge bg-warning text-dark">Pending</span>
                      )
                    )}
                  </div>
                </div>
                <small className="text-muted">
                  Reminder 1: Manual | Reminder 2: 5 days before due | Reminder 3: 2 days before due
                </small>
              </div>

              <div className="mb-3">
                <label className="text-muted small">Submission Date</label>
                <p className="fw-bold">{compliance.submission_date ? formatDate(compliance.submission_date) : 'N/A'}</p>
              </div>
              <div className="mb-3">
                <label className="text-muted small">Priority</label>
                <p>
                  <span className={`badge ${getPriorityBadge(compliance.priority)}`}>
                    {compliance.priority}
                  </span>
                </p>
              </div>
              <div className="mb-3">
                <label className="text-muted small">Frequency</label>
                <p className="fw-bold">{compliance.frequency || 'OneTime'}</p>
              </div>
            </div>
          </div>
          
          {/* ✅ NEW: Reminder Info Alert */}
          <div className="alert alert-info mt-3 mb-0">
            <strong>📋 Reminder Info:</strong> 
            <ul className="mb-0 mt-1">
              <li><strong>Reminder 1:</strong> {compliance.reminder_1_date ? `Set for ${formatDate(compliance.reminder_1_date)}` : 'Not configured'}</li>
              <li><strong>Reminder 2:</strong> Automatically sent 5 days before due date</li>
              <li><strong>Reminder 3:</strong> Automatically sent 2 days before due date</li>
            </ul>
          </div>

          {compliance.remarks && (
            <div className="mt-3">
              <label className="text-muted small">Remarks</label>
              <p className="fw-bold">{compliance.remarks}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ComplianceView;
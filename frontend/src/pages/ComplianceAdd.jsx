import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { complianceAPI } from '../services/api';

const ComplianceAdd = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    authority: '',
    compliance_name: '',
    category: 'Labour Compliance',
    valid_date: '',
    submission_date: '',
    process_time: '',
    frequency: 'Monthly',
    reminder_days: '30,15,7,3,1',
    priority: 'Medium',
    status: 'Planned',
    remarks: '',
    reminder_1_date: ''  // ✅ NEW FIELD
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await complianceAPI.create(formData);
      toast.success('Compliance added successfully!');
      navigate('/app/compliance');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to add compliance');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2>Add New Compliance</h2>
          <p className="text-muted">Create a new compliance record</p>
        </div>
      </div>

      <div className="card dashboard-card">
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Authority *</label>
                <input
                  type="text"
                  className="form-control"
                  name="authority"
                  placeholder="e.g., EPFO, ESIC, DISH"
                  value={formData.authority}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">Compliance Name *</label>
                <input
                  type="text"
                  className="form-control"
                  name="compliance_name"
                  placeholder="e.g., EPF Payment Remittance"
                  value={formData.compliance_name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">Category *</label>
                <select
                  className="form-select"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  required
                >
                  <option value="Labour Compliance">Labour Compliance</option>
                  <option value="Insurance">Insurance</option>
                  <option value="Vehicle Compliance">Vehicle Compliance</option>
                  <option value="Factory Compliance">Factory Compliance</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">Frequency *</label>
                <select
                  className="form-select"
                  name="frequency"
                  value={formData.frequency}
                  onChange={handleChange}
                  required
                >
                  <option value="Monthly">Monthly</option>
                  <option value="Quarterly">Quarterly</option>
                  <option value="HalfYearly">HalfYearly</option>
                  <option value="Annual">Annual</option>
                  <option value="OneTime">OneTime</option>
                </select>
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">Valid Date *</label>
                <input
                  type="date"
                  className="form-control"
                  name="valid_date"
                  value={formData.valid_date}
                  onChange={handleChange}
                  required
                />
              </div>

              {/* ✅ NEW: First Notification Date Field */}
              <div className="col-md-6 mb-3">
                <label className="form-label">First Notification Date</label>
                <input
                  type="date"
                  className="form-control"
                  name="reminder_1_date"
                  value={formData.reminder_1_date}
                  onChange={handleChange}
                />
                <small className="text-muted">
                  Set the date for the first reminder. Reminder 2 will be 5 days before due date, Reminder 3 will be 2 days before due date.
                </small>
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">Submission Date</label>
                <input
                  type="date"
                  className="form-control"
                  name="submission_date"
                  value={formData.submission_date}
                  onChange={handleChange}
                />
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">Process Time</label>
                <input
                  type="text"
                  className="form-control"
                  name="process_time"
                  placeholder="e.g., 10 Days"
                  value={formData.process_time}
                  onChange={handleChange}
                />
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">Priority *</label>
                <select
                  className="form-select"
                  name="priority"
                  value={formData.priority}
                  onChange={handleChange}
                  required
                >
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">Status *</label>
                <select
                  className="form-select"
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  required
                >
                  <option value="Planned">Planned</option>
                  <option value="Ongoing">Ongoing</option>
                  <option value="Completed">Completed</option>
                  <option value="Overdue">Overdue</option>
                </select>
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">Reminder Days</label>
                <input
                  type="text"
                  className="form-control"
                  name="reminder_days"
                  placeholder="e.g., 30,15,7,3,1"
                  value={formData.reminder_days}
                  onChange={handleChange}
                />
                <small className="text-muted">Comma separated: 30,15,7,3,1</small>
              </div>

              <div className="col-12 mb-3">
                <label className="form-label">Remarks</label>
                <textarea
                  className="form-control"
                  name="remarks"
                  rows="3"
                  value={formData.remarks}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="d-flex gap-2">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Saving...' : 'Save Compliance'}
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate('/app/compliance')}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ComplianceAdd;
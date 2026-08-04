import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FaPlus, FaSearch, FaEdit, FaTrash, FaEye } from 'react-icons/fa';
import { complianceAPI } from '../services/api';

const Compliance = () => {
  const navigate = useNavigate();
  const [compliance, setCompliance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchCompliance();
  }, [page, search]);

  const fetchCompliance = async () => {
    try {
      setLoading(true);
      const response = await complianceAPI.getAll({ page, search });
      setCompliance(response.data.data || []);
      setTotalPages(response.data.pagination?.pages || 1);
    } catch (error) {
      console.error('Failed to fetch compliance:', error);
      toast.error('Failed to fetch compliance data');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this compliance?')) return;
    
    try {
      await complianceAPI.delete(id);
      toast.success('Compliance deleted successfully');
      fetchCompliance();
    } catch (error) {
      toast.error('Failed to delete compliance');
    }
  };

  // ✅ FIXED: Added /app/ prefix to all navigation paths
  const handleView = (id) => {
    navigate(`/app/compliance/${id}`);
  };

  const handleEdit = (id) => {
    navigate(`/app/compliance/edit/${id}`);
  };

  const handleAdd = () => {
    navigate('/app/compliance/add');
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

  return (
    <div className="fade-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2>Compliance Management</h2>
          <p className="text-muted">Manage all compliance records</p>
        </div>
        <button 
          className="btn btn-primary"
          onClick={handleAdd}  // ✅ Using the fixed function
        >
          <FaPlus className="me-2" />
          Add Compliance
        </button>
      </div>

      <div className="card dashboard-card">
        <div className="card-body">
          <div className="mb-3">
            <div className="input-group">
              <span className="input-group-text bg-white border-end-0">
                <FaSearch className="text-muted" />
              </span>
              <input
                type="text"
                className="form-control border-start-0"
                placeholder="Search compliance..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>

          {loading ? (
            <div className="text-center py-4">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          ) : (
            <>
              <div className="table-responsive">
                <table className="table table-hover">
                  <thead>
                    <tr>
                      <th>Authority</th>
                      <th>Compliance Name</th>
                      <th>Valid Date</th>
                      <th>Status</th>
                      <th>Priority</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {compliance.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="text-center py-4 text-muted">
                          No compliance records found
                        </td>
                      </tr>
                    ) : (
                      compliance.map((item) => (
                        <tr key={item.id}>
                          <td><strong>{item.authority}</strong></td>
                          <td>{item.compliance_name}</td>
                          <td>{item.valid_date}</td>
                          <td>
                            <span className={`badge ${getStatusBadge(item.status)}`}>
                              {item.status}
                            </span>
                          </td>
                          <td>
                            <span className={`badge ${getPriorityBadge(item.priority)}`}>
                              {item.priority}
                            </span>
                          </td>
                          <td>
                            <div className="d-flex gap-2">
                              <button 
                                className="btn btn-sm btn-outline-info"
                                onClick={() => handleView(item.id)}
                                title="View"
                              >
                                <FaEye />
                              </button>
                              <button 
                                className="btn btn-sm btn-outline-primary"
                                onClick={() => handleEdit(item.id)}
                                title="Edit"
                              >
                                <FaEdit />
                              </button>
                              <button 
                                className="btn btn-sm btn-outline-danger"
                                onClick={() => handleDelete(item.id)}
                                title="Delete"
                              >
                                <FaTrash />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              {totalPages > 1 && (
                <div className="d-flex justify-content-between align-items-center mt-3">
                  <span className="text-muted small">
                    Page {page} of {totalPages}
                  </span>
                  <div>
                    <button
                      className="btn btn-sm btn-outline-secondary me-2"
                      disabled={page === 1}
                      onClick={() => setPage(p => p - 1)}
                    >
                      Previous
                    </button>
                    <button
                      className="btn btn-sm btn-outline-secondary"
                      disabled={page === totalPages}
                      onClick={() => setPage(p => p + 1)}
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Compliance;
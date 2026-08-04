import React, { useState, useEffect } from 'react';
import { FaUpload, FaDownload, FaTrash, FaFile, FaFilePdf, FaFileWord, FaFileExcel, FaImage } from 'react-icons/fa';
import { toast } from 'react-toastify';
import { complianceAPI } from '../services/api';
import api from '../services/api';

const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedCompliance, setSelectedCompliance] = useState('');
  const [complianceList, setComplianceList] = useState([]);

  useEffect(() => {
    fetchDocuments();
    fetchComplianceList();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await api.get('/documents');
      setDocuments(response.data || []);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      toast.error('Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const fetchComplianceList = async () => {
    try {
      const response = await complianceAPI.getAll({ per_page: 100 });
      setComplianceList(response.data.data || []);
    } catch (error) {
      console.error('Failed to fetch compliance list:', error);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!selectedCompliance) {
      toast.error('Please select a compliance record first');
      return;
    }
    
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('compliance_id', selectedCompliance);
      
      const response = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      toast.success(response.data.message || 'Document uploaded successfully!');
      fetchDocuments();
      e.target.value = ''; // Reset file input
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (id) => {
    try {
      const response = await api.get(`/documents/${id}`, {
        responseType: 'blob',
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Get filename from content-disposition header or use default
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'document';
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match) filename = match[1];
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Document downloaded successfully!');
    } catch (error) {
      toast.error('Failed to download document');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    
    try {
      await api.delete(`/documents/${id}`);
      toast.success('Document deleted successfully!');
      fetchDocuments();
    } catch (error) {
      toast.error('Failed to delete document');
    }
  };

  const getFileIcon = (fileType) => {
    if (!fileType) return <FaFile className="text-secondary" />;
    const type = fileType.toLowerCase();
    if (type.includes('pdf')) return <FaFilePdf className="text-danger" />;
    if (type.includes('word') || type.includes('doc')) return <FaFileWord className="text-primary" />;
    if (type.includes('excel') || type.includes('xls')) return <FaFileExcel className="text-success" />;
    if (type.includes('image') || type.includes('jpg') || type.includes('jpeg') || type.includes('png')) {
      return <FaImage className="text-info" />;
    }
    return <FaFile className="text-secondary" />;
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  };

  return (
    <div className="fade-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2>Documents</h2>
          <p className="text-muted">Manage compliance documents</p>
        </div>
      </div>

      {/* Upload Section */}
      <div className="card dashboard-card mb-4">
        <div className="card-body">
          <div className="row align-items-end">
            <div className="col-md-5">
              <label className="form-label">Select Compliance</label>
              <select
                className="form-select"
                value={selectedCompliance}
                onChange={(e) => setSelectedCompliance(e.target.value)}
              >
                <option value="">Select a compliance...</option>
                {complianceList.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.compliance_name} ({item.authority})
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-5">
              <label className="form-label">Choose File</label>
              <input
                type="file"
                className="form-control"
                accept=".pdf,.docx,.xlsx,.jpg,.jpeg,.png"
                onChange={handleUpload}
                disabled={uploading || !selectedCompliance}
              />
            </div>
            <div className="col-md-2">
              {uploading && (
                <div className="text-center">
                  <div className="spinner-border spinner-border-sm text-primary" role="status" />
                  <span className="ms-2">Uploading...</span>
                </div>
              )}
            </div>
          </div>
          {!selectedCompliance && (
            <small className="text-warning">Please select a compliance record first</small>
          )}
        </div>
      </div>

      {/* Documents List */}
      <div className="card dashboard-card">
        <div className="card-body">
          {loading ? (
            <div className="text-center py-4">
              <div className="spinner-border text-primary" role="status" />
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-4 text-muted">
              <FaFile size={48} className="mb-3 text-muted" />
              <p>No documents uploaded</p>
            </div>
          ) : (
            <div className="row">
              {documents.map((doc) => (
                <div key={doc.id} className="col-md-4 col-lg-3 mb-3">
                  <div className="border rounded p-3 h-100">
                    <div className="d-flex align-items-center gap-3">
                      <div style={{ fontSize: '32px' }}>
                        {getFileIcon(doc.file_type)}
                      </div>
                      <div className="flex-grow-1">
                        <div className="fw-bold small text-truncate" title={doc.file_name}>
                          {doc.file_name}
                        </div>
                        <div className="text-muted small">{formatFileSize(doc.file_size)}</div>
                        <div className="text-muted small text-truncate" title={doc.compliance_name}>
                          {doc.compliance_name || 'N/A'}
                        </div>
                      </div>
                    </div>
                    <div className="d-flex gap-2 mt-2">
                      <button
                        className="btn btn-sm btn-outline-primary"
                        onClick={() => handleDownload(doc.id)}
                      >
                        <FaDownload size={12} />
                      </button>
                      <button
                        className="btn btn-sm btn-outline-danger"
                        onClick={() => handleDelete(doc.id)}
                      >
                        <FaTrash size={12} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Documents;
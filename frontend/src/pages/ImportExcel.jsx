import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FaUpload, FaFileExcel, FaCheck, FaTimes } from 'react-icons/fa';
import { uploadAPI } from '../services/api';

const ImportExcel = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    // Updated to accept CSV files too
    if (selectedFile && (selectedFile.name.endsWith('.xlsx') || selectedFile.name.endsWith('.xls') || selectedFile.name.endsWith('.csv'))) {
      setFile(selectedFile);
    } else {
      toast.error('Please select a valid Excel (.xlsx, .xls) or CSV (.csv) file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file first');
      return;
    }

    setLoading(true);
    try {
      const response = await uploadAPI.uploadExcel(file);
      setResult(response.data);
      toast.success(`Successfully imported ${response.data.records_imported} records!`);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to import file');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2>Import Excel</h2>
          <p className="text-muted">Upload Excel or CSV file to import compliance data</p>
        </div>
      </div>

      <div className="card dashboard-card">
        <div className="card-body">
          <div className="text-center py-4">
            <div className="mb-4">
              <FaFileExcel size={64} className="text-success" />
            </div>
            <h5>Upload Excel or CSV File</h5>
            <p className="text-muted">Supported formats: .xlsx, .xls, .csv</p>
            
            <div className="border rounded p-4 mt-3" style={{ borderStyle: 'dashed' }}>
              <input
                type="file"
                className="form-control"
                accept=".xlsx,.xls,.csv"
                onChange={handleFileChange}
                style={{ display: 'inline-block', width: 'auto', margin: '0 auto' }}
              />
              {file && (
                <div className="mt-2">
                  <span className="badge bg-success">
                    <FaCheck className="me-1" /> {file.name}
                  </span>
                </div>
              )}
            </div>

            <button
              className="btn btn-primary btn-lg mt-4"
              onClick={handleUpload}
              disabled={!file || loading}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" />
                  Importing...
                </>
              ) : (
                <>
                  <FaUpload className="me-2" />
                  Import File
                </>
              )}
            </button>
          </div>

          {result && (
            <div className="mt-4">
              <h5>Import Results</h5>
              <div className="row">
                <div className="col-md-4">
                  <div className="bg-light p-3 rounded text-center">
                    <small className="text-muted">Total Records</small>
                    <h4>{result.records_imported + (result.errors?.length || 0)}</h4>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="bg-success bg-opacity-10 p-3 rounded text-center">
                    <small className="text-muted">Successfully Imported</small>
                    <h4 className="text-success">{result.records_imported}</h4>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="bg-danger bg-opacity-10 p-3 rounded text-center">
                    <small className="text-muted">Errors</small>
                    <h4 className="text-danger">{result.errors?.length || 0}</h4>
                  </div>
                </div>
              </div>

              {result.errors && result.errors.length > 0 && (
                <div className="mt-3">
                  <h6 className="text-danger">Error Details:</h6>
                  <ul className="list-unstyled">
                    {result.errors.map((error, index) => (
                      <li key={index} className="text-danger small">
                        <FaTimes className="me-1" /> {error}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <button
                className="btn btn-outline-primary mt-3"
                onClick={() => navigate('/app/compliance')}  // ✅ FIXED: Added /app/
              >
                View Compliance Records
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImportExcel;
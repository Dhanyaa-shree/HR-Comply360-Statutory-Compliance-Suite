import React, { useState, useEffect } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import { complianceAPI } from '../services/api';
import { toast } from 'react-toastify';

const CalendarPage = () => {
  const [date, setDate] = useState(new Date());
  const [compliance, setCompliance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCompliance();
  }, []);

  const fetchCompliance = async () => {
    try {
      const response = await complianceAPI.getAll({ per_page: 100 });
      setCompliance(response.data.data);
    } catch (error) {
      toast.error('Failed to fetch compliance data');
    } finally {
      setLoading(false);
    }
  };

  const getEventsForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    return compliance.filter(item => item.valid_date === dateStr);
  };

  const tileContent = ({ date, view }) => {
    if (view === 'month') {
      const events = getEventsForDate(date);
      if (events.length > 0) {
        const hasOverdue = events.some(e => e.status === 'Overdue');
        const hasCompleted = events.some(e => e.status === 'Completed');
        const hasUpcoming = events.some(e => e.status === 'Ongoing' || e.status === 'Planned');
        
        let color = '#3B82F6'; // Blue - Upcoming
        if (hasOverdue) color = '#EF4444'; // Red - Overdue
        else if (hasCompleted && !hasUpcoming && !hasOverdue) color = '#10B981'; // Green - Completed
        
        return (
          <div style={{ 
            width: '8px', 
            height: '8px', 
            borderRadius: '50%', 
            background: color,
            margin: '0 auto',
            marginTop: '2px'
          }} />
        );
      }
    }
    return null;
  };

  const handleDateClick = (date) => {
    setDate(date);
  };

  const selectedEvents = getEventsForDate(date);

  return (
    <div className="fade-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2>Compliance Calendar</h2>
          <p className="text-muted">View compliance deadlines and status</p>
        </div>
      </div>

      <div className="row">
        <div className="col-md-8 mb-4">
          <div className="card dashboard-card">
            <div className="card-body">
              <Calendar
                onChange={handleDateClick}
                value={date}
                tileContent={tileContent}
                className="w-100 border-0"
              />
              <div className="d-flex gap-4 mt-3 justify-content-center">
                <div className="d-flex align-items-center">
                  <span className="badge bg-success me-2">&nbsp;</span>
                  <small>Completed</small>
                </div>
                <div className="d-flex align-items-center">
                  <span className="badge bg-primary me-2">&nbsp;</span>
                  <small>Upcoming</small>
                </div>
                <div className="d-flex align-items-center">
                  <span className="badge bg-danger me-2">&nbsp;</span>
                  <small>Overdue</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card dashboard-card">
            <div className="card-body">
              <h5 className="card-title">
                {date.toLocaleDateString('en-IN', { 
                  weekday: 'long', 
                  day: 'numeric', 
                  month: 'long', 
                  year: 'numeric' 
                })}
              </h5>
              <hr />
              {loading ? (
                <div className="text-center py-3">
                  <div className="spinner-border spinner-border-sm text-primary" role="status" />
                </div>
              ) : selectedEvents.length > 0 ? (
                <div>
                  <p className="text-muted small">{selectedEvents.length} compliance(s)</p>
                  {selectedEvents.map((item) => (
                    <div key={item.id} className="border-bottom py-2">
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <strong className="small">{item.compliance_name}</strong>
                          <div className="text-muted small">{item.authority}</div>
                        </div>
                        <span className={`badge ${
                          item.status === 'Completed' ? 'badge-status-completed' :
                          item.status === 'Overdue' ? 'badge-status-overdue' :
                          'badge-status-ongoing'
                        }`}>
                          {item.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted text-center py-3">No compliance for this date</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CalendarPage;
import React, { useState, useEffect } from 'react';
import { 
  FaFileAlt, FaCheckCircle, FaClock, FaExclamationTriangle, 
  FaCalendarDay 
} from 'react-icons/fa';
import { complianceAPI } from '../services/api';
import { Pie, Bar } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  ArcElement, 
  Tooltip, 
  Legend, 
  CategoryScale, 
  LinearScale, 
  BarElement 
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      console.log('📊 Fetching stats...');
      const response = await complianceAPI.getStats();
      console.log('📊 Stats response:', response.data);
      setStats(response.data);
    } catch (error) {
      console.error('❌ Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
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

  if (!stats || stats.total === 0) {
    return (
      <div className="fade-in">
        <h2 className="mb-4" style={{ color: '#1A1A2E' }}>Dashboard</h2>
        <div className="row">
          <div className="col-12">
            <div className="card dashboard-card">
              <div className="card-body text-center py-5">
                <h5 style={{ color: '#4B5563' }}>No Data Available</h5>
                <p style={{ color: '#4B5563' }}>Import compliance data to see analytics</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ✅ Chart options with visible text
  const chartOptions = {
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#1A1A2E',
          font: { size: 12, weight: '600' }
        }
      },
      tooltip: {
        bodyColor: '#1A1A2E',
        backgroundColor: '#ffffff',
        borderColor: '#E2E8F0',
        borderWidth: 1,
        titleColor: '#1A1A2E'
      }
    }
  };

  const statusData = {
    labels: ['Completed', 'Ongoing', 'Planned', 'Overdue'],
    datasets: [{
      data: [stats.completed || 0, stats.ongoing || 0, stats.planned || 0, stats.overdue || 0],
      backgroundColor: ['#10B981', '#F59E0B', '#3B82F6', '#EF4444'],
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  };

  const monthlyData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [{
      label: 'Completed',
      data: stats.monthly_stats?.map(m => m.count) || Array(12).fill(0),
      backgroundColor: '#10B981',
      borderRadius: 8,
    }]
  };

  // ✅ Bar chart options with visible text
  const barOptions = {
    maintainAspectRatio: false,
    scales: { 
      y: { 
        beginAtZero: true,
        ticks: { color: '#4B5563', font: { size: 11 } },
        grid: { color: '#E2E8F0' }
      },
      x: {
        ticks: { color: '#4B5563', font: { size: 11 } },
        grid: { color: '#E2E8F0' }
      }
    },
    plugins: { 
      legend: { 
        display: false,
        labels: { color: '#1A1A2E' }
      }
    }
  };

  const StatCard = ({ title, value, icon, color, subtitle }) => (
    <div className="col-md-6 col-lg-4 mb-4">
      <div className="card dashboard-card h-100">
        <div className="card-body">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h6 className="mb-1" style={{ color: '#4B5563' }}>{title}</h6>
              <h2 className="mb-0" style={{ color: '#1A1A2E' }}>{value || 0}</h2>
              {subtitle && <small style={{ color: '#4B5563' }}>{subtitle}</small>}
            </div>
            <div className={`card-icon bg-${color} bg-opacity-10`}>
              {icon}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="fade-in">
      <h2 className="mb-4" style={{ color: '#1A1A2E' }}>Dashboard</h2>
      
      <div className="row">
        <StatCard 
          title="Total Compliance" 
          value={stats.total} 
          icon={<FaFileAlt className="text-primary fs-3" style={{ color: '#2563EB' }} />}
          color="primary"
        />
        <StatCard 
          title="Completed" 
          value={stats.completed} 
          icon={<FaCheckCircle className="text-success fs-3" />}
          color="success"
          subtitle={`${stats.completion_rate || 0}% completion rate`}
        />
        <StatCard 
          title="Ongoing" 
          value={stats.ongoing} 
          icon={<FaClock className="text-warning fs-3" />}
          color="warning"
        />
        <StatCard 
          title="Overdue" 
          value={stats.overdue} 
          icon={<FaExclamationTriangle className="text-danger fs-3" />}
          color="danger"
        />
        <StatCard 
          title="Due This Month" 
          value={stats.due_this_month || 0} 
          icon={<FaCalendarDay className="text-info fs-3" />}
          color="info"
        />
      </div>

      <div className="row mt-4">
        <div className="col-md-6 mb-4">
          <div className="card dashboard-card">
            <div className="card-body">
              <h5 className="card-title" style={{ color: '#1A1A2E' }}>Status Distribution</h5>
              <div style={{ height: '300px' }}>
                <Pie data={statusData} options={chartOptions} />
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-6 mb-4">
          <div className="card dashboard-card">
            <div className="card-body">
              <h5 className="card-title" style={{ color: '#1A1A2E' }}>Monthly Completion</h5>
              <div style={{ height: '300px' }}>
                <Bar 
                  data={monthlyData} 
                  options={barOptions} 
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row mt-2">
        <div className="col-12">
          <div className="card dashboard-card">
            <div className="card-body">
              <h5 className="card-title" style={{ color: '#1A1A2E' }}>Category Breakdown</h5>
              <div className="row">
                {stats.category_stats?.map((cat) => (
                  <div className="col-md-3 col-sm-6 mb-3" key={cat.category}>
                    <div className="p-3 rounded text-center" style={{ background: '#E8FFFF' }}>
                      <h6 className="mb-0" style={{ color: '#4B5563' }}>{cat.category}</h6>
                      <h3 className="mb-0" style={{ color: '#1A1A2E' }}>{cat.count}</h3>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
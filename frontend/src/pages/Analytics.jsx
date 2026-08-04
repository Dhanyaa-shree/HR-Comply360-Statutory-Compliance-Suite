import React, { useState, useEffect } from 'react';
import { complianceAPI } from '../services/api';
import { Pie, Bar, Doughnut } from 'react-chartjs-2';
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

const Analytics = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await complianceAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
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

  const completionRate = stats?.completion_rate || 0;
  
  // ✅ Chart options with dark text for visibility on light background
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
      data: [stats?.completed || 0, stats?.ongoing || 0, stats?.planned || 0, stats?.overdue || 0],
      backgroundColor: ['#10B981', '#F59E0B', '#3B82F6', '#EF4444'],
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  };

  const monthlyData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [{
      label: 'Completed',
      data: stats?.monthly_stats?.map(m => m.count) || [],
      backgroundColor: '#10B981',
      borderRadius: 8,
    }]
  };

  const categoryData = {
    labels: stats?.category_stats?.map(c => c.category) || [],
    datasets: [{
      data: stats?.category_stats?.map(c => c.count) || [],
      backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6'],
      borderColor: '#ffffff',
      borderWidth: 2
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

  return (
    <div className="fade-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 style={{ color: '#1A1A2E' }}>Analytics</h2>
          <p style={{ color: '#4B5563' }}>Compliance performance and insights</p>
        </div>
      </div>

      {/* Completion Rate */}
      <div className="card dashboard-card mb-4">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-8">
              <h5 style={{ color: '#1A1A2E' }}>Overall Completion Rate</h5>
              <div className="progress" style={{ height: '30px', background: '#E8FFFF' }}>
                <div 
                  className="progress-bar bg-success" 
                  role="progressbar" 
                  style={{ width: `${completionRate}%` }}
                >
                  {completionRate}%
                </div>
              </div>
              <div className="d-flex justify-content-between mt-1">
                <small style={{ color: '#4B5563' }}>0%</small>
                <small style={{ color: '#4B5563' }}>100%</small>
              </div>
            </div>
            <div className="col-md-4 text-center">
              <h2 className="display-4" style={{ color: '#10B981' }}>{completionRate}%</h2>
              <small style={{ color: '#4B5563' }}>Completion Rate</small>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="row">
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
              <h5 className="card-title" style={{ color: '#1A1A2E' }}>Category Breakdown</h5>
              <div style={{ height: '300px' }}>
                <Doughnut data={categoryData} options={chartOptions} />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-12">
          <div className="card dashboard-card">
            <div className="card-body">
              <h5 className="card-title" style={{ color: '#1A1A2E' }}>Monthly Completion Trend</h5>
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
    </div>
  );
};

export default Analytics;
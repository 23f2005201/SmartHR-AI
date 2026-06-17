import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function Dashboard() {
  const [leaves, setLeaves] = useState([]);
  const [attendance, setAttendance] = useState([]);
  const [attritionData, setAttritionData] = useState(null);
  const [burnoutData, setBurnoutData] = useState(null);
  const [loadingAI, setLoadingAI] = useState(true);

  useEffect(() => {
    fetchDashboardAndAIMetrics();
  }, []);

  const fetchDashboardAndAIMetrics = async () => {
    try {
      const [leavesRes, authRes, attritionRes, burnoutRes] = await Promise.all([
        api.get('/leave/'),
        api.get('/attendance/'),
        // Trigger Scikit-Learn pipelines directly on mounting load cycles
        api.post('/ai/predict-attrition', { years_at_company: 3.5, monthly_salary: 45000, weekly_overtime_hours: 12, satisfaction_score: 2 }),
        api.post('/ai/analyze-leave', { sick_leaves_taken: 4, casual_leaves_taken: 1, consecutive_days_requested: 5 })
      ]);
      setLeaves(leavesRes.data);
      setAttendance(authRes.data);
      setAttritionData(attritionRes.data);
      setBurnoutData(burnoutRes.data);
    } catch (err) {
      console.error("Failed to load connected analytical endpoints metrics.");
    } finally {
      setLoadingAI(false);
    }
  };

  const updateLeaveStatus = async (leaveId, newStatus) => {
    try {
      await api.put(`/leave/${leaveId}/status`, { status: newStatus });
      fetchDashboardAndAIMetrics();
    } catch (err) {
      alert("Failed to update leave status.");
    }
  };

  const pendingLeaves = leaves.filter(l => l.status === 'Pending');

  return (
    <div className="p-8 space-y-8 max-w-7xl w-full mx-auto font-sans text-slate-100">
      
      {/* Row 1: Core Summary Statistics */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Staff Clocked In Today</span>
          <span className="block text-3xl font-bold text-emerald-400 mt-2">{attendance.length}</span>
        </div>
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Action Required: Leaves</span>
          <span className="block text-3xl font-bold text-amber-400 mt-2">{pendingLeaves.length}</span>
        </div>
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Leave Petitions</span>
          <span className="block text-3xl font-bold text-slate-200 mt-2">{leaves.length}</span>
        </div>
      </section>

      {/* Row 2: Live Predictive ML Feature Grid Panels */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Attrition Pipeline Tracker */}
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl relative overflow-hidden backdrop-blur-md shadow-xl">
          <div className="absolute top-0 right-0 bg-blue-500/10 text-blue-400 text-[10px] font-bold px-3 py-1 rounded-bl uppercase tracking-widest border-l border-b border-blue-500/10">
            Scikit-Learn Pipeline
          </div>
          <h3 className="text-md font-bold text-white mb-2">Predictive Staff Turnover Assessment</h3>
          <p className="text-xs text-slate-400 mb-4">Probability forecast models tracing overtime saturation maps vs satisfaction limits.</p>
          {loadingAI ? (
            <div className="h-20 bg-slate-950/40 animate-pulse rounded-xl border border-slate-800"></div>
          ) : attritionData && (
            <div className="p-4 bg-slate-950/50 rounded-xl border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">Attrition Index State</span>
                <span className={`block text-lg font-bold ${attritionData.attrition_risk === 'High' ? 'text-rose-400' : 'text-emerald-400'}`}>{attritionData.attrition_risk} Risk Profile</span>
                <p className="text-xs text-slate-400 mt-1">{attritionData.recommendation}</p>
              </div>
              <div className="text-right ml-4">
                <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">Probability</span>
                <span className="block text-2xl font-extrabold text-white mt-0.5">{attritionData.risk_probability}%</span>
              </div>
            </div>
          )}
        </div>

        {/* Burnout/Leave Anomaly Profile Tracker */}
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl relative overflow-hidden backdrop-blur-md shadow-xl">
          <div className="absolute top-0 right-0 bg-indigo-500/10 text-indigo-400 text-[10px] font-bold px-3 py-1 rounded-bl uppercase tracking-widest border-l border-b border-indigo-500/10">
            RandomForest Model
          </div>
          <h3 className="text-md font-bold text-white mb-2">Leave Sequence Burnout Monitor</h3>
          <p className="text-xs text-slate-400 mb-4">Evaluates requested time configurations against consecutive sick parameters to flag stress states.</p>
          {loadingAI ? (
            <div className="h-20 bg-slate-950/40 animate-pulse rounded-xl border border-slate-800"></div>
          ) : burnoutData && (
            <div className="p-4 bg-slate-950/50 rounded-xl border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">Sequence Classification</span>
                <span className="block text-sm font-bold text-slate-200 mt-0.5">{burnoutData.classification}</span>
                <p className="text-xs text-slate-500 mt-1">Status: {burnoutData.irregular_pattern_detected ? "🚨 Anomalous Multi-Request Metric" : "✓ Within standard deviation intervals."}</p>
              </div>
              <div className="text-right ml-4">
                <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">Anomaly Rank</span>
                <span className="block text-2xl font-extrabold text-amber-400 mt-0.5">{burnoutData.pattern_anomaly_score}%</span>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Row 3: Approval Execution Table Grid */}
      <section className="bg-slate-900 rounded-xl border border-slate-800 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/50">
          <h2 className="text-md font-semibold text-white">Pending Leave Approvals</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-800">
            <thead className="bg-slate-900/30">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Emp ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Duration</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 bg-slate-900/10">
              {pendingLeaves.map((leave) => (
                <tr key={leave.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">#{leave.employee_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">{leave.leave_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">{leave.start_date} to {leave.end_date}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                    <button onClick={() => updateLeaveStatus(leave.id, 'Approved')} className="text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-md transition-colors">Approve</button>
                    <button onClick={() => updateLeaveStatus(leave.id, 'Rejected')} className="text-rose-400 hover:text-rose-300 bg-rose-500/10 border border-rose-500/20 px-3 py-1 rounded-md transition-colors">Reject</button>
                  </td>
                </tr>
              ))}
              {pendingLeaves.length === 0 && (
                <tr>
                  <td colSpan="4" className="px-6 py-12 text-center text-sm text-slate-500">
                    All caught up! No pending leave requests.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
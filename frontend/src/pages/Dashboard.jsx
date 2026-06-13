import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const [leaves, setLeaves] = useState([]);
  const [attendance, setAttendance] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [leavesRes, authRes] = await Promise.all([
        api.get('/leave/'),
        api.get('/attendance/')
      ]);
      setLeaves(leavesRes.data);
      setAttendance(authRes.data);
    } catch (err) {
      console.error("Failed to load dashboard metrics.");
    }
  };

  const updateLeaveStatus = async (leaveId, newStatus) => {
    try {
      await api.put(`/leave/${leaveId}/status`, { status: newStatus });
      fetchDashboardData();
    } catch (err) {
      alert("Failed to update leave status.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const pendingLeaves = leaves.filter(l => l.status === 'Pending');

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans">
      
      {/* NATIVE INTEGRATED SIDEBAR */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between p-6 h-screen sticky top-0">
        <div>
          <div className="text-xl font-bold tracking-wider text-white mb-8">SmartHR AI</div>
          <nav className="space-y-2">
            <button onClick={() => navigate('/dashboard')} className="w-full text-left block py-2.5 px-4 bg-slate-800 text-white rounded-lg font-medium transition-colors">Dashboard Overview</button>
            <button onClick={() => navigate('/onboarding')} className="w-full text-left block py-2.5 px-4 text-slate-400 hover:bg-slate-800 hover:text-white rounded-lg transition-colors">Employee Onboarding</button>
            <button onClick={() => navigate('/attendance')} className="w-full text-left block py-2.5 px-4 text-slate-400 hover:bg-slate-800 hover:text-white rounded-lg transition-colors">Self-Service Access</button>
          </nav>
        </div>
        <button onClick={handleLogout} className="w-full py-2.5 bg-rose-600/90 hover:bg-rose-600 text-white font-semibold rounded-lg text-sm transition-colors shadow-lg shadow-rose-900/20">
          Terminate Session
        </button>
      </aside>
      
      {/* MAIN VIEWPORT BODY */}
      <main className="flex-1 flex flex-col overflow-y-auto">
        {/* NATIVE INTEGRATED HEADER */}
        <header className="bg-slate-900 border-b border-slate-800 py-4 px-8 flex justify-between items-center sticky top-0 z-10">
          <h1 className="text-lg font-semibold text-white">HR Command Center</h1>
          <div className="flex items-center space-x-3">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm shadow-emerald-400 animate-pulse"></span>
            <span className="text-xs font-semibold text-slate-300 bg-slate-800 py-1.5 px-3 rounded-full border border-slate-700">System Operator Online</span>
          </div>
        </header>

        <div className="p-8 space-y-8 max-w-7xl w-full mx-auto">
          {/* Top Metrics Cards */}
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

          {/* Leave Management Table */}
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
      </main>
    </div>
  );
}
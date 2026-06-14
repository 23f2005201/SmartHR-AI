import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function Dashboard() {
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

  const pendingLeaves = leaves.filter(l => l.status === 'Pending');

  return (
    <div className="p-8 space-y-8 max-w-7xl w-full mx-auto">
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
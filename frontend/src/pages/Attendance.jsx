import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function Attendance() {
  const [clockStatus, setClockStatus] = useState('');
  const [leaveData, setLeaveData] = useState({ leave_type: 'Annual', start_date: '', end_date: '' });
  const [myLeaves, setMyLeaves] = useState([]);

  useEffect(() => {
    fetchMyLeaves();
  }, []);

  const fetchMyLeaves = async () => {
    try {
      const res = await api.get('/leave/me');
      setMyLeaves(res.data);
    } catch (err) {
      console.error("Could not fetch leaves");
    }
  };

  const handleClockIn = async () => {
    try {
      await api.post('/attendance/clock-in');
      setClockStatus('Successfully Clocked In for today.');
    } catch (err) {
      setClockStatus(err.response?.data?.detail || 'Clock-in failed.');
    }
  };

  const handleClockOut = async () => {
    try {
      await api.put('/attendance/clock-out');
      setClockStatus('Successfully Clocked Out. Have a good evening!');
    } catch (err) {
      setClockStatus(err.response?.data?.detail || 'Clock-out failed.');
    }
  };

  const handleLeaveSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/leave/', { ...leaveData, employee_id: 0 });
      alert("Leave Request Submitted Successfully!");
      fetchMyLeaves();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to submit leave request.");
    }
  };

  return (
    <div className="p-6 sm:p-8 space-y-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400">
          Employee Self-Service Portal
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Log daily operational time metrics and submit future leave applications.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Attendance Widget */}
        <div className="bg-slate-900/50 backdrop-blur-xl p-6 rounded-2xl border border-slate-800/80 shadow-xl">
          <h2 className="text-lg font-bold text-white mb-4">Daily Attendance Logging</h2>
          <div className="flex space-x-4 mb-4">
            <button onClick={handleClockIn} className="flex-1 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl transition-all active:scale-[0.99] text-sm shadow-lg shadow-emerald-950/20">
              Clock In
            </button>
            <button onClick={handleClockOut} className="flex-1 py-3 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl transition-all active:scale-[0.99] text-sm shadow-lg shadow-rose-950/20">
              Clock Out
            </button>
          </div>
          {clockStatus && <p className="text-xs font-semibold text-blue-400 bg-blue-500/10 p-3 rounded-xl border border-blue-500/10 animate-fadeIn">{clockStatus}</p>}
        </div>

        {/* Leave Request Form */}
        <div className="bg-slate-900/50 backdrop-blur-xl p-6 rounded-2xl border border-slate-800/80 shadow-xl">
          <h2 className="text-lg font-bold text-white mb-4">Submit Leave Petition</h2>
          <form onSubmit={handleLeaveSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest">Leave Category</label>
              <select 
                className="mt-1.5 w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-slate-700 font-medium"
                value={leaveData.leave_type}
                onChange={(e) => setLeaveData({...leaveData, leave_type: e.target.value})}
              >
                <option value="Annual">Annual Leave</option>
                <option value="Sick">Sick Leave</option>
                <option value="Casual">Casual Leave</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest">Start Date</label>
                <input required type="date" className="mt-1.5 w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-slate-700 font-medium" onChange={(e) => setLeaveData({...leaveData, start_date: e.target.value})} />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest">End Date</label>
                <input required type="date" className="mt-1.5 w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-slate-700 font-medium" onChange={(e) => setLeaveData({...leaveData, end_date: e.target.value})} />
              </div>
            </div>
            <button type="submit" className="w-full py-3 bg-white hover:bg-slate-100 text-slate-900 font-bold rounded-xl text-sm transition-all active:scale-[0.99]">Submit Request</button>
          </form>
        </div>
      </div>

      {/* Leave History Table */}
      <div className="bg-slate-900/30 backdrop-blur-xl rounded-2xl border border-slate-800/80 shadow-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/30">
          <h2 className="text-md font-semibold text-white">My Personal Leave History</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-800">
            <thead className="bg-slate-900/60">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-bold text-slate-400 uppercase tracking-widest">Type</th>
                <th className="px-6 py-4 text-left text-xs font-bold text-slate-400 uppercase tracking-widest">Start</th>
                <th className="px-6 py-4 text-left text-xs font-bold text-slate-400 uppercase tracking-widest">End</th>
                <th className="px-6 py-4 text-right text-xs font-bold text-slate-400 uppercase tracking-widest">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 bg-slate-900/10">
              {myLeaves.map((leave, idx) => (
                <tr key={idx} className="hover:bg-slate-800/20 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">{leave.leave_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">{leave.start_date}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">{leave.end_date}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <span className={`px-2.5 py-1 text-xs font-bold rounded-full border ${
                      leave.status === 'Approved' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 
                      leave.status === 'Rejected' ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' : 
                      'bg-amber-500/10 border-amber-500/20 text-amber-400'}`}>
                      {leave.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {myLeaves.length === 0 && <p className="text-center text-sm text-slate-600 py-8">No historical leave records detected.</p>}
        </div>
      </div>
    </div>
  );
}
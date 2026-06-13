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
      // The backend expects employee_id, but our token figures it out. We pass a dummy 0 to pass schema validation if needed, or update schema to make it optional. 
      // Assuming your schema allows omitting employee_id if handled by backend.
      await api.post('/leave/', { ...leaveData, employee_id: 0 });
      alert("Leave Request Submitted Successfully!");
      fetchMyLeaves(); // Refresh the list
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to submit leave request.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-8">Employee Self-Service Portal</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Attendance Widget */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-800 mb-4">Daily Attendance Logging</h2>
          <div className="flex space-x-4 mb-4">
            <button onClick={handleClockIn} className="px-6 py-3 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition-colors">
              Clock In
            </button>
            <button onClick={handleClockOut} className="px-6 py-3 bg-rose-600 text-white font-semibold rounded-lg hover:bg-rose-700 transition-colors">
              Clock Out
            </button>
          </div>
          {clockStatus && <p className="text-sm font-medium text-brand-600 bg-brand-50 p-3 rounded">{clockStatus}</p>}
        </div>

        {/* Leave Request Form */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-800 mb-4">Submit Leave Petition</h2>
          <form onSubmit={handleLeaveSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-600">Leave Category</label>
              <select 
                className="mt-1 w-full p-2 border rounded-md"
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
                <label className="block text-sm font-medium text-slate-600">Start Date</label>
                <input required type="date" className="mt-1 w-full p-2 border rounded-md" onChange={(e) => setLeaveData({...leaveData, start_date: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600">End Date</label>
                <input required type="date" className="mt-1 w-full p-2 border rounded-md" onChange={(e) => setLeaveData({...leaveData, end_date: e.target.value})} />
              </div>
            </div>
            <button type="submit" className="w-full py-2 bg-brand-600 text-white font-semibold rounded-lg hover:bg-brand-700">Submit Request</button>
          </form>
        </div>
      </div>

      {/* Leave History Table */}
      <div className="mt-8 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <h2 className="text-xl font-semibold text-slate-800 mb-4">My Leave History</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Start</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">End</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {myLeaves.map((leave, idx) => (
                <tr key={idx}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">{leave.leave_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{leave.start_date}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{leave.end_date}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                      ${leave.status === 'Approved' ? 'bg-emerald-100 text-emerald-800' : 
                        leave.status === 'Rejected' ? 'bg-rose-100 text-rose-800' : 
                        'bg-amber-100 text-amber-800'}`}>
                      {leave.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {myLeaves.length === 0 && <p className="text-center text-sm text-slate-500 mt-4">No leave requests found.</p>}
        </div>
      </div>
    </div>
  );
}
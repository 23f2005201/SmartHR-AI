import React, { useState } from 'react';
import api from '../services/api';

export default function Onboarding() {
  const [step, setStep] = useState(1);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    user_id: '',
    first_name: '',
    last_name: '',
    department_id: '',
    joining_date: '',
    salary: ''
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFormSubmit = async () => {
    setError('');
    setSuccess('');
    try {
      const payload = {
        ...formData,
        user_id: parseInt(formData.user_id),
        department_id: formData.department_id ? parseInt(formData.department_id) : null,
        salary: parseFloat(formData.salary)
      };

      await api.post('/employees/', payload);
      setSuccess('Employee profile successfully provisioned on the platform matrix.');
      setStep(3);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit onboarding data profile.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 sm:p-8 font-sans">
      <div className="max-w-2xl mx-auto bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-800 p-6 sm:p-10 shadow-2xl">
        <h1 className="text-2xl font-extrabold tracking-tight text-white mb-6">Staff Onboarding Wizard</h1>
        
        {error && <div className="mb-4 rounded-xl bg-rose-500/10 border border-rose-500/20 p-4 text-xs font-semibold text-rose-400">{error}</div>}

        {step === 1 && (
          <div className="space-y-5">
            <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400 border-b border-slate-800 pb-2">Step 1: Core Identity Profiling</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Associated User ID</label>
                <input name="user_id" type="number" className="mt-1.5 w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-slate-700 font-medium" value={formData.user_id} onChange={handleInputChange} />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Joining Date</label>
                <input name="joining_date" type="date" className="mt-1.5 w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-slate-700 font-medium" value={formData.joining_date} onChange={handleInputChange} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">First Name</label>
                <input name="first_name" type="text" className="mt-1.5 w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-slate-700 font-medium" placeholder="Jane" value={formData.first_name} onChange={handleInputChange} />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Last Name</label>
                <input name="last_name" type="text" className="mt-1.5 w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-slate-700 font-medium" placeholder="Doe" value={formData.last_name} onChange={handleInputChange} />
              </div>
            </div>
            <button onClick={() => setStep(2)} className="w-full mt-4 py-3 bg-white hover:bg-slate-100 text-slate-900 font-bold rounded-xl text-sm transition-all">Continue Set</button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-5">
            <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400 border-b border-slate-800 pb-2">Step 2: Operations & Compensation</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Department ID</label>
                <input name="department_id" type="number" className="mt-1.5 w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-slate-700 font-medium" value={formData.department_id} onChange={handleInputChange} />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Base Monthly Salary (₹)</label>
                <input name="salary" type="number" className="mt-1.5 w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-slate-700 font-medium" placeholder="60000" value={formData.salary} onChange={handleInputChange} />
              </div>
            </div>
            <div className="flex space-x-4 mt-4">
              <button onClick={() => setStep(1)} className="flex-1 py-3 border border-slate-800 text-slate-400 font-bold rounded-xl text-sm hover:bg-slate-900/50 transition-colors">Back</button>
              <button onClick={handleFormSubmit} className="flex-1 py-3 bg-white hover:bg-slate-100 text-slate-900 font-bold rounded-xl text-sm transition-all">Commit Profile</button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="text-center py-6 space-y-4">
            <div className="w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center mx-auto text-xl font-bold">✓</div>
            <p className="text-sm font-semibold text-slate-200">{success}</p>
            <button onClick={() => { setStep(1); setFormData({ user_id: '', first_name: '', last_name: '', department_id: '', joining_date: '', salary: '' }); }} className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-xl text-xs uppercase tracking-wider">Onboard Next Account</button>
          </div>
        )}
      </div>
    </div>
  );
}
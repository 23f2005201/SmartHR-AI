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
      // Cast appropriate data structures before transmission
      const payload = {
        ...formData,
        user_id: parseInt(formData.user_id),
        department_id: formData.department_id ? parseInt(formData.department_id) : null,
        salary: parseFloat(formData.salary)
      };

      await api.post('/employees/', payload);
      setSuccess('Employee profile successfully provisioned on the platform matrix.');
      setStep(3); // Navigate to confirmation screen
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit onboarding data profile.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-2xl mx-auto bg-white rounded-xl border border-slate-200 shadow-sm p-8">
        <h1 className="text-2xl font-bold text-slate-900 mb-6">Staff Onboarding & Profile Wizard</h1>
        
        {error && <div className="mb-4 rounded-md bg-rose-50 p-4 text-sm text-rose-600 border border-rose-100">{error}</div>}

        {step === 1 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-700 border-b pb-2">Step 1: Identity Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-600">Associated User ID</label>
                <input name="user_id" type="number" className="mt-1 w-full rounded-md border p-2 text-sm" value={formData.user_id} onChange={handleInputChange} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600">Joining Date</label>
                <input name="joining_date" type="date" className="mt-1 w-full rounded-md border p-2 text-sm" value={formData.joining_date} onChange={handleInputChange} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-600">First Name</label>
                <input name="first_name" type="text" className="mt-1 w-full rounded-md border p-2 text-sm" value={formData.first_name} onChange={handleInputChange} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600">Last Name</label>
                <input name="last_name" type="text" className="mt-1 w-full rounded-md border p-2 text-sm" value={formData.last_name} onChange={handleInputChange} />
              </div>
            </div>
            <button onClick={() => setStep(2)} className="mt-4 px-4 py-2 bg-brand-600 text-white rounded-md text-sm font-semibold hover:bg-brand-700">Continue Layout</button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-700 border-b pb-2">Step 2: Operational Allocation & Compensation</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-600">Department Identifier</label>
                <input name="department_id" type="number" className="mt-1 w-full rounded-md border p-2 text-sm" value={formData.department_id} onChange={handleInputChange} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600">Annual Gross Salary (£)</label>
                <input name="salary" type="number" className="mt-1 w-full rounded-md border p-2 text-sm" value={formData.salary} onChange={handleInputChange} />
              </div>
            </div>
            <div className="flex space-x-3 mt-4">
              <button onClick={() => setStep(1)} className="px-4 py-2 border rounded-md text-sm text-slate-600">Back</button>
              <button onClick={handleFormSubmit} className="px-4 py-2 bg-emerald-600 text-white rounded-md text-sm font-semibold hover:bg-emerald-700">Commit Provisioning</button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="text-center py-6">
            <div className="text-emerald-500 text-5xl mb-4">✓</div>
            <p className="text-md font-medium text-slate-800">{success}</p>
            <button onClick={() => { setStep(1); setFormData({ user_id: '', first_name: '', last_name: '', department_id: '', joining_date: '', salary: '' }); }} className="mt-6 px-4 py-2 bg-brand-600 text-white rounded-md text-sm font-semibold">Onboard New Employee</button>
          </div>
        )}
      </div>
    </div>
  );
}
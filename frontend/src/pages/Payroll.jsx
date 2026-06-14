import React, { useState } from 'react';
import api from '../services/api';

export default function Payroll() {
  const [empId, setEmpId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [calculatedSheet, setCalculatedSheet] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleProcessPayroll = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post(`/payroll/process/${empId}?start_date=${startDate}&end_date=${endDate}`);
      setCalculatedSheet(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || "Processing run failure. Confirm parameters match records.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <h1 className="text-3xl font-bold mb-8 tracking-tight text-white">Salary Processing & Payroll Engine</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 h-fit">
          <h2 className="text-lg font-semibold text-white mb-4">Run Payroll Calculation</h2>
          <form onSubmit={handleProcessPayroll} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider">Target Employee ID</label>
              <input required type="number" className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-md p-2 text-white" value={empId} onChange={e => setEmpId(e.target.value)} />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider">Start Date</label>
              <input required type="date" className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-md p-2 text-white" value={startDate} onChange={e => setStartDate(e.target.value)} />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider">End Date</label>
              <input required type="date" className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-md p-2 text-white" value={endDate} onChange={e => setEndDate(e.target.value)} />
            </div>
            <button type="submit" className="w-full py-2.5 bg-brand-600 hover:bg-brand-500 font-semibold text-white rounded-md transition-colors">
              {loading ? "Computing Financials..." : "Execute Calculation Run"}
            </button>
          </form>
        </div>

        {calculatedSheet && (
          <div className="lg:col-span-2 bg-slate-900 rounded-xl border border-slate-800 p-8 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 bg-emerald-500/10 text-emerald-400 text-xs px-4 py-1.5 rounded-bl border-l border-b border-emerald-500/20 uppercase tracking-widest font-bold">
              {calculatedSheet.status}
            </div>
            <h3 className="text-xl font-bold text-white mb-6">Generated Pay Slip Statement</h3>
            
            <div className="border border-slate-800 rounded-lg p-4 bg-slate-950/40 space-y-2 mb-6 text-sm text-slate-300">
              <p><strong className="text-slate-400">Employee Reference:</strong> #{calculatedSheet.employee_id}</p>
              <p><strong className="text-slate-400">Statement Period:</strong> {calculatedSheet.pay_period_start} to {calculatedSheet.pay_period_end}</p>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between py-2 border-b border-slate-800">
                <span className="text-slate-400">Gross Calculated Compensation</span>
                <span className="font-semibold text-slate-200">₹{calculatedSheet.gross_salary}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-800">
                <span className="text-rose-400">Statutory Tax Withholding (15%)</span>
                <span className="font-semibold text-rose-400">-₹{calculatedSheet.tax_deductions}</span>
              </div>
              <div className="flex justify-between py-3 text-lg font-bold">
                <span className="text-white">Net Liquid Distribution</span>
                <span className="text-emerald-400">₹{calculatedSheet.net_salary}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
import React from 'react';

export default function Dashboard() {
  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  return (
    <div className="flex h-screen bg-slate-100">
      {/* Structural Lateral Workspace Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col justify-between p-6">
        <div>
          <div className="text-xl font-bold tracking-wider text-brand-500 mb-8">SmartHR AI</div>
          <nav className="space-y-3">
            <a href="/dashboard" className="block py-2 px-4 bg-slate-800 rounded font-medium text-white">Dashboard Overview</a>
            <a href="/onboarding" className="block py-2 px-4 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition-colors">Employee Onboarding</a>
            <a href="/attendance" className="block py-2 px-4 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition-colors">Self-Service Access</a>
          </nav>
        </div>
        <button onClick={handleLogout} className="w-full py-2 bg-rose-600 hover:bg-rose-700 transition-colors rounded text-sm font-semibold">
          Terminate Session
        </button>
      </aside>

      {/* Main Core View Area Workspace */}
      <main className="flex-1 flex flex-col overflow-y-auto">
        <header className="bg-white border-b border-slate-200 py-4 px-8 flex justify-between items-center shadow-sm">
          <h1 className="text-lg font-semibold text-slate-700">Platform Analytics Overview</h1>
          <div className="flex items-center space-x-3">
            <span className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-sm font-medium text-slate-600 bg-slate-100 py-1 px-3 rounded-full">System Operator: Administrative Mode</span>
          </div>
        </header>

        <section className="p-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <span className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Total Active Staff Base</span>
            <span className="text-3xl font-bold text-slate-800 mt-2">--</span>
          </div>
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <span className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Processed Daily Attendance</span>
            <span className="text-3xl font-bold text-slate-800 mt-2">--</span>
          </div>
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <span className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Pending Leave Petitions</span>
            <span className="text-3xl font-bold text-slate-800 mt-2">--</span>
          </div>
        </section>
      </main>
    </div>
  );
}
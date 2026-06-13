import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Sidebar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <aside className="w-64 bg-slate-900 text-white flex flex-col justify-between p-6 h-screen sticky top-0">
      <div>
        <div className="text-xl font-bold tracking-wider text-slate-200 mb-8">SmartHR AI</div>
        <nav className="space-y-3">
          <button onClick={() => navigate('/dashboard')} className="w-full text-left block py-2 px-4 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition-colors">Dashboard Overview</button>
          <button onClick={() => navigate('/onboarding')} className="w-full text-left block py-2 px-4 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition-colors">Employee Onboarding</button>
          <button onClick={() => navigate('/attendance')} className="w-full text-left block py-2 px-4 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition-colors">Self-Service Access</button>
        </nav>
      </div>
      <button onClick={handleLogout} className="w-full py-2 bg-rose-600 hover:bg-rose-700 transition-colors rounded text-sm font-semibold">
        Terminate Session
      </button>
    </aside>
  );
}
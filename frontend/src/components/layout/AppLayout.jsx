import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function AppLayout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const menuItems = [
    { name: 'Dashboard Overview', path: '/dashboard', badge: null },
    { name: 'Employee Onboarding', path: '/onboarding', badge: null },
    { name: 'Payroll Processing', path: '/payroll', badge: 'bg-blue-400' },
    { name: 'Self-Service Access', path: '/attendance', badge: null },
    { name: 'System Audit Reports', path: '/reports', badge: 'bg-emerald-400' },
  ];

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans">
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between p-6 h-screen sticky top-0 z-20">
        <div>
          <div className="text-xl font-bold tracking-wider text-white mb-8">SmartHR AI</div>
          <nav className="space-y-1">
            {menuItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className={`w-full text-left py-2.5 px-4 rounded-lg font-medium transition-colors flex items-center justify-between ${
                    isActive ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
                  }`}
                >
                  <span>{item.name}</span>
                  {item.badge && <span className={`w-1.5 h-1.5 rounded-full ${item.badge}`}></span>}
                </button>
              );
            })}
          </nav>
        </div>
        <button onClick={handleLogout} className="w-full py-2.5 bg-rose-600/90 hover:bg-rose-600 text-white font-semibold rounded-lg text-sm transition-colors shadow-lg shadow-rose-900/20">
          Terminate Session
        </button>
      </aside>
      
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <header className="bg-slate-900 border-b border-slate-800 py-4 px-8 flex justify-between items-center sticky top-0 z-10">
          <h1 className="text-lg font-semibold text-white">HR Command Center</h1>
          <div className="flex items-center space-x-3">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm shadow-emerald-400 animate-pulse"></span>
            <span className="text-xs font-semibold text-slate-300 bg-slate-800 py-1.5 px-3 rounded-full border border-slate-700">System Operator Online</span>
          </div>
        </header>
        <main className="flex-1">
          {children}
        </main>
      </div>
    </div>
  );
}

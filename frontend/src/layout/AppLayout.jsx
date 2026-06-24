import React, { useState } from 'react';
import Sidebar from './Sidebar'; // Point straight to your existing component
import Header from './Header';   // Point straight to your existing component
import LeaveModal from '../LeaveModal'; // Import our multi-format document parser

export default function AppLayout({ children }) {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  return (
    <div className="flex h-screen w-screen bg-slate-950 overflow-hidden font-sans">
      
      {/* 1. Render Your Existing Modular Left Sidebar */}
      <div className="flex-shrink-0 flex flex-col justify-between h-full relative">
        <Sidebar />
        
        {/* 🚀 FLOAT THE COPILOT BUTTON RIGHT OVER THE BOTTOM FOOTER SECTION OF SIDEBAR */}
        <div className="absolute bottom-20 left-0 right-0 px-6">
          <button 
            onClick={() => setIsDrawerOpen(true)}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-3 px-4 rounded-xl shadow-lg shadow-indigo-500/20 text-xs uppercase tracking-widest transition-all cursor-pointer"
          >
            ✨ Launch AI Copilot
          </button>
        </div>
      </div>

      {/* 2. Main Content Window Grid */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        
        {/* Render Your Existing Header Dynamic Wrapper */}
        <Header title="SmartHR Operations Command Center" />
        
        {/* Inject the child page contents viewport canvas */}
        <main className="flex-1 overflow-y-auto p-8 bg-slate-950 text-slate-100">
          {children}
        </main>
      </div>

      {/* --- 🧠 COLD COMPUTE AI PERSISTENT SLIDING DRAWER OVERLAY --- */}
      {isDrawerOpen && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm animate-fadeIn">
          {/* Background overlay click trap to close panel natively */}
          <div className="absolute inset-0" onClick={() => setIsDrawerOpen(false)} />
          
          <div className="relative w-full max-w-lg h-full bg-slate-900 border-l border-slate-800 shadow-2xl p-8 overflow-y-auto flex flex-col">
            <button 
              onClick={() => setIsDrawerOpen(false)}
              className="absolute top-6 right-6 text-slate-400 hover:text-white font-bold text-sm transition-colors cursor-pointer"
            >
              ✕ Close Panel
            </button>
            
            {/* Launch the pre-configured form parser module directly inside layout */}
            <div className="mt-8">
              <LeaveModal />
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
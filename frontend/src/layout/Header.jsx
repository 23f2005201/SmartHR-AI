import React from 'react';

export default function Header({ title }) {
  return (
    <header className="bg-slate-900 border-b border-slate-800 py-4 px-8 flex justify-between items-center shadow-sm sticky top-0 z-10">
      <h1 className="text-lg font-semibold text-slate-700">{title}</h1>
      <div className="flex items-center space-x-3">
        <span className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
        <span className="text-sm font-medium text-slate-600 bg-slate-100 py-1 px-3 rounded-full">System Operator Online</span>
      </div>
    </header>
  );
}
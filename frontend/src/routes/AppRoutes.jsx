import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Simple placeholders for today's skeleton setup
const Login = () => <div className="p-8 text-center"><h2 className="text-2xl font-bold text-brand-600">SmartHR AI Login Portal</h2></div>;
const Dashboard = () => <div className="p-8"><h2 className="text-2xl font-bold">HR Core Management Dashboard</h2></div>;
const Onboarding = () => <div className="p-8"><h2 className="text-2xl font-bold">Employee Onboarding Wizard</h2></div>;
const Attendance = () => <div className="p-8"><h2 className="text-2xl font-bold">Employee Self-Service Clock-In</h2></div>;

// Component to protect authenticated pathways
const ProtectedRoute = ({ children }) => {
  // Simple check against local storage session flags for now
  const isAuthenticated = localStorage.getItem('token') !== null;
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Pathways */}
        <Route path="/login" element={<Login />} />

        {/* Private / Guarded Management Pathways */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        
        <Route path="/onboarding" element={
          <ProtectedRoute>
            <Onboarding />
          </ProtectedRoute>
        } />

        <Route path="/attendance" element={
          <ProtectedRoute>
            <Attendance />
          </ProtectedRoute>
        } />

        {/* Default Route Fallback */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
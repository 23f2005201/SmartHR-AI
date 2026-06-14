import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Import Workspace Components
import Login from '../pages/Login';
import Dashboard from '../pages/Dashboard';
import Onboarding from '../pages/Onboarding';
import Attendance from '../pages/Attendance';
import Payroll from '../pages/Payroll';
import Reports from '../pages/Reports';

// Import Reusable Layout Base Wrapper
import AppLayout from '../components/layout/AppLayout';

// Component to protect authenticated pathways and mount the unified layout
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = localStorage.getItem('token') !== null;
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <AppLayout>{children}</AppLayout>;
};

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Authentication Path */}
        <Route path="/login" element={<Login />} />

        {/* Private / Guarded Management Pathways with Reusable Sidebar */}
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/onboarding" element={<ProtectedRoute><Onboarding /></ProtectedRoute>} />
        <Route path="/payroll" element={<ProtectedRoute><Payroll /></ProtectedRoute>} />
        <Route path="/attendance" element={<ProtectedRoute><Attendance /></ProtectedRoute>} />
        <Route path="/reports" element={<ProtectedRoute><Reports /></ProtectedRoute>} />

        {/* Global Fallback Redirect */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
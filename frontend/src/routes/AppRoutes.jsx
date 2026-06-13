import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import Login from '../pages/Login';
import Dashboard from '../pages/Dashboard';
import Onboarding from '../pages/Onboarding';
import Attendance from '../pages/Attendance';

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
        {/* Force empty root path to clear directly to the login panel */}
        <Route path="/" element={<Navigate to="/login" replace />} />

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
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Home from './pages/Home';
import PromptToDSL from './pages/PromptToDSL';
import Builder from './pages/Builder';
import Generate from './pages/Generate';
import Deploy from './pages/Deploy';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import Footer from './components/Footer';
import { AuthProvider, useAuth } from './lib/auth';
import './App.css';

// Protected route component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();
  const location = useLocation();
  
  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  return <>{children}</>;
};

function AppContent() {
  const { user, loading } = useAuth();
  const isAuthenticated = !!user && !loading;
  
  // Layout with sidebar and header for authenticated users
  const AuthenticatedLayout = ({ children }: { children: React.ReactNode }) => (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-y-auto">
        <Header />
        <main className="flex-1 p-6 bg-[#0a0a0a]">
          {children}
        </main>
        <Footer />
      </div>
    </div>
  );

  return (
    <Routes>
      <Route path="/login" element={
        isAuthenticated ? <Navigate to="/" /> : <Login />
      } />
      <Route path="/register" element={
        isAuthenticated ? <Navigate to="/" /> : <Register />
      } />
      <Route path="/" element={
        <ProtectedRoute>
          <AuthenticatedLayout>
            <Home />
          </AuthenticatedLayout>
        </ProtectedRoute>
      } />
      <Route path="/prompt" element={
        <ProtectedRoute>
          <AuthenticatedLayout>
            <PromptToDSL />
          </AuthenticatedLayout>
        </ProtectedRoute>
      } />
      <Route path="/builder" element={
        <ProtectedRoute>
          <AuthenticatedLayout>
            <Builder />
          </AuthenticatedLayout>
        </ProtectedRoute>
      } />
      <Route path="/dsl-builder" element={
        <ProtectedRoute>
          <AuthenticatedLayout>
            <Builder />
          </AuthenticatedLayout>
        </ProtectedRoute>
      } />
      <Route path="/generate" element={
        <ProtectedRoute>
          <AuthenticatedLayout>
            <Generate />
          </AuthenticatedLayout>
        </ProtectedRoute>
      } />
      <Route path="/deploy" element={
        <ProtectedRoute>
          <AuthenticatedLayout>
            <Deploy />
          </AuthenticatedLayout>
        </ProtectedRoute>
      } />
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <AuthenticatedLayout>
            <Dashboard />
          </AuthenticatedLayout>
        </ProtectedRoute>
      } />
      <Route path="/notifications" element={
        <ProtectedRoute>
          <AuthenticatedLayout>
            <div className="p-6 bg-[#111111] rounded-lg border border-[#333333]">
              <h1 className="text-2xl font-bold mb-4">Notifications</h1>
              <p className="text-gray-400">You have no new notifications.</p>
            </div>
          </AuthenticatedLayout>
        </ProtectedRoute>
      } />
      <Route path="/docs" element={
        <ProtectedRoute>
          <AuthenticatedLayout>
            <div className="p-6 bg-[#111111] rounded-lg border border-[#333333]">
              <h1 className="text-2xl font-bold mb-4">Documentation</h1>
              <p className="text-gray-400 mb-4">Welcome to the InfraNest documentation.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                <div className="p-4 bg-[#1a1a1a] rounded-lg border border-[#333333]">
                  <h2 className="text-xl font-semibold mb-2">Getting Started</h2>
                  <p className="text-gray-400 mb-2">Learn the basics of InfraNest.</p>
                  <a href="#" className="text-[#00ff88] hover:underline">Read more →</a>
                </div>
                
                <div className="p-4 bg-[#1a1a1a] rounded-lg border border-[#333333]">
                  <h2 className="text-xl font-semibold mb-2">DSL Reference</h2>
                  <p className="text-gray-400 mb-2">Explore the Domain Specific Language.</p>
                  <a href="#" className="text-[#00ff88] hover:underline">Read more →</a>
                </div>
                
                <div className="p-4 bg-[#1a1a1a] rounded-lg border border-[#333333]">
                  <h2 className="text-xl font-semibold mb-2">API Documentation</h2>
                  <p className="text-gray-400 mb-2">Integrate with our API.</p>
                  <a href="#" className="text-[#00ff88] hover:underline">Read more →</a>
                </div>
                
                <div className="p-4 bg-[#1a1a1a] rounded-lg border border-[#333333]">
                  <h2 className="text-xl font-semibold mb-2">Deployment Guide</h2>
                  <p className="text-gray-400 mb-2">Deploy your applications.</p>
                  <a href="#" className="text-[#00ff88] hover:underline">Read more →</a>
                </div>
              </div>
            </div>
          </AuthenticatedLayout>
        </ProtectedRoute>
      } />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="min-h-screen bg-[#0a0a0a] text-white">
          <AppContent />
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1a1a1a',
                color: '#ffffff',
                border: '1px solid #333333',
                borderRadius: '8px',
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '14px',
              },
              success: {
                iconTheme: {
                  primary: '#00ff88',
                  secondary: '#000000',
                },
              },
              error: {
                iconTheme: {
                  primary: '#ff4444',
                  secondary: '#000000',
                },
              },
            }}
          />
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Chat from './components/Chat';
import Dashboard from './components/Dashboard';
import { ShieldCheck, LayoutDashboard, MessageSquare } from 'lucide-react';

export default function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col">
        <header className="bg-slate-900 text-white p-4 shadow-md">
          <div className="max-w-6xl mx-auto flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <ShieldCheck className="text-green-400" /> SAHAYA
              </h1>
              <p className="text-xs text-slate-400 mt-1">Multilingual Cooperative & Legal Assistance</p>
            </div>
            <nav className="flex gap-4">
              <Link to="/" className="flex items-center gap-1 hover:text-green-400 transition"><MessageSquare size={18}/> Chat</Link>
              <Link to="/officer" className="flex items-center gap-1 hover:text-green-400 transition"><LayoutDashboard size={18}/> Officer Dashboard</Link>
            </nav>
          </div>
        </header>
        <main className="flex-1 w-full max-w-6xl mx-auto p-4">
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/officer" element={<Dashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

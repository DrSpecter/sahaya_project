import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { AlertTriangle } from 'lucide-react';

export default function Dashboard() {
  const [tickets, setTickets] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/api/tickets').then(res => setTickets(res.data));
  }, []);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
        Officer Grievance Dashboard
      </h2>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-xs uppercase text-slate-500">
              <th className="p-3 font-semibold">Ticket ID</th>
              <th className="p-3 font-semibold">User Query</th>
              <th className="p-3 font-semibold">Confidence</th>
              <th className="p-3 font-semibold">Status</th>
              <th className="p-3 font-semibold">Action</th>
            </tr>
          </thead>
          <tbody>
            {tickets.length === 0 ? (
              <tr><td colSpan="5" className="p-6 text-center text-slate-400">No escalated tickets found.</td></tr>
            ) : tickets.map(t => (
              <tr key={t.id} className="border-b border-slate-100 hover:bg-slate-50 transition">
                <td className="p-3 font-mono text-xs text-slate-600">{t.id}</td>
                <td className="p-3 text-sm text-slate-800 max-w-md truncate">{t.query}</td>
                <td className="p-3 text-sm">
                  <span className="text-orange-600 font-semibold bg-orange-50 px-2 py-1 rounded">{(t.confidence * 100).toFixed(0)}%</span>
                </td>
                <td className="p-3">
                  <span className="text-xs font-bold text-slate-600 bg-slate-200 px-2 py-1 rounded">{t.status}</span>
                </td>
                <td className="p-3">
                  <button className="text-xs bg-slate-900 text-white px-3 py-1.5 rounded hover:bg-slate-800">Resolve</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

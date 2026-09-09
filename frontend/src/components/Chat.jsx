import React, { useState } from 'react';
import axios from 'axios';
import { Send, Mic, AlertTriangle, ShieldCheck, FileText, Globe } from 'lucide-react';

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [lang, setLang] = useState('en');

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', content: input };
    setMessages([...messages, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post('http://localhost:8000/api/chat', { query: input, language: lang });
      setMessages(prev => [...prev, { role: 'ai', data: res.data }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', error: "Connection to SAHAYA server failed." }]);
    }
    setLoading(false);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col h-[85vh]">
      <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50 rounded-t-xl">
        <div className="flex items-center gap-2">
          <span className="flex h-3 w-3 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </span>
          <span className="text-sm font-semibold text-slate-700">Verified Knowledge Base Active</span>
        </div>
        <div className="flex items-center gap-2">
          <Globe size={16} className="text-slate-500"/>
          <select className="bg-transparent text-sm text-slate-600 outline-none" value={lang} onChange={e => setLang(e.target.value)}>
            <option value="en">English</option>
            <option value="ta">தமிழ் (Tamil)</option>
            <option value="hi">हिन्दी (Hindi)</option>
          </select>
        </div>
      </div>

      <div className="flex-1 p-6 overflow-y-auto flex flex-col gap-6">
        {messages.length === 0 && (
          <div className="text-center text-slate-400 mt-20">
            <ShieldCheck size={48} className="mx-auto text-slate-300 mb-4" />
            <h2 className="text-xl font-semibold text-slate-600">No Evidence. No Answer.</h2>
            <p className="mt-2 text-sm">Ask about PMFBY, cooperative rules, schemes or grievances...</p>
            <div className="mt-8 flex justify-center gap-4 flex-wrap">
               <button onClick={() => setInput("What is the PMFBY claim procedure?")} className="px-4 py-2 bg-slate-100 rounded-full text-xs hover:bg-slate-200 text-slate-700">"What is the PMFBY claim procedure?"</button>
               <button onClick={() => setInput("I want to file a grievance about my claim.")} className="px-4 py-2 bg-slate-100 rounded-full text-xs hover:bg-slate-200 text-slate-700">"I want to file a grievance about my claim."</button>
            </div>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex flex-col max-w-[80%] ${msg.role === 'user' ? 'self-end items-end' : 'self-start items-start'}`}>
            {msg.role === 'user' ? (
              <div className="bg-slate-800 text-white px-5 py-3 rounded-2xl rounded-tr-sm">{msg.content}</div>
            ) : msg.error ? (
              <div className="bg-red-50 text-red-600 px-5 py-3 rounded-2xl rounded-tl-sm border border-red-100">{msg.error}</div>
            ) : msg.data.status === 'SUPPORTED' ? (
              <div className="bg-slate-50 border border-slate-200 p-5 rounded-2xl rounded-tl-sm w-full">
                <div className="flex items-center gap-2 mb-3">
                  <ShieldCheck size={18} className="text-green-600" />
                  <span className="text-xs font-bold text-green-700 bg-green-100 px-2 py-1 rounded-md">
                    Verified Answer (Confidence: {msg.data.confidence * 100}%)
                  </span>
                </div>
                <p className="text-slate-700 whitespace-pre-wrap">{msg.data.answer}</p>
                {msg.data.sources && msg.data.sources.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-slate-200">
                    <p className="text-xs font-semibold text-slate-500 mb-2 uppercase">Sources</p>
                    <div className="flex flex-wrap gap-2">
                      {msg.data.sources.map((s, i) => (
                        <div key={i} className="flex items-start gap-2 bg-white border border-slate-200 p-2 rounded-lg shadow-sm text-xs text-slate-600">
                          <FileText size={14} className="text-blue-500 shrink-0 mt-0.5" />
                          <div>
                            <p className="font-semibold">{s.document}</p>
                            <p className="text-[10px] text-slate-400">Page {s.page} • Sec: {s.section}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-orange-50 border border-orange-200 p-5 rounded-2xl rounded-tl-sm w-full">
                 <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle size={20} className="text-orange-600" />
                  <span className="text-xs font-bold text-orange-700 bg-orange-100 px-2 py-1 rounded-md">
                    Insufficient Verified Evidence (Confidence: {msg.data.confidence * 100}%)
                  </span>
                </div>
                <p className="text-slate-800 font-medium mb-1">Your query has been escalated to a human officer.</p>
                <p className="text-sm text-slate-600 mb-4">I couldn't find sufficient supporting evidence in the verified knowledge base to answer this safely. ({msg.data.reason})</p>
                <div className="bg-white border border-orange-200 px-4 py-3 rounded-lg flex justify-between items-center">
                  <div>
                    <p className="text-[10px] text-slate-400 uppercase font-bold">Ticket ID</p>
                    <p className="font-mono text-sm font-bold text-slate-700">{msg.data.ticket_id}</p>
                  </div>
                  <button className="text-xs bg-orange-100 text-orange-700 px-3 py-1.5 rounded-md font-semibold hover:bg-orange-200 transition">View Ticket</button>
                </div>
              </div>
            )}
          </div>
        ))}
        {loading && <div className="self-start text-slate-400 text-sm animate-pulse">SAHAYA is searching verified documents...</div>}
      </div>

      <div className="p-4 bg-white border-t border-slate-100 rounded-b-xl">
        <div className="flex items-center gap-2 max-w-4xl mx-auto">
          <button className="p-3 text-slate-400 hover:text-blue-500 hover:bg-blue-50 rounded-full transition"><Mic size={20}/></button>
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask about PMFBY, cooperative rules, schemes or grievances..."
            className="flex-1 bg-slate-50 border border-slate-200 rounded-full px-5 py-3 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400 transition"
          />
          <button onClick={sendMessage} className="p-3 bg-slate-900 text-white rounded-full hover:bg-slate-800 transition"><Send size={18}/></button>
        </div>
        <p className="text-center text-[10px] text-slate-400 mt-3">SAHAYA provides information from verified sources and does not replace advice from an authorized officer.</p>
      </div>
    </div>
  );
}

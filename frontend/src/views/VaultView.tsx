import React, { useEffect, useState } from 'react';
import { Database, Search, ExternalLink, Clock } from "lucide-react";
import type { TranscriptionRecord } from '../types';

const VaultView: React.FC = () => {
  const [records, setRecords] = useState<TranscriptionRecord[]>([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/history')
      .then(res => res.json())
      .then(data => setRecords(data));
  }, []);

  return (
    <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-center bg-[#1e293b] p-6 rounded-2xl border border-slate-800">
        <div className="flex items-center gap-4">
          <div className="bg-blue-600/20 p-3 rounded-xl border border-blue-500/30">
            <Database className="text-blue-400 w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold">Transcription Vault</h2>
            <p className="text-slate-500 text-sm italic">Local SQLite Persistence</p>
          </div>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input 
            type="text" 
            placeholder="Search hash or file..." 
            className="bg-slate-900 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 w-64"
          />
        </div>
      </div>

      <div className="bg-[#1e293b] rounded-2xl border border-slate-800 overflow-hidden shadow-2xl">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-800/50 text-slate-400 text-[10px] font-black uppercase tracking-widest">
              <th className="px-6 py-4">Timestamp</th>
              <th className="px-6 py-4">Source Hash</th>
              <th className="px-6 py-4">Model</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y border-slate-800 divide-slate-800">
            {records.map((rec) => (
              <tr key={rec.id} className="hover:bg-blue-500/5 transition-colors group">
                <td className="px-6 py-4 text-sm text-slate-300">
                  <div className="flex items-center gap-2">
                    <Clock className="w-3 h-3 text-slate-500" />
                    {new Date(rec.timestamp).toLocaleString()}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <code className="text-[10px] bg-slate-900 px-2 py-1 rounded text-blue-400 font-mono">
                    {rec.audio_hash.substring(0, 16)}...
                  </code>
                </td>
                <td className="px-6 py-4">
                  <span className="text-xs font-bold px-2 py-1 rounded bg-slate-800 border border-slate-700">
                    {rec.model_size}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <button className="text-slate-500 hover:text-white transition-colors p-2 rounded-lg hover:bg-slate-700">
                    <ExternalLink className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default VaultView;
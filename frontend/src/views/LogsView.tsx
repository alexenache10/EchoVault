import React, { useEffect, useState } from 'react';
import { Terminal, RefreshCw, AlertCircle } from "lucide-react";

const LogsView: React.FC = () => {
  const [logs, setLogs] = useState("");
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchLogs = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/logs?lines=150');
      const data = await res.json();
      if (data.status === "success") setLogs(data.logs);
    } catch (e) {
      console.error("Log fetch failed");
    }
  };

  useEffect(() => {
    fetchLogs();
    let interval: any;
    if (autoRefresh) {
      interval = setInterval(fetchLogs, 3000);
    }
    return () => clearInterval(interval);
  }, [autoRefresh]);

  return (
    <div className="h-full flex flex-col space-y-4 animate-in fade-in duration-700">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-3">
           <Terminal className="text-blue-500 w-5 h-5" />
           <h2 className="font-bold text-lg">System Diagnostics</h2>
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer">
            <input 
              type="checkbox" 
              checked={autoRefresh} 
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-slate-700 bg-slate-900 text-blue-600 focus:ring-blue-500"
            />
            Auto-refresh (3s)
          </label>
          <button onClick={fetchLogs} className="p-2 hover:bg-slate-800 rounded-lg transition-colors">
            <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin-slow' : ''}`} />
          </button>
        </div>
      </div>

      <div className="flex-1 bg-black/40 rounded-2xl border border-slate-800 p-6 font-mono text-[13px] overflow-y-auto custom-scrollbar shadow-inner">
        {logs.split("\n").map((line, i) => {
          const isError = line.includes("| ERROR |");
          const isInfo = line.includes("| INFO |");
          return (
            <div key={i} className={`py-0.5 border-l-2 pl-4 mb-1 ${
              isError ? 'border-red-500 bg-red-500/5 text-red-200' : 
              isInfo ? 'border-blue-500 bg-blue-500/5 text-slate-300' : 'border-slate-800 text-slate-500'
            }`}>
              <span className="opacity-50 mr-4">{i + 1}</span>
              {line}
            </div>
          );
        })}
        {logs === "" && (
          <div className="flex flex-col items-center justify-center h-full text-slate-600 opacity-50 gap-4">
             <AlertCircle className="w-12 h-12" />
             <p>No system logs recorded yet</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LogsView;
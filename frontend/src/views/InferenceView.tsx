import React, { useState, useEffect } from 'react';
import { Play, Cpu, Zap, LayoutList, AlignLeft, Video, Activity, Square, Globe } from "lucide-react";
import { useVaultStore } from '../store/useVaultStore';
import { useTranscriptionWS } from '../hooks/useWebSocket';
import { WHISPER_MODELS } from '../utils/models';
import { formatTimestamp } from '../utils/time';

const InferenceView: React.FC = () => {
  const [filePath, setFilePath] = useState("");
  const [modelSize, setModelSize] = useState("base");
  const [language, setLanguage] = useState("ro"); // Default Romanian
  const [targetDevice, setTargetDevice] = useState("cuda");
  const [displayMode, setDisplayMode] = useState<'timeline' | 'reading'>('timeline');
  const [hwStats, setHwStats] = useState({ device: "cpu", vram_usage: 0, vram_total: 1 });

  const { currentSegments, isProcessing, setProcessing } = useVaultStore();
  const { startTranscription } = useTranscriptionWS();

  useEffect(() => {
    const fetchHW = () => 
      fetch('http://localhost:8000/api/v1/hardware')
        .then(r => r.json())
        .then(setHwStats)
        .catch(err => console.error("Hardware Telemetry Offline"));
    
    fetchHW();
    const interval = setInterval(fetchHW, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleStop = async () => {
    try {
      await fetch('http://localhost:8000/api/v1/transcribe/stop', { method: 'POST' });
      setProcessing(false);
    } catch (e) {
      console.error("Failed to send stop signal");
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div className="xl:col-span-2 space-y-6">
          <div className="vault-panel p-8">
            <div className="flex flex-col gap-6">
              <div>
                <label className="text-[10px] uppercase font-black text-slate-500 mb-2 block tracking-widest">Target Resource Path</label>
                <input 
                  type="text" 
                  placeholder="/mnt/d/path/to/media.mp4"
                  className="w-full input-tactical"
                  value={filePath}
                  onChange={(e) => setFilePath(e.target.value)}
                  disabled={isProcessing}
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label className="text-[10px] uppercase font-black text-slate-500 tracking-widest">AI Model</label>
                  <select 
                    value={modelSize} 
                    onChange={(e) => setModelSize(e.target.value)}
                    disabled={isProcessing}
                    className="w-full input-tactical h-[42px]"
                  >
                    {WHISPER_MODELS.map(m => (
                      <option key={m.id} value={m.id}>{"★".repeat(m.stars).padEnd(5, "☆")} {m.label}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] uppercase font-black text-slate-500 tracking-widest">Inference Language</label>
                  <div className="relative">
                    <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <select 
                      value={language} 
                      onChange={(e) => setLanguage(e.target.value)}
                      disabled={isProcessing}
                      className="w-full input-tactical pl-10 h-[42px]"
                    >
                      <option value="ro">Romanian</option>
                      <option value="en">English</option>
                      <option value="de">German</option>
                      <option value="fr">French</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] uppercase font-black text-slate-500 tracking-widest">Compute Unit</label>
                  <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800 h-[42px]">
                    <button 
                      disabled={isProcessing}
                      onClick={() => setTargetDevice("cuda")}
                      className={`flex-1 flex items-center justify-center gap-2 rounded-md text-[10px] font-black transition-all ${targetDevice === 'cuda' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
                    ><Cpu size={12}/> GPU</button>
                    <button 
                      disabled={isProcessing}
                      onClick={() => setTargetDevice("cpu")}
                      className={`flex-1 flex items-center justify-center gap-2 rounded-md text-[10px] font-black transition-all ${targetDevice === 'cpu' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
                    ><Activity size={12}/> CPU</button>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex gap-4 mt-8">
              {!isProcessing ? (
                <button 
                  onClick={() => startTranscription(filePath, modelSize, language, targetDevice)}
                  disabled={!filePath}
                  className="flex-1 btn-primary py-3 flex items-center justify-center gap-3"
                >
                  <Zap size={18} className="fill-current" /> RUN ENGINE
                </button>
              ) : (
                <div className="flex-1 flex items-center justify-between bg-blue-500/5 border border-blue-500/20 px-6 py-3 rounded-xl">
                  <div className="flex items-center gap-3">
                    <div className="relative flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
                    </div>
                    <span className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-400">Processing Stream...</span>
                  </div>
                  <button onClick={handleStop} className="btn-stop p-2 w-10 h-10 group" title="Emergency Stop">
                    <Square size={16} className="fill-current group-hover:scale-90 transition-transform" />
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="bg-slate-950/50 rounded-2xl border border-slate-800/50 overflow-hidden h-[450px] flex flex-col shadow-inner">
            <div className="bg-slate-900/80 px-6 py-3 border-b border-slate-800 flex justify-between items-center">
              <div className="flex gap-2">
                <button onClick={() => setDisplayMode('timeline')} className={`p-2 rounded-md transition-colors ${displayMode === 'timeline' ? 'text-blue-400 bg-blue-400/10' : 'text-slate-500'}`}><LayoutList size={18} /></button>
                <button onClick={() => setDisplayMode('reading')} className={`p-2 rounded-md transition-colors ${displayMode === 'reading' ? 'text-blue-400 bg-blue-400/10' : 'text-slate-500'}`}><AlignLeft size={18} /></button>
              </div>
              <span className="text-[9px] font-mono text-slate-500 uppercase tracking-widest">Output://Stream_Terminal</span>
            </div>
            <div className="flex-1 overflow-y-auto p-6 custom-scrollbar terminal-stream">
              {currentSegments.map((s, i) => (
                <div key={i} className={`gap-6 py-1 ${displayMode === 'reading' ? 'inline' : 'flex border-b border-slate-800/30'}`}>
                   {displayMode === 'timeline' && <span className="text-blue-500/80 w-24 shrink-0 font-bold">[{formatTimestamp(s.start)}]</span>}
                   <span className="text-slate-300 antialiased">{s.text} </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="vault-panel p-6 shadow-xl">
             <h4 className="text-[10px] font-black uppercase text-slate-500 mb-4 tracking-widest flex items-center gap-2"><Video size={14} className="text-blue-500" /> Media Preview</h4>
             <video 
                className="w-full aspect-video bg-black rounded-lg border border-slate-800 shadow-2xl"
                controls
                src={filePath ? `http://localhost:8000/api/v1/stream?path=${encodeURIComponent(filePath)}` : undefined}
             />
          </div>

          <div className="vault-panel p-6 shadow-xl">
             <h4 className="text-[10px] font-black uppercase text-slate-500 mb-4 tracking-widest">Hardware Telemetry</h4>
             <div className="space-y-4">
               <div>
                 <div className="flex justify-between text-[10px] mb-2">
                   <span className="text-slate-400 font-bold uppercase">VRAM Usage</span>
                   <span className="text-blue-400 font-mono">{hwStats.vram_usage.toFixed(2)} GB</span>
                 </div>
                 <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden border border-slate-800">
                    <div className="bg-blue-600 h-full transition-all duration-1000" style={{ width: `${(hwStats.vram_usage / hwStats.vram_total) * 100}%` }} />
                 </div>
               </div>
               <p className="text-[9px] text-slate-600 italic">Target: {hwStats.device.toUpperCase()} Control</p>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InferenceView;
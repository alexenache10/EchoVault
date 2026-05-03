import React, { useState, useRef } from 'react';
import { Upload, Play, Cpu, Zap, CheckCircle2 } from "lucide-react";
import { useVaultStore } from '../store/useVaultStore';
import { useTranscriptionWS } from '../hooks/useWebSocket';

const InferenceView: React.FC = () => {
  const [filePath, setFilePath] = useState("");
  const [modelSize, setModelSize] = useState("base");
  const videoRef = useRef<HTMLVideoElement>(null);
  
  const { currentSegments, isProcessing } = useVaultStore();
  const { startTranscription } = useTranscriptionWS();

  const handleStart = () => {
    if (filePath) startTranscription(filePath, modelSize, "ro");
  };

  const seekTo = (seconds: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = seconds;
      videoRef.current.play();
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div className="xl:col-span-2 space-y-6">
          {/* Configurare Sursă */}
          <div className="bg-[#1e293b] p-8 rounded-2xl border border-slate-800 shadow-2xl">
            <div className="flex flex-col items-center justify-center border-2 border-dashed border-slate-700 rounded-xl p-10 hover:border-blue-500/50 transition-all group">
              <Upload className="w-10 h-10 text-slate-500 group-hover:text-blue-400 mb-4 transition-colors" />
              <input 
                type="text" 
                placeholder="Paste absolute file path (e.g. C:\media\video.mp4)"
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
              />
            </div>
            
            <div className="flex gap-4 mt-6">
              <div className="flex-1 flex items-center gap-3 bg-slate-900 px-4 rounded-lg border border-slate-700">
                <Cpu className="w-4 h-4 text-blue-400" />
                <select 
                  value={modelSize}
                  onChange={(e) => setModelSize(e.target.value)}
                  className="bg-transparent w-full py-2.5 text-sm outline-none"
                >
                  <option value="base">Whisper Base (Fast)</option>
                  <option value="large-v3">Whisper Large V3 (Accurate)</option>
                </select>
              </div>
              <button 
                onClick={handleStart}
                disabled={isProcessing || !filePath}
                className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 px-8 rounded-lg font-bold flex items-center gap-2 transition-all shadow-lg shadow-blue-900/20"
              >
                {isProcessing ? <Zap className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
                Run Engine
              </button>
            </div>
          </div>

          {/* Terminal Segmente */}
          <div className="bg-[#0f172a] rounded-2xl border border-slate-800 overflow-hidden h-[400px] flex flex-col shadow-inner">
            <div className="bg-slate-800/50 px-6 py-3 border-b border-slate-800 flex justify-between items-center">
              <span className="text-xs font-black uppercase tracking-widest text-slate-400">Transcription Stream</span>
              {isProcessing && <span className="text-[10px] text-blue-400 animate-pulse font-mono">LIVE_INFERENCE_ACTIVE</span>}
            </div>
            <div className="flex-1 overflow-y-auto p-6 space-y-3 font-mono text-sm custom-scrollbar">
              {currentSegments.map((s, i) => (
                <div 
                  key={i} 
                  onClick={() => seekTo(s.start)}
                  className="flex gap-4 p-2 rounded-lg hover:bg-blue-500/10 cursor-pointer transition-colors border border-transparent hover:border-blue-500/20 group"
                >
                  <span className="text-blue-500 font-bold w-16 group-hover:scale-110 transition-transform">[{s.start}s]</span>
                  <span className="text-slate-300">{s.text}</span>
                </div>
              ))}
              {currentSegments.length === 0 && !isProcessing && (
                <p className="text-slate-600 italic">No active process. Waiting for input...</p>
              )}
            </div>
          </div>
        </div>

        {/* Player & Stats */}
        <div className="space-y-6">
          <div className="bg-[#1e293b] p-6 rounded-2xl border border-slate-800 shadow-xl">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-tighter mb-4 flex items-center gap-2">
              <Play className="w-4 h-4 fill-blue-500 text-blue-500" /> Media Preview
            </h3>
            <video 
              ref={videoRef}
              controls 
              className="w-full aspect-video bg-black rounded-lg shadow-2xl"
              src={filePath ? `http://localhost:8000/api/v1/stream?path=${encodeURIComponent(filePath)}` : undefined}
            />
          </div>
          
          <div className="bg-blue-600/10 border border-blue-500/20 p-6 rounded-2xl">
            <h4 className="text-blue-400 text-xs font-black uppercase mb-2">Engine Status</h4>
            <div className="space-y-2">
               <div className="flex justify-between text-xs">
                 <span className="text-slate-400">VRAM Usage:</span>
                 <span className="text-slate-200 font-mono">~2.4 GB</span>
               </div>
               <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                 <div className="bg-blue-500 h-full w-[45%]" />
               </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InferenceView;
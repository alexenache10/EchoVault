import React from 'react';
import { 
  PlusCircle, 
  Database, 
  Terminal, 
  LayoutGrid,
  Activity
} from "lucide-react";
import { useVaultStore } from './store/useVaultStore';
import InferenceView from './views/InferenceView';
import VaultView from './views/VaultView';
import LogsView from './views/LogsView';

const App: React.FC = () => {
  const { activeView, setActiveView, isSidebarOpen } = useVaultStore();

  return (
    <div className="flex h-screen bg-[#0f172a] text-slate-50 overflow-hidden font-sans">
      <aside className={`${isSidebarOpen ? "w-64" : "w-20"} bg-[#1e293b] border-r border-slate-800 transition-all duration-300 flex flex-col`}>
        <div className="p-6 flex items-center gap-3 border-b border-slate-800/50">
          <Activity className="w-6 h-6 text-blue-500" />
          {isSidebarOpen && <h1 className="font-black text-xl tracking-tighter uppercase">EchoVault</h1>}
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <NavButton 
            id="new" 
            icon={<PlusCircle />} 
            label="Inference" 
          />
          <NavButton 
            id="history" 
            icon={<Database />} 
            label="The Vault" 
          />
          <NavButton 
            id="logs" 
            icon={<Terminal />} 
            label="System Logs" 
          />
        </nav>
      </aside>

      <main className="flex-1 flex flex-col relative overflow-hidden">
        <header className="h-16 border-b border-slate-800/50 flex items-center px-8 justify-between bg-[#0f172a]/80 backdrop-blur-md z-10">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-widest">
            <LayoutGrid className="w-4 h-4" />
            <span>Workspace / {activeView}</span>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
          {activeView === 'new' && <InferenceView />}
          {activeView === 'history' && <VaultView />}
          {activeView === 'logs' && <LogsView />}
        </div>
      </main>
    </div>
  );
};

const NavButton = ({ id, icon, label }: { id: any, icon: any, label: string }) => {
  const { activeView, setActiveView, isSidebarOpen } = useVaultStore();
  const isActive = activeView === id;

  return (
    <button
      onClick={() => setActiveView(id)}
      className={`w-full flex items-center gap-4 px-4 py-3 rounded-xl transition-all ${
        isActive 
        ? "bg-blue-600 text-white shadow-lg shadow-blue-900/20" 
        : "text-slate-400 hover:bg-slate-800"
      }`}
    >
      {React.cloneElement(icon as React.ReactElement, { size: 20 })}
      {isSidebarOpen && <span className="font-semibold text-sm">{label}</span>}
    </button>
  );
};

export default App;
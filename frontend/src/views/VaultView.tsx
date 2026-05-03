import React, { useEffect, useState } from 'react';
import { Database, Search, FileDown, Clock, Hash, Cpu, FileAudio } from "lucide-react";
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import type { TranscriptionRecord } from '../types';
import { formatTimestamp } from '../utils/time';

const VaultView: React.FC = () => {
  const [records, setRecords] = useState<TranscriptionRecord[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/history')
      .then(res => res.json())
      .then(data => setRecords(data))
      .catch(err => console.error(err));
  }, []);

  const getFileName = (path: string) => {
    if (!path) return "Unknown";
    return path.split(/[/\\]/).pop() || path;
  };

  const sanitizeText = (text: string) => {
    return text
      .replace(/ș/g, 's').replace(/ț/g, 't')
      .replace(/ă/g, 'a').replace(/î/g, 'i').replace(/â/g, 'a')
      .replace(/Ș/g, 'S').replace(/Ț/g, 'T')
      .replace(/Ă/g, 'A').replace(/Î/g, 'I').replace(/Â/g, 'A');
  };

  const exportToPDF = (rec: TranscriptionRecord) => {
    const doc = new jsPDF();
    
    doc.setFillColor(15, 23, 42);
    doc.rect(0, 0, 210, 35, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(18);
    doc.text("EchoVault - Report", 14, 22);

    autoTable(doc, {
      startY: 40,
      body: [
        ["Filename", sanitizeText(getFileName(rec.file_path))], 
        ["Absolute Path", sanitizeText(rec.file_path)],
        ["Audio Hash", rec.audio_hash],
        ["Model", rec.model_size.toUpperCase()],
        ["Data", new Date(rec.timestamp + 'Z').toLocaleString('ro-RO')]
      ],
      styles: { fontSize: 9, cellPadding: 3 },
      columnStyles: { 0: { fontStyle: 'bold', cellWidth: 35 } }
    });

    const fullText = rec.transcript_json.map(s => s.text).join(" ");
    const sanitizedText = sanitizeText(fullText);
    
    autoTable(doc, {
      startY: (doc as any).lastAutoTable.finalY + 10,
      body: [[sanitizedText]],
      theme: 'plain',
      styles: { 
        fontSize: 10, 
        lineHeight: 1.5,
        halign: 'justify'
      }
    });

    doc.save(`Raport_EchoVault_${rec.audio_hash.substring(0, 8)}.pdf`);
  };

  const filteredRecords = records.filter(r => 
    r.file_path.toLowerCase().includes(searchQuery.toLowerCase()) || 
    r.audio_hash.includes(searchQuery)
  );

  return (
    <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-[#1e293b] p-6 rounded-2xl border border-slate-800 gap-4">
        <div className="flex items-center gap-4">
          <div className="bg-blue-600/20 p-3 rounded-xl border border-blue-500/30">
            <Database className="text-blue-400 w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold tracking-tight">Transcription Vault</h2>
            <p className="text-slate-500 text-sm italic">Encrypted Local Storage</p>
          </div>
        </div>
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input 
            type="text" 
            placeholder="Search file path or hash..." 
            className="bg-slate-900 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 w-full transition-all"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <div className="bg-[#1e293b] rounded-2xl border border-slate-800 overflow-hidden shadow-2xl">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-800/50 text-slate-400 text-[10px] font-black uppercase tracking-widest border-b border-slate-800">
              <th className="px-6 py-4">Data</th>
              <th className="px-6 py-4">Fisier Sursa</th>
              <th className="px-6 py-4">Identity (Hash)</th>
              <th className="px-6 py-4">Configuratie</th>
              <th className="px-6 py-4 text-right">Actiuni</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {filteredRecords.map((rec) => (
              <tr key={rec.id} className="vault-row">
                <td className="px-6 py-4 text-sm text-slate-300">
                  <div className="flex items-center gap-2">
                    <Clock className="w-3.5 h-3.5 text-slate-500" />
                    {new Date(rec.timestamp).toLocaleString('ro-RO')}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <FileAudio className="w-3.5 h-3.5 text-blue-500/80" />
                    <span className="text-sm font-medium text-slate-300 truncate max-w-[200px] block" title={rec.file_path}>
                      {getFileName(rec.file_path)}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <Hash className="w-3 h-3 text-blue-500/50" />
                    <code className="text-[10px] bg-slate-900 px-2 py-1 rounded text-blue-400 font-mono border border-slate-700/50">
                      {rec.audio_hash.substring(0, 12)}...
                    </code>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-3.5 h-3.5 text-slate-500" />
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400 uppercase tracking-tighter">
                      {rec.model_size}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 text-right">
                  <button 
                    onClick={() => exportToPDF(rec)}
                    className="bg-blue-600/10 text-blue-500 hover:bg-blue-600 hover:text-white transition-all p-2.5 rounded-xl border border-blue-500/20 active:scale-95"
                    title="Export as PDF"
                  >
                    <FileDown size={18} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filteredRecords.length === 0 && (
          <div className="p-20 text-center text-slate-600 italic">
            Niciun record gasit in baza de date.
          </div>
        )}
      </div>
    </div>
  );
};

export default VaultView;
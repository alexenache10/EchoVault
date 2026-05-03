import { create } from 'zustand';
import type { Segment, TranscriptionRecord } from '../types';

interface VaultState {
  isSidebarOpen: boolean;
  activeView: 'new' | 'history' | 'logs';
  currentSegments: Segment[];
  history: TranscriptionRecord[];
  isProcessing: boolean;
  
  setSidebarOpen: (open: boolean) => void;
  setActiveView: (view: 'new' | 'history' | 'logs') => void;
  addSegment: (segment: Segment) => void;
  resetSegments: () => void;
  setProcessing: (processing: boolean) => void;
  setHistory: (records: TranscriptionRecord[]) => void;
}

export const useVaultStore = create<VaultState>((set) => ({
  isSidebarOpen: true,
  activeView: 'new',
  currentSegments: [],
  history: [],
  isProcessing: false,

  setSidebarOpen: (open) => set({ isSidebarOpen: open }),
  setActiveView: (view) => set({ activeView: view }),
  addSegment: (segment) => set((state) => ({ 
    currentSegments: [...state.currentSegments, segment] 
  })),
  resetSegments: () => set({ currentSegments: [] }),
  setProcessing: (processing) => set({ isProcessing: processing }),
  setHistory: (records) => set({ history: records }),
}));
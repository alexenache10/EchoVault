import { useCallback, useRef } from 'react';
import { useVaultStore } from '../store/useVaultStore';
import type { WSMessage } from '../types';

export const useTranscriptionWS = () => {
  const socketRef = useRef<WebSocket | null>(null);
  const { addSegment, setProcessing, resetSegments } = useVaultStore();

  const startTranscription = useCallback((filePath: string, modelSize: string, language: string, device: string) => {
    resetSegments();
    setProcessing(true);

    const socket = new WebSocket('ws://localhost:8000/api/v1/ws/transcribe');
    socketRef.current = socket;

    socket.onopen = () => {

      socket.send(JSON.stringify({
        file_path: filePath,
        model_size: modelSize,
        language: language,
        device: device
      }));
    };

    socket.onmessage = (event) => {
      const data: WSMessage = JSON.parse(event.data);
      
      switch (data.event) {
        case 'segment':
          addSegment(data.payload);
          break;
        case 'completed':
          setProcessing(false);
          socket.close();
          break;
        case 'error':
          console.error("WS Error:", data.payload);
          setProcessing(false);
          break;
      }
    };

    socket.onclose = () => setProcessing(false);
  }, [addSegment, setProcessing, resetSegments]);

  return { startTranscription };
};
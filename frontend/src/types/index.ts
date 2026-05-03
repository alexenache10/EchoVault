export interface Segment {
  start: number;
  end: number;
  text: string;
}

export interface TranscriptionRecord {
  id: number;
  timestamp: string;
  file_path: string;
  model_size: string;
  audio_hash: string;
  language: string;
  transcript_json: Segment[];
}

export interface WSMessage {
  event: 'info' | 'segment' | 'status' | 'error' | 'completed';
  payload: any;
}
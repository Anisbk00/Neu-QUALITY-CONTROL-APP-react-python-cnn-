/**
 * TypeScript type definitions for the application
 */

export interface AnalysisResult {
  predicted_class: string;
  class_probs: {
    [key: string]: number;
  };
  anomaly_score: number;
}

export interface PieceData {
  id: string;
  filename: string;
  status: 'uploaded' | 'analyzed' | 'validated' | 'rejected';
  analysis_results?: AnalysisResult;
  uploaded_at: string;
  analyzed_at?: string;
}

export interface UploadResponse {
  piece_id: string;
  filename: string;
  message: string;
}

export interface AnalyzeResponse {
  piece_id: string;
  results: AnalysisResult;
}

export type CameraView = 'iso' | 'front' | 'left' | 'right' | 'top';

/**
 * API client utilities (updated for safe analysis)
 */

import axios from 'axios';
import type { UploadResponse, AnalyzeResponse, PieceData, AnalysisResult } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiClient = {
  /**
   * Upload a 3D model file
   */
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<UploadResponse>('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * Analyze captured views
   * Ensures all images are non-empty base64 strings before sending.
   */
  async analyze(pieceId: string, images: string[]): Promise<AnalysisResult> {
    if (!images || images.length === 0) {
      throw new Error('No images provided for analysis');
    }

    // Validate base64 strings
    const sanitizedImages = images.map((img, i) => {
      if (!img || typeof img !== 'string' || img.length < 100) {
        console.warn(`Image ${i} is empty or invalid (length: ${img?.length || 0})`);
      }

      // Optionally strip the data URL prefix if backend needs pure base64
      if (img.includes(',')) {
        return img.split(',')[1];
      }
      return img;
    });

    console.log('Sending images for analysis, count:', sanitizedImages.length);

    const response = await api.post<AnalyzeResponse>('/api/analyze', {
      piece_id: pieceId,
      images: sanitizedImages,
    });

    return response.data.results;
  },

  /**
   * Generate report
   */
  async generateReport(pieceId: string, notes: string = ''): Promise<void> {
    await api.post('/api/report', {
      piece_id: pieceId,
      notes,
    });
  },

  /**
   * Validate piece
   */
  async validatePiece(pieceId: string, notes: string = ''): Promise<void> {
    await api.post('/api/validate', {
      piece_id: pieceId,
      status: 'validated',
      notes,
    });
  },

  /**
   * Reject piece
   */
  async rejectPiece(pieceId: string, notes: string = ''): Promise<void> {
    await api.post('/api/reject', {
      piece_id: pieceId,
      status: 'rejected',
      notes,
    });
  },

  /**
   * Get piece information
   */
  async getPiece(pieceId: string): Promise<PieceData> {
    const response = await api.get<PieceData>(`/api/pieces/${pieceId}`);
    return response.data;
  },

  /**
   * Get all classes
   */
  async getClasses(): Promise<string[]> {
    const response = await api.get<{ classes: string[] }>('/api/classes');
    return response.data.classes;
  },
};

/**
 * Main Application Component
 */

import React, { useState } from 'react';
import LeftPanel from './components/LeftPanel';
import Viewer3D from './components/Viewer3D';
import RightPanel from './components/RightPanel';
import Footer from './components/Footer';
import { apiClient } from './utils/api';
import type { AnalysisResult } from './types';
import './App.css';

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [pieceId, setPieceId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile);
    setIsUploading(true);
    setError(null);
    setAnalysisResults(null);

    try {
      const response = await apiClient.uploadFile(selectedFile);
      setPieceId(response.piece_id);
      console.log('File uploaded:', response);
    } catch (err) {
      setError('Échec du téléchargement du fichier');
      console.error('Upload error:', err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleViewsCapture = async (images: string[]) => {
    if (!pieceId) {
      setError('Aucune pièce chargée');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      console.log(`Analyzing ${images.length} views...`);
      const results = await apiClient.analyze(pieceId, images);
      setAnalysisResults(results);
      console.log('Analysis complete:', results);
    } catch (err) {
      setError('Échec de l\'analyse');
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSaveReport = async () => {
    if (!pieceId) return;

    try {
      await apiClient.generateReport(pieceId);
      alert('Rapport enregistré avec succès');
    } catch (err) {
      alert('Échec de l\'enregistrement du rapport');
      console.error('Report error:', err);
    }
  };

  const handleReject = async () => {
    if (!pieceId) return;

    if (confirm('Êtes-vous sûr de vouloir rejeter cette pièce ?')) {
      try {
        await apiClient.rejectPiece(pieceId);
        alert('Pièce rejetée');
        // Reset state
        setFile(null);
        setPieceId(null);
        setAnalysisResults(null);
      } catch (err) {
        alert('Échec du rejet');
        console.error('Reject error:', err);
      }
    }
  };

  const handleValidate = async () => {
    if (!pieceId) return;

    try {
      await apiClient.validatePiece(pieceId);
      alert('Pièce validée avec succès ✅');
      // Reset state
      setFile(null);
      setPieceId(null);
      setAnalysisResults(null);
    } catch (err) {
      alert('Échec de la validation');
      console.error('Validate error:', err);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <button className="menu-button">☰</button>
        </div>
        <h1 className="header-title">CONTRÔLE QUALITÉ VISUEL</h1>
        <div className="header-right">
          <button className="header-btn">🔄 Recharger</button>
          <button className="header-btn">⚙️ Paramètres</button>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      <div className="main-content">
        <LeftPanel
          pieceId={pieceId}
          onFileSelect={handleFileSelect}
          isLoading={isUploading}
        />

        <div className="center-panel">
          <div className="render-status">
            <span className={`status-indicator ${file ? 'active' : ''}`}>●</span>
            RENDU 3D {file ? 'ACTIF' : 'INACTIF'}
          </div>

          <Viewer3D
            file={file}
            onViewsCapture={handleViewsCapture}
          />
        </div>

        <RightPanel
          results={analysisResults}
          isAnalyzing={isAnalyzing}
        />
      </div>

      <Footer
        pieceId={pieceId}
        hasResults={!!analysisResults}
        onSaveReport={handleSaveReport}
        onReject={handleReject}
        onValidate={handleValidate}
        isLoading={isAnalyzing}
      />
    </div>
  );
};

export default App;

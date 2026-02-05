/**
 * Right Panel Component - Analysis Results
 */

import React from 'react';
import type { AnalysisResult } from '../types';

interface RightPanelProps {
  results: AnalysisResult | null;
  isAnalyzing: boolean;
}

const CLASS_DISPLAY_NAMES: { [key: string]: string } = {
  'crazing': 'Crazing',
  'inclusion': 'Inclusion',
  'patches': 'Patches',
  'pitted_surface': 'Surface Piquée',
  'rolled-in_scale': 'Écaille Roulée',
  'scratches': 'Rayures',
};

const RightPanel: React.FC<RightPanelProps> = ({ results, isAnalyzing }) => {
  const getDisplayName = (className: string): string => {
    return CLASS_DISPLAY_NAMES[className] || className;
  };

  const getStatusColor = (score: number): string => {
    if (score >= 70) return '#ff4444';
    if (score >= 50) return '#ffaa00';
    return '#44ff44';
  };

  return (
    <div className="right-panel">
      <h2>MESURE 3D / IA</h2>

      <div className="analyze-status">
        {isAnalyzing && (
          <div className="analyzing-indicator">
            <span className="spinner">⏳</span>
            Analyse en cours...
          </div>
        )}
      </div>

      <div className="results-section">
        <h3>RÉSULTATS D'ANALYSE</h3>

        {!results && !isAnalyzing && (
          <div className="no-results">
            <p>Aucune analyse disponible</p>
            <p className="hint">Importez une pièce et lancez l'analyse automatique</p>
          </div>
        )}

        {results && (
          <>
            <div className="result-main">
              <div className="result-label">Anomalie</div>
              <div className="result-value" style={{ color: getStatusColor(results.anomaly_score) }}>
                Probabilité {Math.round(results.anomaly_score)}%
              </div>
            </div>

            <div className="predicted-class">
              <strong>Classe détectée:</strong>
              <div className="class-badge">
                {getDisplayName(results.predicted_class)}
              </div>
            </div>

            <div className="class-probabilities">
              <h4>Probabilités par classe:</h4>
              {Object.entries(results.class_probs)
                .sort(([, a], [, b]) => b - a)
                .map(([className, prob]) => (
                  <div key={className} className="prob-row">
                    <span className="prob-label">{getDisplayName(className)}</span>
                    <div className="prob-bar-container">
                      <div
                        className="prob-bar"
                        style={{
                          width: `${prob * 100}%`,
                          backgroundColor: className === results.predicted_class ? '#4a9eff' : '#ccc',
                        }}
                      />
                    </div>
                    <span className="prob-value">{(prob * 100).toFixed(1)}%</span>
                  </div>
                ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default RightPanel;

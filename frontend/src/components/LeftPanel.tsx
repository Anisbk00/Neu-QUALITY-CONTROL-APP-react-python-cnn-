/**
 * Left Panel Component
 */

import React from 'react';

interface LeftPanelProps {
  pieceId: string | null;
  onFileSelect: (file: File) => void;
  isLoading: boolean;
}

const LeftPanel: React.FC<LeftPanelProps> = ({ pieceId, onFileSelect, isLoading }) => {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  };

  return (
    <div className="left-panel">
      <button className="import-button" onClick={() => document.getElementById('file-input')?.click()}>
        <span className="icon">⬆</span>
        Importer une pièce
      </button>
      
      <input
        id="file-input"
        type="file"
        accept=".stl,.obj,.gltf,.glb"
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />

      <button className="model-selector" disabled>
        <span className="icon">🤖</span>
        Sélectionner un modèle
      </button>

      <div className="piece-id-section">
        <label>ID pièce:</label>
        <input
          type="text"
          value={pieceId || ''}
          readOnly
          placeholder={isLoading ? 'Chargement...' : 'Aucune pièce'}
          className="piece-id-input"
        />
      </div>

      <div className="import-preview-section">
        <h3>IMPORTER UNE PIÈCE 3D</h3>
        <div className="preview-box">
          <div className="preview-icon">📦</div>
          <p>Aperçu miniature</p>
        </div>
      </div>

      <div className="inspection-summary">
        <h3>📋 RÉSUMÉ DE L'INSPECTION</h3>
        <div className="summary-row">
          <span>Défaut</span>
          <span>Probabilité</span>
        </div>
      </div>
    </div>
  );
};

export default LeftPanel;

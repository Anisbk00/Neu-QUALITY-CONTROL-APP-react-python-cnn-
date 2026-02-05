/**
 * Footer Component - Action Buttons (Fully functional)
 */

import React, { useState } from 'react';
import { apiClient } from '../utils/api';

interface FooterProps {
  pieceId: string | null;
  hasResults: boolean;
  isLoading: boolean;
  onStatusChange?: () => void; // callback after validate/reject/report
}

const Footer: React.FC<FooterProps> = ({ pieceId, hasResults, isLoading, onStatusChange }) => {
  const [actionLoading, setActionLoading] = useState(false);

  const canAct = !!pieceId && hasResults && !isLoading && !actionLoading;

  const handleSaveReport = async () => {
    if (!pieceId) return;
    try {
      setActionLoading(true);
      await apiClient.generateReport(pieceId);
      alert('📄 Rapport généré avec succès');
      onStatusChange?.();
    } catch (err: any) {
      console.error('Report generation failed:', err);
      alert(`❌ Échec de la génération du rapport: ${err?.message || err}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleValidate = async () => {
    if (!pieceId) return;
    const confirm = window.confirm('✅ Confirmer la validation de la pièce ?');
    if (!confirm) return;

    try {
      setActionLoading(true);
      await apiClient.validatePiece(pieceId);
      alert('✅ Pièce validée avec succès');
      onStatusChange?.();
    } catch (err: any) {
      console.error('Validation failed:', err);
      alert(`❌ Échec de la validation: ${err?.message || err}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!pieceId) return;
    const confirm = window.confirm('❌ Confirmer le rejet de la pièce ?');
    if (!confirm) return;

    try {
      setActionLoading(true);
      await apiClient.rejectPiece(pieceId);
      alert('❌ Pièce rejetée');
      onStatusChange?.();
    } catch (err: any) {
      console.error('Rejection failed:', err);
      alert(`❌ Échec du rejet: ${err?.message || err}`);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="footer" style={{ display: 'flex', gap: 8, marginTop: 12 }}>
      <button
        className="btn btn-secondary"
        onClick={handleSaveReport}
        disabled={!canAct}
      >
        📄 Enregistrer rapport
      </button>

      <button
        className="btn btn-reject"
        onClick={handleReject}
        disabled={!canAct}
      >
        ❌ Rejeter la pièce
      </button>

      <button
        className="btn btn-validate"
        onClick={handleValidate}
        disabled={!canAct}
      >
        ✅ Valider la pièce
      </button>

      {actionLoading && <span style={{ marginLeft: 12 }}>⏳ Action en cours...</span>}
    </div>
  );
};

export default Footer;

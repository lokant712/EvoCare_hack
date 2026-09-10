import React, { useState } from 'react';
import { LongitudinalMemoryPayload, MemoryHistoryItem } from '../../types';
import { Brain, History, ShieldAlert, Sparkles, CheckCircle2 } from 'lucide-react';
import { SourceBadge } from '../common/SourceBadge';
import { apiService } from '../../services/api';

interface LongitudinalMemoryPanelProps {
  memory: LongitudinalMemoryPayload;
  patientId?: string;
  onSelectEvidence?: (evidenceCode: string) => void;
}

export const LongitudinalMemoryPanel: React.FC<LongitudinalMemoryPanelProps> = ({
  memory,
  patientId = 'P001',
}) => {
  const [showHistory, setShowHistory] = useState(false);
  const [historyList, setHistoryList] = useState<MemoryHistoryItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const handleOpenHistory = async () => {
    setShowHistory(true);
    setLoadingHistory(true);
    try {
      const hist = await apiService.getMemoryHistory(patientId, 'Mobility');
      setHistoryList(hist);
    } catch {
      // Fallback display
      setHistoryList([
        {
          id: 1,
          version_number: memory.current_version,
          update_type: 'TEMPORAL_UPDATE',
          change_summary: memory.recent_changes,
          created_at: memory.last_updated,
          created_by: 'CAREGIVER_CONSOLIDATION',
          validation_status: 'APPLIED',
        },
      ]);
    } finally {
      setLoadingHistory(false);
    }
  };

  return (
    <div
      style={{
        backgroundColor: 'var(--color-surface)',
        borderRadius: '12px',
        border: '1px solid var(--color-border)',
        padding: '20px',
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.02)',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--color-text-main)', margin: 0 }}>
              Longitudinal Evolving Patient Memory
            </h2>
            <SourceBadge type="AI-DERIVED" size="sm" />
          </div>
          <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', margin: '2px 0 0 0' }}>
            Continuously updated clinical synthesis synchronized with Patient Wiki
          </p>
        </div>

        {/* Memory Version Pill & History Trigger */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span
            style={{
              fontSize: '11px',
              fontFamily: "'IBM Plex Mono', monospace",
              fontWeight: 700,
              backgroundColor: 'var(--color-plum-soft)',
              color: 'var(--color-plum-dark)',
              padding: '4px 10px',
              borderRadius: '6px',
              border: '1px solid var(--color-plum-border)',
            }}
          >
            MEMORY VERSION {memory.current_version}
          </span>
          <button
            onClick={handleOpenHistory}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              fontSize: '12px',
              fontWeight: 600,
              padding: '4px 10px',
              borderRadius: '6px',
              backgroundColor: 'var(--color-bg)',
              color: 'var(--color-text-secondary)',
              border: '1px solid var(--color-border-strong)',
              cursor: 'pointer',
            }}
          >
            <History size={13} />
            View Version History
          </button>
        </div>
      </div>

      {/* Memory Sections Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '14px' }}>
        {/* Baseline Status */}
        <div style={{ padding: '14px', backgroundColor: 'var(--color-bg)', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
            <CheckCircle2 size={14} style={{ color: 'var(--color-accent)' }} />
            <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-accent-dark)', textTransform: 'uppercase' }}>
              Historical Baseline
            </span>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.4 }}>{memory.baseline}</p>
        </div>

        {/* Recent Synthesized Trajectory */}
        <div style={{ padding: '14px', backgroundColor: 'var(--color-plum-soft)', borderRadius: '8px', border: '1px solid var(--color-plum-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
            <Sparkles size={14} style={{ color: 'var(--color-plum)' }} />
            <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-plum-dark)', textTransform: 'uppercase' }}>
              Recent Longitudinal Trajectory
            </span>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--color-plum-dark)', margin: 0, lineHeight: 1.4 }}>{memory.recent_changes}</p>
        </div>

        {/* Clinician-Confirmed Context */}
        <div style={{ padding: '14px', backgroundColor: 'var(--color-accent-soft)', borderRadius: '8px', border: '1px solid var(--color-accent-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-accent-dark)', textTransform: 'uppercase' }}>
              Clinician-Confirmed Notes
            </span>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--color-accent-dark)', margin: 0, lineHeight: 1.4 }}>{memory.clinician_confirmed}</p>
        </div>

        {/* Known Unknowns & Etiology Protection */}
        <div style={{ padding: '14px', backgroundColor: 'var(--color-warning-soft)', borderRadius: '8px', border: '1px solid var(--color-warning-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
            <ShieldAlert size={14} style={{ color: 'var(--color-warning)' }} />
            <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-warning-dark)', textTransform: 'uppercase' }}>
              Known Unknowns & Safety Gating
            </span>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--color-warning-dark)', margin: 0, lineHeight: 1.4 }}>{memory.unknowns}</p>
        </div>
      </div>

      {/* History Modal */}
      {showHistory && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(28, 26, 20, 0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: '20px',
          }}
          onClick={() => setShowHistory(false)}
        >
          <div
            style={{
              backgroundColor: 'var(--color-surface)',
              borderRadius: '12px',
              maxWidth: '650px',
              width: '100%',
              maxHeight: '80vh',
              overflowY: 'auto',
              padding: '24px',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Brain size={20} style={{ color: 'var(--color-accent)' }} />
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--color-text-main)', margin: 0 }}>
                  Memory Version Audit History
                </h3>
              </div>
              <button
                onClick={() => setShowHistory(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '18px',
                  fontWeight: 700,
                  color: 'var(--color-text-muted)',
                  cursor: 'pointer',
                }}
              >
                ✕
              </button>
            </div>

            {loadingHistory ? (
              <div style={{ padding: '20px', textAlign: 'center', color: 'var(--color-text-muted)' }}>Loading version history...</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {historyList.map((h, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '12px 14px',
                      backgroundColor: 'var(--color-bg)',
                      borderRadius: '8px',
                      border: '1px solid var(--color-border)',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--color-text-main)' }}>
                        Version {h.version_number}
                      </span>
                      <span
                        style={{
                          fontSize: '11px',
                          fontFamily: "'IBM Plex Mono', monospace",
                          padding: '2px 6px',
                          borderRadius: '4px',
                          backgroundColor: 'var(--color-success-soft)',
                          color: 'var(--color-success-dark)',
                          fontWeight: 600,
                        }}
                      >
                        {h.validation_status}
                      </span>
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>{h.change_summary}</div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-faint)' }}>Created: {h.created_at}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

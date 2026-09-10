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
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        border: '1px solid #e2e8f0',
        padding: '20px',
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.02)',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a', margin: 0 }}>
              Longitudinal Evolving Patient Memory
            </h2>
            <SourceBadge type="AI-DERIVED" size="sm" />
          </div>
          <p style={{ fontSize: '12px', color: '#64748b', margin: '2px 0 0 0' }}>
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
              backgroundColor: '#e0e7ff',
              color: '#3730a3',
              padding: '4px 10px',
              borderRadius: '6px',
              border: '1px solid #c7d2fe',
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
              backgroundColor: '#f8fafc',
              color: '#475569',
              border: '1px solid #cbd5e1',
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
        <div style={{ padding: '14px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
            <CheckCircle2 size={14} style={{ color: '#0284c7' }} />
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#0369a1', textTransform: 'uppercase' }}>
              Historical Baseline
            </span>
          </div>
          <p style={{ fontSize: '13px', color: '#334155', margin: 0, lineHeight: 1.4 }}>{memory.baseline}</p>
        </div>

        {/* Recent Synthesized Trajectory */}
        <div style={{ padding: '14px', backgroundColor: '#f5f3ff', borderRadius: '8px', border: '1px solid #ddd6fe' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
            <Sparkles size={14} style={{ color: '#7c3aed' }} />
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#6d28d9', textTransform: 'uppercase' }}>
              Recent Longitudinal Trajectory
            </span>
          </div>
          <p style={{ fontSize: '13px', color: '#4c1d95', margin: 0, lineHeight: 1.4 }}>{memory.recent_changes}</p>
        </div>

        {/* Clinician-Confirmed Context */}
        <div style={{ padding: '14px', backgroundColor: '#f0f9ff', borderRadius: '8px', border: '1px solid #bae6fd' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#0369a1', textTransform: 'uppercase' }}>
              Clinician-Confirmed Notes
            </span>
          </div>
          <p style={{ fontSize: '13px', color: '#0c4a6e', margin: 0, lineHeight: 1.4 }}>{memory.clinician_confirmed}</p>
        </div>

        {/* Known Unknowns & Etiology Protection */}
        <div style={{ padding: '14px', backgroundColor: '#fefce8', borderRadius: '8px', border: '1px solid #fef08a' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
            <ShieldAlert size={14} style={{ color: '#ca8a04' }} />
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#854d0e', textTransform: 'uppercase' }}>
              Known Unknowns & Safety Gating
            </span>
          </div>
          <p style={{ fontSize: '13px', color: '#713f12', margin: 0, lineHeight: 1.4 }}>{memory.unknowns}</p>
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
            backgroundColor: 'rgba(15, 23, 42, 0.6)',
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
              backgroundColor: '#ffffff',
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
                <Brain size={20} style={{ color: '#0284c7' }} />
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a', margin: 0 }}>
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
                  color: '#64748b',
                  cursor: 'pointer',
                }}
              >
                ✕
              </button>
            </div>

            {loadingHistory ? (
              <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>Loading version history...</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {historyList.map((h, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '12px 14px',
                      backgroundColor: '#f8fafc',
                      borderRadius: '8px',
                      border: '1px solid #e2e8f0',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 700, fontSize: '13px', color: '#0f172a' }}>
                        Version {h.version_number}
                      </span>
                      <span
                        style={{
                          fontSize: '11px',
                          fontFamily: "'IBM Plex Mono', monospace",
                          padding: '2px 6px',
                          borderRadius: '4px',
                          backgroundColor: '#ecfdf5',
                          color: '#047857',
                          fontWeight: 600,
                        }}
                      >
                        {h.validation_status}
                      </span>
                    </div>
                    <div style={{ fontSize: '12px', color: '#334155', marginBottom: '4px' }}>{h.change_summary}</div>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Created: {h.created_at}</div>
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

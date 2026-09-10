import React from 'react';
import { CaregiverObservationItem } from '../../types';
import { SourceBadge } from '../common/SourceBadge';
import { Users, FileText, Calendar } from 'lucide-react';

interface CaregiverObservationsPanelProps {
  observations: CaregiverObservationItem[];
  onSelectEvidence: (evidenceCode: string) => void;
}

export const CaregiverObservationsPanel: React.FC<CaregiverObservationsPanelProps> = ({
  observations,
  onSelectEvidence,
}) => {
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
              Caregiver Observation Feed
            </h2>
            <SourceBadge type="CAREGIVER-REPORTED" size="sm" />
          </div>
          <p style={{ fontSize: '12px', color: '#64748b', margin: '2px 0 0 0' }}>
            Natural language observations reported by family caregivers (CG001, CG002, CG003)
          </p>
        </div>
      </div>

      {/* Observation Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '420px', overflowY: 'auto', paddingRight: '4px' }}>
        {observations.map((obs) => (
          <div
            key={obs.id}
            style={{
              padding: '12px 14px',
              backgroundColor: '#fffdfa',
              borderRadius: '8px',
              border: '1px solid #fef3c7',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '11px',
                    fontWeight: 700,
                    color: '#92400e',
                    backgroundColor: '#fef3c7',
                    padding: '2px 6px',
                    borderRadius: '4px',
                  }}
                >
                  <Users size={12} />
                  {obs.caregiver_id}
                </span>
                <span
                  style={{
                    fontSize: '11px',
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontWeight: 600,
                    color: '#475569',
                    backgroundColor: '#f1f5f9',
                    padding: '2px 6px',
                    borderRadius: '4px',
                  }}
                >
                  {obs.category.toUpperCase()}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '11px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '3px' }}>
                  <Calendar size={11} />
                  {obs.observed_at}
                </span>
                <button
                  onClick={() => onSelectEvidence(obs.evidence_code)}
                  style={{
                    fontSize: '11px',
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontWeight: 600,
                    padding: '2px 6px',
                    backgroundColor: '#e0f2fe',
                    color: '#0369a1',
                    border: '1px solid #bae6fd',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '3px',
                  }}
                >
                  <FileText size={10} />
                  {obs.evidence_code}
                </button>
              </div>
            </div>

            {/* Verbatim Caregiver Observation Statement */}
            <p style={{ fontSize: '13px', color: '#1f2937', margin: '2px 0 0 0', lineHeight: 1.4, fontStyle: 'italic' }}>
              "{obs.observation_text}"
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

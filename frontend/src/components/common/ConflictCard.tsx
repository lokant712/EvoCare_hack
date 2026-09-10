import React from 'react';
import { AlertTriangle, Stethoscope, Users } from 'lucide-react';
import { ConflictItem } from '../../types';

interface ConflictCardProps {
  conflict: ConflictItem;
  onSelectEvidence?: (evidenceCode: string) => void;
}

export const ConflictCard: React.FC<ConflictCardProps> = ({ conflict, onSelectEvidence }) => {
  return (
    <div
      style={{
        backgroundColor: 'var(--color-surface)',
        borderRadius: '10px',
        border: '1px solid var(--color-warning-border)',
        padding: '16px',
        marginBottom: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={18} style={{ color: 'var(--color-warning)' }} />
          <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--color-warning-dark)' }}>{conflict.title}</span>
          <span
            style={{
              fontSize: '11px',
              fontFamily: "'IBM Plex Mono', monospace",
              padding: '2px 6px',
              borderRadius: '4px',
              backgroundColor: 'var(--color-warning-soft)',
              color: 'var(--color-warning-dark)',
              fontWeight: 600,
            }}
          >
            {conflict.category.toUpperCase()}
          </span>
        </div>
        <span
          style={{
            fontSize: '11px',
            fontWeight: 600,
            padding: '2px 8px',
            borderRadius: '9999px',
            backgroundColor: 'var(--color-danger-soft)',
            color: 'var(--color-danger-dark)',
          }}
        >
          {conflict.status}
        </span>
      </div>

      <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginBottom: '12px', lineHeight: 1.4 }}>
        {conflict.description}
      </p>

      {/* Dual Perspective Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
        {/* Clinician Perspective */}
        <div
          style={{
            backgroundColor: 'var(--color-accent-soft)',
            padding: '10px 12px',
            borderRadius: '8px',
            border: '1px solid var(--color-accent-border)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
            <Stethoscope size={14} style={{ color: 'var(--color-accent)' }} />
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-accent-dark)' }}>CLINICIAN VIEW</span>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--color-accent-dark)', margin: 0 }}>{conflict.doctor_view}</p>
        </div>

        {/* Caregiver Perspective */}
        <div
          style={{
            backgroundColor: 'var(--color-warning-soft)',
            padding: '10px 12px',
            borderRadius: '8px',
            border: '1px solid var(--color-warning-border)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
            <Users size={14} style={{ color: 'var(--color-warning)' }} />
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-warning-dark)' }}>CAREGIVER VIEW</span>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--color-warning-dark)', margin: 0 }}>{conflict.caregiver_view}</p>
        </div>
      </div>

      {/* Contextual Explanation */}
      <div
        style={{
          fontSize: '12px',
          color: 'var(--color-text-muted)',
          backgroundColor: 'var(--color-bg)',
          padding: '8px 10px',
          borderRadius: '6px',
          borderLeft: '3px solid var(--color-border-strong)',
          marginBottom: '10px',
        }}
      >
        <span style={{ fontWeight: 600, color: 'var(--color-text-secondary)' }}>Context: </span>
        {conflict.context}
      </div>

      {/* Supporting Evidence Chips */}
      {conflict.evidence_ids && conflict.evidence_ids.length > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '11px', color: 'var(--color-text-faint)', fontWeight: 500 }}>Evidence:</span>
          {conflict.evidence_ids.map((ev) => (
            <button
              key={ev}
              onClick={() => onSelectEvidence?.(ev)}
              style={{
                fontSize: '11px',
                fontFamily: "'IBM Plex Mono', monospace",
                padding: '2px 8px',
                borderRadius: '4px',
                backgroundColor: 'var(--color-surface-alt)',
                border: '1px solid var(--color-border-strong)',
                color: 'var(--color-accent)',
                cursor: 'pointer',
                fontWeight: 600,
              }}
            >
              {ev}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

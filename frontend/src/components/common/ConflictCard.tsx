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
        backgroundColor: '#fff',
        borderRadius: '10px',
        border: '1px solid #fed7aa',
        padding: '16px',
        marginBottom: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={18} style={{ color: '#ea580c' }} />
          <span style={{ fontWeight: 700, fontSize: '14px', color: '#9a3412' }}>{conflict.title}</span>
          <span
            style={{
              fontSize: '11px',
              fontFamily: "'IBM Plex Mono', monospace",
              padding: '2px 6px',
              borderRadius: '4px',
              backgroundColor: '#ffedd5',
              color: '#c2410c',
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
            backgroundColor: '#fee2e2',
            color: '#991b1b',
          }}
        >
          {conflict.status}
        </span>
      </div>

      <p style={{ fontSize: '13px', color: '#4b5563', marginBottom: '12px', lineHeight: 1.4 }}>
        {conflict.description}
      </p>

      {/* Dual Perspective Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
        {/* Clinician Perspective */}
        <div
          style={{
            backgroundColor: '#f0f9ff',
            padding: '10px 12px',
            borderRadius: '8px',
            border: '1px solid #bae6fd',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
            <Stethoscope size={14} style={{ color: '#0284c7' }} />
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#0369a1' }}>CLINICIAN VIEW</span>
          </div>
          <p style={{ fontSize: '12px', color: '#0c4a6e', margin: 0 }}>{conflict.doctor_view}</p>
        </div>

        {/* Caregiver Perspective */}
        <div
          style={{
            backgroundColor: '#fefce8',
            padding: '10px 12px',
            borderRadius: '8px',
            border: '1px solid #fef08a',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
            <Users size={14} style={{ color: '#ca8a04' }} />
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#854d0e' }}>CAREGIVER VIEW</span>
          </div>
          <p style={{ fontSize: '12px', color: '#713f12', margin: 0 }}>{conflict.caregiver_view}</p>
        </div>
      </div>

      {/* Contextual Explanation */}
      <div
        style={{
          fontSize: '12px',
          color: '#6b7280',
          backgroundColor: '#f9fafb',
          padding: '8px 10px',
          borderRadius: '6px',
          borderLeft: '3px solid #cbd5e1',
          marginBottom: '10px',
        }}
      >
        <span style={{ fontWeight: 600, color: '#374151' }}>Context: </span>
        {conflict.context}
      </div>

      {/* Supporting Evidence Chips */}
      {conflict.evidence_ids && conflict.evidence_ids.length > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '11px', color: '#9ca3af', fontWeight: 500 }}>Evidence:</span>
          {conflict.evidence_ids.map((ev) => (
            <button
              key={ev}
              onClick={() => onSelectEvidence?.(ev)}
              style={{
                fontSize: '11px',
                fontFamily: "'IBM Plex Mono', monospace",
                padding: '2px 8px',
                borderRadius: '4px',
                backgroundColor: '#f1f5f9',
                border: '1px solid #cbd5e1',
                color: '#0284c7',
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

import React from 'react';
import { EvidenceDetailItem } from '../../types';
import { FileText, Calendar, User, ShieldCheck, Link2 } from 'lucide-react';
import { SourceBadge } from '../common/SourceBadge';

interface EvidenceDrawerProps {
  evidence: EvidenceDetailItem | null;
  onClose: () => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ evidence, onClose }) => {
  if (!evidence) return null;

  return (
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
        zIndex: 110,
        padding: '20px',
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#ffffff',
          borderRadius: '14px',
          maxWidth: '600px',
          width: '100%',
          maxHeight: '80vh',
          overflowY: 'auto',
          padding: '24px',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.25)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={20} style={{ color: '#0284c7' }} />
            <div>
              <span
                style={{
                  fontSize: '14px',
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontWeight: 700,
                  color: '#0f172a',
                }}
              >
                {evidence.evidence_code}
              </span>
              <div style={{ fontSize: '11px', color: '#64748b' }}>Immutable Raw Evidence Record</div>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '20px',
              fontWeight: 700,
              color: '#94a3b8',
              cursor: 'pointer',
            }}
          >
            ✕
          </button>
        </div>

        {/* Source & Status Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <SourceBadge type={evidence.source_type} size="sm" />
          <span
            style={{
              fontSize: '11px',
              fontFamily: "'IBM Plex Mono', monospace",
              fontWeight: 600,
              padding: '2px 8px',
              backgroundColor: '#f1f5f9',
              color: '#475569',
              borderRadius: '9999px',
            }}
          >
            {evidence.category.toUpperCase()}
          </span>
          <span
            style={{
              fontSize: '11px',
              fontWeight: 600,
              padding: '2px 8px',
              backgroundColor: '#ecfdf5',
              color: '#047857',
              borderRadius: '9999px',
            }}
          >
            {evidence.status}
          </span>
        </div>

        {/* Verbatim Original Statement */}
        <div
          style={{
            backgroundColor: '#f8fafc',
            borderRadius: '8px',
            border: '1px solid #e2e8f0',
            padding: '14px',
            marginBottom: '16px',
          }}
        >
          <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '6px' }}>
            Exact Original Statement (Verbatim)
          </div>
          <p style={{ fontSize: '14px', color: '#0f172a', margin: 0, lineHeight: 1.5, fontStyle: 'italic' }}>
            "{evidence.original_statement}"
          </p>
        </div>

        {/* Metadata Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '10px',
            fontSize: '12px',
            marginBottom: '16px',
          }}
        >
          <div style={{ padding: '8px 10px', backgroundColor: '#f1f5f9', borderRadius: '6px' }}>
            <div style={{ color: '#64748b', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
              <Calendar size={12} /> Observed At
            </div>
            <div style={{ fontWeight: 600, color: '#0f172a', fontFamily: "'IBM Plex Mono', monospace" }}>
              {evidence.observed_at}
            </div>
          </div>
          <div style={{ padding: '8px 10px', backgroundColor: '#f1f5f9', borderRadius: '6px' }}>
            <div style={{ color: '#64748b', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
              <User size={12} /> Recorded By / Observer
            </div>
            <div style={{ fontWeight: 600, color: '#0f172a' }}>{evidence.observer || evidence.source_type}</div>
          </div>
        </div>

        {/* Linked Memory Claims */}
        {evidence.linked_claims && evidence.linked_claims.length > 0 && (
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 700, color: '#334155', marginBottom: '6px' }}>
              <Link2 size={13} /> Linked Active Memory Claims
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {evidence.linked_claims.map((claim, idx) => (
                <div
                  key={idx}
                  style={{
                    fontSize: '12px',
                    color: '#1e293b',
                    backgroundColor: '#eef2ff',
                    padding: '8px 10px',
                    borderRadius: '6px',
                    borderLeft: '3px solid #6366f1',
                  }}
                >
                  {claim}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Immutability confirmation */}
        <div
          style={{
            padding: '8px 12px',
            backgroundColor: '#ecfdf5',
            borderRadius: '6px',
            border: '1px solid #a7f3d0',
            fontSize: '11px',
            color: '#065f46',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}
        >
          <ShieldCheck size={14} />
          <span>Evidence records in EvoCare are immutable and cryptographically indexed.</span>
        </div>
      </div>
    </div>
  );
};

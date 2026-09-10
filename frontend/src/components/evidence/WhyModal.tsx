import React from 'react';
import { RecentChangeItem, EvidenceDetailItem } from '../../types';
import { HelpCircle, ArrowDown, FileText, CheckCircle2 } from 'lucide-react';
import { SourceBadge } from '../common/SourceBadge';

interface WhyModalProps {
  change: RecentChangeItem | null;
  provenanceMap: Record<string, EvidenceDetailItem>;
  onClose: () => void;
  onSelectEvidence: (evidenceCode: string) => void;
}

export const WhyModal: React.FC<WhyModalProps> = ({
  change,
  provenanceMap,
  onClose,
  onSelectEvidence,
}) => {
  if (!change) return null;

  return (
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
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: 'var(--color-surface)',
          borderRadius: '14px',
          maxWidth: '720px',
          width: '100%',
          maxHeight: '85vh',
          overflowY: 'auto',
          padding: '28px',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.25)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '8px',
                backgroundColor: 'var(--color-accent-soft)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--color-accent)',
              }}
            >
              <HelpCircle size={22} />
            </div>
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--color-text-main)', margin: 0 }}>
                Why This Information Appears
              </h2>
              <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', margin: '2px 0 0 0' }}>
                Complete clinical provenance & derivation trace from original observations
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '20px',
              fontWeight: 700,
              color: 'var(--color-text-faint)',
              cursor: 'pointer',
            }}
          >
            ✕
          </button>
        </div>

        {/* Step 1: Synthesized Memory Claim */}
        <div
          style={{
            backgroundColor: 'var(--color-bg)',
            borderRadius: '10px',
            border: '1px solid var(--color-border)',
            padding: '16px',
            marginBottom: '14px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
              1. Synthesized Memory Claim ({change.category})
            </span>
            <SourceBadge type="AI-DERIVED" size="sm" />
          </div>
          <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--color-text-main)', lineHeight: 1.4 }}>
            "{change.change_summary}"
          </div>
          {change.memory_version && (
            <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--color-text-muted)', fontFamily: "'IBM Plex Mono', monospace" }}>
              Memory Version: {change.memory_version} • Confidence: {change.confidence}
            </div>
          )}
        </div>

        {/* Flow indicator */}
        <div style={{ display: 'flex', justifyContent: 'center', margin: '8px 0', color: 'var(--color-text-faint)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 600 }}>
            <ArrowDown size={16} /> Derived deterministically from supporting raw evidence:
          </div>
        </div>

        {/* Step 2: Supporting Evidence List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '10px' }}>
          {change.evidence_ids.map((evCode) => {
            const evDetail = provenanceMap[evCode];
            return (
              <div
                key={evCode}
                style={{
                  backgroundColor: 'var(--color-surface)',
                  borderRadius: '10px',
                  border: '1px solid var(--color-border-strong)',
                  padding: '14px 16px',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span
                      style={{
                        fontSize: '12px',
                        fontFamily: "'IBM Plex Mono', monospace",
                        fontWeight: 700,
                        backgroundColor: 'var(--color-accent)',
                        color: '#ffffff',
                        padding: '2px 8px',
                        borderRadius: '4px',
                      }}
                    >
                      {evCode}
                    </span>
                    <SourceBadge type={evDetail ? evDetail.source_type : 'CAREGIVER'} size="sm" />
                  </div>
                  <span style={{ fontSize: '12px', color: 'var(--color-text-muted)', fontFamily: "'IBM Plex Mono', monospace" }}>
                    {evDetail?.observed_at || change.observed_date}
                  </span>
                </div>

                {/* Original raw statement */}
                <div style={{ fontSize: '13px', color: 'var(--color-text-main)', lineHeight: 1.4, margin: '6px 0', fontStyle: 'italic' }}>
                  "{evDetail?.original_statement || 'Original observation recorded in longitudinal database.'}"
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '8px', paddingTop: '6px', borderTop: '1px dashed var(--color-border)' }}>
                  <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                    Status: <strong>{evDetail?.status || 'IMMUTABLE'}</strong> • Observer: <strong>{evDetail?.observer || 'Caregiver'}</strong>
                  </span>
                  <button
                    onClick={() => onSelectEvidence(evCode)}
                    style={{
                      fontSize: '11px',
                      fontWeight: 600,
                      color: 'var(--color-accent)',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    <FileText size={12} /> Inspect Raw Evidence
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer Disclaimer */}
        <div
          style={{
            marginTop: '20px',
            padding: '10px 14px',
            backgroundColor: 'var(--color-bg)',
            borderRadius: '8px',
            border: '1px solid var(--color-border)',
            fontSize: '11px',
            color: 'var(--color-text-muted)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <CheckCircle2 size={16} style={{ color: 'var(--color-accent)', flexShrink: 0 }} />
          <span>
            <strong>Traceability Assurance:</strong> This memory item is deterministically linked to immutable evidence records above. No diagnosis has been synthesized.
          </span>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { RecentChangeItem } from '../../types';
import { SourceBadge } from '../common/SourceBadge';
import { TrendingUp, TrendingDown, RefreshCw, HelpCircle, FileText } from 'lucide-react';

interface RecentChangesPanelProps {
  recentChanges: RecentChangeItem[];
  onOpenWhy: (change: RecentChangeItem) => void;
  onSelectEvidence: (evidenceCode: string) => void;
}

export const RecentChangesPanel: React.FC<RecentChangesPanelProps> = ({
  recentChanges,
  onOpenWhy,
  onSelectEvidence,
}) => {
  const getDirectionBadge = (direction: string) => {
    switch (direction) {
      case 'IMPROVEMENT':
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '11px',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: '9999px',
              backgroundColor: '#ecfdf5',
              color: '#047857',
              border: '1px solid #a7f3d0',
            }}
          >
            <TrendingUp size={12} /> IMPROVEMENT
          </span>
        );
      case 'DECLINE':
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '11px',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: '9999px',
              backgroundColor: '#fef2f2',
              color: '#b91c1c',
              border: '1px solid #fca5a5',
            }}
          >
            <TrendingDown size={12} /> DECLINE / ALERT
          </span>
        );
      case 'FLUCTUATION':
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '11px',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: '9999px',
              backgroundColor: '#fffbeb',
              color: '#b45309',
              border: '1px solid #fde68a',
            }}
          >
            <RefreshCw size={12} /> FLUCTUATION
          </span>
        );
      default:
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '11px',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: '9999px',
              backgroundColor: '#f1f5f9',
              color: '#475569',
              border: '1px solid #cbd5e1',
            }}
          >
            NEW OBSERVATION
          </span>
        );
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
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a', margin: 0 }}>
              Recent Patient Health Trajectory & Changes
            </h2>
            <span
              style={{
                fontSize: '11px',
                fontWeight: 600,
                backgroundColor: '#e0f2fe',
                color: '#0369a1',
                padding: '2px 8px',
                borderRadius: '9999px',
              }}
            >
              PRIORITY DOCTOR VIEW
            </span>
          </div>
          <p style={{ fontSize: '13px', color: '#64748b', margin: '4px 0 0 0' }}>
            What has changed in this patient recently? (Derived from verified caregiver & clinical evidence)
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {recentChanges.map((change, idx) => (
          <div
            key={idx}
            style={{
              padding: '16px 18px',
              backgroundColor: '#f8fafc',
              borderRadius: '10px',
              border: '1px solid #e2e8f0',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
            }}
          >
            {/* Header: Title, Badges, Direction */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a' }}>{change.title}</span>
                <span
                  style={{
                    fontSize: '11px',
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontWeight: 600,
                    padding: '2px 6px',
                    backgroundColor: '#e2e8f0',
                    color: '#334155',
                    borderRadius: '4px',
                  }}
                >
                  {change.category.toUpperCase()}
                </span>
                {getDirectionBadge(change.direction)}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <SourceBadge type={change.source_type} size="sm" />
                <span style={{ fontSize: '12px', color: '#64748b', fontFamily: "'IBM Plex Mono', monospace" }}>
                  {change.observed_date}
                </span>
              </div>
            </div>

            {/* Trajectory progression: Previous -> Latest */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '12px',
                backgroundColor: '#ffffff',
                padding: '12px 14px',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
              }}
            >
              <div>
                <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '2px' }}>
                  Previous State
                </div>
                <div style={{ fontSize: '13px', color: '#475569' }}>{change.previous_state}</div>
              </div>
              <div style={{ borderLeft: '1px solid #e2e8f0', paddingLeft: '12px' }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: '#0284c7', textTransform: 'uppercase', marginBottom: '2px' }}>
                  Latest Observation
                </div>
                <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>{change.latest_state}</div>
              </div>
            </div>

            {/* Synthesized longitudinal claim */}
            <div style={{ fontSize: '13px', color: '#334155', lineHeight: 1.4 }}>
              <strong>Synthesized Claim:</strong> {change.change_summary}
            </div>

            {/* Action Bar: Evidence Count, Provenance [Why?] button */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '4px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '12px', color: '#64748b' }}>
                  Evidence ({change.evidence_count} records):
                </span>
                {change.evidence_ids.map((ev) => (
                  <button
                    key={ev}
                    onClick={() => onSelectEvidence(ev)}
                    style={{
                      fontSize: '11px',
                      fontFamily: "'IBM Plex Mono', monospace",
                      fontWeight: 600,
                      padding: '2px 6px',
                      borderRadius: '4px',
                      backgroundColor: '#e0f2fe',
                      color: '#0369a1',
                      border: '1px solid #bae6fd',
                      cursor: 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '3px',
                    }}
                  >
                    <FileText size={10} />
                    {ev}
                  </button>
                ))}
              </div>

              <button
                onClick={() => onOpenWhy(change)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '5px',
                  fontSize: '12px',
                  fontWeight: 700,
                  padding: '5px 12px',
                  borderRadius: '6px',
                  backgroundColor: '#0284c7',
                  color: '#ffffff',
                  border: 'none',
                  cursor: 'pointer',
                  boxShadow: '0 1px 2px rgba(2, 132, 199, 0.2)',
                  transition: 'background-color 0.15s',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#0369a1')}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#0284c7')}
              >
                <HelpCircle size={14} />
                Why? (Trace Provenance)
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

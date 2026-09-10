import React from 'react';
import { OverviewStatusItem } from '../../types';
import { SourceBadge } from '../common/SourceBadge';
import { Activity, Brain, Utensils, AlertCircle, ShieldAlert, Bone } from 'lucide-react';

interface PatientOverviewCardProps {
  overview: OverviewStatusItem[];
}

export const PatientOverviewCard: React.FC<PatientOverviewCardProps> = ({ overview }) => {
  const getCategoryIcon = (category: string) => {
    const cat = category.toLowerCase();
    if (cat.includes('mobility')) return <Activity size={18} style={{ color: 'var(--color-accent)' }} />;
    if (cat.includes('cognition')) return <Brain size={18} style={{ color: 'var(--color-plum)' }} />;
    if (cat.includes('nutrition')) return <Utensils size={18} style={{ color: 'var(--color-success)' }} />;
    if (cat.includes('dizziness')) return <AlertCircle size={18} style={{ color: 'var(--color-warning)' }} />;
    if (cat.includes('fall')) return <ShieldAlert size={18} style={{ color: 'var(--color-danger)' }} />;
    return <Bone size={18} style={{ color: 'var(--color-text-secondary)' }} />;
  };

  const getBorderColor = (tone: string) => {
    switch (tone) {
      case 'alert':
        return 'var(--color-danger-border)';
      case 'caution':
        return 'var(--color-warning-border)';
      case 'info':
        return 'var(--color-accent-border)';
      default:
        return 'var(--color-border)';
    }
  };

  const getCardBg = (tone: string) => {
    switch (tone) {
      case 'alert':
        return 'var(--color-danger-soft)';
      case 'caution':
        return 'var(--color-surface-raised)';
      case 'info':
        return 'var(--color-bg)';
      default:
        return 'var(--color-surface)';
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
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--color-text-main)', margin: 0 }}>
            Longitudinal Health Domain Overview
          </h2>
          <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', margin: '2px 0 0 0' }}>
            Baseline versus recent status across core functional domains (Non-diagnostic summaries)
          </p>
        </div>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '14px',
        }}
      >
        {overview.map((item, idx) => (
          <div
            key={idx}
            style={{
              padding: '14px 16px',
              backgroundColor: getCardBg(item.status_tone),
              borderRadius: '10px',
              border: `1px solid ${getBorderColor(item.status_tone)}`,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: '10px',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {getCategoryIcon(item.category)}
                  <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--color-text-main)' }}>{item.category}</span>
                </div>
                <SourceBadge type={item.source_type} size="sm" />
              </div>

              {/* Baseline */}
              <div style={{ marginBottom: '6px' }}>
                <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                  Baseline:{' '}
                </span>
                <span style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>{item.baseline}</span>
              </div>

              {/* Recent Status */}
              <div>
                <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                  Recent State:{' '}
                </span>
                <span
                  style={{
                    fontSize: '13px',
                    fontWeight: 600,
                    color: item.status_tone === 'alert' ? 'var(--color-danger-dark)' : item.status_tone === 'caution' ? 'var(--color-warning-dark)' : 'var(--color-text-main)',
                  }}
                >
                  {item.recent_status}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

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
    if (cat.includes('mobility')) return <Activity size={18} style={{ color: '#0284c7' }} />;
    if (cat.includes('cognition')) return <Brain size={18} style={{ color: '#9333ea' }} />;
    if (cat.includes('nutrition')) return <Utensils size={18} style={{ color: '#16a34a' }} />;
    if (cat.includes('dizziness')) return <AlertCircle size={18} style={{ color: '#ea580c' }} />;
    if (cat.includes('fall')) return <ShieldAlert size={18} style={{ color: '#dc2626' }} />;
    return <Bone size={18} style={{ color: '#4b5563' }} />;
  };

  const getBorderColor = (tone: string) => {
    switch (tone) {
      case 'alert':
        return '#fca5a5';
      case 'caution':
        return '#fde68a';
      case 'info':
        return '#bae6fd';
      default:
        return '#e2e8f0';
    }
  };

  const getCardBg = (tone: string) => {
    switch (tone) {
      case 'alert':
        return '#fff5f5';
      case 'caution':
        return '#fffdfa';
      case 'info':
        return '#f8fbff';
      default:
        return '#ffffff';
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
          <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a', margin: 0 }}>
            Longitudinal Health Domain Overview
          </h2>
          <p style={{ fontSize: '12px', color: '#64748b', margin: '2px 0 0 0' }}>
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
                  <span style={{ fontSize: '14px', fontWeight: 700, color: '#1e293b' }}>{item.category}</span>
                </div>
                <SourceBadge type={item.source_type} size="sm" />
              </div>

              {/* Baseline */}
              <div style={{ marginBottom: '6px' }}>
                <span style={{ fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
                  Baseline:{' '}
                </span>
                <span style={{ fontSize: '13px', color: '#334155' }}>{item.baseline}</span>
              </div>

              {/* Recent Status */}
              <div>
                <span style={{ fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
                  Recent State:{' '}
                </span>
                <span
                  style={{
                    fontSize: '13px',
                    fontWeight: 600,
                    color: item.status_tone === 'alert' ? '#b91c1c' : item.status_tone === 'caution' ? '#b45309' : '#0f172a',
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

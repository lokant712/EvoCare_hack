import React, { useState } from 'react';
import { TimelineEventItem } from '../../types';
import { SourceBadge } from '../common/SourceBadge';
import { Calendar, Filter, FileText } from 'lucide-react';

interface PatientTimelineProps {
  timeline: TimelineEventItem[];
  onSelectEvidence?: (evidenceCode: string) => void;
}

export const PatientTimeline: React.FC<PatientTimelineProps> = ({ timeline, onSelectEvidence }) => {
  const [selectedFilter, setSelectedFilter] = useState<string>('ALL');

  const categories = ['ALL', ...Array.from(new Set(timeline.map((e) => e.category)))];

  const filteredEvents = selectedFilter === 'ALL'
    ? timeline
    : timeline.filter((e) => e.category === selectedFilter);

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
      {/* Header & Filter */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px', marginBottom: '16px' }}>
        <div>
          <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a', margin: 0 }}>
            Longitudinal Patient Timeline
          </h2>
          <p style={{ fontSize: '12px', color: '#64748b', margin: '2px 0 0 0' }}>
            Unified chronological history of clinical consultations, laboratory results, and caregiver observations
          </p>
        </div>

        {/* Filter Pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <Filter size={13} style={{ color: '#64748b' }} />
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedFilter(cat)}
              style={{
                fontSize: '11px',
                fontWeight: 600,
                padding: '3px 8px',
                borderRadius: '6px',
                border: selectedFilter === cat ? '1px solid #0284c7' : '1px solid #e2e8f0',
                backgroundColor: selectedFilter === cat ? '#e0f2fe' : '#ffffff',
                color: selectedFilter === cat ? '#0369a1' : '#64748b',
                cursor: 'pointer',
              }}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Timeline Stream */}
      <div style={{ position: 'relative', paddingLeft: '24px' }}>
        {/* Left vertical timeline line */}
        <div
          style={{
            position: 'absolute',
            top: '8px',
            bottom: '8px',
            left: '8px',
            width: '2px',
            backgroundColor: '#e2e8f0',
          }}
        />

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {filteredEvents.map((evt) => (
            <div key={evt.id} style={{ position: 'relative' }}>
              {/* Timeline marker bullet */}
              <div
                style={{
                  position: 'absolute',
                  left: '-20px',
                  top: '12px',
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  backgroundColor: '#0284c7',
                  border: '2px solid #ffffff',
                  boxShadow: '0 0 0 2px #bae6fd',
                }}
              />

              {/* Event Card */}
              <div
                style={{
                  padding: '12px 14px',
                  backgroundColor: '#f8fafc',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '6px', marginBottom: '6px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '12px', fontFamily: "'IBM Plex Mono', monospace", fontWeight: 700, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Calendar size={12} />
                      {evt.date}
                    </span>
                    <span style={{ fontSize: '13px', fontWeight: 700, color: '#1e293b' }}>
                      {evt.title}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <SourceBadge type={evt.badge} size="sm" />
                    {evt.evidence_id && (
                      <button
                        onClick={() => onSelectEvidence?.(evt.evidence_id!)}
                        style={{
                          fontSize: '11px',
                          fontFamily: "'IBM Plex Mono', monospace",
                          color: '#0284c7',
                          backgroundColor: '#e0f2fe',
                          border: '1px solid #bae6fd',
                          borderRadius: '4px',
                          padding: '1px 6px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '2px',
                        }}
                      >
                        <FileText size={10} />
                        {evt.evidence_id}
                      </button>
                    )}
                  </div>
                </div>

                <div style={{ fontSize: '13px', color: '#475569', lineHeight: 1.4 }}>
                  {evt.description}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

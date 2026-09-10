import React from 'react';
import { SourceBadgeType } from '../../types';

interface SourceBadgeProps {
  type: SourceBadgeType | string;
  size?: 'sm' | 'md';
  showDisclaimer?: boolean;
}

export const SourceBadge: React.FC<SourceBadgeProps> = ({ type, size = 'sm', showDisclaimer = false }) => {
  const normalized = type.toUpperCase().replace(/\s+/g, '-');

  const getStyles = () => {
    switch (normalized) {
      case 'CLINICIAN-CONFIRMED':
      case 'DOCTOR':
        return {
          bg: '#e0f2fe',
          text: '#0369a1',
          border: '#bae6fd',
          label: 'CLINICIAN-CONFIRMED'
        };
      case 'CAREGIVER-REPORTED':
      case 'CAREGIVER':
        return {
          bg: '#fef3c7',
          text: '#92400e',
          border: '#fde68a',
          label: 'CAREGIVER-REPORTED'
        };
      case 'PATIENT-REPORTED':
      case 'PATIENT':
        return {
          bg: '#f3e8ff',
          text: '#7e22ce',
          border: '#e9d5ff',
          label: 'PATIENT-REPORTED'
        };
      case 'AI-DERIVED':
      case 'AI_DERIVED':
        return {
          bg: '#e0e7ff',
          text: '#3730a3',
          border: '#c7d2fe',
          label: 'AI-DERIVED'
        };
      case 'LAB':
        return {
          bg: '#ecfdf5',
          text: '#047857',
          border: '#a7f3d0',
          label: 'LAB RESULT'
        };
      case 'MEDICATION':
      case 'MEDICAL-RECORD':
        return {
          bg: '#f1f5f9',
          text: '#334155',
          border: '#cbd5e1',
          label: 'MEDICAL RECORD'
        };
      default:
        return {
          bg: '#f8fafc',
          text: '#475569',
          border: '#e2e8f0',
          label: type
        };
    }
  };

  const style = getStyles();
  const isSmall = size === 'sm';

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        fontSize: isSmall ? '11px' : '12px',
        fontWeight: 600,
        fontFamily: "'IBM Plex Mono', monospace",
        padding: isSmall ? '2px 8px' : '4px 10px',
        borderRadius: '9999px',
        backgroundColor: style.bg,
        color: style.text,
        border: `1px solid ${style.border}`,
        letterSpacing: '0.02em',
        whiteSpace: 'nowrap',
      }}
      title={style.label === 'AI-DERIVED' ? 'Derived from recorded evidence; not a clinical diagnosis.' : undefined}
    >
      <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: style.text }} />
      {style.label}
      {showDisclaimer && style.label === 'AI-DERIVED' && (
        <span style={{ fontSize: '10px', fontWeight: 400, opacity: 0.85, marginLeft: '4px' }}>
          (Derived from recorded evidence; not a clinical diagnosis)
        </span>
      )}
    </span>
  );
};

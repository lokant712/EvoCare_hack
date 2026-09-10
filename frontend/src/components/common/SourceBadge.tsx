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
          bg: 'var(--color-accent-soft)',
          text: 'var(--color-accent-dark)',
          border: 'var(--color-accent-border)',
          label: 'CLINICIAN-CONFIRMED'
        };
      case 'CAREGIVER-REPORTED':
      case 'CAREGIVER':
        return {
          bg: 'var(--color-warning-soft)',
          text: 'var(--color-warning-dark)',
          border: 'var(--color-warning-border)',
          label: 'CAREGIVER-REPORTED'
        };
      case 'PATIENT-REPORTED':
      case 'PATIENT':
        return {
          bg: 'var(--color-plum-soft)',
          text: 'var(--color-plum-dark)',
          border: 'var(--color-plum-border)',
          label: 'PATIENT-REPORTED'
        };
      case 'AI-DERIVED':
      case 'AI_DERIVED':
        return {
          bg: 'var(--color-plum-soft)',
          text: 'var(--color-plum-dark)',
          border: 'var(--color-plum-border)',
          label: 'AI-DERIVED'
        };
      case 'LAB':
        return {
          bg: 'var(--color-success-soft)',
          text: 'var(--color-success-dark)',
          border: 'var(--color-success-border)',
          label: 'LAB RESULT'
        };
      case 'MEDICATION':
      case 'MEDICAL-RECORD':
        return {
          bg: 'var(--color-surface-alt)',
          text: 'var(--color-text-secondary)',
          border: 'var(--color-border-strong)',
          label: 'MEDICAL RECORD'
        };
      default:
        return {
          bg: 'var(--color-bg)',
          text: 'var(--color-text-secondary)',
          border: 'var(--color-border)',
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

import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner: React.FC<{ message?: string }> = ({ message = 'Loading patient records...' }) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '380px',
        gap: '16px',
        color: 'var(--color-text-secondary)',
      }}
    >
      <Loader2 size={36} className="animate-spin" style={{ color: 'var(--color-accent)' }} />
      <div style={{ fontSize: '15px', fontWeight: 500 }}>{message}</div>
      <div style={{ fontSize: '12px', color: 'var(--color-text-faint)' }}>Retrieving longitudinal memory & evidence from backend...</div>
    </div>
  );
};

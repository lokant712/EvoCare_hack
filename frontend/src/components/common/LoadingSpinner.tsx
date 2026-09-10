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
        color: '#475569',
      }}
    >
      <Loader2 size={36} className="animate-spin" style={{ color: '#0284c7' }} />
      <div style={{ fontSize: '15px', fontWeight: 500 }}>{message}</div>
      <div style={{ fontSize: '12px', color: '#94a3b8' }}>Retrieving longitudinal memory & evidence from backend...</div>
    </div>
  );
};

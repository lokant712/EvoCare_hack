import React from 'react';
import { ShieldAlert, Info } from 'lucide-react';

export const SafetyAlert: React.FC = () => {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: 'var(--color-bg)',
        border: '1px solid var(--color-border)',
        borderRadius: '8px',
        padding: '10px 16px',
        marginBottom: '20px',
        fontSize: '12px',
        color: 'var(--color-text-secondary)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <ShieldAlert size={16} style={{ color: 'var(--color-accent)' }} />
        <span>
          <strong>Clinical Decision Support Guardrail:</strong> AI-derived claims synthesize recorded caregiver & medical observations. They do <em>not</em> constitute clinical diagnoses.
        </span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-text-muted)' }}>
        <Info size={14} />
        <span>Read-Only Clinical Station</span>
      </div>
    </div>
  );
};

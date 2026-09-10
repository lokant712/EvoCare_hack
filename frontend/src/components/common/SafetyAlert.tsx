import React from 'react';
import { ShieldAlert, Info } from 'lucide-react';

export const SafetyAlert: React.FC = () => {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: '#f8fafc',
        border: '1px solid #e2e8f0',
        borderRadius: '8px',
        padding: '10px 16px',
        marginBottom: '20px',
        fontSize: '12px',
        color: '#475569',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <ShieldAlert size={16} style={{ color: '#0284c7' }} />
        <span>
          <strong>Clinical Decision Support Guardrail:</strong> AI-derived claims synthesize recorded caregiver & medical observations. They do <em>not</em> constitute clinical diagnoses.
        </span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#64748b' }}>
        <Info size={14} />
        <span>Read-Only Clinical Station</span>
      </div>
    </div>
  );
};

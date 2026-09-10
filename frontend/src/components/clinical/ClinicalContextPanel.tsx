import React, { useState } from 'react';
import { DiagnosisItem, MedicationItem, LabResultItem } from '../../types';
import { Stethoscope, Pill, FlaskConical, Calendar, UserCheck } from 'lucide-react';
import { SourceBadge } from '../common/SourceBadge';

interface ClinicalContextPanelProps {
  diagnoses: DiagnosisItem[];
  medications: MedicationItem[];
  labs: LabResultItem[];
  onSelectEvidence?: (evidenceCode: string) => void;
}

export const ClinicalContextPanel: React.FC<ClinicalContextPanelProps> = ({
  diagnoses,
  medications,
  labs,
  onSelectEvidence,
}) => {
  const [activeTab, setActiveTab] = useState<'diagnoses' | 'medications' | 'labs'>('diagnoses');

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
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a', margin: 0 }}>
              Clinician-Confirmed Medical Context
            </h2>
            <SourceBadge type="CLINICIAN-CONFIRMED" size="sm" />
          </div>
          <p style={{ fontSize: '12px', color: '#64748b', margin: '2px 0 0 0' }}>
            Verified hospital & outpatient records (Separated from caregiver-reported observations)
          </p>
        </div>

        {/* Tab Buttons */}
        <div style={{ display: 'flex', gap: '4px', backgroundColor: '#f1f5f9', padding: '3px', borderRadius: '8px' }}>
          <button
            onClick={() => setActiveTab('diagnoses')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: 600,
              border: 'none',
              cursor: 'pointer',
              backgroundColor: activeTab === 'diagnoses' ? '#ffffff' : 'transparent',
              color: activeTab === 'diagnoses' ? '#0f172a' : '#64748b',
              boxShadow: activeTab === 'diagnoses' ? '0 1px 2px rgba(0,0,0,0.05)' : 'none',
            }}
          >
            <Stethoscope size={14} />
            Diagnoses ({diagnoses.length})
          </button>
          <button
            onClick={() => setActiveTab('medications')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: 600,
              border: 'none',
              cursor: 'pointer',
              backgroundColor: activeTab === 'medications' ? '#ffffff' : 'transparent',
              color: activeTab === 'medications' ? '#0f172a' : '#64748b',
              boxShadow: activeTab === 'medications' ? '0 1px 2px rgba(0,0,0,0.05)' : 'none',
            }}
          >
            <Pill size={14} />
            Medications ({medications.length})
          </button>
          <button
            onClick={() => setActiveTab('labs')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: 600,
              border: 'none',
              cursor: 'pointer',
              backgroundColor: activeTab === 'labs' ? '#ffffff' : 'transparent',
              color: activeTab === 'labs' ? '#0f172a' : '#64748b',
              boxShadow: activeTab === 'labs' ? '0 1px 2px rgba(0,0,0,0.05)' : 'none',
            }}
          >
            <FlaskConical size={14} />
            Laboratory ({labs.length})
          </button>
        </div>
      </div>

      {/* Tab Content: Diagnoses */}
      {activeTab === 'diagnoses' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
          {diagnoses.map((diag, idx) => (
            <div
              key={idx}
              style={{
                padding: '12px 14px',
                backgroundColor: '#f8fafc',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span
                  style={{
                    fontSize: '11px',
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontWeight: 700,
                    backgroundColor: '#e0f2fe',
                    color: '#0369a1',
                    padding: '2px 6px',
                    borderRadius: '4px',
                  }}
                >
                  ICD-10: {diag.code}
                </span>
                <span style={{ fontSize: '11px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Calendar size={11} /> {diag.confirmed_date}
                </span>
              </div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a', marginBottom: '4px' }}>
                {diag.description}
              </div>
              <div style={{ fontSize: '11px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <UserCheck size={11} /> {diag.doctor}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab Content: Medications */}
      {activeTab === 'medications' && (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e2e8f0', color: '#64748b', fontSize: '11px', textTransform: 'uppercase' }}>
                <th style={{ padding: '8px 12px' }}>Medication Name</th>
                <th style={{ padding: '8px 12px' }}>Dose</th>
                <th style={{ padding: '8px 12px' }}>Frequency</th>
                <th style={{ padding: '8px 12px' }}>Indication</th>
                <th style={{ padding: '8px 12px' }}>Status</th>
                <th style={{ padding: '8px 12px' }}>Evidence</th>
              </tr>
            </thead>
            <tbody>
              {medications.map((med, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #f1f5f9' }}>
                  <td style={{ padding: '10px 12px', fontWeight: 600, color: '#0f172a' }}>{med.name}</td>
                  <td style={{ padding: '10px 12px', color: '#334155' }}>{med.dose}</td>
                  <td style={{ padding: '10px 12px', color: '#334155' }}>{med.frequency}</td>
                  <td style={{ padding: '10px 12px', color: '#64748b' }}>{med.indication}</td>
                  <td style={{ padding: '10px 12px' }}>
                    <span
                      style={{
                        fontSize: '11px',
                        fontWeight: 600,
                        padding: '2px 6px',
                        borderRadius: '4px',
                        backgroundColor: med.status === 'ACTIVE' ? '#ecfdf5' : '#f1f5f9',
                        color: med.status === 'ACTIVE' ? '#047857' : '#475569',
                      }}
                    >
                      {med.status}
                    </span>
                  </td>
                  <td style={{ padding: '10px 12px' }}>
                    <button
                      onClick={() => onSelectEvidence?.(med.evidence_code)}
                      style={{
                        fontSize: '11px',
                        fontFamily: "'IBM Plex Mono', monospace",
                        color: '#0284c7',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        textDecoration: 'underline',
                      }}
                    >
                      {med.evidence_code}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab Content: Labs */}
      {activeTab === 'labs' && (
        <div>
          <div style={{ overflowX: 'auto', marginBottom: '8px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e2e8f0', color: '#64748b', fontSize: '11px', textTransform: 'uppercase' }}>
                  <th style={{ padding: '8px 12px' }}>Date</th>
                  <th style={{ padding: '8px 12px' }}>Test Parameter</th>
                  <th style={{ padding: '8px 12px' }}>Observed Value</th>
                  <th style={{ padding: '8px 12px' }}>Unit</th>
                  <th style={{ padding: '8px 12px' }}>Reference Range</th>
                  <th style={{ padding: '8px 12px' }}>Evidence</th>
                </tr>
              </thead>
              <tbody>
                {labs.map((lab, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '10px 12px', fontFamily: "'IBM Plex Mono', monospace", color: '#64748b' }}>
                      {lab.date}
                    </td>
                    <td style={{ padding: '10px 12px', fontWeight: 600, color: '#0f172a' }}>{lab.test_name}</td>
                    <td style={{ padding: '10px 12px', fontWeight: 700, color: '#0284c7' }}>{lab.value}</td>
                    <td style={{ padding: '10px 12px', color: '#64748b' }}>{lab.unit}</td>
                    <td style={{ padding: '10px 12px', color: '#64748b', fontSize: '12px' }}>{lab.reference_range}</td>
                    <td style={{ padding: '10px 12px' }}>
                      <button
                        onClick={() => onSelectEvidence?.(lab.evidence_code)}
                        style={{
                          fontSize: '11px',
                          fontFamily: "'IBM Plex Mono', monospace",
                          color: '#0284c7',
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          textDecoration: 'underline',
                        }}
                      >
                        {lab.evidence_code}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ fontSize: '11px', color: '#94a3b8', fontStyle: 'italic', paddingLeft: '4px' }}>
            * Note: Laboratory results are displayed chronologically without speculative AI reinterpretation.
          </div>
        </div>
      )}
    </div>
  );
};

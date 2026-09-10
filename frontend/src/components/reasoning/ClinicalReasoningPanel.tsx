import React, { useState } from 'react';
import {
  Brain,
  Sparkles,
  ShieldAlert,
  HelpCircle,
  AlertOctagon,
  Clock,
  Activity,
  CheckCircle2,
  Stethoscope,
  ChevronRight,
  Info
} from 'lucide-react';
import { ClinicalReasoningResponse } from '../../types';
import { apiService, ApiError } from '../../services/api';

interface ClinicalReasoningPanelProps {
  patientId: string;
  onSelectEvidence: (evidenceCode: string) => void;
}

const EXAMPLE_QUESTIONS = [
  "Based on her recent dizziness and mobility changes, what possible problems should I consider?",
  "Why is she dizzy?",
  "Does she have dementia?",
  "Has her mobility worsened over time?",
  "What information is missing to better understand the recent dizziness?"
];

export const ClinicalReasoningPanel: React.FC<ClinicalReasoningPanelProps> = ({
  patientId,
  onSelectEvidence
}) => {
  const [question, setQuestion] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [reasoningData, setReasoningData] = useState<ClinicalReasoningResponse | null>(null);

  const handleAnalyze = async (qText?: string) => {
    const targetQ = (qText || question).trim();
    if (!targetQ) return;
    if (qText) setQuestion(qText);

    setLoading(true);
    setError(null);

    try {
      const data = await apiService.getClinicalReasoning(patientId, targetQ);
      setReasoningData(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to process clinical reasoning request.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        borderRadius: '16px',
        border: '1px solid #cbd5e1',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
        padding: '24px',
        marginBottom: '28px'
      }}
      data-testid="clinical-reasoning-panel"
    >
      {/* 1. Doctor-Only Authentication Warning Banner */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: '#eff6ff',
          border: '1px solid #bfdbfe',
          borderRadius: '8px',
          padding: '10px 16px',
          marginBottom: '18px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Stethoscope size={18} style={{ color: '#2563eb' }} />
          <span style={{ fontSize: '12px', fontWeight: 800, color: '#1e40af', letterSpacing: '0.05em' }}>
            DOCTOR-ONLY CLINICAL REASONING
          </span>
          <span
            style={{
              fontSize: '11px',
              backgroundColor: '#dbeafe',
              color: '#1d4ed8',
              padding: '2px 8px',
              borderRadius: '4px',
              fontWeight: 600
            }}
          >
            DEMO MODE — AUTHENTICATION NOT YET ENABLED (PHASE 8)
          </span>
        </div>
        <div style={{ fontSize: '11px', color: '#64748b' }}>
          Strictly Read-Only Analytical Decision Support
        </div>
      </div>

      {/* Header */}
      <div style={{ marginBottom: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              backgroundColor: '#4f46e5',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff'
            }}
          >
            <Brain size={20} />
          </div>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 800, color: '#0f172a', margin: 0 }}>
              Clinical Reasoning Assistant
            </h2>
            <p style={{ fontSize: '13px', color: '#64748b', margin: '2px 0 0 0' }}>
              Synthesizes longitudinal patient memory, doctor assessments, caregiver observations, labs, and medications into evidence-linked clinical considerations.
            </p>
          </div>
        </div>
      </div>

      {/* Example Prompt Chips */}
      <div style={{ marginBottom: '14px' }}>
        <div style={{ fontSize: '12px', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>
          Example Clinical Inquiries:
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {EXAMPLE_QUESTIONS.map((eq, i) => (
            <button
              key={i}
              onClick={() => handleAnalyze(eq)}
              disabled={loading}
              style={{
                backgroundColor: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                padding: '6px 12px',
                fontSize: '12px',
                color: '#334155',
                cursor: loading ? 'not-allowed' : 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => {
                if (!loading) (e.currentTarget.style.backgroundColor = '#f1f5f9');
              }}
              onMouseLeave={(e) => {
                if (!loading) (e.currentTarget.style.backgroundColor = '#f8fafc');
              }}
            >
              "{eq}"
            </button>
          ))}
        </div>
      </div>

      {/* Query Input & Action */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
          placeholder="Ask a clinical question (e.g. 'What possible problems should I consider for the recent dizziness?')..."
          disabled={loading}
          style={{
            flex: 1,
            padding: '12px 16px',
            fontSize: '14px',
            border: '1px solid #cbd5e1',
            borderRadius: '8px',
            outline: 'none',
            backgroundColor: '#ffffff'
          }}
          data-testid="reasoning-input"
        />
        <button
          onClick={() => handleAnalyze()}
          disabled={loading || !question.trim()}
          style={{
            backgroundColor: loading || !question.trim() ? '#94a3b8' : '#4f46e5',
            color: '#ffffff',
            border: 'none',
            borderRadius: '8px',
            padding: '0 20px',
            fontSize: '14px',
            fontWeight: 700,
            cursor: loading || !question.trim() ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
          data-testid="analyze-button"
        >
          {loading ? (
            <>
              <Activity size={16} className="animate-spin" />
              <span>Analyzing Context...</span>
            </>
          ) : (
            <>
              <Sparkles size={16} />
              <span>Analyze Patient Context</span>
            </>
          )}
        </button>
      </div>

      {/* Error / Rejection Banner */}
      {error && (
        <div
          style={{
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            padding: '14px 18px',
            color: '#991b1b',
            fontSize: '13px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '10px'
          }}
          data-testid="reasoning-error"
        >
          <ShieldAlert size={18} style={{ color: '#dc2626', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <div style={{ fontWeight: 700, marginBottom: '2px' }}>Clinical Reasoning Safety Alert:</div>
            <div>{error}</div>
          </div>
        </div>
      )}

      {/* Results Section */}
      {reasoningData && (
        <div data-testid="reasoning-results">
          {/* Patient Context Summary Pill Header */}
          <div
            style={{
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '10px',
              padding: '14px 18px',
              marginBottom: '20px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '12px', fontWeight: 800, color: '#334155', textTransform: 'uppercase' }}>
                Relevant Context Extracted for Evaluation
              </span>
              <span style={{ fontSize: '11px', color: '#64748b' }}>
                {reasoningData.context_summary.total_evidence_count} Total Patient Evidence Records
              </span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '10px', fontSize: '12px' }}>
              <div>
                <span style={{ fontWeight: 700, color: '#475569' }}>Diagnoses: </span>
                <span style={{ color: '#0f172a' }}>{reasoningData.context_summary.diagnoses.join(', ')}</span>
              </div>
              <div>
                <span style={{ fontWeight: 700, color: '#475569' }}>Active Medications: </span>
                <span style={{ color: '#0f172a' }}>{reasoningData.context_summary.active_medications.join(', ')}</span>
              </div>
              <div>
                <span style={{ fontWeight: 700, color: '#475569' }}>Known Unknowns: </span>
                <span style={{ color: '#b45309' }}>{reasoningData.context_summary.known_unknowns.length} parameters unconfirmed</span>
              </div>
            </div>
          </div>

          {/* AI Clinical Considerations Heading */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a', margin: 0 }}>
              Possible Clinical Considerations
            </h3>
            <span
              style={{
                fontSize: '11px',
                fontWeight: 700,
                backgroundColor: '#fef3c7',
                color: '#92400e',
                padding: '4px 10px',
                borderRadius: '6px',
                border: '1px solid #fde68a'
              }}
              data-testid="not-a-diagnosis-badge"
            >
              AI CLINICAL CONSIDERATION • NOT A DIAGNOSIS
            </span>
          </div>

          {/* Considerations Cards */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '24px' }}>
            {reasoningData.considerations.map((c, idx) => (
              <div
                key={idx}
                style={{
                  backgroundColor: '#ffffff',
                  borderRadius: '12px',
                  border: '1px solid #e2e8f0',
                  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.04)',
                  padding: '20px'
                }}
                data-testid={`consideration-card-${idx}`}
              >
                {/* Card Top */}
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                      <span
                        style={{
                          fontSize: '11px',
                          fontWeight: 700,
                          backgroundColor: '#e0e7ff',
                          color: '#3730a3',
                          padding: '2px 8px',
                          borderRadius: '4px'
                        }}
                      >
                        {c.category}
                      </span>
                      <span
                        style={{
                          fontSize: '11px',
                          fontWeight: 700,
                          backgroundColor: '#f1f5f9',
                          color: '#475569',
                          padding: '2px 8px',
                          borderRadius: '4px'
                        }}
                      >
                        STATUS: {c.status}
                      </span>
                      <span
                        style={{
                          fontSize: '11px',
                          fontWeight: 700,
                          backgroundColor:
                            c.evidence_strength === 'STRONG'
                              ? '#dcfce7'
                              : c.evidence_strength === 'MODERATE'
                              ? '#fef9c3'
                              : '#f1f5f9',
                          color:
                            c.evidence_strength === 'STRONG'
                              ? '#166534'
                              : c.evidence_strength === 'MODERATE'
                              ? '#854d0e'
                              : '#475569',
                          padding: '2px 8px',
                          borderRadius: '4px'
                        }}
                      >
                        EVIDENCE STRENGTH: {c.evidence_strength}
                      </span>
                    </div>
                    <h4 style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a', margin: 0 }}>
                      {idx + 1}. {c.title}
                    </h4>
                  </div>
                </div>

                {/* Description */}
                <p style={{ fontSize: '13px', color: '#334155', lineHeight: '1.5', margin: '0 0 12px 0' }}>
                  {c.description}
                </p>

                {/* Clinical Reasoning Details */}
                <div
                  style={{
                    backgroundColor: '#f8fafc',
                    borderRadius: '8px',
                    padding: '12px 14px',
                    marginBottom: '14px',
                    fontSize: '12px',
                    color: '#334155'
                  }}
                >
                  <div style={{ fontWeight: 700, color: '#1e293b', marginBottom: '4px' }}>Clinical Rationale:</div>
                  <div style={{ lineHeight: '1.5' }}>{c.reasoning}</div>
                </div>

                {/* 2-Column Supporting vs Contradicting Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px', marginBottom: '14px' }}>
                  {/* Supporting Evidence */}
                  <div
                    style={{
                      backgroundColor: '#f0fdf4',
                      border: '1px solid #bbf7d0',
                      borderRadius: '8px',
                      padding: '12px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                      <CheckCircle2 size={14} style={{ color: '#16a34a' }} />
                      <span style={{ fontSize: '12px', fontWeight: 700, color: '#166534' }}>
                        Supporting Evidence ({c.supporting_evidence.length})
                      </span>
                    </div>
                    {c.supporting_evidence.length > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {c.supporting_evidence.map((ev, i) => (
                          <div key={i} style={{ fontSize: '12px', color: '#14532d' }}>
                            <button
                              onClick={() => onSelectEvidence(ev.evidence_id)}
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '4px',
                                backgroundColor: '#dcfce7',
                                color: '#15803d',
                                border: '1px solid #86efac',
                                borderRadius: '4px',
                                padding: '2px 6px',
                                fontSize: '11px',
                                fontWeight: 700,
                                cursor: 'pointer',
                                marginRight: '6px'
                              }}
                              title="Click to view raw evidence statement"
                            >
                              <span>{ev.evidence_id}</span>
                              <ChevronRight size={10} />
                            </button>
                            <span style={{ fontSize: '11px', color: '#166534' }}>({ev.source_type})</span>
                            <div style={{ fontSize: '11px', marginTop: '2px', fontStyle: 'italic' }}>
                              "{ev.original_statement}"
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div style={{ fontSize: '11px', color: '#64748b' }}>No direct supporting citations.</div>
                    )}
                  </div>

                  {/* Contradicting / Weakening Evidence */}
                  <div
                    style={{
                      backgroundColor: '#fffbeb',
                      border: '1px solid #fde68a',
                      borderRadius: '8px',
                      padding: '12px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                      <HelpCircle size={14} style={{ color: '#d97706' }} />
                      <span style={{ fontSize: '12px', fontWeight: 700, color: '#92400e' }}>
                        Contradicting / Weakening Evidence
                      </span>
                    </div>
                    {c.contradicting_evidence.length > 0 ? (
                      <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '11px', color: '#78350f', lineHeight: '1.4' }}>
                        {c.contradicting_evidence.map((ce, i) => (
                          <li key={i}>{ce}</li>
                        ))}
                      </ul>
                    ) : (
                      <div style={{ fontSize: '11px', color: '#64748b' }}>No contradicting evidence identified.</div>
                    )}
                  </div>
                </div>

                {/* Missing Info & Uncertainty */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '11px', color: '#64748b' }}>
                  {c.missing_information.length > 0 && (
                    <div>
                      <strong style={{ color: '#475569' }}>Parameters needed to evaluate:</strong>{' '}
                      {c.missing_information.join('; ')}
                    </div>
                  )}
                  {c.uncertainty && (
                    <div>
                      <strong style={{ color: '#475569' }}>Evidentiary Uncertainty:</strong> {c.uncertainty}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Longitudinal Trajectory Changes & Red Flags Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px', marginBottom: '20px' }}>
            {/* Recent Longitudinal Changes */}
            <div
              style={{
                backgroundColor: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '10px',
                padding: '16px'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
                <Clock size={16} style={{ color: '#4f46e5' }} />
                <h4 style={{ fontSize: '13px', fontWeight: 800, color: '#1e293b', margin: 0 }}>
                  Relevant Longitudinal Trajectory
                </h4>
              </div>
              <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '12px', color: '#334155', lineHeight: '1.5' }}>
                {reasoningData.relevant_changes.map((rc, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{rc}</li>
                ))}
              </ul>
            </div>

            {/* Red Flags for Clinical Attention */}
            <div
              style={{
                backgroundColor: '#fff7ed',
                border: '1px solid #fed7aa',
                borderRadius: '10px',
                padding: '16px'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
                <AlertOctagon size={16} style={{ color: '#ea580c' }} />
                <h4 style={{ fontSize: '13px', fontWeight: 800, color: '#9a3412', margin: 0 }}>
                  Red Flags for Prompt Clinical Assessment
                </h4>
              </div>
              {reasoningData.red_flags.length > 0 ? (
                <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '12px', color: '#7c2d12', lineHeight: '1.5' }}>
                  {reasoningData.red_flags.map((rf, i) => (
                    <li key={i} style={{ marginBottom: '4px' }}>{rf}</li>
                  ))}
                </ul>
              ) : (
                <div style={{ fontSize: '12px', color: '#9a3412' }}>No acute red flags identified in context.</div>
              )}
            </div>
          </div>

          {/* Missing Information for Clarification */}
          {reasoningData.missing_information.length > 0 && (
            <div
              style={{
                backgroundColor: '#f1f5f9',
                borderRadius: '8px',
                padding: '12px 16px',
                marginBottom: '18px',
                fontSize: '12px',
                color: '#334155'
              }}
            >
              <div style={{ fontWeight: 700, color: '#1e293b', marginBottom: '4px' }}>
                Information that may help clarify this question:
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {reasoningData.missing_information.map((mi, i) => (
                  <span
                    key={i}
                    style={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #cbd5e1',
                      borderRadius: '4px',
                      padding: '2px 8px',
                      fontSize: '11px',
                      color: '#475569'
                    }}
                  >
                    • {mi}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Doctor Decision Disclaimer Banner */}
          <div
            style={{
              backgroundColor: '#f8fafc',
              border: '1px solid #cbd5e1',
              borderRadius: '8px',
              padding: '12px 16px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px'
            }}
          >
            <Info size={18} style={{ color: '#0284c7', flexShrink: 0 }} />
            <div style={{ fontSize: '12px', color: '#475569', lineHeight: '1.4' }}>
              <strong>Doctor Decision Disclaimer:</strong> {reasoningData.disclaimer}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

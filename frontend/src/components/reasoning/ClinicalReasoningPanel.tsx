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
        backgroundColor: 'var(--color-surface)',
        borderRadius: '16px',
        border: '1px solid var(--color-border-strong)',
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
          backgroundColor: 'var(--color-accent-soft)',
          border: '1px solid var(--color-accent-border)',
          borderRadius: '8px',
          padding: '10px 16px',
          marginBottom: '18px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Stethoscope size={18} style={{ color: 'var(--color-accent)' }} />
          <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--color-accent-dark)', letterSpacing: '0.05em' }}>
            DOCTOR-ONLY CLINICAL REASONING
          </span>
          <span
            style={{
              fontSize: '11px',
              backgroundColor: 'var(--color-accent-soft)',
              color: 'var(--color-accent-dark)',
              padding: '2px 8px',
              borderRadius: '4px',
              fontWeight: 600
            }}
          >
            DEMO MODE — AUTHENTICATION NOT YET ENABLED (PHASE 8)
          </span>
        </div>
        <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
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
              backgroundColor: 'var(--color-plum)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff'
            }}
          >
            <Brain size={20} />
          </div>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--color-text-main)', margin: 0 }}>
              Clinical Reasoning Assistant
            </h2>
            <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: '2px 0 0 0' }}>
              Synthesizes longitudinal patient memory, doctor assessments, caregiver observations, labs, and medications into evidence-linked clinical considerations.
            </p>
          </div>
        </div>
      </div>

      {/* Example Prompt Chips */}
      <div style={{ marginBottom: '14px' }}>
        <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '6px' }}>
          Example Clinical Inquiries:
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {EXAMPLE_QUESTIONS.map((eq, i) => (
            <button
              key={i}
              onClick={() => handleAnalyze(eq)}
              disabled={loading}
              style={{
                backgroundColor: 'var(--color-bg)',
                border: '1px solid var(--color-border)',
                borderRadius: '6px',
                padding: '6px 12px',
                fontSize: '12px',
                color: 'var(--color-text-secondary)',
                cursor: loading ? 'not-allowed' : 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => {
                if (!loading) (e.currentTarget.style.backgroundColor = 'var(--color-surface-alt)');
              }}
              onMouseLeave={(e) => {
                if (!loading) (e.currentTarget.style.backgroundColor = 'var(--color-bg)');
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
            border: '1px solid var(--color-border-strong)',
            borderRadius: '8px',
            outline: 'none',
            backgroundColor: 'var(--color-surface)'
          }}
          data-testid="reasoning-input"
        />
        <button
          onClick={() => handleAnalyze()}
          disabled={loading || !question.trim()}
          style={{
            backgroundColor: loading || !question.trim() ? 'var(--color-text-faint)' : 'var(--color-plum)',
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
            backgroundColor: 'var(--color-danger-soft)',
            border: '1px solid var(--color-danger-border)',
            borderRadius: '8px',
            padding: '14px 18px',
            color: 'var(--color-danger-dark)',
            fontSize: '13px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '10px'
          }}
          data-testid="reasoning-error"
        >
          <ShieldAlert size={18} style={{ color: 'var(--color-danger)', flexShrink: 0, marginTop: '2px' }} />
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
              backgroundColor: 'var(--color-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: '10px',
              padding: '14px 18px',
              marginBottom: '20px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>
                Relevant Context Extracted for Evaluation
              </span>
              <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                {reasoningData.context_summary.total_evidence_count} Total Patient Evidence Records
              </span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '10px', fontSize: '12px' }}>
              <div>
                <span style={{ fontWeight: 700, color: 'var(--color-text-secondary)' }}>Diagnoses: </span>
                <span style={{ color: 'var(--color-text-main)' }}>{reasoningData.context_summary.diagnoses.join(', ')}</span>
              </div>
              <div>
                <span style={{ fontWeight: 700, color: 'var(--color-text-secondary)' }}>Active Medications: </span>
                <span style={{ color: 'var(--color-text-main)' }}>{reasoningData.context_summary.active_medications.join(', ')}</span>
              </div>
              <div>
                <span style={{ fontWeight: 700, color: 'var(--color-text-secondary)' }}>Known Unknowns: </span>
                <span style={{ color: 'var(--color-warning-dark)' }}>{reasoningData.context_summary.known_unknowns.length} parameters unconfirmed</span>
              </div>
            </div>
          </div>

          {/* AI Clinical Considerations Heading */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--color-text-main)', margin: 0 }}>
              Possible Clinical Considerations
            </h3>
            <span
              style={{
                fontSize: '11px',
                fontWeight: 700,
                backgroundColor: 'var(--color-warning-soft)',
                color: 'var(--color-warning-dark)',
                padding: '4px 10px',
                borderRadius: '6px',
                border: '1px solid var(--color-warning-border)'
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
                  backgroundColor: 'var(--color-surface)',
                  borderRadius: '12px',
                  border: '1px solid var(--color-border)',
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
                          backgroundColor: 'var(--color-plum-soft)',
                          color: 'var(--color-plum-dark)',
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
                          backgroundColor: 'var(--color-surface-alt)',
                          color: 'var(--color-text-secondary)',
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
                              ? 'var(--color-success-soft)'
                              : c.evidence_strength === 'MODERATE'
                              ? 'var(--color-warning-soft)'
                              : 'var(--color-surface-alt)',
                          color:
                            c.evidence_strength === 'STRONG'
                              ? 'var(--color-success-dark)'
                              : c.evidence_strength === 'MODERATE'
                              ? 'var(--color-warning-dark)'
                              : 'var(--color-text-secondary)',
                          padding: '2px 8px',
                          borderRadius: '4px'
                        }}
                      >
                        EVIDENCE STRENGTH: {c.evidence_strength}
                      </span>
                    </div>
                    <h4 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--color-text-main)', margin: 0 }}>
                      {idx + 1}. {c.title}
                    </h4>
                  </div>
                </div>

                {/* Description */}
                <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', lineHeight: '1.5', margin: '0 0 12px 0' }}>
                  {c.description}
                </p>

                {/* Clinical Reasoning Details */}
                <div
                  style={{
                    backgroundColor: 'var(--color-bg)',
                    borderRadius: '8px',
                    padding: '12px 14px',
                    marginBottom: '14px',
                    fontSize: '12px',
                    color: 'var(--color-text-secondary)'
                  }}
                >
                  <div style={{ fontWeight: 700, color: 'var(--color-text-main)', marginBottom: '4px' }}>Clinical Rationale:</div>
                  <div style={{ lineHeight: '1.5' }}>{c.reasoning}</div>
                </div>

                {/* 2-Column Supporting vs Contradicting Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px', marginBottom: '14px' }}>
                  {/* Supporting Evidence */}
                  <div
                    style={{
                      backgroundColor: 'var(--color-success-soft)',
                      border: '1px solid var(--color-success-border)',
                      borderRadius: '8px',
                      padding: '12px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                      <CheckCircle2 size={14} style={{ color: 'var(--color-success)' }} />
                      <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-success-dark)' }}>
                        Supporting Evidence ({c.supporting_evidence.length})
                      </span>
                    </div>
                    {c.supporting_evidence.length > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {c.supporting_evidence.map((ev, i) => (
                          <div key={i} style={{ fontSize: '12px', color: 'var(--color-success-dark)' }}>
                            <button
                              onClick={() => onSelectEvidence(ev.evidence_id)}
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '4px',
                                backgroundColor: 'var(--color-success-soft)',
                                color: 'var(--color-success)',
                                border: '1px solid var(--color-success-border)',
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
                            <span style={{ fontSize: '11px', color: 'var(--color-success-dark)' }}>({ev.source_type})</span>
                            <div style={{ fontSize: '11px', marginTop: '2px', fontStyle: 'italic' }}>
                              "{ev.original_statement}"
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>No direct supporting citations.</div>
                    )}
                  </div>

                  {/* Contradicting / Weakening Evidence */}
                  <div
                    style={{
                      backgroundColor: 'var(--color-warning-soft)',
                      border: '1px solid var(--color-warning-border)',
                      borderRadius: '8px',
                      padding: '12px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                      <HelpCircle size={14} style={{ color: 'var(--color-warning)' }} />
                      <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-warning-dark)' }}>
                        Contradicting / Weakening Evidence
                      </span>
                    </div>
                    {c.contradicting_evidence.length > 0 ? (
                      <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '11px', color: 'var(--color-warning-dark)', lineHeight: '1.4' }}>
                        {c.contradicting_evidence.map((ce, i) => (
                          <li key={i}>{ce}</li>
                        ))}
                      </ul>
                    ) : (
                      <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>No contradicting evidence identified.</div>
                    )}
                  </div>
                </div>

                {/* Missing Info & Uncertainty */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                  {c.missing_information.length > 0 && (
                    <div>
                      <strong style={{ color: 'var(--color-text-secondary)' }}>Parameters needed to evaluate:</strong>{' '}
                      {c.missing_information.join('; ')}
                    </div>
                  )}
                  {c.uncertainty && (
                    <div>
                      <strong style={{ color: 'var(--color-text-secondary)' }}>Evidentiary Uncertainty:</strong> {c.uncertainty}
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
                backgroundColor: 'var(--color-bg)',
                border: '1px solid var(--color-border)',
                borderRadius: '10px',
                padding: '16px'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
                <Clock size={16} style={{ color: 'var(--color-plum)' }} />
                <h4 style={{ fontSize: '13px', fontWeight: 800, color: 'var(--color-text-main)', margin: 0 }}>
                  Relevant Longitudinal Trajectory
                </h4>
              </div>
              <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '12px', color: 'var(--color-text-secondary)', lineHeight: '1.5' }}>
                {reasoningData.relevant_changes.map((rc, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{rc}</li>
                ))}
              </ul>
            </div>

            {/* Red Flags for Clinical Attention */}
            <div
              style={{
                backgroundColor: 'var(--color-warning-soft)',
                border: '1px solid var(--color-warning-border)',
                borderRadius: '10px',
                padding: '16px'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
                <AlertOctagon size={16} style={{ color: 'var(--color-warning)' }} />
                <h4 style={{ fontSize: '13px', fontWeight: 800, color: 'var(--color-warning-dark)', margin: 0 }}>
                  Red Flags for Prompt Clinical Assessment
                </h4>
              </div>
              {reasoningData.red_flags.length > 0 ? (
                <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '12px', color: 'var(--color-warning-dark)', lineHeight: '1.5' }}>
                  {reasoningData.red_flags.map((rf, i) => (
                    <li key={i} style={{ marginBottom: '4px' }}>{rf}</li>
                  ))}
                </ul>
              ) : (
                <div style={{ fontSize: '12px', color: 'var(--color-warning-dark)' }}>No acute red flags identified in context.</div>
              )}
            </div>
          </div>

          {/* Missing Information for Clarification */}
          {reasoningData.missing_information.length > 0 && (
            <div
              style={{
                backgroundColor: 'var(--color-surface-alt)',
                borderRadius: '8px',
                padding: '12px 16px',
                marginBottom: '18px',
                fontSize: '12px',
                color: 'var(--color-text-secondary)'
              }}
            >
              <div style={{ fontWeight: 700, color: 'var(--color-text-main)', marginBottom: '4px' }}>
                Information that may help clarify this question:
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {reasoningData.missing_information.map((mi, i) => (
                  <span
                    key={i}
                    style={{
                      backgroundColor: 'var(--color-surface)',
                      border: '1px solid var(--color-border-strong)',
                      borderRadius: '4px',
                      padding: '2px 8px',
                      fontSize: '11px',
                      color: 'var(--color-text-secondary)'
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
              backgroundColor: 'var(--color-bg)',
              border: '1px solid var(--color-border-strong)',
              borderRadius: '8px',
              padding: '12px 16px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px'
            }}
          >
            <Info size={18} style={{ color: 'var(--color-accent)', flexShrink: 0 }} />
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', lineHeight: '1.4' }}>
              <strong>Doctor Decision Disclaimer:</strong> {reasoningData.disclaimer}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

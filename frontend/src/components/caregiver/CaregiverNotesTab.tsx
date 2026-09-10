import React, { useState } from 'react';
import {
  FileText,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Clock,
  User,
  ShieldCheck,
  Check,
  RotateCcw,
  BookOpen
} from 'lucide-react';
import { DashboardResponse } from '../../types';
import { apiService } from '../../services/api';
import { AuthUser } from '../../services/auth';
import { CaregiverRequestNotificationBanner } from '../connection/CaregiverRequestNotificationBanner';

interface CaregiverNotesTabProps {
  data: DashboardResponse;
  user: AuthUser;
  onObservationSaved: () => void;
}

interface ClarificationQuestionState {
  id: number;
  fieldName: string;
  questionText: string;
  options: string[];
  selectedAnswer: string;
  isCustom: boolean;
}

const SAMPLE_NOTES = [
  'She felt dizzy after getting out of bed this morning and held the wall for support.',
  'She needed someone arm while walking outside in the garden today.',
  'She finished only half of her lunch today and complained of low appetite.',
  'She almost fell near the bathroom but I caught her in time; zero injury occurred.',
  'She woke up three times last night and seemed restless.'
];

export const CaregiverNotesTab: React.FC<CaregiverNotesTabProps> = ({
  data,
  user,
  onObservationSaved,
}) => {
  const [noteText, setNoteText] = useState('');
  const [caregiverId] = useState('CG001');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Session state from backend
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [detectedCategory, setDetectedCategory] = useState<string | null>(null);
  const [questions, setQuestions] = useState<ClarificationQuestionState[]>([]);
  const [requiresClarification, setRequiresClarification] = useState(false);

  // Completed result state
  const [completedResult, setCompletedResult] = useState<{
    evidenceCode: string;
    category: string;
    wikiUpdated: boolean;
    wikiFiles?: string[];
    structuredObservation?: any;
  } | null>(null);

  const handleStartAnalysis = async () => {
    const trimmed = noteText.trim();
    if (!trimmed || loading) return;

    setLoading(true);
    setError(null);
    setCompletedResult(null);

    try {
      const res = await apiService.startObservation(
        data.patient.patient_code,
        trimmed,
        caregiverId
      );

      setSessionId(res.session_id);
      // Backend returns 'category' not 'detected_category'
      setDetectedCategory((res as any).category || (res as any).detected_category || null);
      // requires_clarification lives in observation sub-object
      const requiresClar = (res as any).observation?.requires_clarification
        ?? ((res as any).missing_fields?.length > 0)
        ?? false;
      setRequiresClarification(requiresClar);

      if (res.questions && res.questions.length > 0) {
        const qStates: ClarificationQuestionState[] = res.questions.map((q: any) => ({
          id: q.id,
          fieldName: q.field_name,
          // Backend returns 'question' not 'question_text'
          questionText: q.question_text || q.question || '',
          options: q.options || [],
          selectedAnswer: '',
          isCustom: false,
        }));
        setQuestions(qStates);
      } else {
        setQuestions([]);
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to analyze observation note.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = async (questionIdx: number, answerText: string) => {
    if (!sessionId) return;
    const targetQ = questions[questionIdx];
    if (!targetQ) return;

    // Update local state
    const updated = [...questions];
    updated[questionIdx].selectedAnswer = answerText;
    updated[questionIdx].isCustom = false;
    setQuestions(updated);

    try {
      await apiService.answerClarification(
        sessionId,
        targetQ.id,
        targetQ.fieldName,
        answerText
      );
    } catch (err: any) {
      console.warn('Failed to record answer on backend:', err);
    }
  };

  const handleCompleteSession = async () => {
    if (!sessionId || loading) return;

    setLoading(true);
    setError(null);

    try {
      const res = await apiService.completeClarification(sessionId);
      setCompletedResult({
        evidenceCode: res.evidence_code,
        category: res.category,
        wikiUpdated: !!res.wiki_updated,
        wikiFiles: res.wiki_files,
        structuredObservation: res.structured_observation,
      });

      // Refetch dashboard data so recent observations update
      onObservationSaved();
    } catch (err: any) {
      setError(err?.message || 'Failed to finalize observation and update Wiki.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setNoteText('');
    setSessionId(null);
    setDetectedCategory(null);
    setQuestions([]);
    setRequiresClarification(false);
    setCompletedResult(null);
    setError(null);
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px 20px 60px 20px' }}>
      {/* Top Caregiver Header Card */}
      <div
        style={{
          backgroundColor: 'var(--color-surface)',
          borderRadius: '12px',
          border: '1px solid var(--color-border)',
          padding: '20px 24px',
          marginBottom: '24px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.03)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '10px',
              backgroundColor: 'var(--color-success)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--color-surface)',
              boxShadow: '0 2px 6px rgba(5, 150, 105, 0.25)',
              flexShrink: 0,
            }}
          >
            <FileText size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontSize: '18px', fontWeight: 700, margin: 0, color: 'var(--color-text-main)' }}>
                Caregiver Daily Observation &amp; Notes
              </h2>
              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  backgroundColor: 'var(--color-success-soft)',
                  color: 'var(--color-success-dark)',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  border: '1px solid var(--color-success-border)',
                }}
              >
                Caregiver Portal
              </span>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: '4px 0 0 0' }}>
              Record home observations for <b>{data.patient.name} ({data.patient.patient_code})</b>. EvoCare AI evaluates clarity and updates the patient's existing wiki files.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              fontSize: '12px',
              color: 'var(--color-text-secondary)',
              backgroundColor: 'var(--color-bg)',
              padding: '6px 12px',
              borderRadius: '6px',
              border: '1px solid var(--color-border)',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <User size={13} style={{ color: 'var(--color-success)' }} />
            <span>Observer: <b>{user.full_name || 'Caregiver'} ({caregiverId})</b></span>
          </div>

          <button
            onClick={handleReset}
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              border: '1px solid var(--color-border-strong)',
              backgroundColor: 'var(--color-surface)',
              color: 'var(--color-text-secondary)',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <RotateCcw size={13} />
            <span>New Note</span>
          </button>
        </div>
      </div>

      {/* Patient Pairing Requests & Active Pairings Banner */}
      <CaregiverRequestNotificationBanner onConnectionsChanged={onObservationSaved} />

      {/* Main Grid: Input Column & History Feed */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '24px' }}>
        {/* Left Column: Note Entry & Clarification Flow */}
        <div>
          {/* Note Input Box */}
          <div
            style={{
              backgroundColor: 'var(--color-surface)',
              borderRadius: '12px',
              border: '1px solid var(--color-border)',
              padding: '20px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.03)',
              marginBottom: '24px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <label style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-text-main)' }}>
                Enter Today's Observation
              </label>
              <span style={{ fontSize: '11px', color: 'var(--color-text-faint)' }}>Plain natural language</span>
            </div>

            <textarea
              id="caregiver-note-input"
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
              placeholder="Describe what you observed (e.g., 'She felt dizzy when getting out of bed this morning', 'She needed support walking outside', 'She only finished half her lunch')..."
              rows={4}
              disabled={loading || sessionId !== null}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid var(--color-border-strong)',
                fontSize: '14px',
                color: 'var(--color-text-main)',
                boxSizing: 'border-box',
                resize: 'vertical',
                outline: 'none',
                fontFamily: 'inherit',
                lineHeight: '1.5',
                backgroundColor: sessionId !== null ? 'var(--color-bg)' : 'var(--color-surface)',
              }}
            />

            {/* Quick Helper Chips (only when not yet submitted) */}
            {sessionId === null && (
              <div style={{ marginTop: '12px' }}>
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontWeight: 600, marginBottom: '6px' }}>
                  Sample Observations:
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {SAMPLE_NOTES.map((sample, idx) => (
                    <button
                      key={idx}
                      onClick={() => setNoteText(sample)}
                      style={{
                        backgroundColor: 'var(--color-surface-alt)',
                        border: '1px solid var(--color-border)',
                        borderRadius: '14px',
                        padding: '4px 10px',
                        fontSize: '11px',
                        color: 'var(--color-text-secondary)',
                        cursor: 'pointer',
                        textAlign: 'left',
                      }}
                    >
                      {sample}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Options Row */}
            <div
              style={{
                marginTop: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '12px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', color: 'var(--color-text-muted)' }}>
                  <Clock size={14} />
                  <span>Observed: Today</span>
                </div>
              </div>

              {sessionId === null && (
                <button
                  id="caregiver-analyze-btn"
                  onClick={handleStartAnalysis}
                  disabled={!noteText.trim() || loading}
                  style={{
                    padding: '8px 18px',
                    borderRadius: '8px',
                    border: 'none',
                    backgroundColor: noteText.trim() && !loading ? 'var(--color-success)' : 'var(--color-border-strong)',
                    color: 'var(--color-surface)',
                    fontWeight: 700,
                    fontSize: '13px',
                    cursor: noteText.trim() && !loading ? 'pointer' : 'default',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    boxShadow: noteText.trim() && !loading ? '0 2px 6px rgba(5, 150, 105, 0.3)' : 'none',
                  }}
                >
                  <Sparkles size={16} />
                  <span>{loading ? 'Analyzing with AI…' : 'Analyze & Process Note'}</span>
                </button>
              )}
            </div>

            {error && (
              <div
                style={{
                  marginTop: '14px',
                  backgroundColor: 'var(--color-danger-soft)',
                  border: '1px solid var(--color-danger-border)',
                  borderRadius: '8px',
                  padding: '10px 14px',
                  color: 'var(--color-danger-dark)',
                  fontSize: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <AlertCircle size={15} style={{ flexShrink: 0 }} />
                <span>{error}</span>
              </div>
            )}
          </div>

          {/* AI Ambiguity / Clarification Interactive Flow */}
          {sessionId !== null && !completedResult && (
            <div
              style={{
                backgroundColor: 'var(--color-surface)',
                borderRadius: '12px',
                border: '1px solid var(--color-border)',
                padding: '20px',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.03)',
                marginBottom: '24px',
              }}
            >
              {requiresClarification ? (
                <>
                  <div
                    style={{
                      backgroundColor: 'var(--color-warning-soft)',
                      border: '1px solid var(--color-warning-soft)',
                      borderRadius: '8px',
                      padding: '12px 16px',
                      marginBottom: '16px',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '10px',
                    }}
                  >
                    <HelpCircle size={18} style={{ color: 'var(--color-warning)', marginTop: '2px', flexShrink: 0 }} />
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-warning-dark)' }}>
                        AI Ambiguity Check: Additional Details Needed
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--color-warning-dark)', marginTop: '2px', lineHeight: '1.4' }}>
                        To help Dr. Ramesh Varma understand the context accurately, please answer the quick clarification questions below:
                      </div>
                    </div>
                  </div>

                  {/* Clarification Questions */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '20px' }}>
                    {questions.map((q, qIdx) => (
                      <div
                        key={q.id}
                        style={{
                          backgroundColor: 'var(--color-bg)',
                          borderRadius: '8px',
                          border: '1px solid var(--color-border)',
                          padding: '12px 14px',
                        }}
                      >
                        <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '8px' }}>
                          {qIdx + 1}. {q.questionText}
                        </div>

                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                          {q.options.map((opt, oIdx) => {
                            const isSelected = q.selectedAnswer === opt;
                            return (
                              <button
                                key={oIdx}
                                onClick={() => handleSelectOption(qIdx, opt)}
                                style={{
                                  padding: '6px 12px',
                                  borderRadius: '6px',
                                  border: isSelected ? '2px solid var(--color-success)' : '1px solid var(--color-border-strong)',
                                  backgroundColor: isSelected ? 'var(--color-success-soft)' : 'var(--color-surface)',
                                  color: isSelected ? 'var(--color-success-dark)' : 'var(--color-text-secondary)',
                                  fontSize: '12px',
                                  fontWeight: isSelected ? 700 : 500,
                                  cursor: 'pointer',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '6px',
                                  transition: 'all 0.1s ease',
                                }}
                              >
                                {isSelected && <Check size={14} style={{ color: 'var(--color-success)' }} />}
                                <span>{opt}</span>
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div
                  style={{
                    backgroundColor: 'var(--color-success-soft)',
                    border: '1px solid var(--color-success-border)',
                    borderRadius: '8px',
                    padding: '14px 16px',
                    marginBottom: '18px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                  }}
                >
                  <CheckCircle2 size={20} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-success-dark)' }}>
                      Observation is Clear &amp; Complete
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-success-dark)', marginTop: '2px' }}>
                      Category: <b>{detectedCategory?.toUpperCase()}</b>. No ambiguous points detected. Ready to persist.
                    </div>
                  </div>
                </div>
              )}

              {/* Complete and Sync Button */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button
                  onClick={handleReset}
                  style={{
                    padding: '8px 14px',
                    borderRadius: '8px',
                    border: '1px solid var(--color-border-strong)',
                    backgroundColor: 'var(--color-surface)',
                    color: 'var(--color-text-secondary)',
                    fontSize: '13px',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>

                <button
                  id="caregiver-complete-btn"
                  onClick={handleCompleteSession}
                  disabled={loading}
                  style={{
                    padding: '8px 18px',
                    borderRadius: '8px',
                    border: 'none',
                    backgroundColor: 'var(--color-success)',
                    color: 'var(--color-surface)',
                    fontWeight: 700,
                    fontSize: '13px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    boxShadow: '0 2px 6px rgba(5, 150, 105, 0.3)',
                  }}
                >
                  <ShieldCheck size={16} />
                  <span>{loading ? 'Updating Wiki…' : 'Confirm & Save to Patient Wiki'}</span>
                </button>
              </div>
            </div>
          )}

          {/* Success Banner upon completion */}
          {completedResult && (
            <div
              style={{
                backgroundColor: 'var(--color-success-soft)',
                borderRadius: '12px',
                border: '1px solid var(--color-success-border)',
                padding: '20px',
                marginBottom: '24px',
                boxShadow: '0 4px 12px rgba(22, 163, 74, 0.08)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                <div
                  style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--color-success)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--color-surface)',
                    flexShrink: 0,
                  }}
                >
                  <Check size={20} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--color-success-dark)' }}>
                    Observation Recorded &amp; Synchronized to Existing Wiki File!
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--color-success-dark)', marginTop: '4px', lineHeight: '1.5' }}>
                    Assigned Evidence Code: <span style={{ fontFamily: 'monospace', fontWeight: 700 }}>{completedResult.evidenceCode}</span>
                    <br />
                    Category: <b>{completedResult.category}</b>
                  </div>

                  {completedResult.wikiUpdated && (
                    <div
                      style={{
                        marginTop: '10px',
                        padding: '8px 12px',
                        backgroundColor: 'var(--color-surface)',
                        border: '1px solid var(--color-success-border)',
                        borderRadius: '6px',
                        fontSize: '12px',
                        color: 'var(--color-success)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                      }}
                    >
                      <BookOpen size={14} />
                      <span>Directly modified existing Markdown file: <b>Caregiver/{completedResult.category.charAt(0).toUpperCase() + completedResult.category.slice(1)}.md</b></span>
                    </div>
                  )}

                  <div style={{ marginTop: '16px' }}>
                    <button
                      onClick={handleReset}
                      style={{
                        padding: '6px 14px',
                        borderRadius: '6px',
                        border: 'none',
                        backgroundColor: 'var(--color-success)',
                        color: 'var(--color-surface)',
                        fontWeight: 700,
                        fontSize: '12px',
                        cursor: 'pointer',
                      }}
                    >
                      + Record Another Observation
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Historical Observations Log */}
        <div>
          <div
            style={{
              backgroundColor: 'var(--color-surface)',
              borderRadius: '12px',
              border: '1px solid var(--color-border)',
              padding: '20px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.03)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Clock size={16} style={{ color: 'var(--color-success)' }} />
                <h3 style={{ fontSize: '14px', fontWeight: 700, margin: 0, color: 'var(--color-text-main)' }}>
                  Recent Caregiver Observations On File
                </h3>
              </div>
              <span style={{ fontSize: '11px', color: 'var(--color-text-faint)' }}>
                Total: {data.caregiver_observations.length} logs
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '580px', overflowY: 'auto' }}>
              {data.caregiver_observations.slice(0, 15).map((obs) => (
                <div
                  key={obs.id}
                  style={{
                    padding: '12px 14px',
                    borderRadius: '8px',
                    border: '1px solid var(--color-surface-alt)',
                    backgroundColor: 'var(--color-bg)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span
                      style={{
                        fontSize: '10px',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        backgroundColor: 'var(--color-accent-soft)',
                        color: 'var(--color-accent-dark)',
                        padding: '2px 6px',
                        borderRadius: '4px',
                      }}
                    >
                      {obs.category}
                    </span>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                      {obs.observed_at ? obs.observed_at.slice(0, 10) : '—'}
                    </span>
                  </div>

                  <div style={{ fontSize: '13px', color: 'var(--color-text-main)', lineHeight: '1.4', fontStyle: 'italic' }}>
                    "{obs.observation_text}"
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '6px', fontSize: '11px', color: 'var(--color-text-faint)' }}>
                    <span>Observer: {obs.caregiver_id}</span>
                    <span style={{ fontFamily: 'monospace' }}>{obs.evidence_code}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

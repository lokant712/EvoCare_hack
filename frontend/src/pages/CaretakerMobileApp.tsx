import React, { useState } from 'react';
import {
  FileText,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Clock,
  HeartHandshake,
  LogOut,
  Check,
  BookOpen,
  ShieldCheck,
  Plus,
  Smartphone,
  Laptop,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { DashboardResponse } from '../types';
import { apiService } from '../services/api';
import { AuthUser, AuthorizedPatient } from '../services/auth';
import { CaregiverRequestNotificationBanner } from '../components/connection/CaregiverRequestNotificationBanner';
import { ThemeToggle } from '../components/common/ThemeToggle';

interface CaretakerMobileAppProps {
  data: DashboardResponse;
  user: AuthUser;
  authorizedPatients?: AuthorizedPatient[];
  selectedPatientCode?: string;
  onSelectPatient?: (code: string) => void;
  onObservationSaved: () => void;
  onLogout?: () => void;
  onSwitchToDesktop?: () => void;
}

interface ClarificationQuestionState {
  id: number;
  fieldName: string;
  questionText: string;
  options: string[];
  selectedAnswer: string;
}

const QUICK_OBSERVATIONS = [
  { label: 'Morning Dizziness', text: 'She felt dizzy after getting out of bed this morning and held the wall for support.' },
  { label: 'Near-Fall / Stumbled', text: 'She almost fell near the bathroom door but I caught her in time; zero ground impact, no injury.' },
  { label: 'Low Appetite', text: 'She finished only half of her lunch today and complained of low appetite.' },
  { label: 'Walking Support', text: 'She needed someone’s arm while walking outside in the garden today.' },
  { label: 'Sleep Restless', text: 'She woke up three times last night and seemed restless.' },
  { label: 'Pillbox Taken', text: 'Morning blood pressure and diabetes medicines were taken on time with water.' },
];

export const CaretakerMobileApp: React.FC<CaretakerMobileAppProps> = ({
  data,
  user,
  authorizedPatients = [],
  onSelectPatient,
  onObservationSaved,
  onLogout,
  onSwitchToDesktop,
}) => {
  const [activeTab, setActiveTab] = useState<'log' | 'history' | 'pairing'>('log');
  const [noteText, setNoteText] = useState('');
  const [caregiverId] = useState(user.username || 'CG001');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isWideView, setIsWideView] = useState(false);

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
      setDetectedCategory((res as any).category || (res as any).detected_category || null);
      const requiresClar =
        (res as any).observation?.requires_clarification ??
        ((res as any).missing_fields?.length > 0) ??
        false;
      setRequiresClarification(requiresClar);

      if (res.questions && res.questions.length > 0) {
        const qStates: ClarificationQuestionState[] = res.questions.map((q: any) => ({
          id: q.id,
          fieldName: q.field_name,
          questionText: q.question_text || q.question || '',
          options: q.options || [],
          selectedAnswer: '',
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

    const updated = [...questions];
    updated[questionIdx].selectedAnswer = answerText;
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
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100dvh',
        backgroundColor: 'var(--color-bg)',
        alignItems: 'center',
        justifyContent: 'flex-start',
        position: 'relative',
        padding: isWideView ? '20px' : '0',
        transition: 'all 0.2s ease',
      }}
    >
      {/* Mobile Device Container Frame */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          height: isWideView ? '92vh' : '100dvh',
          width: '100%',
          maxWidth: isWideView ? '860px' : '480px',
          backgroundColor: 'var(--color-surface)',
          color: 'var(--color-text-main)',
          boxShadow: isWideView ? '0 10px 40px rgba(0, 0, 0, 0.15)' : 'none',
          borderRadius: isWideView ? '24px' : '0',
          position: 'relative',
          overflow: 'hidden',
          border: isWideView ? '1px solid var(--color-border-strong)' : 'none',
        }}
      >
        {/* 1. Mobile App Top Bar */}
        <header
          style={{
            padding: '12px 16px',
            backgroundColor: 'var(--color-surface)',
            borderBottom: '1px solid var(--color-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexShrink: 0,
            zIndex: 30,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: '12px',
                backgroundColor: 'var(--color-success)',
                color: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 2px 8px rgba(5, 150, 105, 0.35)',
                flexShrink: 0,
              }}
            >
              <HeartHandshake size={20} />
            </div>
            <div style={{ minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontSize: '14px', fontWeight: 800, color: 'var(--color-text-main)', whiteSpace: 'nowrap' }}>
                  EvoCare Caregiver
                </span>
                <span
                  style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    padding: '2px 7px',
                    borderRadius: '10px',
                    backgroundColor: 'var(--color-success-soft)',
                    color: 'var(--color-success-dark)',
                    border: '1px solid var(--color-success-border)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '3px',
                  }}
                >
                  <Smartphone size={10} /> Mobile
                </span>
              </div>

              {/* Patient Selector or Label */}
              {authorizedPatients.length > 1 && onSelectPatient ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}>
                  <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Patient:</span>
                  <select
                    value={data.patient.patient_code}
                    onChange={(e) => onSelectPatient(e.target.value)}
                    style={{
                      fontSize: '11.5px',
                      fontWeight: 700,
                      backgroundColor: 'var(--color-surface-alt)',
                      color: 'var(--color-text-main)',
                      border: '1px solid var(--color-border)',
                      borderRadius: '6px',
                      padding: '1px 6px',
                      outline: 'none',
                      cursor: 'pointer',
                    }}
                  >
                    {authorizedPatients.map((p) => (
                      <option key={p.patient_code} value={p.patient_code}>
                        {p.name} ({p.patient_code})
                      </option>
                    ))}
                  </select>
                </div>
              ) : (
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  Patient: <b style={{ color: 'var(--color-text-main)' }}>{data.patient.name}</b> ({data.patient.patient_code})
                </div>
              )}
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexShrink: 0 }}>
            {onSwitchToDesktop && (
              <button
                onClick={onSwitchToDesktop}
                title="Switch to PC Desktop Portal"
                style={{
                  padding: '4px 8px',
                  height: '32px',
                  borderRadius: '8px',
                  backgroundColor: 'var(--color-surface-alt)',
                  border: '1px solid var(--color-border)',
                  color: 'var(--color-text-main)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '11px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                <Laptop size={13} style={{ color: 'var(--color-accent)' }} />
                <span>PC View</span>
              </button>
            )}

            {/* Desktop Frame Mode Switcher */}
            <button
              onClick={() => setIsWideView(!isWideView)}
              title={isWideView ? 'Switch to Phone Frame' : 'Expand View'}
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                backgroundColor: 'var(--color-surface-alt)',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text-muted)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
              }}
            >
              {isWideView ? <Minimize2 size={13} /> : <Maximize2 size={13} />}
            </button>

            <ThemeToggle size="sm" />

            {onLogout && (
              <button
                onClick={onLogout}
                title="Sign Out"
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  backgroundColor: 'var(--color-surface-alt)',
                  border: '1px solid var(--color-border)',
                  color: 'var(--color-text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                }}
              >
                <LogOut size={13} />
              </button>
            )}
          </div>
        </header>

        {/* 2. Scrollable Body Content */}
        <main
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '14px 16px 85px 16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
            WebkitOverflowScrolling: 'touch',
          }}
        >
          {/* TAB 3: PAIRING / CONNECTION MANAGEMENT */}
          {activeTab === 'pairing' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div
                style={{
                  padding: '12px 14px',
                  borderRadius: '12px',
                  backgroundColor: 'var(--color-surface-alt)',
                  border: '1px solid var(--color-border)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                }}
              >
                <ShieldCheck size={20} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: '12.5px', fontWeight: 700, color: 'var(--color-text-main)' }}>
                    Caretaker Pairing &amp; Consent
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                    Review patient pairing requests and active verified connections.
                  </div>
                </div>
              </div>

              <CaregiverRequestNotificationBanner onConnectionsChanged={onObservationSaved} />
            </div>
          )}

          {/* TAB 1: LOG DAILY NOTE */}
          {activeTab === 'log' && (
            <>
              {/* Patient Snapshot Pill */}
              <div
                style={{
                  padding: '10px 14px',
                  borderRadius: '12px',
                  backgroundColor: 'var(--color-surface-alt)',
                  border: '1px solid var(--color-border)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '10px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
                  <div
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      backgroundColor: 'var(--color-accent-soft)',
                      color: 'var(--color-accent)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                      fontWeight: 700,
                      fontSize: '12px',
                    }}
                  >
                    {data.patient.name.charAt(0)}
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: '12.5px', fontWeight: 700, color: 'var(--color-text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {data.patient.name} · {data.patient.age}y {data.patient.sex}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                      Caregiver: <b style={{ color: 'var(--color-text-main)' }}>{user.full_name || user.username}</b>
                    </div>
                  </div>
                </div>

                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    color: 'var(--color-success)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    flexShrink: 0,
                    backgroundColor: 'var(--color-success-soft)',
                    padding: '3px 8px',
                    borderRadius: '8px',
                    border: '1px solid var(--color-success-border)',
                  }}
                >
                  <ShieldCheck size={13} /> Active
                </span>
              </div>

              {/* Note Entry Card */}
              <div
                style={{
                  backgroundColor: 'var(--color-surface)',
                  borderRadius: '16px',
                  border: '1px solid var(--color-border)',
                  padding: '16px',
                  boxShadow: '0 2px 10px rgba(0, 0, 0, 0.04)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <FileText size={15} style={{ color: 'var(--color-success)' }} />
                    <span style={{ fontSize: '13px', fontWeight: 800, color: 'var(--color-text-main)' }}>
                      Home Observation Note
                    </span>
                  </div>
                  <span style={{ fontSize: '11px', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Clock size={11} /> Today
                  </span>
                </div>

                {/* Observation Textarea */}
                <div>
                  <textarea
                    value={noteText}
                    onChange={(e) => setNoteText(e.target.value)}
                    placeholder="Type today's home observation (e.g., 'She felt dizzy after getting out of bed', 'Almost slipped near door, no fall', 'Finished half meal')..."
                    rows={4}
                    disabled={loading || sessionId !== null}
                    style={{
                      width: '100%',
                      padding: '12px 14px',
                      borderRadius: '12px',
                      border: '1px solid var(--color-border-strong)',
                      fontSize: '14px',
                      color: 'var(--color-text-main)',
                      backgroundColor: sessionId !== null ? 'var(--color-surface-alt)' : 'var(--color-bg)',
                      outline: 'none',
                      resize: 'none',
                      boxSizing: 'border-box',
                      fontFamily: 'inherit',
                      lineHeight: 1.5,
                    }}
                  />
                </div>

                {/* Quick Preset One-Tap Observation Chips */}
                {sessionId === null && (
                  <div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontWeight: 700, marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.4px' }}>
                      One-Tap Quick Presets:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {QUICK_OBSERVATIONS.map((item, idx) => (
                        <button
                          key={idx}
                          onClick={() => setNoteText(item.text)}
                          style={{
                            padding: '6px 11px',
                            borderRadius: '16px',
                            border: '1px solid var(--color-border)',
                            backgroundColor: 'var(--color-surface-alt)',
                            color: 'var(--color-text-secondary)',
                            fontSize: '11.5px',
                            fontWeight: 600,
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            transition: 'all 0.15s ease',
                          }}
                        >
                          <Plus size={11} style={{ color: 'var(--color-success)' }} />
                          <span>{item.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Analyze Button */}
                {sessionId === null && (
                  <button
                    onClick={handleStartAnalysis}
                    disabled={!noteText.trim() || loading}
                    style={{
                      width: '100%',
                      padding: '13px',
                      borderRadius: '12px',
                      border: 'none',
                      backgroundColor: noteText.trim() && !loading ? 'var(--color-success)' : 'var(--color-surface-alt)',
                      color: noteText.trim() && !loading ? '#ffffff' : 'var(--color-text-faint)',
                      fontSize: '14px',
                      fontWeight: 700,
                      cursor: noteText.trim() && !loading ? 'pointer' : 'default',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px',
                      boxShadow: noteText.trim() && !loading ? '0 4px 14px rgba(5, 150, 105, 0.35)' : 'none',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <Sparkles size={16} />
                    <span>{loading ? 'AI Analyzing Note…' : 'Evaluate & Process Note'}</span>
                  </button>
                )}

                {error && (
                  <div style={{ padding: '10px 12px', borderRadius: '10px', backgroundColor: 'var(--color-danger-soft)', color: 'var(--color-danger)', fontSize: '12.5px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <AlertCircle size={16} style={{ flexShrink: 0 }} />
                    <span>{error}</span>
                  </div>
                )}
              </div>

              {/* AI Ambiguity / Clarification Flow */}
              {sessionId !== null && !completedResult && (
                <div
                  style={{
                    backgroundColor: 'var(--color-surface)',
                    borderRadius: '16px',
                    border: '1px solid var(--color-border)',
                    padding: '16px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '14px',
                    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.04)',
                  }}
                >
                  {requiresClarification ? (
                    <>
                      <div
                        style={{
                          padding: '12px 14px',
                          borderRadius: '10px',
                          backgroundColor: 'var(--color-warning-soft)',
                          border: '1px solid var(--color-warning-border)',
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: '10px',
                        }}
                      >
                        <HelpCircle size={18} style={{ color: 'var(--color-warning-dark)', marginTop: '1px', flexShrink: 0 }} />
                        <div>
                          <div style={{ fontSize: '13px', fontWeight: 800, color: 'var(--color-warning-dark)' }}>
                            AI Clarification Needed
                          </div>
                          <div style={{ fontSize: '11.5px', color: 'var(--color-warning-dark)', marginTop: '2px' }}>
                            Tap the answer that best fits so the doctor gets accurate context:
                          </div>
                        </div>
                      </div>

                      {/* Touch Friendly Questions */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {questions.map((q, qIdx) => (
                          <div
                            key={q.id}
                            style={{
                              padding: '12px 14px',
                              borderRadius: '12px',
                              backgroundColor: 'var(--color-surface-alt)',
                              border: '1px solid var(--color-border)',
                            }}
                          >
                            <div style={{ fontSize: '12.5px', fontWeight: 700, color: 'var(--color-text-main)', marginBottom: '8px' }}>
                              {qIdx + 1}. {q.questionText}
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                              {q.options.map((opt, oIdx) => {
                                const isSelected = q.selectedAnswer === opt;
                                return (
                                  <button
                                    key={oIdx}
                                    onClick={() => handleSelectOption(qIdx, opt)}
                                    style={{
                                      padding: '10px 14px',
                                      borderRadius: '10px',
                                      border: `1.5px solid ${isSelected ? 'var(--color-success)' : 'var(--color-border)'}`,
                                      backgroundColor: isSelected ? 'var(--color-success-soft)' : 'var(--color-surface)',
                                      color: isSelected ? 'var(--color-success-dark)' : 'var(--color-text-main)',
                                      fontSize: '13px',
                                      fontWeight: isSelected ? 700 : 500,
                                      cursor: 'pointer',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'space-between',
                                      minHeight: '44px',
                                      textAlign: 'left',
                                      transition: 'all 0.15s ease',
                                    }}
                                  >
                                    <span>{opt}</span>
                                    {isSelected && <Check size={15} style={{ color: 'var(--color-success)' }} />}
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
                        padding: '12px 14px',
                        borderRadius: '10px',
                        backgroundColor: 'var(--color-success-soft)',
                        border: '1px solid var(--color-success-border)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                      }}
                    >
                      <CheckCircle2 size={18} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
                      <div style={{ fontSize: '12.5px', fontWeight: 600, color: 'var(--color-success-dark)' }}>
                        Observation is comprehensive! Category: <b>{detectedCategory?.toUpperCase()}</b>
                      </div>
                    </div>
                  )}

                  {/* Confirm & Sync */}
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      onClick={handleReset}
                      style={{
                        flex: 1,
                        padding: '12px',
                        borderRadius: '10px',
                        border: '1px solid var(--color-border)',
                        backgroundColor: 'transparent',
                        color: 'var(--color-text-muted)',
                        fontSize: '13px',
                        fontWeight: 600,
                        cursor: 'pointer',
                        minHeight: '44px',
                      }}
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleCompleteSession}
                      disabled={loading}
                      style={{
                        flex: 2,
                        padding: '12px',
                        borderRadius: '10px',
                        border: 'none',
                        backgroundColor: 'var(--color-success)',
                        color: '#ffffff',
                        fontSize: '13.5px',
                        fontWeight: 700,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '6px',
                        minHeight: '44px',
                        boxShadow: '0 4px 12px rgba(5, 150, 105, 0.3)',
                      }}
                    >
                      <ShieldCheck size={16} />
                      <span>{loading ? 'Saving…' : 'Save to Patient Wiki'}</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Success Card */}
              {completedResult && (
                <div
                  style={{
                    backgroundColor: 'var(--color-success-soft)',
                    borderRadius: '16px',
                    border: '1px solid var(--color-success-border)',
                    padding: '18px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px',
                    boxShadow: '0 4px 14px rgba(5, 150, 105, 0.15)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={20} style={{ color: 'var(--color-success)' }} />
                    <span style={{ fontSize: '14px', fontWeight: 800, color: 'var(--color-success-dark)' }}>
                      Saved &amp; Synchronized!
                    </span>
                  </div>
                  <div style={{ fontSize: '12.5px', color: 'var(--color-success-dark)', lineHeight: 1.5 }}>
                    Evidence Code: <b style={{ fontFamily: 'monospace' }}>{completedResult.evidenceCode}</b>
                    <br />
                    Category: <b>{completedResult.category}</b>
                  </div>
                  {completedResult.wikiUpdated && (
                    <div style={{ fontSize: '11.5px', color: 'var(--color-success-dark)', display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <BookOpen size={13} />
                      <span>Updated Patient Wiki: <b>Caregiver/{completedResult.category}.md</b></span>
                    </div>
                  )}
                  <button
                    onClick={handleReset}
                    style={{
                      padding: '10px 16px',
                      borderRadius: '10px',
                      border: 'none',
                      backgroundColor: 'var(--color-success)',
                      color: '#ffffff',
                      fontSize: '13px',
                      fontWeight: 700,
                      cursor: 'pointer',
                      marginTop: '4px',
                      minHeight: '44px',
                    }}
                  >
                    + Record Another Log
                  </button>
                </div>
              )}
            </>
          )}

          {/* TAB 2: HISTORICAL LOGS */}
          {activeTab === 'history' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 4px' }}>
                <span style={{ fontSize: '13.5px', fontWeight: 800, color: 'var(--color-text-main)' }}>
                  Recent Observations
                </span>
                <span style={{ fontSize: '11px', color: 'var(--color-text-muted)', backgroundColor: 'var(--color-surface-alt)', padding: '2px 8px', borderRadius: '10px', border: '1px solid var(--color-border)' }}>
                  {data.caregiver_observations.length} total entries
                </span>
              </div>

              {data.caregiver_observations.length === 0 ? (
                <div style={{ padding: '30px 16px', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: '13px' }}>
                  No recorded home observations yet for this patient.
                </div>
              ) : (
                data.caregiver_observations.map((obs) => (
                  <div
                    key={obs.id}
                    style={{
                      padding: '14px 16px',
                      borderRadius: '12px',
                      backgroundColor: 'var(--color-surface)',
                      border: '1px solid var(--color-border)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px',
                      boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span
                        style={{
                          fontSize: '10.5px',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          padding: '2px 8px',
                          borderRadius: '6px',
                          backgroundColor: 'var(--color-accent-soft)',
                          color: 'var(--color-accent-dark)',
                        }}
                      >
                        {obs.category}
                      </span>
                      <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                        {obs.observed_at ? obs.observed_at.slice(0, 10) : 'Today'}
                      </span>
                    </div>
                    <div style={{ fontSize: '13.5px', color: 'var(--color-text-main)', fontStyle: 'italic', lineHeight: 1.4 }}>
                      "{obs.observation_text}"
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '11px', color: 'var(--color-text-muted)', paddingTop: '4px', borderTop: '1px solid var(--color-border-subtle)' }}>
                      <span>Observer: <b>{obs.caregiver_id}</b></span>
                      <span style={{ fontFamily: 'monospace', fontWeight: 600 }}>{obs.evidence_code}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </main>

        {/* 3. Bottom Mobile App Tab Bar */}
        <nav
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: '62px',
            backgroundColor: 'var(--color-surface)',
            borderTop: '1px solid var(--color-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-around',
            zIndex: 40,
            paddingBottom: 'env(safe-area-inset-bottom, 4px)',
          }}
        >
          <button
            onClick={() => setActiveTab('log')}
            style={{
              background: 'none',
              border: 'none',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '3px',
              color: activeTab === 'log' ? 'var(--color-success)' : 'var(--color-text-muted)',
              cursor: 'pointer',
              padding: '8px 16px',
              minWidth: '70px',
              minHeight: '44px',
            }}
          >
            <FileText size={19} />
            <span style={{ fontSize: '11px', fontWeight: activeTab === 'log' ? 800 : 500 }}>Log Note</span>
          </button>

          <button
            onClick={() => setActiveTab('history')}
            style={{
              background: 'none',
              border: 'none',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '3px',
              color: activeTab === 'history' ? 'var(--color-success)' : 'var(--color-text-muted)',
              cursor: 'pointer',
              padding: '8px 16px',
              minWidth: '70px',
              minHeight: '44px',
            }}
          >
            <Clock size={19} />
            <span style={{ fontSize: '11px', fontWeight: activeTab === 'history' ? 800 : 500 }}>Past Logs</span>
          </button>

          <button
            onClick={() => setActiveTab('pairing')}
            style={{
              background: 'none',
              border: 'none',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '3px',
              color: activeTab === 'pairing' ? 'var(--color-success)' : 'var(--color-text-muted)',
              cursor: 'pointer',
              padding: '8px 16px',
              minWidth: '70px',
              minHeight: '44px',
              position: 'relative',
            }}
          >
            <HeartHandshake size={19} />
            <span style={{ fontSize: '11px', fontWeight: activeTab === 'pairing' ? 800 : 500 }}>Pairing</span>
          </button>
        </nav>
      </div>
    </div>
  );
};

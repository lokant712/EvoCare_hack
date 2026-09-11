import React, { useState, useRef, useEffect } from 'react';
import {
  ArrowUp,
  Sparkles,
  Bot,
  AlertTriangle,
  Copy,
  Check,
  RotateCcw,
  ChevronDown
} from 'lucide-react';
import { DashboardResponse, ClinicalReasoningResponse } from '../../types';
import { apiService } from '../../services/api';
import { AuthUser } from '../../services/auth';
import { ChatMessage, ChatSession } from '../../services/chatStorage';

interface ClinicalAssistantTabProps {
  data: DashboardResponse;
  user: AuthUser;
  onSelectEvidence: (code: string) => void;
  onSwitchToPatientRecords: () => void;
  activeSession?: ChatSession;
  onUpdateSessionMessages?: (sessionId: string, messages: ChatMessage[]) => void;
}

const ANIMATED_SUGGESTED_QUESTIONS = [
  'Why is she dizzy in the mornings after taking Telmisartan?',
  'Evaluate 30-day fall risk and near-bathroom stumble trajectory',
  'Summarize recent mobility changes between clinic and home',
  'Review Metformin 500mg adherence against latest renal function labs',
  'Check cross-domain conflicts between caregiver logs and prescriptions',
  'What did caregiver Priya Raman document regarding nocturnal sleep awakenings?',
  'Analyze knee osteoarthritis stiffness progression upon morning rising',
  'Is her current blood pressure regimen well-tolerated at home?',
];

export const ClinicalAssistantTab: React.FC<ClinicalAssistantTabProps> = ({
  data,
  user,
  onSelectEvidence,
  onSwitchToPatientRecords: _onSwitchToPatientRecords,
  activeSession,
  onUpdateSessionMessages,
}) => {
  const [internalMessages, setInternalMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedMsgId, setCopiedMsgId] = useState<string | null>(null);
  const [expandedReasoning, setExpandedReasoning] = useState<Record<string, boolean>>({});

  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const currentMessages = activeSession ? activeSession.messages : internalMessages;

  const scrollToBottom = () => {
    if (typeof chatEndRef.current?.scrollIntoView === 'function') {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentMessages, loading]);

  // Extract clean Doctor display name
  const getDoctorDisplayName = () => {
    if (user.full_name) {
      const cleaned = user.full_name.split('(')[0].trim();
      return cleaned.startsWith('Dr.') ? cleaned : `Dr. ${cleaned}`;
    }
    return 'Dr. Chandran';
  };


  const handleSend = async (queryText?: string) => {
    const textToSend = (queryText || inputValue).trim();
    if (!textToSend || loading) return;

    const userMsgId = 'user-' + Date.now();
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const newMessages: ChatMessage[] = [
      ...currentMessages,
      {
        id: userMsgId,
        sender: 'user',
        timestamp: timeStr,
        text: textToSend,
      },
    ];

    if (activeSession && onUpdateSessionMessages) {
      onUpdateSessionMessages(activeSession.id, newMessages);
    } else {
      setInternalMessages(newMessages);
    }

    setInputValue('');
    setLoading(true);

    try {
      const response: ClinicalReasoningResponse = await apiService.getClinicalReasoning(
        data.patient.patient_code,
        textToSend
      );

      const assistantMsgId = 'assistant-' + Date.now();
      const updatedWithAssistant: ChatMessage[] = [
        ...newMessages,
        {
          id: assistantMsgId,
          sender: 'assistant',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          reasoningData: response,
        },
      ];

      if (activeSession && onUpdateSessionMessages) {
        onUpdateSessionMessages(activeSession.id, updatedWithAssistant);
      } else {
        setInternalMessages(updatedWithAssistant);
      }
    } catch (err: any) {
      const updatedWithError: ChatMessage[] = [
        ...newMessages,
        {
          id: 'error-' + Date.now(),
          sender: 'assistant',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          error: err?.message || 'Unable to complete clinical reasoning inquiry. Please try again.',
        },
      ];

      if (activeSession && onUpdateSessionMessages) {
        onUpdateSessionMessages(activeSession.id, updatedWithError);
      } else {
        setInternalMessages(updatedWithError);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(id);
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

  const toggleReasoningAccordion = (id: string) => {
    setExpandedReasoning((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  // Helper to render text with clickable provenance chips
  const renderTextWithEvidence = (text: string) => {
    const parts = text.split(/(\[EV-[A-Z0-9-]+\]|\[Why\?\])/g);
    return parts.map((part, index) => {
      const evMatch = part.match(/^\[(EV-[A-Z0-9-]+)\]$/);
      if (evMatch) {
        const code = evMatch[1];
        return (
          <button
            key={index}
            onClick={() => onSelectEvidence(code)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '3px',
              padding: '1px 6px',
              borderRadius: '4px',
              backgroundColor: 'var(--color-accent-soft)',
              color: 'var(--color-accent-bright)',
              border: '1px solid var(--color-accent-border)',
              fontSize: '11px',
              fontWeight: 600,
              fontFamily: 'var(--font-mono)',
              cursor: 'pointer',
              margin: '0 2px',
              verticalAlign: 'baseline',
            }}
            title={`Inspect provenance evidence record ${code}`}
          >
            <span>{code}</span>
          </button>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  const isEmptyConversation = currentMessages.length === 0;

  return (
    <div
      style={{
        backgroundColor: 'var(--color-bg)',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        width: '100%',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Centered Scrollable Conversation Canvas */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: isEmptyConversation ? '0 16px' : '24px 16px 140px',
        }}
      >
        {/* ================= EMPTY STATE (ChatGPT Hero View) ================= */}
        {isEmptyConversation ? (
          <div
            style={{
              maxWidth: '780px',
              width: '100%',
              margin: 'auto 0',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              gap: '24px',
              padding: '40px 0',
            }}
          >
            {/* Animated Greeting Title (ChatGPT Style) */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: '14px',
                  backgroundColor: 'var(--color-surface)',
                  border: '1px solid var(--color-border)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-accent)',
                  boxShadow: 'var(--shadow-sm)',
                  marginBottom: '8px',
                }}
              >
                <Bot size={26} />
              </div>

              <h2
                className="animate-greeting-shimmer"
                style={{
                  fontSize: '28px',
                  fontWeight: 800,
                  letterSpacing: '-0.03em',
                  lineHeight: 1.2,
                }}
              >
                Good to see you, {getDoctorDisplayName()}.
              </h2>

              <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', maxWidth: '520px' }}>
                Consultative reasoning grounded in{' '}
                <strong style={{ color: 'var(--color-text-main)' }}>{data.patient.name}</strong>'s 6 longitudinal
                health domains, 47 caregiver observations, and clinic records.
              </p>
            </div>

            {/* Floating Centered Input Bar */}
            <div style={{ width: '100%', maxWidth: '680px' }}>
              <div
                className="chatgpt-pill-shadow"
                style={{
                  width: '100%',
                  borderRadius: '24px',
                  backgroundColor: 'var(--color-surface)',
                  padding: '10px 14px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                  transition: 'all 0.2s ease',
                }}
              >
                <textarea
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={`Ask anything about ${data.patient.name}'s records, medications, conflicts...`}
                  rows={2}
                  style={{
                    width: '100%',
                    backgroundColor: 'transparent',
                    border: 'none',
                    outline: 'none',
                    resize: 'none',
                    fontSize: '14px',
                    color: 'var(--color-text-main)',
                    lineHeight: 1.5,
                    fontFamily: 'var(--font-sans)',
                  }}
                />

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span
                      style={{
                        fontSize: '11px',
                        color: 'var(--color-text-faint)',
                        fontFamily: 'var(--font-mono)',
                      }}
                    >
                      Patient: {data.patient.patient_code}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>

                    {/* Send Button */}
                    <button
                      onClick={() => handleSend()}
                      disabled={!inputValue.trim() || loading}
                      style={{
                        width: '34px',
                        height: '34px',
                        borderRadius: '50%',
                        backgroundColor: inputValue.trim() ? 'var(--color-accent)' : 'var(--color-surface-alt)',
                        border: 'none',
                        color: inputValue.trim() ? '#ffffff' : 'var(--color-text-faint)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: inputValue.trim() ? 'pointer' : 'not-allowed',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      <ArrowUp size={18} />
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Straight-Line Animated Suggested Questions (Marquee Bouncing Carousel) */}
            <div style={{ width: '100%', overflow: 'hidden', position: 'relative', marginTop: '12px' }}>
              <div
                style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                  color: 'var(--color-text-faint)',
                  marginBottom: '10px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                }}
              >
                <Sparkles size={12} style={{ color: 'var(--color-accent)' }} />
                <span>Suggested Clinical Inquiries (Straight-Line Flow)</span>
              </div>

              {/* Animated Carousel Track */}
              <div className="animate-marquee-straight" style={{ gap: '10px', padding: '4px 0' }}>
                {ANIMATED_SUGGESTED_QUESTIONS.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(q)}
                    style={{
                      padding: '8px 14px',
                      borderRadius: '12px',
                      backgroundColor: 'var(--color-surface)',
                      border: '1px solid var(--color-border)',
                      color: 'var(--color-text-secondary)',
                      fontSize: '12px',
                      fontWeight: 500,
                      cursor: 'pointer',
                      whiteSpace: 'nowrap',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      boxShadow: 'var(--shadow-sm)',
                      transition: 'all 0.15s ease',
                      flexShrink: 0,
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'var(--color-surface-raised)';
                      e.currentTarget.style.borderColor = 'var(--color-accent)';
                      e.currentTarget.style.color = 'var(--color-text-main)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'var(--color-surface)';
                      e.currentTarget.style.borderColor = 'var(--color-border)';
                      e.currentTarget.style.color = 'var(--color-text-secondary)';
                    }}
                  >
                    <span style={{ color: 'var(--color-accent)' }}>•</span>
                    <span>{q}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* ================= ACTIVE CHAT THREAD (ChatGPT Stream View) ================= */
          <div
            style={{
              maxWidth: '820px',
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              gap: '24px',
            }}
          >
            {currentMessages.map((msg) => {
              if (msg.sender === 'user') {
                return (
                  <div
                    key={msg.id}
                    style={{
                      display: 'flex',
                      justifyContent: 'flex-end',
                      width: '100%',
                    }}
                  >
                    <div
                      style={{
                        maxWidth: '75%',
                        padding: '12px 18px',
                        borderRadius: '20px 20px 4px 20px',
                        backgroundColor: 'var(--color-surface-raised)',
                        border: '1px solid var(--color-border)',
                        color: 'var(--color-text-main)',
                        fontSize: '14px',
                        lineHeight: 1.5,
                        boxShadow: 'var(--shadow-sm)',
                      }}
                    >
                      {msg.text}
                    </div>
                  </div>
                );
              }

              // Assistant message card
              const rd = msg.reasoningData;
              const primaryConsideration = rd?.considerations && rd.considerations.length > 0 ? rd.considerations[0] : null;
              const textContent = msg.text || primaryConsideration?.description || '';

              return (
                <div
                  key={msg.id}
                  style={{
                    display: 'flex',
                    gap: '14px',
                    width: '100%',
                    alignItems: 'flex-start',
                  }}
                >
                  <div
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '8px',
                      backgroundColor: 'var(--color-accent)',
                      color: '#ffffff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                      marginTop: '2px',
                    }}
                  >
                    <Bot size={18} />
                  </div>

                  <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {/* Error display if any */}
                    {msg.error && (
                      <div
                        style={{
                          padding: '12px 16px',
                          borderRadius: '12px',
                          backgroundColor: 'var(--color-danger-soft)',
                          border: '1px solid var(--color-danger-border)',
                          color: 'var(--color-danger)',
                          fontSize: '13px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                        }}
                      >
                        <AlertTriangle size={16} />
                        <span>{msg.error}</span>
                      </div>
                    )}

                    {/* Standard Text or Initial Summary */}
                    {textContent && (
                      <div
                        style={{
                          fontSize: '14px',
                          color: 'var(--color-text-main)',
                          lineHeight: 1.6,
                          whiteSpace: 'pre-line',
                        }}
                      >
                        {renderTextWithEvidence(textContent)}
                      </div>
                    )}

                    {/* Structured Clinical Reasoning Card (from LLM) */}
                    {rd && (
                      <div
                        style={{
                          backgroundColor: 'var(--color-surface)',
                          border: '1px solid var(--color-border)',
                          borderRadius: '16px',
                          padding: '16px 20px',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '14px',
                          boxShadow: 'var(--shadow-sm)',
                        }}
                      >
                        {/* Primary Finding or Guardrail Banner */}
                        {primaryConsideration?.title && (
                          <div
                            style={{
                              padding: '12px 14px',
                              borderRadius: '10px',
                              backgroundColor: primaryConsideration.category?.includes('Guardrail')
                                ? 'var(--color-warning-soft)'
                                : 'var(--color-surface-alt)',
                              borderLeft: `4px solid ${
                                primaryConsideration.category?.includes('Guardrail')
                                  ? 'var(--color-warning)'
                                  : 'var(--color-accent)'
                              }`,
                              fontSize: '14px',
                              fontWeight: 600,
                              color: 'var(--color-text-main)',
                              lineHeight: 1.5,
                            }}
                          >
                            <span
                              style={{
                                color: primaryConsideration.category?.includes('Guardrail')
                                  ? 'var(--color-warning-dark)'
                                  : 'var(--color-accent)',
                                fontWeight: 700,
                                display: 'block',
                                fontSize: '11px',
                                textTransform: 'uppercase',
                                marginBottom: '2px',
                              }}
                            >
                              {primaryConsideration.category?.includes('Guardrail')
                                ? '🛡️ Clinical Scope & Guardrail Active'
                                : `Primary Consideration • ${primaryConsideration.category}`}
                            </span>
                            {renderTextWithEvidence(primaryConsideration.description || primaryConsideration.title)}
                          </div>
                        )}

                        {/* Longitudinal Evidence Points */}
                        {primaryConsideration?.supporting_evidence && primaryConsideration.supporting_evidence.length > 0 && (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            <div
                              style={{
                                fontSize: '11px',
                                fontWeight: 700,
                                textTransform: 'uppercase',
                                letterSpacing: '0.05em',
                                color: 'var(--color-text-muted)',
                              }}
                            >
                              Longitudinal Supporting Evidence:
                            </div>
                            <ul style={{ margin: 0, paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                              {primaryConsideration.supporting_evidence.map((ev, i) => (
                                <li
                                  key={i}
                                  style={{
                                    fontSize: '13px',
                                    color: 'var(--color-text-secondary)',
                                    lineHeight: 1.5,
                                  }}
                                >
                                  {renderTextWithEvidence(`[${ev.evidence_id}] ${ev.original_statement}`)}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Collapsible Deep Reasoning Accordion */}
                        <div
                          style={{
                            borderTop: '1px solid var(--color-border)',
                            paddingTop: '10px',
                          }}
                        >
                          <button
                            onClick={() => toggleReasoningAccordion(msg.id)}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: 'var(--color-accent)',
                              fontSize: '12px',
                              fontWeight: 600,
                              display: 'flex',
                              alignItems: 'center',
                              gap: '6px',
                              cursor: 'pointer',
                              padding: 0,
                            }}
                          >
                            <Sparkles size={14} />
                            <span>
                              {expandedReasoning[msg.id]
                                ? 'Hide Deep Clinical Reasoning Traces'
                                : 'Show Deep Clinical Reasoning & Evidence Strength'}
                            </span>
                            <ChevronDown
                              size={14}
                              style={{
                                transform: expandedReasoning[msg.id] ? 'rotate(180deg)' : 'rotate(0deg)',
                                transition: 'transform 0.2s ease',
                              }}
                            />
                          </button>

                          {expandedReasoning[msg.id] && (
                            <div
                              style={{
                                marginTop: '10px',
                                padding: '12px 14px',
                                borderRadius: '10px',
                                backgroundColor: 'var(--color-surface-alt)',
                                fontSize: '12px',
                                color: 'var(--color-text-muted)',
                                lineHeight: 1.5,
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '8px',
                              }}
                            >
                              <div>
                                <strong style={{ color: 'var(--color-text-main)' }}>Clinical Rationale:</strong>{' '}
                                {primaryConsideration?.reasoning || 'Evaluated against patient health memory baseline.'}
                              </div>
                              {primaryConsideration?.evidence_strength && (
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                  <strong style={{ color: 'var(--color-text-main)' }}>Evidence Strength:</strong>
                                  <span
                                    style={{
                                      fontFamily: 'var(--font-mono)',
                                      color: 'var(--color-accent)',
                                      fontWeight: 700,
                                    }}
                                  >
                                    {primaryConsideration.evidence_strength}
                                  </span>
                                </div>
                              )}
                            </div>
                          )}
                        </div>

                        {/* Action Bar */}
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            paddingTop: '6px',
                          }}
                        >
                          <div style={{ display: 'flex', gap: '6px' }}>
                            <button
                              onClick={() => handleCopy(msg.id, primaryConsideration?.description || textContent)}
                              style={{
                                padding: '4px 8px',
                                borderRadius: '6px',
                                backgroundColor: 'var(--color-surface-alt)',
                                border: '1px solid var(--color-border)',
                                color: 'var(--color-text-muted)',
                                fontSize: '11px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px',
                                cursor: 'pointer',
                              }}
                            >
                              {copiedMsgId === msg.id ? <Check size={12} style={{ color: 'var(--color-success)' }} /> : <Copy size={12} />}
                              <span>{copiedMsgId === msg.id ? 'Copied' : 'Copy'}</span>
                            </button>
                          </div>

                          <span
                            style={{
                              fontSize: '10px',
                              color: 'var(--color-text-faint)',
                              fontFamily: 'var(--font-mono)',
                            }}
                          >
                            {msg.timestamp}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Loading Indicator with Animated Glowing & Brightening Shimmer Effect */}
            {loading && (
              <div style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '8px',
                    backgroundColor: 'var(--color-accent)',
                    color: '#ffffff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  <Bot size={18} />
                </div>
                <div
                  className="animate-glow-box"
                  style={{
                    padding: '14px 20px',
                    borderRadius: '16px',
                    backgroundColor: 'var(--color-surface)',
                    border: '1px solid var(--color-accent)',
                    fontSize: '13px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    boxShadow: '0 0 20px rgba(47, 166, 150, 0.25)',
                  }}
                >
                  <RotateCcw size={16} className="animate-spin" style={{ color: 'var(--color-accent)' }} />
                  <span className="animate-text-lighting">
                    Synthesizing longitudinal health memory across 6 domains, caregiver logs & clinic records...
                  </span>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>
        )}
      </div>

      {/* ================= FLOATING BOTTOM INPUT BAR (When Conversation is Active) ================= */}
      {!isEmptyConversation && (
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            padding: '16px 24px 20px',
            background: 'linear-gradient(180deg, rgba(0,0,0,0) 0%, var(--color-bg) 35%)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <div
            className="chatgpt-pill-shadow"
            style={{
              width: '100%',
              maxWidth: '820px',
              borderRadius: '24px',
              backgroundColor: 'var(--color-surface)',
              padding: '8px 14px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
            }}
          >
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask follow-up question for ${data.patient.name}...`}
              rows={1}
              style={{
                flex: 1,
                backgroundColor: 'transparent',
                border: 'none',
                outline: 'none',
                resize: 'none',
                fontSize: '14px',
                color: 'var(--color-text-main)',
                lineHeight: 1.4,
                fontFamily: 'var(--font-sans)',
                paddingTop: '6px',
              }}
            />


            <button
              onClick={() => handleSend()}
              disabled={!inputValue.trim() || loading}
              style={{
                width: '34px',
                height: '34px',
                borderRadius: '50%',
                backgroundColor: inputValue.trim() ? 'var(--color-accent)' : 'var(--color-surface-alt)',
                border: 'none',
                color: inputValue.trim() ? '#ffffff' : 'var(--color-text-faint)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: inputValue.trim() ? 'pointer' : 'not-allowed',
              }}
            >
              <ArrowUp size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

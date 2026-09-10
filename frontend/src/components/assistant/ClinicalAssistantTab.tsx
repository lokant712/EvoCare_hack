import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  Bot,
  AlertTriangle,
  ChevronRight,
  Pill,
  HeartPulse
} from 'lucide-react';
import { DashboardResponse, ClinicalReasoningResponse } from '../../types';
import { apiService } from '../../services/api';
import { AuthUser } from '../../services/auth';

interface ClinicalAssistantTabProps {
  data: DashboardResponse;
  user: AuthUser;
  onSelectEvidence: (code: string) => void;
  onSwitchToPatientRecords: () => void;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  timestamp: string;
  text?: string;
  isInitialSummary?: boolean;
  reasoningData?: ClinicalReasoningResponse;
  error?: string;
}

const EXAMPLE_PROMPTS = [
  'Why is she dizzy in the mornings?',
  'Evaluate fall risk and mobility trajectory',
  'Summarize recent mobility changes between clinic and home',
  'Review current medications and adherence observations'
];

export const ClinicalAssistantTab: React.FC<ClinicalAssistantTabProps> = ({
  data,
  user,
  onSelectEvidence,
  onSwitchToPatientRecords,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-msg',
      sender: 'assistant',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isInitialSummary: true,
      text: `Hello ${user.full_name.split('(')[0].trim()}. I am your EvoCare Clinical Reasoning Assistant. I have loaded ${data.patient.name}'s longitudinal health memory across 9 domains, 47 caregiver observations, and clinic records.`
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (typeof chatEndRef.current?.scrollIntoView === 'function') {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (queryText?: string) => {
    const textToSend = (queryText || inputValue).trim();
    if (!textToSend || loading) return;

    const userMsgId = 'user-' + Date.now();
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    setMessages((prev) => [
      ...prev,
      {
        id: userMsgId,
        sender: 'user',
        timestamp: timeStr,
        text: textToSend,
      },
    ]);
    setInputValue('');
    setLoading(true);

    try {
      const response = await apiService.getClinicalReasoning(data.patient.patient_code, textToSend);
      const assistantMsgId = 'assistant-' + Date.now();
      setMessages((prev) => [
        ...prev,
        {
          id: assistantMsgId,
          sender: 'assistant',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          reasoningData: response,
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: 'error-' + Date.now(),
          sender: 'assistant',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          error: err?.message || 'Unable to complete clinical reasoning inquiry. Please try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      style={{
        backgroundColor: 'var(--color-bg)',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        width: '100%',
        overflow: 'hidden',
      }}
    >
      {/* Sleek Sub-Header */}
      <div
        style={{
          padding: '10px 24px',
          borderBottom: '1px solid var(--color-border)',
          backgroundColor: 'var(--color-surface)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        <div
          style={{
            maxWidth: '900px',
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                backgroundColor: 'var(--color-accent)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
              }}
            >
              <Bot size={18} />
            </div>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--color-text-main)' }}>
                EvoCare Clinical AI Assistant
              </div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                Consultative intelligence grounded in {data.patient.name}'s longitudinal records
              </div>
            </div>
          </div>

          <div
            style={{
              fontSize: '11px',
              fontWeight: 600,
              color: 'var(--color-accent-dark)',
              backgroundColor: 'var(--color-accent-soft)',
              padding: '4px 10px',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Sparkles size={13} />
            <span>Consultative Reasoning</span>
          </div>
        </div>
      </div>

      {/* Message Thread Area - Full-Screen Centered Column (ChatGPT / Claude / Gemini style) */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '24px 20px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          backgroundColor: 'var(--color-surface)',
        }}
      >
        <div
          style={{
            maxWidth: '900px',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            gap: '24px',
          }}
        >
          {messages.map((msg) =>
            msg.sender === 'user' ? (
              /* User Message - Clean Right-Aligned Pill */
              <div
                key={msg.id}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-end',
                  width: '100%',
                }}
              >
                <div
                  style={{
                    maxWidth: '75%',
                    backgroundColor: 'var(--color-accent)',
                    color: '#ffffff',
                    padding: '12px 18px',
                    borderRadius: '20px 20px 4px 20px',
                    boxShadow: '0 2px 4px rgba(13, 110, 100, 0.15)',
                    fontSize: '14px',
                    lineHeight: 1.5,
                    wordBreak: 'break-word',
                  }}
                >
                  {msg.text}
                </div>
                <div style={{ fontSize: '10px', color: 'var(--color-text-faint)', marginTop: '4px', paddingRight: '4px' }}>
                  {msg.timestamp}
                </div>
              </div>
            ) : (
              /* Assistant Message - Full Modern Card */
              <div
                key={msg.id}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  width: '100%',
                  gap: '6px',
                }}
              >
                <div style={{ display: 'flex', gap: '14px', width: '100%', alignItems: 'flex-start' }}>
                  {/* Avatar */}
                  <div
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      backgroundColor: 'var(--color-accent)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#ffffff',
                      flexShrink: 0,
                      marginTop: '2px',
                    }}
                  >
                    <Bot size={17} />
                  </div>

                  {/* Message Content */}
                  <div
                    style={{
                      flex: 1,
                      backgroundColor: 'var(--color-bg)',
                      borderRadius: '16px',
                      border: '1px solid var(--color-border)',
                      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.03)',
                      padding: '18px 22px',
                      fontSize: '14px',
                      lineHeight: 1.5,
                      color: 'var(--color-text-main)',
                    }}
                  >
                    {/* Initial Summary Card or Normal Text */}
                    {msg.isInitialSummary ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                        <div style={{ fontSize: '14px', lineHeight: 1.5, color: 'var(--color-text-main)' }}>
                          {msg.text}
                        </div>

                        {/* Embedded Baseline Summary Card */}
                        <div
                          style={{
                            backgroundColor: 'var(--color-surface)',
                            border: '1px solid var(--color-border)',
                            borderRadius: '12px',
                            padding: '16px',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '12px',
                          }}
                        >
                          <div
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              flexWrap: 'wrap',
                              gap: '8px',
                              borderBottom: '1px solid var(--color-surface-alt)',
                              paddingBottom: '10px',
                            }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <HeartPulse size={18} style={{ color: 'var(--color-accent)' }} />
                              <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-accent-dark)' }}>
                                Essential Patient Summary &amp; Longitudinal Baseline
                              </span>
                            </div>
                            <button
                              onClick={onSwitchToPatientRecords}
                              style={{
                                backgroundColor: 'var(--color-surface)',
                                border: '1px solid var(--color-border-strong)',
                                color: 'var(--color-accent)',
                                padding: '4px 10px',
                                borderRadius: '6px',
                                fontSize: '11px',
                                fontWeight: 700,
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px',
                                boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                              }}
                            >
                              <span>View Full Patient Records Tab</span>
                              <ChevronRight size={13} />
                            </button>
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                            {/* Confirmed Chronic Conditions */}
                            <div style={{ backgroundColor: 'var(--color-bg)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                                Confirmed Chronic Conditions
                              </div>
                              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                                <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-main)', backgroundColor: 'var(--color-border)', padding: '2px 6px', borderRadius: '4px' }}>
                                  Type 2 Diabetes (E11.9)
                                </span>
                                <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-main)', backgroundColor: 'var(--color-border)', padding: '2px 6px', borderRadius: '4px' }}>
                                  Hypertension (I10)
                                </span>
                                <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-main)', backgroundColor: 'var(--color-border)', padding: '2px 6px', borderRadius: '4px' }}>
                                  Bilateral Knee Osteoarthritis
                                </span>
                              </div>
                            </div>

                            {/* Recent Trajectory Alerts */}
                            <div style={{ backgroundColor: 'var(--color-warning-soft)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--color-warning-border)' }}>
                              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-warning-dark)', textTransform: 'uppercase', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <AlertTriangle size={12} />
                                Recent Trajectory Warnings
                              </div>
                              <div style={{ fontSize: '11px', color: 'var(--color-warning-dark)', lineHeight: 1.4 }}>
                                • <strong>Mobility:</strong> Intermittent outdoor arm support needed<br />
                                • <strong>Dizziness:</strong> Positional morning lightheadedness<br />
                                • <strong>Falls:</strong> Near-fall on Sep 06 (Zero ground impact)
                              </div>
                            </div>

                            {/* Active Regimen */}
                            <div style={{ backgroundColor: 'var(--color-bg)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <Pill size={12} />
                                Active Regimen ({data.medications.length})
                              </div>
                              <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                                {data.medications.slice(0, 3).map((m, i) => (
                                  <span key={i} style={{ backgroundColor: 'var(--color-success-soft)', color: 'var(--color-success-dark)', padding: '2px 6px', borderRadius: '4px', border: '1px solid var(--color-success-border)', fontSize: '10px', fontWeight: 600 }}>
                                    {m.name} {m.dose} ({m.frequency})
                                  </span>
                                ))}
                                {data.medications.length > 3 && (
                                  <span style={{ fontSize: '10px', color: 'var(--color-text-muted)', alignSelf: 'center' }}>
                                    +{data.medications.length - 3} more
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>

                          <div style={{ fontSize: '12px', color: 'var(--color-accent-dark)', fontWeight: 600, paddingTop: '4px' }}>
                            💬 What clinical considerations, trajectory questions, or drug safety interactions would you like to explore?
                          </div>
                        </div>
                      </div>
                    ) : (
                      <>
                        {msg.text && <div style={{ fontSize: '14px', lineHeight: 1.5 }}>{msg.text}</div>}
                      </>
                    )}

                    {/* Error state */}
                    {msg.error && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-danger-dark)' }}>
                        <AlertTriangle size={16} />
                        <span>{msg.error}</span>
                      </div>
                    )}

                    {/* Structured Clinical Reasoning Response */}
                    {msg.reasoningData && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {/* Consideration Cards */}
                        <div>
                          <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.04em' }}>
                            Differential Considerations for Clinician Evaluation
                          </div>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                            {msg.reasoningData.considerations.map((c, i) => (
                              <div
                                key={i}
                                style={{
                                  backgroundColor: 'var(--color-surface)',
                                  border: '1px solid var(--color-border-strong)',
                                  borderRadius: '10px',
                                  padding: '14px 16px',
                                }}
                              >
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                                  <span style={{ fontWeight: 700, color: 'var(--color-text-main)', fontSize: '14px' }}>
                                    {c.title}
                                  </span>
                                  <span
                                    style={{
                                      fontSize: '10px',
                                      fontWeight: 700,
                                      backgroundColor: 'var(--color-warning-soft)',
                                      color: 'var(--color-warning-dark)',
                                      padding: '2px 8px',
                                      borderRadius: '4px',
                                    }}
                                  >
                                    {c.status.replace(/_/g, ' ')}
                                  </span>
                                </div>
                                <p style={{ margin: '0 0 10px 0', fontSize: '13px', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                                  {c.description || c.reasoning || 'Evaluated against longitudinal evidence.'}
                                </p>

                                {/* Supporting Evidence Chips */}
                                {c.references && c.references.length > 0 && (
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                                    <span style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontWeight: 600 }}>Evidence:</span>
                                    {c.references.map((refCode) => (
                                      <button
                                        key={refCode}
                                        onClick={() => onSelectEvidence(refCode)}
                                        style={{
                                          fontSize: '11px',
                                          fontFamily: "'IBM Plex Mono', monospace",
                                          fontWeight: 600,
                                          backgroundColor: 'var(--color-accent-soft)',
                                          color: 'var(--color-accent-dark)',
                                          border: '1px solid var(--color-accent-border)',
                                          borderRadius: '4px',
                                          padding: '2px 7px',
                                          cursor: 'pointer',
                                          transition: 'background-color 0.15s',
                                        }}
                                        title="Inspect raw immutable evidence"
                                      >
                                        {refCode}
                                      </button>
                                    ))}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Disclaimer */}
                        <div style={{ fontSize: '11px', color: 'var(--color-text-faint)', fontStyle: 'italic', borderTop: '1px solid var(--color-border)', paddingTop: '8px' }}>
                          ⚠ {msg.reasoningData.disclaimer}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <div style={{ fontSize: '10px', color: 'var(--color-text-faint)', marginLeft: '46px' }}>
                  {msg.timestamp}
                </div>
              </div>
            )
          )}

          {/* Loading Indicator */}
          {loading && (
            <div style={{ display: 'flex', gap: '14px', alignItems: 'center', width: '100%' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-accent)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ffffff',
                  flexShrink: 0,
                }}
              >
                <Bot size={17} />
              </div>
              <div
                style={{
                  backgroundColor: 'var(--color-bg)',
                  border: '1px solid var(--color-border)',
                  padding: '12px 18px',
                  borderRadius: '14px',
                  fontSize: '13px',
                  color: 'var(--color-text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <span
                  style={{
                    width: '12px',
                    height: '12px',
                    border: '2px solid var(--color-accent)',
                    borderTopColor: 'transparent',
                    borderRadius: '50%',
                    animation: 'spin 0.8s linear infinite',
                    display: 'inline-block',
                  }}
                />
                Analyzing longitudinal patient memory and validating clinical reasoning…
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>
      </div>

      {/* Bottom Floating/Docked Input Capsule (ChatGPT / Claude / Gemini style) */}
      <div
        style={{
          borderTop: '1px solid var(--color-border)',
          backgroundColor: 'var(--color-surface)',
          padding: '12px 20px 16px 20px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          flexShrink: 0,
        }}
      >
        <div style={{ maxWidth: '900px', width: '100%', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {/* Suggested Inquiries */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              overflowX: 'auto',
              paddingBottom: '2px',
            }}
          >
            <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-faint)', whiteSpace: 'nowrap' }}>
              Suggestions:
            </span>
            {EXAMPLE_PROMPTS.map((prompt, i) => (
              <button
                key={i}
                onClick={() => handleSend(prompt)}
                disabled={loading}
                style={{
                  backgroundColor: 'var(--color-bg)',
                  border: '1px solid var(--color-border)',
                  color: 'var(--color-text-secondary)',
                  padding: '4px 12px',
                  borderRadius: '16px',
                  fontSize: '12px',
                  whiteSpace: 'nowrap',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  transition: 'all 0.15s',
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'var(--color-accent-soft)';
                  (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--color-accent-border)';
                  (e.currentTarget as HTMLButtonElement).style.color = 'var(--color-accent-dark)';
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'var(--color-bg)';
                  (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--color-border)';
                  (e.currentTarget as HTMLButtonElement).style.color = 'var(--color-text-secondary)';
                }}
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Modern Pill Input Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border-strong)',
              borderRadius: '24px',
              boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
              padding: '4px 8px 4px 18px',
            }}
          >
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about patient trajectory, symptoms, drug interactions, or caregiver observations..."
              disabled={loading}
              style={{
                flex: 1,
                border: 'none',
                outline: 'none',
                fontSize: '14px',
                color: 'var(--color-text-main)',
                padding: '10px 0',
                backgroundColor: 'transparent',
              }}
            />
            <button
              type="submit"
              disabled={loading || !inputValue.trim()}
              style={{
                backgroundColor: loading || !inputValue.trim() ? 'var(--color-border)' : 'var(--color-accent)',
                color: loading || !inputValue.trim() ? 'var(--color-text-faint)' : '#ffffff',
                border: 'none',
                borderRadius: '20px',
                padding: '8px 18px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontWeight: 600,
                fontSize: '13px',
                cursor: loading || !inputValue.trim() ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.15s',
                flexShrink: 0,
              }}
            >
              <Send size={14} />
              <span>Send</span>
            </button>
          </form>

          <div style={{ textAlign: 'center', fontSize: '11px', color: 'var(--color-text-faint)' }}>
            EvoCare AI interprets and constrains evidence • Human clinician remains the definitive decision-maker
          </div>
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

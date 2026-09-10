import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  Bot,
  User as UserIcon,
  AlertTriangle,
  Info,
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
        backgroundColor: '#ffffff',
        borderRadius: '16px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.04)',
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 190px)',
        minHeight: '680px',
        overflow: 'hidden',
      }}
    >
      {/* Chat Header */}
        <div
          style={{
            padding: '14px 20px',
            borderBottom: '1px solid #f1f5f9',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: '#ffffff',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '34px',
                height: '34px',
                borderRadius: '8px',
                backgroundColor: '#0284c7',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
              }}
            >
              <Bot size={20} />
            </div>
            <div>
              <div style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a' }}>
                EvoCare Clinical AI Assistant
              </div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>
                Grounded in immutable patient memory • Doctor-only consultative station
              </div>
            </div>
          </div>

          <div
            style={{
              fontSize: '11px',
              fontWeight: 600,
              color: '#0369a1',
              backgroundColor: '#e0f2fe',
              padding: '4px 10px',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Sparkles size={13} />
            <span>Consultative Reasoning Engine</span>
          </div>
        </div>

        {/* Message Thread Area */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '24px 20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '20px',
            backgroundColor: '#fafafa',
          }}
        >
          {messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                display: 'flex',
                gap: '12px',
                maxWidth: msg.sender === 'user' ? '82%' : '92%',
                alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row',
              }}
            >
              {/* Avatar */}
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: msg.sender === 'user' ? '#0f172a' : '#0284c7',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ffffff',
                  flexShrink: 0,
                  marginTop: '2px',
                }}
              >
                {msg.sender === 'user' ? <UserIcon size={16} /> : <Bot size={16} />}
              </div>

              {/* Message Content Bubble */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div
                  style={{
                    backgroundColor: msg.sender === 'user' ? '#0284c7' : '#ffffff',
                    color: msg.sender === 'user' ? '#ffffff' : '#0f172a',
                    padding: msg.sender === 'user' ? '12px 16px' : '16px 20px',
                    borderRadius: '14px',
                    border: msg.sender === 'user' ? 'none' : '1px solid #e2e8f0',
                    boxShadow: '0 1px 2px rgba(0, 0, 0, 0.04)',
                    fontSize: '14px',
                    lineHeight: 1.5,
                  }}
                >
                  {/* Message Body: Initial Patient Summary or Standard Message */}
                  {msg.isInitialSummary ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                      <div style={{ fontSize: '14px', lineHeight: 1.5, color: '#0f172a' }}>
                        {msg.text}
                      </div>

                      {/* Embedded Essential Patient Summary Card directly in chat */}
                      <div
                        style={{
                          backgroundColor: '#f8fafc',
                          border: '1px solid #e2e8f0',
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
                            borderBottom: '1px solid #e2e8f0',
                            paddingBottom: '10px',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <HeartPulse size={18} style={{ color: '#0284c7' }} />
                            <span style={{ fontSize: '13px', fontWeight: 700, color: '#0369a1' }}>
                              Essential Patient Summary &amp; Longitudinal Baseline
                            </span>
                          </div>
                          <button
                            onClick={onSwitchToPatientRecords}
                            style={{
                              backgroundColor: '#ffffff',
                              border: '1px solid #cbd5e1',
                              color: '#0284c7',
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
                          <div style={{ backgroundColor: '#ffffff', padding: '10px 12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                            <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '6px' }}>
                              Confirmed Chronic Conditions
                            </div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                              <span style={{ fontSize: '11px', fontWeight: 600, color: '#0f172a', backgroundColor: '#f1f5f9', padding: '2px 6px', borderRadius: '4px' }}>
                                Type 2 Diabetes (E11.9)
                              </span>
                              <span style={{ fontSize: '11px', fontWeight: 600, color: '#0f172a', backgroundColor: '#f1f5f9', padding: '2px 6px', borderRadius: '4px' }}>
                                Hypertension (I10)
                              </span>
                              <span style={{ fontSize: '11px', fontWeight: 600, color: '#0f172a', backgroundColor: '#f1f5f9', padding: '2px 6px', borderRadius: '4px' }}>
                                Bilateral Knee Osteoarthritis
                              </span>
                            </div>
                          </div>

                          {/* Recent Trajectory Alerts */}
                          <div style={{ backgroundColor: '#fff7ed', padding: '10px 12px', borderRadius: '8px', border: '1px solid #fed7aa' }}>
                            <div style={{ fontSize: '11px', fontWeight: 700, color: '#c2410c', textTransform: 'uppercase', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                              <AlertTriangle size={12} />
                              Recent Trajectory Warnings
                            </div>
                            <div style={{ fontSize: '11px', color: '#7c2d12', lineHeight: 1.4 }}>
                              • <strong>Mobility:</strong> Intermittent outdoor arm support needed<br />
                              • <strong>Dizziness:</strong> Positional morning lightheadedness<br />
                              • <strong>Falls:</strong> Near-fall on Sep 06 (Zero ground impact)
                            </div>
                          </div>

                          {/* Active Regimen */}
                          <div style={{ backgroundColor: '#ffffff', padding: '10px 12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                            <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                              <Pill size={12} />
                              Active Regimen ({data.medications.length})
                            </div>
                            <div style={{ fontSize: '11px', color: '#334155', display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                              {data.medications.slice(0, 3).map((m, i) => (
                                <span key={i} style={{ backgroundColor: '#f0fdf4', color: '#166534', padding: '2px 6px', borderRadius: '4px', border: '1px solid #bbf7d0', fontSize: '10px', fontWeight: 600 }}>
                                  {m.name} {m.dose} ({m.frequency})
                                </span>
                              ))}
                              {data.medications.length > 3 && (
                                <span style={{ fontSize: '10px', color: '#64748b', alignSelf: 'center' }}>
                                  +{data.medications.length - 3} more
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        <div style={{ fontSize: '12px', color: '#0369a1', fontWeight: 600, paddingTop: '4px' }}>
                          💬 What clinical considerations, trajectory questions, or drug safety interactions would you like to explore?
                        </div>
                      </div>
                    </div>
                  ) : (
                    <>
                      {/* Simple text message */}
                      {msg.text && <div>{msg.text}</div>}
                    </>
                  )}

                  {/* Error state */}
                  {msg.error && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#b91c1c' }}>
                      <AlertTriangle size={16} />
                      <span>{msg.error}</span>
                    </div>
                  )}

                  {/* Structured Clinical Reasoning Response */}
                  {msg.reasoningData && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {/* Context Summary */}
                      {msg.reasoningData.context_summary && (
                        <div
                          style={{
                            backgroundColor: '#f8fafc',
                            padding: '12px 14px',
                            borderRadius: '8px',
                            border: '1px solid #e2e8f0',
                            fontSize: '13px',
                          }}
                        >
                          <div style={{ fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                            Patient Trajectory Context
                          </div>
                          <div style={{ color: '#475569' }}>
                            {msg.reasoningData.context_summary.relevant_observations?.join('; ') || 'Analyzed longitudinal observations, clinical records, and baseline.'}
                          </div>
                        </div>
                      )}

                      {/* Consideration Cards */}
                      <div>
                        <div style={{ fontSize: '12px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '8px' }}>
                          Differential Considerations for Clinician Evaluation
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                          {msg.reasoningData.considerations.map((c, i) => (
                            <div
                              key={i}
                              style={{
                                backgroundColor: '#ffffff',
                                border: '1px solid #cbd5e1',
                                borderRadius: '10px',
                                padding: '12px 14px',
                              }}
                            >
                              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                                <span style={{ fontWeight: 700, color: '#0f172a', fontSize: '14px' }}>
                                  {c.title}
                                </span>
                                <span
                                  style={{
                                    fontSize: '10px',
                                    fontWeight: 700,
                                    backgroundColor: '#fef3c7',
                                    color: '#92400e',
                                    padding: '2px 8px',
                                    borderRadius: '4px',
                                  }}
                                >
                                  {c.status.replace(/_/g, ' ')}
                                </span>
                              </div>
                              <p style={{ margin: '0 0 10px 0', fontSize: '13px', color: '#475569' }}>
                                {c.description || c.reasoning || 'Evaluated against longitudinal evidence.'}
                              </p>

                              {/* Supporting Evidence Chips */}
                              {c.references && c.references.length > 0 && (
                                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                                  <span style={{ fontSize: '11px', color: '#64748b', fontWeight: 600 }}>Evidence:</span>
                                  {c.references.map((refCode) => (
                                    <button
                                      key={refCode}
                                      onClick={() => onSelectEvidence(refCode)}
                                      style={{
                                        fontSize: '11px',
                                        fontFamily: "'IBM Plex Mono', monospace",
                                        fontWeight: 600,
                                        backgroundColor: '#e0f2fe',
                                        color: '#0369a1',
                                        border: '1px solid #bae6fd',
                                        borderRadius: '4px',
                                        padding: '1px 6px',
                                        cursor: 'pointer',
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

                      {/* Missing Information / Caveats */}
                      {msg.reasoningData.missing_information && msg.reasoningData.missing_information.length > 0 && (
                        <div
                          style={{
                            backgroundColor: '#fffbeb',
                            border: '1px solid #fef3c7',
                            borderRadius: '8px',
                            padding: '10px 14px',
                            fontSize: '12px',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 700, color: '#92400e', marginBottom: '4px' }}>
                            <Info size={14} />
                            <span>Missing Clinical Information (Missing != Normal)</span>
                          </div>
                          <ul style={{ margin: 0, paddingLeft: '18px', color: '#78350f' }}>
                            {msg.reasoningData.missing_information.map((item, idx) => (
                              <li key={idx}>{item}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Disclaimer */}
                      <div style={{ fontSize: '11px', color: '#94a3b8', fontStyle: 'italic', borderTop: '1px solid #f1f5f9', paddingTop: '8px' }}>
                        ⚠ {msg.reasoningData.disclaimer}
                      </div>
                    </div>
                  )}
                </div>

                <div
                  style={{
                    fontSize: '10px',
                    color: '#94a3b8',
                    alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                    padding: '0 4px',
                  }}
                >
                  {msg.timestamp}
                </div>
              </div>
            </div>
          ))}

          {/* Loading Indicator */}
          {loading && (
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: '#0284c7',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ffffff',
                }}
              >
                <Bot size={16} />
              </div>
              <div
                style={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e2e8f0',
                  padding: '12px 18px',
                  borderRadius: '14px',
                  fontSize: '13px',
                  color: '#64748b',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <span
                  style={{
                    width: '12px',
                    height: '12px',
                    border: '2px solid #0284c7',
                    borderTopColor: 'transparent',
                    borderRadius: '50%',
                    animation: 'spin 0.8s linear infinite',
                    display: 'inline-block',
                  }}
                />
                Analyzing longitudinal patient memory and validating evidence constraints…
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Example Prompt Chips Bar */}
        <div
          style={{
            padding: '10px 20px',
            backgroundColor: '#ffffff',
            borderTop: '1px solid #f1f5f9',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            overflowX: 'auto',
          }}
        >
          <span style={{ fontSize: '11px', fontWeight: 600, color: '#94a3b8', whiteSpace: 'nowrap' }}>
            Suggested Inquiries:
          </span>
          {EXAMPLE_PROMPTS.map((prompt, i) => (
            <button
              key={i}
              onClick={() => handleSend(prompt)}
              disabled={loading}
              style={{
                backgroundColor: '#f8fafc',
                border: '1px solid #e2e8f0',
                color: '#334155',
                padding: '4px 10px',
                borderRadius: '20px',
                fontSize: '12px',
                whiteSpace: 'nowrap',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.15s',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.backgroundColor = '#e0f2fe';
                (e.currentTarget as HTMLButtonElement).style.borderColor = '#bae6fd';
                (e.currentTarget as HTMLButtonElement).style.color = '#0369a1';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.backgroundColor = '#f8fafc';
                (e.currentTarget as HTMLButtonElement).style.borderColor = '#e2e8f0';
                (e.currentTarget as HTMLButtonElement).style.color = '#334155';
              }}
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div
          style={{
            padding: '14px 20px',
            borderTop: '1px solid #e2e8f0',
            backgroundColor: '#ffffff',
          }}
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            style={{ display: 'flex', gap: '10px', alignItems: 'center' }}
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
                padding: '12px 16px',
                borderRadius: '10px',
                border: '1px solid #cbd5e1',
                fontSize: '14px',
                color: '#0f172a',
                outline: 'none',
                boxSizing: 'border-box',
              }}
              onFocus={(e) => (e.target.style.borderColor = '#0284c7')}
              onBlur={(e) => (e.target.style.borderColor = '#cbd5e1')}
            />
            <button
              type="submit"
              disabled={loading || !inputValue.trim()}
              style={{
                backgroundColor: loading || !inputValue.trim() ? '#cbd5e1' : '#0284c7',
                color: '#ffffff',
                border: 'none',
                borderRadius: '10px',
                padding: '12px 18px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontWeight: 600,
                fontSize: '14px',
                cursor: loading || !inputValue.trim() ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.15s',
              }}
            >
              <Send size={15} />
              <span>Send</span>
            </button>
          </form>
          <div style={{ textAlign: 'center', marginTop: '6px', fontSize: '11px', color: '#94a3b8' }}>
            EvoCare AI interprets and constrains evidence • Human clinician remains the definitive decision-maker
          </div>
        </div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  };

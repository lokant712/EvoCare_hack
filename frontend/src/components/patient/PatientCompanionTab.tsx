import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  Bot,
  User,
  Pill,
  HeartPulse,
  Info,
  ShieldCheck,
  Stethoscope,
  HelpCircle,
  RotateCcw
} from 'lucide-react';
import { DashboardResponse } from '../../types';
import { apiService } from '../../services/api';
import { AuthUser } from '../../services/auth';

interface PatientCompanionTabProps {
  data: DashboardResponse;
  user: AuthUser;
}

interface CompanionMessage {
  id: string;
  sender: 'user' | 'assistant';
  timestamp: string;
  text: string;
  disclaimer?: string;
  isWelcome?: boolean;
}

const PATIENT_PROMPTS = [
  'When should I take my medicines?',
  'What did Dr. Ramesh Varma advise in my last visit?',
  'What advice is recorded for my morning dizziness?',
  'What doctors have I consulted previously?',
  'How have my sleep and walking been lately?'
];

export const PatientCompanionTab: React.FC<PatientCompanionTabProps> = ({ data, user }) => {
  const patientName = user.full_name || data.patient.name || 'Meenakshi Raman';
  const firstName = patientName.split(' ')[0];

  const initialWelcomeMsg: CompanionMessage = {
    id: 'welcome-patient',
    sender: 'assistant',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    isWelcome: true,
    text: `Hello ${firstName}! I am your EvoCare Personal Health Companion. 
I am here to help you easily understand your health records, medications, doctor instructions, and daily logs in simple language.

Ask me anything about your prescriptions, appointments, or recorded advice.`,
    disclaimer: 'This companion is for your personal information and understanding. It does not replace medical advice from Dr. Ramesh Varma.'
  };

  const [messages, setMessages] = useState<CompanionMessage[]>([initialWelcomeMsg]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [showSummaryCard, setShowSummaryCard] = useState(true);
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
      const response = await apiService.queryPatientCompanion(
        data.patient.patient_code,
        textToSend
      );

      const assistantMsgId = 'assistant-' + Date.now();
      setMessages((prev) => [
        ...prev,
        {
          id: assistantMsgId,
          sender: 'assistant',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text: response.answer,
          disclaimer: response.disclaimer,
        },
      ]);
    } catch (err: any) {
      const errorMsgId = 'error-' + Date.now();
      setMessages((prev) => [
        ...prev,
        {
          id: errorMsgId,
          sender: 'assistant',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text: `I apologize, but I could not retrieve your health records right now (${err?.message || 'Connection error'}). Please verify your connection or try again in a moment.`,
          disclaimer: 'For urgent medical questions, please contact your clinic directly.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleResetChat = () => {
    setMessages([initialWelcomeMsg]);
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 65px)',
        backgroundColor: '#f8fafc',
        color: '#0f172a',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* Top Patient Header Bar */}
      <div
        style={{
          backgroundColor: '#ffffff',
          borderBottom: '1px solid #e2e8f0',
          padding: '12px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          boxShadow: '0 1px 2px rgba(0,0,0,0.02)',
          zIndex: 10,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              backgroundColor: '#d97706',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              boxShadow: '0 2px 6px rgba(217, 119, 6, 0.25)',
            }}
          >
            <Bot size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontSize: '16px', fontWeight: 700, margin: 0, color: '#0f172a' }}>
                Personal Health Companion
              </h2>
              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  backgroundColor: '#fef3c7',
                  color: '#92400e',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  border: '1px solid #fde68a',
                }}
              >
                Informational Mode
              </span>
            </div>
            <p style={{ fontSize: '12px', color: '#64748b', margin: 0 }}>
              Grounded in records for {data.patient.name} ({data.patient.patient_code})
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={() => setShowSummaryCard(!showSummaryCard)}
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              border: '1px solid #cbd5e1',
              backgroundColor: showSummaryCard ? '#f1f5f9' : '#ffffff',
              color: '#475569',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Info size={14} />
            <span>{showSummaryCard ? 'Hide Health Card' : 'Show Health Card'}</span>
          </button>

          <button
            onClick={handleResetChat}
            title="Start new conversation"
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              border: '1px solid #e2e8f0',
              backgroundColor: '#ffffff',
              color: '#64748b',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <RotateCcw size={13} />
            <span>New Chat</span>
          </button>
        </div>
      </div>

      {/* Main Conversation Area */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px 24px 140px 24px',
          maxWidth: '960px',
          width: '100%',
          margin: '0 auto',
          boxSizing: 'border-box',
        }}
      >
        {/* Optional Collapsible Patient Health Summary Card */}
        {showSummaryCard && (
          <div
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '12px',
              border: '1px solid #e2e8f0',
              padding: '16px 20px',
              marginBottom: '24px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.03)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Stethoscope size={18} style={{ color: '#0284c7' }} />
                <span style={{ fontSize: '13px', fontWeight: 700, color: '#0f172a' }}>
                  Your Health Baseline at a Glance
                </span>
              </div>
              <span style={{ fontSize: '11px', color: '#94a3b8' }}>Verified Clinician Records</span>
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                gap: '12px',
              }}
            >
              {/* Prescriptions */}
              <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '10px 14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                  <Pill size={14} style={{ color: '#16a34a' }} />
                  <span style={{ fontSize: '12px', fontWeight: 700, color: '#166534' }}>Current Medications</span>
                </div>
                <div style={{ fontSize: '11px', color: '#14532d', lineHeight: '1.4' }}>
                  • <b>Metformin 500mg</b> — Twice daily with meals<br />
                  • <b>Amlodipine 5mg</b> — Morning for blood pressure<br />
                  • <b>Atorvastatin 10mg</b> — Nightly for cholesterol<br />
                  • <b>Glimepiride 1mg</b> — Morning with breakfast
                </div>
              </div>

              {/* Conditions */}
              <div style={{ backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '10px 14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                  <HeartPulse size={14} style={{ color: '#2563eb' }} />
                  <span style={{ fontSize: '12px', fontWeight: 700, color: '#1e40af' }}>Ongoing Conditions</span>
                </div>
                <div style={{ fontSize: '11px', color: '#1e3a8a', lineHeight: '1.4' }}>
                  • Type 2 Diabetes (Under active management)<br />
                  • Essential Hypertension (Monitored)<br />
                  • Bilateral Knee Osteoarthritis (Knee care)
                </div>
              </div>

              {/* Attending Physician */}
              <div style={{ backgroundColor: '#fffbeb', border: '1px solid #fef3c7', borderRadius: '8px', padding: '10px 14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                  <ShieldCheck size={14} style={{ color: '#d97706' }} />
                  <span style={{ fontSize: '12px', fontWeight: 700, color: '#92400e' }}>Doctor &amp; Clinic</span>
                </div>
                <div style={{ fontSize: '11px', color: '#78350f', lineHeight: '1.4' }}>
                  • <b>Dr. Ramesh Varma, MD</b> (Treating Physician)<br />
                  • Previous notes: Dr. S. Chandran, MD<br />
                  • Status: Next review in 3 months
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Message Stream */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {messages.map((msg) => {
            const isUser = msg.sender === 'user';
            return (
              <div
                key={msg.id}
                style={{
                  display: 'flex',
                  justifyContent: isUser ? 'flex-end' : 'flex-start',
                  alignItems: 'flex-start',
                  gap: '12px',
                }}
              >
                {!isUser && (
                  <div
                    style={{
                      width: '34px',
                      height: '34px',
                      borderRadius: '50%',
                      backgroundColor: '#d97706',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#ffffff',
                      flexShrink: 0,
                      marginTop: '2px',
                      boxShadow: '0 2px 4px rgba(217, 119, 6, 0.2)',
                    }}
                  >
                    <Bot size={18} />
                  </div>
                )}

                <div
                  style={{
                    maxWidth: isUser ? '75%' : '85%',
                    backgroundColor: isUser ? '#0f172a' : '#ffffff',
                    color: isUser ? '#ffffff' : '#0f172a',
                    padding: '14px 18px',
                    borderRadius: isUser ? '16px 16px 4px 16px' : '4px 16px 16px 16px',
                    boxShadow: isUser
                      ? '0 2px 8px rgba(15, 23, 42, 0.15)'
                      : '0 2px 8px rgba(0, 0, 0, 0.04)',
                    border: isUser ? 'none' : '1px solid #e2e8f0',
                  }}
                >
                  <div
                    style={{
                      fontSize: '14px',
                      lineHeight: '1.6',
                      whiteSpace: 'pre-line',
                      letterSpacing: '-0.01em',
                    }}
                  >
                    {msg.text}
                  </div>

                  {msg.isWelcome && (
                    <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #f1f5f9' }}>
                      <div
                        style={{
                          fontSize: '11px',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          color: '#64748b',
                          letterSpacing: '0.05em',
                          marginBottom: '8px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                        }}
                      >
                        <HelpCircle size={13} style={{ color: '#d97706' }} />
                        <span>Suggested Questions for Your Records:</span>
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {PATIENT_PROMPTS.map((prompt, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleSend(prompt)}
                            style={{
                              backgroundColor: '#f8fafc',
                              border: '1px solid #cbd5e1',
                              borderRadius: '16px',
                              padding: '5px 12px',
                              fontSize: '12px',
                              color: '#334155',
                              cursor: 'pointer',
                              textAlign: 'left',
                              transition: 'all 0.15s ease',
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.backgroundColor = '#fef3c7';
                              e.currentTarget.style.borderColor = '#f59e0b';
                              e.currentTarget.style.color = '#92400e';
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.backgroundColor = '#f8fafc';
                              e.currentTarget.style.borderColor = '#cbd5e1';
                              e.currentTarget.style.color = '#334155';
                            }}
                          >
                            {prompt}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {msg.disclaimer && (
                    <div
                      style={{
                        marginTop: '12px',
                        paddingTop: '8px',
                        borderTop: isUser ? 'none' : '1px solid #f1f5f9',
                        fontSize: '11px',
                        color: isUser ? '#cbd5e1' : '#64748b',
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '6px',
                        fontStyle: 'italic',
                      }}
                    >
                      <Info size={13} style={{ flexShrink: 0, marginTop: '2px', color: '#d97706' }} />
                      <span>{msg.disclaimer}</span>
                    </div>
                  )}

                  <div
                    style={{
                      fontSize: '10px',
                      color: isUser ? '#94a3b8' : '#94a3b8',
                      marginTop: '6px',
                      textAlign: 'right',
                    }}
                  >
                    {msg.timestamp}
                  </div>
                </div>

                {isUser && (
                  <div
                    style={{
                      width: '34px',
                      height: '34px',
                      borderRadius: '50%',
                      backgroundColor: '#0f172a',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#ffffff',
                      flexShrink: 0,
                      marginTop: '2px',
                    }}
                  >
                    <User size={18} />
                  </div>
                )}
              </div>
            );
          })}

          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div
                style={{
                  width: '34px',
                  height: '34px',
                  borderRadius: '50%',
                  backgroundColor: '#d97706',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ffffff',
                  flexShrink: 0,
                }}
              >
                <Bot size={18} />
              </div>
              <div
                style={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e2e8f0',
                  padding: '12px 18px',
                  borderRadius: '4px 16px 16px 16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: '#64748b',
                  fontSize: '13px',
                }}
              >
                <Sparkles size={16} className="animate-spin" style={{ color: '#d97706' }} />
                <span>Consulting your personal health records…</span>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>
      </div>

      {/* Floating Modern Pill Input at Bottom */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          backgroundColor: 'linear-gradient(to top, #f8fafc 80%, rgba(248, 250, 252, 0) 100%)',
          padding: '16px 24px 20px 24px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <div
          style={{
            maxWidth: '960px',
            width: '100%',
            backgroundColor: '#ffffff',
            borderRadius: '24px',
            border: '1px solid #cbd5e1',
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.08)',
            display: 'flex',
            alignItems: 'center',
            padding: '6px 8px 6px 18px',
            gap: '10px',
            boxSizing: 'border-box',
          }}
        >
          <input
            type="text"
            id="patient-companion-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask about your medicines, doctor's advice, appointments, or balance tips…"
            disabled={loading}
            style={{
              flex: 1,
              border: 'none',
              outline: 'none',
              fontSize: '14px',
              color: '#0f172a',
              backgroundColor: 'transparent',
            }}
          />
          <button
            id="patient-companion-send-btn"
            onClick={() => handleSend()}
            disabled={!inputValue.trim() || loading}
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '50%',
              backgroundColor: inputValue.trim() && !loading ? '#d97706' : '#e2e8f0',
              color: inputValue.trim() && !loading ? '#ffffff' : '#94a3b8',
              border: 'none',
              cursor: inputValue.trim() && !loading ? 'pointer' : 'default',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'background-color 0.15s ease',
              flexShrink: 0,
            }}
          >
            <Send size={16} />
          </button>
        </div>

        <div
          style={{
            marginTop: '8px',
            fontSize: '11px',
            color: '#64748b',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}
        >
          <ShieldCheck size={13} style={{ color: '#16a34a' }} />
          <span>Informational records viewer • Private &amp; encrypted • Always follow your doctor's clinical advice</span>
        </div>
      </div>
    </div>
  );
};

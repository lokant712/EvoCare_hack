import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  Bot,
  User,
  Info,
  ShieldCheck,
  HelpCircle,
  RotateCcw,
  HeartHandshake
} from 'lucide-react';
import { DashboardResponse } from '../../types';
import { apiService } from '../../services/api';
import { AuthUser } from '../../services/auth';
import { PatientCaregiverConnectionModal } from '../connection/PatientCaregiverConnectionModal';

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

const renderFormattedMessage = (text: string, isUser: boolean) => {
  const lines = text.split('\n');
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
      {lines.map((line, lineIdx) => {
        if (!line.trim()) {
          return <div key={lineIdx} style={{ height: '6px' }} />;
        }
        const parts = line.split(/(\*\*.*?\*\*)/g);
        const isBullet = line.trim().startsWith('•') || line.trim().startsWith('-');
        return (
          <div
            key={lineIdx}
            style={{
              paddingLeft: isBullet ? '14px' : '0',
              textIndent: isBullet ? '-14px' : '0',
              lineHeight: '1.6',
            }}
          >
            {parts.map((part, partIdx) => {
              if (part.startsWith('**') && part.endsWith('**') && part.length >= 4) {
                return (
                  <strong
                    key={partIdx}
                    style={{
                      fontWeight: 700,
                      color: isUser ? 'var(--color-accent-contrast)' : 'var(--color-text-main)',
                    }}
                  >
                    {part.slice(2, -2)}
                  </strong>
                );
              }
              return part;
            })}
          </div>
        );
      })}
    </div>
  );
};

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
  const [showCaretakerModal, setShowCaretakerModal] = useState(false);
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
        backgroundColor: 'var(--color-bg)',
        color: 'var(--color-text-main)',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* Top Patient Header Bar */}
      <div
        style={{
          backgroundColor: 'var(--color-surface)',
          borderBottom: '1px solid var(--color-border)',
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
              backgroundColor: 'var(--color-warning)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              boxShadow: '0 2px 6px rgba(163, 102, 31, 0.25)',
            }}
          >
            <Bot size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontSize: '16px', fontWeight: 700, margin: 0, color: 'var(--color-text-main)' }}>
                Personal Health Companion
              </h2>
              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  backgroundColor: 'var(--color-warning-soft)',
                  color: 'var(--color-warning-dark)',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  border: '1px solid var(--color-warning-border)',
                }}
              >
                Informational Mode
              </span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', margin: 0 }}>
              Grounded in records for {data.patient.name} ({data.patient.patient_code})
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            id="evocare-patient-caretaker-btn"
            onClick={() => setShowCaretakerModal(true)}
            style={{
              padding: '6px 14px',
              borderRadius: '6px',
              border: '1px solid var(--color-success-border)',
              backgroundColor: 'var(--color-success-soft)',
              color: 'var(--color-success-dark)',
              fontSize: '12px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <HeartHandshake size={14} />
            <span>My Caretaker</span>
          </button>

          <button
            onClick={handleResetChat}
            title="Start new conversation"
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              border: '1px solid var(--color-border)',
              backgroundColor: 'var(--color-surface)',
              color: 'var(--color-text-muted)',
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

      <PatientCaregiverConnectionModal
        isOpen={showCaretakerModal}
        onClose={() => setShowCaretakerModal(false)}
        patientCode={data.patient.patient_code}
        patientName={data.patient.name}
        user={user}
      />

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
                      backgroundColor: 'var(--color-warning)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#ffffff',
                      flexShrink: 0,
                      marginTop: '2px',
                      boxShadow: '0 2px 4px rgba(163, 102, 31, 0.2)',
                    }}
                  >
                    <Bot size={18} />
                  </div>
                )}

                <div
                  style={{
                    maxWidth: isUser ? '75%' : '85%',
                    backgroundColor: isUser ? 'var(--color-accent)' : 'var(--color-surface)',
                    color: isUser ? 'var(--color-accent-contrast)' : 'var(--color-text-main)',
                    padding: '14px 18px',
                    borderRadius: isUser ? '16px 16px 4px 16px' : '4px 16px 16px 16px',
                    boxShadow: isUser
                      ? 'var(--shadow-sm)'
                      : '0 2px 8px rgba(0, 0, 0, 0.04)',
                    border: isUser ? 'none' : '1px solid var(--color-border)',
                  }}
                >
                  <div
                    style={{
                      fontSize: '14px',
                      letterSpacing: '-0.01em',
                    }}
                  >
                    {renderFormattedMessage(msg.text, isUser)}
                  </div>

                  {msg.isWelcome && (
                    <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid var(--color-surface-alt)' }}>
                      <div
                        style={{
                          fontSize: '11px',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          color: 'var(--color-text-muted)',
                          letterSpacing: '0.05em',
                          marginBottom: '8px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                        }}
                      >
                        <HelpCircle size={13} style={{ color: 'var(--color-warning)' }} />
                        <span>Suggested Questions for Your Records:</span>
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {PATIENT_PROMPTS.map((prompt, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleSend(prompt)}
                            style={{
                              backgroundColor: 'var(--color-bg)',
                              border: '1px solid var(--color-border-strong)',
                              borderRadius: '16px',
                              padding: '5px 12px',
                              fontSize: '12px',
                              color: 'var(--color-text-secondary)',
                              cursor: 'pointer',
                              textAlign: 'left',
                              transition: 'all 0.15s ease',
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.backgroundColor = 'var(--color-warning-soft)';
                              e.currentTarget.style.borderColor = 'var(--color-warning)';
                              e.currentTarget.style.color = 'var(--color-warning-dark)';
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.backgroundColor = 'var(--color-bg)';
                              e.currentTarget.style.borderColor = 'var(--color-border-strong)';
                              e.currentTarget.style.color = 'var(--color-text-secondary)';
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
                        borderTop: isUser ? 'none' : '1px solid var(--color-surface-alt)',
                        fontSize: '11px',
                        color: isUser ? 'var(--color-border-strong)' : 'var(--color-text-muted)',
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '6px',
                        fontStyle: 'italic',
                      }}
                    >
                      <Info size={13} style={{ flexShrink: 0, marginTop: '2px', color: 'var(--color-warning)' }} />
                      <span>{msg.disclaimer}</span>
                    </div>
                  )}

                  <div
                    style={{
                      fontSize: '10px',
                      color: isUser ? 'var(--color-text-faint)' : 'var(--color-text-faint)',
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
                      backgroundColor: 'var(--color-accent)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'var(--color-accent-contrast)',
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
                  backgroundColor: 'var(--color-warning)',
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
                  backgroundColor: 'var(--color-surface)',
                  border: '1px solid var(--color-border)',
                  padding: '12px 18px',
                  borderRadius: '4px 16px 16px 16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: 'var(--color-text-muted)',
                  fontSize: '13px',
                }}
              >
                <Sparkles size={16} className="animate-spin" style={{ color: 'var(--color-warning)' }} />
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
          backgroundColor: 'linear-gradient(to top, var(--color-bg) 80%, rgba(247, 244, 238, 0) 100%)',
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
            backgroundColor: 'var(--color-surface)',
            borderRadius: '24px',
            border: '1px solid var(--color-border-strong)',
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
              color: 'var(--color-text-main)',
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
              backgroundColor: inputValue.trim() && !loading ? 'var(--color-warning)' : 'var(--color-border)',
              color: inputValue.trim() && !loading ? '#ffffff' : 'var(--color-text-faint)',
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
            color: 'var(--color-text-muted)',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}
        >
          <ShieldCheck size={13} style={{ color: 'var(--color-success)' }} />
          <span>Informational records viewer • Private &amp; encrypted • Always follow your doctor's clinical advice</span>
        </div>
      </div>
    </div>
  );
};

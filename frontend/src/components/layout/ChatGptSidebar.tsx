import React, { useState } from 'react';
import {
  MessageSquare,
  Plus,
  ClipboardList,
  PenSquare,
  ChevronLeft,
  ChevronRight,
  Trash2,
  Edit2,
  Clock,
  Pin,
  Bot,
  LogOut
} from 'lucide-react';
import { ChatSession } from '../../services/chatStorage';
import { AuthUser } from '../../services/auth';

interface ChatGptSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  activeTab: 'assistant' | 'records' | 'entry';
  onSelectTab: (tab: 'assistant' | 'records' | 'entry') => void;
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
  onDeleteSession: (sessionId: string) => void;
  onRenameSession: (sessionId: string, newTitle: string) => void;
  user: AuthUser;
  onLogout: () => void;
  sessionRemainingSeconds: number | null;
  patientName?: string;
  patientCode: string;
  onOpenSecurityModal?: () => void;
}

export const ChatGptSidebar: React.FC<ChatGptSidebarProps> = ({
  isOpen,
  onToggle,
  activeTab,
  onSelectTab,
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  onRenameSession,
  user,
  onLogout,
  sessionRemainingSeconds,
  patientCode,
  onOpenSecurityModal,
}) => {
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const handleStartRename = (e: React.MouseEvent, session: ChatSession) => {
    e.stopPropagation();
    setEditingSessionId(session.id);
    setEditTitle(session.title);
  };

  const handleSaveRename = (sessionId: string) => {
    if (editTitle.trim()) {
      onRenameSession(sessionId, editTitle.trim());
    }
    setEditingSessionId(null);
  };

  const formatTimer = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const pinnedSessions = sessions.filter((s) => s.isPinned);
  const recentSessions = sessions.filter((s) => !s.isPinned);

  if (!isOpen) {
    return (
      <div
        style={{
          width: '54px',
          height: '100vh',
          backgroundColor: 'var(--color-surface)',
          borderRight: '1px solid var(--color-border)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 0',
          zIndex: 30,
          flexShrink: 0,
          transition: 'width 0.2s ease',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={onToggle}
            title="Expand Sidebar"
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              backgroundColor: 'var(--color-surface-alt)',
              border: '1px solid var(--color-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--color-text-main)',
              cursor: 'pointer',
            }}
          >
            <ChevronRight size={18} />
          </button>

          <button
            onClick={onNewChat}
            title="New Chat"
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              backgroundColor: 'var(--color-accent-soft)',
              border: '1px solid var(--color-accent-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--color-accent-bright)',
              cursor: 'pointer',
            }}
          >
            <Plus size={18} />
          </button>

          <div style={{ width: '28px', height: '1px', backgroundColor: 'var(--color-border)' }} />

          <button
            onClick={() => onSelectTab('assistant')}
            title="Clinical Assistant"
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              backgroundColor: activeTab === 'assistant' ? 'var(--color-surface-raised)' : 'transparent',
              border: activeTab === 'assistant' ? '1px solid var(--color-accent)' : 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: activeTab === 'assistant' ? 'var(--color-accent)' : 'var(--color-text-muted)',
              cursor: 'pointer',
            }}
          >
            <MessageSquare size={18} />
          </button>

          <button
            onClick={() => onSelectTab('records')}
            title="Patient Health Records"
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              backgroundColor: activeTab === 'records' ? 'var(--color-surface-raised)' : 'transparent',
              border: activeTab === 'records' ? '1px solid var(--color-accent)' : 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: activeTab === 'records' ? 'var(--color-accent)' : 'var(--color-text-muted)',
              cursor: 'pointer',
            }}
          >
            <ClipboardList size={18} />
          </button>

          <button
            onClick={() => onSelectTab('entry')}
            title="Diagnosis & Rx Entry"
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              backgroundColor: activeTab === 'entry' ? 'var(--color-surface-raised)' : 'transparent',
              border: activeTab === 'entry' ? '1px solid var(--color-accent)' : 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: activeTab === 'entry' ? 'var(--color-accent)' : 'var(--color-text-muted)',
              cursor: 'pointer',
            }}
          >
            <PenSquare size={18} />
          </button>
        </div>

        <button
          onClick={onLogout}
          title="Sign Out"
          style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            backgroundColor: 'transparent',
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--color-text-faint)',
            cursor: 'pointer',
          }}
        >
          <LogOut size={18} />
        </button>
      </div>
    );
  }

  return (
    <aside
      style={{
        width: '260px',
        height: '100vh',
        backgroundColor: 'var(--color-surface)',
        borderRight: '1px solid var(--color-border)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        flexShrink: 0,
        zIndex: 30,
        transition: 'width 0.2s ease',
        overflow: 'hidden',
      }}
    >
      {/* Top Header & New Chat Button */}
      <div style={{ padding: '12px 14px', borderBottom: '1px solid var(--color-border)' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                width: '26px',
                height: '26px',
                borderRadius: '7px',
                backgroundColor: 'var(--color-accent)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
              }}
            >
              <Bot size={15} />
            </div>
            <span style={{ fontSize: '13px', fontWeight: 800, color: 'var(--color-text-main)', letterSpacing: '-0.02em' }}>
              EvoCare AI
            </span>
            <span
              onClick={onOpenSecurityModal}
              title="Click to view 2FA Security Consent Gate"
              style={{
                fontSize: '9px',
                fontWeight: 700,
                padding: '2px 5px',
                borderRadius: '4px',
                backgroundColor: 'var(--color-accent-soft)',
                color: 'var(--color-accent)',
                fontFamily: 'var(--font-mono)',
                cursor: onOpenSecurityModal ? 'pointer' : 'default',
              }}
            >
              CLINICAL
            </span>
          </div>

          <button
            onClick={onToggle}
            title="Collapse sidebar"
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--color-text-muted)',
              cursor: 'pointer',
              padding: '4px',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <ChevronLeft size={18} />
          </button>
        </div>

        {/* New Chat Primary Button (ChatGPT Style) */}
        <button
          onClick={onNewChat}
          style={{
            width: '100%',
            padding: '9px 12px',
            borderRadius: '10px',
            backgroundColor: 'var(--color-surface-alt)',
            border: '1px solid var(--color-border-strong)',
            color: 'var(--color-text-main)',
            fontSize: '13px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--color-surface-raised)';
            e.currentTarget.style.borderColor = 'var(--color-accent)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--color-surface-alt)';
            e.currentTarget.style.borderColor = 'var(--color-border-strong)';
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Plus size={16} style={{ color: 'var(--color-accent)' }} />
            <span>New Consultation</span>
          </div>
          <span
            style={{
              fontSize: '10px',
              color: 'var(--color-text-faint)',
              fontFamily: 'var(--font-mono)',
            }}
          >
            {patientCode}
          </span>
        </button>
      </div>

      {/* Main Navigation Tabs */}
      <div style={{ padding: '8px 10px', borderBottom: '1px solid var(--color-border)' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
          <button
            onClick={() => onSelectTab('assistant')}
            style={{
              padding: '8px 10px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeTab === 'assistant' ? 'var(--color-accent-soft)' : 'transparent',
              color: activeTab === 'assistant' ? 'var(--color-accent-bright)' : 'var(--color-text-main)',
              fontSize: '12px',
              fontWeight: activeTab === 'assistant' ? 700 : 500,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              cursor: 'pointer',
              textAlign: 'left',
              width: '100%',
            }}
          >
            <MessageSquare size={15} style={{ color: activeTab === 'assistant' ? 'var(--color-accent)' : 'var(--color-text-muted)' }} />
            <span>Clinical AI Assistant</span>
          </button>

          <button
            onClick={() => onSelectTab('records')}
            style={{
              padding: '8px 10px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeTab === 'records' ? 'var(--color-accent-soft)' : 'transparent',
              color: activeTab === 'records' ? 'var(--color-accent-bright)' : 'var(--color-text-main)',
              fontSize: '12px',
              fontWeight: activeTab === 'records' ? 700 : 500,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              cursor: 'pointer',
              textAlign: 'left',
              width: '100%',
            }}
          >
            <ClipboardList size={15} style={{ color: activeTab === 'records' ? 'var(--color-accent)' : 'var(--color-text-muted)' }} />
            <span>Patient Health Records</span>
          </button>

          <button
            onClick={() => onSelectTab('entry')}
            style={{
              padding: '8px 10px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeTab === 'entry' ? 'var(--color-accent-soft)' : 'transparent',
              color: activeTab === 'entry' ? 'var(--color-accent-bright)' : 'var(--color-text-main)',
              fontSize: '12px',
              fontWeight: activeTab === 'entry' ? 700 : 500,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              cursor: 'pointer',
              textAlign: 'left',
              width: '100%',
            }}
          >
            <PenSquare size={15} style={{ color: activeTab === 'entry' ? 'var(--color-accent)' : 'var(--color-text-muted)' }} />
            <span>Diagnosis & Rx Entry</span>
          </button>
        </div>
      </div>

      {/* Chat Sessions History List (ChatGPT Pinned & Recent) */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '10px 10px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
        }}
      >
        {/* Pinned Section */}
        {pinnedSessions.length > 0 && (
          <div>
            <div
              style={{
                fontSize: '10px',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                color: 'var(--color-text-faint)',
                padding: '4px 6px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <Pin size={11} />
              <span>Pinned Consultations</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', marginTop: '2px' }}>
              {pinnedSessions.map((session) => {
                const isActive = activeSessionId === session.id && activeTab === 'assistant';
                return (
                  <div
                    key={session.id}
                    onClick={() => {
                      onSelectTab('assistant');
                      onSelectSession(session.id);
                    }}
                    style={{
                      padding: '7px 8px',
                      borderRadius: '7px',
                      backgroundColor: isActive ? 'var(--color-surface-raised)' : 'transparent',
                      border: isActive ? '1px solid var(--color-border-strong)' : '1px solid transparent',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', minWidth: 0, flex: 1 }}>
                      <MessageSquare size={13} style={{ color: isActive ? 'var(--color-accent)' : 'var(--color-text-muted)', flexShrink: 0 }} />
                      {editingSessionId === session.id ? (
                        <input
                          type="text"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          onBlur={() => handleSaveRename(session.id)}
                          onKeyDown={(e) => e.key === 'Enter' && handleSaveRename(session.id)}
                          autoFocus
                          style={{
                            width: '100%',
                            fontSize: '11px',
                            backgroundColor: 'var(--color-bg)',
                            color: 'var(--color-text-main)',
                            border: '1px solid var(--color-accent)',
                            borderRadius: '4px',
                            padding: '2px 4px',
                          }}
                        />
                      ) : (
                        <span
                          style={{
                            fontSize: '11px',
                            color: isActive ? 'var(--color-text-main)' : 'var(--color-text-secondary)',
                            fontWeight: isActive ? 600 : 400,
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}
                        >
                          {session.title}
                        </span>
                      )}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
                      <button
                        onClick={(e) => handleStartRename(e, session)}
                        title="Rename"
                        style={{
                          background: 'none',
                          border: 'none',
                          color: 'var(--color-text-faint)',
                          padding: '2px',
                          cursor: 'pointer',
                          display: 'none',
                        }}
                      >
                        <Edit2 size={11} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Recent Chats Section */}
        <div>
          <div
            style={{
              fontSize: '10px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: 'var(--color-text-faint)',
              padding: '4px 6px',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Clock size={11} />
            <span>Recent Conversations</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', marginTop: '2px' }}>
            {recentSessions.map((session) => {
              const isActive = activeSessionId === session.id && activeTab === 'assistant';
              return (
                <div
                  key={session.id}
                  onClick={() => {
                    onSelectTab('assistant');
                    onSelectSession(session.id);
                  }}
                  style={{
                    padding: '7px 8px',
                    borderRadius: '7px',
                    backgroundColor: isActive ? 'var(--color-surface-raised)' : 'transparent',
                    border: isActive ? '1px solid var(--color-border-strong)' : '1px solid transparent',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', minWidth: 0, flex: 1 }}>
                    <MessageSquare size={13} style={{ color: isActive ? 'var(--color-accent)' : 'var(--color-text-muted)', flexShrink: 0 }} />
                    {editingSessionId === session.id ? (
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onBlur={() => handleSaveRename(session.id)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSaveRename(session.id)}
                        autoFocus
                        style={{
                          width: '100%',
                          fontSize: '11px',
                          backgroundColor: 'var(--color-bg)',
                          color: 'var(--color-text-main)',
                          border: '1px solid var(--color-accent)',
                          borderRadius: '4px',
                          padding: '2px 4px',
                        }}
                      />
                    ) : (
                      <span
                        style={{
                          fontSize: '11px',
                          color: isActive ? 'var(--color-text-main)' : 'var(--color-text-secondary)',
                          fontWeight: isActive ? 600 : 400,
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                        }}
                      >
                        {session.title}
                      </span>
                    )}
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(session.id);
                    }}
                    title="Delete session"
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--color-text-faint)',
                      padding: '2px',
                      cursor: 'pointer',
                      opacity: 0.6,
                    }}
                  >
                    <Trash2 size={11} />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Doctor User Profile & Session Timer at Bottom */}
      <div
        style={{
          padding: '12px 14px',
          borderTop: '1px solid var(--color-border)',
          backgroundColor: 'var(--color-surface-alt)',
        }}
      >
        {/* Session Timer Pill */}
        {sessionRemainingSeconds !== null && (
          <div
            style={{
              padding: '4px 8px',
              borderRadius: '6px',
              backgroundColor: sessionRemainingSeconds < 120 ? 'var(--color-danger-soft)' : 'var(--color-accent-soft)',
              border: `1px solid ${sessionRemainingSeconds < 120 ? 'var(--color-danger-border)' : 'var(--color-accent-border)'}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '10px',
              fontSize: '11px',
            }}
          >
            <span
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                color: sessionRemainingSeconds < 120 ? 'var(--color-danger)' : 'var(--color-accent)',
                fontWeight: 600,
              }}
            >
              <Clock size={12} />
              Session:
            </span>
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontWeight: 700,
                color: sessionRemainingSeconds < 120 ? 'var(--color-danger)' : 'var(--color-accent-bright)',
              }}
            >
              {formatTimer(sessionRemainingSeconds)}
            </span>
          </div>
        )}

        {/* Doctor Info Row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                backgroundColor: 'var(--color-accent)',
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 700,
                fontSize: '11px',
                flexShrink: 0,
              }}
            >
              {user.username ? user.username.slice(0, 2).toUpperCase() : 'DR'}
            </div>
            <div style={{ minWidth: 0 }}>
              <div
                style={{
                  fontSize: '12px',
                  fontWeight: 700,
                  color: 'var(--color-text-main)',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {user.full_name || 'Dr. A. Chandran, MD'}
              </div>
              <div style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>
                Attending Physician
              </div>
            </div>
          </div>

          <button
            onClick={onLogout}
            title="Sign Out"
            style={{
              padding: '6px',
              borderRadius: '6px',
              background: 'none',
              border: 'none',
              color: 'var(--color-text-faint)',
              cursor: 'pointer',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--color-danger)')}
            onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--color-text-faint)')}
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
};

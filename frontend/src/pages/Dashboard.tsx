import React, { useState, useEffect } from 'react';
import { usePatient } from '../hooks/usePatient';
import { Header } from '../components/layout/Header';
import { ChatGptSidebar } from '../components/layout/ChatGptSidebar';
import { PatientRecordsTab } from '../components/patient/PatientRecordsTab';
import { ClinicalAssistantTab } from '../components/assistant/ClinicalAssistantTab';
import { DoctorClinicalEntryTab } from '../components/clinical/DoctorClinicalEntryTab';
import { PatientCompanionTab } from '../components/patient/PatientCompanionTab';
import { CaregiverNotesTab } from '../components/caregiver/CaregiverNotesTab';
import { CaretakerMobileApp } from './CaretakerMobileApp';
import { AdminUserManagement } from '../components/admin/AdminUserManagement';
import { DoctorPatientAccessGate } from '../components/doctor/DoctorPatientAccessGate';
import { WhyModal } from '../components/evidence/WhyModal';
import { EvidenceDrawer } from '../components/evidence/EvidenceDrawer';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { ThemeToggle } from '../components/common/ThemeToggle';
import { RecentChangeItem, EvidenceDetailItem } from '../types';
import {
  ShieldCheck,
  MessageSquare,
  ClipboardList,
  PenSquare,
  Menu,
  UserCheck
} from 'lucide-react';
import { authService, AuthUser, AuthorizedPatient } from '../services/auth';
import { chatStorageService, ChatSession, ChatMessage } from '../services/chatStorage';

interface DashboardProps {
  user: AuthUser;
  onLogout: () => void;
}

type TabType = 'assistant' | 'records' | 'entry';

export const Dashboard: React.FC<DashboardProps> = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState<TabType>('assistant');
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [authorizedPatients, setAuthorizedPatients] = useState<AuthorizedPatient[]>([]);
  const [selectedPatientCode, setSelectedPatientCode] = useState<string>('P001');
  const [verifiedPatientCodes, setVerifiedPatientCodes] = useState<Set<string>>(
    () => new Set(['P001', 'P002', 'P003', 'P004', 'P005'])
  );
  const [sessionRemainingSeconds, setSessionRemainingSeconds] = useState<number | null>(null);
  const [show2FAModal, setShow2FAModal] = useState<boolean>(false);

  // Responsive device detection for Caretaker: auto-switches between mobile & desktop PC
  const [isMobileScreen, setIsMobileScreen] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return window.innerWidth < 768;
    }
    return false;
  });
  const [caregiverViewMode, setCaregiverViewMode] = useState<'auto' | 'mobile' | 'desktop'>('auto');

  useEffect(() => {
    const handleResize = () => {
      setIsMobileScreen(window.innerWidth < 768);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Chat sessions state
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  const { data, loading, error, refetch } = usePatient(selectedPatientCode);
  const [selectedWhyChange, setSelectedWhyChange] = useState<RecentChangeItem | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceDetailItem | null>(null);

  // Load chat sessions on patient change & always start with a fresh new chat on login
  useEffect(() => {
    // Create a fresh consultation session for this doctor login session
    const newSession = chatStorageService.createNewSession(selectedPatientCode, 'New Consultation Inquiry');
    const allSessions = chatStorageService.getSessions(selectedPatientCode);
    setChatSessions(allSessions);
    setActiveSessionId(newSession.id);
    setActiveTab('assistant');
  }, [selectedPatientCode]);

  // 10-Minute session timeout effect for doctors
  useEffect(() => {
    if (user.role !== 'DOCTOR' || sessionRemainingSeconds === null) return;

    if (sessionRemainingSeconds <= 0) {
      // 10 minutes session timed out -> auto-lock record immediately!
      setVerifiedPatientCodes(new Set());
      setSessionRemainingSeconds(null);
      return;
    }

    const timer = setInterval(() => {
      setSessionRemainingSeconds((prev) => (prev !== null && prev > 0 ? prev - 1 : 0));
    }, 1000);

    return () => clearInterval(timer);
  }, [user.role, sessionRemainingSeconds]);

  const reloadAuthorizedPatients = async () => {
    const patients = await authService.getAuthorizedPatients();
    setAuthorizedPatients(patients);
    return patients;
  };

  // Fetch authorized patient list from backend
  useEffect(() => {
    reloadAuthorizedPatients().then((patients) => {
      if (patients.length > 0 && !selectedPatientCode) {
        setSelectedPatientCode(patients[0].patient_code);
      }
    });
  }, []);

  const handlePatientUnlocked = (code: string) => {
    setVerifiedPatientCodes(new Set([code]));
    setSelectedPatientCode(code);
    if (user.role === 'DOCTOR') {
      setSessionRemainingSeconds(600);
    }
    setShow2FAModal(false);
    reloadAuthorizedPatients();
    refetch();
  };

  const handleOpenEvidence = (code: string) => {
    if (data?.provenance_map && data.provenance_map[code]) {
      setSelectedEvidence(data.provenance_map[code]);
    } else {
      setSelectedEvidence({
        evidence_code: code,
        patient_id: data?.patient?.id || 1,
        source_type: code.startsWith('EV-CG') ? 'CAREGIVER' : code.startsWith('EV-DR') ? 'DOCTOR' : 'PATIENT',
        observed_at: '—',
        recorded_at: '—',
        original_statement: `Evidence record ${code}. Full record available in the backend evidence store.`,
        category: 'general',
        status: 'IMMUTABLE',
        observer: 'On record',
        linked_claims: [],
      });
    }
  };

  // Chat session operations
  const handleNewChat = () => {
    const newSession = chatStorageService.createNewSession(selectedPatientCode, 'New Consultation Inquiry');
    const updated = chatStorageService.getSessions(selectedPatientCode);
    setChatSessions(updated);
    setActiveSessionId(newSession.id);
    setActiveTab('assistant');
  };

  const handleDeleteSession = (sessionId: string) => {
    chatStorageService.deleteSession(sessionId);
    const updated = chatStorageService.getSessions(selectedPatientCode);
    setChatSessions(updated);
    if (activeSessionId === sessionId) {
      if (updated.length > 0) {
        setActiveSessionId(updated[0].id);
      } else {
        handleNewChat();
      }
    }
  };

  const handleRenameSession = (sessionId: string, newTitle: string) => {
    chatStorageService.renameSession(sessionId, newTitle);
    const updated = chatStorageService.getSessions(selectedPatientCode);
    setChatSessions(updated);
  };

  const handleUpdateSessionMessages = (sessionId: string, messages: ChatMessage[]) => {
    const session = chatSessions.find((s) => s.id === sessionId);
    if (session) {
      const updatedSession: ChatSession = {
        ...session,
        messages,
        updatedAt: 'Just now',
      };
      // If title is default and user sent first message, auto-name the session
      if (session.title === 'New Consultation Inquiry' && messages.length > 0) {
        const firstUser = messages.find((m) => m.sender === 'user');
        if (firstUser && firstUser.text) {
          updatedSession.title = firstUser.text.slice(0, 36) + (firstUser.text.length > 36 ? '…' : '');
        }
      }
      chatStorageService.saveSession(updatedSession);
      const allUpdated = chatStorageService.getSessions(selectedPatientCode);
      setChatSessions(allUpdated);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-bg)' }}>
        <LoadingSpinner message="Loading EvoCare Patient Dashboard…" />
      </div>
    );
  }

  // Admin Login Mode
  if (user.role === 'ADMIN') {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-bg)', color: 'var(--color-text-main)', fontFamily: 'var(--font-sans)' }}>
        <div style={{ backgroundColor: '#1c1a14', borderBottom: '1px solid #3d3a2f', padding: '14px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: '#d9a24a', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ShieldCheck size={20} color="#1c1a14" />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '15px', color: '#f7f4ee' }}>EvoCare — Admin Console</div>
              <div style={{ fontSize: '11px', color: '#a89d89' }}>User Management & System Oversight</div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '13px', color: '#a89d89' }}>Logged in as <b style={{ color: '#f7f4ee' }}>{user.full_name || user.username}</b></span>
            <ThemeToggle size="sm" />
            <button onClick={onLogout} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid #5b5346', backgroundColor: 'transparent', color: '#a89d89', fontSize: '12px', cursor: 'pointer', fontWeight: 600 }}>
              Sign Out
            </button>
          </div>
        </div>
        <AdminUserManagement user={user} />
      </div>
    );
  }

  // Doctor Role: 2FA Gate
  if (user.role === 'DOCTOR' && !verifiedPatientCodes.has(selectedPatientCode)) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-bg)', color: 'var(--color-text-main)' }}>
        <Header
          patient={{
            id: 1,
            patient_code: selectedPatientCode,
            name: 'Patient Record Locked',
            age: 0,
            sex: '—',
            location: '2-Step Consent Required',
            dataset_type: 'SYNTHETIC',
            primary_language: 'English',
          }}
          user={user}
          authorizedPatients={authorizedPatients}
          selectedPatientCode={selectedPatientCode}
          onSelectPatient={(code) => setSelectedPatientCode(code)}
          onLogout={onLogout}
          onOpen2FA={() => setShow2FAModal(true)}
        />
        <main>
          <DoctorPatientAccessGate
            initialPatientCode={selectedPatientCode}
            onPatientUnlocked={handlePatientUnlocked}
          />
        </main>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-bg)', padding: '40px 20px' }}>
        <ErrorMessage message={error || `Patient ${selectedPatientCode} records unavailable.`} onRetry={refetch} />
      </div>
    );
  }

  // Patient Login Mode
  if (user.role === 'PATIENT') {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-bg)', color: 'var(--color-text-main)' }}>
        <Header
          patient={data.patient}
          user={user}
          authorizedPatients={authorizedPatients}
          selectedPatientCode={selectedPatientCode}
          onSelectPatient={setSelectedPatientCode}
          onLogout={onLogout}
        />
        <main style={{ flex: 1 }}>
          <PatientCompanionTab data={data} user={user} />
        </main>
      </div>
    );
  }

  // Caregiver Login Mode: Actively switches between Mobile Smartphone App and Desktop PC Portal based on screen width / device
  if (user.role === 'CAREGIVER') {
    const showMobileView =
      caregiverViewMode === 'mobile' || (caregiverViewMode === 'auto' && isMobileScreen);

    if (showMobileView) {
      return (
        <div style={{ minHeight: '100dvh', backgroundColor: 'var(--color-bg)', color: 'var(--color-text-main)' }}>
          <CaretakerMobileApp
            data={data}
            user={user}
            authorizedPatients={authorizedPatients}
            selectedPatientCode={selectedPatientCode}
            onSelectPatient={setSelectedPatientCode}
            onObservationSaved={refetch}
            onLogout={onLogout}
            onSwitchToDesktop={() => setCaregiverViewMode('desktop')}
          />
        </div>
      );
    }

    // Full PC Desktop Caregiver Portal View
    return (
      <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-bg)', color: 'var(--color-text-main)' }}>
        <Header
          patient={data.patient}
          user={user}
          authorizedPatients={authorizedPatients}
          selectedPatientCode={selectedPatientCode}
          onSelectPatient={setSelectedPatientCode}
          onLogout={onLogout}
        />
        <main style={{ flex: 1 }}>
          <CaregiverNotesTab
            data={data}
            user={user}
            onObservationSaved={refetch}
            onSwitchToMobile={() => setCaregiverViewMode('mobile')}
          />
        </main>
      </div>
    );
  }

  // Find active chat session
  const activeSession =
    chatSessions.find((s) => s.id === activeSessionId) ||
    chatSessions[0] || {
      id: 'session-default',
      patientCode: selectedPatientCode,
      title: 'Active Consultation',
      createdAt: 'Just now',
      updatedAt: 'Just now',
      messages: [],
    };

  return (
    <div
      style={{
        display: 'flex',
        height: '100vh',
        width: '100vw',
        backgroundColor: 'var(--color-bg)',
        color: 'var(--color-text-main)',
        overflow: 'hidden',
      }}
    >
      {/* ChatGPT-Style Left Sidebar */}
      <ChatGptSidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        activeTab={activeTab}
        onSelectTab={(tab) => setActiveTab(tab)}
        sessions={chatSessions}
        activeSessionId={activeSessionId}
        onSelectSession={(id) => setActiveSessionId(id)}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        onRenameSession={handleRenameSession}
        user={user}
        onLogout={onLogout}
        sessionRemainingSeconds={sessionRemainingSeconds}
        patientName={data.patient.name}
        patientCode={data.patient.patient_code}
        onOpenSecurityModal={() => setShow2FAModal(true)}
      />

      {/* Main Canvas Area */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
          minWidth: 0,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Top Minimal ChatGPT-Style Header Bar */}
        <header
          style={{
            height: '52px',
            backgroundColor: 'var(--color-surface)',
            borderBottom: '1px solid var(--color-border)',
            padding: '0 16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexShrink: 0,
            zIndex: 20,
          }}
        >
          {/* Left: Sidebar Toggle + Mode Switcher Pill */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {!sidebarOpen && (
              <button
                onClick={() => setSidebarOpen(true)}
                title="Open Sidebar"
                style={{
                  width: '34px',
                  height: '34px',
                  borderRadius: '8px',
                  backgroundColor: 'var(--color-surface-alt)',
                  border: '1px solid var(--color-border)',
                  color: 'var(--color-text-main)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                }}
              >
                <Menu size={16} />
              </button>
            )}

            {/* Top Navigation Mode Pills (ChatGPT style) */}
            <div
              style={{
                display: 'flex',
                backgroundColor: 'var(--color-surface-alt)',
                padding: '3px',
                borderRadius: '10px',
                border: '1px solid var(--color-border)',
              }}
            >
              <button
                onClick={() => setActiveTab('assistant')}
                style={{
                  padding: '5px 12px',
                  borderRadius: '8px',
                  border: 'none',
                  backgroundColor: activeTab === 'assistant' ? 'var(--color-surface-raised)' : 'transparent',
                  color: activeTab === 'assistant' ? 'var(--color-text-main)' : 'var(--color-text-muted)',
                  fontWeight: activeTab === 'assistant' ? 700 : 500,
                  fontSize: '12px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  boxShadow: activeTab === 'assistant' ? 'var(--shadow-sm)' : 'none',
                  transition: 'all 0.15s ease',
                }}
              >
                <MessageSquare size={13} style={{ color: activeTab === 'assistant' ? 'var(--color-accent)' : 'inherit' }} />
                <span>Chat</span>
              </button>

              <button
                onClick={() => setActiveTab('records')}
                style={{
                  padding: '5px 12px',
                  borderRadius: '8px',
                  border: 'none',
                  backgroundColor: activeTab === 'records' ? 'var(--color-surface-raised)' : 'transparent',
                  color: activeTab === 'records' ? 'var(--color-text-main)' : 'var(--color-text-muted)',
                  fontWeight: activeTab === 'records' ? 700 : 500,
                  fontSize: '12px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  boxShadow: activeTab === 'records' ? 'var(--shadow-sm)' : 'none',
                  transition: 'all 0.15s ease',
                }}
              >
                <ClipboardList size={13} style={{ color: activeTab === 'records' ? 'var(--color-accent)' : 'inherit' }} />
                <span>Health Records</span>
              </button>

              <button
                onClick={() => setActiveTab('entry')}
                style={{
                  padding: '5px 12px',
                  borderRadius: '8px',
                  border: 'none',
                  backgroundColor: activeTab === 'entry' ? 'var(--color-surface-raised)' : 'transparent',
                  color: activeTab === 'entry' ? 'var(--color-text-main)' : 'var(--color-text-muted)',
                  fontWeight: activeTab === 'entry' ? 700 : 500,
                  fontSize: '12px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  boxShadow: activeTab === 'entry' ? 'var(--shadow-sm)' : 'none',
                  transition: 'all 0.15s ease',
                }}
              >
                <PenSquare size={13} style={{ color: activeTab === 'entry' ? 'var(--color-accent)' : 'inherit' }} />
                <span>Diagnosis Entry</span>
              </button>
            </div>
          </div>

          {/* Center: Patient Selector Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '4px 10px',
                borderRadius: '10px',
                backgroundColor: 'var(--color-surface-alt)',
                border: '1px solid var(--color-border)',
              }}
            >
              <span style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontWeight: 600 }}>
                Patient:
              </span>
              <select
                value={selectedPatientCode}
                onChange={(e) => setSelectedPatientCode(e.target.value)}
                style={{
                  backgroundColor: 'transparent',
                  border: 'none',
                  color: 'var(--color-text-main)',
                  fontSize: '12px',
                  fontWeight: 700,
                  outline: 'none',
                  cursor: 'pointer',
                }}
              >
                {authorizedPatients.map((p) => (
                  <option key={p.patient_code} value={p.patient_code} style={{ backgroundColor: 'var(--color-surface)', color: 'var(--color-text-main)' }}>
                    {p.name} ({p.patient_code})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Right: Theme Toggle & Security Status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ThemeToggle size="sm" />
            <button
              onClick={() => setShow2FAModal(true)}
              title="Doctor 2FA Security Consent Verified"
              style={{
                padding: '4px 10px',
                borderRadius: '8px',
                backgroundColor: 'var(--color-success-soft)',
                border: '1px solid var(--color-success-border)',
                color: 'var(--color-success)',
                fontSize: '11px',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                cursor: 'pointer',
              }}
            >
              <UserCheck size={13} />
              <span>2FA Verified</span>
            </button>
          </div>
        </header>

        {/* Dynamic Tab Body */}
        <div style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {activeTab === 'assistant' && (
            <ClinicalAssistantTab
              data={data}
              user={user}
              onSelectEvidence={handleOpenEvidence}
              onSwitchToPatientRecords={() => setActiveTab('records')}
              activeSession={activeSession}
              onUpdateSessionMessages={handleUpdateSessionMessages}
            />
          )}

          {activeTab === 'records' && (
            <div style={{ flex: 1, overflowY: 'auto', padding: '24px 32px' }}>
              <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
                <PatientRecordsTab
                  data={data}
                  onOpenWhy={(change) => setSelectedWhyChange(change)}
                  onSelectEvidence={handleOpenEvidence}
                />
              </div>
            </div>
          )}

          {activeTab === 'entry' && (
            <div style={{ flex: 1, overflowY: 'auto', padding: '24px 32px' }}>
              <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
                <DoctorClinicalEntryTab
                  data={data}
                  onEntrySaved={refetch}
                  onSelectEvidence={handleOpenEvidence}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 2-Step Verification Modal if doctor clicks Unlock Patient */}
      {show2FAModal && (
        <DoctorPatientAccessGate
          isModal={true}
          initialPatientCode={selectedPatientCode}
          onPatientUnlocked={handlePatientUnlocked}
          onCancel={() => setShow2FAModal(false)}
        />
      )}

      {/* Modals & Evidence Drawers */}
      <WhyModal
        change={selectedWhyChange}
        provenanceMap={data.provenance_map}
        onClose={() => setSelectedWhyChange(null)}
        onSelectEvidence={handleOpenEvidence}
      />

      <EvidenceDrawer
        evidence={selectedEvidence}
        onClose={() => setSelectedEvidence(null)}
      />
    </div>
  );
};

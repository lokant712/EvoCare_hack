import React, { useState, useEffect } from 'react';
import { usePatient } from '../hooks/usePatient';
import { Header } from '../components/layout/Header';
import { PatientRecordsTab } from '../components/patient/PatientRecordsTab';
import { ClinicalAssistantTab } from '../components/assistant/ClinicalAssistantTab';
import { DoctorClinicalEntryTab } from '../components/clinical/DoctorClinicalEntryTab';
import { PatientCompanionTab } from '../components/patient/PatientCompanionTab';
import { CaregiverNotesTab } from '../components/caregiver/CaregiverNotesTab';
import { AdminUserManagement } from '../components/admin/AdminUserManagement';
import { DoctorPatientAccessGate } from '../components/doctor/DoctorPatientAccessGate';
import { WhyModal } from '../components/evidence/WhyModal';
import { EvidenceDrawer } from '../components/evidence/EvidenceDrawer';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { RecentChangeItem, EvidenceDetailItem } from '../types';
import { ShieldCheck, MessageSquare, ClipboardList, PenSquare } from 'lucide-react';
import { authService, AuthUser, AuthorizedPatient } from '../services/auth';

interface DashboardProps {
  user: AuthUser;
  onLogout: () => void;
}

type TabType = 'assistant' | 'records' | 'entry';

export const Dashboard: React.FC<DashboardProps> = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState<TabType>('assistant');
  const [authorizedPatients, setAuthorizedPatients] = useState<AuthorizedPatient[]>([]);
  const [selectedPatientCode, setSelectedPatientCode] = useState<string>('P001');
  const [verifiedPatientCodes, setVerifiedPatientCodes] = useState<Set<string>>(() => {
    // Other roles don't require doctor-patient 2FA gate
    if (user.role !== 'DOCTOR') {
      return new Set(['P001', 'P002']);
    }
    return new Set<string>();
  });
  const [show2FAModal, setShow2FAModal] = useState<boolean>(false);

  const { data, loading, error, refetch } = usePatient(selectedPatientCode);
  const [selectedWhyChange, setSelectedWhyChange] = useState<RecentChangeItem | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceDetailItem | null>(null);

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
    // Strictly one patient active per doctor at a time
    setVerifiedPatientCodes(new Set([code]));
    setSelectedPatientCode(code);
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

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
        <LoadingSpinner message="Loading EvoCare Patient Dashboard…" />
      </div>
    );
  }

  // Admin Login Mode: Full User Management Console
  if (user.role === 'ADMIN') {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', color: '#0f172a', fontFamily: 'Inter, system-ui, sans-serif' }}>
        {/* Admin Header */}
        <div style={{ backgroundColor: '#1e293b', borderBottom: '1px solid #334155', padding: '14px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: '#f59e0b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ShieldCheck size={20} color="#1e293b" />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '15px', color: '#f8fafc' }}>EvoCare — Admin Console</div>
              <div style={{ fontSize: '11px', color: '#94a3b8' }}>User Management & System Oversight</div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '13px', color: '#94a3b8' }}>Logged in as <b style={{ color: '#f8fafc' }}>{user.full_name || user.username}</b></span>
            <button onClick={onLogout} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid #475569', backgroundColor: 'transparent', color: '#94a3b8', fontSize: '12px', cursor: 'pointer', fontWeight: 600 }}>
              Sign Out
            </button>
          </div>
        </div>
        <AdminUserManagement user={user} />
      </div>
    );
  }

  // Doctor Role: If current patient record has not been 2FA verified in this session, show the 2-step gate
  if (user.role === 'DOCTOR' && !verifiedPatientCodes.has(selectedPatientCode)) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', color: '#0f172a' }}>
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
      <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', padding: '40px 20px' }}>
        <ErrorMessage message={error || `Patient ${selectedPatientCode} records unavailable.`} onRetry={refetch} />
      </div>
    );
  }

  // Patient Login Mode: Exclusively Chatbot Interface for Informational Use Only
  if (user.role === 'PATIENT') {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', color: '#0f172a' }}>
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

  // Caregiver Login Mode: Exclusively Caregiver Observation & Clarification Notes Portal
  if (user.role === 'CAREGIVER') {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', color: '#0f172a' }}>
        <Header
          patient={data.patient}
          user={user}
          authorizedPatients={authorizedPatients}
          selectedPatientCode={selectedPatientCode}
          onSelectPatient={setSelectedPatientCode}
          onLogout={onLogout}
        />
        <main style={{ flex: 1 }}>
          <CaregiverNotesTab data={data} user={user} onObservationSaved={refetch} />
        </main>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', color: '#0f172a' }}>
      {/* Top Fixed Header */}
      <Header
        patient={data.patient}
        user={user}
        authorizedPatients={authorizedPatients}
        selectedPatientCode={selectedPatientCode}
        onSelectPatient={(code) => {
          setSelectedPatientCode(code);
        }}
        onLogout={onLogout}
        onOpen2FA={() => setShow2FAModal(true)}
      />

      {/* 2-Step Verification Modal if doctor clicks Unlock Patient */}
      {show2FAModal && (
        <DoctorPatientAccessGate
          isModal={true}
          initialPatientCode={selectedPatientCode}
          onPatientUnlocked={handlePatientUnlocked}
          onCancel={() => setShow2FAModal(false)}
        />
      )}

      {/* Full-Width Tab Navigation Subheader */}
      <div
        style={{
          backgroundColor: '#ffffff',
          borderBottom: '1px solid #e2e8f0',
          padding: '8px 24px',
          boxShadow: '0 1px 2px rgba(0, 0, 0, 0.03)',
          zIndex: 30,
        }}
      >
        <div
          style={{
            maxWidth: '1440px',
            margin: '0 auto',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {/* Tab 1: AI Assistant (Full Screen) */}
            <button
              onClick={() => setActiveTab('assistant')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 18px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: activeTab === 'assistant' ? '#0284c7' : 'transparent',
                color: activeTab === 'assistant' ? '#ffffff' : '#475569',
                fontWeight: 700,
                fontSize: '13px',
                cursor: 'pointer',
                transition: 'all 0.15s ease-in-out',
                boxShadow: activeTab === 'assistant' ? '0 2px 4px rgba(2, 132, 199, 0.25)' : 'none',
              }}
            >
              <MessageSquare size={16} />
              <span>Clinical AI Assistant</span>
              <span
                style={{
                  fontSize: '10px',
                  padding: '2px 6px',
                  borderRadius: '10px',
                  backgroundColor: activeTab === 'assistant' ? 'rgba(255, 255, 255, 0.25)' : '#e0f2fe',
                  color: activeTab === 'assistant' ? '#ffffff' : '#0369a1',
                }}
              >
                Chat
              </span>
            </button>

            {/* Tab 2: About Patient (Longitudinal Records) */}
            <button
              onClick={() => setActiveTab('records')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 18px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: activeTab === 'records' ? '#0284c7' : 'transparent',
                color: activeTab === 'records' ? '#ffffff' : '#475569',
                fontWeight: 700,
                fontSize: '13px',
                cursor: 'pointer',
                transition: 'all 0.15s ease-in-out',
                boxShadow: activeTab === 'records' ? '0 2px 4px rgba(2, 132, 199, 0.25)' : 'none',
              }}
            >
              <ClipboardList size={16} />
              <span>About Patient &amp; Longitudinal Records</span>
              <span
                style={{
                  fontSize: '10px',
                  padding: '2px 6px',
                  borderRadius: '10px',
                  backgroundColor: activeTab === 'records' ? 'rgba(255, 255, 255, 0.25)' : '#f1f5f9',
                  color: activeTab === 'records' ? '#ffffff' : '#475569',
                }}
              >
                6 Domains
              </span>
            </button>

            {/* Tab 3: Clinical Entry (Diagnosis & Prescriptions) */}
            <button
              onClick={() => setActiveTab('entry')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 18px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: activeTab === 'entry' ? '#0284c7' : 'transparent',
                color: activeTab === 'entry' ? '#ffffff' : '#475569',
                fontWeight: 700,
                fontSize: '13px',
                cursor: 'pointer',
                transition: 'all 0.15s ease-in-out',
                boxShadow: activeTab === 'entry' ? '0 2px 4px rgba(2, 132, 199, 0.25)' : 'none',
              }}
            >
              <PenSquare size={16} />
              <span>Enter Diagnosis &amp; Prescriptions</span>
              <span
                style={{
                  fontSize: '10px',
                  padding: '2px 6px',
                  borderRadius: '10px',
                  backgroundColor: activeTab === 'entry' ? 'rgba(255, 255, 255, 0.25)' : '#f0fdf4',
                  color: activeTab === 'entry' ? '#ffffff' : '#166534',
                }}
              >
                Markdown Export
              </span>
            </button>
          </div>

          <div style={{ fontSize: '12px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontWeight: 600 }}>Active Patient:</span>
            <span style={{ fontWeight: 700, color: '#0f172a' }}>{data.patient.name}</span>
            <span style={{ fontFamily: 'monospace', backgroundColor: '#e2e8f0', padding: '1px 6px', borderRadius: '4px', fontSize: '11px' }}>
              {data.patient.patient_code}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content: Full Screen for Assistant, Centered Container for Records & Entry */}
      {activeTab === 'assistant' ? (
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', height: 'calc(100vh - 118px)', overflow: 'hidden' }}>
          <ClinicalAssistantTab
            data={data}
            user={user}
            onSelectEvidence={handleOpenEvidence}
            onSwitchToPatientRecords={() => setActiveTab('records')}
          />
        </main>
      ) : (
        <main style={{ maxWidth: '1440px', margin: '0 auto', padding: '20px 24px 40px 24px', width: '100%', boxSizing: 'border-box' }}>
          {activeTab === 'records' && (
            <PatientRecordsTab
              data={data}
              onOpenWhy={(change) => setSelectedWhyChange(change)}
              onSelectEvidence={handleOpenEvidence}
            />
          )}

          {activeTab === 'entry' && (
            <DoctorClinicalEntryTab
              data={data}
              onEntrySaved={refetch}
              onSelectEvidence={handleOpenEvidence}
            />
          )}

          {/* Footer Note */}
          <footer
            style={{
              textAlign: 'center',
              padding: '28px 0 16px 0',
              borderTop: '1px solid #e2e8f0',
              color: '#94a3b8',
              fontSize: '12px',
              marginTop: '32px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', marginBottom: '4px' }}>
              <ShieldCheck size={14} style={{ color: '#0284c7' }} />
              <span>EvoCare Clinical Intelligence Station • Doctor Portal • Multi-Tab Clinical Workflow</span>
            </div>
            <div>Patient {data.patient.patient_code} ({data.patient.name}) • Synthetic Demo Dataset</div>
          </footer>
        </main>
      )}

      {/* Modals & Drawers */}
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

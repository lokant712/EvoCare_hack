import React, { useState, useEffect } from 'react';
import { usePatient } from '../hooks/usePatient';
import { Header } from '../components/layout/Header';
import { PatientRecordsTab } from '../components/patient/PatientRecordsTab';
import { ClinicalAssistantTab } from '../components/assistant/ClinicalAssistantTab';
import { DoctorClinicalEntryTab } from '../components/clinical/DoctorClinicalEntryTab';
import { PatientCompanionTab } from '../components/patient/PatientCompanionTab';
import { CaregiverNotesTab } from '../components/caregiver/CaregiverNotesTab';
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

  const { data, loading, error, refetch } = usePatient(selectedPatientCode);
  const [selectedWhyChange, setSelectedWhyChange] = useState<RecentChangeItem | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceDetailItem | null>(null);

  // Fetch authorized patient list from backend
  useEffect(() => {
    authService.getAuthorizedPatients().then((patients) => {
      setAuthorizedPatients(patients);
      if (patients.length > 0) {
        setSelectedPatientCode(patients[0].patient_code);
      }
    });
  }, []);

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

  // Admin Login Mode: System Administration Panel (no patient record required)
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
              <div style={{ fontSize: '11px', color: '#94a3b8' }}>System Administration & Oversight</div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '13px', color: '#94a3b8' }}>Logged in as <b style={{ color: '#f8fafc' }}>{user.full_name || user.username}</b></span>
            <button onClick={onLogout} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid #475569', backgroundColor: 'transparent', color: '#94a3b8', fontSize: '12px', cursor: 'pointer', fontWeight: 600 }}>
              Sign Out
            </button>
          </div>
        </div>

        {/* Admin Body */}
        <div style={{ maxWidth: '960px', margin: '40px auto', padding: '0 24px' }}>
          {/* Welcome Banner */}
          <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '24px 28px', marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '16px' }}>
              <div style={{ width: '48px', height: '48px', borderRadius: '10px', backgroundColor: '#fef3c7', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ShieldCheck size={24} color="#d97706" />
              </div>
              <div>
                <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: '#0f172a' }}>System Administrator Dashboard</h2>
                <p style={{ margin: '4px 0 0', fontSize: '13px', color: '#64748b' }}>EvoCare Longitudinal Health Memory Platform — Admin Oversight</p>
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
              {[
                { label: 'Active Patients', value: '2', color: '#0ea5e9' },
                { label: 'Active Users', value: '5', color: '#059669' },
                { label: 'System Status', value: 'LIVE', color: '#10b981' },
              ].map(({ label, value, color }) => (
                <div key={label} style={{ backgroundColor: '#f8fafc', borderRadius: '8px', padding: '14px 16px', border: '1px solid #e2e8f0', textAlign: 'center' }}>
                  <div style={{ fontSize: '24px', fontWeight: 800, color }}>{value}</div>
                  <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>{label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Demo Accounts */}
          <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '24px 28px', marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
            <h3 style={{ margin: '0 0 16px', fontSize: '15px', fontWeight: 700, color: '#0f172a' }}>Demo Account Directory</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ backgroundColor: '#f8fafc' }}>
                  {['Username', 'Password', 'Role', 'Access'].map(h => (
                    <th key={h} style={{ padding: '8px 12px', textAlign: 'left', fontWeight: 600, color: '#475569', borderBottom: '1px solid #e2e8f0' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  { username: 'doctor.demo', password: 'DoctorPass123!', role: 'DOCTOR', access: 'Patient P001 — Full Clinical Dashboard' },
                  { username: 'doctor.other', password: 'DoctorPass123!', role: 'DOCTOR', access: 'Patient P002 — Isolation Test' },
                  { username: 'caregiver.demo', password: 'CaregiverPass123!', role: 'CAREGIVER', access: 'Patient P001 — Caregiver Notes Portal' },
                  { username: 'patient.demo', password: 'PatientPass123!', role: 'PATIENT', access: 'Patient P001 — Informational Chatbot Only' },
                  { username: 'admin.demo', password: 'AdminPass123!', role: 'ADMIN', access: 'System Administration Console' },
                ].map(row => (
                  <tr key={row.username} style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '10px 12px', fontFamily: 'monospace', color: '#0f172a', fontWeight: 600 }}>{row.username}</td>
                    <td style={{ padding: '10px 12px', fontFamily: 'monospace', color: '#475569' }}>{row.password}</td>
                    <td style={{ padding: '10px 12px' }}>
                      <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '11px', fontWeight: 700,
                        backgroundColor: row.role === 'DOCTOR' ? '#eff6ff' : row.role === 'CAREGIVER' ? '#f0fdf4' : row.role === 'PATIENT' ? '#fdf4ff' : '#fffbeb',
                        color: row.role === 'DOCTOR' ? '#1d4ed8' : row.role === 'CAREGIVER' ? '#065f46' : row.role === 'PATIENT' ? '#7e22ce' : '#92400e'
                      }}>{row.role}</span>
                    </td>
                    <td style={{ padding: '10px 12px', color: '#64748b' }}>{row.access}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Security Note */}
          <div style={{ backgroundColor: '#fef9c3', border: '1px solid #fde68a', borderRadius: '10px', padding: '14px 18px', fontSize: '12px', color: '#78350f' }}>
            <b>⚠ Admin Notice:</b> This console is for system oversight only. Patient clinical records, caregiver observations, and diagnostic data must be accessed through the respective role-specific portals. All actions are audit-logged.
          </div>
        </div>
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
        onSelectPatient={setSelectedPatientCode}
        onLogout={onLogout}
      />

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

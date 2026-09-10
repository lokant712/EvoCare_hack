import React from 'react';
import { Activity, User, MapPin, Calendar, Lock, LogOut, ChevronDown, Shield, KeyRound } from 'lucide-react';
import { PatientDemographics } from '../../types';
import { AuthUser, AuthorizedPatient } from '../../services/auth';

interface HeaderProps {
  patient: PatientDemographics;
  user: AuthUser;
  authorizedPatients: AuthorizedPatient[];
  selectedPatientCode: string;
  onSelectPatient: (code: string) => void;
  onLogout: () => void;
  onOpen2FA?: () => void;
}

const ROLE_COLORS: Record<string, string> = {
  DOCTOR: '#0284c7',
  CAREGIVER: '#059669',
  ADMIN: '#7c3aed',
  PATIENT: '#d97706',
};

export const Header: React.FC<HeaderProps> = ({
  patient,
  user,
  authorizedPatients,
  selectedPatientCode,
  onSelectPatient,
  onLogout,
  onOpen2FA,
}) => {
  const roleColor = ROLE_COLORS[user.role] || '#64748b';

  return (
    <header
      style={{
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e2e8f0',
        padding: '12px 24px',
        position: 'sticky',
        top: 0,
        zIndex: 40,
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
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
        {/* Logo & Product Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              backgroundColor: '#0284c7',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              boxShadow: '0 2px 4px rgba(2, 132, 199, 0.25)',
              flexShrink: 0,
            }}
          >
            <Activity size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 style={{ fontSize: '17px', fontWeight: 700, color: '#0f172a', margin: 0, letterSpacing: '-0.02em' }}>
                EvoCare
              </h1>
              <span
                style={{
                  fontSize: '10px',
                  fontWeight: 600,
                  backgroundColor: '#f1f5f9',
                  color: '#475569',
                  padding: '2px 6px',
                  borderRadius: '4px',
                }}
              >
                Clinical Intelligence
              </span>
            </div>
            <div style={{ fontSize: '11px', color: '#94a3b8' }}>
              Longitudinal Patient Memory
            </div>
          </div>
        </div>

        {/* Centre: Patient Identity */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            backgroundColor: '#f8fafc',
            padding: '8px 14px',
            borderRadius: '10px',
            border: '1px solid #e2e8f0',
            flex: '0 1 auto',
          }}
        >
          {/* Patient avatar */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                backgroundColor: '#e0f2fe',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#0284c7',
                flexShrink: 0,
              }}
            >
              <User size={16} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a' }}>{patient.name}</span>
                <span
                  style={{
                    fontSize: '11px',
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontWeight: 600,
                    backgroundColor: '#0284c7',
                    color: '#ffffff',
                    padding: '1px 6px',
                    borderRadius: '4px',
                  }}
                >
                  {patient.patient_code}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '11px', color: '#64748b' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                  <Calendar size={11} />
                  {patient.age}y · {patient.sex}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                  <MapPin size={11} />
                  {patient.location}
                </span>
              </div>
            </div>
          </div>

          {/* Patient switcher — only shown if user has multiple authorized patients */}
          {authorizedPatients.length > 1 && (
            <div style={{ display: 'flex', gap: '4px' }}>
              {authorizedPatients.map((p) => (
                <button
                  key={p.patient_code}
                  id={`evocare-patient-switch-${p.patient_code}`}
                  onClick={() => onSelectPatient(p.patient_code)}
                  style={{
                    padding: '4px 8px',
                    borderRadius: '5px',
                    border: '1px solid',
                    borderColor: selectedPatientCode === p.patient_code ? '#0284c7' : '#e2e8f0',
                    backgroundColor: selectedPatientCode === p.patient_code ? '#e0f2fe' : '#ffffff',
                    color: selectedPatientCode === p.patient_code ? '#0284c7' : '#64748b',
                    fontSize: '11px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  {p.patient_code}
                  {selectedPatientCode === p.patient_code && <ChevronDown size={11} />}
                </button>
              ))}
            </div>
          )}

          {/* Badges & 2FA Button */}
          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
            {user.role === 'DOCTOR' && onOpen2FA && (
              <button
                id="evocare-open-2fa-btn"
                type="button"
                onClick={onOpen2FA}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '4px 10px',
                  borderRadius: '5px',
                  border: '1px solid #bae6fd',
                  backgroundColor: '#f0f9ff',
                  color: '#0369a1',
                  fontSize: '11px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <KeyRound size={12} />
                <span>+ Unlock Patient (2FA)</span>
              </button>
            )}
            <div
              style={{
                padding: '3px 8px',
                backgroundColor: '#fef3c7',
                color: '#92400e',
                border: '1px solid #fde68a',
                borderRadius: '5px',
                fontSize: '10px',
                fontWeight: 700,
                letterSpacing: '0.04em',
                whiteSpace: 'nowrap',
              }}
            >
              SYNTHETIC DEMO
            </div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '3px',
                padding: '3px 7px',
                backgroundColor: '#f1f5f9',
                color: '#475569',
                borderRadius: '5px',
                fontSize: '10px',
                fontWeight: 600,
              }}
            >
              <Lock size={10} />
              READ-ONLY
            </div>
          </div>
        </div>

        {/* Right: Logged-in user + logout */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                backgroundColor: roleColor + '18',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: roleColor,
                flexShrink: 0,
              }}
            >
              <Shield size={15} />
            </div>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a', lineHeight: 1.2 }}>
                {user.full_name.split('(')[0].trim()}
              </div>
              <div
                style={{
                  fontSize: '10px',
                  fontWeight: 700,
                  color: roleColor,
                  letterSpacing: '0.04em',
                }}
              >
                {user.role}
              </div>
            </div>
          </div>

          <button
            id="evocare-logout-button"
            onClick={onLogout}
            title="Sign out"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              padding: '7px 12px',
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '7px',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: 600,
              color: '#475569',
              transition: 'all 0.15s',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = '#fee2e2';
              (e.currentTarget as HTMLButtonElement).style.borderColor = '#fca5a5';
              (e.currentTarget as HTMLButtonElement).style.color = '#dc2626';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = '#f8fafc';
              (e.currentTarget as HTMLButtonElement).style.borderColor = '#e2e8f0';
              (e.currentTarget as HTMLButtonElement).style.color = '#475569';
            }}
          >
            <LogOut size={13} />
            Sign out
          </button>
        </div>
      </div>
    </header>
  );
};

import React from 'react';
import { Activity, User, MapPin, Calendar, Lock, LogOut, ChevronDown, Shield, KeyRound, Clock } from 'lucide-react';
import { PatientDemographics } from '../../types';
import { AuthUser, AuthorizedPatient } from '../../services/auth';
import { ThemeToggle } from '../common/ThemeToggle';

interface HeaderProps {
  patient: PatientDemographics;
  user: AuthUser;
  authorizedPatients: AuthorizedPatient[];
  selectedPatientCode: string;
  onSelectPatient: (code: string) => void;
  onLogout: () => void;
  onOpen2FA?: () => void;
  onLockSession?: () => void;
  sessionRemainingSeconds?: number | null;
}

const ROLE_COLORS: Record<string, string> = {
  DOCTOR: 'var(--color-accent)',
  CAREGIVER: 'var(--color-success)',
  ADMIN: 'var(--color-plum)',
  PATIENT: 'var(--color-warning)',
};

export const Header: React.FC<HeaderProps> = ({
  patient,
  user,
  authorizedPatients,
  selectedPatientCode,
  onSelectPatient,
  onLogout,
  onOpen2FA,
  onLockSession,
  sessionRemainingSeconds,
}) => {
  const roleColor = ROLE_COLORS[user.role] || 'var(--color-text-muted)';

  return (
    <header
      style={{
        backgroundColor: 'var(--color-surface)',
        borderBottom: '1px solid var(--color-border)',
        padding: 0,
        position: 'sticky',
        top: 0,
        zIndex: 40,
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
      }}
    >
      {/* Prominent Doctor Active Session Notice Bar at the Very Top */}
      {user.role === 'DOCTOR' && sessionRemainingSeconds !== undefined && sessionRemainingSeconds !== null && (
        <div
          id="evocare-top-session-bar"
          style={{
            backgroundColor: sessionRemainingSeconds < 120 ? 'var(--color-danger-dark)' : 'var(--color-accent-dark)',
            color: 'var(--color-surface)',
            padding: '7px 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '12px',
            fontWeight: 500,
            borderBottom: '1px solid',
            borderColor: sessionRemainingSeconds < 120 ? 'var(--color-danger-dark)' : 'var(--color-accent-dark)',
            transition: 'background-color 0.3s ease',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                backgroundColor: sessionRemainingSeconds < 120 ? 'var(--color-danger)' : 'var(--color-accent)',
                padding: '2px 9px',
                borderRadius: '4px',
                fontWeight: 700,
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: '13px',
                letterSpacing: '0.04em',
                boxShadow: sessionRemainingSeconds < 120 ? '0 0 8px rgba(179, 76, 64, 0.6)' : 'none',
              }}
            >
              <Clock size={13} />
              <span>
                {Math.floor(sessionRemainingSeconds / 60).toString().padStart(2, '0')}:
                {(sessionRemainingSeconds % 60).toString().padStart(2, '0')}
              </span>
            </div>
            <span>
              <strong>Doctor Active Session ({patient.name} &bull; {patient.patient_code})</strong>
              {sessionRemainingSeconds < 120
                ? ' — ⚠️ Warning: Session expiring soon! Patient record will auto-lock to prevent unauthorized access.'
                : ' — Auto-locks after 10 mins of access to prevent chart misuse.'}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {onOpen2FA && (
              <button
                type="button"
                onClick={onOpen2FA}
                style={{
                  padding: '3px 10px',
                  borderRadius: '4px',
                  backgroundColor: 'rgba(255, 255, 255, 0.18)',
                  border: '1px solid rgba(255, 255, 255, 0.35)',
                  color: 'var(--color-surface)',
                  fontSize: '11px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <KeyRound size={11} />
                Switch Patient (2FA)
              </button>
            )}
            {onLockSession && (
              <button
                type="button"
                onClick={onLockSession}
                style={{
                  padding: '3px 10px',
                  borderRadius: '4px',
                  backgroundColor: 'var(--color-danger)',
                  border: 'none',
                  color: 'var(--color-surface)',
                  fontSize: '11px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <Lock size={11} />
                Lock Record
              </button>
            )}
          </div>
        </div>
      )}

      <div
        style={{
          maxWidth: '1440px',
          margin: '0 auto',
          padding: '12px 24px',
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
              backgroundColor: 'var(--color-accent)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--color-surface)',
              boxShadow: '0 2px 4px rgba(13, 110, 100, 0.25)',
              flexShrink: 0,
            }}
          >
            <Activity size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 style={{ fontSize: '17px', fontWeight: 700, color: 'var(--color-text-main)', margin: 0, letterSpacing: '-0.02em' }}>
                EvoCare
              </h1>
              <span
                style={{
                  fontSize: '10px',
                  fontWeight: 600,
                  backgroundColor: 'var(--color-surface-alt)',
                  color: 'var(--color-text-secondary)',
                  padding: '2px 6px',
                  borderRadius: '4px',
                }}
              >
                Clinical Intelligence
              </span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-faint)' }}>
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
            backgroundColor: 'var(--color-bg)',
            padding: '8px 14px',
            borderRadius: '10px',
            border: '1px solid var(--color-border)',
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
                backgroundColor: 'var(--color-accent-soft)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--color-accent)',
                flexShrink: 0,
              }}
            >
              <User size={16} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--color-text-main)' }}>{patient.name}</span>
                <span
                  style={{
                    fontSize: '11px',
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontWeight: 600,
                    backgroundColor: 'var(--color-accent)',
                    color: 'var(--color-surface)',
                    padding: '1px 6px',
                    borderRadius: '4px',
                  }}
                >
                  {patient.patient_code}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '11px', color: 'var(--color-text-muted)' }}>
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

          {/* Patient switcher — only shown for non-doctor roles if user has multiple authorized patients */}
          {user.role !== 'DOCTOR' && authorizedPatients.length > 1 && (
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
                    borderColor: selectedPatientCode === p.patient_code ? 'var(--color-accent)' : 'var(--color-border)',
                    backgroundColor: selectedPatientCode === p.patient_code ? 'var(--color-accent-soft)' : 'var(--color-surface)',
                    color: selectedPatientCode === p.patient_code ? 'var(--color-accent)' : 'var(--color-text-muted)',
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

          {/* Badges & 2FA Button & 10-min Session Timer */}
          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
            {user.role === 'DOCTOR' && sessionRemainingSeconds !== undefined && sessionRemainingSeconds !== null && (
              <div
                id="evocare-session-timer-badge"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '3px 8px',
                  borderRadius: '5px',
                  backgroundColor: sessionRemainingSeconds < 120 ? 'var(--color-danger-soft)' : 'var(--color-success-soft)',
                  border: '1px solid',
                  borderColor: sessionRemainingSeconds < 120 ? 'var(--color-danger-border)' : 'var(--color-success-border)',
                  color: sessionRemainingSeconds < 120 ? 'var(--color-danger-dark)' : 'var(--color-success-dark)',
                  fontSize: '11px',
                  fontWeight: 700,
                  fontFamily: "'IBM Plex Mono', monospace",
                }}
              >
                <Clock size={11} />
                <span>
                  {Math.floor(sessionRemainingSeconds / 60).toString().padStart(2, '0')}:
                  {(sessionRemainingSeconds % 60).toString().padStart(2, '0')}
                </span>
                <span style={{ fontSize: '10px', opacity: 0.85, fontFamily: 'var(--font-sans)' }}>
                  {sessionRemainingSeconds < 120 ? 'Expiring' : 'Session (10m)'}
                </span>
              </div>
            )}

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
                  border: '1px solid var(--color-accent-border)',
                  backgroundColor: 'var(--color-accent-soft)',
                  color: 'var(--color-accent-dark)',
                  fontSize: '11px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <KeyRound size={12} />
                <span>Switch Patient (2FA)</span>
              </button>
            )}
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
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-main)', lineHeight: 1.2 }}>
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

          <ThemeToggle size="sm" />

          <button
            id="evocare-logout-button"
            onClick={onLogout}
            title="Sign out"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              padding: '7px 12px',
              backgroundColor: 'var(--color-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: '7px',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: 600,
              color: 'var(--color-text-secondary)',
              transition: 'all 0.15s',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'var(--color-danger-soft)';
              (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--color-danger-border)';
              (e.currentTarget as HTMLButtonElement).style.color = 'var(--color-danger)';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'var(--color-bg)';
              (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--color-border)';
              (e.currentTarget as HTMLButtonElement).style.color = 'var(--color-text-secondary)';
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

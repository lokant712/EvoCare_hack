import React, { useState } from 'react';
import {
  Activity,
  Lock,
  User,
  AlertCircle,
  ShieldCheck,
  Eye,
  EyeOff,
  Stethoscope,
  HeartHandshake,
  MessageSquare,
  Shield,
  ArrowLeft,
  ArrowRight,
  LogIn,
  Sparkles,
  KeyRound,
  LucideIcon,
} from 'lucide-react';
import { authService, AuthUser } from '../services/auth';
import { ThemeToggle } from '../components/common/ThemeToggle';
import { CareNetworkScene } from '../components/common/CareNetworkScene';

interface LoginPageProps {
  onLoginSuccess: (user: AuthUser) => void;
}

type RoleType = 'DOCTOR' | 'CAREGIVER' | 'PATIENT' | 'ADMIN';

interface RoleMetadata {
  id: RoleType;
  title: string;
  badge: string;
  subtitle: string;
  description: string;
  accent: string;
  accentSoft: string;
  accentBorder: string;
  icon: LucideIcon;
  demoUser: string;
  demoPass: string;
  demoRoleDesc: string;
}

const ROLES: RoleMetadata[] = [
  {
    id: 'DOCTOR',
    title: 'Doctor',
    badge: 'Physicians & clinicians',
    subtitle: 'Clinical decision support',
    description: 'Longitudinal health memory, diagnostic reasoning, 2FA patient verification, and differential analysis.',
    accent: 'var(--color-accent)',
    accentSoft: 'var(--color-accent-soft)',
    accentBorder: 'var(--color-accent-border)',
    icon: Stethoscope,
    demoUser: 'doctor.demo',
    demoPass: 'DoctorPass123!',
    demoRoleDesc: 'Full clinical reasoning station with 2FA email consent security.',
  },
  {
    id: 'CAREGIVER',
    title: 'Caregiver',
    badge: 'Family & caretakers',
    subtitle: 'Observations & daily logs',
    description: 'Log patient daily observations, behavior, nutrition, and manage patient connection requests.',
    accent: 'var(--color-warning-dark)',
    accentSoft: 'var(--color-warning-soft)',
    accentBorder: 'var(--color-warning-border)',
    icon: HeartHandshake,
    demoUser: 'caregiver.demo',
    demoPass: 'CaregiverPass123!',
    demoRoleDesc: 'Submit vital observations and accept patient pairing invites.',
  },
  {
    id: 'PATIENT',
    title: 'Patient',
    badge: 'Patients & individuals',
    subtitle: 'AI health companion',
    description: 'Engage with your personalized conversational health companion, check symptoms, and pair caretakers.',
    accent: 'var(--color-success)',
    accentSoft: 'var(--color-success-soft)',
    accentBorder: 'var(--color-success-border)',
    icon: MessageSquare,
    demoUser: 'patient.demo',
    demoPass: 'PatientPass123!',
    demoRoleDesc: 'Conversational wellness companion and caregiver connection management.',
  },
  {
    id: 'ADMIN',
    title: 'Administrator',
    badge: 'System & governance',
    subtitle: 'Access & user management',
    description: 'Manage users, clinical roles, system security parameters, and cross-provider access controls.',
    accent: 'var(--color-plum-dark)',
    accentSoft: 'var(--color-plum-soft)',
    accentBorder: 'var(--color-plum-border)',
    icon: Shield,
    demoUser: 'admin.demo',
    demoPass: 'AdminPass123!',
    demoRoleDesc: 'Administrative controls and provider authorization management.',
  },
];

const BrandMark: React.FC<{ size?: number }> = ({ size = 38 }) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: '50%',
      background: 'linear-gradient(155deg, var(--color-accent-bright) 0%, var(--color-accent-dark) 100%)',
      border: '1px solid rgba(255,255,255,0.25)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: '#ffffff',
      boxShadow: '0 6px 16px -4px rgba(8, 79, 71, 0.55)',
      flexShrink: 0,
    }}
  >
    <Activity size={Math.round(size * 0.55)} />
  </div>
);

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [selectedRole, setSelectedRole] = useState<RoleType | null>(null);
  const [hoveredRole, setHoveredRole] = useState<RoleType | null>(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentRoleConfig = ROLES.find((r) => r.id === selectedRole);

  const handleSelectRole = (role: RoleType) => {
    setSelectedRole(role);
    const config = ROLES.find((r) => r.id === role);
    if (config) {
      setUsername(config.demoUser);
      setPassword(config.demoPass);
    }
    setError(null);
  };

  const handleBackToLanding = () => {
    setSelectedRole(null);
    setUsername('');
    setPassword('');
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const user = await authService.login(username.trim(), password);
      onLoginSuccess(user);
    } catch (err: any) {
      setError(err?.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
    setError(null);
  };

  const shellStyle: React.CSSProperties = {
    minHeight: '100dvh',
    backgroundColor: 'var(--color-bg)',
    display: 'flex',
    flexDirection: 'column',
  };

  // STEP 1: ROLE LANDING — asymmetric split hero
  if (!selectedRole) {
    return (
      <div style={shellStyle}>
        <div
          style={{
            flex: 1,
            display: 'grid',
            gridTemplateColumns: 'minmax(320px, 1fr) minmax(0, 1.55fr)',
            minHeight: '100dvh',
          }}
        >
          {/* Left: editorial brand panel */}
          <div
            className="evocare-grain"
            style={{
              position: 'relative',
              background: 'linear-gradient(165deg, var(--color-accent) 0%, var(--color-accent-dark) 55%, var(--color-accent-dark) 100%)',
              color: '#f4f1ea',
              padding: '48px 40px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              overflow: 'hidden',
            }}
          >
            <CareNetworkScene />

            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              <BrandMark />
              <div>
                <div style={{ fontSize: '20px', fontWeight: 800, letterSpacing: '-0.02em' }}>EvoCare</div>
                <div style={{ fontSize: '12px', opacity: 0.75, fontWeight: 500 }}>Clinical intelligence platform</div>
              </div>
            </div>

            <div style={{ maxWidth: '440px' }}>
              <div
                style={{
                  fontSize: '12px',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.12em',
                  opacity: 0.65,
                  marginBottom: '18px',
                }}
              >
                Evolving Longitudinal Care
              </div>
              <h1
                style={{
                  fontSize: 'clamp(28px, 3.4vw, 40px)',
                  fontWeight: 700,
                  lineHeight: 1.15,
                  letterSpacing: '-0.03em',
                  margin: '0 0 20px 0',
                }}
              >
                One longitudinal record, read the same way by everyone caring for a patient.
              </h1>
              <p style={{ fontSize: '14.5px', lineHeight: 1.7, opacity: 0.8, fontWeight: 400, margin: 0 }}>
                Doctors, caregivers, patients, and administrators work from a single evidence-linked
                timeline — every claim traceable back to who observed it and when.
              </p>
            </div>

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '9px',
                fontSize: '12.5px',
                opacity: 0.75,
                borderTop: '1px solid rgba(244,241,234,0.18)',
                paddingTop: '18px',
              }}
            >
              <ShieldCheck size={15} />
              <span>Multi-role access control &middot; 2FA patient memory gate &middot; audited clinical platform</span>
            </div>
          </div>

          {/* Right: role selection */}
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              padding: '56px clamp(28px, 6vw, 88px)',
            }}
          >
            <div style={{ maxWidth: '620px', width: '100%', marginLeft: 'auto', marginRight: 'auto' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px' }}>
                <div>
                  <h2
                    style={{
                      fontSize: '15px',
                      fontWeight: 700,
                      color: 'var(--color-text-main)',
                      margin: '0 0 6px 0',
                    }}
                  >
                    Continue as
                  </h2>
                </div>
                <ThemeToggle />
              </div>
              <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: '0 0 28px 0' }}>
                Select the portal that matches your role to reach a dedicated, role-scoped sign-in.
              </p>

              <div className="evocare-stagger" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {ROLES.map((role) => {
                  const Icon = role.icon;
                  const isHovered = hoveredRole === role.id;
                  return (
                    <button
                      key={role.id}
                      id={`evocare-select-role-${role.id.toLowerCase()}`}
                      type="button"
                      onClick={() => handleSelectRole(role.id)}
                      onMouseEnter={() => setHoveredRole(role.id)}
                      onMouseLeave={() => setHoveredRole(null)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '16px',
                        width: '100%',
                        textAlign: 'left',
                        backgroundColor: 'var(--color-surface)',
                        border: `1px solid ${isHovered ? role.accent : 'var(--color-border)'}`,
                        borderRadius: 'var(--radius-md)',
                        padding: '16px 18px',
                        cursor: 'pointer',
                        transform: isHovered ? 'translateX(4px)' : 'translateX(0)',
                        boxShadow: isHovered ? '0 10px 28px -12px rgba(28,26,20,0.22)' : 'var(--shadow-sm)',
                      }}
                    >
                      <div
                        style={{
                          width: '44px',
                          height: '44px',
                          borderRadius: 'var(--radius-sm)',
                          backgroundColor: role.accentSoft,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: role.accent,
                          flexShrink: 0,
                        }}
                      >
                        <Icon size={21} />
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', flexWrap: 'wrap' }}>
                          <span style={{ fontSize: '15.5px', fontWeight: 700, color: 'var(--color-text-main)' }}>
                            {role.title}
                          </span>
                          <span style={{ fontSize: '11.5px', color: 'var(--color-text-muted)' }}>{role.subtitle}</span>
                        </div>
                        <div
                          style={{
                            fontSize: '12.5px',
                            color: 'var(--color-text-muted)',
                            marginTop: '2px',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {role.description}
                        </div>
                      </div>
                      <ArrowRight
                        size={17}
                        style={{
                          color: role.accent,
                          flexShrink: 0,
                          transform: isHovered ? 'translateX(2px)' : 'translateX(0)',
                          transition: 'transform 0.15s ease',
                        }}
                      />
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // STEP 2: ROLE-SPECIFIC SIGN-IN
  const Icon = currentRoleConfig?.icon || Lock;
  const accent = currentRoleConfig?.accent || 'var(--color-accent)';

  return (
    <div style={shellStyle}>
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '32px 24px',
          position: 'relative',
        }}
      >
        <button
          id="evocare-back-to-roles"
          type="button"
          onClick={handleBackToLanding}
          style={{
            position: 'absolute',
            top: '28px',
            left: '28px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: 'transparent',
            border: '1px solid var(--color-border)',
            color: 'var(--color-text-muted)',
            fontSize: '12.5px',
            fontWeight: 600,
            cursor: 'pointer',
            padding: '7px 14px',
            borderRadius: 'var(--radius-sm)',
          }}
        >
          <ArrowLeft size={14} />
          <span>Change role</span>
        </button>

        <div style={{ position: 'absolute', top: '28px', right: '28px' }}>
          <ThemeToggle />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '28px' }}>
          <BrandMark size={32} />
          <span style={{ fontSize: '17px', fontWeight: 800, letterSpacing: '-0.02em', color: 'var(--color-text-main)' }}>
            EvoCare
          </span>
        </div>

        <div
          style={{
            backgroundColor: 'var(--color-surface)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--color-border)',
            borderTop: `3px solid ${accent}`,
            padding: '36px',
            width: '100%',
            maxWidth: '440px',
            boxShadow: 'var(--shadow-lg)',
          }}
        >
          {/* Role Header Banner */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '26px' }}>
            <div
              style={{
                width: '46px',
                height: '46px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: currentRoleConfig?.accentSoft,
                border: `1px solid ${currentRoleConfig?.accentBorder}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: accent,
                flexShrink: 0,
              }}
            >
              <Icon size={23} />
            </div>
            <div>
              <div
                style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  color: accent,
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                }}
              >
                {currentRoleConfig?.badge}
              </div>
              <h2
                style={{
                  fontSize: '21px',
                  fontWeight: 700,
                  color: 'var(--color-text-main)',
                  margin: '3px 0 0 0',
                }}
              >
                {currentRoleConfig?.title} sign in
              </h2>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <div
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '8px',
                backgroundColor: 'var(--color-danger-soft)',
                border: '1px solid var(--color-danger-border)',
                borderRadius: 'var(--radius-sm)',
                padding: '10px 12px',
                marginBottom: '20px',
              }}
            >
              <AlertCircle size={16} style={{ color: 'var(--color-danger)', flexShrink: 0, marginTop: '1px' }} />
              <span style={{ fontSize: '13px', color: 'var(--color-danger)' }}>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Username */}
            <div style={{ marginBottom: '16px' }}>
              <label
                htmlFor="evocare-username"
                style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '6px' }}
              >
                User ID / Username
              </label>
              <div style={{ position: 'relative' }}>
                <User
                  size={15}
                  style={{
                    position: 'absolute',
                    left: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--color-text-faint)',
                  }}
                />
                <input
                  id="evocare-username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder={`e.g. ${currentRoleConfig?.demoUser || 'username'}`}
                  autoComplete="username"
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '10px 12px 10px 36px',
                    border: '1px solid var(--color-border-strong)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '14px',
                    color: 'var(--color-text-main)',
                    backgroundColor: loading ? 'var(--color-surface-alt)' : 'var(--color-surface)',
                    outline: 'none',
                    boxSizing: 'border-box',
                  }}
                  onFocus={(e) => (e.target.style.borderColor = accent)}
                  onBlur={(e) => (e.target.style.borderColor = 'var(--color-border-strong)')}
                />
              </div>
            </div>

            {/* Password */}
            <div style={{ marginBottom: '20px' }}>
              <label
                htmlFor="evocare-password"
                style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '6px' }}
              >
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <Lock
                  size={15}
                  style={{
                    position: 'absolute',
                    left: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--color-text-faint)',
                  }}
                />
                <input
                  id="evocare-password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  autoComplete="current-password"
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '10px 40px 10px 36px',
                    border: '1px solid var(--color-border-strong)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '14px',
                    color: 'var(--color-text-main)',
                    backgroundColor: loading ? 'var(--color-surface-alt)' : 'var(--color-surface)',
                    outline: 'none',
                    boxSizing: 'border-box',
                  }}
                  onFocus={(e) => (e.target.style.borderColor = accent)}
                  onBlur={(e) => (e.target.style.borderColor = 'var(--color-border-strong)')}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  style={{
                    position: 'absolute',
                    right: '10px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    padding: '4px',
                    color: 'var(--color-text-faint)',
                  }}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              id="evocare-login-submit"
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: loading ? 'var(--color-text-faint)' : accent,
                color: '#ffffff',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                fontSize: '14px',
                fontWeight: 700,
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                boxShadow: loading ? 'none' : `0 8px 20px -6px ${accent}80`,
              }}
              onMouseEnter={(e) => {
                if (!loading) (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(-1px)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(0)';
              }}
            >
              {loading ? (
                <>
                  <span
                    style={{
                      width: '14px',
                      height: '14px',
                      border: '2px solid rgba(255,255,255,0.4)',
                      borderTopColor: '#ffffff',
                      borderRadius: '50%',
                      animation: 'spin 0.7s linear infinite',
                      display: 'inline-block',
                    }}
                  />
                  Authenticating…
                </>
              ) : (
                <>
                  <LogIn size={15} />
                  Sign in to {currentRoleConfig?.title} portal
                </>
              )}
            </button>
          </form>

          {/* Role-Specific Demo Credentials Box */}
          {currentRoleConfig && (
            <div
              style={{
                marginTop: '24px',
                padding: '16px',
                backgroundColor: currentRoleConfig.accentSoft,
                borderRadius: 'var(--radius-md)',
                border: `1px solid ${currentRoleConfig.accentBorder}`,
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '10px',
                }}
              >
                <div
                  style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    color: accent,
                    textTransform: 'uppercase',
                    letterSpacing: '0.06em',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px',
                  }}
                >
                  <KeyRound size={12} />
                  {currentRoleConfig.title} demo credentials
                </div>
                <button
                  id={`evocare-demo-${currentRoleConfig.demoUser}`}
                  type="button"
                  onClick={() => fillDemo(currentRoleConfig.demoUser, currentRoleConfig.demoPass)}
                  style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    backgroundColor: accent,
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: 'var(--radius-sm)',
                    padding: '4px 9px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  <Sparkles size={11} />
                  Auto-fill
                </button>
              </div>

              <div style={{ fontSize: '12px', color: 'var(--color-text-main)', marginBottom: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '3px 0' }}>
                  <span style={{ color: 'var(--color-text-muted)' }}>Username:</span>
                  <strong style={{ fontFamily: 'var(--font-mono)' }}>{currentRoleConfig.demoUser}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '3px 0' }}>
                  <span style={{ color: 'var(--color-text-muted)' }}>Password:</span>
                  <strong style={{ fontFamily: 'var(--font-mono)' }}>{currentRoleConfig.demoPass}</strong>
                </div>
              </div>

              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', borderTop: `1px solid ${currentRoleConfig.accentBorder}`, paddingTop: '6px' }}>
                {currentRoleConfig.demoRoleDesc}
              </div>
            </div>
          )}
        </div>

        {/* Security badge */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            marginTop: '20px',
            fontSize: '12px',
            color: 'var(--color-text-muted)',
          }}
        >
          <ShieldCheck size={13} style={{ color: accent }} />
          <span>JWT-secured &middot; role-specific endpoint authorization</span>
        </div>
      </div>
    </div>
  );
};

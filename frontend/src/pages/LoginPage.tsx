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
  ChevronRight,
  Sparkles,
  KeyRound,
  LucideIcon,
} from 'lucide-react';
import { authService, AuthUser } from '../services/auth';

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
  primaryColor: string;
  accentColor: string;
  bgLight: string;
  borderColor: string;
  icon: LucideIcon;
  demoUser: string;
  demoPass: string;
  demoRoleDesc: string;
}

const ROLES: RoleMetadata[] = [
  {
    id: 'DOCTOR',
    title: 'Doctor Portal',
    badge: 'Physicians & Clinicians',
    subtitle: 'Clinical Decision Support',
    description: 'Longitudinal health memory, diagnostic reasoning, 2FA patient verification, and differential analysis.',
    primaryColor: '#0284c7',
    accentColor: '#0369a1',
    bgLight: '#f0f9ff',
    borderColor: '#bae6fd',
    icon: Stethoscope,
    demoUser: 'doctor.demo',
    demoPass: 'DoctorPass123!',
    demoRoleDesc: 'Full clinical reasoning station with 2FA email consent security.',
  },
  {
    id: 'CAREGIVER',
    title: 'Caregiver Portal',
    badge: 'Family & Caretakers',
    subtitle: 'Observations & Daily Logs',
    description: 'Log patient daily observations, behavior, nutrition, and manage patient connection requests.',
    primaryColor: '#059669',
    accentColor: '#047857',
    bgLight: '#f0fdf4',
    borderColor: '#bbf7d0',
    icon: HeartHandshake,
    demoUser: 'caregiver.demo',
    demoPass: 'CaregiverPass123!',
    demoRoleDesc: 'Submit vital observations and accept patient pairing invites.',
  },
  {
    id: 'PATIENT',
    title: 'Patient Companion',
    badge: 'Patients & Individuals',
    subtitle: 'AI Health Companion',
    description: 'Engage with your personalized conversational health companion, check symptoms, and pair caretakers.',
    primaryColor: '#d97706',
    accentColor: '#b45309',
    bgLight: '#fffbeb',
    borderColor: '#fde68a',
    icon: MessageSquare,
    demoUser: 'patient.demo',
    demoPass: 'PatientPass123!',
    demoRoleDesc: 'Conversational wellness companion and caregiver connection management.',
  },
  {
    id: 'ADMIN',
    title: 'System Admin',
    badge: 'System & Governance',
    subtitle: 'Access & User Management',
    description: 'Manage users, clinical roles, system security parameters, and cross-provider access controls.',
    primaryColor: '#7c3aed',
    accentColor: '#6d28d9',
    bgLight: '#faf5ff',
    borderColor: '#e9d5ff',
    icon: Shield,
    demoUser: 'admin.demo',
    demoPass: 'AdminPass123!',
    demoRoleDesc: 'Administrative controls and provider authorization management.',
  },
];

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [selectedRole, setSelectedRole] = useState<RoleType | null>(null);
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

  // STEP 1: LANDING PAGE (ROLE SELECTION)
  if (!selectedRole) {
    return (
      <div
        style={{
          minHeight: '100vh',
          backgroundColor: '#f8fafc',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '32px 20px',
          fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
        }}
      >
        {/* Top Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '36px', maxWidth: '640px' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '12px',
              backgroundColor: '#ffffff',
              padding: '8px 20px',
              borderRadius: '999px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
              border: '1px solid #e2e8f0',
              marginBottom: '20px',
            }}
          >
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                backgroundColor: '#0284c7',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
              }}
            >
              <Activity size={18} />
            </div>
            <span style={{ fontSize: '18px', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.02em' }}>
              EvoCare
            </span>
            <span style={{ fontSize: '12px', color: '#64748b', fontWeight: 500 }}>
              Longitudinal Health Memory
            </span>
          </div>

          <h1
            style={{
              fontSize: '32px',
              fontWeight: 800,
              color: '#0f172a',
              letterSpacing: '-0.03em',
              margin: '0 0 12px 0',
              lineHeight: 1.2,
            }}
          >
            Welcome to EvoCare
          </h1>
          <p style={{ fontSize: '15px', color: '#64748b', margin: 0, lineHeight: 1.5 }}>
            Select your role below to access your dedicated healthcare portal
          </p>
        </div>

        {/* 4 Role Selection Cards Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '20px',
            width: '100%',
            maxWidth: '1040px',
            marginBottom: '36px',
          }}
        >
          {ROLES.map((role) => {
            const Icon = role.icon;
            return (
              <div
                key={role.id}
                id={`evocare-select-role-${role.id.toLowerCase()}`}
                onClick={() => handleSelectRole(role.id)}
                style={{
                  backgroundColor: '#ffffff',
                  borderRadius: '16px',
                  border: '1px solid #e2e8f0',
                  padding: '24px',
                  cursor: 'pointer',
                  transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  boxShadow: '0 2px 10px rgba(0, 0, 0, 0.03)',
                  position: 'relative',
                  overflow: 'hidden',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.borderColor = role.primaryColor;
                  e.currentTarget.style.boxShadow = `0 12px 24px ${role.primaryColor}15`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.borderColor = '#e2e8f0';
                  e.currentTarget.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.03)';
                }}
              >
                <div>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '16px',
                    }}
                  >
                    <div
                      style={{
                        width: '44px',
                        height: '44px',
                        borderRadius: '12px',
                        backgroundColor: role.bgLight,
                        border: `1px solid ${role.borderColor}`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: role.primaryColor,
                      }}
                    >
                      <Icon size={22} />
                    </div>
                    <span
                      style={{
                        fontSize: '11px',
                        fontWeight: 700,
                        backgroundColor: role.bgLight,
                        color: role.primaryColor,
                        padding: '3px 8px',
                        borderRadius: '6px',
                        border: `1px solid ${role.borderColor}`,
                      }}
                    >
                      {role.badge}
                    </span>
                  </div>

                  <h3
                    style={{
                      fontSize: '18px',
                      fontWeight: 700,
                      color: '#0f172a',
                      margin: '0 0 4px 0',
                    }}
                  >
                    {role.title}
                  </h3>
                  <div
                    style={{
                      fontSize: '12px',
                      fontWeight: 600,
                      color: role.primaryColor,
                      marginBottom: '10px',
                    }}
                  >
                    {role.subtitle}
                  </div>
                  <p
                    style={{
                      fontSize: '13px',
                      color: '#64748b',
                      lineHeight: 1.5,
                      margin: 0,
                    }}
                  >
                    {role.description}
                  </p>
                </div>

                <div
                  style={{
                    marginTop: '20px',
                    paddingTop: '14px',
                    borderTop: '1px solid #f1f5f9',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    color: role.primaryColor,
                    fontSize: '13px',
                    fontWeight: 600,
                  }}
                >
                  <span>Enter as {role.badge.split(' ')[0]}</span>
                  <ChevronRight size={16} />
                </div>
              </div>
            );
          })}
        </div>

        {/* Security Footer Note */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '12px',
            color: '#94a3b8',
          }}
        >
          <ShieldCheck size={14} style={{ color: '#0284c7' }} />
          <span>Multi-Role Access Control • 2FA Patient Memory Consent • End-to-End Audited</span>
        </div>
      </div>
    );
  }

  // STEP 2: ROLE-SPECIFIC LOGIN PAGE
  const Icon = currentRoleConfig?.icon || Lock;

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: currentRoleConfig?.bgLight || '#f8fafc',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
      }}
    >
      {/* Back to Role Selection Button */}
      <div style={{ width: '100%', maxWidth: '440px', marginBottom: '16px' }}>
        <button
          id="evocare-back-to-roles"
          type="button"
          onClick={handleBackToLanding}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: 'none',
            border: 'none',
            color: '#64748b',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            padding: '6px 0',
            transition: 'color 0.15s',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = '#0f172a')}
          onMouseLeave={(e) => (e.currentTarget.style.color = '#64748b')}
        >
          <ArrowLeft size={16} />
          <span>Back to Role Selection</span>
        </button>
      </div>

      {/* Role-Specific Sign In Card */}
      <div
        style={{
          backgroundColor: '#ffffff',
          borderRadius: '20px',
          border: '1px solid #e2e8f0',
          padding: '36px',
          width: '100%',
          maxWidth: '440px',
          boxShadow: '0 8px 30px rgba(0, 0, 0, 0.06)',
        }}
      >
        {/* Role Header Banner */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '24px' }}>
          <div
            style={{
              width: '48px',
              height: '48px',
              borderRadius: '14px',
              backgroundColor: currentRoleConfig?.bgLight || '#f0f9ff',
              border: `1px solid ${currentRoleConfig?.borderColor || '#bae6fd'}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: currentRoleConfig?.primaryColor || '#0284c7',
              flexShrink: 0,
            }}
          >
            <Icon size={24} />
          </div>
          <div>
            <div
              style={{
                fontSize: '11px',
                fontWeight: 700,
                color: currentRoleConfig?.primaryColor || '#0284c7',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              {currentRoleConfig?.badge}
            </div>
            <h2
              style={{
                fontSize: '20px',
                fontWeight: 800,
                color: '#0f172a',
                margin: '2px 0 0 0',
                letterSpacing: '-0.02em',
              }}
            >
              {currentRoleConfig?.title}
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
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '8px',
              padding: '10px 12px',
              marginBottom: '20px',
            }}
          >
            <AlertCircle size={16} style={{ color: '#dc2626', flexShrink: 0, marginTop: '1px' }} />
            <span style={{ fontSize: '13px', color: '#991b1b' }}>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Username */}
          <div style={{ marginBottom: '16px' }}>
            <label
              htmlFor="evocare-username"
              style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#374151', marginBottom: '6px' }}
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
                  color: '#9ca3af',
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
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px',
                  color: '#0f172a',
                  backgroundColor: loading ? '#f9fafb' : '#ffffff',
                  outline: 'none',
                  boxSizing: 'border-box',
                  transition: 'border-color 0.15s',
                }}
                onFocus={(e) => (e.target.style.borderColor = currentRoleConfig?.primaryColor || '#0284c7')}
                onBlur={(e) => (e.target.style.borderColor = '#d1d5db')}
              />
            </div>
          </div>

          {/* Password */}
          <div style={{ marginBottom: '20px' }}>
            <label
              htmlFor="evocare-password"
              style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#374151', marginBottom: '6px' }}
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
                  color: '#9ca3af',
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
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px',
                  color: '#0f172a',
                  backgroundColor: loading ? '#f9fafb' : '#ffffff',
                  outline: 'none',
                  boxSizing: 'border-box',
                  transition: 'border-color 0.15s',
                }}
                onFocus={(e) => (e.target.style.borderColor = currentRoleConfig?.primaryColor || '#0284c7')}
                onBlur={(e) => (e.target.style.borderColor = '#d1d5db')}
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
                  color: '#9ca3af',
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
              backgroundColor: loading ? '#94a3b8' : currentRoleConfig?.primaryColor || '#0284c7',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 700,
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.15s',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              boxShadow: `0 2px 8px ${currentRoleConfig?.primaryColor || '#0284c7'}40`,
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
                <Lock size={14} />
                Sign In to {currentRoleConfig?.title}
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
              backgroundColor: currentRoleConfig.bgLight,
              borderRadius: '12px',
              border: `1px solid ${currentRoleConfig.borderColor}`,
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
                  color: currentRoleConfig.primaryColor,
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                }}
              >
                <KeyRound size={12} />
                {currentRoleConfig.title} Demo Credentials
              </div>
              <button
                id={`evocare-demo-${currentRoleConfig.demoUser}`}
                type="button"
                onClick={() => fillDemo(currentRoleConfig.demoUser, currentRoleConfig.demoPass)}
                style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  backgroundColor: currentRoleConfig.primaryColor,
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '5px',
                  padding: '3px 8px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <Sparkles size={11} />
                Auto-Fill
              </button>
            </div>

            <div style={{ fontSize: '12px', color: '#334155', marginBottom: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '3px 0' }}>
                <span style={{ color: '#64748b' }}>Username:</span>
                <strong style={{ fontFamily: "'IBM Plex Mono', monospace" }}>{currentRoleConfig.demoUser}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '3px 0' }}>
                <span style={{ color: '#64748b' }}>Password:</span>
                <strong style={{ fontFamily: "'IBM Plex Mono', monospace" }}>{currentRoleConfig.demoPass}</strong>
              </div>
            </div>

            <div style={{ fontSize: '11px', color: '#64748b', borderTop: '1px solid #e2e8f0', paddingTop: '6px' }}>
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
          color: '#64748b',
        }}
      >
        <ShieldCheck size={13} style={{ color: currentRoleConfig?.primaryColor || '#0284c7' }} />
        <span>JWT-secured · Role-specific endpoint authorization</span>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

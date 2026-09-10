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
  LogIn,
  Sparkles,
  KeyRound,
  LucideIcon,
  Users,
  Heart,
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
  themeColor: string;
  topBorderColor: string;
  btnColor: string;
  bgLight: string;
  borderColor: string;
  icon: LucideIcon;
  demoUser: string;
  demoPass: string;
  demoRoleDesc: string;
  graphicType: 'doctor' | 'employee' | 'parent' | 'alumni';
}

const ROLES: RoleMetadata[] = [
  {
    id: 'DOCTOR',
    title: 'Doctor',
    badge: 'Physicians & Clinicians',
    subtitle: 'Clinical Decision Support',
    description: 'Longitudinal health memory, diagnostic reasoning, 2FA patient verification, and differential analysis.',
    themeColor: '#0284c7',
    topBorderColor: '#0284c7',
    btnColor: '#0284c7',
    bgLight: '#f0f9ff',
    borderColor: '#bae6fd',
    icon: Stethoscope,
    demoUser: 'doctor.demo',
    demoPass: 'DoctorPass123!',
    demoRoleDesc: 'Full clinical reasoning station with 2FA email consent security.',
    graphicType: 'doctor',
  },
  {
    id: 'CAREGIVER',
    title: 'Caregiver',
    badge: 'Family & Caretakers',
    subtitle: 'Observations & Daily Logs',
    description: 'Log patient daily observations, behavior, nutrition, and manage patient connection requests.',
    themeColor: '#d97706',
    topBorderColor: '#eab308',
    btnColor: '#ca8a04',
    bgLight: '#fefce8',
    borderColor: '#fef08a',
    icon: HeartHandshake,
    demoUser: 'caregiver.demo',
    demoPass: 'CaregiverPass123!',
    demoRoleDesc: 'Submit vital observations and accept patient pairing invites.',
    graphicType: 'employee',
  },
  {
    id: 'PATIENT',
    title: 'Patient',
    badge: 'Patients & Individuals',
    subtitle: 'AI Health Companion',
    description: 'Engage with your personalized conversational health companion, check symptoms, and pair caretakers.',
    themeColor: '#16a34a',
    topBorderColor: '#22c55e',
    btnColor: '#16a34a',
    bgLight: '#f0fdf4',
    borderColor: '#bbf7d0',
    icon: MessageSquare,
    demoUser: 'patient.demo',
    demoPass: 'PatientPass123!',
    demoRoleDesc: 'Conversational wellness companion and caregiver connection management.',
    graphicType: 'parent',
  },
  {
    id: 'ADMIN',
    title: 'Administrator',
    badge: 'System & Governance',
    subtitle: 'Access & User Management',
    description: 'Manage users, clinical roles, system security parameters, and cross-provider access controls.',
    themeColor: '#0284c7',
    topBorderColor: '#38bdf8',
    btnColor: '#0284c7',
    bgLight: '#f0f9ff',
    borderColor: '#bae6fd',
    icon: Shield,
    demoUser: 'admin.demo',
    demoPass: 'AdminPass123!',
    demoRoleDesc: 'Administrative controls and provider authorization management.',
    graphicType: 'alumni',
  },
];

// Visual Avatar Graphic Component mimicking the portal cards in the reference
const RoleGraphic: React.FC<{ type: 'doctor' | 'employee' | 'parent' | 'alumni' }> = ({
  type,
}) => {
  if (type === 'doctor') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <div
          style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            backgroundColor: '#e0f2fe',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#0284c7',
            marginBottom: '4px',
          }}
        >
          <Stethoscope size={24} />
        </div>
        <div style={{ display: 'flex', gap: '3px', marginTop: '2px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#93c5fd' }} />
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#60a5fa' }} />
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#93c5fd' }} />
        </div>
      </div>
    );
  }

  if (type === 'employee') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <div
          style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            backgroundColor: '#fef9c3',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ca8a04',
            marginBottom: '4px',
          }}
        >
          <Users size={24} />
        </div>
        <div style={{ display: 'flex', gap: '3px', marginTop: '2px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#fde047' }} />
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#eab308' }} />
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#fde047' }} />
        </div>
      </div>
    );
  }

  if (type === 'parent') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <div
          style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            backgroundColor: '#dcfce7',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#16a34a',
            marginBottom: '4px',
          }}
        >
          <Heart size={24} />
        </div>
        <div style={{ display: 'flex', gap: '3px', marginTop: '2px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#86efac' }} />
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#4ade80' }} />
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#86efac' }} />
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <div
        style={{
          width: '42px',
          height: '42px',
          borderRadius: '10px',
          backgroundColor: '#e0f2fe',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#0284c7',
          marginBottom: '4px',
        }}
      >
        <Shield size={24} />
      </div>
      <div style={{ display: 'flex', gap: '3px', marginTop: '2px' }}>
        <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#7dd3fc' }} />
        <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#38bdf8' }} />
        <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#7dd3fc' }} />
      </div>
    </div>
  );
};

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

  // STEP 1: PORTAL LANDING PAGE (MATCHING THE UPLOADED REFERENCE DESIGN)
  if (!selectedRole) {
    return (
      <div
        style={{
          minHeight: '100vh',
          backgroundColor: '#f1f5f9',
          display: 'flex',
          flexDirection: 'column',
          fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        }}
      >
        {/* Top Deep Blue Banner */}
        <header
          style={{
            background: 'linear-gradient(90deg, #1e3a8a 0%, #1e40af 40%, #2563eb 100%)',
            color: '#ffffff',
            padding: '14px 32px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: '50%',
                backgroundColor: 'rgba(255, 255, 255, 0.18)',
                border: '1.5px solid rgba(255, 255, 255, 0.4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
              }}
            >
              <Activity size={22} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                <span style={{ fontSize: '22px', fontWeight: 800, letterSpacing: '-0.02em' }}>EvoCare</span>
                <span style={{ fontSize: '13px', fontWeight: 400, opacity: 0.9 }}>(Clinical Intelligence Platform)</span>
              </div>
            </div>
          </div>
          <div
            style={{
              fontSize: '11px',
              fontWeight: 600,
              backgroundColor: 'rgba(255, 255, 255, 0.15)',
              padding: '4px 10px',
              borderRadius: '4px',
              border: '1px solid rgba(255, 255, 255, 0.25)',
            }}
          >
            Longitudinal Health Memory
          </div>
        </header>

        {/* Central Content Area */}
        <main
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '48px 24px',
            maxWidth: '1200px',
            margin: '0 auto',
            width: '100%',
            boxSizing: 'border-box',
          }}
        >
          {/* Header Title & Subtitle */}
          <div style={{ textAlign: 'center', marginBottom: '44px', maxWidth: '820px' }}>
            <h1
              style={{
                fontSize: '26px',
                fontWeight: 700,
                color: '#0284c7',
                margin: '0 0 14px 0',
                letterSpacing: '-0.02em',
              }}
            >
              EvoCare translates to "Evolving Longitudinal Care"
            </h1>
            <p
              style={{
                fontSize: '13px',
                color: '#1e293b',
                lineHeight: 1.6,
                fontWeight: 500,
                margin: 0,
              }}
            >
              A digital health initiative facilitating Doctor, Caregiver, Patient, and Administrator to access and
              process Longitudinal Health Records, Clinical Reasoning, and Care Observations on one common platform.
            </p>
          </div>

          {/* 4 Horizontal Role Cards Grid */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: '20px',
              width: '100%',
              marginBottom: '48px',
            }}
          >
            {ROLES.map((role) => (
              <div
                key={role.id}
                id={`evocare-select-role-${role.id.toLowerCase()}`}
                onClick={() => handleSelectRole(role.id)}
                style={{
                  backgroundColor: '#ffffff',
                  borderRadius: '6px',
                  borderTop: `4px solid ${role.topBorderColor}`,
                  boxShadow: '0 4px 14px rgba(0, 0, 0, 0.07)',
                  padding: '20px 24px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  transition: 'all 0.18s ease',
                  userSelect: 'none',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-3px)';
                  e.currentTarget.style.boxShadow = '0 8px 20px rgba(0, 0, 0, 0.12)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 14px rgba(0, 0, 0, 0.07)';
                }}
              >
                {/* Left side: Avatar Graphic */}
                <RoleGraphic type={role.graphicType} />

                {/* Right side: Role Title + Action Button */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
                  <span
                    style={{
                      fontSize: '18px',
                      fontWeight: 700,
                      color: role.themeColor,
                      letterSpacing: '-0.01em',
                    }}
                  >
                    {role.title}
                  </span>

                  <button
                    type="button"
                    style={{
                      width: '36px',
                      height: '32px',
                      borderRadius: '4px',
                      backgroundColor: role.btnColor,
                      border: 'none',
                      color: '#ffffff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      boxShadow: `0 2px 6px ${role.btnColor}60`,
                    }}
                    aria-label={`Enter ${role.title} Portal`}
                  >
                    <LogIn size={17} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Bottom Security Footer */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '12px',
              color: '#64748b',
            }}
          >
            <ShieldCheck size={14} style={{ color: '#0284c7' }} />
            <span>Multi-Role Access Control • 2FA Patient Memory Gate • End-to-End Audited Clinical Platform</span>
          </div>
        </main>
      </div>
    );
  }

  // STEP 2: DEDICATED ROLE-SPECIFIC LOGIN PAGE
  const Icon = currentRoleConfig?.icon || Lock;

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#f1f5f9',
        display: 'flex',
        flexDirection: 'column',
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      {/* Top Banner */}
      <header
        style={{
          background: 'linear-gradient(90deg, #1e3a8a 0%, #1e40af 40%, #2563eb 100%)',
          color: '#ffffff',
          padding: '14px 32px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '50%',
              backgroundColor: 'rgba(255, 255, 255, 0.18)',
              border: '1.5px solid rgba(255, 255, 255, 0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
            }}
          >
            <Activity size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
              <span style={{ fontSize: '22px', fontWeight: 800, letterSpacing: '-0.02em' }}>EvoCare</span>
              <span style={{ fontSize: '13px', fontWeight: 400, opacity: 0.9 }}>
                ({currentRoleConfig?.title} Portal)
              </span>
            </div>
          </div>
        </div>
        <button
          id="evocare-back-to-roles"
          type="button"
          onClick={handleBackToLanding}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: 'rgba(255, 255, 255, 0.15)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            color: '#ffffff',
            fontSize: '12px',
            fontWeight: 600,
            cursor: 'pointer',
            padding: '6px 12px',
            borderRadius: '4px',
            transition: 'background-color 0.15s',
          }}
        >
          <ArrowLeft size={14} />
          <span>Change Role</span>
        </button>
      </header>

      {/* Login Container */}
      <main
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '32px 24px',
        }}
      >
        <div
          style={{
            backgroundColor: '#ffffff',
            borderRadius: '8px',
            borderTop: `4px solid ${currentRoleConfig?.topBorderColor || '#0284c7'}`,
            border: '1px solid #e2e8f0',
            borderTopWidth: '4px',
            borderTopColor: currentRoleConfig?.topBorderColor || '#0284c7',
            padding: '36px',
            width: '100%',
            maxWidth: '440px',
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.08)',
          }}
        >
          {/* Role Header Banner */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '24px' }}>
            <div
              style={{
                width: '46px',
                height: '46px',
                borderRadius: '10px',
                backgroundColor: currentRoleConfig?.bgLight || '#f0f9ff',
                border: `1px solid ${currentRoleConfig?.borderColor || '#bae6fd'}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: currentRoleConfig?.themeColor || '#0284c7',
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
                  color: currentRoleConfig?.themeColor || '#0284c7',
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
                {currentRoleConfig?.title} Sign In
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
                borderRadius: '6px',
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
                    borderRadius: '6px',
                    fontSize: '14px',
                    color: '#0f172a',
                    backgroundColor: loading ? '#f9fafb' : '#ffffff',
                    outline: 'none',
                    boxSizing: 'border-box',
                    transition: 'border-color 0.15s',
                  }}
                  onFocus={(e) => (e.target.style.borderColor = currentRoleConfig?.themeColor || '#0284c7')}
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
                    borderRadius: '6px',
                    fontSize: '14px',
                    color: '#0f172a',
                    backgroundColor: loading ? '#f9fafb' : '#ffffff',
                    outline: 'none',
                    boxSizing: 'border-box',
                    transition: 'border-color 0.15s',
                  }}
                  onFocus={(e) => (e.target.style.borderColor = currentRoleConfig?.themeColor || '#0284c7')}
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
                backgroundColor: loading ? '#94a3b8' : currentRoleConfig?.themeColor || '#0284c7',
                color: '#ffffff',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: 700,
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.15s',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                boxShadow: `0 2px 8px ${currentRoleConfig?.themeColor || '#0284c7'}40`,
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
                  Sign In to {currentRoleConfig?.title} Portal
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
                borderRadius: '8px',
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
                    color: currentRoleConfig.themeColor,
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
                    backgroundColor: currentRoleConfig.themeColor,
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '4px',
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
          <ShieldCheck size={13} style={{ color: currentRoleConfig?.themeColor || '#0284c7' }} />
          <span>JWT-secured · Role-specific endpoint authorization</span>
        </div>
      </main>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

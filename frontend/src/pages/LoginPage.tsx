import React, { useState } from 'react';
import { Activity, Lock, User, AlertCircle, ShieldCheck, Eye, EyeOff } from 'lucide-react';
import { authService, AuthUser } from '../services/auth';

interface LoginPageProps {
  onLoginSuccess: (user: AuthUser) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#f0f9ff',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        fontFamily: "'Inter', system-ui, sans-serif",
      }}
    >
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px' }}>
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            backgroundColor: '#0284c7',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: '0 4px 12px rgba(2, 132, 199, 0.3)',
          }}
        >
          <Activity size={28} />
        </div>
        <div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a', letterSpacing: '-0.03em' }}>
            EvoCare
          </div>
          <div style={{ fontSize: '12px', color: '#64748b', marginTop: '1px' }}>
            Longitudinal Patient Memory System
          </div>
        </div>
      </div>

      {/* Card */}
      <div
        style={{
          backgroundColor: '#ffffff',
          borderRadius: '16px',
          border: '1px solid #e2e8f0',
          padding: '36px',
          width: '100%',
          maxWidth: '420px',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.06)',
        }}
      >
        <h2
          style={{
            fontSize: '20px',
            fontWeight: 700,
            color: '#0f172a',
            margin: '0 0 4px 0',
            letterSpacing: '-0.02em',
          }}
        >
          Sign In
        </h2>
        <p style={{ fontSize: '13px', color: '#64748b', margin: '0 0 28px 0' }}>
          Authenticate to access patient records
        </p>

        {/* Error */}
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
              Username
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
                placeholder="e.g. doctor.demo"
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
                onFocus={(e) => (e.target.style.borderColor = '#0284c7')}
                onBlur={(e) => (e.target.style.borderColor = '#d1d5db')}
              />
            </div>
          </div>

          {/* Password */}
          <div style={{ marginBottom: '24px' }}>
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
                onFocus={(e) => (e.target.style.borderColor = '#0284c7')}
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
              padding: '11px',
              backgroundColor: loading ? '#93c5fd' : '#0284c7',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.15s',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
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
                Sign In
              </>
            )}
          </button>
        </form>

        {/* Demo credentials */}
        <div
          style={{
            marginTop: '24px',
            padding: '14px',
            backgroundColor: '#f8fafc',
            borderRadius: '10px',
            border: '1px solid #e2e8f0',
          }}
        >
          <div
            style={{
              fontSize: '11px',
              fontWeight: 700,
              color: '#475569',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginBottom: '10px',
            }}
          >
            Demo Credentials
          </div>
          {[
            { label: 'Doctor (P001)', user: 'doctor.demo', pass: 'DoctorPass123!', color: '#0284c7' },
            { label: 'Caregiver (P001)', user: 'caregiver.demo', pass: 'CaregiverPass123!', color: '#059669' },
            { label: 'Patient (P001)', user: 'patient.demo', pass: 'PatientPass123!', color: '#d97706' },
            { label: 'Admin', user: 'admin.demo', pass: 'AdminPass123!', color: '#7c3aed' },
          ].map(({ label, user, pass, color }) => (
            <button
              key={user}
              id={`evocare-demo-${user}`}
              onClick={() => fillDemo(user, pass)}
              disabled={loading}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '7px 10px',
                marginBottom: '6px',
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '12px',
                color: '#374151',
                textAlign: 'left',
              }}
            >
              <span>
                <span style={{ fontWeight: 600, color }}>{label}</span>
                <span style={{ color: '#9ca3af', marginLeft: '6px' }}>{user}</span>
              </span>
              <span
                style={{
                  fontSize: '10px',
                  fontWeight: 600,
                  backgroundColor: color + '15',
                  color,
                  padding: '2px 6px',
                  borderRadius: '4px',
                }}
              >
                Fill
              </span>
            </button>
          ))}
          <div style={{ fontSize: '10px', color: '#94a3b8', marginTop: '8px' }}>
            ⚠ Synthetic demo data only. Not for clinical use.
          </div>
        </div>
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
        <ShieldCheck size={13} style={{ color: '#0284c7' }} />
        JWT-secured · Role-based access · Patient-level authorization
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

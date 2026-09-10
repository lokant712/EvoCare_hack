import React, { useState, useEffect } from 'react';
import { Shield, UserCheck, Lock, CheckCircle2, AlertCircle, Mail } from 'lucide-react';
import { authService } from '../../services/auth';

interface DoctorPatientAccessGateProps {
  initialPatientCode?: string;
  onPatientUnlocked: (patientCode: string) => void;
  onCancel?: () => void;
  isModal?: boolean;
}

const DEMO_PATIENTS = [
  { code: 'P001', name: 'Meenakshi' },
  { code: 'P002', name: 'Ananya' },
  { code: 'P003', name: 'Rajesh' },
  { code: 'P004', name: 'Sunita' },
  { code: 'P005', name: 'Vikramaditya' },
];

export const DoctorPatientAccessGate: React.FC<DoctorPatientAccessGateProps> = ({
  initialPatientCode = 'P001',
  onPatientUnlocked,
  onCancel,
  isModal = false,
}) => {
  const [patientCode, setPatientCode] = useState<string>(initialPatientCode);
  const [patientInfo, setPatientInfo] = useState<{ name: string; email: string; age: number; sex: string; location: string } | null>(null);
  const [lookupLoading, setLookupLoading] = useState<boolean>(false);
  const [lookupError, setLookupError] = useState<string | null>(null);

  // 2FA state
  const [otpRequested, setOtpRequested] = useState<boolean>(false);
  const [generatedOtp, setGeneratedOtp] = useState<string | null>(null);
  const [enteredOtp, setEnteredOtp] = useState<string>('');
  const [verifyLoading, setVerifyLoading] = useState<boolean>(false);
  const [verifyError, setVerifyError] = useState<string | null>(null);
  const [verifySuccess, setVerifySuccess] = useState<boolean>(false);

  // Quick lookup when patientCode changes
  const handleLookup = async (codeToLookup: string) => {
    const clean = codeToLookup.trim().toUpperCase();
    if (!clean) return;
    setLookupLoading(true);
    setLookupError(null);
    setOtpRequested(false);
    setGeneratedOtp(null);
    setEnteredOtp('');
    setVerifyError(null);

    try {
      const token = authService.getToken();
      const res = await fetch(`/api/patients/lookup/${clean}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        throw new Error(`Patient '${clean}' not found.`);
      }
      const data = await res.json();
      setPatientInfo(data);
    } catch (err: any) {
      setPatientInfo(null);
      setLookupError(err.message || 'Failed to find patient.');
    } finally {
      setLookupLoading(false);
    }
  };

  useEffect(() => {
    if (initialPatientCode) {
      handleLookup(initialPatientCode);
    }
  }, [initialPatientCode]);

  // Request Patient 2FA Consent OTP
  const handleRequestOtp = async () => {
    const clean = patientCode.trim().toUpperCase();
    if (!clean) return;
    setLookupLoading(true);
    setVerifyError(null);

    try {
      const token = authService.getToken();
      const res = await fetch('/api/patients/request-access-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ patient_code: clean }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to dispatch code.');
      }

      const data = await res.json();
      setOtpRequested(true);
      const code = data.demo_code || '7742';
      setGeneratedOtp(code);
      setEnteredOtp(code); // Pre-fill for quick physician demo flow
    } catch (err: any) {
      setVerifyError(err.message || 'Error requesting consent code.');
    } finally {
      setLookupLoading(false);
    }
  };

  // Verify Patient Consent OTP
  const handleVerifyOtp = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const cleanCode = patientCode.trim().toUpperCase();
    const cleanOtp = enteredOtp.trim();
    if (!cleanOtp) {
      setVerifyError('Please enter the verification code.');
      return;
    }

    setVerifyLoading(true);
    setVerifyError(null);

    try {
      const token = authService.getToken();
      const res = await fetch('/api/patients/verify-access-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          patient_code: cleanCode,
          verification_code: cleanOtp,
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Invalid verification code.');
      }

      setVerifySuccess(true);
      setTimeout(() => {
        onPatientUnlocked(cleanCode);
      }, 500);
    } catch (err: any) {
      setVerifyError(err.message || 'Verification failed.');
    } finally {
      setVerifyLoading(false);
    }
  };

  const content = (
    <div
      style={{
        backgroundColor: 'var(--color-surface)',
        borderRadius: '16px',
        border: '1px solid var(--color-border)',
        boxShadow: '0 16px 36px -8px rgba(0, 0, 0, 0.14)',
        width: '100%',
        maxWidth: '480px',
        overflow: 'hidden',
      }}
    >
      {/* Sleek Minimal Header */}
      <div
        style={{
          padding: '20px 24px 16px 24px',
          borderBottom: '1px solid var(--color-border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              backgroundColor: 'var(--color-accent-soft)',
              color: 'var(--color-accent)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px solid var(--color-accent-border)',
            }}
          >
            <Shield size={20} />
          </div>
          <div>
            <h2 style={{ fontSize: '16px', fontWeight: 800, margin: 0, color: 'var(--color-text-main)', letterSpacing: '-0.01em' }}>
              Unlock Patient Records
            </h2>
            <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginTop: '2px' }}>
              Two-Factor Physician Verification Gate
            </div>
          </div>
        </div>

        <span
          style={{
            fontSize: '11px',
            fontWeight: 700,
            padding: '3px 8px',
            borderRadius: '12px',
            backgroundColor: 'var(--color-surface-alt)',
            color: 'var(--color-text-muted)',
            border: '1px solid var(--color-border)',
          }}
        >
          2FA Active
        </span>
      </div>

      <div style={{ padding: '20px 24px' }}>
        {/* Patient Selection Pills */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--color-text-main)', marginBottom: '8px' }}>
            Select Patient Record
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {DEMO_PATIENTS.map((p) => {
              const isSelected = patientCode === p.code;
              return (
                <button
                  key={p.code}
                  type="button"
                  id={`evocare-quick-select-${p.code}`}
                  onClick={() => {
                    setPatientCode(p.code);
                    handleLookup(p.code);
                  }}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '8px',
                    border: `1px solid ${isSelected ? 'var(--color-accent)' : 'var(--color-border)'}`,
                    backgroundColor: isSelected ? 'var(--color-accent-soft)' : 'var(--color-surface-alt)',
                    color: isSelected ? 'var(--color-accent-dark)' : 'var(--color-text-main)',
                    fontSize: '12px',
                    fontWeight: isSelected ? 700 : 500,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <b>{p.code}</b> {p.name}
                </button>
              );
            })}
          </div>

          {/* Hidden/Direct Code Input for test accessibility */}
          <div style={{ display: 'none' }}>
            <input
              id="evocare-patient-id-input"
              type="text"
              value={patientCode}
              onChange={(e) => setPatientCode(e.target.value.toUpperCase())}
            />
            <button
              id="evocare-patient-lookup-btn"
              type="button"
              onClick={() => handleLookup(patientCode)}
            >
              Lookup
            </button>
          </div>
        </div>

        {/* Patient Info Row */}
        {patientInfo && (
          <div
            style={{
              padding: '10px 14px',
              borderRadius: '8px',
              backgroundColor: 'var(--color-surface-alt)',
              border: '1px solid var(--color-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '16px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <UserCheck size={16} style={{ color: 'var(--color-accent)' }} />
              <div>
                <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-text-main)' }}>
                  {patientInfo.name}
                </span>
                <span style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginLeft: '6px' }}>
                  {patientInfo.age}y · {patientInfo.sex} · {patientCode}
                </span>
              </div>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Mail size={12} />
              <span>{patientInfo.email || 'lokanthsrihari7@gmail.com'}</span>
            </div>
          </div>
        )}

        {lookupError && (
          <div style={{ marginBottom: '14px', padding: '8px 12px', borderRadius: '6px', backgroundColor: 'var(--color-danger-soft)', color: 'var(--color-danger)', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertCircle size={14} />
            {lookupError}
          </div>
        )}

        {/* Step 2: Patient Consent Code Section */}
        <form onSubmit={handleVerifyOtp}>
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-text-main)' }}>
                6-Digit Consent Code
              </label>

              {!otpRequested ? (
                <button
                  id="evocare-request-code-btn"
                  type="button"
                  onClick={handleRequestOtp}
                  disabled={lookupLoading}
                  style={{
                    padding: '4px 10px',
                    borderRadius: '6px',
                    border: '1px solid var(--color-accent-border)',
                    backgroundColor: 'var(--color-accent-soft)',
                    color: 'var(--color-accent-dark)',
                    fontSize: '11px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  <Mail size={11} />
                  Send Code to Patient Email
                </button>
              ) : (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '11px', color: 'var(--color-success)', fontWeight: 600 }}>
                    Sent to Gmail
                  </span>
                  {generatedOtp && (
                    <button
                      type="button"
                      onClick={() => setEnteredOtp(generatedOtp)}
                      title="Click to fill demo code"
                      style={{
                        padding: '2px 6px',
                        borderRadius: '4px',
                        border: '1px dashed var(--color-accent)',
                        backgroundColor: 'var(--color-accent-soft)',
                        color: 'var(--color-accent-dark)',
                        fontFamily: 'monospace',
                        fontSize: '11px',
                        fontWeight: 700,
                        cursor: 'pointer',
                      }}
                    >
                      Fill: {generatedOtp}
                    </button>
                  )}
                </div>
              )}
            </div>

            <div style={{ position: 'relative' }}>
              <input
                id="evocare-otp-input"
                type="text"
                maxLength={10}
                value={enteredOtp}
                onChange={(e) => setEnteredOtp(e.target.value)}
                placeholder={otpRequested ? 'e.g. 7742' : 'Click "Send Code" or enter code'}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  border: '1.5px solid var(--color-border-strong)',
                  fontSize: '16px',
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontWeight: 700,
                  letterSpacing: '0.15em',
                  textAlign: 'center',
                  backgroundColor: 'var(--color-surface)',
                  color: 'var(--color-text-main)',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            </div>
          </div>

          {verifyError && (
            <div style={{ marginBottom: '14px', padding: '8px 12px', borderRadius: '6px', backgroundColor: 'var(--color-danger-soft)', color: 'var(--color-danger)', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <AlertCircle size={14} />
              {verifyError}
            </div>
          )}

          {verifySuccess && (
            <div style={{ marginBottom: '14px', padding: '8px 12px', borderRadius: '6px', backgroundColor: 'var(--color-success-soft)', color: 'var(--color-success-dark)', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle2 size={14} />
              Consent verified! Opening patient chart…
            </div>
          )}

          <div style={{ display: 'flex', gap: '8px' }}>
            {isModal && onCancel && (
              <button
                type="button"
                onClick={onCancel}
                style={{
                  flex: 1,
                  padding: '10px 14px',
                  borderRadius: '8px',
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'transparent',
                  color: 'var(--color-text-muted)',
                  fontSize: '13px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Cancel
              </button>
            )}

            <button
              id="evocare-verify-unlock-btn"
              type="submit"
              disabled={verifyLoading || verifySuccess}
              style={{
                flex: 2,
                padding: '11px 18px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: verifySuccess ? 'var(--color-success)' : 'var(--color-accent)',
                color: '#ffffff',
                fontSize: '13.5px',
                fontWeight: 700,
                cursor: verifyLoading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                boxShadow: '0 4px 12px -2px rgba(13, 110, 100, 0.35)',
                transition: 'all 0.15s ease',
              }}
            >
              <Lock size={14} />
              {verifyLoading ? 'Verifying…' : verifySuccess ? 'Unlocked' : 'Verify & Unlock Chart'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  if (isModal) {
    return (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.55)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px',
          zIndex: 9999,
        }}
      >
        {content}
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: '75vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px 20px',
      }}
    >
      {content}
    </div>
  );
};

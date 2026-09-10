import React, { useState, useEffect } from 'react';
import { Shield, UserCheck, Lock, CheckCircle2, AlertCircle, RefreshCw, Mail } from 'lucide-react';
import { authService } from '../../services/auth';

interface DoctorPatientAccessGateProps {
  initialPatientCode?: string;
  onPatientUnlocked: (patientCode: string) => void;
  onCancel?: () => void;
  isModal?: boolean;
}

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
        throw new Error(`Patient '${clean}' not found in registry.`);
      }
      const data = await res.json();
      setPatientInfo(data);
    } catch (err: any) {
      setPatientInfo(null);
      setLookupError(err.message || 'Failed to lookup patient.');
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
        throw new Error(data.detail || 'Failed to generate patient consent code.');
      }

      const data = await res.json();
      setOtpRequested(true);
      setGeneratedOtp(data.demo_code || null);
    } catch (err: any) {
      setVerifyError(err.message || 'Error requesting patient consent code.');
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
      setVerifyError('Please enter the 6-digit patient verification code.');
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
      }, 700);
    } catch (err: any) {
      setVerifyError(err.message || 'Verification failed. Please check the code.');
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
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04)',
        width: '100%',
        maxWidth: '560px',
        overflow: 'hidden',
      }}
    >
      {/* Header Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, var(--color-accent-dark) 0%, var(--color-accent) 50%, var(--color-accent-bright) 100%)',
          padding: '24px',
          color: 'var(--color-surface)',
          position: 'relative',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '12px',
              backgroundColor: 'rgba(255, 255, 255, 0.18)',
              backdropFilter: 'blur(8px)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Shield size={24} color="#ffffff" />
          </div>
          <div>
            <div style={{ fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.08em', opacity: 0.9, fontWeight: 700 }}>
              Physician Security Gate
            </div>
            <h2 style={{ fontSize: '20px', fontWeight: 800, margin: '2px 0 0 0', letterSpacing: '-0.02em' }}>
              2-Step Patient Record Verification
            </h2>
          </div>
        </div>
        <p style={{ margin: '12px 0 0 0', fontSize: '13px', opacity: 0.92, lineHeight: 1.45 }}>
          To maintain zero unauthorized clinical data exposure, enter the Patient ID and the patient's real-time consent code to unlock their longitudinal health memory.
        </p>
      </div>

      <div style={{ padding: '24px' }}>
        {/* Step 1: Patient Code Selection */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontSize: '13px', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '6px' }}>
            Step 1: Patient ID / Code
          </label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input
              id="evocare-patient-id-input"
              type="text"
              value={patientCode}
              onChange={(e) => setPatientCode(e.target.value.toUpperCase())}
              placeholder="e.g. P001 or P002"
              style={{
                flex: 1,
                padding: '10px 14px',
                borderRadius: '8px',
                border: '1.5px solid var(--color-border-strong)',
                fontSize: '14px',
                fontFamily: "'IBM Plex Mono', monospace",
                fontWeight: 600,
                outline: 'none',
              }}
            />
            <button
              id="evocare-patient-lookup-btn"
              type="button"
              onClick={() => handleLookup(patientCode)}
              disabled={lookupLoading || !patientCode.trim()}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: '1px solid var(--color-border-strong)',
                backgroundColor: 'var(--color-bg)',
                color: 'var(--color-text-secondary)',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <RefreshCw size={14} className={lookupLoading ? 'animate-spin' : ''} />
              Lookup
            </button>
          </div>

          {/* Preset patient quick chips */}
          <div style={{ marginTop: '8px' }}>
            <span style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
              Quick Select Demo Patient:
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {[
                { code: 'P001', name: 'Meenakshi' },
                { code: 'P002', name: 'Ananya' },
                { code: 'P003', name: 'Rajesh' },
                { code: 'P004', name: 'Sunita' },
                { code: 'P005', name: 'Vikramaditya' },
              ].map((p) => (
                <button
                  key={p.code}
                  type="button"
                  id={`evocare-quick-select-${p.code}`}
                  onClick={() => {
                    setPatientCode(p.code);
                    handleLookup(p.code);
                  }}
                  style={{
                    padding: '3px 8px',
                    borderRadius: '4px',
                    border: '1px solid',
                    borderColor: patientCode === p.code ? 'var(--color-accent)' : 'var(--color-border)',
                    backgroundColor: patientCode === p.code ? 'var(--color-accent-soft)' : 'var(--color-surface)',
                    color: patientCode === p.code ? 'var(--color-accent-dark)' : 'var(--color-text-secondary)',
                    fontSize: '11px',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  <b>{p.code}</b> ({p.name})
                </button>
              ))}
            </div>
          </div>

          {lookupError && (
            <div style={{ marginTop: '8px', padding: '8px 12px', borderRadius: '6px', backgroundColor: 'var(--color-danger-soft)', border: '1px solid var(--color-danger-border)', color: 'var(--color-danger-dark)', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <AlertCircle size={14} />
              {lookupError}
            </div>
          )}

          {/* Patient Card Preview */}
          {patientInfo && (
            <div
              style={{
                marginTop: '12px',
                padding: '12px 14px',
                borderRadius: '8px',
                backgroundColor: 'var(--color-success-soft)',
                border: '1px solid var(--color-success-border)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <UserCheck size={16} color="var(--color-success)" />
                  <span style={{ fontWeight: 700, color: 'var(--color-success-dark)', fontSize: '14px' }}>{patientInfo.name}</span>
                  <span style={{ fontSize: '11px', padding: '1px 6px', borderRadius: '4px', backgroundColor: 'var(--color-success-soft)', color: 'var(--color-success-dark)', fontWeight: 600 }}>
                    {patientCode}
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: 'var(--color-success)', marginTop: '2px' }}>
                  {patientInfo.age} yrs · {patientInfo.sex} · {patientInfo.location}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: 'var(--color-success-dark)', marginTop: '4px' }}>
                  <Mail size={12} />
                  <span>Patient Gmail: <b>{patientInfo.email || 'lokanthsrihari7@gmail.com'}</b></span>
                </div>
              </div>
              <span style={{ fontSize: '11px', color: 'var(--color-success)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                <CheckCircle2 size={13} /> Active Profile
              </span>
            </div>
          )}
        </div>

        {/* Step 2: Patient Consent Code Generation & Input */}
        {patientInfo && (
          <div style={{ borderTop: '1px solid var(--color-surface-alt)', paddingTop: '18px', marginTop: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-text-secondary)' }}>
                Step 2: Patient 2-Step Consent Code (Sent to Gmail)
              </label>
              {!otpRequested ? (
                <button
                  id="evocare-request-code-btn"
                  type="button"
                  onClick={handleRequestOtp}
                  disabled={lookupLoading}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '6px',
                    border: 'none',
                    backgroundColor: 'var(--color-accent)',
                    color: 'var(--color-surface)',
                    fontSize: '12px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  <Mail size={13} />
                  Send Code to Gmail
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleRequestOtp}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--color-accent)',
                    fontSize: '11px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    textDecoration: 'underline',
                  }}
                >
                  Resend Email
                </button>
              )}
            </div>

            {/* Live Gmail Sent Notification Banner */}
            {otpRequested && (
              <div
                style={{
                  marginBottom: '16px',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  backgroundColor: 'var(--color-success-soft)',
                  border: '1px solid var(--color-success-border)',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: 'var(--color-success-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-success)' }}>
                      <Mail size={15} />
                    </div>
                    <div>
                      <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-success-dark)' }}>
                        Verification Code Dispatched to Gmail
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--color-success)' }}>
                        Sent to: <b>{patientInfo.email || 'lokanthsrihari7@gmail.com'}</b>
                      </div>
                    </div>
                  </div>

                  {generatedOtp && (
                    <div
                      onClick={() => setEnteredOtp(generatedOtp)}
                      title="Click to auto-fill code (Demo Helper)"
                      style={{
                        fontFamily: "'IBM Plex Mono', monospace",
                        fontSize: '16px',
                        fontWeight: 800,
                        letterSpacing: '0.1em',
                        backgroundColor: 'var(--color-warning-border)',
                        color: 'var(--color-warning-dark)',
                        padding: '3px 10px',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        border: '1px dashed var(--color-warning)',
                      }}
                    >
                      {generatedOtp}
                    </div>
                  )}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--color-success-dark)', marginTop: '6px', fontStyle: 'italic' }}>
                  The patient has received their 6-digit consent code at <b>{patientInfo.email || 'lokanthsrihari7@gmail.com'}</b>. Ask the patient for the code to unlock this profile.
                </div>
              </div>
            )}

            <form onSubmit={handleVerifyOtp}>
              <div style={{ marginBottom: '16px' }}>
                <div style={{ position: 'relative' }}>
                  <input
                    id="evocare-otp-input"
                    type="text"
                    maxLength={10}
                    value={enteredOtp}
                    onChange={(e) => setEnteredOtp(e.target.value)}
                    placeholder="Enter 6-digit patient code"
                    disabled={!otpRequested || verifyLoading || verifySuccess}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      borderRadius: '8px',
                      border: '1.5px solid var(--color-border-strong)',
                      fontSize: '18px',
                      fontFamily: "'IBM Plex Mono', monospace",
                      fontWeight: 700,
                      letterSpacing: '0.2em',
                      textAlign: 'center',
                      backgroundColor: !otpRequested ? 'var(--color-bg)' : 'var(--color-surface)',
                      outline: 'none',
                      boxSizing: 'border-box',
                    }}
                  />
                </div>
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '4px', textAlign: 'center' }}>
                  {otpRequested ? 'Code sent to patient phone/app. Ask patient for the 6 digits.' : 'Click "Request Consent Code" above to generate code.'}
                </div>
              </div>

              {verifyError && (
                <div style={{ marginBottom: '14px', padding: '8px 12px', borderRadius: '6px', backgroundColor: 'var(--color-danger-soft)', border: '1px solid var(--color-danger-border)', color: 'var(--color-danger-dark)', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <AlertCircle size={14} />
                  {verifyError}
                </div>
              )}

              {verifySuccess && (
                <div style={{ marginBottom: '14px', padding: '10px 12px', borderRadius: '6px', backgroundColor: 'var(--color-success-soft)', border: '1px solid var(--color-success-border)', color: 'var(--color-success-dark)', fontSize: '13px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle2 size={16} />
                  2-Step Verification verified! Unlocking records...
                </div>
              )}

              <div style={{ display: 'flex', gap: '10px', marginTop: '8px' }}>
                {isModal && onCancel && (
                  <button
                    type="button"
                    onClick={onCancel}
                    style={{
                      flex: 1,
                      padding: '12px 16px',
                      borderRadius: '8px',
                      border: '1px solid var(--color-border-strong)',
                      backgroundColor: 'var(--color-surface)',
                      color: 'var(--color-text-secondary)',
                      fontSize: '13px',
                      fontWeight: 700,
                      cursor: 'pointer',
                    }}
                  >
                    Cancel
                  </button>
                )}
                <button
                  id="evocare-verify-unlock-btn"
                  type="submit"
                  disabled={!otpRequested || !enteredOtp.trim() || verifyLoading || verifySuccess}
                  style={{
                    flex: 2,
                    padding: '12px 20px',
                    borderRadius: '8px',
                    border: 'none',
                    backgroundColor: verifySuccess ? 'var(--color-success)' : (!otpRequested || !enteredOtp.trim()) ? 'var(--color-text-faint)' : 'var(--color-accent)',
                    color: 'var(--color-surface)',
                    fontSize: '14px',
                    fontWeight: 700,
                    cursor: (!otpRequested || !enteredOtp.trim() || verifyLoading) ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    boxShadow: '0 2px 4px rgba(13, 110, 100, 0.2)',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <Lock size={15} />
                  {verifyLoading ? 'Verifying Consent Code…' : verifySuccess ? 'Access Granted' : 'Verify & Unlock Patient Chart'}
                </button>
              </div>
            </form>
          </div>
        )}
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
          backgroundColor: 'rgba(28, 26, 20, 0.65)',
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
        minHeight: '80vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px 20px',
      }}
    >
      {content}
    </div>
  );
};

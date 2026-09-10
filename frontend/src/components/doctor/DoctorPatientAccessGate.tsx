import React, { useState, useEffect } from 'react';
import { Shield, KeyRound, UserCheck, Lock, CheckCircle2, AlertCircle, RefreshCw, Sparkles } from 'lucide-react';
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
  const [patientInfo, setPatientInfo] = useState<{ name: string; age: number; sex: string; location: string } | null>(null);
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
        backgroundColor: '#ffffff',
        borderRadius: '16px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04)',
        width: '100%',
        maxWidth: '560px',
        overflow: 'hidden',
      }}
    >
      {/* Header Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, #0369a1 0%, #0284c7 50%, #0ea5e9 100%)',
          padding: '24px',
          color: '#ffffff',
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
          <label style={{ display: 'block', fontSize: '13px', fontWeight: 700, color: '#334155', marginBottom: '6px' }}>
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
                border: '1.5px solid #cbd5e1',
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
                border: '1px solid #cbd5e1',
                backgroundColor: '#f8fafc',
                color: '#334155',
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
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
            <span style={{ fontSize: '11px', color: '#64748b', fontWeight: 600 }}>Quick select:</span>
            {['P001', 'P002'].map((code) => (
              <button
                key={code}
                type="button"
                onClick={() => {
                  setPatientCode(code);
                  handleLookup(code);
                }}
                style={{
                  padding: '2px 8px',
                  borderRadius: '4px',
                  border: '1px solid #e2e8f0',
                  backgroundColor: patientCode === code ? '#e0f2fe' : '#ffffff',
                  color: patientCode === code ? '#0369a1' : '#64748b',
                  fontSize: '11px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                {code} {code === 'P001' ? '(Meenakshi)' : '(Patient 2)'}
              </button>
            ))}
          </div>

          {lookupError && (
            <div style={{ marginTop: '8px', padding: '8px 12px', borderRadius: '6px', backgroundColor: '#fef2f2', border: '1px solid #fecaca', color: '#b91c1c', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
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
                backgroundColor: '#f0fdf4',
                border: '1px solid #bbf7d0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <UserCheck size={16} color="#15803d" />
                  <span style={{ fontWeight: 700, color: '#166534', fontSize: '14px' }}>{patientInfo.name}</span>
                  <span style={{ fontSize: '11px', padding: '1px 6px', borderRadius: '4px', backgroundColor: '#dcfce7', color: '#166534', fontWeight: 600 }}>
                    {patientCode}
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: '#15803d', marginTop: '2px' }}>
                  {patientInfo.age} yrs · {patientInfo.sex} · {patientInfo.location}
                </div>
              </div>
              <span style={{ fontSize: '11px', color: '#16a34a', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                <CheckCircle2 size={13} /> Verified Patient
              </span>
            </div>
          )}
        </div>

        {/* Step 2: Patient Consent Code Generation & Input */}
        {patientInfo && (
          <div style={{ borderTop: '1px solid #f1f5f9', paddingTop: '18px', marginTop: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label style={{ fontSize: '13px', fontWeight: 700, color: '#334155' }}>
                Step 2: Patient 2-Step Consent Code
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
                    backgroundColor: '#0284c7',
                    color: '#ffffff',
                    fontSize: '12px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  <KeyRound size={13} />
                  Request Consent Code
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleRequestOtp}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#0284c7',
                    fontSize: '11px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    textDecoration: 'underline',
                  }}
                >
                  Resend Code
                </button>
              )}
            </div>

            {/* Simulated Live Patient Consent Banner */}
            {otpRequested && generatedOtp && (
              <div
                style={{
                  marginBottom: '16px',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  backgroundColor: '#fefce8',
                  border: '1px solid #fef08a',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#854d0e', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase' }}>
                    <Sparkles size={13} /> Patient Consent Code (Demo Simulation)
                  </div>
                  <div style={{ fontSize: '12px', color: '#713f12', marginTop: '2px' }}>
                    Patient <b>{patientInfo.name}</b> authorized access with code:
                  </div>
                </div>
                <div
                  onClick={() => setEnteredOtp(generatedOtp)}
                  title="Click to auto-fill code"
                  style={{
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontSize: '18px',
                    fontWeight: 800,
                    letterSpacing: '0.15em',
                    backgroundColor: '#fef08a',
                    color: '#713f12',
                    padding: '4px 12px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    border: '1px dashed #ca8a04',
                  }}
                >
                  {generatedOtp}
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
                      border: '1.5px solid #cbd5e1',
                      fontSize: '18px',
                      fontFamily: "'IBM Plex Mono', monospace",
                      fontWeight: 700,
                      letterSpacing: '0.2em',
                      textAlign: 'center',
                      backgroundColor: !otpRequested ? '#f8fafc' : '#ffffff',
                      outline: 'none',
                      boxSizing: 'border-box',
                    }}
                  />
                </div>
                <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px', textAlign: 'center' }}>
                  {otpRequested ? 'Code sent to patient phone/app. Ask patient for the 6 digits.' : 'Click "Request Consent Code" above to generate code.'}
                </div>
              </div>

              {verifyError && (
                <div style={{ marginBottom: '14px', padding: '8px 12px', borderRadius: '6px', backgroundColor: '#fef2f2', border: '1px solid #fecaca', color: '#b91c1c', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <AlertCircle size={14} />
                  {verifyError}
                </div>
              )}

              {verifySuccess && (
                <div style={{ marginBottom: '14px', padding: '10px 12px', borderRadius: '6px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', color: '#166534', fontSize: '13px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
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
                      border: '1px solid #cbd5e1',
                      backgroundColor: '#ffffff',
                      color: '#475569',
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
                    backgroundColor: verifySuccess ? '#16a34a' : (!otpRequested || !enteredOtp.trim()) ? '#94a3b8' : '#0284c7',
                    color: '#ffffff',
                    fontSize: '14px',
                    fontWeight: 700,
                    cursor: (!otpRequested || !enteredOtp.trim() || verifyLoading) ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    boxShadow: '0 2px 4px rgba(2, 132, 199, 0.2)',
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
          backgroundColor: 'rgba(15, 23, 42, 0.65)',
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

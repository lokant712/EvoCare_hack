import React, { useState, useEffect } from 'react';
import { UserPlus, CheckCircle2, Clock, AlertCircle, Trash2, HeartHandshake, ShieldCheck } from 'lucide-react';
import { authService, AuthUser } from '../../services/auth';

interface PatientCaregiverConnectionModalProps {
  patientCode: string;
  patientName: string;
  user: AuthUser;
  isOpen: boolean;
  onClose: () => void;
  onConnectionUpdated?: () => void;
}

interface CaregiverOption {
  id: number;
  username: string;
  full_name: string;
  email: string;
}

interface ConnectionRecord {
  id: number;
  patient_code: string;
  patient_name: string;
  caregiver_user_id: number;
  caregiver_name: string;
  caregiver_username: string;
  caregiver_email: string;
  status: string;
  requested_by: string;
  notes: string | null;
  created_at: string;
}

export const PatientCaregiverConnectionModal: React.FC<PatientCaregiverConnectionModalProps> = ({
  patientCode,
  patientName,
  isOpen,
  onClose,
  onConnectionUpdated,
}) => {
  const [caregivers, setCaregivers] = useState<CaregiverOption[]>([]);
  const [myConnections, setMyConnections] = useState<ConnectionRecord[]>([]);
  const [selectedCaregiverId, setSelectedCaregiverId] = useState<number | null>(null);
  const [notes, setNotes] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const fetchData = async () => {
    setMessage(null);
    try {
      const token = authService.getToken();
      const [cgRes, connRes] = await Promise.all([
        fetch('/api/caregiver-connections/caregivers', {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`/api/caregiver-connections/my-connections?patient_code=${patientCode}`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (cgRes.ok) {
        const cgData = await cgRes.json();
        setCaregivers(cgData);
        if (cgData.length > 0 && !selectedCaregiverId) {
          setSelectedCaregiverId(cgData[0].id);
        }
      }

      if (connRes.ok) {
        const connData = await connRes.json();
        setMyConnections(connData);
      }
    } catch (err: any) {
      setMessage({ text: 'Failed to load caretaker data.', type: 'error' });
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchData();
    }
  }, [isOpen, patientCode]);

  const handleSendRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCaregiverId) return;

    setSubmitting(true);
    setMessage(null);

    try {
      const token = authService.getToken();
      const res = await fetch('/api/caregiver-connections/request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          patient_code: patientCode,
          caregiver_user_id: selectedCaregiverId,
          notes: notes || undefined,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to send pairing request.');
      }

      setMessage({ text: data.message || 'Pairing request sent!', type: 'success' });
      fetchData();
      if (onConnectionUpdated) onConnectionUpdated();
    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDisconnect = async (connectionId: number) => {
    if (!window.confirm('Are you sure you want to disconnect this caretaker?')) return;
    setSubmitting(true);

    try {
      const token = authService.getToken();
      const res = await fetch(`/api/caregiver-connections/${connectionId}/disconnect`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        throw new Error('Failed to disconnect caretaker.');
      }

      setMessage({ text: 'Caretaker has been disconnected.', type: 'success' });
      fetchData();
      if (onConnectionUpdated) onConnectionUpdated();
    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  const activeConnection = myConnections.find((c) => c.status === 'APPROVED');
  const pendingConnection = myConnections.find((c) => c.status === 'PENDING');

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
      <div
        style={{
          backgroundColor: '#ffffff',
          borderRadius: '16px',
          border: '1px solid #e2e8f0',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
          width: '100%',
          maxWidth: '520px',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div
          style={{
            background: 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
            padding: '20px 24px',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <HeartHandshake size={24} />
            <div>
              <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700 }}>
                My Caretaker Connection
              </h3>
              <div style={{ fontSize: '12px', opacity: 0.9 }}>
                Patient: <b>{patientName}</b> ({patientCode})
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#ffffff',
              fontSize: '20px',
              cursor: 'pointer',
              fontWeight: 700,
            }}
          >
            ×
          </button>
        </div>

        <div style={{ padding: '24px' }}>
          {message && (
            <div
              style={{
                padding: '10px 14px',
                borderRadius: '8px',
                backgroundColor: message.type === 'success' ? '#f0fdf4' : '#fef2f2',
                border: '1px solid',
                borderColor: message.type === 'success' ? '#bbf7d0' : '#fecaca',
                color: message.type === 'success' ? '#166534' : '#b91c1c',
                fontSize: '13px',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              {message.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
              <span>{message.text}</span>
            </div>
          )}

          {/* Case 1: Active Connected Caretaker */}
          {activeConnection ? (
            <div
              style={{
                padding: '16px',
                borderRadius: '10px',
                backgroundColor: '#f0fdf4',
                border: '1.5px solid #86efac',
                marginBottom: '16px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '50%', backgroundColor: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#15803d' }}>
                    <ShieldCheck size={20} />
                  </div>
                  <div>
                    <div style={{ fontSize: '15px', fontWeight: 700, color: '#166534' }}>
                      {activeConnection.caregiver_name}
                    </div>
                    <div style={{ fontSize: '12px', color: '#15803d' }}>
                      @{activeConnection.caregiver_username} · {activeConnection.caregiver_email}
                    </div>
                  </div>
                </div>
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    padding: '3px 8px',
                    borderRadius: '6px',
                    backgroundColor: '#dcfce7',
                    color: '#166534',
                  }}
                >
                  CONNECTED
                </span>
              </div>
              <div style={{ fontSize: '12px', color: '#166534', marginTop: '10px' }}>
                ✓ This caretaker has permanent permission to record observations and assist with your care.
              </div>

              <div style={{ marginTop: '16px', borderTop: '1px solid #bbf7d0', paddingTop: '12px', display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => handleDisconnect(activeConnection.id)}
                  disabled={submitting}
                  style={{
                    padding: '6px 14px',
                    borderRadius: '6px',
                    border: '1px solid #fecaca',
                    backgroundColor: '#fff1f2',
                    color: '#e11d48',
                    fontSize: '12px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  <Trash2 size={13} />
                  Remove Caretaker
                </button>
              </div>
            </div>
          ) : pendingConnection ? (
            /* Case 2: Pending Approval */
            <div
              style={{
                padding: '16px',
                borderRadius: '10px',
                backgroundColor: '#fefce8',
                border: '1.5px solid #fde047',
                marginBottom: '16px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Clock size={20} color="#854d0e" />
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: 700, color: '#713f12' }}>
                      Request Sent to: {pendingConnection.caregiver_name}
                    </div>
                    <div style={{ fontSize: '12px', color: '#854d0e' }}>
                      Awaiting caregiver approval.
                    </div>
                  </div>
                </div>
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    padding: '3px 8px',
                    borderRadius: '6px',
                    backgroundColor: '#fef08a',
                    color: '#854d0e',
                  }}
                >
                  PENDING
                </span>
              </div>

              <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => handleDisconnect(pendingConnection.id)}
                  disabled={submitting}
                  style={{
                    padding: '4px 10px',
                    borderRadius: '6px',
                    border: '1px solid #cbd5e1',
                    backgroundColor: '#ffffff',
                    color: '#64748b',
                    fontSize: '11px',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Cancel Request
                </button>
              </div>
            </div>
          ) : (
            /* Case 3: Select and Connect Caregiver */
            <form onSubmit={handleSendRequest}>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 700, color: '#334155', marginBottom: '6px' }}>
                  Choose a Registered Caretaker:
                </label>
                <select
                  value={selectedCaregiverId || ''}
                  onChange={(e) => setSelectedCaregiverId(Number(e.target.value))}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    border: '1.5px solid #cbd5e1',
                    fontSize: '14px',
                    outline: 'none',
                    backgroundColor: '#ffffff',
                  }}
                >
                  {caregivers.map((cg) => (
                    <option key={cg.id} value={cg.id}>
                      {cg.full_name} (@{cg.username}) — {cg.email}
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 700, color: '#334155', marginBottom: '6px' }}>
                  Optional Note / Relationship:
                </label>
                <input
                  type="text"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. Primary family caregiver, daily home visits"
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    border: '1.5px solid #cbd5e1',
                    fontSize: '13px',
                    outline: 'none',
                    boxSizing: 'border-box',
                  }}
                />
              </div>

              <button
                type="submit"
                disabled={submitting || !selectedCaregiverId}
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '8px',
                  border: 'none',
                  backgroundColor: '#059669',
                  color: '#ffffff',
                  fontSize: '14px',
                  fontWeight: 700,
                  cursor: submitting ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                }}
              >
                <UserPlus size={16} />
                {submitting ? 'Sending Request…' : 'Send Caretaker Pairing Request'}
              </button>
            </form>
          )}

          <div style={{ marginTop: '20px', borderTop: '1px solid #f1f5f9', paddingTop: '12px', display: 'flex', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '8px 16px',
                borderRadius: '6px',
                border: '1px solid #cbd5e1',
                backgroundColor: '#ffffff',
                color: '#475569',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { HeartHandshake, CheckCircle2, Trash2, Users, AlertCircle } from 'lucide-react';
import { authService } from '../../services/auth';

interface CaregiverRequestNotificationBannerProps {
  onConnectionsChanged?: () => void;
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

export const CaregiverRequestNotificationBanner: React.FC<CaregiverRequestNotificationBannerProps> = ({
  onConnectionsChanged,
}) => {
  const [connections, setConnections] = useState<ConnectionRecord[]>([]);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const fetchConnections = async () => {
    try {
      const token = authService.getToken();
      const res = await fetch('/api/caregiver-connections/my-connections', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setConnections(data);
      }
    } catch (err) {
      // ignore silent fetch errors
    }
  };

  useEffect(() => {
    fetchConnections();
  }, []);

  const handleRespond = async (connectionId: number, action: 'APPROVE' | 'REJECT') => {
    setActionLoading(connectionId);
    setMessage(null);

    try {
      const token = authService.getToken();
      const res = await fetch(`/api/caregiver-connections/${connectionId}/respond`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ action }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to respond to request.');
      }

      setMessage({ text: data.message || `Request ${action.toLowerCase()}d successfully.`, type: 'success' });
      fetchConnections();
      if (onConnectionsChanged) onConnectionsChanged();
    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  const handleDisconnect = async (connectionId: number) => {
    if (!window.confirm('Are you sure you want to remove this patient pairing?')) return;
    setActionLoading(connectionId);

    try {
      const token = authService.getToken();
      const res = await fetch(`/api/caregiver-connections/${connectionId}/disconnect`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        throw new Error('Failed to remove patient connection.');
      }

      setMessage({ text: 'Patient connection removed.', type: 'success' });
      fetchConnections();
      if (onConnectionsChanged) onConnectionsChanged();
    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  const pendingRequests = connections.filter((c) => c.status === 'PENDING');
  const approvedConnections = connections.filter((c) => c.status === 'APPROVED');

  if (pendingRequests.length === 0 && approvedConnections.length === 0) {
    return null;
  }

  return (
    <div style={{ marginBottom: '20px' }}>
      {message && (
        <div
          style={{
            padding: '10px 14px',
            borderRadius: '8px',
            backgroundColor: message.type === 'success' ? 'var(--color-success-soft)' : 'var(--color-danger-soft)',
            border: '1px solid',
            borderColor: message.type === 'success' ? 'var(--color-success-border)' : 'var(--color-danger-border)',
            color: message.type === 'success' ? 'var(--color-success-dark)' : 'var(--color-danger-dark)',
            fontSize: '13px',
            marginBottom: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          {message.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
          <span>{message.text}</span>
        </div>
      )}

      {/* Incoming Pending Pairing Requests */}
      {pendingRequests.map((req) => (
        <div
          key={req.id}
          style={{
            padding: '16px 20px',
            borderRadius: '12px',
            backgroundColor: 'var(--color-warning-soft)',
            border: '1.5px solid var(--color-warning-border)',
            boxShadow: '0 2px 4px rgba(0,0,0,0.03)',
            marginBottom: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', backgroundColor: 'var(--color-warning-border)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-warning-dark)' }}>
              <HeartHandshake size={22} />
            </div>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 800, color: 'var(--color-warning-dark)' }}>
                Incoming Patient Pairing Request
              </div>
              <div style={{ fontSize: '13px', color: 'var(--color-warning-dark)', marginTop: '2px' }}>
                Patient <b>{req.patient_name}</b> ({req.patient_code}) requested you as their primary caretaker.
                {req.notes && <span style={{ fontStyle: 'italic', marginLeft: '6px' }}>"{req.notes}"</span>}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              id={`evocare-approve-btn-${req.id}`}
              type="button"
              onClick={() => handleRespond(req.id, 'APPROVE')}
              disabled={actionLoading === req.id}
              style={{
                padding: '8px 16px',
                borderRadius: '6px',
                border: 'none',
                backgroundColor: 'var(--color-success)',
                color: '#ffffff',
                fontSize: '13px',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <CheckCircle2 size={15} />
              Approve Pairing
            </button>
            <button
              id={`evocare-reject-btn-${req.id}`}
              type="button"
              onClick={() => handleRespond(req.id, 'REJECT')}
              disabled={actionLoading === req.id}
              style={{
                padding: '8px 14px',
                borderRadius: '6px',
                border: '1px solid var(--color-border-strong)',
                backgroundColor: 'var(--color-surface)',
                color: 'var(--color-text-secondary)',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Reject
            </button>
          </div>
        </div>
      ))}

      {/* Active Paired Patients Section */}
      {approvedConnections.length > 0 && (
        <div
          style={{
            padding: '12px 16px',
            borderRadius: '10px',
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '10px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Users size={16} color="var(--color-success)" />
            <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-text-main)' }}>
              Connected Patients ({approvedConnections.length}):
            </span>
            <div style={{ display: 'flex', gap: '6px' }}>
              {approvedConnections.map((c) => (
                <span
                  key={c.id}
                  style={{
                    fontSize: '11px',
                    fontWeight: 600,
                    padding: '2px 8px',
                    borderRadius: '4px',
                    backgroundColor: 'var(--color-success-soft)',
                    color: 'var(--color-success-dark)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  {c.patient_name} ({c.patient_code})
                  <button
                    onClick={() => handleDisconnect(c.id)}
                    title="Remove patient connection"
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--color-danger-dark)',
                      cursor: 'pointer',
                      padding: 0,
                      display: 'flex',
                    }}
                  >
                    <Trash2 size={11} />
                  </button>
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

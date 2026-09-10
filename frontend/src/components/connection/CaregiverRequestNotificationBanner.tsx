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
            backgroundColor: message.type === 'success' ? '#f0fdf4' : '#fef2f2',
            border: '1px solid',
            borderColor: message.type === 'success' ? '#bbf7d0' : '#fecaca',
            color: message.type === 'success' ? '#166534' : '#b91c1c',
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
            backgroundColor: '#fefce8',
            border: '1.5px solid #fde047',
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
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', backgroundColor: '#fef08a', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#854d0e' }}>
              <HeartHandshake size={22} />
            </div>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 800, color: '#713f12' }}>
                Incoming Patient Pairing Request
              </div>
              <div style={{ fontSize: '13px', color: '#854d0e', marginTop: '2px' }}>
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
                backgroundColor: '#16a34a',
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
                border: '1px solid #cbd5e1',
                backgroundColor: '#ffffff',
                color: '#475569',
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
            backgroundColor: '#ffffff',
            border: '1px solid #e2e8f0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '10px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Users size={16} color="#059669" />
            <span style={{ fontSize: '13px', fontWeight: 700, color: '#0f172a' }}>
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
                    backgroundColor: '#dcfce7',
                    color: '#166534',
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
                      color: '#b91c1c',
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

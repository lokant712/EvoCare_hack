import React, { useState, useEffect, useCallback } from 'react';
import {
  Users, UserPlus, UserCheck, UserX,
  Search, RefreshCw, AlertCircle, CheckCircle2, X,
  Stethoscope, HeartHandshake, User, Shield
} from 'lucide-react';
import { AuthUser, authService } from '../../services/auth';

const API_BASE = '/api';
const authHeaders = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${authService.getToken() || ''}`,
});

interface UserRecord {
  id: number;
  username: string;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string | null;
  last_login_at: string | null;
  authorized_patients: string[];
}

const ROLE_META: Record<string, { label: string; color: string; bg: string; icon: React.ReactNode }> = {
  DOCTOR:    { label: 'Doctor',    color: 'var(--color-accent-dark)', bg: 'var(--color-accent-soft)', icon: <Stethoscope size={13} /> },
  CAREGIVER: { label: 'Caregiver', color: 'var(--color-success-dark)', bg: 'var(--color-success-soft)', icon: <HeartHandshake size={13} /> },
  PATIENT:   { label: 'Patient',   color: 'var(--color-plum-dark)', bg: 'var(--color-plum-soft)', icon: <User size={13} /> },
  ADMIN:     { label: 'Admin',     color: 'var(--color-warning-dark)', bg: 'var(--color-warning-soft)', icon: <Shield size={13} /> },
};

const ROLE_FILTER_TABS = [
  { key: 'ALL',      label: 'All Users' },
  { key: 'DOCTOR',   label: 'Doctors' },
  { key: 'CAREGIVER',label: 'Caretakers' },
  { key: 'PATIENT',  label: 'Patients' },
  { key: 'ADMIN',    label: 'Admins' },
];

interface AddUserForm {
  username: string; password: string; full_name: string;
  email: string; role: string; patient_code: string;
}

const emptyForm: AddUserForm = {
  username: '', password: '', full_name: '', email: '', role: 'DOCTOR', patient_code: ''
};

interface Props { user: AuthUser; }

export const AdminUserManagement: React.FC<Props> = ({ user }) => {
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filterRole, setFilterRole] = useState('ALL');
  const [search, setSearch] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [form, setForm] = useState<AddUserForm>(emptyForm);
  const [formError, setFormError] = useState<string | null>(null);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);
  const [togglingId, setTogglingId] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // OTP verification modal state
  const [otpModal, setOtpModal] = useState<{ userId: number; username: string; email: string; otp?: string } | null>(null);
  const [otpInput, setOtpInput] = useState('');
  const [otpError, setOtpError] = useState<string | null>(null);
  const [otpVerifying, setOtpVerifying] = useState(false);
  const [pendingOtp, setPendingOtp] = useState<{ otp: string; message: string } | null>(null); // shown after create

  const fetchUsers = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const r = await fetch(`${API_BASE}/admin/users`, { headers: authHeaders() });
      if (!r.ok) throw new Error(`Server error ${r.status}`);
      setUsers(await r.json());
    } catch (e: any) {
      setError(e.message || 'Failed to load users');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleToggle = async (u: UserRecord) => {
    if (u.id === Number((user as any).id)) return; // can't disable self
    setTogglingId(u.id);
    try {
      const r = await fetch(`${API_BASE}/admin/users/${u.id}/toggle`, {
        method: 'PATCH', headers: authHeaders()
      });
      if (!r.ok) throw new Error((await r.json()).detail || 'Toggle failed');
      const updated = await r.json();
      setUsers(prev => prev.map(x => x.id === u.id ? { ...x, is_active: updated.is_active } : x));
    } catch (e: any) {
      setError(e.message);
    } finally { setTogglingId(null); }
  };

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true); setFormError(null); setFormSuccess(null);
    try {
      const r = await fetch(`${API_BASE}/admin/users`, {
        method: 'POST', headers: authHeaders(), body: JSON.stringify(form)
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || 'Failed to create user');
      setForm(emptyForm);
      setShowAddForm(false);
      fetchUsers();
      // Show OTP panel immediately after creation
      if (d.verification_otp) {
        setPendingOtp({ otp: d.verification_otp, message: d.otp_message });
        setOtpModal({ userId: d.id, username: d.username, email: d.email });
      }
    } catch (e: any) {
      setFormError(e.message);
    } finally { setSubmitting(false); }
  };

  const handleVerifyOtp = async () => {
    if (!otpModal) return;
    setOtpVerifying(true); setOtpError(null);
    try {
      const r = await fetch(`${API_BASE}/admin/users/${otpModal.userId}/verify`, {
        method: 'POST', headers: authHeaders(), body: JSON.stringify({ otp: otpInput })
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || 'Verification failed');
      setUsers(prev => prev.map(x => x.id === otpModal.userId ? { ...x, is_verified: true } : x));
      setOtpModal(null); setPendingOtp(null); setOtpInput('');
      fetchUsers();
    } catch (e: any) {
      setOtpError(e.message);
    } finally { setOtpVerifying(false); }
  };

  const handleResendOtp = async (u: UserRecord) => {
    try {
      const r = await fetch(`${API_BASE}/admin/users/${u.id}/resend-otp`, {
        method: 'POST', headers: authHeaders()
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || 'Resend failed');
      setPendingOtp({ otp: d.verification_otp, message: d.otp_message });
      setOtpInput('');
      setOtpError(null);
      setOtpModal({ userId: u.id, username: u.username, email: u.email });
    } catch (e: any) { setError(e.message); }
  };


  const filtered = users.filter(u => {
    const matchRole = filterRole === 'ALL' || u.role === filterRole;
    const q = search.toLowerCase();
    const matchSearch = !q || u.username.toLowerCase().includes(q) ||
      u.full_name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q);
    return matchRole && matchSearch;
  });

  const counts = { ALL: users.length, ...Object.fromEntries(
    ['DOCTOR','CAREGIVER','PATIENT','ADMIN'].map(r => [r, users.filter(u => u.role === r).length])
  )};

  // ─── Styles ──────────────────────────────────────────────────────────────
  const card: React.CSSProperties = {
    backgroundColor: 'var(--color-surface)', borderRadius: '12px', border: '1px solid var(--color-border)',
    boxShadow: '0 2px 8px rgba(0,0,0,0.04)', overflow: 'hidden'
  };
  const inputStyle: React.CSSProperties = {
    width: '100%', padding: '9px 12px', borderRadius: '7px',
    border: '1px solid var(--color-border-strong)', fontSize: '13px', color: 'var(--color-text-main)',
    outline: 'none', boxSizing: 'border-box', backgroundColor: 'var(--color-bg)'
  };

  return (
    <div style={{ padding: '28px 24px', maxWidth: '1100px', margin: '0 auto', fontFamily: 'var(--font-sans)' }}>

      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', backgroundColor: 'var(--color-warning-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Users size={20} color="var(--color-warning)" />
          </div>
          <div>
            <h2 style={{ margin: 0, fontSize: '17px', fontWeight: 700, color: 'var(--color-text-main)' }}>User Management</h2>
            <p style={{ margin: '2px 0 0', fontSize: '12px', color: 'var(--color-text-muted)' }}>Manage all system accounts — create, view, enable or disable</p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button onClick={fetchUsers} disabled={loading} style={{ padding: '8px 12px', borderRadius: '7px', border: '1px solid var(--color-border)', backgroundColor: 'var(--color-surface)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
            <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
          </button>
          <button onClick={() => { setShowAddForm(true); setFormError(null); setFormSuccess(null); }}
            style={{ padding: '8px 16px', borderRadius: '7px', border: 'none', backgroundColor: 'var(--color-accent)', color: '#fff', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '7px', fontSize: '13px', fontWeight: 700, boxShadow: '0 2px 6px rgba(37,99,235,0.25)' }}>
            <UserPlus size={15} /> Add User
          </button>
        </div>
      </div>

      {/* Stats row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '20px' }}>
        {(['DOCTOR','CAREGIVER','PATIENT','ADMIN'] as const).map(role => {
          const m = ROLE_META[role];
          const active = users.filter(u => u.role === role && u.is_active).length;
          const total = users.filter(u => u.role === role).length;
          return (
            <div key={role} style={{ ...card, padding: '14px 16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span style={{ padding: '5px', borderRadius: '7px', backgroundColor: m.bg, color: m.color, display: 'flex' }}>{m.icon}</span>
                <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-muted)' }}>{m.label}s</span>
              </div>
              <div style={{ fontSize: '22px', fontWeight: 800, color: m.color }}>{total}</div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-faint)', marginTop: '2px' }}>{active} active · {total - active} disabled</div>
            </div>
          );
        })}
      </div>

      {/* Add User Modal */}
      {showAddForm && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.45)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ ...card, width: '480px', maxHeight: '90vh', overflowY: 'auto', padding: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <UserPlus size={20} color="var(--color-accent)" />
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: 'var(--color-text-main)' }}>Add New User</h3>
              </div>
              <button onClick={() => setShowAddForm(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-faint)' }}><X size={20} /></button>
            </div>

            {formError && (
              <div style={{ backgroundColor: 'var(--color-danger-soft)', border: '1px solid var(--color-danger-border)', borderRadius: '7px', padding: '10px 14px', marginBottom: '14px', display: 'flex', gap: '8px', alignItems: 'flex-start', fontSize: '12px', color: 'var(--color-danger-dark)' }}>
                <AlertCircle size={14} style={{ flexShrink: 0, marginTop: '1px' }} /> {formError}
              </div>
            )}
            {formSuccess && (
              <div style={{ backgroundColor: 'var(--color-success-soft)', border: '1px solid var(--color-success-border)', borderRadius: '7px', padding: '10px 14px', marginBottom: '14px', display: 'flex', gap: '8px', alignItems: 'center', fontSize: '12px', color: 'var(--color-success-dark)' }}>
                <CheckCircle2 size={14} /> {formSuccess}
              </div>
            )}

            <form onSubmit={handleAddUser}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {[
                  { label: 'Full Name *', key: 'full_name', type: 'text', placeholder: 'e.g. Dr. Arjun Mehta' },
                  { label: 'Username *', key: 'username', type: 'text', placeholder: 'e.g. doctor.arjun' },
                  { label: 'Email *', key: 'email', type: 'email', placeholder: 'e.g. arjun@hospital.com' },
                  { label: 'Password *', key: 'password', type: 'password', placeholder: 'Min 8 characters' },
                ].map(({ label, key, type, placeholder }) => (
                  <div key={key}>
                    <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', display: 'block', marginBottom: '5px' }}>{label}</label>
                    <input
                      type={type} placeholder={placeholder} required
                      value={(form as any)[key]}
                      onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
                      style={inputStyle}
                    />
                  </div>
                ))}

                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', display: 'block', marginBottom: '5px' }}>Role *</label>
                  <select value={form.role} onChange={e => setForm(f => ({ ...f, role: e.target.value }))} style={{ ...inputStyle, cursor: 'pointer' }}>
                    <option value="DOCTOR">Doctor</option>
                    <option value="CAREGIVER">Caretaker</option>
                    <option value="PATIENT">Patient</option>
                    <option value="ADMIN">Admin</option>
                  </select>
                </div>

                {(form.role === 'DOCTOR' || form.role === 'CAREGIVER' || form.role === 'PATIENT') && (
                  <div>
                    <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', display: 'block', marginBottom: '5px' }}>Patient Access (optional)</label>
                    <select value={form.patient_code} onChange={e => setForm(f => ({ ...f, patient_code: e.target.value }))} style={{ ...inputStyle, cursor: 'pointer' }}>
                      <option value="">— No patient access yet —</option>
                      <option value="P001">P001 — Meenakshi Raman</option>
                      <option value="P002">P002 — Synthetic Patient 2</option>
                    </select>
                  </div>
                )}

                <div style={{ display: 'flex', gap: '10px', marginTop: '6px' }}>
                  <button type="button" onClick={() => setShowAddForm(false)} style={{ flex: 1, padding: '10px', borderRadius: '7px', border: '1px solid var(--color-border)', backgroundColor: 'var(--color-surface)', fontSize: '13px', fontWeight: 600, color: 'var(--color-text-secondary)', cursor: 'pointer' }}>
                    Cancel
                  </button>
                  <button type="submit" disabled={submitting} style={{ flex: 2, padding: '10px', borderRadius: '7px', border: 'none', backgroundColor: submitting ? 'var(--color-accent-border)' : 'var(--color-accent)', color: '#fff', fontSize: '13px', fontWeight: 700, cursor: submitting ? 'default' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '7px' }}>
                    <UserPlus size={15} /> {submitting ? 'Creating…' : 'Create Account'}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Filter + Search bar */}
      <div style={{ ...card, padding: '14px 16px', marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '14px', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {ROLE_FILTER_TABS.map(tab => {
            const active = filterRole === tab.key;
            return (
              <button key={tab.key} onClick={() => setFilterRole(tab.key)} style={{ padding: '6px 13px', borderRadius: '20px', border: active ? 'none' : '1px solid var(--color-border)', backgroundColor: active ? 'var(--color-accent)' : 'var(--color-surface)', color: active ? '#ffffff' : 'var(--color-text-secondary)', fontSize: '12px', fontWeight: 600, cursor: 'pointer', transition: 'all 0.15s' }}>
                {tab.label} <span style={{ opacity: 0.7 }}>({(counts as any)[tab.key] || 0})</span>
              </button>
            );
          })}
        </div>
        <div style={{ position: 'relative', minWidth: '220px' }}>
          <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-faint)' }} />
          <input placeholder="Search by name, username, email…" value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ ...inputStyle, paddingLeft: '32px', borderRadius: '20px' }} />
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div style={{ backgroundColor: 'var(--color-danger-soft)', border: '1px solid var(--color-danger-border)', borderRadius: '8px', padding: '10px 14px', marginBottom: '12px', display: 'flex', gap: '8px', fontSize: '13px', color: 'var(--color-danger-dark)', alignItems: 'center' }}>
          <AlertCircle size={15} /> {error}
        </div>
      )}

      {/* User Table */}
      <div style={card}>
        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--color-text-faint)', fontSize: '13px' }}>Loading users…</div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--color-text-faint)', fontSize: '13px' }}>No users found matching your filters.</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ backgroundColor: 'var(--color-bg)', borderBottom: '1px solid var(--color-border)' }}>
                {['Name & Username', 'Email', 'Role', 'Patient Access', 'Last Login', 'Status', 'Actions'].map(h => (
                  <th key={h} style={{ padding: '11px 14px', textAlign: 'left', fontWeight: 600, color: 'var(--color-text-secondary)', whiteSpace: 'nowrap' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((u, i) => {
                const m = ROLE_META[u.role] || ROLE_META.ADMIN;
                const isSelf = String(u.username) === String(user.username);
                return (
                  <tr key={u.id} style={{ borderBottom: i < filtered.length - 1 ? '1px solid var(--color-surface-alt)' : 'none', backgroundColor: !u.is_active ? 'var(--color-bg)' : '#fff', opacity: u.is_active ? 1 : 0.7 }}>
                    <td style={{ padding: '12px 14px' }}>
                      <div style={{ fontWeight: 600, color: 'var(--color-text-main)' }}>{u.full_name}</div>
                      <div style={{ fontSize: '11px', color: 'var(--color-text-faint)', fontFamily: 'monospace', marginTop: '2px' }}>@{u.username}</div>
                    </td>
                    <td style={{ padding: '12px 14px', color: 'var(--color-text-secondary)', fontSize: '12px' }}>{u.email}</td>
                    <td style={{ padding: '12px 14px' }}>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', padding: '3px 9px', borderRadius: '10px', backgroundColor: m.bg, color: m.color, fontSize: '11px', fontWeight: 700 }}>
                        {m.icon} {m.label}
                      </span>
                    </td>
                    <td style={{ padding: '12px 14px' }}>
                      {u.authorized_patients.length > 0
                        ? u.authorized_patients.map(p => (
                          <span key={p} style={{ display: 'inline-block', marginRight: '4px', padding: '2px 7px', borderRadius: '8px', backgroundColor: 'var(--color-accent-soft)', color: 'var(--color-accent-dark)', fontSize: '11px', fontWeight: 600 }}>{p}</span>
                        ))
                        : <span style={{ color: 'var(--color-text-faint)', fontSize: '11px' }}>—</span>
                      }
                    </td>
                    <td style={{ padding: '12px 14px', color: 'var(--color-text-faint)', fontSize: '11px' }}>{u.last_login_at || '—'}</td>
                    <td style={{ padding: '12px 14px' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', padding: '3px 9px', borderRadius: '10px', fontSize: '11px', fontWeight: 700,
                          backgroundColor: u.is_active ? 'var(--color-success-soft)' : 'var(--color-danger-soft)',
                          color: u.is_active ? 'var(--color-success)' : 'var(--color-danger)' }}>
                          {u.is_active ? <><UserCheck size={12} /> Active</> : <><UserX size={12} /> Disabled</>}
                        </span>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '2px 7px', borderRadius: '10px', fontSize: '10px', fontWeight: 700,
                          backgroundColor: u.is_verified ? 'var(--color-accent-soft)' : 'var(--color-warning-soft)',
                          color: u.is_verified ? 'var(--color-accent-dark)' : 'var(--color-warning-dark)' }}>
                          {u.is_verified ? '✔ Verified' : '⏳ Unverified'}
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: '12px 14px' }}>
                      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                        {isSelf ? (
                          <span style={{ fontSize: '11px', color: 'var(--color-text-faint)' }}>You</span>
                        ) : (
                          <>
                            <button onClick={() => handleToggle(u)} disabled={togglingId === u.id}
                              style={{ padding: '5px 10px', borderRadius: '6px', border: 'none', fontSize: '11px', fontWeight: 700, cursor: 'pointer',
                                backgroundColor: u.is_active ? 'var(--color-danger-soft)' : 'var(--color-success-soft)',
                                color: u.is_active ? 'var(--color-danger)' : 'var(--color-success)' }}>
                              {togglingId === u.id ? '…' : u.is_active ? 'Disable' : 'Enable'}
                            </button>
                            {!u.is_verified && (
                              <button onClick={() => handleResendOtp(u)}
                                style={{ padding: '5px 10px', borderRadius: '6px', border: '1px solid var(--color-warning-border)', backgroundColor: 'var(--color-warning-soft)', fontSize: '11px', fontWeight: 700, color: 'var(--color-warning-dark)', cursor: 'pointer' }}>
                                Verify OTP
                              </button>
                            )}
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* OTP Verification Modal */}
      {otpModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1100, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ backgroundColor: 'var(--color-surface)', borderRadius: '14px', padding: '28px', width: '420px', boxShadow: '0 8px 40px rgba(0,0,0,0.18)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: 'var(--color-warning-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px' }}>🔐</div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '15px', color: 'var(--color-text-main)' }}>Verify Account</div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>@{otpModal.username} · {otpModal.email}</div>
                </div>
              </div>
              <button onClick={() => { setOtpModal(null); setPendingOtp(null); setOtpInput(''); }} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-faint)' }}><X size={20} /></button>
            </div>

            {pendingOtp && (
              <div style={{ backgroundColor: 'var(--color-success-soft)', border: '1px solid var(--color-success-border)', borderRadius: '10px', padding: '14px 16px', marginBottom: '16px' }}>
                <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-success-dark)', marginBottom: '6px' }}>📧 {pendingOtp.message}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ fontFamily: 'monospace', fontSize: '28px', fontWeight: 800, color: 'var(--color-success)', letterSpacing: '8px', backgroundColor: 'var(--color-success-soft)', padding: '8px 16px', borderRadius: '8px', flex: 1, textAlign: 'center' }}>
                    {pendingOtp.otp}
                  </div>
                  <button onClick={() => navigator.clipboard.writeText(pendingOtp.otp)}
                    style={{ padding: '8px 10px', borderRadius: '7px', border: '1px solid var(--color-success-border)', backgroundColor: 'var(--color-surface)', cursor: 'pointer', fontSize: '11px', color: 'var(--color-success-dark)', fontWeight: 600 }}>
                    Copy
                  </button>
                </div>
                <div style={{ fontSize: '11px', color: 'var(--color-success)', marginTop: '6px', opacity: 0.8 }}>Share this OTP with the user. It expires when used.</div>
              </div>
            )}

            <div style={{ marginBottom: '14px' }}>
              <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', display: 'block', marginBottom: '6px' }}>Enter OTP to verify account:</label>
              <input type="text" maxLength={6} placeholder="6-digit OTP" value={otpInput}
                onChange={e => setOtpInput(e.target.value.replace(/\D/g, ''))}
                style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '2px solid var(--color-border)', fontSize: '20px', fontFamily: 'monospace', fontWeight: 700, textAlign: 'center', letterSpacing: '6px', color: 'var(--color-text-main)', outline: 'none', boxSizing: 'border-box' }}
              />
            </div>

            {otpError && (
              <div style={{ backgroundColor: 'var(--color-danger-soft)', border: '1px solid var(--color-danger-border)', borderRadius: '7px', padding: '8px 12px', marginBottom: '12px', fontSize: '12px', color: 'var(--color-danger-dark)', display: 'flex', gap: '6px', alignItems: 'center' }}>
                <AlertCircle size={13} /> {otpError}
              </div>
            )}

            <div style={{ display: 'flex', gap: '10px' }}>
              <button onClick={() => { setOtpModal(null); setPendingOtp(null); setOtpInput(''); }}
                style={{ flex: 1, padding: '10px', borderRadius: '7px', border: '1px solid var(--color-border)', backgroundColor: 'var(--color-surface)', fontSize: '13px', fontWeight: 600, color: 'var(--color-text-secondary)', cursor: 'pointer' }}>
                Close
              </button>
              <button onClick={handleVerifyOtp} disabled={otpInput.length !== 6 || otpVerifying}
                style={{ flex: 2, padding: '10px', borderRadius: '7px', border: 'none', backgroundColor: otpInput.length === 6 ? 'var(--color-success)' : 'var(--color-border-strong)', color: '#fff', fontSize: '13px', fontWeight: 700, cursor: otpInput.length === 6 ? 'pointer' : 'default', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '7px' }}>
                <CheckCircle2 size={15} /> {otpVerifying ? 'Verifying…' : 'Confirm & Verify'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

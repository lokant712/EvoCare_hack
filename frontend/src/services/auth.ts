/**
 * EvoCare Authentication Service
 * Manages JWT token lifecycle: login, logout, token storage, user decoding.
 */

import { API_BASE } from './api';

const TOKEN_KEY = 'evocare_access_token';
const USER_KEY = 'evocare_user';

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'DOCTOR' | 'CAREGIVER' | 'ADMIN' | 'PATIENT';
}

export interface AuthorizedPatient {
  patient_code: string;
  name: string;
  age: number;
  sex: string;
  access_role: string;
}

export interface LoginResult {
  access_token: string;
  refresh_token: string;
  user: AuthUser;
  expires_in: number;
}

class AuthService {
  /** Attempt login; returns user info on success, throws on failure. */
  async login(username: string, password: string): Promise<AuthUser> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      const msg = data?.detail || `Login failed (HTTP ${res.status})`;
      throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }

    const data: LoginResult = await res.json();
    this._storeToken(data.access_token);
    this._storeUser(data.user);
    return data.user;
  }

  /** Logout: revoke server-side token, clear local storage. */
  async logout(): Promise<void> {
    const token = this.getToken();
    if (token) {
      try {
        await fetch(`${API_BASE}/auth/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch {
        // Ignore network errors on logout — always clear local state
      }
    }
    this._clearSession();
  }

  /** Get stored JWT access token or null. */
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  /** Get current stored user object or null. */
  getUser(): AuthUser | null {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as AuthUser;
    } catch {
      return null;
    }
  }

  /** Returns true if a token is currently stored. */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  /** Fetch the list of patients this user is authorized to access. */
  async getAuthorizedPatients(): Promise<AuthorizedPatient[]> {
    const token = this.getToken();
    if (!token) return [];
    const res = await fetch(`${API_BASE}/auth/authorized-patients`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return [];
    return res.json();
  }

  private _storeToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  }

  private _storeUser(user: AuthUser): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  private _clearSession(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

export const authService = new AuthService();

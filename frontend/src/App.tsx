import React, { useState, useEffect } from 'react';
import { Dashboard } from './pages/Dashboard';
import { LoginPage } from './pages/LoginPage';
import { authService, AuthUser } from './services/auth';

export const App: React.FC = () => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    // On mount, check if a valid session already exists
    const stored = authService.getUser();
    const token = authService.getToken();
    if (stored && token) {
      setUser(stored);
    }
    setChecking(false);

    // Listen for global 401 events from api.ts
    const onUnauthorized = () => setUser(null);
    window.addEventListener('evocare:unauthorized', onUnauthorized);
    return () => window.removeEventListener('evocare:unauthorized', onUnauthorized);
  }, []);

  const handleLoginSuccess = (loggedInUser: AuthUser) => {
    setUser(loggedInUser);
  };

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
  };

  if (checking) {
    return null; // Brief flash while checking localStorage
  }

  if (!user) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return <Dashboard user={user} onLogout={handleLogout} />;
};

export default App;

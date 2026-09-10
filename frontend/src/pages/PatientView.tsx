import React from 'react';
import { Dashboard } from './Dashboard';
import { AuthUser } from '../services/auth';

const DEMO_USER: AuthUser = {
  id: 1,
  username: 'doctor.demo',
  email: 'doctor.demo@evocare.health',
  full_name: 'Dr. Ramesh Varma, MD',
  role: 'DOCTOR',
};

export const PatientView: React.FC = () => {
  return <Dashboard user={DEMO_USER} onLogout={() => {}} />;
};

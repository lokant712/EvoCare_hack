import React, { useState } from 'react';
import { PatientOverviewCard } from './PatientOverviewCard';
import { RecentChangesPanel } from './RecentChangesPanel';
import { ClinicalContextPanel } from '../clinical/ClinicalContextPanel';
import { CaregiverObservationsPanel } from '../caregiver/CaregiverObservationsPanel';
import { LongitudinalMemoryPanel } from '../memory/LongitudinalMemoryPanel';
import { PatientTimeline } from '../timeline/PatientTimeline';
import { ConflictCard } from '../common/ConflictCard';
import { DashboardResponse, RecentChangeItem } from '../../types';
import {
  TrendingUp,
  Stethoscope,
  HeartHandshake,
  History,
  AlertTriangle,
  UserCheck,
  Pill,
  Activity,
  ShieldCheck,
} from 'lucide-react';

interface PatientRecordsTabProps {
  data: DashboardResponse;
  onOpenWhy: (change: RecentChangeItem) => void;
  onSelectEvidence: (code: string) => void;
}

type RecordSection = 'changes' | 'clinical' | 'caregiver' | 'timeline' | 'conflicts';

export const PatientRecordsTab: React.FC<PatientRecordsTabProps> = ({
  data,
  onOpenWhy,
  onSelectEvidence,
}) => {
  const [activeSection, setActiveSection] = useState<RecordSection>('changes');

  const conflictCount = data.conflicts?.length || 0;
  const recentChangeCount = data.recent_changes?.length || 0;
  const diagCount = data.clinical_diagnoses?.length || 0;
  const medCount = data.medications?.length || 0;
  const obsCount = data.caregiver_observations?.length || 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Sleek Clinical Header Summary Card */}
      <div
        style={{
          backgroundColor: 'var(--color-surface)',
          borderRadius: '14px',
          border: '1px solid var(--color-border)',
          padding: '18px 22px',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          {/* Patient Bio */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '12px',
                backgroundColor: 'var(--color-accent-soft)',
                border: '1px solid var(--color-accent-border)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--color-accent)',
                flexShrink: 0,
              }}
            >
              <UserCheck size={22} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h1 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--color-text-main)', margin: 0 }}>
                  {data.patient.name}
                </h1>
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--color-surface-alt)',
                    color: 'var(--color-text-secondary)',
                    fontFamily: "'IBM Plex Mono', monospace",
                  }}
                >
                  {data.patient.patient_code}
                </span>
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 600,
                    padding: '2px 8px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--color-success-soft)',
                    color: 'var(--color-success-dark)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  <ShieldCheck size={12} /> Verified 2FA
                </span>
              </div>
              <div style={{ fontSize: '12.5px', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                {data.patient.age} yrs · {data.patient.sex} · {data.patient.location} · Primary Physician: <b>Dr. Anand Rao</b>
              </div>
            </div>
          </div>

          {/* Quick Metrics */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
            <div
              style={{
                padding: '6px 12px',
                borderRadius: '8px',
                backgroundColor: 'var(--color-surface-alt)',
                border: '1px solid var(--color-border)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <Activity size={14} style={{ color: 'var(--color-accent)' }} />
              <div>
                <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                  Active Diagnoses
                </div>
                <div style={{ fontSize: '12.5px', fontWeight: 700, color: 'var(--color-text-main)' }}>
                  {diagCount} Conditions
                </div>
              </div>
            </div>

            <div
              style={{
                padding: '6px 12px',
                borderRadius: '8px',
                backgroundColor: 'var(--color-surface-alt)',
                border: '1px solid var(--color-border)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <Pill size={14} style={{ color: 'var(--color-success)' }} />
              <div>
                <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                  Medications
                </div>
                <div style={{ fontSize: '12.5px', fontWeight: 700, color: 'var(--color-text-main)' }}>
                  {medCount} Active Regimens
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Clean Segmented Sub-Navigation Pills */}
        <div
          style={{
            marginTop: '16px',
            paddingTop: '14px',
            borderTop: '1px solid var(--color-border)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            overflowX: 'auto',
          }}
        >
          <button
            onClick={() => setActiveSection('changes')}
            style={{
              padding: '7px 14px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeSection === 'changes' ? 'var(--color-accent)' : 'var(--color-surface-alt)',
              color: activeSection === 'changes' ? '#ffffff' : 'var(--color-text-secondary)',
              fontSize: '12.5px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.15s ease',
              whiteSpace: 'nowrap',
            }}
          >
            <TrendingUp size={14} />
            <span>Recent Trajectory & Changes</span>
            {recentChangeCount > 0 && (
              <span
                style={{
                  fontSize: '10.5px',
                  padding: '1px 6px',
                  borderRadius: '10px',
                  backgroundColor: activeSection === 'changes' ? 'rgba(255,255,255,0.25)' : 'var(--color-accent-soft)',
                  color: activeSection === 'changes' ? '#ffffff' : 'var(--color-accent-dark)',
                  fontWeight: 800,
                }}
              >
                {recentChangeCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveSection('clinical')}
            style={{
              padding: '7px 14px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeSection === 'clinical' ? 'var(--color-accent)' : 'var(--color-surface-alt)',
              color: activeSection === 'clinical' ? '#ffffff' : 'var(--color-text-secondary)',
              fontSize: '12.5px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.15s ease',
              whiteSpace: 'nowrap',
            }}
          >
            <Stethoscope size={14} />
            <span>Clinical Records & Labs</span>
            <span
              style={{
                fontSize: '10.5px',
                padding: '1px 6px',
                borderRadius: '10px',
                backgroundColor: activeSection === 'clinical' ? 'rgba(255,255,255,0.25)' : 'var(--color-surface)',
                color: activeSection === 'clinical' ? '#ffffff' : 'var(--color-text-muted)',
                fontWeight: 700,
              }}
            >
              {diagCount + medCount}
            </span>
          </button>

          <button
            onClick={() => setActiveSection('caregiver')}
            style={{
              padding: '7px 14px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeSection === 'caregiver' ? 'var(--color-accent)' : 'var(--color-surface-alt)',
              color: activeSection === 'caregiver' ? '#ffffff' : 'var(--color-text-secondary)',
              fontSize: '12.5px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.15s ease',
              whiteSpace: 'nowrap',
            }}
          >
            <HeartHandshake size={14} />
            <span>Caregiver Daily Observations</span>
            <span
              style={{
                fontSize: '10.5px',
                padding: '1px 6px',
                borderRadius: '10px',
                backgroundColor: activeSection === 'caregiver' ? 'rgba(255,255,255,0.25)' : 'var(--color-surface)',
                color: activeSection === 'caregiver' ? '#ffffff' : 'var(--color-text-muted)',
                fontWeight: 700,
              }}
            >
              {obsCount}
            </span>
          </button>

          <button
            onClick={() => setActiveSection('timeline')}
            style={{
              padding: '7px 14px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeSection === 'timeline' ? 'var(--color-accent)' : 'var(--color-surface-alt)',
              color: activeSection === 'timeline' ? '#ffffff' : 'var(--color-text-secondary)',
              fontSize: '12.5px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.15s ease',
              whiteSpace: 'nowrap',
            }}
          >
            <History size={14} />
            <span>Timeline & Longitudinal Wiki</span>
          </button>

          {conflictCount > 0 && (
            <button
              onClick={() => setActiveSection('conflicts')}
              style={{
                padding: '7px 14px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: activeSection === 'conflicts' ? 'var(--color-warning)' : 'var(--color-warning-soft)',
                color: activeSection === 'conflicts' ? '#1c1a14' : 'var(--color-warning-dark)',
                fontSize: '12.5px',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                transition: 'all 0.15s ease',
                whiteSpace: 'nowrap',
              }}
            >
              <AlertTriangle size={14} />
              <span>Discrepancies & Conflicts</span>
              <span
                style={{
                  fontSize: '10.5px',
                  padding: '1px 6px',
                  borderRadius: '10px',
                  backgroundColor: activeSection === 'conflicts' ? 'rgba(0,0,0,0.15)' : 'var(--color-warning-border)',
                  color: 'inherit',
                  fontWeight: 800,
                }}
              >
                {conflictCount}
              </span>
            </button>
          )}
        </div>
      </div>

      {/* SECTION 1: RECENT TRAJECTORY & HEALTH DOMAINS */}
      {activeSection === 'changes' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Recent Changes with Why? Traceability button */}
          <RecentChangesPanel
            recentChanges={data.recent_changes}
            onOpenWhy={onOpenWhy}
            onSelectEvidence={onSelectEvidence}
          />

          {/* Core Functional Health Domains Overview */}
          <PatientOverviewCard overview={data.overview} />
        </div>
      )}

      {/* SECTION 2: CLINICAL RECORDS (Diagnoses, Meds, Labs) */}
      {activeSection === 'clinical' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <ClinicalContextPanel
            diagnoses={data.clinical_diagnoses}
            medications={data.medications}
            labs={data.labs}
            onSelectEvidence={onSelectEvidence}
          />
        </div>
      )}

      {/* SECTION 3: CAREGIVER LOGS */}
      {activeSection === 'caregiver' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <CaregiverObservationsPanel
            observations={data.caregiver_observations}
            onSelectEvidence={onSelectEvidence}
          />
        </div>
      )}

      {/* SECTION 4: TIMELINE & LIVING WIKI */}
      {activeSection === 'timeline' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <PatientTimeline
            timeline={data.timeline}
            onSelectEvidence={onSelectEvidence}
          />

          <LongitudinalMemoryPanel
            memory={data.longitudinal_memory}
            patientId={data.patient.patient_code}
            onSelectEvidence={onSelectEvidence}
          />
        </div>
      )}

      {/* SECTION 5: DISCREPANCIES & CONFLICTS */}
      {activeSection === 'conflicts' && data.conflicts && data.conflicts.length > 0 && (
        <div
          style={{
            backgroundColor: 'var(--color-surface)',
            borderRadius: '12px',
            border: '1px solid var(--color-warning-border)',
            padding: '20px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <AlertTriangle size={18} style={{ color: 'var(--color-warning)' }} />
            <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--color-warning-dark)', margin: 0 }}>
              Contextual Discrepancies & Conflict Analysis
            </h2>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', margin: '0 0 14px 0' }}>
            Recorded differences between clinical exam and home observations (Preserved contextually without premature AI resolution)
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {data.conflicts.map((c) => (
              <ConflictCard key={c.id} conflict={c} onSelectEvidence={onSelectEvidence} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

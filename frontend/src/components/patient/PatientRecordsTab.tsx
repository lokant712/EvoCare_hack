import React from 'react';
import { SafetyAlert } from '../common/SafetyAlert';
import { PatientOverviewCard } from './PatientOverviewCard';
import { RecentChangesPanel } from './RecentChangesPanel';
import { ClinicalContextPanel } from '../clinical/ClinicalContextPanel';
import { CaregiverObservationsPanel } from '../caregiver/CaregiverObservationsPanel';
import { LongitudinalMemoryPanel } from '../memory/LongitudinalMemoryPanel';
import { PatientTimeline } from '../timeline/PatientTimeline';
import { ConflictCard } from '../common/ConflictCard';
import { DashboardResponse, RecentChangeItem } from '../../types';
import { AlertTriangle } from 'lucide-react';

interface PatientRecordsTabProps {
  data: DashboardResponse;
  onOpenWhy: (change: RecentChangeItem) => void;
  onSelectEvidence: (code: string) => void;
}

export const PatientRecordsTab: React.FC<PatientRecordsTabProps> = ({
  data,
  onOpenWhy,
  onSelectEvidence,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Safety & Read-Only Banner */}
      <SafetyAlert />

      {/* 1. Patient Overview Card (6 key health domains) */}
      <PatientOverviewCard overview={data.overview} />

      {/* 2. Recent Changes Panel with Why? button */}
      <RecentChangesPanel
        recentChanges={data.recent_changes}
        onOpenWhy={onOpenWhy}
        onSelectEvidence={onSelectEvidence}
      />

      {/* 2-Column Clinical & Caregiver Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))',
          gap: '24px',
        }}
      >
        {/* Clinical Context (Diagnoses, Meds, Labs) */}
        <ClinicalContextPanel
          diagnoses={data.clinical_diagnoses}
          medications={data.medications}
          labs={data.labs}
          onSelectEvidence={onSelectEvidence}
        />

        {/* Caregiver Observations */}
        <CaregiverObservationsPanel
          observations={data.caregiver_observations}
          onSelectEvidence={onSelectEvidence}
        />
      </div>

      {/* 3. Longitudinal Memory Panel (Living Wiki) */}
      <LongitudinalMemoryPanel
        memory={data.longitudinal_memory}
        patientId={data.patient.patient_code}
        onSelectEvidence={onSelectEvidence}
      />

      {/* 4. Longitudinal Patient Timeline */}
      <PatientTimeline
        timeline={data.timeline}
        onSelectEvidence={onSelectEvidence}
      />

      {/* 5. Discrepancy & Conflict Analysis Panel */}
      {data.conflicts && data.conflicts.length > 0 && (
        <div
          style={{
            backgroundColor: '#ffffff',
            borderRadius: '12px',
            border: '1px solid #fed7aa',
            padding: '20px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <AlertTriangle size={18} style={{ color: '#ea580c' }} />
            <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#9a3412', margin: 0 }}>
              Contextual Discrepancies &amp; Conflict Analysis
            </h2>
          </div>
          <p style={{ fontSize: '12px', color: '#64748b', margin: '0 0 14px 0' }}>
            Recorded differences between clinical exam and home observations (Preserved contextually without premature AI resolution)
          </p>
          {data.conflicts.map((c) => (
            <ConflictCard key={c.id} conflict={c} onSelectEvidence={onSelectEvidence} />
          ))}
        </div>
      )}
    </div>
  );
};

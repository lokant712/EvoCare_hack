import React, { useState } from 'react';
import {
  Plus,
  Trash2,
  FileText,
  CheckCircle,
  Copy,
  Download,
  Eye,
  Code,
  Stethoscope,
  AlertCircle
} from 'lucide-react';
import { apiService } from '../../services/api';
import { DashboardResponse } from '../../types';

interface DoctorClinicalEntryTabProps {
  data: DashboardResponse;
  onEntrySaved: () => void;
  onSelectEvidence?: (code: string) => void;
}

interface DiagnosisRow {
  condition: string;
  icd_code: string;
  status: string;
  notes: string;
}

interface PrescriptionRow {
  medication_name: string;
  dose: string;
  frequency: string;
  indication: string;
  instructions: string;
}

const COMMON_DIAGNOSES = [
  { condition: 'Orthostatic Hypotension', icd: 'I95.1' },
  { condition: 'Benign Paroxysmal Positional Vertigo', icd: 'H81.10' },
  { condition: 'Gait Instability & Fall Risk', icd: 'R26.81' },
  { condition: 'Diabetic Peripheral Neuropathy', icd: 'E11.40' },
  { condition: 'Vitamin D Deficiency', icd: 'E55.9' }
];

const COMMON_MEDS = [
  { name: 'Meclizine', dose: '25 mg', freq: 'Once daily as needed for dizziness' },
  { name: 'Fludrocortisone', dose: '0.1 mg', freq: 'Once daily in morning' },
  { name: 'Cholecalciferol (Vit D3)', dose: '60,000 IU', freq: 'Once weekly for 8 weeks' },
  { name: 'Physical Therapy (Balance)', dose: '2x / week', freq: 'Gait retraining & vestibular exercises' }
];

export const DoctorClinicalEntryTab: React.FC<DoctorClinicalEntryTabProps> = ({
  data,
  onEntrySaved,
  onSelectEvidence,
}) => {
  const [consultationTitle, setConsultationTitle] = useState('Geriatric Trajectory Review & Clinical Management');
  const [clinicalNotes, setClinicalNotes] = useState(
    'Evaluated reported morning dizziness and balance instability. Caregiver observation of near-fall noted.'
  );

  const [diagnoses, setDiagnoses] = useState<DiagnosisRow[]>([
    {
      condition: 'Orthostatic Hypotension',
      icd_code: 'I95.1',
      status: 'CONFIRMED',
      notes: 'Correlates with reported morning postural lightheadedness upon standing from bed.'
    }
  ]);

  const [prescriptions, setPrescriptions] = useState<PrescriptionRow[]>([
    {
      medication_name: 'Meclizine',
      dose: '25 mg',
      frequency: 'Once daily PRN in morning',
      indication: 'Positional vestibular dizziness',
      instructions: 'Take with food after rising.'
    }
  ]);

  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [generatedMarkdown, setGeneratedMarkdown] = useState<string | null>(null);
  const [showRawMarkdown, setShowRawMarkdown] = useState(false);
  const [copied, setCopied] = useState(false);

  // Add diagnosis row
  const addDiagnosisRow = () => {
    setDiagnoses([
      ...diagnoses,
      { condition: '', icd_code: '', status: 'CONFIRMED', notes: '' }
    ]);
  };

  const removeDiagnosisRow = (index: number) => {
    setDiagnoses(diagnoses.filter((_, i) => i !== index));
  };

  const updateDiagnosis = (index: number, field: keyof DiagnosisRow, value: string) => {
    const updated = [...diagnoses];
    updated[index][field] = value;
    setDiagnoses(updated);
  };

  // Add prescription row
  const addPrescriptionRow = () => {
    setPrescriptions([
      ...prescriptions,
      { medication_name: '', dose: '', frequency: '', indication: '', instructions: '' }
    ]);
  };

  const removePrescriptionRow = (index: number) => {
    setPrescriptions(prescriptions.filter((_, i) => i !== index));
  };

  const updatePrescription = (index: number, field: keyof PrescriptionRow, value: string) => {
    const updated = [...prescriptions];
    updated[index][field] = value;
    setPrescriptions(updated);
  };

  const [savedEvidenceIds, setSavedEvidenceIds] = useState<string[]>([]);

  // Submit and convert to Markdown
  const handleSaveAndGenerateMarkdown = async () => {
    setSaving(true);
    setSaveError(null);
    setSaveSuccess(null);

    // Validate
    const validDiags = diagnoses.filter((d) => d.condition.trim());
    const validMeds = prescriptions.filter((p) => p.medication_name.trim());

    if (validDiags.length === 0 && validMeds.length === 0) {
      setSaveError('Please enter at least one diagnosis or prescription before submitting.');
      setSaving(false);
      return;
    }

    try {
      const payload = {
        consultation_title: consultationTitle,
        clinical_notes: clinicalNotes,
        diagnoses: validDiags,
        prescriptions: validMeds,
      };

      const res = await apiService.recordDoctorEntries(data.patient.patient_code, payload);
      setSaveSuccess(res.message || 'Saved successfully and generated Markdown clinical report.');
      setGeneratedMarkdown(res.markdown_content);
      setSavedEvidenceIds(res.created_evidence_ids || []);
      onEntrySaved(); // refresh dashboard data in parent
    } catch (err: any) {
      setSaveError(err?.message || 'Failed to save clinical entries.');
    } finally {
      setSaving(false);
    }
  };

  const copyMarkdownToClipboard = () => {
    if (generatedMarkdown) {
      navigator.clipboard.writeText(generatedMarkdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const downloadMarkdownFile = () => {
    if (generatedMarkdown) {
      const blob = new Blob([generatedMarkdown], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Clinical_Note_${data.patient.patient_code}_${new Date().toISOString().slice(0, 10)}.md`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header Banner */}
      <div
        style={{
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          border: '1px solid #e2e8f0',
          padding: '20px 24px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              backgroundColor: '#059669',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
            }}
          >
            <Stethoscope size={20} />
          </div>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a', margin: 0 }}>
              Doctor Clinical Entry &amp; Markdown Generator
            </h2>
            <div style={{ fontSize: '12px', color: '#64748b' }}>
              Record structured diagnoses and prescriptions • Automatically compiled into immutable Markdown reports
            </div>
          </div>
        </div>

        {/* General Encounter Info */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px', marginTop: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#475569', marginBottom: '4px' }}>
              Encounter Title
            </label>
            <input
              type="text"
              value={consultationTitle}
              onChange={(e) => setConsultationTitle(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #cbd5e1',
                fontSize: '13px',
                boxSizing: 'border-box',
              }}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#475569', marginBottom: '4px' }}>
              Clinical Examination Notes
            </label>
            <input
              type="text"
              value={clinicalNotes}
              onChange={(e) => setClinicalNotes(e.target.value)}
              placeholder="Clinical impressions and findings..."
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #cbd5e1',
                fontSize: '13px',
                boxSizing: 'border-box',
              }}
            />
          </div>
        </div>
      </div>

      {/* Success / Error Messages */}
      {saveSuccess && (
        <div
          style={{
            backgroundColor: '#ecfdf5',
            border: '1px solid #a7f3d0',
            borderRadius: '8px',
            padding: '12px 16px',
            color: '#065f46',
            fontSize: '13px',
            fontWeight: 600,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle size={16} style={{ color: '#059669', flexShrink: 0 }} />
            <span>{saveSuccess}</span>
          </div>
          {savedEvidenceIds.length > 0 && (
            <div style={{ marginTop: '10px', display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '11px', color: '#047857', fontWeight: 600 }}>Immutable Evidence Codes Generated:</span>
              {savedEvidenceIds.map((evId) => (
                <button
                  key={evId}
                  type="button"
                  onClick={() => onSelectEvidence?.(evId)}
                  style={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #059669',
                    borderRadius: '4px',
                    padding: '2px 8px',
                    fontSize: '11px',
                    fontFamily: 'monospace',
                    fontWeight: 700,
                    color: '#047857',
                    cursor: onSelectEvidence ? 'pointer' : 'default',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                  title="Click to inspect this evidence in the provenance drawer"
                >
                  <span>{evId}</span>
                  <span style={{ fontSize: '9px', textDecoration: 'underline' }}>(view)</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {saveError && (
        <div
          style={{
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: '#991b1b',
            fontSize: '13px',
            fontWeight: 600,
          }}
        >
          <AlertCircle size={16} style={{ color: '#dc2626', flexShrink: 0 }} />
          <span>{saveError}</span>
        </div>
      )}

      {/* ============================================================ */}
      {/* 1. STRUCTURED DIAGNOSIS TABLE                                */}
      {/* ============================================================ */}
      <div
        style={{
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          border: '1px solid #e2e8f0',
          padding: '20px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a', margin: 0 }}>
              1. Structured Diagnoses Table
            </h3>
            <span style={{ fontSize: '12px', color: '#64748b' }}>
              Enter clinician-confirmed assessments or differential diagnoses
            </span>
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button
              onClick={addDiagnosisRow}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                padding: '6px 12px',
                backgroundColor: '#f0fdf4',
                color: '#166534',
                border: '1px solid #bbf7d0',
                borderRadius: '6px',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <Plus size={14} />
              <span>Add Diagnosis Row</span>
            </button>
          </div>
        </div>

        {/* Quick Suggestion Chips */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '14px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: 600 }}>Quick Suggestions:</span>
          {COMMON_DIAGNOSES.map((item, i) => (
            <button
              key={i}
              onClick={() => {
                setDiagnoses([
                  ...diagnoses,
                  { condition: item.condition, icd_code: item.icd, status: 'CONFIRMED', notes: '' }
                ]);
              }}
              style={{
                fontSize: '11px',
                backgroundColor: '#f8fafc',
                border: '1px solid #e2e8f0',
                color: '#334155',
                padding: '2px 8px',
                borderRadius: '12px',
                cursor: 'pointer',
              }}
            >
              + {item.condition} ({item.icd})
            </button>
          ))}
        </div>

        {/* The Structured Table */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ backgroundColor: '#f8fafc', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                <th style={{ padding: '10px 12px', fontWeight: 700, color: '#334155' }}>Condition / Diagnosis</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, color: '#334155', width: '120px' }}>ICD-10</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, color: '#334155', width: '150px' }}>Status</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, color: '#334155' }}>Clinical Rationale / Notes</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, color: '#334155', width: '60px', textAlign: 'center' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {diagnoses.map((row, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #f1f5f9' }}>
                  <td style={{ padding: '8px 12px' }}>
                    <input
                      type="text"
                      value={row.condition}
                      onChange={(e) => updateDiagnosis(idx, 'condition', e.target.value)}
                      placeholder="e.g. Orthostatic Hypotension"
                      style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '13px', boxSizing: 'border-box' }}
                    />
                  </td>
                  <td style={{ padding: '8px 12px' }}>
                    <input
                      type="text"
                      value={row.icd_code}
                      onChange={(e) => updateDiagnosis(idx, 'icd_code', e.target.value)}
                      placeholder="e.g. I95.1"
                      style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '13px', boxSizing: 'border-box', fontFamily: 'monospace' }}
                    />
                  </td>
                  <td style={{ padding: '8px 12px' }}>
                    <select
                      value={row.status}
                      onChange={(e) => updateDiagnosis(idx, 'status', e.target.value)}
                      style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '13px', boxSizing: 'border-box', backgroundColor: '#ffffff' }}
                    >
                      <option value="CONFIRMED">CONFIRMED</option>
                      <option value="SUSPECTED">SUSPECTED</option>
                      <option value="DIFFERENTIAL">DIFFERENTIAL</option>
                      <option value="RESOLVED">RESOLVED</option>
                    </select>
                  </td>
                  <td style={{ padding: '8px 12px' }}>
                    <input
                      type="text"
                      value={row.notes}
                      onChange={(e) => updateDiagnosis(idx, 'notes', e.target.value)}
                      placeholder="Rationale / observation tie-in..."
                      style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '13px', boxSizing: 'border-box' }}
                    />
                  </td>
                  <td style={{ padding: '8px 12px', textAlign: 'center' }}>
                    <button
                      onClick={() => removeDiagnosisRow(idx)}
                      disabled={diagnoses.length <= 1}
                      title="Remove row"
                      style={{
                        background: 'none',
                        border: 'none',
                        color: diagnoses.length <= 1 ? '#cbd5e1' : '#ef4444',
                        cursor: diagnoses.length <= 1 ? 'not-allowed' : 'pointer',
                        padding: '4px',
                      }}
                    >
                      <Trash2 size={15} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ============================================================ */}
      {/* 2. STRUCTURED PRESCRIPTIONS TABLE                            */}
      {/* ============================================================ */}
      <div
        style={{
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          border: '1px solid #e2e8f0',
          padding: '20px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a', margin: 0 }}>
              2. Structured Medications &amp; Prescriptions Table
            </h3>
            <span style={{ fontSize: '12px', color: '#64748b' }}>
              Add or adjust pharmacotherapy orders and therapy regimens
            </span>
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button
              onClick={addPrescriptionRow}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                padding: '6px 12px',
                backgroundColor: '#eff6ff',
                color: '#1d4ed8',
                border: '1px solid #bfdbfe',
                borderRadius: '6px',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <Plus size={14} />
              <span>Add Prescription Row</span>
            </button>
          </div>
        </div>

        {/* Quick Suggestion Chips */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '14px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: 600 }}>Common Prescriptions:</span>
          {COMMON_MEDS.map((med, i) => (
            <button
              key={i}
              onClick={() => {
                setPrescriptions([
                  ...prescriptions,
                  { medication_name: med.name, dose: med.dose, frequency: med.freq, indication: 'Management', instructions: 'As directed' }
                ]);
              }}
              style={{
                fontSize: '11px',
                backgroundColor: '#f8fafc',
                border: '1px solid #e2e8f0',
                color: '#334155',
                padding: '2px 8px',
                borderRadius: '12px',
                cursor: 'pointer',
              }}
            >
              + {med.name} ({med.dose})
            </button>
          ))}
        </div>

        {/* The Structured Table */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ backgroundColor: '#f8fafc', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                <th style={{ padding: '10px 12px', fontWeight: 700, color: '#334155' }}>Medication Name</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, color: '#334155', width: '120px' }}>Dosage</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, color: '#334155' }}>Frequency</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, color: '#334155' }}>Indication</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, color: '#334155' }}>Instructions</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, color: '#334155', width: '60px', textAlign: 'center' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {prescriptions.map((row, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #f1f5f9' }}>
                  <td style={{ padding: '8px 12px' }}>
                    <input
                      type="text"
                      value={row.medication_name}
                      onChange={(e) => updatePrescription(idx, 'medication_name', e.target.value)}
                      placeholder="e.g. Meclizine"
                      style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '13px', boxSizing: 'border-box' }}
                    />
                  </td>
                  <td style={{ padding: '8px 12px' }}>
                    <input
                      type="text"
                      value={row.dose}
                      onChange={(e) => updatePrescription(idx, 'dose', e.target.value)}
                      placeholder="e.g. 25 mg"
                      style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '13px', boxSizing: 'border-box' }}
                    />
                  </td>
                  <td style={{ padding: '8px 12px' }}>
                    <input
                      type="text"
                      value={row.frequency}
                      onChange={(e) => updatePrescription(idx, 'frequency', e.target.value)}
                      placeholder="e.g. Once daily in morning"
                      style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '13px', boxSizing: 'border-box' }}
                    />
                  </td>
                  <td style={{ padding: '8px 12px' }}>
                    <input
                      type="text"
                      value={row.indication}
                      onChange={(e) => updatePrescription(idx, 'indication', e.target.value)}
                      placeholder="e.g. Positional dizziness"
                      style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '13px', boxSizing: 'border-box' }}
                    />
                  </td>
                  <td style={{ padding: '8px 12px' }}>
                    <input
                      type="text"
                      value={row.instructions}
                      onChange={(e) => updatePrescription(idx, 'instructions', e.target.value)}
                      placeholder="e.g. Take with breakfast"
                      style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '13px', boxSizing: 'border-box' }}
                    />
                  </td>
                  <td style={{ padding: '8px 12px', textAlign: 'center' }}>
                    <button
                      onClick={() => removePrescriptionRow(idx)}
                      disabled={prescriptions.length <= 1}
                      title="Remove row"
                      style={{
                        background: 'none',
                        border: 'none',
                        color: prescriptions.length <= 1 ? '#cbd5e1' : '#ef4444',
                        cursor: prescriptions.length <= 1 ? 'not-allowed' : 'pointer',
                        padding: '4px',
                      }}
                    >
                      <Trash2 size={15} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ============================================================ */}
      {/* 3. SUBMIT & GENERATE MARKDOWN BUTTON                         */}
      {/* ============================================================ */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', alignItems: 'center' }}>
        <button
          onClick={handleSaveAndGenerateMarkdown}
          disabled={saving}
          style={{
            backgroundColor: saving ? '#93c5fd' : '#0284c7',
            color: '#ffffff',
            padding: '12px 24px',
            borderRadius: '8px',
            border: 'none',
            fontSize: '14px',
            fontWeight: 700,
            cursor: saving ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: '0 2px 4px rgba(2, 132, 199, 0.25)',
          }}
        >
          <FileText size={16} />
          <span>{saving ? 'Processing & Converting...' : 'Save & Convert to Markdown Note (.md)'}</span>
        </button>
      </div>

      {/* ============================================================ */}
      {/* 4. LIVE MARKDOWN PREVIEW & EXPORT VIEWER                     */}
      {/* ============================================================ */}
      {generatedMarkdown && (
        <div
          style={{
            backgroundColor: '#ffffff',
            borderRadius: '12px',
            border: '1px solid #0284c7',
            overflow: 'hidden',
            boxShadow: '0 4px 12px rgba(2, 132, 199, 0.08)',
          }}
        >
          {/* Header */}
          <div
            style={{
              backgroundColor: '#f0f9ff',
              borderBottom: '1px solid #bae6fd',
              padding: '12px 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '8px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={18} style={{ color: '#0284c7' }} />
              <span style={{ fontSize: '14px', fontWeight: 700, color: '#0369a1' }}>
                Generated Clinical Markdown Note (.md)
              </span>
              <span style={{ fontSize: '11px', color: '#0284c7', backgroundColor: '#e0f2fe', padding: '2px 6px', borderRadius: '4px', fontWeight: 600 }}>
                Saved to Knowledge Base
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <button
                onClick={() => setShowRawMarkdown(!showRawMarkdown)}
                style={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #cbd5e1',
                  color: '#475569',
                  padding: '4px 10px',
                  borderRadius: '6px',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                {showRawMarkdown ? <Eye size={13} /> : <Code size={13} />}
                <span>{showRawMarkdown ? 'Render View' : 'Raw Markdown'}</span>
              </button>

              <button
                onClick={copyMarkdownToClipboard}
                style={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #cbd5e1',
                  color: '#475569',
                  padding: '4px 10px',
                  borderRadius: '6px',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <Copy size={13} />
                <span>{copied ? 'Copied!' : 'Copy Markdown'}</span>
              </button>

              <button
                onClick={downloadMarkdownFile}
                style={{
                  backgroundColor: '#0284c7',
                  border: 'none',
                  color: '#ffffff',
                  padding: '4px 12px',
                  borderRadius: '6px',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <Download size={13} />
                <span>Download .md</span>
              </button>
            </div>
          </div>

          {/* Body */}
          <div style={{ padding: '20px' }}>
            {showRawMarkdown ? (
              <pre
                style={{
                  backgroundColor: '#0f172a',
                  color: '#e2e8f0',
                  padding: '16px',
                  borderRadius: '8px',
                  fontSize: '12px',
                  fontFamily: "'IBM Plex Mono', monospace",
                  overflowX: 'auto',
                  lineHeight: 1.5,
                  margin: 0,
                }}
              >
                {generatedMarkdown}
              </pre>
            ) : (
              <div style={{ fontSize: '13px', lineHeight: 1.6, color: '#334155' }}>
                <pre
                  style={{
                    backgroundColor: '#f8fafc',
                    color: '#1e293b',
                    padding: '16px',
                    borderRadius: '8px',
                    fontSize: '12px',
                    fontFamily: 'system-ui, sans-serif',
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.6,
                    border: '1px solid #e2e8f0',
                    margin: 0,
                  }}
                >
                  {generatedMarkdown}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

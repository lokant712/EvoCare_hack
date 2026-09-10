# EvoCare Doctor Dashboard & Longitudinal Patient View

The frontend workstation interface for **EvoCare — Longitudinal Patient Health Memory & Clinical Intelligence**.

---

## 1. Overview
The Doctor Dashboard provides clinicians with an instant, prioritized understanding of a patient's health trajectory over time without having to manually inspect dozens of disconnected records.

### Core Visual Capabilities:
- **Patient Identity & Demographics**: Clear synthetic demo classification.
- **Priority Doctor View (Recent Changes)**: Answers *"What changed in this patient recently?"* in seconds with directional trajectory indicators (`IMPROVEMENT`, `DECLINE`, `FLUCTUATION`, `NEW_OBSERVATION`).
- **Clinician-Confirmed Medical Context**: Tabbed views of ICD-10 Diagnoses, Active Medications (dose, frequency, indication), and Historical Laboratory results.
- **Caregiver Observation Feed**: Visually separated natural language reports with observer IDs (`CG001`, `CG002`) and timestamps.
- **Longitudinal Evolving Memory**: Synthesized health memory with version tracking and audit history.
- **Chronological Patient Timeline**: Unified event stream across doctor assessments, labs, and caregiver notes.
- **Contextual Discrepancies & Conflicts**: Side-by-side doctor vs caregiver perspectives preserved contextually.
- **Provenance & [Why?] Derivation Trace**: One-click deep link tracing any AI-derived memory statement back to its immutable raw evidence records.

---

## 2. Technology Stack
- **Framework**: React 18 with TypeScript
- **Bundler & Dev Server**: Vite 6
- **Icons**: Lucide React
- **Testing**: Vitest + React Testing Library + JSDOM

---

## 3. Installation & Local Development

### Prerequisites
- Node.js >= 18.0.0
- npm >= 9.0.0
- EvoCare FastAPI Backend running at `http://127.0.0.1:8000`

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 3. Run Automated Unit Tests (21 Tests)
```bash
npm test
```

### 4. Build Production Bundle
```bash
npm run build
```

---

## 4. Architectural Rules & Invariants
1. **Read-Only Station**: The Phase 6 dashboard does not contain mutation controls or write actions.
2. **AI-Derived Labeling**: All synthesized claims are marked with the `AI-DERIVED` badge and explicit disclaimer.
3. **Fall vs Near-Fall Invariant**: Near-falls are strictly displayed as near-falls with 0 completed falls.
4. **No Guessed Diagnoses**: Cognition confusion is not labeled as dementia; dizziness etiology remains marked as `UNKNOWN`.
5. **Separation of Concerns**: Caregiver observations are kept visually distinct from clinician-confirmed diagnoses.

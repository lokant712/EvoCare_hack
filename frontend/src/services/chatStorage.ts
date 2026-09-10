import { ClinicalReasoningResponse } from '../types';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  timestamp: string;
  text?: string;
  isInitialSummary?: boolean;
  reasoningData?: ClinicalReasoningResponse;
  error?: string;
}

export interface ChatSession {
  id: string;
  patientCode: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  isPinned?: boolean;
  messages: ChatMessage[];
}

const STORAGE_KEY = 'evocare_doctor_chat_sessions_v1';

// Pre-seeded clinical sessions for doctor reference
const DEFAULT_SESSIONS: ChatSession[] = [
  {
    id: 'session-dizziness-telmisartan',
    patientCode: 'P001',
    title: 'Morning Dizziness & Telmisartan Timing',
    createdAt: 'Today, 08:30 AM',
    updatedAt: 'Today, 08:30 AM',
    isPinned: true,
    messages: [
      {
        id: 'msg-seed-1',
        sender: 'user',
        timestamp: '08:30 AM',
        text: 'Why is she dizzy in the mornings after taking Telmisartan 40mg?',
      },
      {
        id: 'msg-seed-2',
        sender: 'assistant',
        timestamp: '08:30 AM',
        text: '### Clinical Analysis: Morning Postural Hypotension\n\n1. **Longitudinal Evidence**: Caregiver documented 4 distinct lightheadedness episodes occurring within 45 minutes of morning awakening and rising from bed `[EV-CG-040]`.\n2. **Pharmacodynamics**: Patient takes **Telmisartan 40mg** immediately upon waking on an empty stomach. Peak plasma concentration coincides with morning orthostatic vulnerability.\n3. **Clinical Recommendation**: Advise shifting Telmisartan administration to evening (post-dinner) and maintaining a 2-minute seated pause before standing.',
      },
    ],
  },
  {
    id: 'session-fall-risk-gait',
    patientCode: 'P001',
    title: 'Fall Risk & Near-Bathroom Stumble',
    createdAt: 'Yesterday, 04:15 PM',
    updatedAt: 'Yesterday, 04:15 PM',
    isPinned: true,
    messages: [
      {
        id: 'msg-seed-3',
        sender: 'user',
        timestamp: '04:15 PM',
        text: 'Evaluate fall risk and mobility trajectory based on recent logs.',
      },
      {
        id: 'msg-seed-4',
        sender: 'assistant',
        timestamp: '04:15 PM',
        text: '### Fall Risk & Gait Assessment\n\n- **Trajectory**: Moderate risk elevation over the last 14 days.\n- **Key Event**: Near-fall stumble near bathroom doorframe at 06:15 AM `[EV-CG-042]`. Zero ground impact or trauma.\n- **Contributing Factors**: Bilateral knee osteoarthritic stiffness upon morning waking + unlit hallway.\n- **Interventions**: Recommended installation of motion-sensor nightlights and quad-cane evaluation.',
      },
    ],
  },
  {
    id: 'session-metformin-renal',
    patientCode: 'P001',
    title: 'Metformin vs eGFR Clearance Review',
    createdAt: 'Sep 9, 11:20 AM',
    updatedAt: 'Sep 9, 11:20 AM',
    isPinned: false,
    messages: [
      {
        id: 'msg-seed-5',
        sender: 'user',
        timestamp: '11:20 AM',
        text: 'Review Metformin 500mg BD adherence against latest renal function labs.',
      },
      {
        id: 'msg-seed-6',
        sender: 'assistant',
        timestamp: '11:20 AM',
        text: '### Renal Clearance & Glycemic Control\n\n- **Current eGFR**: 68 mL/min/1.73m² (Mildly decreased, safe for Metformin therapy >45 mL/min).\n- **HbA1c**: 7.2% (Target <7.5% for age 72).\n- **Caregiver Adherence**: 94% compliance logged over last 30 days `[EV-CG-038]`.\n- **Conclusion**: Current Metformin 500mg BID regimen remains safe and effective with bi-annual renal monitoring.',
      },
    ],
  },
];

export const chatStorageService = {
  getSessions(patientCode: string): ChatSession[] {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed: ChatSession[] = JSON.parse(stored);
        const filtered = parsed.filter((s) => s.patientCode === patientCode);
        if (filtered.length > 0) return filtered;
      }
    } catch (e) {
      console.warn('Failed to read chat sessions from localStorage:', e);
    }
    // Return default filtered sessions
    return DEFAULT_SESSIONS.filter((s) => s.patientCode === patientCode);
  },

  saveSession(session: ChatSession): void {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      let sessions: ChatSession[] = stored ? JSON.parse(stored) : DEFAULT_SESSIONS;
      const index = sessions.findIndex((s) => s.id === session.id);
      if (index >= 0) {
        sessions[index] = session;
      } else {
        sessions = [session, ...sessions];
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
    } catch (e) {
      console.warn('Failed to save chat session:', e);
    }
  },

  createNewSession(patientCode: string, title?: string): ChatSession {
    const newSession: ChatSession = {
      id: 'session-' + Date.now(),
      patientCode,
      title: title || 'New Consultation Inquiry',
      createdAt: 'Just now',
      updatedAt: 'Just now',
      isPinned: false,
      messages: [],
    };
    this.saveSession(newSession);
    return newSession;
  },

  deleteSession(sessionId: string): void {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const sessions: ChatSession[] = JSON.parse(stored);
        const filtered = sessions.filter((s) => s.id !== sessionId);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
      }
    } catch (e) {
      console.warn('Failed to delete chat session:', e);
    }
  },

  renameSession(sessionId: string, newTitle: string): void {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const sessions: ChatSession[] = JSON.parse(stored);
        const session = sessions.find((s) => s.id === sessionId);
        if (session) {
          session.title = newTitle;
          session.updatedAt = 'Just now';
          localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
        }
      }
    } catch (e) {
      console.warn('Failed to rename session:', e);
    }
  },
};

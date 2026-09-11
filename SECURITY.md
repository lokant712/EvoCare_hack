# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Invariants in EvoCare

EvoCare implements rigorous security and safety guardrails for geriatric health management:

1. **Two-Factor Physician Verification Gate (2FA)**:
   Physicians cannot unlock or inspect longitudinal patient health records without entering a 6-digit consent OTP dispatched to the patient's registered email address.

2. **Session Lifecycles & Auto-Timeout**:
   Clinical charts auto-lock after 10 minutes of active session time to prevent unauthorized unattended access.

3. **Multi-Role RBAC Authorization**:
   - **DOCTOR**: Access to clinical decision support, diagnostic entry, and verified patient charts.
   - **CAREGIVER**: Restricted strictly to observation logging and caregiver coordination notes.
   - **PATIENT**: AI health companion access and caregiver connection management.
   - **ADMIN**: User role assignment, provider access control, and audit logs.

4. **Deterministic Clinical Safety Engine**:
   AI layers are strictly decision-support agents; autonomous speculative diagnoses and unverified medication alteration prompts are structurally blocked.

5. **Secrets & Environment Isolation**:
   No hardcoded secrets or production keys exist in the codebase. All sensitive API credentials are read from runtime environment variables.

## Reporting a Vulnerability

If you discover a security vulnerability within EvoCare, please report it privately to the maintainers or open a confidential security advisory on GitHub.

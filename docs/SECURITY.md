# EvoCare — Security, RBAC & Audit Architecture

EvoCare implements defense-in-depth security engineered specifically for clinical environments.

```
       AUTHENTICATE THE USER
                 ↓
         AUTHORIZE THE ROLE
                 ↓
        AUTHORIZE THE PATIENT
                 ↓
     RETRIEVE MINIMUM REQUIRED DATA
                 ↓
         AUDIT THE ACTION
                 ↓
       PRESERVE IMMUTABILITY
```

---

## 1. Authentication

- **Mechanism**: OAuth2 Password Bearer flow with JSON Web Tokens (JWT).
- **Algorithm**: `HS256` signed with backend secret key.
- **Hashing**: `bcrypt` password hashing with salt rounds.
- **Lifetimes**: Access tokens valid for 60 minutes; refresh tokens supported for rotation.
- **Protection**: Brute-force rate limiting blocks repeated failed logins per IP and username.

---

## 2. Role-Based Access Control (RBAC) Matrix

| Resource / Action | DOCTOR | CAREGIVER | ADMIN |
| :--- | :---: | :---: | :---: |
| **View Assigned Patient Dashboard** | ✅ ALLOWED | ✅ ALLOWED | ❌ FORBIDDEN |
| **View Longitudinal Health Memory** | ✅ ALLOWED | ✅ ALLOWED | ❌ FORBIDDEN |
| **View Raw Evidence & Provenance** | ✅ ALLOWED | ✅ ALLOWED | ❌ FORBIDDEN |
| **Query Clinical Reasoning Assistant**| ✅ ALLOWED | ❌ FORBIDDEN | ❌ FORBIDDEN |
| **Submit Caregiver Observations** | ❌ FORBIDDEN | ✅ ALLOWED | ❌ FORBIDDEN |
| **Modify Clinical Diagnoses / Labs** | ❌ READ-ONLY | ❌ FORBIDDEN | ❌ FORBIDDEN |
| **Manage User Accounts & Grants** | ❌ FORBIDDEN | ❌ FORBIDDEN | ✅ ALLOWED |
| **Inspect System Security & Audit Log**| ❌ FORBIDDEN | ❌ FORBIDDEN | ✅ ALLOWED |

> **Critical Rule**: Frontend role hiding is NOT authorization. Every single permission check is enforced server-side via FastAPI dependency injection (`get_current_user`, `require_doctor`, `verify_patient_access`).

---

## 3. Patient-Level Access Isolation

Authentication alone does not grant access to patient records. Access requires an active grant record in `patient_access_grants`:

- `doctor.demo` has access to `P001` (Meenakshi Raman).
- `doctor.other` has access to `P002` (Ananya Sharma).
- Attempting to query `/api/dashboard/patients/P002` while authenticated as `doctor.demo` immediately returns **HTTP 403 Forbidden** and logs a `PATIENT_ACCESS_DENIED` security event.

---

## 4. Prompt Injection & Adversarial Defense

The Doctor Clinical Reasoning Assistant (`/api/clinical-reasoning/{patient_id}`) processes user queries alongside clinical data. To prevent prompt injection attacks:

1. **Pre-LLM Regex Filtering**:
   - Matches and rejects known adversarial jailbreak patterns:
     - `"ignore all instructions"`
     - `"disregard all previous rules"`
     - `"bypass safety"`
     - `"system prompt override"`
     - `"diagnose directly"`
   - Rejections return **HTTP 422** and log a `PROMPT_INJECTION_ATTEMPT` security event with IP address and user ID.
2. **Deterministic Post-LLM Schema Validation**:
   - Even if an LLM generates unexpected text, `ClinicalReasoningValidator` enforces strictly typed Pydantic models.
   - Any consideration claiming a definitive diagnosis or unauthorized prescription is stripped or rejected.

---

## 5. Security Audit Logging

All security-relevant actions are recorded immutably in the `audit_logs` and `security_events` database tables:

- `LOGIN_SUCCESS` / `LOGIN_FAILURE`
- `DASHBOARD_VIEW`
- `CLINICAL_REASONING_QUERY`
- `PATIENT_ACCESS_DENIED`
- `PROMPT_INJECTION_ATTEMPT`

Each audit entry captures:
- `user_id` & `username`
- `role`
- `patient_id`
- `ip_address`
- `correlation_id` (UUID)
- `timestamp` (UTC)
- `details` (JSON payload summary)

---

## 6. HTTP Security Headers

The FastAPI middleware automatically attaches standard security headers to every response:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`

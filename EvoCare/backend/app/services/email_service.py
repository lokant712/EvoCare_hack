import os
import smtplib
import logging
from pathlib import Path
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, List, Optional
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

logger = logging.getLogger(__name__)

class EmailService:
    _sent_emails: List[Dict[str, Any]] = []

    @classmethod
    def send_patient_access_code(
        cls,
        patient_email: str,
        patient_name: str,
        patient_code: str,
        doctor_name: str,
        verification_code: str
    ) -> Dict[str, Any]:
        """
        Sends 6-digit access OTP to patient's email (default: lokanthsrihari7@gmail.com).
        """
        # Dynamically reload .env to ensure fresh credentials
        if load_dotenv:
            env_path = Path(__file__).resolve().parent.parent.parent / ".env"
            if env_path.exists():
                load_dotenv(env_path, override=True)

        target_email = (patient_email or "lokanthsrihari7@gmail.com").strip()
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "").strip()
        raw_password = os.getenv("SMTP_PASSWORD", "").strip()
        # Google App Passwords are 16 chars with spaces like 'onvq jxdx olku edlo'
        smtp_password = raw_password.replace(" ", "")
        sender_email = os.getenv("EMAIL_FROM", smtp_user or "lokanthsrihari7@gmail.com").strip()

        subject = f"[EvoCare Security] Physician Access Verification Code for {patient_name} ({patient_code})"

        text_body = f"""
Dear {patient_name},

A healthcare provider, Dr. {doctor_name}, has requested access to your longitudinal medical records on the EvoCare Health Platform.

Your 6-digit Physician Consent Verification Code is:
=========================
        {verification_code}
=========================

Please share this code with your doctor ONLY if you authorize them to view your health records and clinical history.
This verification code will expire in 10 minutes.

If you did not expect this request, please contact your care team immediately.

Warm regards,
EvoCare Clinical Intelligence Team
"""

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px; }}
    .card {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
    .header {{ background: linear-gradient(135deg, #0369a1, #0284c7); padding: 24px; color: #ffffff; text-align: center; }}
    .header h1 {{ margin: 0; font-size: 20px; font-weight: 700; }}
    .content {{ padding: 24px; color: #334155; line-height: 1.6; font-size: 14px; }}
    .code-box {{ background: #f0f9ff; border: 2px dashed #0284c7; border-radius: 8px; padding: 16px; text-align: center; margin: 20px 0; }}
    .code {{ font-family: 'Courier New', Courier, monospace; font-size: 32px; font-weight: 800; color: #0369a1; letter-spacing: 6px; }}
    .footer {{ background: #f1f5f9; padding: 14px; text-align: center; font-size: 11px; color: #64748b; border-top: 1px solid #e2e8f0; }}
    .badge {{ display: inline-block; padding: 3px 8px; background: #e0f2fe; color: #0369a1; border-radius: 4px; font-weight: 600; font-size: 12px; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h1>EvoCare Clinical Health Memory</h1>
      <div style="font-size: 12px; opacity: 0.9; margin-top: 4px;">Physician 2-Step Access Authorization</div>
    </div>
    <div class="content">
      <p>Hello <b>{patient_name}</b>,</p>
      <p><b>Dr. {doctor_name}</b> has requested access to view your complete longitudinal health memory and clinical records on EvoCare.</p>
      
      <div class="code-box">
        <div style="font-size: 11px; text-transform: uppercase; color: #0284c7; font-weight: 700; margin-bottom: 6px;">Your 6-Digit Consent Code</div>
        <div class="code">{verification_code}</div>
        <div style="font-size: 11px; color: #64748b; margin-top: 6px;">Expires in 10 minutes</div>
      </div>

      <p style="font-size: 13px; color: #475569;">
        🔒 <b>Patient Privacy Protection:</b> Share this code with your doctor only if you give permission to open your health profile.
      </p>
    </div>
    <div class="footer">
      Patient Code: <span class="badge">{patient_code}</span> · EvoCare Health Security System · Destination: {target_email}
    </div>
  </div>
</body>
</html>
"""

        dispatch_status = "SENT"
        error_msg = None

        # Try sending live SMTP if credentials provided
        if smtp_user and smtp_password:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = sender_email
                msg["To"] = target_email
                msg.attach(MIMEText(text_body, "plain"))
                msg.attach(MIMEText(html_body, "html"))

                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    server.sendmail(sender_email, [target_email], msg.as_string())
                logger.info(f"Successfully dispatched 2FA email to {target_email} via SMTP.")
            except Exception as e:
                logger.warning(f"SMTP dispatch warning (logged for offline reliability): {e}")
                dispatch_status = "LOGGED_LOCAL"
                error_msg = str(e)
        else:
            # Simulated local dispatch when SMTP credentials are not in .env
            dispatch_status = "SIMULATED_DISPATCH"
            logger.info(f"[EMAIL DISPATCH SIMULATION] Sent OTP {verification_code} to {target_email} for patient {patient_code} ({patient_name})")

        record = {
            "recipient": target_email,
            "patient_name": patient_name,
            "patient_code": patient_code,
            "doctor_name": doctor_name,
            "verification_code": verification_code,
            "subject": subject,
            "status": dispatch_status,
            "error": error_msg,
            "sent_at": datetime.now(timezone.utc).isoformat()
        }
        cls._sent_emails.append(record)
        return record

    @classmethod
    def get_recent_sent_emails(cls) -> List[Dict[str, Any]]:
        return cls._sent_emails[-20:]

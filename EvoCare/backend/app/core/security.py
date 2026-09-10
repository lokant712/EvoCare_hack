import uuid
import time
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Set
from jose import jwt, JWTError

from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory revoked token blacklist for logout
_REVOKED_TOKENS: Set[str] = set()

# In-memory rate-limiter: tracking {key: [timestamp, ...]}
_FAILED_LOGIN_ATTEMPTS: Dict[str, list] = {}
_RATE_LIMIT_WINDOW_SECONDS = 300  # 5 minutes
_MAX_FAILED_ATTEMPTS = 5


def hash_password(password: str) -> str:
    """Hash password using bcrypt with salt."""
    if not password:
        raise ValueError("Password cannot be empty.")
    # Truncate to 72 bytes if needed for bcrypt safety
    pw_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pw_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        pw_bytes = plain_password.encode('utf-8')[:72]
        return bcrypt.checkpw(pw_bytes, hashed_password.encode('utf-8'))
    except Exception as e:
        logger.warning(f"Password verification error: {e}")
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create short-lived JWT access token."""
    to_encode = data.copy()
    now_ts = int(time.time())
    expire_seconds = int(expires_delta.total_seconds()) if expires_delta else (settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    expire_ts = now_ts + expire_seconds
    
    to_encode.update({
        "iat": now_ts,
        "exp": expire_ts,
        "jti": str(uuid.uuid4()),
        "type": "access"
    })
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create long-lived JWT refresh token."""
    to_encode = data.copy()
    now_ts = int(time.time())
    expire_seconds = int(expires_delta.total_seconds()) if expires_delta else (settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400)
    expire_ts = now_ts + expire_seconds
    
    to_encode.update({
        "iat": now_ts,
        "exp": expire_ts,
        "jti": str(uuid.uuid4()),
        "type": "refresh"
    })
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt



def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT token."""
    if is_token_revoked(token):
        raise ValueError("Token has been revoked/logged out.")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid or expired token: {str(e)}")


def revoke_token(token: str) -> None:
    """Revoke a token on logout."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": False})
        jti = payload.get("jti", token)
        _REVOKED_TOKENS.add(jti)
    except Exception:
        _REVOKED_TOKENS.add(token)


def is_token_revoked(token: str) -> bool:
    """Check if token or its jti is in the revocation blacklist."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": False})
        jti = payload.get("jti")
        if jti and jti in _REVOKED_TOKENS:
            return True
    except Exception:
        pass
    return token in _REVOKED_TOKENS


# Rate limiting helpers
def check_login_rate_limit(identifier: str) -> bool:
    """Check if an identifier (username or IP) is rate-limited due to repeated failures."""
    now = time.time()
    attempts = _FAILED_LOGIN_ATTEMPTS.get(identifier, [])
    # Filter attempts within window
    valid_attempts = [t for t in attempts if now - t < _RATE_LIMIT_WINDOW_SECONDS]
    _FAILED_LOGIN_ATTEMPTS[identifier] = valid_attempts
    return len(valid_attempts) < _MAX_FAILED_ATTEMPTS


def record_failed_login(identifier: str) -> None:
    """Record a failed login timestamp."""
    now = time.time()
    attempts = _FAILED_LOGIN_ATTEMPTS.get(identifier, [])
    attempts.append(now)
    _FAILED_LOGIN_ATTEMPTS[identifier] = attempts


def reset_failed_logins(identifier: str) -> None:
    """Reset failed login tracker upon successful authentication."""
    if identifier in _FAILED_LOGIN_ATTEMPTS:
        del _FAILED_LOGIN_ATTEMPTS[identifier]

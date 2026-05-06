"""
AutoJustice AI NEXUS - Authentication Router
JWT-based authentication for police officers.
Passwords hashed with bcrypt. Tokens expire after configured duration.
"""
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from models.db_models import OfficerUser, AuditLog
from models.schemas import OfficerLoginRequest, Token, OfficerCreate, OfficerResponse
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer(auto_error=False)

# ─── JWT Setup ───────────────────────────────────────────────────────────────
try:
    from jose import JWTError, jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logger.error("python-jose not installed. Run: pip install python-jose[cryptography]")

# ─── Bcrypt Setup (direct — bypasses passlib/bcrypt version incompatibility) ─
try:
    import bcrypt as _bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logger.error("bcrypt not installed. Run: pip install bcrypt")


# ─── Helper Functions ─────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    """Hash password using bcrypt directly. Truncates to 72 bytes (bcrypt limit)."""
    if not BCRYPT_AVAILABLE:
        raise RuntimeError("bcrypt is required. Run: pip install bcrypt")
    pwd_bytes = password.encode("utf-8")[:72]
    return _bcrypt.hashpw(pwd_bytes, _bcrypt.gensalt(12)).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    if not BCRYPT_AVAILABLE:
        return False
    try:
        return _bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except Exception:
        return False


def _create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    if not JWT_AVAILABLE:
        raise RuntimeError("python-jose is required for authentication")
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def _decode_token(token: str) -> Optional[dict]:
    if not JWT_AVAILABLE:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


def get_current_officer(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[OfficerUser]:
    """
    FastAPI dependency: extract and validate JWT from Authorization header.
    Returns the OfficerUser or None if token is missing/invalid.
    Use require_officer() to enforce authentication.
    """
    if not credentials:
        return None
    payload = _decode_token(credentials.credentials)
    if not payload:
        return None
    officer_id = payload.get("sub")
    if not officer_id:
        return None
    officer = db.query(OfficerUser).filter(
        OfficerUser.id == officer_id,
        OfficerUser.is_active == True,
    ).first()
    return officer


def require_officer(
    officer: Optional[OfficerUser] = Depends(get_current_officer),
) -> OfficerUser:
    """Strict auth dependency — raises 401 if no valid token."""
    if not officer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return officer


def require_admin(
    officer: OfficerUser = Depends(require_officer),
) -> OfficerUser:
    """Admin-only dependency — raises 403 for non-admin officers."""
    if officer.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return officer


def ensure_default_admin(db: Session) -> None:
    """
    Create default admin account if no officers exist.
    Called on application startup.
    """
    if not JWT_AVAILABLE or not BCRYPT_AVAILABLE:
        logger.warning("Auth dependencies not installed — skipping default admin creation")
        return

    count = db.query(OfficerUser).count()
    if count == 0:
        admin = OfficerUser(
            id=str(uuid.uuid4()),
            username=settings.default_admin_username,
            full_name="System Administrator",
            hashed_password=_hash_password(settings.default_admin_password),
            role="admin",
            department="Cyber Crime Police Station",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        logger.info(
            f"Default admin created: username='{settings.default_admin_username}' "
            f"— CHANGE THE PASSWORD IMMEDIATELY IN PRODUCTION"
        )


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/login", response_model=Token)
def login(payload: OfficerLoginRequest, db: Session = Depends(get_db)):
    """Officer login — returns a JWT Bearer token."""
    if not JWT_AVAILABLE or not BCRYPT_AVAILABLE:
        raise HTTPException(503, "Authentication service unavailable — missing dependencies.")

    officer = db.query(OfficerUser).filter(
        OfficerUser.username == payload.username.strip(),
        OfficerUser.is_active == True,
    ).first()

    if not officer or not _verify_password(payload.password, officer.hashed_password):
        logger.warning(f"Failed login attempt for username: {payload.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    officer.last_login = datetime.utcnow()
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        action="OFFICER_LOGIN",
        actor=officer.username,
        actor_id=officer.id,
        details={"role": officer.role},
    ))
    db.commit()

    token = _create_access_token({
        "sub": officer.id,
        "username": officer.username,
        "role": officer.role,
    })

    return Token(
        access_token=token,
        token_type="bearer",
        officer_id=officer.id,
        full_name=officer.full_name,
        role=officer.role,
        badge_number=officer.badge_number,
    )


@router.get("/me", response_model=OfficerResponse)
def get_me(officer: OfficerUser = Depends(require_officer)):
    """Get current officer's profile."""
    return officer


@router.post("/officers", response_model=OfficerResponse)
def create_officer(
    payload: OfficerCreate,
    db: Session = Depends(get_db),
    admin: OfficerUser = Depends(require_admin),
):
    """Admin only: create a new officer account."""
    if not JWT_AVAILABLE or not BCRYPT_AVAILABLE:
        raise HTTPException(503, "Auth dependencies not installed.")

    existing = db.query(OfficerUser).filter(
        OfficerUser.username == payload.username.strip()
    ).first()
    if existing:
        raise HTTPException(400, f"Username '{payload.username}' already exists.")

    officer = OfficerUser(
        id=str(uuid.uuid4()),
        username=payload.username.strip(),
        full_name=payload.full_name.strip(),
        hashed_password=_hash_password(payload.password),
        badge_number=payload.badge_number,
        email=payload.email,
        rank=payload.rank,
        department=payload.department,
        phone=payload.phone,
        role=payload.role,
    )
    db.add(officer)
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        action="OFFICER_CREATED",
        actor=admin.username,
        actor_id=admin.id,
        details={"new_officer": payload.username, "role": payload.role},
    ))
    db.commit()
    db.refresh(officer)
    return officer


@router.get("/officers", response_model=list[OfficerResponse])
def list_officers(
    db: Session = Depends(get_db),
    officer: OfficerUser = Depends(require_officer),
):
    """List all active officers (accessible to all officers)."""
    return db.query(OfficerUser).filter(OfficerUser.is_active == True).all()


@router.put("/officers/{officer_id}/deactivate")
def deactivate_officer(
    officer_id: str,
    db: Session = Depends(get_db),
    admin: OfficerUser = Depends(require_admin),
):
    """Admin only: deactivate an officer account."""
    target = db.query(OfficerUser).filter(OfficerUser.id == officer_id).first()
    if not target:
        raise HTTPException(404, "Officer not found.")
    if target.id == admin.id:
        raise HTTPException(400, "Cannot deactivate your own account.")
    target.is_active = False
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        action="OFFICER_DEACTIVATED",
        actor=admin.username,
        actor_id=admin.id,
        details={"target_officer": target.username},
    ))
    db.commit()
    return {"success": True, "message": f"Officer {target.username} deactivated."}

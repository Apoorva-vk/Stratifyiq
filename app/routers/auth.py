import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.deps import get_current_user, require_role
from app.models import Company, Invite, PasswordReset, PendingVerification, User
from app.schemas import (
    AcceptInviteIn, ForgotPasswordIn, InviteIn, LoginIn, ResetPasswordIn, SignupIn, TokenOut, VerifyIn,
)
from app.security import create_access_token, hash_password, utcnow_naive, verify_password
from app.services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_for(user: User) -> TokenOut:
    return TokenOut(
        access_token=create_access_token(user.id, user.role, user.company_id),
        role=user.role,
        company_id=user.company_id,
    )


def _send_verification(db: Session, user: User) -> dict:
    token = secrets.token_urlsafe(24)
    old = db.get(PendingVerification, user.id)
    if old is not None:
        db.delete(old)
        db.flush()
    db.add(PendingVerification(user_id=user.id, token=token, expires_at=utcnow_naive() + timedelta(hours=24)))
    db.commit()
    link = f"{settings.APP_BASE_URL}/?verify={token}"
    sent = send_email(
        user.email,
        "Confirm your StratifyIQ email",
        "Welcome to StratifyIQ. Confirm your email address within 24 hours using this link:\n"
        f"{link}\n",
    )
    result = {"email_sent": sent}
    if not sent and settings.EMAIL_DEV_FALLBACK:
        result["verify_token"] = token
        result["verify_link"] = link
    return result


@router.post("/signup", status_code=201)
def signup(body: SignupIn, db: Session = Depends(get_db)):
    """Creates a company workspace and its Admin. The Admin must confirm their email before logging in."""
    if db.scalar(select(User).where(User.email == body.email)):
        raise HTTPException(409, "Email already registered")
    company = Company(name=body.company_name)
    db.add(company)
    db.flush()
    user = User(
        company_id=company.id,
        email=body.email,
        full_name=body.full_name,
        password_hash=hash_password(body.password),
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    result = _send_verification(db, user)
    message = ("Account created. Check your email and confirm it, then log in."
               if result["email_sent"] else
               "Account created. Email is not set up, so use the confirmation link shown here.")
    return {"message": message, **result}


@router.post("/verify")
def verify_email(body: VerifyIn, db: Session = Depends(get_db)):
    pending = db.scalar(select(PendingVerification).where(PendingVerification.token == body.token))
    if pending is None or pending.expires_at < utcnow_naive():
        raise HTTPException(400, "Confirmation link is invalid or has expired")
    db.delete(pending)
    db.commit()
    return {"message": "Email confirmed. You can now log in."}


@router.post("/resend-verification", status_code=202)
def resend_verification(body: ForgotPasswordIn, db: Session = Depends(get_db)):
    response = {"message": "If the account still needs confirming, a new link has been sent."}
    user = db.scalar(select(User).where(User.email == body.email))
    if user is not None and db.get(PendingVerification, user.id) is not None:
        result = _send_verification(db, user)
        response.update({k: v for k, v in result.items() if k.startswith("verify_")})
    return response


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    if not user.is_active:
        raise HTTPException(403, "Account is disabled")
    if db.get(PendingVerification, user.id) is not None:
        raise HTTPException(403, "Please confirm your email first. Check your inbox, or request a new link.")
    return _token_for(user)


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "full_name": user.full_name,
            "role": user.role, "company_id": user.company_id}


@router.post("/invite", status_code=201)
def invite_manager(body: InviteIn, admin: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Admin invites a Manager. The link is emailed; if email is not set up, it is printed
    to the backend console and (in development) returned here."""
    if db.scalar(select(User).where(User.email == body.email)):
        raise HTTPException(409, "Email already registered")
    token = secrets.token_urlsafe(24)
    db.add(Invite(
        company_id=admin.company_id,
        email=body.email,
        role=body.role,
        token=token,
        accepted=False,
        expires_at=utcnow_naive() + timedelta(days=7),
    ))
    db.commit()
    link = f"{settings.APP_BASE_URL}/?invite={token}"
    sent = send_email(
        body.email,
        "You're invited to StratifyIQ",
        "You have been invited to join a StratifyIQ workspace as a Manager.\n\n"
        f"Accept the invitation within 7 days using this link:\n{link}\n",
    )
    result = {
        "message": "Invitation emailed." if sent else "Email is not set up. Share the link below.",
        "email_sent": sent,
        "expires_in_days": 7,
    }
    # Always returned to the Admin who created the invitation, so the link can be shared directly.
    result["invite_token"] = token
    result["invite_link"] = link
    return result


@router.post("/accept-invite", response_model=TokenOut, status_code=201)
def accept_invite(body: AcceptInviteIn, db: Session = Depends(get_db)):
    inv = db.scalar(select(Invite).where(Invite.token == body.token))
    if inv is None or inv.accepted or inv.expires_at < utcnow_naive():
        raise HTTPException(400, "Invite is invalid, used or expired")
    if db.scalar(select(User).where(User.email == inv.email)):
        raise HTTPException(409, "Email already registered")
    user = User(
        company_id=inv.company_id,
        email=inv.email,
        full_name=body.full_name,
        password_hash=hash_password(body.password),
        role=inv.role,
    )
    inv.accepted = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_for(user)


@router.post("/forgot-password", status_code=202)
def forgot_password(body: ForgotPasswordIn, db: Session = Depends(get_db)):
    """Always returns the same message, so accounts cannot be discovered. The reset link is
    emailed. In development (email not set up and EMAIL_DEV_FALLBACK on) the token is also
    returned so the flow can be tested. Turn EMAIL_DEV_FALLBACK off in production."""
    response = {"message": "If the account exists, a reset link has been sent."}
    user = db.scalar(select(User).where(User.email == body.email))
    if user is None or not user.is_active:
        return response
    token = secrets.token_urlsafe(24)
    db.add(PasswordReset(user_id=user.id, token=token,
                         expires_at=utcnow_naive() + timedelta(minutes=30), used=False))
    db.commit()
    link = f"{settings.APP_BASE_URL}/?reset={token}"
    sent = send_email(
        user.email,
        "Reset your StratifyIQ password",
        "Use this link to set a new password (valid for 30 minutes):\n"
        f"{link}\n\nIf you did not ask for this, you can ignore this email.\n",
    )
    if not sent and settings.EMAIL_DEV_FALLBACK:
        response["reset_token"] = token
        response["reset_link"] = link
    return response


@router.post("/reset-password")
def reset_password(body: ResetPasswordIn, db: Session = Depends(get_db)):
    pr = db.scalar(select(PasswordReset).where(PasswordReset.token == body.token))
    if pr is None or pr.used or pr.expires_at < utcnow_naive():
        raise HTTPException(400, "Reset link is invalid or has expired")
    user = db.get(User, pr.user_id)
    user.password_hash = hash_password(body.password)
    db.query(PasswordReset).filter(
        PasswordReset.user_id == user.id, PasswordReset.used.is_(False)
    ).update({PasswordReset.used: True})
    db.commit()
    return {"message": "Password updated. You can now log in."}

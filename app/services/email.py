"""Sends email over SMTP. If SMTP is not configured, the message is printed to the
backend console instead, so the invitation and reset flows can still be tested.
Passwords and tokens are never logged except in that console fallback."""
import smtplib
from email.message import EmailMessage

from app.config import settings


def smtp_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.SMTP_FROM)


def send_email(to: str, subject: str, body: str) -> bool:
    if not smtp_configured():
        print(f"\n[EMAIL not configured, printed instead]\nTo: {to}\nSubject: {subject}\n{body}\n")
        return False
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as exc:  # network or login failure; the caller falls back gracefully
        print(f"[EMAIL failed] {type(exc).__name__}: {exc}")
        return False


def send_email_with_attachment(to: str, subject: str, body: str, data: bytes, filename: str,
                               mime: str = "application/pdf") -> bool:
    """Same SMTP path as send_email, with one file attached."""
    if not smtp_configured():
        print(f"\n[EMAIL not configured, attachment not sent] To: {to}, file: {filename}\n")
        return False
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    maintype, subtype = mime.split("/", 1)
    msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as server:
            server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as exc:
        print(f"[EMAIL failed] {type(exc).__name__}: {exc}")
        return False

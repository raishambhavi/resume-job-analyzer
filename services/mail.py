"""SMTP email sending for password reset (and future notifications)."""
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

MAIL_SERVER = os.environ.get("MAIL_SERVER", "").strip()
MAIL_PORT = int(os.environ.get("MAIL_PORT", "587") or 587)
MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "").strip()
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "").strip()
MAIL_FROM = os.environ.get("MAIL_FROM", "").strip() or MAIL_USERNAME
MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ("1", "true", "yes")
MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "").lower() in ("1", "true", "yes")


def is_mail_configured() -> bool:
    return bool(MAIL_SERVER and MAIL_FROM and MAIL_USERNAME and MAIL_PASSWORD)


def send_email(to_addr: str, subject: str, body_text: str, body_html: Optional[str] = None) -> None:
    if not is_mail_configured():
        raise RuntimeError("Mail is not configured (set MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM).")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = to_addr
    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    if body_html:
        msg.attach(MIMEText(body_html, "html", "utf-8"))

    context = ssl.create_default_context()
    if MAIL_USE_SSL:
        with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT, timeout=30, context=context) as server:
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, to_addr, msg.as_string())
    else:
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=30) as server:
            if MAIL_USE_TLS:
                server.starttls(context=context)
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, to_addr, msg.as_string())

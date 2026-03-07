"""App config: env vars and constants."""
import os

SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-change-in-production"
# Render: set DATABASE_URL to postgres. Local: SQLite.
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///resume_analyzer.db"

# Stripe (optional until you add keys)
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_ID_MONTHLY = os.environ.get("STRIPE_PRICE_ID_MONTHLY", "")  # $10/mo
STRIPE_PRICE_ID_TOPUP = os.environ.get("STRIPE_PRICE_ID_TOPUP", "")     # $1 one-time

# Limits
FREE_BASIC_ANALYSES_PER_MONTH = 20
UPGRADED_DETAILED_ANALYSES_PER_MONTH = 20
TOPUP_PRICE_CENTS = 100  # $1

# Optional: SMTP for password-reset OTP email. If not set, OTP is logged to console (dev only).
MAIL_SERVER = os.environ.get("MAIL_SERVER", "")
MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
MAIL_FROM = os.environ.get("MAIL_FROM", "noreply@resume-role-fit.local")

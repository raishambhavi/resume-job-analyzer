"""App configuration from environment."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-change-in-production"

DATABASE_URL = os.environ.get("DATABASE_URL") or f"sqlite:///{os.path.join(BASE_DIR, 'clear_resume.db')}"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://") :]

SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "").lower() in ("1", "true", "yes")
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "").strip()
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_OAUTH_REDIRECT_URI", "").strip()

LINKEDIN_CLIENT_ID = os.environ.get("LINKEDIN_OAUTH_CLIENT_ID", "").strip()
LINKEDIN_CLIENT_SECRET = os.environ.get("LINKEDIN_OAUTH_CLIENT_SECRET", "").strip()
LINKEDIN_REDIRECT_URI = os.environ.get("LINKEDIN_OAUTH_REDIRECT_URI", "").strip()

# Public site URL for password-reset links (no trailing slash), e.g. https://yourapp.onrender.com
APP_PUBLIC_URL = os.environ.get("APP_PUBLIC_URL", "").strip().rstrip("/")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "").strip()

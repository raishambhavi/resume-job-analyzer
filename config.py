"""App config: env vars and constants."""
import os

# No login or payments; config is minimal.
# Optional: SECRET_KEY if you add sessions later
SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-change-in-production"

"""Database models: User, Analysis, and password-reset OTP."""
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import secrets

db = SQLAlchemy()
bcrypt = Bcrypt()

# OTP validity in seconds (e.g. 10 minutes)
OTP_EXPIRY_SECONDS = 600
OTP_LENGTH = 6


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    plan = db.Column(db.String(20), default="free")  # free | upgraded
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    detailed_extra_remaining = db.Column(db.Integer, default=0)  # top-up analyses
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_upgraded(self) -> bool:
        return self.plan == "upgraded"


class PasswordResetToken(db.Model):
    """One-time OTP for password reset. One per email; overwritten on new request."""
    __tablename__ = "password_reset_tokens"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    otp_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_otp() -> str:
        return "".join(secrets.choice("0123456789") for _ in range(OTP_LENGTH))

    def set_otp(self, otp: str) -> None:
        self.otp_hash = bcrypt.generate_password_hash(otp).decode("utf-8")
        self.expires_at = datetime.utcnow() + timedelta(seconds=OTP_EXPIRY_SECONDS)

    def check_otp(self, otp: str) -> bool:
        if datetime.utcnow() > self.expires_at:
            return False
        return bcrypt.check_password_hash(self.otp_hash, otp)


class Analysis(db.Model):
    __tablename__ = "analyses"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    analysis_type = db.Column(db.String(20), nullable=False)  # basic | detailed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("analyses", lazy="dynamic"))

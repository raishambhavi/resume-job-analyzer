"""Database models for Clear Resume."""
from datetime import datetime

from extensions import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    google_sub = db.Column(db.String(255), unique=True, nullable=True, index=True)
    linkedin_sub = db.Column(db.String(255), unique=True, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship(
        "UserProfileRecord",
        backref=db.backref("user", lazy="joined"),
        uselist=False,
        cascade="all, delete-orphan",
    )
    resumes = db.relationship(
        "SavedResume",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.check_password_hash(self.password_hash, password)


class UserProfileRecord(db.Model):
    """JSON profile blob (manual fields, education, experience arrays, tags)."""

    __tablename__ = "user_profiles"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    data_json = db.Column(db.Text, nullable=False, default="{}")


class SavedResume(db.Model):
    __tablename__ = "saved_resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    display_name = db.Column(db.String(255), nullable=False)
    content_text = db.Column(db.Text, nullable=False, default="")
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PasswordResetToken(db.Model):
    """Single active reset request per email; token verified via bcrypt hash."""

    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    token_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_raw_token(self, raw: str) -> None:
        self.token_hash = bcrypt.generate_password_hash(raw).decode("utf-8")

    def check_raw_token(self, raw: str) -> bool:
        if datetime.utcnow() > self.expires_at:
            return False
        return bcrypt.check_password_hash(self.token_hash, raw)

"""
Clear Resume — Flask API + static SPA.
"""
import json
import os
import secrets
import time
from datetime import datetime, timedelta
from collections import defaultdict
from io import BytesIO
from urllib.parse import quote as url_quote
from urllib.parse import urlencode, urlparse

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, redirect, request, send_file, send_from_directory, session, url_for
from flask_cors import CORS
from pypdf import PdfReader
import docx

import config as app_config
from analyzer import analyze, analyze_basic, analyze_detailed
from extensions import bcrypt, db
from meta_data import JOB_ROLE_SUGGESTIONS, SKILL_SUGGESTIONS
from models import PasswordResetToken, SavedResume, User, UserProfileRecord
from profile_completion import compute_profile_completion
from services.ai_features import generate_interview_prep, resume_builder_narrative
from services.ats_resume import analyze_ats_friendliness, extract_company_name_hint, extract_jd_keywords
from services.company_insights import build_company_insights
from services.mail import is_mail_configured, send_email
from services.pdf_resume import html_to_pdf_bytes
from services.resume_templates import TEMPLATES, render_resume_html

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR)
app.config["SECRET_KEY"] = app_config.SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = app_config.DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_SECURE"] = app_config.SESSION_COOKIE_SECURE
app.config["SESSION_COOKIE_HTTPONLY"] = app_config.SESSION_COOKIE_HTTPONLY
app.config["SESSION_COOKIE_SAMESITE"] = app_config.SESSION_COOKIE_SAMESITE
app.permanent_session_lifetime = timedelta(days=14)

db.init_app(app)
bcrypt.init_app(app)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
_RATE_LIMIT_REQUESTS = 40
_RATE_LIMIT_WINDOW = 60
_rate_limit_store = defaultdict(list)
_forgot_password_store = defaultdict(list)


def _forgot_password_rate_limited(ip: str) -> bool:
    now = time.time()
    window = 3600
    limit = 8
    _forgot_password_store[ip] = [t for t in _forgot_password_store[ip] if t > now - window]
    if len(_forgot_password_store[ip]) >= limit:
        return True
    _forgot_password_store[ip].append(now)
    return False


def _rate_limit_exceeded(ip: str) -> bool:
    now = time.time()
    window_start = now - _RATE_LIMIT_WINDOW
    _rate_limit_store[ip] = [t for t in _rate_limit_store[ip] if t > window_start]
    if len(_rate_limit_store[ip]) >= _RATE_LIMIT_REQUESTS:
        return True
    _rate_limit_store[ip].append(now)
    return False


def _client_ip():
    return (request.headers.get("X-Forwarded-For") or request.remote_addr or "unknown").split(",")[0].strip()


def _current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)


def _require_user():
    u = _current_user()
    if not u:
        return None, (jsonify({"error": "Please sign in or create an account."}), 401)
    return u, None


def _safe_filename_ext(filename: str) -> str:
    if not filename:
        return ""
    name = filename.lower().strip()
    if "." not in name:
        return ""
    return name.rsplit(".", 1)[-1]


def _extract_text_from_pdf_bytes(data: bytes) -> str:
    reader = PdfReader(BytesIO(data))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join([p.strip() for p in parts if p.strip()])


def _extract_text_from_docx_bytes(data: bytes) -> str:
    d = docx.Document(BytesIO(data))
    parts = [p.text.strip() for p in d.paragraphs if p.text and p.text.strip()]
    return "\n".join(parts)


def _extract_text_from_image_bytes(data: bytes) -> str:
    try:
        from PIL import Image  # type: ignore
        import pytesseract  # type: ignore

        img = Image.open(BytesIO(data))
        text = pytesseract.image_to_string(img)
        return (text or "").strip()
    except Exception as e:
        raise ValueError(
            "Image OCR is optional. Use paste/PDF/DOCX, or install Tesseract + Pillow + pytesseract."
        ) from e


def _extract_text_from_upload(file_storage) -> str:
    if file_storage is None:
        raise ValueError("No file uploaded.")
    data = file_storage.read()
    if not data:
        raise ValueError("Uploaded file was empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError("Uploaded file is too large (max 10MB).")
    ext = _safe_filename_ext(file_storage.filename or "")
    content_type = (file_storage.mimetype or "").lower()
    if ext in {"txt"} or content_type.startswith("text/"):
        return data.decode("utf-8", errors="ignore").strip()
    if ext in {"pdf"} or "pdf" in content_type:
        return _extract_text_from_pdf_bytes(data)
    if ext in {"docx"} or "word" in content_type or "officedocument" in content_type:
        return _extract_text_from_docx_bytes(data)
    if ext in {"png", "jpg", "jpeg", "webp"} or content_type.startswith("image/"):
        return _extract_text_from_image_bytes(data)
    raise ValueError("Unsupported file type. Use TXT, PDF, DOCX, or image.")


def _extract_text_from_url(url: str) -> str:
    if not url or not url.strip():
        raise ValueError("URL is required.")
    url = url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Please provide a valid http(s) URL.")
    r = requests.get(url, timeout=20, headers={"User-Agent": "ClearResume/1.0"})
    r.raise_for_status()
    ctype = (r.headers.get("Content-Type") or "").lower()
    content = r.content or b""
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("Linked content is too large (max 10MB).")
    path = (parsed.path or "").lower()
    if "application/pdf" in ctype or path.endswith(".pdf"):
        return _extract_text_from_pdf_bytes(content)
    if "officedocument" in ctype or path.endswith(".docx"):
        return _extract_text_from_docx_bytes(content)
    if ctype.startswith("text/plain") or path.endswith(".txt"):
        return content.decode("utf-8", errors="ignore").strip()
    if "text/html" in ctype or "<html" in content[:5000].lower():
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True).strip()
    return content.decode("utf-8", errors="ignore").strip()


def _get_text_from_multipart(prefix: str) -> str:
    mode = (request.form.get(f"{prefix}_mode") or "paste").strip().lower()
    if mode == "paste":
        return (request.form.get(f"{prefix}_text") or "").strip()
    if mode == "link":
        return _extract_text_from_url(request.form.get(f"{prefix}_link") or "")
    if mode == "file":
        return _extract_text_from_upload(request.files.get(f"{prefix}_file"))
    raise ValueError(f"Invalid {prefix} input mode.")


def _profile_dict(user: User) -> dict:
    rec = UserProfileRecord.query.get(user.id)
    if not rec or not rec.data_json:
        return {}
    try:
        return json.loads(rec.data_json)
    except json.JSONDecodeError:
        return {}


def _set_profile_dict(user: User, data: dict) -> None:
    rec = UserProfileRecord.query.get(user.id)
    if not rec:
        rec = UserProfileRecord(user_id=user.id, data_json="{}")
        db.session.add(rec)
    rec.data_json = json.dumps(data)
    db.session.commit()


def _has_primary_resume(user: User) -> bool:
    return SavedResume.query.filter_by(user_id=user.id, is_primary=True).first() is not None


# --- Auth ---


@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password or len(password) < 8:
        return jsonify({"error": "Valid email and password (8+ characters) required."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists."}), 409
    u = User(email=email)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    db.session.add(UserProfileRecord(user_id=u.id, data_json=json.dumps({"email": email})))
    db.session.commit()
    session["user_id"] = u.id
    session.permanent = True
    return jsonify({"ok": True, "user": {"id": u.id, "email": u.email}})


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    u = User.query.filter_by(email=email).first()
    if not u or not u.check_password(password):
        return jsonify({"error": "Invalid email or password."}), 401
    session["user_id"] = u.id
    session.permanent = True
    return jsonify({"ok": True, "user": {"id": u.id, "email": u.email}})


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/api/auth/me", methods=["GET"])
def me():
    u = _current_user()
    if not u:
        return jsonify({"authenticated": False})
    prof = _profile_dict(u)
    completion = compute_profile_completion(prof, _has_primary_resume(u))
    return jsonify(
        {
            "authenticated": True,
            "user": {"id": u.id, "email": u.email},
            "profile_completion_percent": completion,
        }
    )


@app.route("/api/auth/account", methods=["DELETE"])
def delete_account():
    u, err = _require_user()
    if err:
        return err
    PasswordResetToken.query.filter_by(email=u.email).delete()
    SavedResume.query.filter_by(user_id=u.id).delete()
    UserProfileRecord.query.filter_by(user_id=u.id).delete()
    db.session.delete(u)
    db.session.commit()
    session.clear()
    return jsonify({"ok": True})


@app.route("/api/auth/google/start", methods=["GET"])
def google_start():
    cid = app_config.GOOGLE_CLIENT_ID
    if not cid or not app_config.GOOGLE_CLIENT_SECRET:
        return jsonify({"error": "Google sign-in is not configured on this server."}), 503
    redirect_uri = app_config.GOOGLE_REDIRECT_URI or (request.url_root.rstrip("/") + "/api/auth/google/callback")
    state = secrets.token_urlsafe(16)
    session["oauth_google_state"] = state
    session["oauth_google_redirect_uri"] = redirect_uri
    params = {
        "client_id": cid,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    return redirect("https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params))


@app.route("/api/auth/google/callback", methods=["GET"])
def google_callback():
    if request.args.get("state") != session.get("oauth_google_state"):
        return redirect("/?auth_error=state")
    code = request.args.get("code")
    if not code:
        return redirect("/?auth_error=code")
    redirect_uri = session.get("oauth_google_redirect_uri") or (
        app_config.GOOGLE_REDIRECT_URI or (request.url_root.rstrip("/") + "/api/auth/google/callback")
    )
    token_r = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": app_config.GOOGLE_CLIENT_ID,
            "client_secret": app_config.GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )
    if not token_r.ok:
        return redirect("/?auth_error=token")
    access = token_r.json().get("access_token")
    info_r = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {access}"},
        timeout=20,
    )
    if not info_r.ok:
        return redirect("/?auth_error=userinfo")
    info = info_r.json()
    sub = info.get("sub")
    email = (info.get("email") or "").lower()
    if not sub or not email:
        return redirect("/?auth_error=profile")
    u = User.query.filter_by(google_sub=sub).first()
    if not u:
        u = User.query.filter_by(email=email).first()
        if u:
            u.google_sub = sub
        else:
            u = User(email=email, google_sub=sub, password_hash=None)
            db.session.add(u)
            db.session.commit()
            db.session.add(UserProfileRecord(user_id=u.id, data_json=json.dumps({"email": email})))
            db.session.commit()
    if not UserProfileRecord.query.get(u.id):
        db.session.add(UserProfileRecord(user_id=u.id, data_json=json.dumps({"email": email})))
    db.session.commit()
    session["user_id"] = u.id
    session.permanent = True
    session.pop("oauth_google_state", None)
    session.pop("oauth_google_redirect_uri", None)
    return redirect("/?signed_in=1")


@app.route("/api/auth/linkedin/start", methods=["GET"])
def linkedin_start():
    cid = app_config.LINKEDIN_CLIENT_ID
    if not cid or not app_config.LINKEDIN_CLIENT_SECRET:
        return jsonify({"error": "LinkedIn sign-in is not configured on this server."}), 503
    redirect_uri = app_config.LINKEDIN_REDIRECT_URI or (
        request.url_root.rstrip("/") + "/api/auth/linkedin/callback"
    )
    state = secrets.token_urlsafe(16)
    session["oauth_linkedin_state"] = state
    session["oauth_linkedin_redirect_uri"] = redirect_uri
    params = {
        "response_type": "code",
        "client_id": cid,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": "openid profile email",
    }
    return redirect("https://www.linkedin.com/oauth/v2/authorization?" + urlencode(params))


@app.route("/api/auth/linkedin/callback", methods=["GET"])
def linkedin_callback():
    if request.args.get("state") != session.get("oauth_linkedin_state"):
        return redirect("/?auth_error=linkedin_state")
    code = request.args.get("code")
    if not code:
        return redirect("/?auth_error=linkedin_code")
    redirect_uri = session.get("oauth_linkedin_redirect_uri") or (
        app_config.LINKEDIN_REDIRECT_URI or (request.url_root.rstrip("/") + "/api/auth/linkedin/callback")
    )
    token_r = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": app_config.LINKEDIN_CLIENT_ID,
            "client_secret": app_config.LINKEDIN_CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    if not token_r.ok:
        return redirect("/?auth_error=linkedin_token")
    access = token_r.json().get("access_token")
    if not access:
        return redirect("/?auth_error=linkedin_token")
    info_r = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access}"},
        timeout=20,
    )
    if not info_r.ok:
        return redirect("/?auth_error=linkedin_userinfo")
    info = info_r.json()
    sub = info.get("sub")
    email = (info.get("email") or "").strip().lower()
    if not sub:
        return redirect("/?auth_error=linkedin_profile")
    if not email:
        return redirect("/?auth_error=linkedin_email")
    u = User.query.filter_by(linkedin_sub=sub).first()
    if not u:
        u = User.query.filter_by(email=email).first()
        if u:
            u.linkedin_sub = sub
        else:
            u = User(email=email, linkedin_sub=sub, password_hash=None)
            db.session.add(u)
            db.session.commit()
            db.session.add(UserProfileRecord(user_id=u.id, data_json=json.dumps({"email": email})))
            db.session.commit()
    if not UserProfileRecord.query.get(u.id):
        db.session.add(UserProfileRecord(user_id=u.id, data_json=json.dumps({"email": email})))
    db.session.commit()
    session["user_id"] = u.id
    session.permanent = True
    session.pop("oauth_linkedin_state", None)
    session.pop("oauth_linkedin_redirect_uri", None)
    return redirect("/?signed_in=1")


@app.route("/api/auth/forgot-password", methods=["POST"])
def forgot_password():
    ip = _client_ip()
    if _forgot_password_rate_limited(ip):
        return jsonify({"error": "Too many reset requests. Try again later."}), 429
    if not is_mail_configured():
        return jsonify(
            {
                "error": "Password reset email is not configured. Set MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, and MAIL_FROM.",
            }
        ), 503

    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"error": "Email is required."}), 400

    u = User.query.filter_by(email=email).first()
    if u and u.password_hash:
        raw = secrets.token_urlsafe(32)
        PasswordResetToken.query.filter_by(email=email).delete()
        pr = PasswordResetToken(
            email=email,
            expires_at=datetime.utcnow() + timedelta(hours=2),
        )
        pr.set_raw_token(raw)
        db.session.add(pr)
        db.session.commit()

        base = app_config.APP_PUBLIC_URL or request.url_root.rstrip("/")
        link = f"{base}/?reset_token={raw}&email={url_quote(email, safe='')}"
        subj = "Clear Resume — reset your password"
        body = (
            f"You requested a password reset for Clear Resume.\n\n"
            f"Open this link (valid for 2 hours):\n{link}\n\n"
            f"If you did not request this, you can ignore this email."
        )
        html = f'<p>You requested a password reset for <strong>Clear Resume</strong>.</p><p><a href="{link}">Reset your password</a> (valid for 2 hours).</p><p>If you did not request this, ignore this email.</p>'
        try:
            send_email(email, subj, body, html)
        except Exception as e:
            PasswordResetToken.query.filter_by(email=email).delete()
            db.session.commit()
            return jsonify({"error": f"Could not send email: {e!s}"}), 500

    return jsonify(
        {
            "ok": True,
            "message": "If an account exists with that email, we sent a reset link.",
        }
    )


@app.route("/api/auth/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    token = (data.get("token") or "").strip()
    password = data.get("password") or ""
    if not email or not token:
        return jsonify({"error": "Email and reset token are required."}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400

    pr = PasswordResetToken.query.filter_by(email=email).first()
    if not pr or not pr.check_raw_token(token):
        return jsonify({"error": "Invalid or expired reset link."}), 400

    u = User.query.filter_by(email=email).first()
    if not u:
        return jsonify({"error": "Account not found."}), 404

    u.set_password(password)
    db.session.delete(pr)
    db.session.commit()
    session["user_id"] = u.id
    session.permanent = True
    return jsonify({"ok": True, "message": "Password updated. You are signed in."})


# --- Profile & resumes ---


@app.route("/api/profile", methods=["GET", "PUT"])
def profile():
    u, err = _require_user()
    if err:
        return err
    if request.method == "GET":
        rec = UserProfileRecord.query.get(u.id)
        if not rec:
            rec = UserProfileRecord(user_id=u.id, data_json=json.dumps({"email": u.email}))
            db.session.add(rec)
            db.session.commit()
        data = _profile_dict(u)
        primary = SavedResume.query.filter_by(user_id=u.id, is_primary=True).first()
        return jsonify(
            {
                "profile": data,
                "profile_completion_percent": compute_profile_completion(data, primary is not None),
                "primary_resume_id": primary.id if primary else None,
            }
        )
    body = request.get_json(force=True, silent=True) or {}
    prof = body.get("profile")
    if not isinstance(prof, dict):
        return jsonify({"error": "Expected { profile: { ... } }"}), 400
    skills = prof.get("skills") or []
    roles = prof.get("desired_roles") or []
    if isinstance(skills, list) and len(skills) > 20:
        return jsonify({"error": "Maximum 20 skills."}), 400
    if isinstance(roles, list) and len(roles) > 5:
        return jsonify({"error": "Maximum 5 desired roles."}), 400
    merged = _profile_dict(u)
    merged.update(prof)
    if u.email and not merged.get("email"):
        merged["email"] = u.email
    _set_profile_dict(u, merged)
    primary = SavedResume.query.filter_by(user_id=u.id, is_primary=True).first()
    return jsonify(
        {
            "ok": True,
            "profile_completion_percent": compute_profile_completion(merged, primary is not None),
        }
    )


@app.route("/api/resumes", methods=["GET"])
def list_resumes():
    u, err = _require_user()
    if err:
        return err
    rows = SavedResume.query.filter_by(user_id=u.id).order_by(SavedResume.created_at.desc()).all()
    return jsonify(
        {
            "resumes": [
                {
                    "id": r.id,
                    "display_name": r.display_name,
                    "is_primary": r.is_primary,
                    "preview": (r.content_text or "")[:400],
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in rows
            ]
        }
    )


@app.route("/api/resumes", methods=["POST"])
def upload_resume():
    u, err = _require_user()
    if err:
        return err
    display_name = (request.form.get("display_name") or "Resume").strip() or "Resume"
    text = (request.form.get("content_text") or "").strip()
    if not text and request.files.get("file"):
        text = _extract_text_from_upload(request.files.get("file"))
    if not text:
        return jsonify({"error": "Provide content_text or a PDF/DOCX/TXT file."}), 400
    make_primary = request.form.get("is_primary", "").lower() in ("1", "true", "yes")
    if make_primary:
        SavedResume.query.filter_by(user_id=u.id).update({"is_primary": False})
    r = SavedResume(user_id=u.id, display_name=display_name, content_text=text, is_primary=make_primary)
    db.session.add(r)
    db.session.commit()
    return jsonify({"ok": True, "id": r.id, "is_primary": r.is_primary})


@app.route("/api/resumes/<int:rid>", methods=["GET"])
def get_resume(rid):
    u, err = _require_user()
    if err:
        return err
    r = SavedResume.query.filter_by(id=rid, user_id=u.id).first()
    if not r:
        return jsonify({"error": "Not found."}), 404
    return jsonify(
        {
            "id": r.id,
            "display_name": r.display_name,
            "content_text": r.content_text or "",
            "is_primary": r.is_primary,
        }
    )


@app.route("/api/resumes/<int:rid>/primary", methods=["PATCH"])
def set_primary_resume(rid):
    u, err = _require_user()
    if err:
        return err
    r = SavedResume.query.filter_by(id=rid, user_id=u.id).first()
    if not r:
        return jsonify({"error": "Resume not found."}), 404
    SavedResume.query.filter_by(user_id=u.id).update({"is_primary": False})
    r.is_primary = True
    db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/resumes/<int:rid>", methods=["DELETE"])
def delete_resume(rid):
    u, err = _require_user()
    if err:
        return err
    r = SavedResume.query.filter_by(id=rid, user_id=u.id).first()
    if not r:
        return jsonify({"error": "Not found."}), 404
    db.session.delete(r)
    db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/meta/skills", methods=["GET"])
def meta_skills():
    q = (request.args.get("q") or "").strip().lower()
    if not q:
        return jsonify({"skills": SKILL_SUGGESTIONS[:80]})
    out = [s for s in SKILL_SUGGESTIONS if q in s.lower()][:40]
    return jsonify({"skills": out})


@app.route("/api/meta/job-roles", methods=["GET"])
def meta_roles():
    q = (request.args.get("q") or "").strip().lower()
    if not q:
        return jsonify({"roles": JOB_ROLE_SUGGESTIONS[:60]})
    out = [s for s in JOB_ROLE_SUGGESTIONS if q in s.lower()][:30]
    return jsonify({"roles": out})


# --- Analyze (original + enhanced) ---


@app.route("/api/analyze", methods=["POST"])
def run_analyze():
    ip = _client_ip()
    if _rate_limit_exceeded(ip):
        return jsonify({"error": "Too many requests. Please wait a minute."}), 429
    try:
        if request.is_json:
            data = request.get_json(force=True, silent=True) or {}
            resume = (data.get("resume", "") or "").strip()
            job_description = (data.get("job_description", "") or "").strip()
        else:
            resume = _get_text_from_multipart("resume")
            job_description = _get_text_from_multipart("job")
        if not resume or not job_description:
            return jsonify({"error": "Both resume and job description are required."}), 400
        result = analyze_basic(resume, job_description)
        full = analyze(resume, job_description)
        result["fit_summary"] = full.get("fit_summary")
        result["major_alignment"] = full.get("major_alignment")
        result["major_gaps"] = full.get("major_gaps")
        result["topics_to_prepare"] = full.get("topics_to_prepare")
        return jsonify(result)
    except requests.HTTPError as e:
        return jsonify({"error": f"Failed to fetch link: {e}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze-detailed", methods=["POST"])
def run_analyze_detailed():
    ip = _client_ip()
    if _rate_limit_exceeded(ip):
        return jsonify({"error": "Too many requests."}), 429
    try:
        if request.is_json:
            data = request.get_json(force=True, silent=True) or {}
            resume = (data.get("resume", "") or "").strip()
            job_description = (data.get("job_description", "") or "").strip()
        else:
            resume = _get_text_from_multipart("resume")
            job_description = _get_text_from_multipart("job")
        if not resume or not job_description:
            return jsonify({"error": "Both resume and job description are required."}), 400
        return jsonify(analyze_detailed(resume, job_description))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/resume-templates", methods=["GET"])
def resume_templates_list():
    return jsonify({"templates": TEMPLATES})


@app.route("/api/job-fit-report-multipart", methods=["POST"])
def job_fit_report_multipart():
    """Same as job-fit-report but accepts paste/file/link multipart fields."""
    ip = _client_ip()
    if _rate_limit_exceeded(ip):
        return jsonify({"error": "Too many requests."}), 429
    try:
        resume = _get_text_from_multipart("resume")
        job_description = _get_text_from_multipart("job")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    company = (request.form.get("company_name") or "").strip() or extract_company_name_hint(job_description)
    if not resume or not job_description:
        return jsonify({"error": "Both resume and job description are required."}), 400

    basic = analyze_basic(resume, job_description)
    detailed = analyze_detailed(resume, job_description)
    full = analyze(resume, job_description)
    ats = analyze_ats_friendliness(resume, job_description)
    company_block = build_company_insights(company, job_description[:200])
    deciding = list(detailed.get("deciding_factors") or [])
    for line in company_block.get("summary_bullets", [])[:3]:
        deciding.append(f"Interview intel (search/web): {line}")

    return jsonify(
        {
            "fit_score": basic.get("percentage_fit"),
            "selection_score": basic.get("chances_of_getting_hired"),
            "ats": ats,
            "resume_improvements": detailed.get("tips", []),
            "strengths": detailed.get("strengths"),
            "gaps": detailed.get("gaps_with_score"),
            "deciding_factors": deciding,
            "skills_to_polish": detailed.get("skills_to_prepare"),
            "topics_to_prepare": full.get("topics_to_prepare"),
            "company_insights": company_block,
            "handoff": {
                "resume": resume,
                "job_description": job_description,
                "company_name": company,
            },
        }
    )


@app.route("/api/job-fit-report", methods=["POST"])
def job_fit_report():
    """Full Clear Resume report: fit, ATS, company context, detailed, CTAs data."""
    ip = _client_ip()
    if _rate_limit_exceeded(ip):
        return jsonify({"error": "Too many requests."}), 429
    data = request.get_json(force=True, silent=True) or {}
    resume = (data.get("resume") or "").strip()
    job_description = (data.get("job_description") or "").strip()
    company = (data.get("company_name") or "").strip() or extract_company_name_hint(job_description)
    if not resume or not job_description:
        return jsonify({"error": "resume and job_description are required."}), 400

    basic = analyze_basic(resume, job_description)
    detailed = analyze_detailed(resume, job_description)
    full = analyze(resume, job_description)
    ats = analyze_ats_friendliness(resume, job_description)
    company_block = build_company_insights(company, job_description[:200])

    deciding = list(detailed.get("deciding_factors") or [])
    for line in company_block.get("summary_bullets", [])[:3]:
        deciding.append(f"Interview intel (search/web): {line}")

    return jsonify(
        {
            "fit_score": basic.get("percentage_fit"),
            "selection_score": basic.get("chances_of_getting_hired"),
            "ats": ats,
            "resume_improvements": detailed.get("tips", []),
            "strengths": detailed.get("strengths"),
            "gaps": detailed.get("gaps_with_score"),
            "deciding_factors": deciding,
            "skills_to_polish": detailed.get("skills_to_prepare"),
            "topics_to_prepare": full.get("topics_to_prepare"),
            "company_insights": company_block,
            "handoff": {
                "resume": resume,
                "job_description": job_description,
                "company_name": company,
            },
        }
    )


@app.route("/api/interview-prep", methods=["POST"])
def interview_prep():
    ip = _client_ip()
    if _rate_limit_exceeded(ip):
        return jsonify({"error": "Too many requests."}), 429
    data = request.get_json(force=True, silent=True) or {}
    jd = (data.get("job_description") or "").strip()
    resume = (data.get("resume") or "").strip()
    company = (data.get("company_name") or "").strip() or extract_company_name_hint(jd)
    if not jd:
        return jsonify({"error": "job_description is required."}), 400
    return jsonify(generate_interview_prep(jd, resume, company))


@app.route("/api/resume-builder/analyze", methods=["POST"])
def resume_builder_analyze():
    ip = _client_ip()
    if _rate_limit_exceeded(ip):
        return jsonify({"error": "Too many requests."}), 429
    data = request.get_json(force=True, silent=True) or {}
    jd = (data.get("job_description") or "").strip()
    resume = (data.get("resume") or "").strip()
    if not jd or not resume:
        return jsonify({"error": "job_description and resume are required."}), 400

    keywords = extract_jd_keywords(jd, limit=50)
    ats = analyze_ats_friendliness(resume, jd)
    narrative = resume_builder_narrative(resume, jd, keywords)
    return jsonify(
        {
            "keywords_from_jd": keywords,
            "ats": ats,
            "narrative": narrative,
            "templates": TEMPLATES,
        }
    )


@app.route("/api/resume-builder/preview", methods=["POST"])
def resume_builder_preview():
    data = request.get_json(force=True, silent=True) or {}
    template_id = (data.get("template_id") or "classic-chronological").strip()
    resume = data.get("resume") or ""
    kw = data.get("keyword_line") or ""
    html = render_resume_html(template_id, resume, kw)
    return jsonify({"html": html, "template_id": template_id})


@app.route("/api/resume-builder/pdf", methods=["POST"])
def resume_builder_pdf():
    data = request.get_json(force=True, silent=True) or {}
    template_id = (data.get("template_id") or "classic-chronological").strip()
    resume = data.get("resume") or ""
    kw = data.get("keyword_line") or ""
    html = render_resume_html(template_id, resume, kw)
    try:
        pdf_bytes = html_to_pdf_bytes(html)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="clear-resume-preview.pdf",
    )


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


@app.route("/")
def index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.isfile(index_path):
        return jsonify({"error": "index.html not found"}), 500
    return send_file(index_path, mimetype="text/html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(STATIC_DIR, path)


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    app.run(debug=True, host="127.0.0.1", port=port)

"""
Flask API for Resume–Job Compatibility Analyzer
"""

import os
import time
from collections import defaultdict
from datetime import datetime
from io import BytesIO
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, send_from_directory, send_file, session
from flask_cors import CORS
from pypdf import PdfReader
import docx

from config import (
    SECRET_KEY,
    DATABASE_URL,
    FREE_BASIC_ANALYSES_PER_MONTH,
    UPGRADED_DETAILED_ANALYSES_PER_MONTH,
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
    STRIPE_PRICE_ID_MONTHLY,
    STRIPE_PRICE_ID_TOPUP,
)
from models import db, bcrypt, User, Analysis
from analyzer import analyze_basic, analyze_detailed

# Use absolute path for static folder so it works when deployed (e.g. Render)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app = Flask(__name__, static_folder=STATIC_DIR)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
db.init_app(app)
bcrypt.init_app(app)
CORS(app, supports_credentials=True)


def _start_of_month():
    n = datetime.utcnow()
    return n.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _current_user():
    if not session.get("user_id"):
        return None
    return User.query.get(session["user_id"])


def _basic_used_this_month(user_id: int) -> int:
    return Analysis.query.filter(
        Analysis.user_id == user_id,
        Analysis.analysis_type == "basic",
        Analysis.created_at >= _start_of_month(),
    ).count()


def _detailed_used_this_month(user_id: int) -> int:
    return Analysis.query.filter(
        Analysis.user_id == user_id,
        Analysis.analysis_type == "detailed",
        Analysis.created_at >= _start_of_month(),
    ).count()


MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10MB

# Simple rate limit: max requests per minute per IP (helps protect free tier)
_RATE_LIMIT_REQUESTS = 30
_RATE_LIMIT_WINDOW = 60  # seconds
_rate_limit_store = defaultdict(list)


def _rate_limit_exceeded(ip: str) -> bool:
    now = time.time()
    window_start = now - _RATE_LIMIT_WINDOW
    _rate_limit_store[ip] = [t for t in _rate_limit_store[ip] if t > window_start]
    if len(_rate_limit_store[ip]) >= _RATE_LIMIT_REQUESTS:
        return True
    _rate_limit_store[ip].append(now)
    return False


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
        # Optional dependency: only needed if you use image upload mode.
        from PIL import Image  # type: ignore
        import pytesseract  # type: ignore

        img = Image.open(BytesIO(data))
        text = pytesseract.image_to_string(img)
        return (text or "").strip()
    except Exception as e:
        raise ValueError(
            "Image OCR is optional and not installed on this system yet.\n\n"
            "Fastest option: use Paste / PDF / DOCX instead.\n\n"
            "If you want image OCR:\n"
            "- Install Pillow + pytesseract (Python packages)\n"
            "- Install Tesseract OCR on your computer (macOS Homebrew: `brew install tesseract`)\n"
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

    raise ValueError("Unsupported file type. Please upload TXT, PDF, DOCX, or an image (PNG/JPG).")


def _extract_text_from_url(url: str) -> str:
    if not url or not url.strip():
        raise ValueError("URL is required.")
    url = url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Please provide a valid http(s) URL.")

    r = requests.get(url, timeout=20, headers={"User-Agent": "ResumeRoleFit/1.0"})
    r.raise_for_status()

    ctype = (r.headers.get("Content-Type") or "").lower()
    content = r.content or b""
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("Linked content is too large (max 10MB).")

    # File-like URLs
    path = (parsed.path or "").lower()
    if "application/pdf" in ctype or path.endswith(".pdf"):
        return _extract_text_from_pdf_bytes(content)
    if "officedocument" in ctype or path.endswith(".docx"):
        return _extract_text_from_docx_bytes(content)
    if ctype.startswith("text/plain") or path.endswith(".txt"):
        return content.decode("utf-8", errors="ignore").strip()

    # Default: treat as HTML/text
    if "text/html" in ctype or "<html" in content[:5000].lower():
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return text.strip()

    # Fallback: decode as text
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


@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify({"error": "Email and password required."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists."}), 400
    user = User(email=email, plan="free")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    session["user_id"] = user.id
    return jsonify({"ok": True, "user": {"id": user.id, "email": user.email, "plan": user.plan}})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password."}), 401
    session["user_id"] = user.id
    return jsonify({"ok": True, "user": {"id": user.id, "email": user.email, "plan": user.plan}})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"ok": True})


@app.route("/api/me", methods=["GET"])
def me():
    user = _current_user()
    if not user:
        return jsonify({"user": None}), 200
    basic_used = _basic_used_this_month(user.id)
    detailed_used = _detailed_used_this_month(user.id)
    return jsonify({
        "user": {"id": user.id, "email": user.email, "plan": user.plan, "detailed_extra_remaining": user.detailed_extra_remaining},
        "usage": {
            "basic_used": basic_used,
            "basic_limit": FREE_BASIC_ANALYSES_PER_MONTH,
            "detailed_used": detailed_used,
            "detailed_limit": UPGRADED_DETAILED_ANALYSES_PER_MONTH,
        },
    })


@app.route("/api/analyze", methods=["POST"])
def run_analyze():
    user = _current_user()
    if not user:
        return jsonify({"error": "Please sign up or log in to run an analysis."}), 401
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    if _rate_limit_exceeded(client_ip):
        return jsonify({"error": "Too many requests. Please wait a minute and try again."}), 429
    basic_used = _basic_used_this_month(user.id)
    if basic_used >= FREE_BASIC_ANALYSES_PER_MONTH:
        return jsonify({"error": f"You've used all {FREE_BASIC_ANALYSES_PER_MONTH} free analyses this month. Upgrade for detailed reports and more."}), 402
    try:
        if request.is_json:
            data = request.get_json(force=True, silent=True) or {}
            resume = (data.get("resume", "") or "").strip()
            job_description = (data.get("job_description", "") or "").strip()
        else:
            resume = _get_text_from_multipart("resume")
            job_description = _get_text_from_multipart("job")

        if not resume or not job_description:
            return jsonify({"error": "Both resume and job description are required. Please provide text, a link, or a file for each."}), 400

        result = analyze_basic(resume, job_description)
        rec = Analysis(user_id=user.id, analysis_type="basic")
        db.session.add(rec)
        db.session.commit()
        result["usage"] = {"basic_used": basic_used + 1, "basic_limit": FREE_BASIC_ANALYSES_PER_MONTH}
        return jsonify(result)
    except requests.HTTPError as e:
        return jsonify({"error": f"Failed to fetch link content: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze-detailed", methods=["POST"])
def run_analyze_detailed():
    user = _current_user()
    if not user:
        return jsonify({"error": "Please log in."}), 401
    if not user.is_upgraded:
        return jsonify({"error": "Upgrade to the $10/month plan to get detailed reports."}), 403
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    if _rate_limit_exceeded(client_ip):
        return jsonify({"error": "Too many requests. Please wait a minute and try again."}), 429
    detailed_used = _detailed_used_this_month(user.id)
    allowed = detailed_used < UPGRADED_DETAILED_ANALYSES_PER_MONTH or (user.detailed_extra_remaining or 0) > 0
    if not allowed:
        return jsonify({"error": "You've used your 20 detailed analyses this month. Buy a $1 top-up for one more.", "need_topup": True}), 402
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

        result = analyze_detailed(resume, job_description)
        if detailed_used >= UPGRADED_DETAILED_ANALYSES_PER_MONTH and (user.detailed_extra_remaining or 0) > 0:
            user.detailed_extra_remaining = (user.detailed_extra_remaining or 0) - 1
            db.session.add(user)
        rec = Analysis(user_id=user.id, analysis_type="detailed")
        db.session.add(rec)
        db.session.commit()
        detailed_used_after = _detailed_used_this_month(user.id)
        result["usage"] = {
            "detailed_used": detailed_used_after,
            "detailed_limit": UPGRADED_DETAILED_ANALYSES_PER_MONTH,
            "detailed_extra_remaining": user.detailed_extra_remaining or 0,
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/create-checkout-subscription", methods=["POST"])
def create_checkout_subscription():
    if not STRIPE_SECRET_KEY:
        return jsonify({"error": "Payments not configured."}), 503
    user = _current_user()
    if not user:
        return jsonify({"error": "Log in first."}), 401
    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
        checkout = stripe.checkout.Session.create(
            mode="subscription",
            customer_email=user.email,
            line_items=[{"price": STRIPE_PRICE_ID_MONTHLY, "quantity": 1}],
            success_url=request.host_url.rstrip("/") + "/?upgraded=1",
            cancel_url=request.host_url.rstrip("/") + "/?canceled=1",
            metadata={"user_id": str(user.id)},
        )
        return jsonify({"url": checkout.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/create-checkout-topup", methods=["POST"])
def create_checkout_topup():
    if not STRIPE_SECRET_KEY:
        return jsonify({"error": "Payments not configured."}), 503
    user = _current_user()
    if not user:
        return jsonify({"error": "Log in first."}), 401
    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
        checkout = stripe.checkout.Session.create(
            mode="payment",
            customer_email=user.email,
            line_items=[{"price": STRIPE_PRICE_ID_TOPUP, "quantity": 1}],
            success_url=request.host_url.rstrip("/") + "/?topup=1",
            cancel_url=request.host_url.rstrip("/") + "/?canceled=1",
            metadata={"user_id": str(user.id), "type": "topup"},
        )
        return jsonify({"url": checkout.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stripe-webhook", methods=["POST"])
def stripe_webhook():
    if not STRIPE_WEBHOOK_SECRET:
        return jsonify({"error": "Webhook not configured."}), 503
    payload = request.get_data()
    sig = request.headers.get("Stripe-Signature", "")
    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    if event["type"] == "checkout.session.completed":
        sess = event["data"]["object"]
        user_id = sess.get("metadata", {}).get("user_id")
        if not user_id:
            return jsonify({"ok": True})
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({"ok": True})
        if sess.get("metadata", {}).get("type") == "topup":
            user.detailed_extra_remaining = (user.detailed_extra_remaining or 0) + 1
            db.session.add(user)
        elif sess.get("mode") == "subscription" and sess.get("subscription"):
            user.plan = "upgraded"
            user.stripe_subscription_id = sess["subscription"]
            db.session.add(user)
        db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


@app.route("/")
def index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.isfile(index_path):
        return jsonify({"error": "index.html not found", "static_dir": STATIC_DIR}), 500
    return send_file(index_path, mimetype="text/html")


@app.route("/login")
def login_page():
    p = os.path.join(STATIC_DIR, "login.html")
    return send_file(p, mimetype="text/html") if os.path.isfile(p) else send_file(os.path.join(STATIC_DIR, "index.html"), mimetype="text/html")


@app.route("/signup")
def signup_page():
    p = os.path.join(STATIC_DIR, "signup.html")
    return send_file(p, mimetype="text/html") if os.path.isfile(p) else send_file(os.path.join(STATIC_DIR, "index.html"), mimetype="text/html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(STATIC_DIR, path)


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    app.run(debug=True, host="127.0.0.1", port=port)

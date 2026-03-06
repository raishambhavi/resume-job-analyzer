"""
Flask API for Resume–Job Compatibility Analyzer
"""

import os
from io import BytesIO
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from pypdf import PdfReader
import docx

from analyzer import analyze

# Use absolute path for static folder so it works when deployed (e.g. Render)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)


MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10MB


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


@app.route("/api/analyze", methods=["POST"])
def run_analyze():
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

        result = analyze(resume, job_description)
        return jsonify(result)
    except requests.HTTPError as e:
        return jsonify({"error": f"Failed to fetch link content: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


@app.route("/")
def index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.isfile(index_path):
        return jsonify({"error": "index.html not found", "static_dir": STATIC_DIR}), 500
    return send_file(index_path, mimetype="text/html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(STATIC_DIR, path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    app.run(debug=True, host="127.0.0.1", port=port)

"""
ATS-friendly resume layout presets (simple HTML for preview/download).
Names reflect common recruiter-accepted styles: chronological, clean headings, no tables in body.
"""

from html import escape
from typing import Dict, List


TEMPLATES: List[Dict[str, str]] = [
    {
        "id": "classic-chronological",
        "name": "Classic Chronological",
        "description": "Single column, bold employer lines—most compatible with legacy ATS.",
    },
    {
        "id": "modern-minimal",
        "name": "Modern Minimal",
        "description": "Lots of white space, clear hierarchy; works well with Greenhouse/Lever parsers.",
    },
    {
        "id": "technical-skills-forward",
        "name": "Technical Skills Forward",
        "description": "Skills block near the top for engineering and data roles.",
    },
    {
        "id": "executive-summary-top",
        "name": "Profile + Summary Top",
        "description": "3–4 line summary under name—common for PM, BA, and consulting tracks.",
    },
    {
        "id": "project-heavy",
        "name": "Project-Heavy",
        "description": "Highlights projects under experience—good for early-career and bootcamp grads.",
    },
    {
        "id": "two-tone-headers",
        "name": "Two-Tone Headers",
        "description": "Subtle header bars for sections; still linear reading order for ATS.",
    },
    {
        "id": "compact-one-page",
        "name": "Compact One-Page",
        "description": "Tighter spacing to hit one page while keeping standard headings.",
    },
    {
        "id": "consulting-style",
        "name": "Consulting Style",
        "description": "Impact bullets with metrics first—common in strategy and ops hiring.",
    },
    {
        "id": "academic-cv-lite",
        "name": "Academic CV Lite",
        "description": "Education elevated; suited to research, RA, and lab-adjacent roles.",
    },
    {
        "id": "sales-customer",
        "name": "Sales / Customer",
        "description": "Quota, pipeline, and stakeholder bullets emphasized.",
    },
]


def _wrap_body(inner: str, title: str = "Resume") -> str:
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><title>{escape(title)}</title>
<style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #111; max-width: 720px; margin: 24px auto; line-height: 1.45; font-size: 11pt; }}
h1 {{ font-size: 18pt; margin: 0 0 4px; letter-spacing: 0.02em; }}
.contact {{ font-size: 10pt; color: #333; margin-bottom: 14px; }}
h2 {{ font-size: 11pt; text-transform: uppercase; letter-spacing: 0.06em; border-bottom: 1px solid #ccc; margin: 16px 0 8px; padding-bottom: 2px; }}
.job {{ margin-bottom: 10px; }}
.job-title {{ font-weight: 700; }}
.meta {{ font-size: 10pt; color: #444; }}
ul {{ margin: 4px 0 0 18px; padding: 0; }}
.keywords {{ font-size: 10pt; color: #222; margin-top: 8px; }}
</style></head><body>{inner}</body></html>"""


def render_resume_html(template_id: str, resume_plain: str, keyword_line: str = "") -> str:
    text = escape(resume_plain or "(Paste your resume content here.)")
    kw = escape(keyword_line) if keyword_line else ""

    header_extra = ""
    if template_id == "technical-skills-forward" and kw:
        header_extra = f'<div class="keywords"><strong>Core keywords aligned to role:</strong> {kw}</div>'
    elif template_id == "executive-summary-top":
        header_extra = '<p class="contact"><em>Summary:</em> Results-driven professional aligning experience with role requirements.</p>'

    inner = f"""
<h1>Your Name</h1>
<div class="contact">City, ST • email@example.com • +1 • linkedin.com/in/yourprofile</div>
{header_extra}
<h2>Professional Experience</h2>
<div class="job"><div class="job-title">Role Title</div><div class="meta">Company — Start – End</div>
<ul><li>Achievement with metrics…</li><li>Another bullet tailored to the job…</li></ul></div>
<h2>Education</h2>
<div class="job"><div class="job-title">Degree, Field</div><div class="meta">University — Year</div></div>
<h2>Skills</h2>
<p>{kw or "List tools and methods from the job description that you truly know."}</p>
<h2>Resume content (from your upload)</h2>
<pre style="white-space:pre-wrap;font-family:inherit;font-size:10pt;border:1px solid #ddd;padding:12px;border-radius:6px;background:#fafafa;">{text}</pre>
"""
    return _wrap_body(inner, "ATS-friendly resume preview")

"""
ATS-oriented keyword overlap and simple structure heuristics.
"""
import re
from typing import Dict, List, Set

from analyzer import COMMON_SKILLS, extract_skills_from_text, normalize_text


_STOP = frozenset(
    """
    the a an and or to of in for on with at by from as is are was were be been being
    this that these those it its we you they our your their will can may must should
    all any some not no yes if then else when where what which who how about into over
    out up down new also more most less least other such than then so very just like
    work experience years year team role job company skills requirements responsibilities
    ability strong excellent good great looking hire hiring apply application remote
    full time part contract internship senior junior level preferred plus bonus
    """.split()
)


def extract_jd_keywords(job_description: str, limit: int = 50) -> List[str]:
    """Important tokens + known skills from JD."""
    skills = extract_skills_from_text(job_description)
    norm = normalize_text(job_description)
    # word frequency for substantive tokens
    words = re.findall(r"\b[a-z][a-z0-9+#.-]{2,}\b", norm)
    freq: Dict[str, int] = {}
    for w in words:
        if w in _STOP:
            continue
        freq[w] = freq.get(w, 0) + 1
    ranked = sorted(freq.keys(), key=lambda x: (-freq[x], x))
    out: List[str] = []
    seen: Set[str] = set()
    for s in sorted(skills):
        if s not in seen:
            out.append(s)
            seen.add(s)
    for w in ranked:
        if w not in seen and len(out) < limit:
            out.append(w)
            seen.add(w)
    return out[:limit]


def _detect_sections(resume: str) -> Dict[str, bool]:
    low = resume.lower()
    return {
        "has_experience": bool(re.search(r"\b(experience|employment|work history)\b", low)),
        "has_education": bool(re.search(r"\b(education|university|degree|bachelor|master)\b", low)),
        "has_skills_block": bool(re.search(r"\b(skills|technical skills|competencies)\b", low)),
        "has_contact": bool(re.search(r"\b(@|\+\d|[\w.-]+@[\w.-]+\.\w{2,})\b", low)),
    }


def analyze_ats_friendliness(resume_text: str, job_description: str) -> Dict:
    resume_text = resume_text or ""
    job_description = job_description or ""
    keys = extract_jd_keywords(job_description)
    rnorm = normalize_text(resume_text)
    present = [k for k in keys if k in rnorm]
    missing = [k for k in keys if k not in rnorm]
    denom = max(len(keys), 1)
    keyword_score = round(100 * len(present) / denom)

    sections = _detect_sections(resume_text)
    struct_pts = sum(sections.values())
    struct_score = int(round(100 * struct_pts / len(sections)))
    overall = int(round(keyword_score * 0.72 + struct_score * 0.28))

    tips: List[str] = []
    if not sections["has_skills_block"]:
        tips.append("Add a clearly labeled Skills section with keywords from the job description (only skills you truly have).")
    if not sections["has_experience"]:
        tips.append("Use an Experience or Work History section with employer, title, dates, and bullet achievements.")
    if not sections["has_education"]:
        tips.append("Include Education with degree, field, and institution.")
    if missing[:8]:
        tips.append(
            "Weave missing JD terms into honest bullets where applicable: "
            + ", ".join(missing[:8])
            + ("…" if len(missing) > 8 else "")
        )
    tips.append("Prefer simple formatting: one column, standard headings, no tables for core content—many ATS parsers struggle with complex layouts.")
    tips.append("Mirror phrasing from the posting (e.g. job titles and tool names) without keyword stuffing.")

    friendly = overall >= 68
    return {
        "ats_score": overall,
        "keyword_match_score": keyword_score,
        "structure_score": struct_score,
        "keywords_present_in_resume": present,
        "keywords_missing_from_resume": missing[:25],
        "section_checklist": sections,
        "likely_ats_friendly": friendly,
        "improvement_tips": tips[:10],
    }


def extract_company_name_hint(job_description: str) -> str:
    """Best-effort company name from first lines or common patterns."""
    if not (job_description or "").strip():
        return ""
    lines = [ln.strip() for ln in job_description.strip().splitlines() if ln.strip()]
    for ln in lines[:4]:
        m = re.match(r"^(.{2,80}?)\s+[-–—]\s+", ln)
        if m:
            return m.group(1).strip()
        m2 = re.match(r"^(?:at|@)\s+(.{2,80})$", ln, re.I)
        if m2:
            return m2.group(1).strip()
    return lines[0][:80] if lines else ""

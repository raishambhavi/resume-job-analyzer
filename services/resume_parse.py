"""
Best-effort extraction of profile fields from plain resume text (PDF/DOCX → text).
Not perfect for every format; fills obvious email, phone, name, address, summary, and light education/experience.
"""

import re
from typing import Any, Dict, List, Optional


def _norm(s: str) -> str:
    return " ".join((s or "").split())


def _extract_email(text: str) -> str:
    m = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)
    return m.group(0).lower() if m else ""


def _extract_phone_parts(text: str) -> tuple:
    """Return (country_code, local_digits) e.g. ('+1', '6504308504') or ('', '')."""
    patterns = [
        r"(\+\d{1,3})[\s.\-]*\(?(\d{3})\)?[\s.\-]*(\d{3})[\s.\-]*(\d{4})\b",
        r"\(?(\d{3})\)?[\s.\-]*(\d{3})[\s.\-]*(\d{4})\b",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            g = m.groups()
            if len(g) == 4:
                return g[0], "".join(g[1:4])
            if len(g) == 3:
                return "+1", "".join(g)
    return "", ""


def _candidate_name_lines(lines: List[str]) -> Optional[tuple]:
    skip = {
        "resume",
        "cv",
        "curriculum vitae",
        "phone",
        "email",
        "linkedin",
        "github",
    }
    for ln in lines[:12]:
        low = ln.strip().lower()
        if not low or low in skip:
            continue
        if "@" in ln or re.search(r"\d{3}.*\d{4}", ln):
            continue
        if re.match(r"^(http|www\.|linkedin\.com)", low):
            continue
        parts = ln.split()
        if 2 <= len(parts) <= 5 and len(ln) < 70:
            if re.match(r"^[\w\s\-'.]+$", ln, re.I):
                return parts[0], " ".join(parts[1:])
    return None


def _extract_address_us(text: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    # Multiline: street line then "City, ST ZIP"
    m = re.search(
        r"(?ms)^(\d{1,6}\s+[\w\s#.\-]+?(?:Apt\.?\s*[\w\-]+)?)\s*$\s*^([^,\n]+),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)\s*$",
        text,
        re.MULTILINE,
    )
    if m:
        out["address"] = _norm(m.group(1))
        out["city"] = _norm(m.group(2))
        out["state"] = m.group(3).upper()
        out["zip_code"] = m.group(4)
        return out
    # Any line: City, ST ZIP
    m2 = re.search(r"(?m)^([^,\n]{2,60}),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)\s*$", text)
    if m2:
        out["city"] = _norm(m2.group(1))
        out["state"] = m2.group(2).upper()
        out["zip_code"] = m2.group(3)
    return out


def _extract_summary(text: str) -> str:
    # Section boundaries must be line-anchored so words like "Experienced" do not match "experience".
    _end = r"(?=(?:^|\n)\s*(?:experience|work\s+history|education|skills|projects)\b|\Z)"
    for pat in (
        rf"(?is)(?:professional\s+)?summary\s*:?\s*(.+?){_end}",
        rf"(?is)objective\s*:?\s*(.+?){_end}",
        rf"(?is)profile\s*:?\s*(.+?){_end}",
    ):
        m = re.search(pat, text)
        if m:
            block = _norm(m.group(1))
            if 40 < len(block) < 4000:
                return block[:3500]
    return ""


def _extract_education_lines(text: str) -> List[Dict[str, Any]]:
    out = []
    m = re.search(
        r"(?is)(?:^|\n)\s*education\b\s*:?\s*(.+?)(?=(?:^|\n)\s*(?:experience|work\s+history|employment|skills|projects|certifications)\b|\Z)",
        text,
    )
    if not m:
        return out
    block = m.group(1)
    for ln in block.splitlines():
        ln = ln.strip()
        if len(ln) < 8:
            continue
        if re.search(r"(?i)(university|college|institute|school|bachelor|master|ph\.?d|b\.?s\.?|m\.?s\.?|mba)", ln):
            deg = ln
            spec = ""
            if "–" in ln or " - " in ln:
                parts = re.split(r"\s*[–\-]\s*", ln, 1)
                deg = parts[0].strip()
                spec = parts[1].strip() if len(parts) > 1 else ""
            out.append(
                {
                    "degree": deg[:120],
                    "specialization": spec[:120],
                    "completed": True,
                    "start_date": "",
                    "end_date": "",
                }
            )
            if len(out) >= 3:
                break
    return out


def _extract_experience_first(text: str) -> List[Dict[str, Any]]:
    out = []
    m = re.search(
        r"(?is)(?:^|\n)\s*(?:experience|work\s+history|employment)\b\s*:?\s*(.+?)(?=(?:^|\n)\s*(?:education|skills|projects|certifications)\b|\Z)",
        text,
    )
    if not m:
        return out
    block = m.group(1).strip()
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    if not lines:
        return out
    company = ""
    title = ""
    # First substantial line often title or Company — Title
    first = lines[0]

    def _looks_company(s: str) -> bool:
        return bool(
            re.search(r"\b(inc|llc|ltd|corp|company|technologies|labs|systems|group)\b", s, re.I)
        )

    def _looks_title(s: str) -> bool:
        return bool(
            re.search(
                r"\b(engineer|developer|manager|lead|architect|analyst|designer|scientist|director|intern|consultant)\b",
                s,
                re.I,
            )
        )

    if "|" in first:
        parts = [p.strip() for p in first.split("|", 1)]
        a, b = parts[0], parts[1] if len(parts) > 1 else ""
        if _looks_company(a) and not _looks_company(b):
            company, title = a, b
        elif _looks_company(b) and not _looks_company(a):
            title, company = a, b
        elif _looks_title(b) and not _looks_title(a):
            company, title = a, b
        else:
            title, company = a, b
    elif " at " in first.lower():
        idx = first.lower().index(" at ")
        title, company = first[:idx].strip(), first[idx + 4 :].strip()
    else:
        title = first[:160]
    desc_bits = lines[1:5] if len(lines) > 1 else []
    out.append(
        {
            "company": company[:160] or "—",
            "title": title[:160],
            "start_date": "",
            "end_date": "",
            "still_working": False,
            "description": " ".join(desc_bits)[:800],
        }
    )
    return out


def extract_profile_hints(text: str) -> Dict[str, Any]:
    """Return dict aligned with User profile JSON keys (partial)."""
    text = text or ""
    if not text.strip():
        return {}

    lines = [ln.strip() for ln in text.replace("\r", "").split("\n") if ln.strip()]

    hints: Dict[str, Any] = {}

    em = _extract_email(text)
    if em:
        hints["email"] = em

    cc, digits = _extract_phone_parts(text)
    if digits:
        if cc:
            hints["phone_country_code"] = cc
        else:
            hints["phone_country_code"] = "+1"
        # display-friendly
        if len(digits) == 10:
            hints["phone"] = f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"
        else:
            hints["phone"] = digits

    name = _candidate_name_lines(lines)
    if name:
        hints["first_name"], hints["last_name"] = name

    hints.update(_extract_address_us(text))

    summ = _extract_summary(text)
    if summ:
        hints["profile_summary"] = summ

    edu = _extract_education_lines(text)
    if edu:
        hints["education"] = edu

    exp = _extract_experience_first(text)
    if exp:
        hints["experience"] = exp

    return hints

"""Profile completion percentage from structured profile dict."""
from typing import Any, Dict, List


def _nonempty(val: Any) -> bool:
    if val is None:
        return False
    if isinstance(val, str):
        return bool(val.strip())
    return bool(val)


def _list_score(items: List, min_filled: int, weight: float) -> float:
    if not items:
        return 0.0
    filled = 0
    for it in items:
        if isinstance(it, dict) and any(_nonempty(v) for v in it.values()):
            filled += 1
        elif _nonempty(it):
            filled += 1
    ratio = min(1.0, filled / max(min_filled, 1))
    return weight * ratio


def compute_profile_completion(profile: Dict[str, Any], has_primary_resume: bool) -> int:
    """
    Weighted 0–100 score. Skills (up to 20) and desired roles (up to 5) contribute when present.
    """
    if not profile:
        profile = {}

    total = 0.0
    max_pts = 100.0

    # Core identity & contact (35)
    total += 5 if _nonempty(profile.get("first_name")) else 0
    total += 5 if _nonempty(profile.get("last_name")) else 0
    total += 5 if _nonempty(profile.get("email")) else 0
    total += 4 if _nonempty(profile.get("phone_country_code")) and _nonempty(profile.get("phone")) else 0
    total += 3 if _nonempty(profile.get("address")) else 0
    total += 4 if _nonempty(profile.get("city")) and _nonempty(profile.get("state")) else 0
    total += 2 if _nonempty(profile.get("zip_code")) else 0
    total += 7 if _nonempty(profile.get("profile_summary")) else 0

    # Demographics (6)
    total += 3 if _nonempty(profile.get("birthdate")) else 0
    total += 3 if _nonempty(profile.get("gender")) else 0

    # Education & experience (28)
    edu = profile.get("education") or []
    if isinstance(edu, list):
        total += _list_score(edu, 1, 12)
    exp = profile.get("experience") or []
    if isinstance(exp, list):
        total += _list_score(exp, 1, 16)

    # Skills & goals (16)
    skills = profile.get("skills") or []
    if isinstance(skills, list) and skills:
        total += min(10, 2 * min(len(skills), 5))
    roles = profile.get("desired_roles") or []
    if isinstance(roles, list) and roles:
        total += min(6, 2 * min(len(roles), 3))

    # Primary resume (15)
    total += 15 if has_primary_resume else 0

    # Normalize if we exceeded 100 due to overlapping weights
    pct = int(round(min(100, (total / max_pts) * 100)))
    return min(100, max(0, pct))

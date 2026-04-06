"""
Company / interview context: optional web snippets via SerpAPI; otherwise curated search links + templates.
"""
import os
import re
from typing import Any, Dict, List

import requests

SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "").strip()


def _serp_query(q: str) -> List[Dict[str, Any]]:
    if not SERPAPI_KEY:
        return []
    try:
        r = requests.get(
            "https://serpapi.com/search.json",
            params={"q": q, "api_key": SERPAPI_KEY, "num": 5},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        out = []
        for it in data.get("organic_results") or []:
            out.append(
                {
                    "title": it.get("title"),
                    "snippet": it.get("snippet"),
                    "link": it.get("link"),
                }
            )
        return out[:5]
    except Exception:
        return []


def build_company_insights(company_guess: str, job_title_hint: str) -> Dict[str, Any]:
    company = (company_guess or "").strip()
    role = (job_title_hint or "").strip()
    parts: List[str] = []

    queries = []
    if company:
        queries.append(f'{company} Glassdoor interview')
        queries.append(f'{company} interview experience site:reddit.com OR site:glassdoor.com')
    if company and role:
        queries.append(f'{company} {role} interview questions')

    snippets: List[Dict[str, Any]] = []
    for q in queries[:2]:
        snippets.extend(_serp_query(q))

    for s in snippets[:4]:
        if s.get("title") and s.get("snippet"):
            parts.append(f"{s['title']}: {s['snippet']}")

    if not parts:
        parts.append(
            "Live Glassdoor and Google review text requires a search API key (set SERPAPI_KEY) or manual research. "
            "Use the links below to read recent interview experiences."
        )

    slug = re.sub(r"[^\w]+", "+", company) if company else ""
    links = []
    if company:
        links.append(
            {
                "label": f"Glassdoor — {company} reviews & interviews",
                "url": f"https://www.google.com/search?q={slug}+Glassdoor+interviews",
            }
        )
        links.append(
            {
                "label": f"Google reviews — {company} interview",
                "url": f"https://www.google.com/search?q={slug}+interview+experience",
            }
        )

    return {
        "company_used": company or None,
        "summary_bullets": parts[:6],
        "source_snippets": snippets[:6],
        "search_links": links,
        "disclaimer": "Summaries are for preparation only and may be incomplete. Verify on official employer and review sites.",
    }

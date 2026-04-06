"""
Optional OpenAI-powered interview prep and resume-builder narrative.
Falls back to structured templates when OPENAI_API_KEY is unset.
"""
import json
import os
import re
from typing import Any, Dict, List

import requests

from analyzer import analyze_detailed, extract_skills_from_text

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def _openai_chat(messages: List[Dict[str, str]], json_mode: bool = False) -> str:
    if not OPENAI_API_KEY:
        return ""
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    body: Dict[str, Any] = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "temperature": 0.4,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=body,
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    return (data["choices"][0]["message"]["content"] or "").strip()


def _infer_seniority(job_description: str, resume: str) -> str:
    text = f"{job_description} {resume}".lower()
    if re.search(r"\b(senior|sr\.|lead|principal|staff|director|manager|8\+\s*years|10\+\s*years)\b", text):
        return "experienced"
    if re.search(r"\b(intern|internship|entry|graduate|0-2\s*years|1\s*year)\b", text):
        return "entry"
    return "mid"


def interview_prep_fallback(job_description: str, resume: str, company: str) -> Dict[str, Any]:
    jd_skills = sorted(extract_skills_from_text(job_description))
    det = analyze_detailed(resume or "", job_description or "")
    seniority = _infer_seniority(job_description, resume)
    behavioral = [
        {
            "question": "Tell me about yourself and why this role fits your background.",
            "answer_framework": "Present 60–90s pitch: current focus, 2 relevant wins with metrics, why this company/role, what you want to learn next.",
            "technique": "Use Present → Past → Future structure; end with a question about team priorities.",
            "reminders": "Stay concise; tie every sentence to value for this role.",
        },
        {
            "question": "Describe a time you faced a tight deadline or conflicting priorities.",
            "answer_framework": "STAR: Situation, Task, Action, Result—with one clear trade-off you managed.",
            "technique": "Emphasize how you communicated and measured success.",
            "reminders": "Pick a real example; quantify impact if possible.",
        },
        {
            "question": "Tell me about a disagreement with a teammate or stakeholder. How did you resolve it?",
            "answer_framework": "Focus on empathy, data, and agreed success criteria—not on blaming.",
            "technique": "End with relationship + outcome (what shipped, what improved).",
            "reminders": "Avoid negativity about people; show ownership.",
        },
        {
            "question": "Describe a mistake you made and what you changed afterward.",
            "answer_framework": "Short context, ownership, fix, prevention/monitoring.",
            "technique": "Shows maturity and learning velocity—valued at every level.",
            "reminders": "Pick a medium mistake, not a catastrophic one.",
        },
        {
            "question": "Why are you interested in our company and this team?",
            "answer_framework": "Connect mission/product to your skills; cite something specific (product, blog, launch).",
            "technique": "Pair admiration with how you will contribute in first 90 days.",
            "reminders": "Research the company site and recent news before the call.",
        },
    ]
    technical = []
    for skill in (jd_skills[:10] or ["the core tools mentioned in the job description"]):
        level_note = "entry-level depth" if seniority == "entry" else "deeper architecture and trade-offs" if seniority == "experienced" else "balanced depth"
        technical.append(
            {
                "question": f"How have you used {skill} in production or projects? What trade-offs did you consider?",
                "sample_answer_points": [
                    f"Clarify context and constraints at {level_note}.",
                    "Walk through design, implementation, testing, and monitoring.",
                    "Close with metrics, lessons learned, and what you'd improve next.",
                ],
                "technique": "Use a short diagram-in-words: inputs → processing → outputs → failure modes.",
                "reminders": "If you haven't used it hands-on, say so and show adjacent experience + learning plan.",
            }
        )
    while len(technical) < 10:
        technical.append(
            {
                "question": "How would you approach debugging a production issue affecting customers?",
                "sample_answer_points": [
                    "Triage severity, communicate status, reproduce, isolate, fix, postmortem.",
                    "Mention logging, metrics, rollbacks, feature flags.",
                ],
                "technique": "Show structured thinking under pressure.",
                "reminders": "Never skip user impact and stakeholder updates.",
            }
        )
        if len(technical) >= 10:
            break

    return {
        "company": company or None,
        "seniority_guess": seniority,
        "behavioral_questions": behavioral[:5],
        "technical_questions": technical[:10],
        "general_interview_tips": [
            "Clarify questions before answering; pause to think.",
            "Quantify outcomes (%, $, time saved, scale).",
            "Prepare 5 stories that map to the job’s top requirements.",
            "Ask interviewers about success metrics and team workflow.",
        ],
        "from_detailed_report": {
            "possible_questions": det.get("possible_questions", [])[:8],
            "skills_to_polish": [x.get("skill") for x in det.get("skills_to_prepare", [])[:8]],
        },
        "ai_generated": False,
    }


def generate_interview_prep(job_description: str, resume: str, company: str) -> Dict[str, Any]:
    if not OPENAI_API_KEY:
        return interview_prep_fallback(job_description, resume, company)

    sys = (
        "You are an interview coach. Return ONLY valid JSON with keys: "
        "behavioral_questions (array of 5 objects: question, answer_framework, technique, reminders), "
        "technical_questions (array of 10 objects: question, sample_answer_points array of strings, technique, reminders), "
        "general_interview_tips (array of strings). "
        "Tailor difficulty to the role: entry vs experienced based on the JD. "
        "Use the job description's skills and responsibilities."
    )
    user = json.dumps(
        {
            "company": company,
            "job_description": job_description[:12000],
            "resume": resume[:12000],
        }
    )
    try:
        raw = _openai_chat(
            [{"role": "system", "content": sys}, {"role": "user", "content": user}],
            json_mode=True,
        )
        data = json.loads(raw)
        data["ai_generated"] = True
        data["company"] = company or None
        return data
    except Exception:
        return interview_prep_fallback(job_description, resume, company)


def resume_builder_ai_fallback(resume: str, job_description: str, keywords: List[str]) -> Dict[str, Any]:
    missing = [k for k in keywords[:20] if k and k.lower() not in (resume or "").lower()]
    bullets = [
        f"Add '{w}' into an achievement bullet if you have real experience (mirror the JD wording)." for w in missing[:8]
    ]
    return {
        "executive_summary": "ATS parsers favor clear section headings, consistent dates, and skills that appear in the job description when truthful.",
        "suggested_bullet_rewrites": bullets,
        "formatting_tips": [
            "Single-column layout, standard fonts (Arial/Calibri 10–11pt).",
            "Use Work Experience → Education → Skills order unless you're a new grad.",
            "Avoid icons and text boxes for critical content.",
        ],
        "ai_generated": False,
    }


def resume_builder_narrative(resume: str, job_description: str, keywords: List[str]) -> Dict[str, Any]:
    if not OPENAI_API_KEY:
        return resume_builder_ai_fallback(resume, job_description, keywords)

    sys = (
        "You help tailor resumes for ATS. Return ONLY JSON: executive_summary (string), "
        "suggested_bullet_rewrites (array of strings), formatting_tips (array of strings). "
        "Never invent employers or degrees; only suggest honest phrasing."
    )
    user = json.dumps(
        {"resume": resume[:10000], "job_description": job_description[:10000], "priority_keywords": keywords[:40]}
    )
    try:
        raw = _openai_chat(
            [{"role": "system", "content": sys}, {"role": "user", "content": user}],
            json_mode=True,
        )
        data = json.loads(raw)
        data["ai_generated"] = True
        return data
    except Exception:
        return resume_builder_ai_fallback(resume, job_description, keywords)

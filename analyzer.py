"""
Resume–Job Compatibility Analyzer
Extracts skills, compares with job requirements, and scores fit.
"""

import re

# Short prep guidance for common skills. Used to generate "Topics to prepare".
TOPIC_GUIDE = {
    "python": ["data structures basics", "OOP", "error handling", "writing clean functions", "common libraries you used"],
    "sql": ["joins", "group by / aggregates", "window functions", "indexes", "query optimization"],
    "rest api": ["HTTP verbs & status codes", "auth (JWT/OAuth basics)", "pagination", "rate limiting", "error handling"],
    "docker": ["images vs containers", "Dockerfile basics", "volumes & networking", "docker compose"],
    "aws": ["S3", "EC2", "IAM basics", "VPC high-level", "CloudWatch"],
    "kubernetes": ["pods/deployments/services", "configmaps/secrets", "ingress basics", "scaling"],
    "git": ["branching", "PR workflow", "merge vs rebase", "resolving conflicts"],
    "ci/cd": ["pipelines basics", "unit tests in CI", "build artifacts", "deployment strategies"],
    "machine learning": ["train/validation split", "overfitting", "metrics", "feature engineering basics"],
    "data analysis": ["EDA", "data cleaning", "visualization", "insights & storytelling"],
    "excel": ["pivot tables", "lookups", "charts", "data cleaning basics"],
    "power bi": ["data modeling", "DAX basics", "dashboards", "refresh & sharing"],
    "tableau": ["charts", "dashboards", "filters/actions", "storytelling"],
    "project management": ["scope", "prioritization", "estimation", "risk management"],
    "agile": ["ceremonies", "user stories", "backlog grooming", "iteration planning"],
    "scrum": ["roles", "sprints", "standups", "retrospectives"],
    "system design": ["requirements → components", "APIs & data models", "scaling basics", "caching", "trade-offs"],
    "communication": ["structured updates", "clarifying questions", "writing concise docs"],
    "leadership": ["ownership", "mentoring", "driving alignment", "decision-making"],
}

# Rough categories to explain "major alignment" at a higher level.
SKILL_CATEGORIES = {
    "Programming": {"python", "javascript", "java", "typescript", "c++", "c#", "go", "golang", "ruby", "php", "swift", "kotlin", "rust", "r"},
    "Web/Backend": {"flask", "django", "fastapi", "spring", "express", "rest api", "api development", "microservices", "graphql"},
    "Data": {"sql", "data analysis", "data science", "statistics", "pandas", "numpy", "excel", "power bi", "tableau"},
    "ML/AI": {"machine learning", "nlp", "computer vision", "tensorflow", "pytorch"},
    "Cloud/DevOps": {"aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd", "devops", "linux", "cloud", "security", "networking"},
    "Product/Design": {"product management", "ui/ux", "figma"},
    "Collaboration": {"communication", "teamwork", "leadership", "problem solving", "stakeholder management", "jira", "confluence", "mentoring", "presentation", "writing"},
}
# Common skills across tech, business, and general roles (lowercase for matching)
COMMON_SKILLS = {
    "python", "javascript", "java", "typescript", "react", "node.js", "sql", "aws",
    "docker", "kubernetes", "git", "rest api", "machine learning", "data analysis",
    "excel", "power bi", "tableau", "project management", "agile", "scrum",
    "communication", "leadership", "problem solving", "teamwork", "analytics",
    "html", "css", "mongodb", "postgresql", "redis", "graphql", "ci/cd",
    "terraform", "linux", "azure", "gcp", "r", "pandas", "numpy", "tensorflow",
    "pytorch", "nlp", "computer vision", "data science", "statistics",
    "figma", "ui/ux", "product management", "jira", "confluence",
    "sales", "marketing", "customer success", "negotiation", "presentation",
    "writing", "research", "budgeting", "stakeholder management", "mentoring",
    "c++", "c#", "go", "golang", "ruby", "php", "swift", "kotlin", "rust",
    "vue", "angular", "django", "flask", "fastapi", "spring", "express",
    "microservices", "api development", "testing", "unit testing", "qa",
    "security", "devops", "cloud", "networking", "system design",
}


def normalize_text(text: str) -> str:
    """Lowercase and normalize whitespace."""
    if not text or not text.strip():
        return ""
    return " ".join(text.lower().split())


def extract_skills_from_text(text: str) -> set:
    """Extract skill-like terms from text using keyword matching and patterns."""
    normalized = normalize_text(text)
    if not normalized:
        return set()

    found = set()

    # 1. Direct match from known skills
    for skill in COMMON_SKILLS:
        # Word boundary style: skill as whole word or with common punctuation
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, normalized):
            found.add(skill)

    # 2. Common multi-word phrases in job descriptions (e.g. "machine learning", "data analysis")
    for skill in COMMON_SKILLS:
        if skill in normalized and skill not in found:
            found.add(skill)

    # 3. Extract capitalized or notable phrases (e.g. "Machine Learning", "REST APIs")
    # Look for 2–4 word sequences that might be skills
    words = re.findall(r"\b[\w+#.]+\b", normalized)
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        if bigram in COMMON_SKILLS:
            found.add(bigram)
        if i < len(words) - 2:
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            if trigram in COMMON_SKILLS:
                found.add(trigram)

    return found


def _top_categories(skills: set) -> list:
    counts = []
    for cat, cat_skills in SKILL_CATEGORIES.items():
        overlap = sorted(skills & cat_skills)
        if overlap:
            counts.append((cat, len(overlap), overlap))
    counts.sort(key=lambda t: (-t[1], t[0]))
    return [{"category": c, "count": n, "skills": s[:8]} for (c, n, s) in counts]


def _build_fit_summary(
    compatibility_score: float,
    n_matched: int,
    n_required: int,
    strong_skills: list,
    skills_to_improve: list,
) -> str:
    top_match = ", ".join(strong_skills[:6]) if strong_skills else "—"
    top_gaps = ", ".join(skills_to_improve[:6]) if skills_to_improve else "—"
    if n_required == 0:
        return "No clear skill keywords were detected in the job description. Try pasting a fuller JD (requirements + responsibilities) for a better match."
    return (
        f"Your resume matches {n_matched} of {n_required} skills mentioned in the job description "
        f"({compatibility_score}%). "
        f"Top overlaps: {top_match}. "
        f"Biggest gaps: {top_gaps}."
    )


def _topics_to_prepare(missing_skills: list, limit: int = 8) -> list:
    topics = []
    for skill in missing_skills[:limit]:
        guide = TOPIC_GUIDE.get(skill)
        if guide:
            topics.append({"skill": skill, "topics": guide})
        else:
            topics.append(
                {
                    "skill": skill,
                    "topics": ["learn core concepts", "build a small project/example", "be ready to explain trade-offs and usage"],
                }
            )
    return topics


def analyze(resume_text: str, job_description: str) -> dict:
    """
    Analyze compatibility between resume and job description.
    Returns: strong_skills, skills_to_improve, compatibility_score, selection_chance, details.
    """
    resume_text = (resume_text or "").strip()
    job_description = (job_description or "").strip()

    resume_skills = extract_skills_from_text(resume_text)
    job_skills = extract_skills_from_text(job_description)

    # Skills you have that the job wants
    strong_skills = sorted(resume_skills & job_skills)
    # Skills the job wants that you didn't show in resume
    skills_to_improve = sorted(job_skills - resume_skills)
    # Skills in resume not in JD (still useful context)
    other_skills = sorted(resume_skills - job_skills)

    # Compatibility: what fraction of required (job) skills you match
    n_required = len(job_skills)
    n_matched = len(strong_skills)
    if n_required == 0:
        compatibility_score = 100
    else:
        compatibility_score = round(100 * n_matched / n_required, 1)

    # Selection chance: heuristic based on match rate and balance
    # Higher match = higher chance; having some "other" skills is a small bonus
    match_factor = n_matched / max(n_required, 1)
    coverage_bonus = min(0.1, len(other_skills) * 0.01)  # slight bonus for extra skills
    raw_chance = min(100, (match_factor * 85) + 5 + (compatibility_score * 0.1) + coverage_bonus * 100)
    selection_chance = round(min(95, max(5, raw_chance)), 1)

    fit_summary = _build_fit_summary(compatibility_score, n_matched, n_required, strong_skills, skills_to_improve)
    alignments = _top_categories(set(strong_skills))
    gaps_by_category = _top_categories(set(skills_to_improve))
    topics = _topics_to_prepare(skills_to_improve)

    return {
        "strong_skills": strong_skills,
        "skills_to_improve": skills_to_improve,
        "other_relevant_skills": other_skills,
        "compatibility_score": compatibility_score,
        "selection_chance": selection_chance,
        "fit_summary": fit_summary,
        "major_alignment": alignments[:3],
        "major_gaps": gaps_by_category[:3],
        "topics_to_prepare": topics,
        "summary": {
            "matched_count": n_matched,
            "required_count": n_required,
            "gap_count": len(skills_to_improve),
        },
    }


# ---- Basic (free) output: short bullets only ----
def analyze_basic(resume_text: str, job_description: str) -> dict:
    """Free plan: short bullet-form output only."""
    full = analyze(resume_text, job_description)
    return {
        "percentage_fit": full["compatibility_score"],
        "chances_of_getting_hired": full["selection_chance"],
        "skills_matched": full["strong_skills"],
        "areas_to_improve": full["skills_to_improve"],
        "you_are_strong_in": full["strong_skills"],
        "areas_to_work_on": full["skills_to_improve"],
        "other_topics_to_consider": full["other_relevant_skills"],
        "summary": full["summary"],
    }


# ---- Detailed (upgraded) output: full report ----
# Template questions by skill for "questions you might get asked"
POSSIBLE_QUESTIONS = {
    "python": ["Describe a project where you used Python.", "How do you handle errors and testing in Python?", "Explain the difference between list and tuple."],
    "sql": ["Describe a complex query you wrote.", "How do you optimize slow queries?", "Explain joins and when you use each type."],
    "javascript": ["How do you manage async code (callbacks, promises)?", "Describe a front-end feature you built.", "Explain event handling and DOM manipulation."],
    "react": ["How do you manage state in React?", "Describe a component you built and why.", "Explain hooks (useState, useEffect)."],
    "aws": ["Describe an AWS service you've used in production.", "How do you secure resources (IAM, VPC)?", "Explain high availability and scaling on AWS."],
    "docker": ["How do you use Docker in your workflow?", "Explain Dockerfile best practices.", "Difference between image and container."],
    "communication": ["Describe a time you had to explain a technical concept to non-technical stakeholders.", "How do you handle conflicting priorities?"],
    "leadership": ["Describe a project you led.", "How do you mentor or support teammates?", "How do you make decisions under ambiguity?"],
    "agile": ["How do you run or participate in sprints?", "Describe how you write or break down user stories.", "How do you handle scope changes?"],
    "machine learning": ["Describe an ML model you built or tuned.", "How do you avoid overfitting?", "Explain your approach to feature engineering."],
    "data analysis": ["Walk through an analysis you did from raw data to insight.", "How do you validate and clean data?", "How do you present findings to stakeholders?"],
    "rest api": ["How do you design REST endpoints?", "How do you handle versioning and errors?", "Describe authentication (e.g. JWT) you've used."],
    "system design": ["How would you design a URL shortener?", "How do you approach scaling a high-traffic system?", "Discuss trade-offs between consistency and availability."],
}

def _possible_questions_for_skills(skills: list, limit: int = 8) -> list:
    out = []
    for s in skills[:limit]:
        qs = POSSIBLE_QUESTIONS.get(s, ["How have you used " + s + " in a project?", "What challenges did you face with " + s + "?"])
        out.extend(qs[:2])
    return out[:15]


def _tips_from_gaps(gaps: list, strong: list, limit: int = 10) -> list:
    tips = []
    for g in gaps[:limit]:
        if g in TOPIC_GUIDE:
            tips.append(f"Add keywords or bullet points related to: {g}. Consider: " + ", ".join(TOPIC_GUIDE[g][:3]))
        else:
            tips.append(f"Include experience or projects that show {g}. Use the term in your resume if relevant.")
    for s in strong[:3]:
        tips.append(f"Keep highlighting {s}; it's a match. Add metrics or outcomes if possible.")
    return tips[:12]


def analyze_detailed(resume_text: str, job_description: str) -> dict:
    """Upgraded plan: detailed report with point-wise analysis, questions, tips."""
    full = analyze(resume_text, job_description)
    strong = full["strong_skills"]
    gaps = full["skills_to_improve"]
    n_req = full["summary"]["required_count"]
    n_mat = full["summary"]["matched_count"]

    point_wise = []
    if n_req > 0:
        point_wise.append(f"Your resume matches {n_mat} of {n_req} required skills ({full['compatibility_score']}%).")
    point_wise.append(f"Selection chance (heuristic): {full['selection_chance']}%.")
    point_wise.append("Strengths: " + (", ".join(strong[:8]) if strong else "None detected from keyword match."))
    point_wise.append("Gaps: " + (", ".join(gaps[:8]) if gaps else "No major gaps detected."))

    gap_scores = []
    for g in gaps[:10]:
        # Simple gap "score": how critical (we don't have importance; use order as proxy)
        gap_scores.append({"skill": g, "score": "High" if g in (gaps[:3]) else "Medium", "description": f"Job requires {g}; add evidence or keywords in resume."})

    deciding = []
    for cat in full.get("major_gaps", [])[:3]:
        deciding.append(f"{cat['category']}: focus on " + ", ".join(cat.get("skills", [])[:4]))
    for cat in full.get("major_alignment", [])[:2]:
        deciding.append(f"Leverage {cat['category']}: " + ", ".join(cat.get("skills", [])[:4]))

    return {
        "match_percentage": full["compatibility_score"],
        "point_wise_analysis": point_wise,
        "strengths": [f"You match on: {s}" for s in strong[:10]] if strong else ["No keyword matches found; consider adding more role-relevant terms."],
        "gaps_with_score": gap_scores,
        "selection_chance": full["selection_chance"],
        "skills_to_prepare": [{"skill": t["skill"], "topics": t["topics"]} for t in full["topics_to_prepare"]],
        "deciding_factors": deciding if deciding else ["Improve keyword overlap with the job description.", "Add concrete outcomes and metrics to your bullets."],
        "possible_questions": _possible_questions_for_skills(list(set(strong + gaps))),
        "tips": _tips_from_gaps(gaps, strong),
        "summary": full["summary"],
    }

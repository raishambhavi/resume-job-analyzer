# Resume × Role Fit

Paste your resume and a job description to see how compatible you are with the role: what you’re strong in, what to work on, and an estimated chance of being shortlisted.

## What it does

- **Compatibility score** – Percentage of job-required skills that appear in your resume.
- **Selection chance** – Heuristic estimate of how likely your resume is to get shortlisted (for guidance only).
- **You’re strong in** – Skills the job asks for that you’ve already highlighted.
- **Consider working on** – Skills the job wants that aren’t clearly reflected in your resume yet.
- **Other relevant skills** – Skills in your resume that weren’t in the job description (bonus context).

## Setup and run

**New to this project?** Use the **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for step-by-step install instructions (Python, terminal commands, and troubleshooting).

**Quick start (once Python is installed):**

1. **Create a virtual environment (recommended)**

   ```bash
   cd resume-job-analyzer
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Start the app**

   ```bash
   python app.py
   ```

4. Open **http://127.0.0.1:5000** in your browser, paste your resume and the job description, then click **Analyze fit**.

## How it works

- The analyzer uses **keyword matching** against a built-in list of common skills (tech, tools, soft skills).
- It extracts skills from both your resume and the job description, then compares them to compute compatibility and the selection-chance estimate.
- Results are meant as a **guide**, not a guarantee. Tailor your resume and prep based on the gaps it suggests.

## Project structure

- `app.py` – Flask server and `/api/analyze` endpoint.
- `analyzer.py` – Skill extraction and compatibility logic.
- `static/` – Frontend: `index.html`, `styles.css`, `script.js`.
- `requirements.txt` – Python dependencies.

## Sharing and showcasing

See **[SHOWCASE.md](SHOWCASE.md)** for where to host your code (e.g. GitHub), where to share the project (LinkedIn, resume, portfolio), and how to deploy a live version (e.g. Render, PythonAnywhere, Railway).

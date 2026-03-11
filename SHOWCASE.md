# Where to share and showcase this project

Use this as a **visibility project** for your portfolio: put the code online and optionally deploy a live version so recruiters and others can try it.

---

## 1. Put your code on GitHub (do this first)

**Why:** Shows your code, commit history, and README. Easy to link from resume, LinkedIn, and portfolio sites.

**Steps:**

1. Create a free account at [github.com](https://github.com) if you don’t have one.
2. Create a **new repository** (e.g. `resume-job-fit` or `resume-role-analyzer`). Choose **Public**. Don’t add a README yet if the project already has one.
3. On your computer, open Terminal in the project folder and run:

   ```bash
   cd "/Users/shambhavirai/Desktop/Cursor Projects/resume-job-analyzer"
   git init
   git add .
   git commit -m "Initial commit: Resume x Role Fit analyzer"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

   Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your GitHub username and repo name.

4. On the repo page, click **Settings → General** and add a **Description** and **Topics** (e.g. `python`, `flask`, `resume`, `portfolio`).

**Link to use:**  
`https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`

---

## 2. Where to share the project (visibility)

Share the **GitHub link** (and the live app link once deployed) in these places:

| Place | What to do |
|-------|------------|
| **LinkedIn** | Post about the project: what it does, why you built it, and link to GitHub (and live app). Add it under **Featured** or in your **Experience / Projects** section. |
| **Resume** | Under “Projects”, add a line like: “Resume–Job Fit Analyzer (Python, Flask) – [GitHub link]” and optionally “[Live demo](link)”. |
| **Portfolio site** | If you have a personal site (e.g. on Notion, GitHub Pages, or a custom domain), add a **Projects** card with title, short description, tech stack, and link to repo + live app. |
| **GitHub profile README** | Add this repo to the “Featured” section of your profile so it appears on your main GitHub page. |
| **Hackathons / dev communities** | Share in Discord/Slack communities, Dev.to, Hashnode, or hackathon galleries if the rules allow. |

---

## 3. Deploy a live version (optional but impressive)

A **live link** lets people use the app without cloning or running code. Good options for a Flask app:

### Option A: Render (good free tier, simple)

1. Go to [render.com](https://render.com) and sign up (GitHub login is fine).
2. **New → Web Service**.
3. Connect your **GitHub repo** (the one with this project).
4. Settings:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app` (you’ll add `gunicorn` to `requirements.txt` for production).
5. Click **Create Web Service**. Render will build and give you a URL like `https://your-app-name.onrender.com`.

**Note:** On the free tier the app may sleep after inactivity; the first visit after that can be slow.

### Option B: PythonAnywhere (free tier, no credit card)

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com).
2. Open a **Bash console**, clone your repo (or upload the project).
3. Create a **virtualenv**, activate it, and run `pip install -r requirements.txt`.
4. In the **Web** tab, create a new **Flask** app, point it to your project folder and `app.py`.
5. Reload the app. Your site will be at `https://YOUR_USERNAME.pythonanywhere.com`.

### Option C: Railway (simple, free tier with limits)

1. Go to [railway.app](https://railway.app) and sign up with GitHub.
2. **New Project → Deploy from GitHub** and select your repo.
3. Railway often detects Python/Flask. If not, set **Start Command** to something like `gunicorn app:app` and add `gunicorn` to `requirements.txt`.
4. In **Settings**, add a **Public URL**. Use that link to share your app.

---

## 4. Make the app deployment-ready (for Render / Railway)

Add **gunicorn** so the app runs correctly in production:

1. In `requirements.txt`, add a new line:
   ```text
   gunicorn==21.2.0
   ```
2. Use **Start command**: `gunicorn app:app` (or `gunicorn -w 1 -b 0.0.0.0:$PORT app:app` if the host gives you a `PORT` variable).

After that, your **visibility set** is:

- **Code:** GitHub repo  
- **Live app:** Render / PythonAnywhere / Railway URL  
- **Story:** LinkedIn post + resume + portfolio + GitHub profile  

Use the same links everywhere so recruiters and others can both see your code and try the app.

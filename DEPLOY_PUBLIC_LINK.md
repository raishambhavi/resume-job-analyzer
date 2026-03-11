# How to share your app with a public link (so anyone can open and use it)

Right now the app runs only on your computer. To get a **link you can share** (e.g. with recruiters or friends) so they can open it in their browser and use the app, you need to **deploy** it to a free hosting service.

Below is the **easiest option (Render)** in simple steps. Your code must already be on **GitHub** (see GITHUB_AND_RESUME_GUIDE.md if not).

---

## Option 1: Render (recommended – free, simple)

### Step 1: Create a Render account
1. Go to **https://render.com** in your browser.
2. Click **“Get Started for Free”**.
3. Sign up with **GitHub** (so Render can access your repo). Click **“Sign up with GitHub”** and approve access.

### Step 2: Create a new Web Service
1. After logging in, click **“New +”** (top right).
2. Click **“Web Service”**.

### Step 3: Connect your GitHub repo
1. Under **“Connect a repository”**, find **resume-job-analyzer** (or whatever you named it).
2. If you don’t see it, click **“Configure account”** and give Render access to the repo.
3. Click **“Connect”** next to **resume-job-analyzer**.

### Step 4: Set build and start settings
1. **Name:** Keep as is or type something like `resume-role-fit`.
2. **Region:** Choose one close to you (e.g. Oregon).
3. **Branch:** `main` (default).
4. **Runtime:** **Python 3** (Render uses `.python-version` or env var `PYTHON_VERSION` – this repo has `.python-version` set to 3.12.7).
5. **Build Command:**  
   Type exactly:  
   `pip install -r requirements.txt`
6. **Start Command:**  
   Type exactly:  
   `gunicorn -w 1 -b 0.0.0.0:$PORT app:app`
7. **Instance type:** Leave as **Free**.

### Step 5: Deploy (no database or env vars needed)
This app has **no login, no signup, and no payments**. You do **not** need to add a database or any environment variables.

1. Click **“Create Web Service”**.
2. Wait until the status is **“Live”** (green). Your public link is at the top, e.g. **https://resume-role-fit-xxxx.onrender.com**.

### Step 6: Share the link
- Copy that URL (e.g. `https://resume-role-fit-xxxx.onrender.com`).
- Share it with anyone. They can use **Simple analysis** and **Detailed analysis** and **download the detailed report** – no account required.

**Notes:**
- On the **free** plan, the app may “sleep” after 15 minutes of no use. The first open after that can take 30–60 seconds to wake up; then it works normally.
- You can put this **same link on your resume** (e.g. “Live demo: https://...”) so recruiters can try the app without downloading anything.

---

## How to update the app on GitHub and Render

After you change code locally, do this to update both GitHub and your live app.

### 1. Update on GitHub (push your latest code)

In Terminal, from your project folder:

```bash
cd "/Users/shambhavirai/Desktop/Cursor Projects/resume-job-analyzer"
git status
git add .
git commit -m "Describe your changes (e.g. Add download for detailed analysis)"
git push origin main
```

- If your default branch is `master` instead of `main`, use: `git push origin master`.
- If you haven’t set a remote yet: `git remote add origin https://github.com/YOUR_USERNAME/resume-job-analyzer.git` then push.

### 2. Update on Render (redeploy so the live site uses the new code)

Render can **auto-deploy** when you push to GitHub (if you left that enabled). If not, or to force a fresh deploy:

1. Go to **https://dashboard.render.com** and log in.
2. Click your **Web Service** (resume-job-analyzer / resume-role-fit).
3. Click **“Manual Deploy”** (top right) → **“Deploy latest commit”**.
4. Wait until the status is **“Live”** (green). Your public URL stays the same; it now serves the updated app.

**Summary:** Push to GitHub → Render picks up the new commit (or you trigger Manual Deploy) → live site is updated.

---

## Option 2: Railway (alternative, also free tier)

1. Go to **https://railway.app** and sign up with GitHub.
2. Click **“New Project”** → **“Deploy from GitHub repo”**.
3. Select **resume-job-analyzer**.
4. After it’s created, open the project → **Settings** → **Networking** → **Generate Domain**.
5. Set the **start command** to: `gunicorn -w 1 -b 0.0.0.0:$PORT app:app` (in Settings or in a **Procfile**).
6. Your public link will be like **https://something.up.railway.app**.

---

## Summary

| Step | What you do |
|------|-------------|
| 1 | Put your project on GitHub (if not already). |
| 2 | Sign up at Render with GitHub. |
| 3 | Create a **Web Service**, connect your repo, set **Build** and **Start** as above. |
| 4 | Click **Create Web Service** – no database or env vars needed. |
| 5 | Copy the **public URL** and share it. |

**To update later:** Push changes to GitHub, then on Render click **Manual Deploy** → **Deploy latest commit** (or rely on auto-deploy).

---

## Troubleshooting: “Not Found” when opening the link

### 1. Use the full URL with **https://**
Open **https://your-app-name.onrender.com** (replace with your actual Render URL). Do **not** use `http://` or omit `https://`.

### 2. Check that your GitHub repo has the **entire** project
The repo must include the **`static`** folder with:
- `static/index.html`
- `static/styles.css`
- `static/script.js`

If the `static` folder is missing, the app will deploy but the main page will not load. Add it to the repo, push to GitHub, then on Render: **Manual Deploy** → **Deploy latest commit**.

### 3. See if the backend is running
Open **https://your-app-name.onrender.com/api/health** in your browser.

- If you see **`{"ok":true}`** → the app is running; the problem is likely the main page or missing `static` files. Push the latest code and redeploy.
- If you get **Not Found** here too → check **Logs** on Render (your service → **Logs** tab) for errors.

### 4. Redeploy after code changes
Push the latest code to GitHub. On Render, click **Manual Deploy** → **Deploy latest commit**. Wait until status is **Live**, then try the main link again with **https://**.

### 5. Check Render dashboard
1. Open your service on **dashboard.render.com**.
2. **Logs** tab: Look for errors (e.g. “ModuleNotFoundError”, “No such file”).
3. **Settings**: **Start Command** must be exactly: `gunicorn -w 1 -b 0.0.0.0:$PORT app:app`.
4. **Build Command** should be: `pip install -r requirements.txt`.
5. Save, then **Manual Deploy** → **Deploy latest commit** again.

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
4. **Runtime:** **Python 3**.
5. **Build Command:**  
   Type exactly:  
   `pip install -r requirements.txt`
6. **Start Command:**  
   Type exactly:  
   `gunicorn -w 1 -b 0.0.0.0:$PORT app:app`
7. **Instance type:** Leave as **Free**.

### Step 5: Deploy
1. Click **“Create Web Service”**.
2. Render will build and deploy. Wait a few minutes until you see **“Live”** (green) at the top.
3. At the top you’ll see a URL like: **https://resume-role-fit-xxxx.onrender.com**. That is your **public link**.

### Step 6: Share the link
- Copy that URL (e.g. `https://resume-role-fit-xxxx.onrender.com`).
- Share it with anyone. When they open it, they’ll see and use your app (paste resume, job description, Analyze fit).

**Notes:**
- On the **free** plan, the app may “sleep” after 15 minutes of no use. The first open after that can take 30–60 seconds to wake up; then it works normally.
- You can put this **same link on your resume** (e.g. “Live demo: https://...”) so recruiters can try the app without downloading anything.

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
| 2 | Sign up at Render (or Railway) with GitHub. |
| 3 | Create a **Web Service** and connect your **resume-job-analyzer** repo. |
| 4 | Set **Build:** `pip install -r requirements.txt` and **Start:** `gunicorn -w 1 -b 0.0.0.0:$PORT app:app`. |
| 5 | Deploy and copy the **public URL** (e.g. `https://resume-role-fit-xxxx.onrender.com`). |
| 6 | Share that URL; anyone can open it and use the app. |

After this, you’ll have **two** links to share:
- **GitHub link** – for code (resume, portfolio).
- **Live app link** – for using the app in the browser (resume “Live demo”, recruiters, friends).

---

## Troubleshooting: “Not Found” when opening the link

If you see **“Not Found”** or **“The requested URL was not found on the server”** when opening your Render link, try the following.

### 1. Use the full URL with **https://**
Open:
**https://resume-job-analyzer.onrender.com**  
(Replace with your actual Render URL.)  
Do **not** use `http://` or omit `https://`.

### 2. Check that your GitHub repo has the **entire** project
The repo must include the **`static`** folder with these files inside it:
- `static/index.html`
- `static/styles.css`
- `static/script.js`

If you uploaded the project manually and forgot the `static` folder, the app will deploy but the main page will not load (Not Found).

**Fix:** On your Mac, add the `static` folder to the repo and push to GitHub (or re-upload the project including `static`). Then on Render, trigger a new deploy (Render → your service → **Manual Deploy** → **Deploy latest commit**).

### 3. See if the backend is running
Open this URL in your browser (use your real Render URL):
**https://resume-job-analyzer.onrender.com/api/health**

- If you see **`{"ok":true}`** → the app is running; the problem is likely the main page or missing `static` files. Do step 2 and redeploy.
- If you also get **Not Found** here → the app may not have started. Check **Logs** on Render (your service → **Logs** tab) for error messages.

### 4. Redeploy after code changes
Push the latest code to GitHub (including `app.py`, `Procfile`, `runtime.txt`, and the full `static` folder). On Render, click **Manual Deploy** → **Deploy latest commit**. Wait until the status is **Live**, then try the main link again (with **https://**).

### 5. If the app still shows “Not Found” – find out where it fails
**A) Test the backend:**  
Open this URL (use your real Render URL):  
**https://resume-job-analyzer.onrender.com/api/health**

- If you see **`{"ok":true}`** → The app is running. The problem is only the main page. Push the latest code (with the updated `app.py` and `Procfile`), redeploy, and try the main link again.
- If you get **Not Found** or an error here too → The app is not running correctly. Go to step B.

**B) Check Render dashboard:**  
1. Open your service on **dashboard.render.com**.  
2. **Logs** tab: Look for red error lines (e.g. “ModuleNotFoundError”, “No such file”, “Address already in use”).  
3. **Settings** (or **Environment**) tab: **Start Command** must be exactly:  
   `gunicorn -w 1 -b 0.0.0.0:$PORT app:app`  
   (If you added a **Procfile** with `web: gunicorn -w 1 -b 0.0.0.0:$PORT app:app`, you can leave Start Command **blank** and Render will use the Procfile.)  
4. **Build Command** should be: `pip install -r requirements.txt`.  
5. Save, then do **Manual Deploy** → **Deploy latest commit** again.

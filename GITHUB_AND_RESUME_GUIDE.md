# Step-by-step: Put your project on GitHub and add it to your resume

This guide is for someone new to GitHub. Follow the steps in order.

---

## Important: Two different links (why the GitHub link doesn’t “run” the app)

| Link | What it is | What happens when you open it |
|------|------------|-------------------------------|
| **GitHub repo link**<br>e.g. `https://github.com/YourUsername/resume-job-analyzer` | Where your **code** is stored. This is the link you put on your **resume**. | You see the project page: code, README, files. The app does **not** run here. GitHub only shows the project; it does not run Python/Flask apps. So it is **normal** that the app doesn’t run when you open this link. |
| **Local app link**<br>`http://127.0.0.1:5050` | Where the app runs **on your own computer** when you start it (e.g. `./venv/bin/python app.py`). | The actual app UI (paste resume, job description, Analyze fit). This works **only on your Mac** while the server is running. Recruiters cannot open this link; it’s your machine only. |

**Summary:**

- **GitHub link** = for your resume. Recruiters open it to **see your code and README**. They can download the project and run it on their machine if they want. The app is **not** supposed to run in the browser when you open the GitHub link.
- **127.0.0.1:5050** = the app **running on your computer**. You use this when you’re testing; recruiters don’t use this link.

**If you want a link that recruiters can open and actually use the app in the browser** (like a live demo), you need to **deploy** the app to a hosting service (e.g. Render, Railway). That gives you a public URL like `https://your-app-name.onrender.com`. See **SHOWCASE.md** in this project for short deployment steps. Deployment is optional; many recruiters are happy with just the GitHub link.

---

## Part 1: Create a GitHub account

### Step 1.1: Go to GitHub
1. Open your web browser (Chrome, Safari, etc.).
2. In the address bar, type: **github.com** and press Enter.

### Step 1.2: Sign up
1. On the GitHub homepage, click the green **“Sign up”** button (top right).
2. Enter your **email address**.
3. Create a **password** (use something strong; GitHub will tell you if it’s too weak).
4. Choose a **username**. This will appear in your profile and in your project links (e.g. `github.com/YourUsername`). Use something professional if you plan to share with recruiters (e.g. your name or a clean handle).
5. Type **“y”** or **“n”** for the product updates question (your choice).
6. Click **“Create account”**.

### Step 1.3: Verify your email
1. GitHub will send a **code** to your email.
2. Check your inbox (and spam folder), get the code.
3. Enter the code on GitHub and finish verification.

### Step 1.4: Complete the short survey (optional)
GitHub may ask a few questions (e.g. “What brings you here?”). You can skip or answer briefly, then click **“Continue”** or **“Skip”**.

You now have a **GitHub account**. Your profile URL will look like: **https://github.com/YourUsername**.

---

## Part 2: Create a new repository (a “folder” for your project on GitHub)

A **repository** (or “repo”) is where your code will live on GitHub. One project = one repo.

### Step 2.1: Start creating a repo
1. Make sure you are **logged in** to GitHub.
2. In the top-right corner, click the **“+”** icon.
3. Click **“New repository”**.

### Step 2.2: Fill in the details
1. **Repository name:** Type something short and clear, e.g. **resume-job-analyzer** or **resume-role-fit**. (No spaces; use a hyphen if you want.)
2. **Description (optional):** e.g. “Resume and job description fit analyzer – see how you match a role.”
3. **Public:** Select **Public** so recruiters can see it without logging in.
4. **Do NOT** check “Add a README file” (your project already has files; we’ll upload them).
5. Leave the rest as default.
6. Click the green **“Create repository”** button.

### Step 2.3: Note your repo link
After the repo is created, you’ll see a page with a URL like:
**https://github.com/YourUsername/resume-job-analyzer**

This is the **link you will put on your resume**. Copy it and save it somewhere (e.g. a Notes app).

---

## Part 3: Upload your project code to this repository

You have two options. **Option A** is easier if you have never used the terminal. **Option B** uses the terminal (same place where you ran `./venv/bin/python app.py`).

---

### Option A: Upload using the GitHub website (no terminal)

#### Step 3.A.1: Open the upload page
1. On your new repository page (the one you just created), you should see something like “Quick setup” or “…or push an existing repository from the command line.”
2. Look for a link that says **“uploading an existing file”** or **“upload files”** and click it.  
   (If you don’t see it, click **“Add file”** → **“Upload files”**.)

#### Step 3.A.2: Prepare your project folder on your Mac
1. On your Mac, open **Finder**.
2. Go to: **Desktop → Cursor Projects → resume-job-analyzer**.
3. **Do not upload the `venv` folder** (it’s large and not needed on GitHub).  
   So we’ll upload everything **except** `venv`:
   - Select these items (hold **Command** and click each): **app.py**, **analyzer.py**, **requirements.txt**, **run.sh**, the **static** folder, and all **.md** files (README.md, SETUP_GUIDE.md, SHOWCASE.md, GITHUB_AND_RESUME_GUIDE.md, etc.).
   - Or select everything, then **hold Option** and drag to copy them to a **new** folder on your Desktop called **resume-job-analyzer-upload** (so you don’t include `venv`). Then open that new folder.

#### Step 3.A.3: Drag and drop onto GitHub
1. In that folder, select **all** the files and folders (but not `venv`).
2. Drag them into the GitHub browser window where it says **“Drag files here”** or **“upload files”**.
3. Wait until every file shows as uploaded.
4. At the bottom, in the **“Commit message”** box, type: **First upload of resume-job-analyzer**.
5. Click the green **“Commit changes”** (or **“Commit to main”**) button.

Your code is now on GitHub. The link **https://github.com/YourUsername/resume-job-analyzer** (use your real username and repo name) is what you put on your resume.

---

### Option B: Upload using Terminal (Git commands)

Use this only if you are comfortable with the same Terminal where you ran the app.

#### Step 3.B.1: Install Git (if needed)
1. Open **Terminal**.
2. Run: `git --version`
3. If you see a version number (e.g. `git version 2.39.0`), Git is installed. If the computer says “command not found,” install Git from: https://git-scm.com/download/mac

#### Step 3.B.2: Go to your project folder
```bash
cd "/Users/shambhavirai/Desktop/Cursor Projects/resume-job-analyzer"
```

#### Step 3.B.3: Ignore the `venv` folder (so we don’t upload it)
1. Check if a file named **.gitignore** exists in the project folder.
2. If it does not exist, create it: in Terminal you can run:
   ```bash
   echo "venv/" >> .gitignore
   echo "__pycache__/" >> .gitignore
   echo "*.pyc" >> .gitignore
   ```
   This tells GitHub to ignore `venv` and cache files.

#### Step 3.B.4: Turn the folder into a Git repo and add files
Run these one after the other (replace **YourUsername** and **resume-job-analyzer** with your real GitHub username and repo name):

```bash
git init
git add .
git commit -m "First upload: Resume x Role Fit analyzer"
git branch -M main
git remote add origin https://github.com/YourUsername/resume-job-analyzer.git
git push -u origin main
```

5. When you run `git push`, GitHub may ask for your **username** and **password**.  
   - **Password:** GitHub no longer accepts your normal account password here. You must use a **Personal Access Token (PAT)**.
   - To create one: GitHub → **Settings** (your profile menu) → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token**. Give it a name, choose “repo” scope, generate, then **copy the token** and paste it when the terminal asks for “Password.”

After this, your code is on GitHub. The link is: **https://github.com/YourUsername/resume-job-analyzer**.

---

## Part 4: Make the repo look good for recruiters

### Step 4.1: Add a short description
1. On your repository page, click the **gear icon** next to “About” (right side).
2. In **Description**, type something like: **Resume–job fit analyzer (Python, Flask). Paste resume + JD → compatibility score, skills match, topics to prepare.**
3. Optionally add **Topics** (tags), e.g. **python**, **flask**, **resume**, **portfolio**.
4. Click **Save changes**.

### Step 4.2: Check the README
Your project already has a **README.md**. It will show on the main page of the repo. If you added a description and topics, recruiters will see a clear, professional repo.

---

## Part 5: What link to use on your resume

- **Use this link:**  
  **https://github.com/YourUsername/resume-job-analyzer**  
  (Replace **YourUsername** and **resume-job-analyzer** with your real username and repo name.)

- **Where to put it:**  
  In the **Projects** (or **Experience**) section of your resume, add a line like:
  - **Resume × Role Fit Analyzer** – Python, Flask. Analyzes resume vs job description; compatibility score, skills gap, topics to prepare.  
    **Link:** https://github.com/YourUsername/resume-job-analyzer

- **What recruiters see:**  
  When they open the link, they see your code, README, and (if you added them) description and topics. They can **run it on their own machine** by following the README (or SETUP_GUIDE.md).

---

## Part 6: “Run whenever I want” – two meanings

1. **Run on your own computer whenever you want**  
   You already do this: open Terminal, go to the project folder, run `./venv/bin/python app.py`, then open http://127.0.0.1:5050. Your code is also on GitHub, so you (or anyone) can download it and run it the same way.

2. **Give recruiters a “live” link where they can use the app in the browser**  
   That means **deploying** the app (e.g. Render, Railway, PythonAnywhere). Your project’s **SHOWCASE.md** has short instructions for that. It’s optional; many recruiters are happy to see the GitHub link and README.

---

## Quick checklist

- [ ] GitHub account created.
- [ ] New **public** repository created (e.g. `resume-job-analyzer`).
- [ ] Project code uploaded (Option A: website upload without `venv`; Option B: Git from Terminal with `.gitignore`).
- [ ] Repo description and topics added.
- [ ] Resume link saved and added to resume: **https://github.com/YourUsername/resume-job-analyzer**.

If you get stuck on a step, note which step number and what you see on the screen, and you can ask for help with that exact step.

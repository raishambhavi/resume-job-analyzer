# Step-by-step: Replace old files on GitHub with new app and deploy on Render

Follow these steps **in order** in your Terminal. Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username.

---

## Part 1: Make sure your local project is the “new” app

Your folder should already have the simplified app (no login/signup/payments, with download). These files were just removed so they don’t get pushed again:

- `static/login.html` (deleted)
- `static/signup.html` (deleted)
- `models.py` (deleted)

If you made any other edits in Cursor, save all files before continuing.

---

## Part 2: Open Terminal and go to the project

```bash
cd "/Users/shambhavirai/Desktop/Cursor Projects/resume-job-analyzer"
```

---

## Part 3: Check Git remote

See what remote is set:

```bash
git remote -v
```

- If you see nothing, add your GitHub repo (use your real repo URL):

  ```bash
  git remote add origin https://github.com/YOUR_GITHUB_USERNAME/resume-job-analyzer.git
  ```

- If `origin` points to the wrong URL, fix it:

  ```bash
  git remote set-url origin https://github.com/YOUR_GITHUB_USERNAME/resume-job-analyzer.git
  ```

---

## Part 4: Stage everything (including deletions)

```bash
git add -A
```

This stages new files, changed files, and **deleted** files (like login.html, signup.html, models.py).

---

## Part 5: Commit

```bash
git commit -m "Simplified app: no login/signup/payments, download detailed report; remove old auth files"
```

If Git says “nothing to commit, working tree clean”, your last commit already had all changes. You can skip to Part 6.

---

## Part 6: Push to GitHub (replace GitHub with your local version)

**Option A – You’re okay replacing GitHub’s history with your local one (recommended if the repo is only yours):**

```bash
git push -u origin main --force
```

If your default branch on GitHub is `master`:

```bash
git push -u origin main --force
git push -u origin master --force
```

Use the one that matches your GitHub branch. This makes GitHub match your laptop exactly (old files removed, new code in place).

**Option B – You want to keep GitHub history and only add a new commit:**

```bash
git pull origin main --rebase
git push -u origin main
```

(Use `master` instead of `main` if that’s your branch name.) If there are conflicts, Git will tell you; resolve them, then `git add .` and `git rebase --continue`, then push again.

---

## Part 7: Confirm on GitHub

1. Open **https://github.com/YOUR_GITHUB_USERNAME/resume-job-analyzer** in your browser.
2. Check that:
   - `static/login.html` and `static/signup.html` are **gone**.
   - `models.py` is **gone**.
   - `app.py`, `static/index.html`, `static/script.js`, `requirements.txt` are there and updated.

---

## Part 8: Deploy (or redeploy) on Render

1. Go to **https://dashboard.render.com** and log in.
2. Click your **Web Service** (e.g. resume-job-analyzer or resume-role-fit).
3. Click **“Manual Deploy”** (top right) → **“Deploy latest commit”**.
4. Wait until the status is **“Live”** (green).

Your public URL stays the same; it will now serve the simplified app (Simple analysis, Detailed analysis, Download detailed report, no login).

---

## Quick checklist

| Step | Action |
|------|--------|
| 1 | `cd` to project folder |
| 2 | `git remote -v` (add or fix `origin` if needed) |
| 3 | `git add -A` |
| 4 | `git commit -m "..."` |
| 5 | `git push -u origin main --force` (or `master`) |
| 6 | Check GitHub in browser |
| 7 | Render → Manual Deploy → Deploy latest commit |

---

## If something goes wrong

- **“Permission denied” or “could not read from remote”**  
  Check the remote URL: `git remote -v`. Fix with `git remote set-url origin https://github.com/USERNAME/REPO.git`. Use HTTPS; if you use SSH, use the `git@github.com:...` URL.

- **“Updates were rejected”**  
  You’re not using `--force`. If you’re sure you want GitHub to match your laptop, use `git push -u origin main --force` (or `master`).

- **Render still shows the old app**  
  Make sure you clicked **Manual Deploy** → **Deploy latest commit** and waited until **Live**. Check the **Logs** tab on Render for errors.

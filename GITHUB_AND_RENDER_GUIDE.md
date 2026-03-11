# Complete guide: Push your app to GitHub and deploy on Render

Follow these steps **in order**. Do not skip steps.

---

## Part 1: Fix your GitHub remote URL

1. Open **Terminal** (Applications → Utilities → Terminal, or search "Terminal").

2. Go to your project folder:
   ```bash
   cd "/Users/shambhavirai/Desktop/Cursor Projects/resume-job-analyzer"
   ```

3. See what remote URL Git is using:
   ```bash
   git remote -v
   ```
   You might see something like `https://github.com/YOUR_USERNAME/resume-job-analyzer.git`.

4. **Replace the placeholder with your real GitHub username.**  
   Example: if your GitHub username is **ShambhaviRai**, run:
   ```bash
   git remote set-url origin https://github.com/ShambhaviRai/resume-job-analyzer.git
   ```
   Use **your own** GitHub username instead of ShambhaviRai.

5. Check that it’s correct:
   ```bash
   git remote -v
   ```
   Both lines should show the same URL with **your** username.

---

## Part 2: Create a Personal Access Token (GitHub does not accept passwords)

1. In your browser, go to **https://github.com** and log in.

2. Click your **profile picture** (top right) → **Settings**.

3. In the left sidebar, scroll down and click **Developer settings**.

4. Click **Personal access tokens** → **Tokens (classic)**.

5. Click **Generate new token** → **Generate new token (classic)**.

6. Fill in:
   - **Note:** e.g. `Mac Terminal Git`
   - **Expiration:** e.g. 90 days or No expiration (your choice)
   - Under **Scopes**, tick **repo** (this gives access to your repositories).

7. Click **Generate token** at the bottom.

8. **Copy the token immediately** (it looks like `ghp_xxxxxxxxxxxx`).  
   You will **not** see it again. Paste it into a Notes app or password manager for now.

9. You can close the GitHub tab when done.

---

## Part 3: Push your code to GitHub

1. In Terminal, make sure you’re in the project folder:
   ```bash
   cd "/Users/shambhavirai/Desktop/Cursor Projects/resume-job-analyzer"
   ```

2. Stage all changes (new, changed, and deleted files):
   ```bash
   git add -A
   ```

3. Commit:
   ```bash
   git commit -m "Simplified app: no login or payments, add download detailed report"
   ```
   If it says **“nothing to commit, working tree clean”**, that’s fine — your last commit already had everything. Go to step 4.

4. Push to GitHub:
   ```bash
   git push -u origin main
   ```
   If your GitHub repo uses **master** instead of **main**, use:
   ```bash
   git push -u origin master
   ```

5. When Git asks for credentials:
   - **Username for 'https://github.com':** type your **GitHub username** (e.g. ShambhaviRai) and press Enter.
   - **Password for 'https://github.com':** **paste your Personal Access Token** (the one you copied in Part 2). Do **not** type your GitHub account password. Press Enter.

6. If it succeeds, you’ll see something like `Branch 'main' set up to track remote branch 'main' from 'origin'.`

7. **Check on GitHub:** Open **https://github.com/YOUR_USERNAME/resume-job-analyzer** in your browser (use your username). You should see your latest files there.

---

## Part 4: Deploy (or update) on Render

1. Go to **https://dashboard.render.com** in your browser and log in.

2. On the dashboard, click your **Web Service** (e.g. **resume-job-analyzer** or **resume-role-fit**).

3. At the top right, click **Manual Deploy** → **Deploy latest commit**.

4. Wait until the status at the top turns **Live** (green). This can take 1–3 minutes.

5. Click your service’s **URL** (e.g. `https://resume-job-analyzer-xxxx.onrender.com`) to open the app. You should see the simplified app: Simple analysis, Detailed analysis, and Download detailed analysis — no login.

---

## Quick reference

| Part | What you do |
|------|-------------|
| 1 | Set correct remote URL: `git remote set-url origin https://github.com/YOUR_USERNAME/resume-job-analyzer.git` |
| 2 | On GitHub: Settings → Developer settings → Personal access tokens → Generate token (classic), tick **repo**, copy the token |
| 3 | Terminal: `git add -A` → `git commit -m "..."` → `git push -u origin main` (use **token** as password when asked) |
| 4 | Render dashboard → your Web Service → Manual Deploy → Deploy latest commit → wait for Live |

---

## If something goes wrong

**“Authentication failed” or “Invalid username or token”**  
- You must use the **Personal Access Token** as the password, not your GitHub account password.  
- Make sure the remote URL has your **real** username, not `YOUR_USERNAME`.

**“Repository not found”**  
- Check the URL: `git remote -v`. Fix with `git remote set-url origin https://github.com/YOUR_USERNAME/resume-job-analyzer.git`.  
- Ensure the repo **resume-job-analyzer** exists on your GitHub account (create it at https://github.com/new if needed).

**“pathspec 'folder-name/' did not match any files”**  
- That command was only an example. You don’t need to remove “folder-name”. For this guide, just run `git add -A` and `git commit` and `git push` as in Part 3.

**Render still shows the old app**  
- Wait until the deploy status is **Live**.  
- Try opening the app URL in an incognito/private window to avoid cache.

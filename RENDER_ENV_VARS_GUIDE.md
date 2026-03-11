# How to set environment variables on Render (step-by-step)

**Note:** The current app (no login, no payments) **does not require any environment variables**. You can deploy and use it without adding env vars. This guide is kept for reference if you later add a database or other features that need env vars.

---

This guide walks you through **exactly** where to click and what to type so your app can use the database and sessions (login/signup) on Render.

---

## Part A: Open the Environment tab

1. Go to **https://dashboard.render.com** and log in.
2. You should see a list of your services (e.g. **resume-role-fit** or **resume-job-analyzer**).  
   - If you don’t see any services, create a **Web Service** first (connect your GitHub repo and deploy once), then come back.
3. **Click the name** of your Web Service (the resume app).  
   - This opens that service’s page.
4. On the left sidebar, click **“Environment”**.  
   - If you don’t see a sidebar, look for a tab or link named **Environment** at the top (e.g. **Environment**, **Settings**, **Logs**, **Shell**).
5. You should now see a section titled **Environment Variables** (or **Env**).  
   - There may be a table with **Key** and **Value** columns, or an **“Add Environment Variable”** / **“Add Variable”** button.

You are now in the right place to add the variables below.

---

## Part B: Add the three required variables

Add these **one by one**. For each variable, use the **“Add Environment Variable”** (or **“Add Variable”**) button if you see it; otherwise look for **Key** and **Value** fields to fill.

---

### 1. DATABASE_URL (database connection string)

You need a **PostgreSQL** database on Render first.

**If you don’t have a database yet:**

1. In the Render dashboard, click the **“New +”** button (top right).
2. Click **“PostgreSQL”**.
3. Fill in:
   - **Name:** e.g. `resume-analyzer-db`
   - **Region:** choose the **same region** as your Web Service (e.g. Oregon).
   - **Plan:** **Free**.
4. Click **“Create Database”**.
5. Wait until the status shows **“Available”** (green). This can take 1–2 minutes.
6. Click the **name** of this new database to open it.
7. On the database page, find the **“Connect”** or **“Info”** section.
8. Look for **“Internal Database URL”** (not “External”).  
   - It looks like: `postgres://user:password@hostname/database_name`
   - **Internal** is used when the app and database are on Render; **External** is for your own computer.
9. Click **“Copy”** next to the Internal Database URL (or select the whole string and copy it).

**Add it to your Web Service:**

1. Go back to your **Web Service** (click its name in the dashboard).
2. Open **Environment** (left sidebar or top tab).
3. Add a new variable:
   - **Key:** type exactly: `DATABASE_URL`
   - **Value:** paste the Internal Database URL you copied (the long string starting with `postgres://`).
4. Save.  
   - There may be a **“Save Changes”** button at the bottom, or each row may save automatically.

**Alternative (if Render shows “Add from Render”):**

- Some Render layouts have an option like **“Add from Render”** or **“Link existing resource”**.
- Click it and choose your **PostgreSQL** database.  
- Render may auto-add a variable like `DATABASE_URL` with the correct value. If so, you don’t need to copy the URL manually.

---

### 2. SECRET_KEY (random string for sessions)

The app needs a long, random string so login/signup sessions are secure.

**Option A – Using your Mac Terminal (recommended):**

1. On your Mac, open **Terminal** (Applications → Utilities → Terminal, or search “Terminal”).
2. Run this command exactly (you can copy and paste):

   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

3. Press **Enter**.  
   - You’ll see one long line of random letters and numbers (e.g. `a1b2c3d4e5f6...`). That is your **SECRET_KEY**.
4. **Copy** that entire line (select it and Cmd+C).

**Option B – If you don’t have Python or Terminal:**

- Use any long random string (at least 32 characters).  
  Examples of ways to get one:
  - Use a password generator (e.g. 1Password, LastPass “generate password”, 32+ characters).
  - Or type a long random mix of letters and numbers yourself (e.g. 40+ characters).

**Add it to Render:**

1. In your Web Service → **Environment**, add another variable:
   - **Key:** exactly: `SECRET_KEY`
   - **Value:** paste the long random string you generated (no spaces at the start or end).
2. Save.

---

### 3. SESSION_COOKIE_SECURE (for HTTPS)

This tells the app to send cookies only over HTTPS, which Render uses.

1. In the same **Environment** section, add one more variable:
   - **Key:** exactly: `SESSION_COOKIE_SECURE`
   - **Value:** exactly: `true`  
     (all lowercase; no quotes in the value field).
2. Save.

---

## Part C: Save and redeploy

1. Make sure all three variables are listed:
   - `DATABASE_URL` = (long postgres URL)
   - `SECRET_KEY` = (long random string)
   - `SESSION_COOKIE_SECURE` = `true`

2. If there is a **“Save Changes”** (or similar) button, click it.

3. **Redeploy** so the app starts with the new variables:
   - On the same Web Service page, find **“Manual Deploy”** (often top right or in a **Deploy** tab).
   - Click **“Manual Deploy”** → **“Deploy latest commit”** (or **“Deploy”**).
   - Wait until the deploy finishes and status is **“Live”** (green).

4. Open your app URL (e.g. `https://your-app-name.onrender.com`).  
   - Basic analysis should work without login; **Sign up** / **Log in** should work if the database and env vars are set correctly.

---

## Quick checklist

| Step | What you did |
|------|----------------|
| 1 | Opened dashboard.render.com → your Web Service → **Environment**. |
| 2 | Created a **PostgreSQL** database (if needed), copied its **Internal Database URL**. |
| 3 | Added **DATABASE_URL** = (pasted Internal URL). |
| 4 | Generated **SECRET_KEY** (e.g. `python3 -c "import secrets; print(secrets.token_hex(32))"`) and added **SECRET_KEY** = (that string). |
| 5 | Added **SESSION_COOKIE_SECURE** = `true`. |
| 6 | Saved and ran **Manual Deploy** → **Deploy latest commit**. |

---

## If something doesn’t match (different layout)

- Render sometimes changes the dashboard. If you don’t see **Environment** in the sidebar, look for:
  - **Settings** → then **Environment**, or  
  - Tabs at the top: **Logs**, **Metrics**, **Environment**, **Settings**.
- The **“Add Environment Variable”** might be worded as **“Add Variable”** or **“+ Add”**.
- **Key** and **Value** might be in a form or in a table where you type the key in one column and the value in another.

If you tell me what you see on your screen (e.g. “I see Logs and Settings but no Environment”), I can adapt these steps to your layout.

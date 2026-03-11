# Next steps: deploy signup, login, and plans on Render

Your app now has:
- **Sign up / Log in** – users have accounts so analyses are tied to them.
- **Free plan** – 20 **basic** analyses per month (short bullets: fit %, selection chance, skills matched, areas to improve, strong in, areas to work on, other topics).
- **Upgraded plan** – $10/month: 20 **detailed** reports per month (point-wise analysis, strengths, gaps with score, deciding factors, possible interview questions, tips). After 20, **$1 per analysis** (top-up).

Follow these steps to run it locally and then deploy on Render.

---

## Step 1: Install new dependencies locally

In your project folder, with the virtual environment activated:

```bash
cd "/Users/shambhavirai/Desktop/Cursor Projects/resume-job-analyzer"
source venv/bin/activate   # or: .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

New packages: `flask-sqlalchemy`, `flask-bcrypt`, `psycopg2-binary`, `stripe`.

---

## Step 2: Set environment variables locally (optional)

For **local** runs you can leave everything default:
- Database: **SQLite** (file `resume_analyzer.db` in the project folder).
- Stripe: leave unset; “Upgrade” will show “Payments not configured” until you add keys.
- Secret: a default is used; for production you must set `SECRET_KEY`.

To test Stripe locally later, create a `.env` file (do not commit it) or export:

- `SECRET_KEY` – random string (e.g. `openssl rand -hex 32`).
- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID_MONTHLY`, `STRIPE_PRICE_ID_TOPUP` (see Step 6).

---

## Step 3: Run the app locally

```bash
./venv/bin/python app.py
```

Open **http://127.0.0.1:5050**. You should see:
- **Log in** and **Sign up** in the top bar.
- After signing up and logging in: **Basic analysis (free)** and usage (e.g. Basic: 0/20/mo).
- After an analysis: basic result (short bullets). If you later add an upgraded user in the DB or via Stripe, **Detailed report (upgraded)** will appear.

---

## Step 4: Create a Postgres database on Render

On the **free** tier, Render’s filesystem is **ephemeral**, so SQLite would be reset on each deploy. You need a **PostgreSQL** database.

### 4.1 Open the Render dashboard

1. Go to **https://dashboard.render.com** and log in (sign up with GitHub if you haven’t).
2. You should see your **Dashboard** with a list of services (or “New +” if this is a new account).

### 4.2 Create a new PostgreSQL database

1. Click the **New +** button (top right).
2. In the dropdown, click **PostgreSQL**.
3. On the “Create a new PostgreSQL” page:
   - **Name:** Type a name (e.g. `resume-analyzer-db`). This is only for your reference.
   - **Database:** Leave default (e.g. `resume_analyzer_db`).
   - **User:** Leave default (Render generates one).
   - **Region:** Choose the same region as your web service (e.g. **Oregon (US West)**) so the app and DB are close.
   - **Plan:** Select **Free**.
4. Scroll down and click **Create Database**.
5. Wait until the status shows **Available** (green). This may take a minute.

### 4.3 Copy the database URL

1. On the database’s page, find the **Connection** (or **Connect**) section.
2. You’ll see **Internal Database URL** and **External Database URL**.
   - **Use Internal Database URL** if your web service is on the same Render account (recommended; faster and free).
   - Use **External** only if the app runs somewhere else.
3. Click **Copy** next to **Internal Database URL** (or the one you chose). It looks like:
   ```text
   postgres://user:password@hostname/database_name
   ```
4. **Save this URL somewhere safe** (e.g. a temporary note). You’ll paste it as `DATABASE_URL` in the next step.  
   **Note:** Your app’s `config.py` automatically converts `postgres://` to `postgresql://` if needed, so you can paste the URL as Render shows it.

---

## Step 5: Set environment variables and deploy the web service

### 5.1 Open your Web Service

1. In the Render dashboard, go to **Dashboard** (or **Services** in the left sidebar).
2. Click your **resume-job-analyzer** (or **resume-role-fit**) **Web Service** (the one that serves the app, not the database).

### 5.2 Generate a SECRET_KEY

1. On your computer, open a terminal.
2. Run one of these to generate a long random string:
   - **macOS/Linux:** `openssl rand -hex 32`
   - **Windows (PowerShell):** `[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }) | ForEach-Object { [byte]$_ })`
3. Copy the output (e.g. `a1b2c3d4e5...`). This is your `SECRET_KEY`. **Keep it secret** and don’t commit it to Git.

### 5.3 Add environment variables on Render

1. In your Web Service on Render, click **Environment** in the left sidebar (or the **Environment** tab).
2. Under **Environment Variables**, click **Add Environment Variable** (or **Add Variable**).
3. Add these **one by one**:

   | Key | Value | Notes |
   |-----|--------|--------|
   | `SECRET_KEY` | *(paste the string from 5.2)* | Required. Used to sign sessions. |
   | `DATABASE_URL` | *(paste the Postgres URL from Step 4.3)* | Required. Replace any existing `DATABASE_URL` if present. |
   | `SESSION_COOKIE_SECURE` | `true` | Exactly the word `true` (lowercase). Required for cookies over HTTPS. |

4. For each row: type the **Key** in the left box, paste the **Value** in the right box, then click **Save** (or **Add**). Repeat until all three are added.
5. Double-check: no extra spaces, and `SESSION_COOKIE_SECURE` is the string `true`, not `True` or `1`.

### 5.4 Confirm build and start commands

1. In the same Web Service, go to **Settings** (left sidebar).
2. Under **Build & Deploy**:
   - **Build Command:** should be `pip install -r requirements.txt`. If it’s empty, add it.
   - **Start Command:** should be `gunicorn -w 1 -b 0.0.0.0:$PORT app:app`. If it’s empty, add it.
3. Save any changes.

### 5.5 Push code and deploy

1. On your computer, make sure your latest code (including `config.py`, `models.py`, `app.py`, `static/login.html`, `static/signup.html`, and the rest of the app) is committed and pushed to **GitHub** (the repo connected to this Render service).
2. Back on Render, open your Web Service → **Manual Deploy** (top right) → **Deploy latest commit**.
3. Wait until the deploy finishes and the status is **Live** (green). Check the **Logs** tab if anything fails.
4. Open **https://your-app-name.onrender.com** (use the URL shown at the top of the service). You should see **Log in** and **Sign up** in the top bar. Sign up with an email/password; the app will create the database tables on first signup.

---

## Step 6: Stripe (optional – for $10/mo and $1 top-up)

Do this only if you want paying users. Until these are set, the **Upgrade** button will show “Payments not configured.”

### 6.1 Stripe account and API key

1. Go to **https://dashboard.stripe.com** and sign in (or create an account).
2. In the left sidebar, click **Developers** → **API keys**.
3. Under **Standard keys**, find **Secret key** (starts with `sk_`). Click **Reveal** and **Copy**. Save it somewhere safe; you’ll add it as `STRIPE_SECRET_KEY` on Render.

### 6.2 Create products and prices in Stripe

1. In the Stripe dashboard, go to **Product catalog** → **Products** (or **Add product**).
2. **First product – monthly subscription:**
   - Click **Add product**.
   - **Name:** e.g. `Resume × Role Fit – Upgraded`.
   - **Pricing:** Select **Recurring**, set **$10.00 USD** and **Monthly**.
   - Click **Save**. On the product page, under **Pricing**, find the **Price ID** (e.g. `price_1ABC...`). Copy it → this is `STRIPE_PRICE_ID_MONTHLY`.
3. **Second product – one-time top-up:**
   - Click **Add product** again.
   - **Name:** e.g. `Detailed analysis top-up`.
   - **Pricing:** Select **One time**, set **$1.00 USD**.
   - Click **Save**. Copy the **Price ID** → this is `STRIPE_PRICE_ID_TOPUP`.

### 6.3 Create a webhook in Stripe

1. In Stripe, go to **Developers** → **Webhooks**.
2. Click **Add endpoint**.
3. **Endpoint URL:** `https://your-app-name.onrender.com/api/stripe-webhook` (replace `your-app-name` with your real Render URL).
4. Under **Events to send**, click **Select events** and choose **checkout.session.completed**. Then click **Add endpoint**.
5. On the new endpoint’s page, under **Signing secret**, click **Reveal** and **Copy**. This is `STRIPE_WEBHOOK_SECRET`.

### 6.4 Add Stripe env vars on Render and redeploy

1. In the Render dashboard, open your **Web Service** → **Environment**.
2. Add four more environment variables (click **Add Environment Variable** for each):

   | Key | Value |
   |-----|--------|
   | `STRIPE_SECRET_KEY` | *(Secret key from 6.1)* |
   | `STRIPE_WEBHOOK_SECRET` | *(Signing secret from 6.3)* |
   | `STRIPE_PRICE_ID_MONTHLY` | *(Price ID for $10/mo from 6.2)* |
   | `STRIPE_PRICE_ID_TOPUP` | *(Price ID for $1 one-time from 6.2)* |

3. Save each one.
4. Go to **Manual Deploy** → **Deploy latest commit** so the new variables are loaded. After the deploy is **Live**, **Upgrade — $10/mo** and **Buy top-up $1** will work.

---

## Step 7: Quick checklist

| Done | Item |
|------|------|
| ☐ | Step 1: `pip install -r requirements.txt` locally. |
| ☐ | Step 3: Run app locally; sign up, log in, run basic analysis. |
| ☐ | Step 4: Create a Postgres database on Render (4.1–4.3); copy Internal Database URL. |
| ☐ | Step 5: Set on Render: `SECRET_KEY`, `DATABASE_URL`, `SESSION_COOKIE_SECURE=true` (5.2–5.3). |
| ☐ | Step 5: Confirm build/start commands (5.4); push code and Manual Deploy (5.5); test signup/login on live URL. |
| ☐ | (Optional) Step 6: Create Stripe products/prices (6.2), webhook (6.3); add four Stripe env vars (6.4); redeploy and test upgrade/top-up. |

---

## Summary of behaviour

- **Unauthenticated:** Can open the app; **Analyze** returns “Please sign up or log in” and redirects to login.
- **Signed up (free):** 20 basic analyses per month; short bullet output; **Upgrade — $10/mo** visible.
- **Upgraded ($10/mo):** 20 detailed analyses per month; **Detailed report (upgraded)** button; after 20, **Buy top-up $1** for one more detailed analysis.
- **Data:** Analyses are **not** stored (only a count per user per month and, for upgraded, top-up balance). Resume and job text are not saved.

If you tell me your Render service URL and whether you use Postgres already, I can adapt these steps (e.g. exact env var names or Stripe webhook URL).

# Make your tool public, link it from Wix, and get it on Google Search

You’ve deployed on Render (free). Next: make the app a bit more secure, link it from your Wix site, and help Google find it.

---

## 1. Security (already added)

- **HTTPS:** Render gives you HTTPS. Always share the **https://** link so traffic is encrypted.
- **Rate limiting:** The app now limits how many analyses one person can do per minute (e.g. 30 per minute per IP). That protects your free tier from abuse and keeps the app usable for everyone.
- **No login required:** The tool stays public; no passwords or accounts. Resume/job text is not stored on the server.

Nothing else is required for “a little secure” at this stage.

---

## 2. Link the tool from your Wix website

So visitors on your Wix site can find and open the tool:

### Option A: Button or text link (recommended)

1. In **Wix Editor**, open the page where you want the tool (e.g. “Projects”, “Tools”, or “Resume”).
2. Add a **button** or **text** (e.g. “Try Resume × Role Fit” or “Resume–Job Match Tool”).
3. Select it → **Link** (or “Click to set link”).
4. Choose **Web address (URL)** and paste your Render link:  
   **https://resume-job-analyzer.onrender.com**  
   (Use your real Render URL if it’s different.)
5. Save and publish your Wix site.

When someone clicks that button or link, they go to your tool. Your Wix site stays the main place people find you; the tool is one click away.

### Option B: Embed (iframe)

Some Wix plans let you add an **HTML iframe** (embed custom code):

1. Add an **Embed** element → **HTML iframe**.
2. Enter the URL: **https://resume-job-analyzer.onrender.com**
3. Adjust size (e.g. 800px wide, 700px tall).

If the embed is blocked or looks wrong, use **Option A** (link/button) instead.

---

## 3. Get the tool visible on Google Search

### Step 1: Set the right URL in your app (one-time)

In your project, open **static/index.html**. Find the two lines with `resume-job-analyzer.onrender.com` and make sure they use **your real Render URL**:

- `<link rel="canonical" href="https://YOUR-ACTUAL-URL.onrender.com/" />`
- `<meta property="og:url" content="https://YOUR-ACTUAL-URL.onrender.com/" />`

Then push to GitHub and redeploy on Render. That helps Google and social shares use the correct link.

### Step 2: Link from your Wix site

Add a clear link to the tool on your Wix site (as in section 2). Google uses links from your main website to discover and rank other pages (like your tool). So “Your Wix site → link to tool” helps the tool get indexed.

### Step 3: Submit the tool URL to Google

1. Go to **Google Search Console**: https://search.google.com/search-console  
2. Sign in with the Google account you use for your site.
3. **Add a property:**
   - If you already have your **Wix site** as a property, you can add the **Render tool URL** as a second property (choose “URL prefix” and enter e.g. `https://resume-job-analyzer.onrender.com`).
   - Or add only the tool URL if you prefer.
4. **Verify ownership:**  
   For the Render URL, use the “HTML tag” method if possible: add the meta tag Google gives you to **static/index.html** in the `<head>`, push, redeploy, then click “Verify” in Search Console.  
   (If you only verify your Wix site, that’s still useful; linking from Wix to the tool helps Google find it.)
5. After the property is verified, use **URL Inspection** → paste your tool URL (e.g. `https://resume-job-analyzer.onrender.com`) → **Request indexing**.

Google will then crawl the tool. It can take a few days to a few weeks to show in search.

### Step 4: Optional – add the tool to your Wix sitemap or menu

- In Wix, add the tool link in your main menu or footer so it’s easy to find.
- If Wix lets you add custom links to the sitemap, include the tool URL. Otherwise, the link from your homepage or a “Projects” page is enough.

---

## 4. Checklist

| Done | Step |
|------|------|
| ☐ | Use **https://** when sharing the tool. |
| ☐ | In **static/index.html**, set canonical and **og:url** to your real Render URL, then push and redeploy. |
| ☐ | On **Wix**, add a button or text link to the tool and publish. |
| ☐ | In **Google Search Console**, add the tool URL (and/or your Wix site), verify, and request indexing for the tool URL. |
| ☐ | Optionally add the tool in your Wix menu or footer. |

After this, the tool is public, a bit more secure (HTTPS + rate limit), linked from your Wix site, and on its way to being visible on Google Search.

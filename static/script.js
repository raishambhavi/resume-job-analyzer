(function () {
  const resumeEl = document.getElementById("resume");
  const jobEl = document.getElementById("job");
  const resumeFileEl = document.getElementById("resume-file");
  const jobFileEl = document.getElementById("job-file");
  const resumeLinkEl = document.getElementById("resume-link");
  const jobLinkEl = document.getElementById("job-link");
  const analyzeBtn = document.getElementById("analyze");
  const sampleBtn = document.getElementById("sample");
  const clearBtn = document.getElementById("clear");
  const statusEl = document.getElementById("status");
  const resultsEl = document.getElementById("results");
  const compatValue = document.getElementById("compat-value");
  const chanceValue = document.getElementById("chance-value");
  const compatRing = document.getElementById("compat-ring");
  const chanceRing = document.getElementById("chance-ring");
  const matchedCountEl = document.getElementById("matched-count");
  const requiredCountEl = document.getElementById("required-count");
  const gapCountEl = document.getElementById("gap-count");
  const strongList = document.getElementById("strong-list");
  const improveList = document.getElementById("improve-list");
  const otherList = document.getElementById("other-list");
  const fitSummaryEl = document.getElementById("fit-summary");
  const alignmentListEl = document.getElementById("alignment-list");
  const gapsListEl = document.getElementById("gaps-list");
  const topicsListEl = document.getElementById("topics-list");
  const authUserEl = document.getElementById("authUser");
  const authUsageEl = document.getElementById("authUsage");
  const authLoginEl = document.getElementById("authLogin");
  const authSignupEl = document.getElementById("authSignup");
  const authUpgradeBtn = document.getElementById("authUpgrade");
  const authTopupBtn = document.getElementById("authTopup");
  const authLogoutBtn = document.getElementById("authLogout");
  const analyzeDetailedBtn = document.getElementById("analyzeDetailed");
  const detailedResultsEl = document.getElementById("detailedResults");
  const detailedContentEl = document.getElementById("detailed-content");

  const apiBase = "";
  let currentUser = null;
  let usage = null;

  const SAMPLE_RESUME = `Shambhavi Rai
Software Engineer / Data Analyst

Skills: Python, SQL, Git, Docker, AWS, React, JavaScript, Communication, Leadership

Experience:
- Built REST APIs in Flask and integrated with a React dashboard.
- Automated reporting with Python (pandas) and SQL.
- Deployed services using Docker and AWS.

Projects:
- Resume × Role Fit Analyzer (Flask, HTML/CSS/JS)
`;

  const SAMPLE_JOB = `We are hiring a Software Engineer.

Requirements:
- Strong Python and SQL
- Experience with REST APIs
- Familiarity with Git and Docker
- Cloud experience (AWS preferred)
- Bonus: React, CI/CD, Kubernetes
- Strong communication and teamwork
`;

  function setStatus(msg, isError = false) {
    statusEl.textContent = msg;
    statusEl.classList.toggle("error", isError);
  }

  function renderSkillList(container, items) {
    container.innerHTML = "";
    container.classList.toggle("empty", !items.length);
    items.forEach((skill) => {
      const li = document.createElement("li");
      li.textContent = skill;
      container.appendChild(li);
    });
  }

  function clampPercent(value) {
    const n = Number(value);
    if (Number.isNaN(n)) return 0;
    return Math.max(0, Math.min(100, n));
  }

  function setRing(ringEl, percent) {
    const p = clampPercent(percent);
    // CSS expects --p in the 0..100 range
    ringEl.style.setProperty("--p", p.toString());
    ringEl.setAttribute("aria-label", `${p}%`);
  }

  function resetUI() {
    resultsEl.classList.add("hidden");
    if (detailedResultsEl) detailedResultsEl.classList.add("hidden");
    compatValue.textContent = "—";
    chanceValue.textContent = "—";
    matchedCountEl.textContent = "—";
    requiredCountEl.textContent = "—";
    gapCountEl.textContent = "—";
    setRing(compatRing, 0);
    setRing(chanceRing, 0);
    renderSkillList(strongList, []);
    renderSkillList(improveList, []);
    renderSkillList(otherList, []);
    fitSummaryEl.textContent = "—";
    alignmentListEl.innerHTML = "";
    gapsListEl.innerHTML = "";
    topicsListEl.innerHTML = "";
    setStatus("");
  }

  function setAuthUI(user, usageData) {
    currentUser = user;
    usage = usageData || usage;
    if (!authUserEl) return;
    if (!user) {
      authUserEl.textContent = "";
      authUsageEl.textContent = "";
      authLoginEl.classList.remove("hidden");
      authSignupEl.classList.remove("hidden");
      authUpgradeBtn.classList.add("hidden");
      authTopupBtn.classList.add("hidden");
      authLogoutBtn.classList.add("hidden");
      return;
    }
    authLoginEl.classList.add("hidden");
    authSignupEl.classList.add("hidden");
    authUserEl.textContent = user.email;
    authLogoutBtn.classList.remove("hidden");
    const basic = usageData?.basic_used ?? usage?.basic_used ?? 0;
    const basicLimit = usageData?.basic_limit ?? usage?.basic_limit ?? 20;
    authUsageEl.textContent = `Basic: ${basic}/${basicLimit}/mo`;
    if (user.plan === "upgraded") {
      authUpgradeBtn.classList.add("hidden");
      const det = usageData?.detailed_used ?? usage?.detailed_used ?? 0;
      const detLimit = usageData?.detailed_limit ?? usage?.detailed_limit ?? 20;
      authUsageEl.textContent += ` • Detailed: ${det}/${detLimit}`;
      if ((usageData?.detailed_extra_remaining ?? user.detailed_extra_remaining ?? 0) > 0)
        authUsageEl.textContent += ` (+${usageData?.detailed_extra_remaining ?? user.detailed_extra_remaining} top-up)`;
      authTopupBtn.classList.remove("hidden");
    } else {
      authUpgradeBtn.classList.remove("hidden");
      authTopupBtn.classList.add("hidden");
    }
  }

  function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove("hidden");
  }
  function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add("hidden");
  }

  function showDetailedGate(message, showSignup, showLogin, showUpgrade) {
    const gateEl = document.getElementById("detailedGateMessage");
    const textEl = document.getElementById("detailedGateText");
    const actionsEl = document.getElementById("detailedGateActions");
    if (!gateEl || !textEl || !actionsEl) return;
    textEl.textContent = message;
    actionsEl.innerHTML = "";
    if (showSignup) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "btn-analyze";
      b.textContent = "Sign up";
      b.addEventListener("click", () => { gateEl.classList.add("hidden"); openModal("signupModal"); });
      actionsEl.appendChild(b);
    }
    if (showLogin) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "btn-secondary";
      b.textContent = "Log in";
      b.addEventListener("click", () => { gateEl.classList.add("hidden"); openModal("loginModal"); });
      actionsEl.appendChild(b);
    }
    if (showUpgrade && authUpgradeBtn) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "btn-upgrade";
      b.textContent = "Upgrade — $10/mo";
      b.addEventListener("click", () => authUpgradeBtn.click());
      actionsEl.appendChild(b);
    }
    gateEl.classList.remove("hidden");
  }

  function hideDetailedGate() {
    const gateEl = document.getElementById("detailedGateMessage");
    if (gateEl) gateEl.classList.add("hidden");
  }

  async function loadAuth() {
    try {
      const res = await fetch(apiBase + "/api/me", { credentials: "include" });
      const data = await res.json();
      setAuthUI(data.user || null, data.usage || null);
    } catch (e) {
      setAuthUI(null);
    }
  }

  function renderDetailedReport(data) {
    if (!detailedContentEl) return;
    let html = "";
    html += `<p><strong>Match:</strong> ${data.match_percentage}%</p>`;
    html += `<p><strong>Selection chance:</strong> ${data.selection_chance}%</p>`;
    if (data.point_wise_analysis?.length) {
      html += "<h3>Point-wise analysis</h3><ul>";
      data.point_wise_analysis.forEach((p) => { html += "<li>" + p + "</li>"; });
      html += "</ul>";
    }
    if (data.strengths?.length) {
      html += "<h3>Strengths</h3><ul>";
      data.strengths.forEach((s) => { html += "<li>" + s + "</li>"; });
      html += "</ul>";
    }
    if (data.gaps_with_score?.length) {
      html += "<h3>Gaps (score & description)</h3><ul>";
      data.gaps_with_score.forEach((g) => { html += "<li><strong>" + (g.skill || g) + "</strong> — " + (g.score || "") + ": " + (g.description || "") + "</li>"; });
      html += "</ul>";
    }
    if (data.deciding_factors?.length) {
      html += "<h3>Major deciding factors</h3><ul>";
      data.deciding_factors.forEach((d) => { html += "<li>" + d + "</li>"; });
      html += "</ul>";
    }
    if (data.possible_questions?.length) {
      html += "<h3>Questions you might get asked</h3><ul>";
      data.possible_questions.forEach((q) => { html += "<li>" + q + "</li>"; });
      html += "</ul>";
    }
    if (data.tips?.length) {
      html += "<h3>Tips to strengthen your resume</h3><ul>";
      data.tips.forEach((t) => { html += "<li>" + t + "</li>"; });
      html += "</ul>";
    }
    if (data.skills_to_prepare?.length) {
      html += "<h3>Relevant skills to prepare</h3>";
      data.skills_to_prepare.forEach((st) => {
        html += "<p><strong>" + (st.skill || st) + "</strong></p><ul>";
        (st.topics || []).forEach((tp) => { html += "<li>" + tp + "</li>"; });
        html += "</ul>";
      });
    }
    detailedContentEl.innerHTML = html;
  }

  function setMode(group, mode) {
    const tabs = document.querySelectorAll(`.mode-tabs[data-group="${group}"] .tab`);
    tabs.forEach((btn) => {
      const active = btn.dataset.mode === mode;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-selected", active ? "true" : "false");
    });

    const panels = document.querySelectorAll(`.mode-panel[data-group="${group}"]`);
    panels.forEach((panel) => {
      panel.classList.toggle("is-hidden", panel.dataset.mode !== mode);
    });
  }

  function getMode(group) {
    const active = document.querySelector(`.mode-tabs[data-group="${group}"] .tab.is-active`);
    return active?.dataset?.mode || "paste";
  }

  function initTabs() {
    document.querySelectorAll(".mode-tabs").forEach((tabsEl) => {
      const group = tabsEl.dataset.group;
      tabsEl.querySelectorAll(".tab").forEach((btn) => {
        btn.addEventListener("click", () => {
          setMode(group, btn.dataset.mode);
          resetUI();
        });
      });
    });
  }

  function renderCategoryStack(container, items) {
    container.innerHTML = "";
    if (!items || !items.length) {
      const p = document.createElement("p");
      p.className = "hint";
      p.textContent = "—";
      container.appendChild(p);
      return;
    }

    items.forEach((it) => {
      const div = document.createElement("div");
      div.className = "pill";
      const title = document.createElement("span");
      title.className = "pill-title";
      title.textContent = it.category;
      const meta = document.createElement("span");
      meta.className = "pill-meta";
      meta.textContent = (it.skills || []).join(", ");
      div.appendChild(title);
      div.appendChild(meta);
      container.appendChild(div);
    });
  }

  function renderTopics(container, topics) {
    container.innerHTML = "";
    if (!topics || !topics.length) {
      const p = document.createElement("p");
      p.className = "hint";
      p.textContent = "No missing topics detected.";
      container.appendChild(p);
      return;
    }

    topics.forEach((t) => {
      const wrap = document.createElement("div");
      wrap.className = "topic";
      const skill = document.createElement("div");
      skill.className = "topic-skill";
      skill.textContent = t.skill;
      wrap.appendChild(skill);

      const ul = document.createElement("ul");
      (t.topics || []).forEach((x) => {
        const li = document.createElement("li");
        li.textContent = x;
        ul.appendChild(li);
      });
      wrap.appendChild(ul);
      container.appendChild(wrap);
    });
  }

  function validateAndAppend(formData, group) {
    const mode = getMode(group);
    formData.append(`${group}_mode`, mode);

    if (mode === "paste") {
      const text = (group === "resume" ? resumeEl.value : jobEl.value).trim();
      formData.append(`${group}_text`, text);
      return !!text;
    }

    if (mode === "link") {
      const url = (group === "resume" ? resumeLinkEl.value : jobLinkEl.value).trim();
      formData.append(`${group}_link`, url);
      return !!url;
    }

    const fileEl = group === "resume" ? resumeFileEl : jobFileEl;
    const f = fileEl?.files?.[0];
    if (f) formData.append(`${group}_file`, f, f.name);
    return !!f;
  }

  sampleBtn.addEventListener("click", () => {
    setMode("resume", "paste");
    setMode("job", "paste");
    resumeEl.value = SAMPLE_RESUME;
    jobEl.value = SAMPLE_JOB;
    resetUI();
    setStatus("Sample loaded. Click “Analyze fit”.");
  });

  clearBtn.addEventListener("click", () => {
    resumeEl.value = "";
    jobEl.value = "";
    resumeLinkEl.value = "";
    jobLinkEl.value = "";
    if (resumeFileEl) resumeFileEl.value = "";
    if (jobFileEl) jobFileEl.value = "";
    setMode("resume", "paste");
    setMode("job", "paste");
    resetUI();
    setStatus("Cleared.");
  });

  analyzeBtn.addEventListener("click", async () => {
    hideDetailedGate();
    const formData = new FormData();
    const okResume = validateAndAppend(formData, "resume");
    const okJob = validateAndAppend(formData, "job");

    if (!okResume || !okJob) {
      setStatus("Please provide both resume and job description (Paste, Upload, or Link for each).", true);
      return;
    }

    analyzeBtn.disabled = true;
    setStatus("Analyzing…");

    try {
      const res = await fetch(apiBase + "/api/analyze", { method: "POST", body: formData, credentials: "include" });
      const data = await res.json();

      if (!res.ok) {
        setStatus(data.error || "Something went wrong.", true);
        return;
      }

      resultsEl.classList.remove("hidden");
      if (detailedResultsEl) detailedResultsEl.classList.add("hidden");
      const score = data.percentage_fit ?? data.compatibility_score;
      const chance = data.chances_of_getting_hired ?? data.selection_chance;
      compatValue.textContent = score;
      chanceValue.textContent = chance;
      setRing(compatRing, score);
      setRing(chanceRing, chance);
      matchedCountEl.textContent = data?.summary?.matched_count ?? "—";
      requiredCountEl.textContent = data?.summary?.required_count ?? "—";
      gapCountEl.textContent = data?.summary?.gap_count ?? "—";
      renderSkillList(strongList, data.you_are_strong_in || data.skills_matched || data.strong_skills || []);
      renderSkillList(improveList, data.areas_to_work_on || data.areas_to_improve || data.skills_to_improve || []);
      renderSkillList(otherList, data.other_topics_to_consider || data.other_relevant_skills || []);
      fitSummaryEl.textContent = data.fit_summary || "—";
      if (data.major_alignment) renderCategoryStack(alignmentListEl, data.major_alignment);
      else alignmentListEl.innerHTML = "";
      if (data.major_gaps) renderCategoryStack(gapsListEl, data.major_gaps);
      else gapsListEl.innerHTML = "";
      if (data.topics_to_prepare) renderTopics(topicsListEl, data.topics_to_prepare);
      else topicsListEl.innerHTML = "";
      if (data.usage) setAuthUI(currentUser, data.usage);
      setStatus("");
    } catch (err) {
      setStatus("Network error. Is the server running?", true);
    } finally {
      analyzeBtn.disabled = false;
    }
  });

  if (analyzeDetailedBtn) {
    analyzeDetailedBtn.addEventListener("click", async () => {
      const formData = new FormData();
      const okResume = validateAndAppend(formData, "resume");
      const okJob = validateAndAppend(formData, "job");
      if (!okResume || !okJob) {
        setStatus("Please provide both resume and job description.", true);
        hideDetailedGate();
        return;
      }
      if (!currentUser) {
        showDetailedGate("Sign up or log in to get detailed analysis (upgrade after creating an account).", true, true, false);
        return;
      }
      if (currentUser.plan !== "upgraded") {
        showDetailedGate("Upgrade to the $10/month plan to unlock detailed reports.", false, false, true);
        return;
      }
      hideDetailedGate();
      analyzeDetailedBtn.disabled = true;
      setStatus("Generating detailed report…");
      try {
        const res = await fetch(apiBase + "/api/analyze-detailed", { method: "POST", body: formData, credentials: "include" });
        const data = await res.json();
        if (res.status === 401) {
          setStatus("Please log in.", true);
          showDetailedGate("Sign up or log in to get detailed analysis.", true, true, false);
          return;
        }
        if (res.status === 402) {
          setStatus(data.error || "Limit reached.", true);
          if (data.need_topup && authTopupBtn) authTopupBtn.classList.remove("hidden");
          return;
        }
        if (!res.ok) { setStatus(data.error || "Error.", true); return; }
        renderDetailedReport(data);
        detailedResultsEl.classList.remove("hidden");
        if (data.usage) setAuthUI(currentUser, data.usage);
        setStatus("");
      } catch (e) {
        setStatus("Network error.", true);
      } finally {
        analyzeDetailedBtn.disabled = false;
      }
    });
  }

  if (authUpgradeBtn) {
    authUpgradeBtn.addEventListener("click", async () => {
      try {
        const res = await fetch(apiBase + "/api/create-checkout-subscription", { method: "POST", credentials: "include" });
        const data = await res.json();
        if (data.url) window.location.href = data.url;
        else setStatus(data.error || "Could not start checkout.", true);
      } catch (e) {
        setStatus("Network error.", true);
      }
    });
  }
  if (authTopupBtn) {
    authTopupBtn.addEventListener("click", async () => {
      try {
        const res = await fetch(apiBase + "/api/create-checkout-topup", { method: "POST", credentials: "include" });
        const data = await res.json();
        if (data.url) window.location.href = data.url;
        else setStatus(data.error || "Could not start checkout.", true);
      } catch (e) {
        setStatus("Network error.", true);
      }
    });
  }
  if (authLogoutBtn) {
    authLogoutBtn.addEventListener("click", async () => {
      await fetch(apiBase + "/api/logout", { method: "POST", credentials: "include" });
      window.location.reload();
    });
  }

  function checkStripeReturn() {
    const params = new URLSearchParams(window.location.search);
    if (params.get("upgraded") === "1") {
      setStatus("You’re upgraded! You now have access to detailed reports.");
      history.replaceState({}, "", window.location.pathname);
    } else if (params.get("topup") === "1") {
      setStatus("Top-up added. You have one more detailed analysis.");
      history.replaceState({}, "", window.location.pathname);
    } else if (params.get("canceled") === "1") {
      setStatus("Checkout was canceled.");
      history.replaceState({}, "", window.location.pathname);
    }
  }

  document.querySelectorAll("[data-dismiss]").forEach((el) => {
    el.addEventListener("click", () => closeModal(el.getAttribute("data-dismiss")));
  });

  if (authLoginEl) authLoginEl.addEventListener("click", () => openModal("loginModal"));
  if (authSignupEl) authSignupEl.addEventListener("click", () => openModal("signupModal"));

  document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("loginEmail").value.trim().toLowerCase();
    const password = document.getElementById("loginPassword").value;
    try {
      const res = await fetch(apiBase + "/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
        credentials: "include",
      });
      const data = await res.json();
      if (!res.ok) { setStatus(data.error || "Login failed.", true); return; }
      closeModal("loginModal");
      setAuthUI(data.user, null);
      loadAuth();
      setStatus("Logged in.");
    } catch (err) { setStatus("Network error.", true); }
  });

  document.getElementById("signupForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("signupEmail").value.trim().toLowerCase();
    const password = document.getElementById("signupPassword").value;
    try {
      const res = await fetch(apiBase + "/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
        credentials: "include",
      });
      const data = await res.json();
      if (!res.ok) { setStatus(data.error || "Sign up failed.", true); return; }
      closeModal("signupModal");
      setAuthUI(data.user, null);
      loadAuth();
      setStatus("Account created. You can now upgrade for detailed analysis.");
    } catch (err) { setStatus("Network error.", true); }
  });

  document.getElementById("forgotPasswordTrigger")?.addEventListener("click", () => {
    closeModal("loginModal");
    document.getElementById("forgotEmail").value = document.getElementById("loginEmail").value || "";
    openModal("forgotModal");
  });

  document.getElementById("forgotForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("forgotEmail").value.trim().toLowerCase();
    try {
      const res = await fetch(apiBase + "/api/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (!res.ok) { setStatus(data.error || "Could not send code.", true); return; }
      closeModal("forgotModal");
      document.getElementById("resetEmail").value = email;
      document.getElementById("resetOtp").value = "";
      document.getElementById("resetNewPassword").value = "";
      openModal("resetModal");
      setStatus("Check your email for the code.");
    } catch (err) { setStatus("Network error.", true); }
  });

  document.getElementById("resetForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("resetEmail").value.trim().toLowerCase();
    const otp = document.getElementById("resetOtp").value.trim();
    const new_password = document.getElementById("resetNewPassword").value;
    try {
      const res = await fetch(apiBase + "/api/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, otp, new_password }),
      });
      const data = await res.json();
      if (!res.ok) { setStatus(data.error || "Reset failed.", true); return; }
      closeModal("resetModal");
      setStatus(data.message || "Password updated. You can log in.");
    } catch (err) { setStatus("Network error.", true); }
  });

  initTabs();
  setMode("resume", "paste");
  setMode("job", "paste");
  loadAuth().then(checkStripeReturn);
  resetUI();
})();

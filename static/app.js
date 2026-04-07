(function () {
  const api = "";

  const els = {
    pages: () => document.querySelectorAll(".cr-page"),
    navItems: () => document.querySelectorAll(".cr-nav-item"),
    authModal: document.getElementById("auth-modal"),
    authTitle: document.getElementById("auth-modal-title"),
    formLogin: document.getElementById("form-login"),
    formSignup: document.getElementById("form-signup"),
    authUserWrap: document.getElementById("auth-user-wrap"),
    authUserEmail: document.getElementById("auth-user-email"),
    btnOpenLogin: document.getElementById("btn-open-login"),
    btnOpenSignup: document.getElementById("btn-open-signup"),
    btnLogout: document.getElementById("btn-logout"),
    accountGuest: document.getElementById("account-guest"),
    accountFormWrap: document.getElementById("account-form-wrap"),
    profilePct: document.getElementById("profile-pct"),
    profileMeterFill: document.getElementById("profile-meter-fill"),
    rbPreviewModal: document.getElementById("rb-preview-modal"),
    rbPreviewFrame: document.getElementById("rb-preview-frame"),
  };

  let lastPreviewHtml = "";
  let lastRbResume = "";
  let lastRbKeywords = "";
  let skillsCache = [];
  let rolesCache = [];

  function showPage(name) {
    els.pages().forEach((p) => {
      p.classList.toggle("hidden", p.dataset.page !== name);
    });
    els.navItems().forEach((b) => {
      b.classList.toggle("is-active", b.dataset.nav === name);
    });
    if (name === "account") loadAccountPage();
    if (name === "job-fit") loadHandoff("job-fit");
    if (name === "resume-builder") loadHandoff("resume-builder");
    if (name === "interview") loadHandoff("interview");
  }

  function loadHandoff(page) {
    try {
      const raw = sessionStorage.getItem("cr_handoff");
      if (!raw) return;
      const h = JSON.parse(raw);
      if (page === "job-fit") {
        if (h.resume) document.getElementById("jf-resume-text").value = h.resume;
        if (h.job_description) document.getElementById("jf-job-text").value = h.job_description;
        if (h.company_name) document.getElementById("jf-company").value = h.company_name;
      }
      if (page === "resume-builder") {
        if (h.job_description) document.getElementById("rb-jd").value = h.job_description;
        if (h.resume) document.getElementById("rb-resume-text").value = h.resume;
      }
      if (page === "interview") {
        if (h.job_description) document.getElementById("iv-jd").value = h.job_description;
        if (h.resume) document.getElementById("iv-resume").value = h.resume;
        if (h.company_name) document.getElementById("iv-company").value = h.company_name;
      }
    } catch (_) {}
  }

  function setHandoff(obj) {
    sessionStorage.setItem("cr_handoff", JSON.stringify(obj));
  }

  function _setOAuthRowVisible(visible) {
    const show = visible !== false;
    const div = document.getElementById("oauth-divider");
    const g = document.getElementById("btn-oauth-google");
    const li = document.getElementById("btn-oauth-linkedin");
    const note = document.getElementById("oauth-config-note");
    if (div) div.classList.toggle("hidden", !show);
    if (g) g.classList.toggle("hidden", !show);
    if (li) li.classList.toggle("hidden", !show);
    if (note) note.classList.toggle("hidden", !show);
  }

  function openAuth(mode) {
    els.authModal.classList.remove("hidden");
    document.getElementById("auth-main-tabs").classList.remove("hidden");
    document.getElementById("auth-view-forgot").classList.add("hidden");
    document.getElementById("auth-view-reset").classList.add("hidden");
    _setOAuthRowVisible(true);
    els.authTitle.textContent = mode === "signup" ? "Sign up" : "Login";
    document.querySelectorAll(".cr-auth-tab").forEach((t) => {
      t.classList.toggle("is-active", t.dataset.authTab === mode);
    });
    if (mode === "login") {
      document.getElementById("auth-view-login").classList.remove("hidden");
      document.getElementById("form-signup").classList.add("hidden");
    } else {
      document.getElementById("auth-view-login").classList.add("hidden");
      document.getElementById("form-signup").classList.remove("hidden");
    }
  }

  function openForgotPassword() {
    els.authModal.classList.remove("hidden");
    document.getElementById("auth-main-tabs").classList.add("hidden");
    document.getElementById("auth-view-login").classList.add("hidden");
    document.getElementById("form-signup").classList.add("hidden");
    document.getElementById("auth-view-forgot").classList.remove("hidden");
    document.getElementById("auth-view-reset").classList.add("hidden");
    _setOAuthRowVisible(false);
    els.authTitle.textContent = "Reset password";
    document.getElementById("forgot-status").textContent = "";
    document.getElementById("forgot-email").value = "";
  }

  function openResetPasswordView(email, token) {
    els.authModal.classList.remove("hidden");
    document.getElementById("auth-main-tabs").classList.add("hidden");
    document.getElementById("auth-view-login").classList.add("hidden");
    document.getElementById("form-signup").classList.add("hidden");
    document.getElementById("auth-view-forgot").classList.add("hidden");
    document.getElementById("auth-view-reset").classList.remove("hidden");
    _setOAuthRowVisible(false);
    els.authTitle.textContent = "New password";
    document.getElementById("reset-email").value = email;
    document.getElementById("reset-token").value = token;
    document.getElementById("reset-password").value = "";
    document.getElementById("reset-status").textContent = "";
  }

  function closeAuth() {
    els.authModal.classList.add("hidden");
    document.getElementById("auth-view-forgot").classList.add("hidden");
    document.getElementById("auth-view-reset").classList.add("hidden");
  }

  async function refreshAuth() {
    const res = await fetch(api + "/api/auth/me", { credentials: "include" });
    const data = await res.json();
    const authed = data.authenticated;
    document.getElementById("btn-open-login").classList.toggle("hidden", authed);
    document.getElementById("btn-open-signup").classList.toggle("hidden", authed);
    els.authUserWrap.classList.toggle("hidden", !authed);
    if (authed) {
      els.authUserEmail.textContent = data.user?.email || "";
    }
    const heroGuest = document.getElementById("hero-actions-guest");
    const heroUser = document.getElementById("hero-actions-user");
    if (heroGuest && heroUser) {
      heroGuest.classList.toggle("hidden", authed);
      heroUser.classList.toggle("hidden", !authed);
    }
    return data;
  }

  // --- Mini tabs (reuse pattern) ---
  function setMode(group, mode) {
    document.querySelectorAll(`.mode-tabs[data-group="${group}"] .tab`).forEach((btn) => {
      const on = btn.dataset.mode === mode;
      btn.classList.toggle("is-active", on);
    });
    document.querySelectorAll(`.mode-panel[data-group="${group}"]`).forEach((panel) => {
      panel.classList.toggle("is-hidden", panel.dataset.mode !== mode);
    });
  }

  function getMode(group) {
    const t = document.querySelector(`.mode-tabs[data-group="${group}"] .tab.is-active`);
    return t?.dataset?.mode || "paste";
  }

  function bindTabs(group) {
    const wrap = document.querySelector(`.mode-tabs[data-group="${group}"]`);
    if (!wrap) return;
    wrap.querySelectorAll(".tab").forEach((btn) => {
      btn.addEventListener("click", () => setMode(group, btn.dataset.mode));
    });
  }

  async function fillSavedSelect(selectId) {
    const sel = document.getElementById(selectId);
    if (!sel) return;
    const res = await fetch(api + "/api/resumes", { credentials: "include" });
    if (!res.ok) return;
    const data = await res.json();
    const cur = sel.value;
    sel.innerHTML = '<option value="">Select…</option>';
    (data.resumes || []).forEach((r) => {
      const o = document.createElement("option");
      o.value = r.id;
      o.textContent = (r.is_primary ? "★ " : "") + r.display_name;
      sel.appendChild(o);
    });
    if (cur) sel.value = cur;
  }

  async function loadResumeIntoField(selectId, textAreaId) {
    const id = document.getElementById(selectId).value;
    if (!id) return;
    const res = await fetch(api + "/api/resumes/" + id, { credentials: "include" });
    const data = await res.json();
    if (res.ok && data.content_text) document.getElementById(textAreaId).value = data.content_text;
  }

  function appendMultipart(formData, tabGroup, fieldPrefix, textId, fileId, linkId) {
    const mode = getMode(tabGroup);
    formData.append(fieldPrefix + "_mode", mode);
    if (mode === "paste") {
      const t = document.getElementById(textId).value.trim();
      formData.append(fieldPrefix + "_text", t);
      return !!t;
    }
    if (mode === "link") {
      const u = document.getElementById(linkId).value.trim();
      formData.append(fieldPrefix + "_link", u);
      return !!u;
    }
    const f = document.getElementById(fileId)?.files?.[0];
    if (f) formData.append(fieldPrefix + "_file", f, f.name);
    return !!f;
  }

  // --- Job fit ---
  document.getElementById("jf-run").addEventListener("click", async () => {
    const st = document.getElementById("jf-status");
    st.textContent = "";
    if (getMode("jf-resume") === "saved") {
      await loadResumeIntoField("jf-resume-saved", "jf-resume-text");
    }
    const company = document.getElementById("jf-company").value.trim();

    const resumePaste = document.getElementById("jf-resume-text").value.trim();
    const jobPaste = document.getElementById("jf-job-text").value.trim();
    const bothPasteFilled =
      getMode("jf-resume") === "paste" &&
      getMode("jf-job") === "paste" &&
      resumePaste &&
      jobPaste;

    st.textContent = "Analyzing…";
    let res;
    let data;
    if (!bothPasteFilled) {
      const formData = new FormData();
      const okR = appendMultipart(formData, "jf-resume", "resume", "jf-resume-text", "jf-resume-file", "jf-resume-link");
      const okJ = appendMultipart(formData, "jf-job", "job", "jf-job-text", "jf-job-file", "jf-job-link");
      if (!okR || !okJ) {
        st.textContent = "Please provide resume and job description (all input modes).";
        return;
      }
      formData.append("company_name", company);
      res = await fetch(api + "/api/job-fit-report-multipart", { method: "POST", body: formData });
      data = await res.json();
    } else {
      res = await fetch(api + "/api/job-fit-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume: resumePaste,
          job_description: jobPaste,
          company_name: company,
        }),
      });
      data = await res.json();
    }
    const resumeText = data.handoff?.resume || document.getElementById("jf-resume-text").value.trim();
    const jobText = data.handoff?.job_description || document.getElementById("jf-job-text").value.trim();
    if (!res.ok) {
      st.textContent = data.error || "Error";
      return;
    }
    st.textContent = "";
    const box = document.getElementById("jf-results");
    box.classList.remove("hidden");
    const ats = data.ats || {};
    box.innerHTML = `
      <div class="cr-report-grid">
        <div class="cr-stat"><span>Fit score</span><strong>${data.fit_score}%</strong></div>
        <div class="cr-stat"><span>Selection score</span><strong>${data.selection_score}%</strong></div>
        <div class="cr-stat"><span>ATS score</span><strong>${ats.ats_score}%</strong></div>
        <div class="cr-stat"><span>ATS-friendly?</span><strong>${ats.likely_ats_friendly ? "Likely yes" : "Needs work"}</strong></div>
      </div>
      <h3 class="cr-h3">Is your resume ATS-friendly?</h3>
      <p>${(ats.improvement_tips || []).map((t) => "• " + escapeHtml(t)).join("<br/>")}</p>
      <h3 class="cr-h3">How can you improve your resume?</h3>
      <ul>${(data.resume_improvements || []).map((t) => "<li>" + escapeHtml(t) + "</li>").join("")}</ul>
      <div class="cr-cta-row">
        <button type="button" class="cr-btn-accent" id="jf-to-builder">Get ATS-friendly resume → Resume Builder</button>
        <button type="button" class="cr-btn-secondary" id="jf-to-interview">Prepare for interview</button>
      </div>
      <h3 class="cr-h3">Strengths</h3>
      <ul>${(data.strengths || []).map((s) => "<li>" + escapeHtml(String(s)) + "</li>").join("")}</ul>
      <h3 class="cr-h3">Gaps</h3>
      <ul>${(data.gaps || []).map((g) => "<li>" + escapeHtml((g.skill || "") + " — " + (g.description || "")) + "</li>").join("")}</ul>
      <h3 class="cr-h3">Deciding factors & interview intel</h3>
      <ul>${(data.deciding_factors || []).map((d) => "<li>" + escapeHtml(String(d)) + "</li>").join("")}</ul>
      <h3 class="cr-h3">Company / review search links</h3>
      <ul>${(data.company_insights?.search_links || []).map((l) => '<li><a href="' + escapeAttr(l.url) + '" target="_blank" rel="noopener">' + escapeHtml(l.label) + "</a></li>").join("")}</ul>
      <p class="cr-hint">${escapeHtml(data.company_insights?.disclaimer || "")}</p>
      <h3 class="cr-h3">Skills to polish</h3>
      <div class="cr-mini-list">${(data.skills_to_polish || []).map((x) => "<div><strong>" + escapeHtml(x.skill || "") + "</strong><ul>" + (x.topics || []).map((t) => "<li>" + escapeHtml(t) + "</li>").join("") + "</ul></div>").join("")}</div>
    `;
    document.getElementById("jf-to-builder").onclick = () => {
      setHandoff({
        resume: resumeText,
        job_description: jobText,
        company_name: company,
      });
      showPage("resume-builder");
    };
    document.getElementById("jf-to-interview").onclick = () => {
      setHandoff({
        resume: resumeText,
        job_description: jobText,
        company_name: company,
      });
      showPage("interview");
    };
  });

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }
  function escapeAttr(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/</g, "&lt;");
  }

  function rerenderSkillTags() {
    renderTags("skill-tags", profileState.skills, (i) => {
      profileState.skills.splice(i, 1);
      rerenderSkillTags();
    });
  }
  function rerenderRoleTags() {
    renderTags("role-tags", profileState.desired_roles, (i) => {
      profileState.desired_roles.splice(i, 1);
      rerenderRoleTags();
    });
  }

  // --- Resume builder ---
  async function runResumeBuilderAnalyze() {
    const st = document.getElementById("rb-status");
    st.textContent = "";
    const rbMode = getMode("rb-res");
    if (rbMode === "saved") await loadResumeIntoField("rb-resume-saved", "rb-resume-text");
    const jd = document.getElementById("rb-jd").value.trim();
    const resume = document.getElementById("rb-resume-text").value.trim();
    const resumeFile = document.getElementById("rb-resume-file")?.files?.[0];
    const hasResume = !!resumeFile || !!resume;
    if (!jd || !hasResume) {
      st.textContent = "Job description and resume required.";
      return;
    }
    st.textContent = "Analyzing…";
    let res;
    if (resumeFile) {
      const fd = new FormData();
      fd.append("job_description", jd);
      fd.append("resume_file", resumeFile, resumeFile.name);
      res = await fetch(api + "/api/resume-builder/analyze", {
        method: "POST",
        body: fd,
      });
    } else {
      lastRbResume = resume;
      res = await fetch(api + "/api/resume-builder/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_description: jd, resume }),
      });
    }
    const data = await res.json();
    if (!res.ok) {
      st.textContent = data.error || "Error";
      return;
    }
    st.textContent = "";
    const nar = data.narrative || {};
    const ats = data.ats || {};
    const kw = (data.keywords_from_jd || []).slice(0, 25).join(", ");
    lastRbKeywords = (data.keywords_from_jd || []).slice(0, 20).join(", ");
    document.getElementById("rb-output").classList.remove("hidden");
    document.getElementById("rb-output").innerHTML = `
      <h3>Keywords from job description</h3>
      <p class="cr-mono">${escapeHtml(kw)}</p>
      <h3>ATS analysis</h3>
      <p>Score: <strong>${ats.ats_score}%</strong> — keyword match ${ats.keyword_match_score}%, structure ${ats.structure_score}%</p>
      <p>Missing keywords (consider if truthful): ${escapeHtml((ats.keywords_missing_from_resume || []).join(", "))}</p>
      <h3>AI / guided suggestions</h3>
      <p>${escapeHtml(nar.executive_summary || "")}</p>
      <ul>${(nar.suggested_bullet_rewrites || []).map((x) => "<li>" + escapeHtml(x) + "</li>").join("")}</ul>
      <h4>Formatting</h4>
      <ul>${(nar.formatting_tips || []).map((x) => "<li>" + escapeHtml(x) + "</li>").join("")}</ul>
    `;
  }

  document.getElementById("rb-analyze").addEventListener("click", runResumeBuilderAnalyze);

  document.getElementById("rb-preview").addEventListener("click", async () => {
    const st = document.getElementById("rb-status");
    const resume = document.getElementById("rb-resume-text").value.trim() || lastRbResume;
    if (!resume) {
      st.textContent = "Add resume text first (or run Analyze).";
      return;
    }
    if (!lastRbKeywords) await runResumeBuilderAnalyze();
    const tid = document.getElementById("rb-template").value || "classic-chronological";
    const kwLine = lastRbKeywords || "";
    const res = await fetch(api + "/api/resume-builder/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ template_id: tid, resume, keyword_line: kwLine }),
    });
    const data = await res.json();
    if (!res.ok) {
      st.textContent = data.error || "Preview failed";
      return;
    }
    lastPreviewHtml = data.html;
    const blob = new Blob([data.html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    els.rbPreviewFrame.src = url;
    els.rbPreviewModal.classList.remove("hidden");
  });

  document.querySelectorAll("[data-close-preview]").forEach((el) => {
    el.addEventListener("click", () => {
      els.rbPreviewModal.classList.add("hidden");
      if (els.rbPreviewFrame.src.startsWith("blob:")) URL.revokeObjectURL(els.rbPreviewFrame.src);
      els.rbPreviewFrame.src = "";
    });
  });

  document.getElementById("rb-download").addEventListener("click", () => {
    if (!lastPreviewHtml) return;
    const blob = new Blob([lastPreviewHtml], { type: "text/html;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "clear-resume-ats.html";
    a.click();
    URL.revokeObjectURL(a.href);
  });

  document.getElementById("rb-download-pdf").addEventListener("click", async () => {
    const st = document.getElementById("rb-status");
    const resume = document.getElementById("rb-resume-text").value.trim() || lastRbResume;
    if (!resume) {
      st.textContent = "Add resume text or open preview first.";
      return;
    }
    if (!lastRbKeywords) await runResumeBuilderAnalyze();
    const tid = document.getElementById("rb-template").value || "classic-chronological";
    st.textContent = "Building PDF…";
    const res = await fetch(api + "/api/resume-builder/pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        template_id: tid,
        resume,
        keyword_line: lastRbKeywords || "",
      }),
    });
    if (!res.ok) {
      let msg = "PDF export failed.";
      try {
        const j = await res.json();
        if (j.error) msg = j.error;
      } catch (_) {}
      st.textContent = msg;
      return;
    }
    const blob = await res.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "clear-resume-preview.pdf";
    a.click();
    URL.revokeObjectURL(a.href);
    st.textContent = "PDF downloaded.";
  });

  // --- Interview ---
  document.getElementById("iv-run").addEventListener("click", async () => {
    const st = document.getElementById("iv-status");
    st.textContent = "Generating…";
    const res = await fetch(api + "/api/interview-prep", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        job_description: document.getElementById("iv-jd").value.trim(),
        resume: document.getElementById("iv-resume").value.trim(),
        company_name: document.getElementById("iv-company").value.trim(),
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      st.textContent = data.error || "Error";
      return;
    }
    st.textContent = "";
    const beh = data.behavioral_questions || [];
    const tech = data.technical_questions || [];
    let html = "<h3>Behavioral (5)</h3>";
    beh.forEach((b, i) => {
      html += `<div class="cr-iv-q"><h4>${i + 1}. ${escapeHtml(b.question || "")}</h4>`;
      html += `<p><strong>Framework:</strong> ${escapeHtml(b.answer_framework || "")}</p>`;
      html += `<p><strong>Technique:</strong> ${escapeHtml(b.technique || "")}</p>`;
      html += `<p><strong>Keep in mind:</strong> ${escapeHtml(b.reminders || "")}</p></div>`;
    });
    html += "<h3>Technical (10)</h3>";
    tech.forEach((b, i) => {
      html += `<div class="cr-iv-q"><h4>${i + 1}. ${escapeHtml(b.question || "")}</h4>`;
      if (b.sample_answer_points) {
        html += "<ul>" + b.sample_answer_points.map((p) => "<li>" + escapeHtml(p) + "</li>").join("") + "</ul>";
      }
      html += `<p><strong>Technique:</strong> ${escapeHtml(b.technique || "")}</p>`;
      html += `<p><strong>Keep in mind:</strong> ${escapeHtml(b.reminders || "")}</p></div>`;
    });
    html += "<h3>General tips</h3><ul>" + (data.general_interview_tips || []).map((t) => "<li>" + escapeHtml(t) + "</li>").join("") + "</ul>";
    document.getElementById("iv-out").classList.remove("hidden");
    document.getElementById("iv-out").innerHTML = html;
  });

  // --- Account profile state ---
  let profileState = {
    skills: [],
    desired_roles: [],
    education: [],
    experience: [],
  };

  function renderTags(containerId, arr, onRemove) {
    const el = document.getElementById(containerId);
    el.innerHTML = "";
    arr.forEach((tag, idx) => {
      const s = document.createElement("span");
      s.className = "cr-tag";
      s.textContent = tag;
      const x = document.createElement("button");
      x.type = "button";
      x.textContent = "×";
      x.onclick = () => onRemove(idx);
      s.appendChild(x);
      el.appendChild(s);
    });
  }

  function addEduRow(entry) {
    const wrap = document.createElement("div");
    wrap.className = "cr-repeat-block";
    wrap.innerHTML = `
      <input type="text" class="cr-input edu-degree" placeholder="Degree" value="${escapeAttr(entry?.degree || "")}" />
      <input type="text" class="cr-input edu-spec" placeholder="Specialization" value="${escapeAttr(entry?.specialization || "")}" />
      <label class="cr-check"><input type="checkbox" class="edu-done" ${entry?.completed ? "checked" : ""} /> Completed</label>
      <input type="month" class="cr-input edu-start" value="${escapeAttr(entry?.start_date || "")}" />
      <input type="month" class="cr-input edu-end" value="${escapeAttr(entry?.end_date || "")}" />
      <button type="button" class="cr-btn-ghost sm edu-rm">Remove</button>
    `;
    wrap.querySelector(".edu-rm").onclick = () => wrap.remove();
    document.getElementById("edu-rows").appendChild(wrap);
  }

  function addExpRow(entry) {
    const wrap = document.createElement("div");
    wrap.className = "cr-repeat-block cr-exp";
    const sw = entry?.still_working ? "checked" : "";
    wrap.innerHTML = `
      <input type="text" class="cr-input exp-company" placeholder="Company" value="${escapeAttr(entry?.company || "")}" />
      <input type="text" class="cr-input exp-title" placeholder="Job title" value="${escapeAttr(entry?.title || "")}" />
      <input type="month" class="cr-input exp-start" value="${escapeAttr(entry?.start_date || "")}" />
      <div class="cr-exp-end-wrap">
        <input type="month" class="cr-input exp-end" value="${escapeAttr(entry?.end_date || "")}" />
        <label class="cr-check"><input type="checkbox" class="exp-current" ${sw} /> Still working here</label>
      </div>
      <textarea class="cr-textarea exp-desc cr-span-2" rows="2" placeholder="Description">${escapeHtml(entry?.description || "")}</textarea>
      <button type="button" class="cr-btn-ghost sm exp-rm">Remove</button>
    `;
    const end = wrap.querySelector(".exp-end");
    const cur = wrap.querySelector(".exp-current");
    function syncEnd() {
      end.disabled = cur.checked;
      end.style.opacity = cur.checked ? "0.45" : "1";
    }
    cur.addEventListener("change", syncEnd);
    syncEnd();
    wrap.querySelector(".exp-rm").onclick = () => wrap.remove();
    document.getElementById("exp-rows").appendChild(wrap);
  }

  function collectProfileFromForm() {
    const edu = [];
    document.querySelectorAll("#edu-rows .cr-repeat-block").forEach((row) => {
      edu.push({
        degree: row.querySelector(".edu-degree").value.trim(),
        specialization: row.querySelector(".edu-spec").value.trim(),
        completed: row.querySelector(".edu-done").checked,
        start_date: row.querySelector(".edu-start").value,
        end_date: row.querySelector(".edu-end").value,
      });
    });
    const exp = [];
    document.querySelectorAll("#exp-rows .cr-repeat-block").forEach((row) => {
      exp.push({
        company: row.querySelector(".exp-company").value.trim(),
        title: row.querySelector(".exp-title").value.trim(),
        start_date: row.querySelector(".exp-start").value,
        end_date: row.querySelector(".exp-current").checked ? "" : row.querySelector(".exp-end").value,
        still_working: row.querySelector(".exp-current").checked,
        description: row.querySelector(".exp-desc").value.trim(),
      });
    });
    return {
      first_name: document.getElementById("pf-first").value.trim(),
      last_name: document.getElementById("pf-last").value.trim(),
      email: document.getElementById("pf-email").value.trim(),
      phone_country_code: document.getElementById("pf-phone-cc").value.trim(),
      phone: document.getElementById("pf-phone").value.trim(),
      address: document.getElementById("pf-address").value.trim(),
      city: document.getElementById("pf-city").value.trim(),
      state: document.getElementById("pf-state").value.trim(),
      zip_code: document.getElementById("pf-zip").value.trim(),
      profile_summary: document.getElementById("pf-summary").value.trim(),
      birthdate: document.getElementById("pf-birth").value,
      gender: document.getElementById("pf-gender").value,
      education: edu,
      experience: exp,
      skills: profileState.skills,
      desired_roles: profileState.desired_roles,
    };
  }

  function mergeParsedIntoProfile(cur, parsed) {
    const out = { ...cur };
    const scalarKeys = [
      "first_name",
      "last_name",
      "email",
      "phone_country_code",
      "phone",
      "address",
      "city",
      "state",
      "zip_code",
      "profile_summary",
    ];
    for (const k of scalarKeys) {
      const v = parsed[k];
      const c = out[k];
      if (v != null && String(v).trim() !== "" && (!c || String(c).trim() === "")) {
        out[k] = v;
      }
    }
    if ((!out.education || !out.education.length) && parsed.education?.length) {
      out.education = parsed.education;
    }
    if ((!out.experience || !out.experience.length) && parsed.experience?.length) {
      out.experience = parsed.experience;
    }
    return out;
  }

  function applyProfileToForm(p) {
    document.getElementById("pf-first").value = p.first_name || "";
    document.getElementById("pf-last").value = p.last_name || "";
    document.getElementById("pf-email").value = p.email || "";
    document.getElementById("pf-phone-cc").value = p.phone_country_code || "";
    document.getElementById("pf-phone").value = p.phone || "";
    document.getElementById("pf-address").value = p.address || "";
    document.getElementById("pf-city").value = p.city || "";
    document.getElementById("pf-state").value = p.state || "";
    document.getElementById("pf-zip").value = p.zip_code || "";
    document.getElementById("pf-summary").value = p.profile_summary || "";
    document.getElementById("pf-birth").value = p.birthdate || "";
    document.getElementById("pf-gender").value = p.gender || "";
    profileState.skills = Array.isArray(p.skills) ? p.skills.slice(0, 20) : [];
    profileState.desired_roles = Array.isArray(p.desired_roles) ? p.desired_roles.slice(0, 5) : [];
    rerenderSkillTags();
    rerenderRoleTags();
    document.getElementById("edu-rows").innerHTML = "";
    (p.education || []).forEach((e) => addEduRow(e));
    document.getElementById("exp-rows").innerHTML = "";
    (p.experience || []).forEach((e) => addExpRow(e));
  }

  async function loadAccountPage() {
    const me = await refreshAuth();
    if (!me.authenticated) {
      els.accountGuest.classList.remove("hidden");
      els.accountFormWrap.classList.add("hidden");
      return;
    }
    els.accountGuest.classList.add("hidden");
    els.accountFormWrap.classList.remove("hidden");
    const res = await fetch(api + "/api/profile", { credentials: "include" });
    const data = await res.json();
    applyProfileToForm(data.profile || {});
    els.profilePct.textContent = (data.profile_completion_percent || 0) + "%";
    els.profileMeterFill.style.width = (data.profile_completion_percent || 0) + "%";
    await refreshResumeList();
    await fillSavedSelect("jf-resume-saved");
    await fillSavedSelect("rb-resume-saved");
  }

  async function refreshResumeList() {
    const res = await fetch(api + "/api/resumes", { credentials: "include" });
    const data = await res.json();
    const ul = document.getElementById("resume-list");
    ul.innerHTML = "";
    (data.resumes || []).forEach((r) => {
      const li = document.createElement("li");
      li.className = "cr-resume-li";
      li.innerHTML = `<span>${r.is_primary ? "★ " : ""}${escapeHtml(r.display_name)}</span>`;
      const p = document.createElement("button");
      p.type = "button";
      p.className = "cr-btn-ghost sm";
      p.textContent = "Set primary";
      p.onclick = async () => {
        await fetch(api + "/api/resumes/" + r.id + "/primary", { method: "PATCH", credentials: "include" });
        loadAccountPage();
      };
      const d = document.createElement("button");
      d.type = "button";
      d.className = "cr-btn-ghost sm";
      d.textContent = "Delete";
      d.onclick = async () => {
        if (!confirm("Delete this resume?")) return;
        await fetch(api + "/api/resumes/" + r.id, { method: "DELETE", credentials: "include" });
        loadAccountPage();
      };
      li.appendChild(p);
      li.appendChild(d);
      ul.appendChild(li);
    });
  }

  document.getElementById("pf-save").addEventListener("click", async () => {
    const st = document.getElementById("pf-status");
    st.textContent = "Saving…";
    const body = { profile: collectProfileFromForm() };
    const res = await fetch(api + "/api/profile", {
      method: "PUT",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) {
      st.textContent = data.error || "Error";
      return;
    }
    st.textContent = "Saved.";
    els.profilePct.textContent = data.profile_completion_percent + "%";
    els.profileMeterFill.style.width = data.profile_completion_percent + "%";
  });

  document.getElementById("pf-logout").addEventListener("click", async () => {
    await fetch(api + "/api/auth/logout", { method: "POST", credentials: "include" });
    refreshAuth();
    showPage("home");
  });

  document.getElementById("pf-delete").addEventListener("click", async () => {
    if (!confirm("Permanently delete your account and data?")) return;
    await fetch(api + "/api/auth/account", { method: "DELETE", credentials: "include" });
    refreshAuth();
    showPage("home");
  });

  document.getElementById("up-resume-btn").addEventListener("click", async () => {
    const fd = new FormData();
    fd.append("display_name", document.getElementById("up-resume-name").value.trim() || "Resume");
    const f = document.getElementById("up-resume-file").files[0];
    if (!f) {
      alert("Choose a file.");
      return;
    }
    fd.append("file", f);
    fd.append("is_primary", "false");
    const res = await fetch(api + "/api/resumes", { method: "POST", body: fd, credentials: "include" });
    if (!res.ok) {
      const e = await res.json();
      alert(e.error || "Upload failed");
      return;
    }
    const uploadData = await res.json();
    document.getElementById("up-resume-file").value = "";
    const parsed = uploadData.parsed_profile || {};
    const profRes = await fetch(api + "/api/profile", { credentials: "include" });
    if (profRes.ok) {
      const profData = await profRes.json();
      const merged = mergeParsedIntoProfile(profData.profile || {}, parsed);
      if (Object.keys(parsed).length) {
        const saveRes = await fetch(api + "/api/profile", {
          method: "PUT",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ profile: merged }),
        });
        const saveData = await saveRes.json();
        const st = document.getElementById("pf-status");
        if (saveRes.ok) {
          st.textContent = "Resume uploaded — filled empty fields from the file (saved).";
          if (els.profilePct && saveData.profile_completion_percent != null) {
            els.profilePct.textContent = saveData.profile_completion_percent + "%";
            els.profileMeterFill.style.width = saveData.profile_completion_percent + "%";
          }
        } else {
          st.textContent = saveData.error || "Could not auto-save; click Save after review.";
        }
      }
    }
    await loadAccountPage();
  });

  document.getElementById("edu-add").addEventListener("click", () => addEduRow({}));
  document.getElementById("exp-add").addEventListener("click", () => addExpRow({}));

  async function loadMetaSkills(q) {
    const res = await fetch(api + "/api/meta/skills?q=" + encodeURIComponent(q));
    const data = await res.json();
    skillsCache = data.skills || [];
    const dl = document.getElementById("skill-datalist");
    dl.innerHTML = "";
    skillsCache.forEach((s) => {
      const o = document.createElement("option");
      o.value = s;
      dl.appendChild(o);
    });
  }
  async function loadMetaRoles(q) {
    const res = await fetch(api + "/api/meta/job-roles?q=" + encodeURIComponent(q));
    const data = await res.json();
    rolesCache = data.roles || [];
    const dl = document.getElementById("role-datalist");
    dl.innerHTML = "";
    rolesCache.forEach((s) => {
      const o = document.createElement("option");
      o.value = s;
      dl.appendChild(o);
    });
  }

  document.getElementById("skill-search").addEventListener("focus", () => loadMetaSkills(""));
  document.getElementById("skill-search").addEventListener("input", (e) => loadMetaSkills(e.target.value));
  document.getElementById("role-search").addEventListener("focus", () => loadMetaRoles(""));
  document.getElementById("role-search").addEventListener("input", (e) => loadMetaRoles(e.target.value));

  document.getElementById("skill-add").addEventListener("click", () => {
    const v = document.getElementById("skill-search").value.trim();
    if (!v || profileState.skills.length >= 20) return;
    if (!profileState.skills.includes(v)) profileState.skills.push(v);
    document.getElementById("skill-search").value = "";
    rerenderSkillTags();
  });

  document.getElementById("role-add").addEventListener("click", () => {
    const v = document.getElementById("role-search").value.trim();
    if (!v || profileState.desired_roles.length >= 5) return;
    if (!profileState.desired_roles.includes(v)) profileState.desired_roles.push(v);
    document.getElementById("role-search").value = "";
    rerenderRoleTags();
  });

  // --- Auth forms ---
  document.getElementById("form-login").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const res = await fetch(api + "/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: fd.get("email"), password: fd.get("password") }),
      credentials: "include",
    });
    const data = await res.json();
    if (!res.ok) {
      alert(data.error || "Login failed");
      return;
    }
    closeAuth();
    refreshAuth();
  });

  document.getElementById("form-signup").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const res = await fetch(api + "/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: fd.get("email"), password: fd.get("password") }),
      credentials: "include",
    });
    const data = await res.json();
    if (!res.ok) {
      alert(data.error || "Sign up failed");
      return;
    }
    closeAuth();
    refreshAuth();
  });

  document.querySelectorAll("[data-close-auth]").forEach((el) => el.addEventListener("click", closeAuth));
  document.querySelectorAll(".cr-auth-tab").forEach((t) => {
    t.addEventListener("click", () => openAuth(t.dataset.authTab));
  });
  els.btnOpenLogin.addEventListener("click", () => openAuth("login"));
  els.btnOpenSignup.addEventListener("click", () => openAuth("signup"));
  document.getElementById("hero-signup").addEventListener("click", () => openAuth("signup"));
  document.getElementById("hero-login").addEventListener("click", () => openAuth("login"));
  document.getElementById("account-login-cta").addEventListener("click", () => openAuth("login"));
  els.btnLogout.addEventListener("click", async () => {
    await fetch(api + "/api/auth/logout", { method: "POST", credentials: "include" });
    refreshAuth();
  });

  document.querySelectorAll("[data-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-toggle");
      const inp = document.getElementById(id);
      inp.type = inp.type === "password" ? "text" : "password";
    });
  });

  document.getElementById("forgot-link").addEventListener("click", (e) => {
    e.preventDefault();
    openForgotPassword();
  });

  document.getElementById("forgot-back").addEventListener("click", () => openAuth("login"));

  document.getElementById("form-forgot").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("forgot-email").value.trim();
    const st = document.getElementById("forgot-status");
    st.textContent = "Sending…";
    const res = await fetch(api + "/api/auth/forgot-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    const data = await res.json();
    if (!res.ok) {
      st.textContent = data.error || "Request failed.";
      return;
    }
    st.textContent = data.message || "Check your email for the reset link.";
  });

  document.getElementById("form-reset").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("reset-email").value;
    const token = document.getElementById("reset-token").value;
    const password = document.getElementById("reset-password").value;
    const st = document.getElementById("reset-status");
    st.textContent = "Updating…";
    const res = await fetch(api + "/api/auth/reset-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, token, password }),
      credentials: "include",
    });
    const data = await res.json();
    if (!res.ok) {
      st.textContent = data.error || "Reset failed.";
      return;
    }
    st.textContent = data.message || "Success.";
    closeAuth();
    refreshAuth();
  });

  // --- Nav ---
  els.navItems().forEach((b) => b.addEventListener("click", () => showPage(b.dataset.nav)));
  document.querySelectorAll("[data-goto]").forEach((b) =>
    b.addEventListener("click", () => showPage(b.getAttribute("data-goto")))
  );

  fetch(api + "/api/resume-templates")
    .then((r) => r.json())
    .then((d) => {
      const sel = document.getElementById("rb-template");
      if (!sel || !d.templates) return;
      sel.innerHTML = "";
      d.templates.forEach((t) => {
        const o = document.createElement("option");
        o.value = t.id;
        o.textContent = t.name;
        sel.appendChild(o);
      });
    })
    .catch(() => {});

  bindTabs("jf-resume");
  bindTabs("jf-job");
  bindTabs("rb-res");

  document.getElementById("jf-resume-saved").addEventListener("change", () =>
    loadResumeIntoField("jf-resume-saved", "jf-resume-text")
  );
  document.getElementById("rb-resume-saved").addEventListener("change", () =>
    loadResumeIntoField("rb-resume-saved", "rb-resume-text")
  );

  refreshAuth();
  showPage("home");

  const params = new URLSearchParams(window.location.search);
  const authErr = params.get("auth_error");
  if (authErr) {
    const hint =
      authErr.startsWith("linkedin")
        ? "LinkedIn sign-in failed. Check LINKEDIN_OAUTH_* and redirect URL in LinkedIn Developer Portal."
        : "Sign-in did not complete. Check Google OAuth client ID, secret, and redirect URI.";
    alert(hint);
    history.replaceState({}, "", "/");
  }
  const rt = params.get("reset_token");
  const rEmail = params.get("email");
  if (rt && rEmail) {
    openResetPasswordView(decodeURIComponent(rEmail), rt);
    history.replaceState({}, "", "/");
  }
  if (params.get("signed_in")) {
    history.replaceState({}, "", "/");
    refreshAuth();
  }
})();

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

  const apiBase = "";

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
      const res = await fetch(apiBase + "/api/analyze", { method: "POST", body: formData });

      const data = await res.json();

      if (!res.ok) {
        setStatus(data.error || "Something went wrong.", true);
        return;
      }

      resultsEl.classList.remove("hidden");
      compatValue.textContent = data.compatibility_score;
      chanceValue.textContent = data.selection_chance;
      setRing(compatRing, data.compatibility_score);
      setRing(chanceRing, data.selection_chance);
      matchedCountEl.textContent = data?.summary?.matched_count ?? "—";
      requiredCountEl.textContent = data?.summary?.required_count ?? "—";
      gapCountEl.textContent = data?.summary?.gap_count ?? "—";
      renderSkillList(strongList, data.strong_skills || []);
      renderSkillList(improveList, data.skills_to_improve || []);
      renderSkillList(otherList, data.other_relevant_skills || []);
      fitSummaryEl.textContent = data.fit_summary || "—";
      renderCategoryStack(alignmentListEl, data.major_alignment || []);
      renderCategoryStack(gapsListEl, data.major_gaps || []);
      renderTopics(topicsListEl, data.topics_to_prepare || []);
      setStatus("");
    } catch (err) {
      setStatus("Network error. Is the server running?", true);
    } finally {
      analyzeBtn.disabled = false;
    }
  });

  initTabs();
  setMode("resume", "paste");
  setMode("job", "paste");
  resetUI();
})();

/* ResumeMatch AI — frontend logic (vanilla, no build step) */
(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const state = { lastResult: null };

  /* ---------- theme ---------- */
  const themeBtn = $("themeBtn");
  const savedTheme = localStorage.getItem("rm-theme");
  if (savedTheme) document.documentElement.dataset.theme = savedTheme;
  themeBtn.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("rm-theme", next);
  });

  /* ---------- token ---------- */
  const tokenInput = $("tokenInput");
  tokenInput.value = localStorage.getItem("rm-token") || "";
  tokenInput.addEventListener("change", () => {
    localStorage.setItem("rm-token", tokenInput.value.trim());
  });

  /* ---------- toast ---------- */
  let toastTimer = null;
  function toast(msg) {
    const el = $("toast");
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("show"), 4200);
  }

  /* ---------- drag & drop ---------- */
  const dropzone = $("dropzone");
  const resumeInput = $("resumeInput");

  ["dragenter", "dragover"].forEach((ev) =>
    dropzone.addEventListener(ev, (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    })
  );
  ["dragleave", "drop"].forEach((ev) =>
    dropzone.addEventListener(ev, (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
    })
  );
  dropzone.addEventListener("drop", async (e) => {
    const file = e.dataTransfer.files?.[0];
    if (!file) return;
    if (!/\.(txt|md|text)$/i.test(file.name)) {
      toast("请拖入 .txt 或 .md 文本文件（PDF 请先转文本）");
      return;
    }
    resumeInput.value = await file.text();
    toast(`已载入：${file.name}`);
  });

  /* ---------- sample ---------- */
  $("sampleBtn")?.addEventListener("click", () => {
    resumeInput.value =
      "张明，男，28岁。\n" +
      "学历：北京大学，计算机科学，硕士，2020年毕业。\n" +
      "工作经历：\n" +
      "- 2020-2023 字节跳动 算法工程师，负责推荐系统优化，使用 Python、PyTorch、Transformer，上线后CTR提升12%。\n" +
      "- 2023-至今 阿里云 高级算法工程师，负责LLM应用开发，精通LangGraph、RAG、向量数据库（Milvus）、Prompt Engineering。\n" +
      "技能：Python, PyTorch, LangGraph, RAG, Milvus, LLM, Prompt Engineering, 大模型微调, Docker, Kubernetes。\n" +
      "项目：独立完成一个基于LangGraph的AI客服Agent，支持多轮对话和工具调用，日均处理5000+请求。";
    toast("已填入示例简历");
  });

  /* ---------- match ---------- */
  const matchBtn = $("matchBtn");

  matchBtn.addEventListener("click", async () => {
    const text = resumeInput.value.trim();
    if (text.length < 10) {
      toast("请先粘贴简历文本（至少 10 个字符）");
      resumeInput.focus();
      return;
    }

    const includeAdvice = $("adviceToggle").checked;
    const token = (tokenInput.value || localStorage.getItem("rm-token") || "").trim();

    setLoading(true);
    try {
      const headers = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const res = await fetch("/api/v1/match", {
        method: "POST",
        headers,
        body: JSON.stringify({ resume_text: text, include_advice: includeAdvice }),
      });

      if (res.status === 401) throw new Error("鉴权失败：API Token 无效或未配置");
      if (!res.ok) {
        let detail = `HTTP ${res.status}`;
        try { detail = (await res.json()).detail || detail; } catch (_) {}
        throw new Error(detail);
      }

      const data = await res.json();
      state.lastResult = data;
      render(data, includeAdvice);
      toast("匹配完成");
      $("results").scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      toast(`匹配失败：${err.message}`);
    } finally {
      setLoading(false);
    }
  });

  function setLoading(on) {
    matchBtn.disabled = on;
    matchBtn.innerHTML = on
      ? '<span class="spinner"></span> 匹配中…'
      : '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h7l-1 8 10-12h-7l1-8Z"/></svg> 开始匹配';

    if (on) {
      $("results").classList.add("show");
      $("candidateCard").style.display = "none";
      $("matchesList").innerHTML =
        '<div class="skeleton"><div class="sk"></div><div class="sk"></div><div class="sk"></div><div class="sk"></div></div>';
      $("adviceTabs").style.display = "none";
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    }
  }

  /* ---------- render ---------- */
  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  function render(data, includeAdvice) {
    const c = data.candidate || {};
    const matches = data.matches || [];
    const expl = data.explanation || {};

    /* candidate */
    const initials = (c.name || "?").trim().slice(0, 1);
    const chips = (c.skills || []).map((s) => `<span class="chip">${escapeHtml(s)}</span>`).join("");
    $("candidateCard").innerHTML = `
      <div class="avatar">${escapeHtml(initials)}</div>
      <div>
        <div class="cand-name">${escapeHtml(c.name || "未知候选人")}</div>
        <div class="cand-role">${escapeHtml(c.career || "职业身份未识别")}</div>
        <div class="cand-meta">
          <span>🎓 ${escapeHtml(c.education || "—")}</span>
          <span>💼 ${Number(c.work_year) > 0 ? Number(c.work_year) + " 年经验" : "经验未知"}</span>
          <span>🧩 ${(c.skills || []).length} 项技能</span>
        </div>
        <div class="chips">${chips || '<span class="chip">暂无技能</span>'}</div>
        ${c.project ? `<div class="cand-project"><b>代表项目</b> · ${escapeHtml(c.project)}</div>` : ""}
      </div>`;
    $("candidateCard").style.display = "grid";

    /* matches */
    $("matchesList").innerHTML = matches
      .map((m, i) => {
        const sig = m.signals || {};
        const ring = scoreRing(m.score);
        const ej = (expl.per_job || []).find((p) => p.job === m.job) || {};
        const ejSkills = ej.skills || {};
        const chips = [
          ...(ejSkills.hit || []).slice(0, 6).map(
            (s) => `<span class="chip chip-hit" title="已命中">✓ ${escapeHtml(s)}</span>`
          ),
          ...(ejSkills.gap || []).slice(0, 6).map(
            (s) => `<span class="chip chip-gap" title="岗位要求，简历缺失">+ ${escapeHtml(s)}</span>`
          ),
        ].join("");
        return `
        <article class="match ${i === 0 ? "top" : ""}" style="animation-delay:${i * 55}ms">
          <div class="rank">${m.rank}</div>
          <div class="match-body">
            <div class="match-title">${escapeHtml(m.job)}</div>
            <div class="match-reason">${escapeHtml(m.reason || "")}</div>
            ${chips ? `<div class="match-skills">${chips}</div>` : ""}
            <div class="signals">
              ${signalBar("规则", sig.rule)}
              ${signalBar("LLM", sig.llm)}
              ${signalBar("重排", sig.rerank)}
              ${sig.career ? `<span class="signal">职业身份 <b>+${sig.career}</b></span>` : ""}
              ${sig.cap != null && sig.cap < 100 ? `<span class="signal">硬上限 <b>${sig.cap}</b></span>` : ""}
            </div>
          </div>
          ${ring}
        </article>`;
      })
      .join("");

    // animate bars + rings after paint
    requestAnimationFrame(() => {
      document.querySelectorAll(".signal .bar i").forEach((el) => {
        el.style.width = el.dataset.w + "%";
      });
      document.querySelectorAll(".score-ring").forEach((el) => {
        const pct = Number(el.dataset.pct) || 0;
        const circle = el.querySelector(".progress");
        if (circle) circle.style.strokeDashoffset = String(201 - (201 * pct) / 100);
      });
    });

    /* advice + explanation tabs */
    const parts =
      includeAdvice && data.advice ? splitAdvice(data.advice) : { advice: "", interview: "" };
    $("panel-advice").innerHTML = parts.advice
      ? `<pre>${escapeHtml(parts.advice)}</pre>`
      : '<div style="color:var(--muted);padding:4px">未生成优化建议</div>';
    $("panel-interview").innerHTML = parts.interview
      ? `<pre>${escapeHtml(parts.interview)}</pre>`
      : '<div style="color:var(--muted);padding:4px">未生成模拟面试题</div>';
    renderExplanation(expl, matches);
    $("panel-debug").innerHTML = renderDebug(matches);
    $("adviceTabs").style.display = "flex";
    activateTab(parts.advice ? "advice" : "explanation");
  }

  function scoreRing(score) {
    const pct = Math.max(0, Math.min(100, Number(score) || 0));
    return `
      <div class="score-ring" data-pct="${pct}">
        <svg width="74" height="74" viewBox="0 0 74 74">
          <circle class="track" cx="37" cy="37" r="32" fill="none" stroke-width="6"/>
          <circle class="progress" cx="37" cy="37" r="32" fill="none" stroke-width="6"/>
        </svg>
        <span class="num">${pct}</span>
      </div>`;
  }

  function signalBar(label, value) {
    if (value == null) return "";
    const v = Math.max(0, Math.min(100, Number(value) || 0));
    return `<span class="signal">${label}
      <span class="bar"><i data-w="${v}"></i></span>
      <b>${Math.round(v)}</b></span>`;
  }

  function splitAdvice(text) {
    const idx = text.indexOf("## 模拟面试题");
    if (idx === -1) return { advice: text, interview: "" };
    return {
      advice: text.slice(0, idx).replace(/^##\s*简历优化建议\s*/, "").trim(),
      interview: text.slice(idx).replace(/^##\s*模拟面试题\s*/, "").trim(),
    };
  }

    /* ---------- P12 可解释报告 ---------- */
    function renderExplanation(expl, matches) {
      const panel = $("panel-explanation");
      if (!panel) return;
      if (!expl.summary) {
        panel.innerHTML = '<div style="color:var(--muted);padding:4px">暂无解读</div>';
        return;
      }

      const rows = (expl.per_job || [])
        .map((p) => {
          const cells = [];
          if (p.verdict) cells.push(`<div class="x-verdict">${escapeHtml(p.verdict)}</div>`);
          if (p.career) cells.push(`<div>🧭 ${escapeHtml(p.career)}</div>`);
          if (p.years) cells.push(`<div>🕓 ${escapeHtml(p.years)}</div>`);
          if (p.education) cells.push(`<div>🎓 ${escapeHtml(p.education)}</div>`);
          if (p.cap) cells.push(`<div class="x-warn">⚠️ ${escapeHtml(p.cap)}</div>`);
          const chips = [
            ...(p.skills?.hit || []).map(
              (s) => `<span class="chip chip-hit">✓ ${escapeHtml(s)}</span>`
            ),
            ...(p.skills?.gap || []).map(
              (s) => `<span class="chip chip-gap">+ ${escapeHtml(s)}</span>`
            ),
          ].join("");
          return `<div class="x-row">
            <div class="x-job">${escapeHtml(p.job)}</div>
            ${cells.join("")}
            ${chips ? `<div class="chips" style="margin-top:10px">${chips}</div>` : ""}
          </div>`;
        })
        .join("");

      panel.innerHTML = `
        <div class="x-summary">${expl.summary
          .split("\n")
          .filter(Boolean)
          .map((s) => `<p>${escapeHtml(s)}</p>`)
          .join("")}</div>
        <div class="x-rows">${rows || '<div style="color:var(--muted)">暂无逐岗位分析</div>'}</div>`;
    }

    function renderDebug(matches) {
      const rows = matches
        .map((m) => {
          const s = m.signals || {};
          return `<tr>
            <td>${m.rank}</td><td>${escapeHtml(m.job)}</td><td>${m.score}</td>
            <td>${s.rule ?? "—"}</td><td>${s.llm ?? "—"}</td>
            <td>${s.rerank ?? "—"}</td><td>${s.career ?? 0}</td><td>${s.cap ?? "—"}</td>
          </tr>`;
        })
        .join("");
      return `<pre style="font-family:var(--font)">四信号明细（规则 / LLM / 重排 / 职业身份 / 硬上限）</pre>
        <div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:13px">
          <thead><tr style="color:var(--muted);text-align:left">
            <th style="padding:8px">#</th><th>岗位</th><th>最终</th><th>规则</th>
            <th>LLM</th><th>重排</th><th>身份</th><th>上限</th>
          </tr></thead>
          <tbody>${rows.replace(/<td/g, '<td style="padding:8px;border-top:1px solid var(--border)"')}</tbody>
        </table></div>`;
    }

  /* ---------- tabs ---------- */
  function activateTab(name) {
    document.querySelectorAll(".tab").forEach((t) =>
      t.classList.toggle("active", t.dataset.panel === name)
    );
    document.querySelectorAll(".tab-panel").forEach((p) =>
      p.classList.toggle("active", p.id === `panel-${name}`)
    );
  }
  $("adviceTabs")?.addEventListener("click", (e) => {
    const tab = e.target.closest(".tab");
    if (tab) activateTab(tab.dataset.panel);
  });
})();

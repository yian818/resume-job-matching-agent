/* ResumeMatch AI — 在线评测台 (P13, vanilla JS) */
(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const state = { timer: null };

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
  tokenInput.addEventListener("change", () =>
    localStorage.setItem("rm-token", tokenInput.value.trim())
  );
  function authHeaders(extra = {}) {
    const t = (tokenInput.value || localStorage.getItem("rm-token") || "").trim();
    return t ? { ...extra, Authorization: `Bearer ${t}` } : extra;
  }

  /* ---------- toast ---------- */
  let toastTimer = null;
  function toast(msg) {
    const el = $("toast");
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("show"), 4200);
  }

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  /* ---------- status ---------- */
  async function loadStatus() {
    try {
      const r = await fetch("/api/eval/status");
      const s = await r.json();
      if (s.building) {
        $("cacheSub").textContent = "构建中…（后台运行，完成后自动刷新）";
        setTimeout(loadStatus, 3000);
        return;
      }
      if (s.has_cache) {
        $("cacheSub").innerHTML =
          `已缓存 <b>${s.cache_n}</b> / ${s.total} 份` +
          (s.built_at ? ` · 构建于 ${escapeHtml(s.built_at)}` : "") +
          (s.config?.temperature != null ? ` · temp=${escapeHtml(s.config.temperature)}` : "");
        simulate();
      } else {
        $("cacheSub").textContent = "尚未构建缓存 —— 先点右侧按钮跑一次评测";
      }
    } catch (e) {
      $("cacheSub").textContent = "状态读取失败：" + e.message;
    }
  }

  /* ---------- build ---------- */
  async function build(limit) {
    try {
      const r = await fetch(`/api/eval/build?limit=${limit}&force=true`, {
        method: "POST",
        headers: authHeaders(),
      });
      if (r.status === 401) return toast("鉴权失败：请在右上角填写 API Token");
      if (!r.ok) {
        let d = `HTTP ${r.status}`;
        try { d = (await r.json()).detail || d; } catch (_) {}
        return toast("构建失败：" + d);
      }
      toast(`已开始构建（${limit} 份），后台运行中…`);
      $("cacheSub").textContent = "构建中…（后台运行，完成后自动刷新）";
      setTimeout(loadStatus, 1500);
    } catch (e) {
      toast("构建失败：" + e.message);
    }
  }
  $("build10Btn").addEventListener("click", () => build(10));
  $("buildBtn").addEventListener("click", () => build(50));

  /* ---------- weights ---------- */
  const sliders = { rule: $("wRule"), llm: $("wLlm"), rerank: $("wRerank") };
  const outputs = { rule: $("wRuleVal"), llm: $("wLlmVal"), rerank: $("wRerankVal") };

  function rawWeights() {
    return {
      rule: Number(sliders.rule.value),
      llm: Number(sliders.llm.value),
      rerank: Number(sliders.rerank.value),
    };
  }
  function normalizedWeights() {
    const w = rawWeights();
    let total = w.rule + w.llm + w.rerank;
    if (total <= 0) { w.rule = 0.4; w.llm = 0.3; w.rerank = 0.3; total = 1; }
    return { rule: w.rule / total, llm: w.llm / total, rerank: w.rerank / total };
  }
  function syncLabels() {
    const w = rawWeights();
    outputs.rule.textContent = w.rule.toFixed(2);
    outputs.llm.textContent = w.llm.toFixed(2);
    outputs.rerank.textContent = w.rerank.toFixed(2);
    const n = normalizedWeights();
    $("weightNote").textContent =
      `实际权重：规则 ${(n.rule * 100).toFixed(0)}% · LLM ${(n.llm * 100).toFixed(0)}% · 重排 ${(n.rerank * 100).toFixed(0)}%` +
      "（自动归一化，分数仍为 0-100 量纲）";
  }

  /* ---------- simulate ---------- */
  async function simulate() {
    const w = normalizedWeights();
    const useCap = $("capToggle").checked ? 1 : 0;
    const url =
      `/api/eval/simulate?w_rule=${w.rule.toFixed(3)}&w_llm=${w.llm.toFixed(3)}` +
      `&w_rerank=${w.rerank.toFixed(3)}&use_cap=${useCap}`;
    try {
      const r = await fetch(url, { headers: authHeaders() });
      if (r.status === 401) return toast("鉴权失败：请在右上角填写 API Token");
      if (r.status === 404) {
        $("cacheSub").textContent = "缓存未构建 —— 先点右侧按钮跑一次评测";
        return;
      }
      if (!r.ok) return toast("模拟失败：HTTP " + r.status);
      const data = await r.json();
      renderMetrics(data.metrics);
      renderFailures(data.failures);
    } catch (e) {
      toast("模拟失败：" + e.message);
    }
  }

  function debouncedSimulate() {
    clearTimeout(state.timer);
    state.timer = setTimeout(simulate, 120);
  }

  Object.values(sliders).forEach((el) => {
    el.addEventListener("input", () => { syncLabels(); debouncedSimulate(); });
  });
  $("capToggle").addEventListener("change", simulate);

  const PRESETS = {
    prod: [0.4, 0.3, 0.3],
    rule: [1, 0, 0],
    llm: [0, 1, 0],
    rerank: [0, 0, 1],
  };
  document.querySelectorAll(".preset").forEach((btn) => {
    btn.addEventListener("click", () => {
      const [a, b, c] = PRESETS[btn.dataset.preset] || PRESETS.prod;
      sliders.rule.value = a;
      sliders.llm.value = b;
      sliders.rerank.value = c;
      syncLabels();
      simulate();
    });
  });

  /* ---------- render metrics ---------- */
  function animateNumber(el, to, fmt) {
    const from = parseFloat(el.dataset.v || "0");
    el.dataset.v = String(to);
    const t0 = performance.now();
    function step(t) {
      const k = Math.min(1, (t - t0) / 420);
      const v = from + (to - from) * k;
      el.textContent = fmt(v);
      if (k < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function renderMetrics(m) {
    animateNumber($("mTop1"), m.top1 * 100, (v) => v.toFixed(1) + "%");
    animateNumber($("mTop3"), m.top3 * 100, (v) => v.toFixed(1) + "%");
    animateNumber($("mMrr"), m.mrr, (v) => v.toFixed(3));
    animateNumber($("mNdcg"), m.ndcg3, (v) => v.toFixed(3));
    animateNumber($("mRecall"), m.recall * 100, (v) => v.toFixed(1) + "%");
  }

  function renderFailures(fails) {
    const list = fails || [];
    $("failSub").textContent = list.length
      ? `${list.length} 份标答未进 Top-1`
      : "当前权重下，全部命中 Top-1";
    if (!list.length) {
      $("failTable").innerHTML = '<div class="eval-ok">✓ 当前权重下，所有标答都在 Top-1。</div>';
      return;
    }
    const rows = list.map((f) => `<tr>
      <td>${escapeHtml(f.rid)}</td>
      <td>${escapeHtml(f.truth)}</td>
      <td>${escapeHtml(f.top1)}</td>
      <td>${f.truth_rank >= 1 ? f.truth_rank : "召回漏"}</td>
    </tr>`).join("");
    $("failTable").innerHTML = `<table class="eval-table">
      <thead><tr><th>简历</th><th>标答岗位</th><th>当前 Top-1</th><th>标答排名</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
  }

  /* ---------- stability ---------- */
  async function loadStability() {
    // 默认先加载 before2（temp0.1 = 生产默认配置的报告），再试 after / before
    for (const tag of ["before2", "after", "before"]) {
      try {
        const r = await fetch(`/api/eval/stability?tag=${tag}`);
        const d = await r.json();
        if (!d.error) return renderStability(d);
      } catch (_) { /* try next */ }
    }
    toast("未找到稳定性报告，请先运行 eval/stability_eval.py");
  }
  $("stabBtn").addEventListener("click", loadStability);

  function renderStability(d) {
    const s = d.summary || {};
    const nCases = s.labeled_cases ?? s.cases ?? 0;
    $("stabSub").textContent =
      `${nCases} 份标答 × ${d.runs || 0} 次 · 翻转率 ${((s.flip_rate || 0) * 100).toFixed(0)}%` +
      ` · 标答跨重复命中率 ${((s.avg_label_rank1_rate || 0) * 100).toFixed(0)}%` +
      (s.sample_stable != null ? ` · 张明压测${s.sample_stable ? "稳定" : "翻转"}` : "") +
      ` · 报告：${escapeHtml(d.tag || "")}`;
    const rows = (d.cases || []).map((c) => `<tr>
      <td>${escapeHtml(c.rid)}</td>
      <td>${escapeHtml(c.truth || "—")}</td>
      <td>${c.stable ? '<span class="tag-ok">稳定</span>' : '<span class="tag-warn">翻转</span>'}</td>
      <td>${(c.top1_bare || []).map(escapeHtml).join(" / ")}</td>
      <td>${c.score_spread ?? "—"}</td>
    </tr>`).join("");
    $("stabBody").innerHTML = `<table class="eval-table">
      <thead><tr><th>简历</th><th>标答</th><th>结论</th><th>各次 Top-1</th><th>分数波动</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
  }

  /* ---------- init ---------- */
  syncLabels();
  loadStatus();
})();

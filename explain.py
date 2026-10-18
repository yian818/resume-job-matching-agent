# explain.py - 可解释报告层（P12）
#
# 背景：四信号融合把每个岗位算出了分数，但用户看到的是"86 分"这个数字，
# 不知道它怎么来的、缺什么、为什么不是另一个岗位。P12 把数字翻译成人话。
#
# 原则（关键）：解释层的事实**全部确定性计算**，不经过 LLM 措辞发挥。
#   - 技能重合/缺口   → skill_overlap（规则引擎）
#   - 职业身份/年限/学历/硬上限 → career_match_score / EDU_RANK / hard_cap
#   - 总评段落        → 模板 + 事实拼接
#
# 面试点：可解释性本身也要可解释——解释层的每一句话都能追溯到一行代码算出来的
# 事实，不存在"模型编了个漂亮理由"的风险。这是和"让 LLM 解释自己"最本质的区别。

from scoring_rules import (
    skill_overlap,
    _normalize_skill,
    career_match_score,
    hard_cap,
    compute_rule_score,
    EDU_RANK,
)


def _resolve(db: dict, title: str):
    """标题可能带部门后缀，剥掉再查岗位库。"""
    bare = title.split("（")[0].strip()
    return db.get(bare) or db.get(title)


def _norm2orig(items):
    """把技能列表建成 {归一化词: 原文} 映射，展示时保留原文不丢信息。"""
    m = {}
    for it in items:
        s = (it or "").strip()
        if s:
            m.setdefault(_normalize_skill(s), s)
    return m


def hit_gap_skills(job: dict, resume_info: dict):
    """
    技能重合（用候选人自己的写法展示）与硬性缺口（岗位要求的、候选人没有的）。

    缺口只取岗位的**原始 required_skills**，不取 JOB_SKILL_EXPANSION 扩充域——
    扩充域是算法补的行业知识，拿来当"你必须会"的缺口不够客观。
    """
    resume = resume_info.get("skill", []) or []
    rmap = _norm2orig(resume)
    req_tokens = (job.get("required_skills") or "").split(",")
    jmap = _norm2orig(req_tokens)

    overlap = skill_overlap(job, resume_info)  # 归一化后的重合集合

    hits = []
    for n in sorted(overlap):
        hits.append(rmap.get(n) or jmap.get(n) or n)

    req_set = {_normalize_skill(s) for s in req_tokens if s.strip()}
    gaps = [jmap.get(n, n) for n in sorted(req_set - overlap)]
    return hits, gaps


def verdict_of(score: int) -> str:
    if score >= 80:
        return "强匹配"
    if score >= 65:
        return "中等匹配"
    if score >= 50:
        return "边缘匹配"
    return "不匹配"


def _career_line(info: dict, job: dict) -> str:
    c = (info.get("career") or "").strip()
    if not c:
        return "职业身份未知"
    if career_match_score(job, info) == 20:
        return f"职业身份「{c}」与岗位职能匹配（+20 确定性加分）"
    return f"职业身份「{c}」与岗位职能不匹配"


def _years_line(info: dict, job: dict) -> str:
    y = info.get("work_year") or 0
    req = job.get("required_years", 1)
    if y <= 0:
        return "工作年限未知"
    if y >= req:
        return f"工作年限 {y} 年 ≥ 要求 {req} 年"
    return f"工作年限 {y} 年 < 要求 {req} 年（差 {req - y} 年）"


def _edu_line(info: dict, job: dict) -> str:
    e = (info.get("education") or "").strip()
    req = job.get("education", "本科")
    if not e:
        return "学历未知"
    if EDU_RANK.get(e, 0) >= EDU_RANK.get(req, 1):
        return f"学历 {e} ≥ 要求 {req}"
    return f"学历 {e} < 要求 {req}"


def _cap_line(job: dict, info: dict) -> str:
    """只有被硬上限压过才解释；cap=100 时无事可说。"""
    cap = hard_cap(job, info)
    if cap >= 100:
        return ""
    n = len(skill_overlap(job, info))
    return f"硬上限 {cap}：核心技能重合仅 {n} 项，总分被物理压到 {cap} 以下"


def _rerank100(s: dict):
    r = s.get("rerank_score")
    return round(float(r) * 100, 1) if r is not None else None


def _build_summary(top: dict, job: dict, info: dict, hits, gaps) -> str:
    """Top-1 总评：模板 + 确定性事实拼接，不经过 LLM。"""
    name = (info.get("name") or "").strip() or "候选人"
    career = (info.get("career") or "").strip() or "未识别"
    score = top.get("final_score", top.get("score", 0))

    lines = [
        f"{name}的职业身份是「{career}」，与 Top-1 岗位「{job['title']}」最终匹配分 "
        f"{score}（{verdict_of(score)}）。"
    ]

    if hits:
        lines.append(f"技能重合 {len(hits)} 项：{'、'.join(hits[:6])}。")
    if gaps:
        lines.append(f"硬性缺口 {len(gaps)} 项：{'、'.join(gaps[:4])}——补齐可明显提分。")
    if career_match_score(job, info) == 20:
        lines.append("职业身份与岗位职能类别一致，拿到 +20 确定性加分。")

    # 三路信号一致度：规则 / LLM / 重排
    vals = []
    rule_v = top.get("rule_score") or compute_rule_score(job, info)
    for label, v in (("规则", rule_v), ("LLM", top.get("llm_score")), ("重排", _rerank100(top))):
        if v is not None:
            vals.append((label, float(v)))
    if len(vals) >= 2:
        vs = [v for _, v in vals]
        spread = max(vs) - min(vs)
        if spread <= 12:
            lines.append(f"规则/LLM/重排三路信号落在 {round(spread)} 分以内，结论稳健。")
        else:
            low = min(vals, key=lambda x: x[1])
            lines.append(
                f"三路信号分歧较大（最大差 {round(spread)} 分），"
                f"{low[0]}路（{round(low[1])}）明显偏低，建议人工复核。"
            )

    cap_line = _cap_line(job, info)
    if cap_line:
        lines.append(f"注意：{cap_line}。")

    return "\n".join(lines)


def build_explanation(job_db: dict, scores: list, resume_info: dict) -> dict:
    """
    从融合后的 job_scores 生成可解释报告。

    返回：
      {summary, verdict,
       per_job: [{job, verdict, career, years, education, cap, skills:{hit,gap}}]}
    """
    if not scores:
        return {"summary": "", "verdict": "", "per_job": []}

    top = scores[0]
    top_job = _resolve(job_db, top["job"])
    hits, gaps = hit_gap_skills(top_job, resume_info) if top_job else ([], [])

    summary = ""
    verdict = ""
    if top_job:
        summary = _build_summary(top, top_job, resume_info, hits, gaps)
        verdict = verdict_of(top.get("final_score", top.get("score", 0)))
        if career_match_score(top_job, resume_info) == 20:
            verdict += " · 职业身份一致"

    per_job = []
    for s in scores:
        job = _resolve(job_db, s["job"])
        if not job:
            per_job.append({
                "job": s["job"],
                "verdict": verdict_of(s.get("final_score", s.get("score", 0))),
                "skills": {"hit": [], "gap": []},
            })
            continue
        h, g = hit_gap_skills(job, resume_info)
        per_job.append({
            "job": s["job"],
            "verdict": verdict_of(s.get("final_score", s.get("score", 0))),
            "career": _career_line(resume_info, job),
            "years": _years_line(resume_info, job),
            "education": _edu_line(resume_info, job),
            "cap": _cap_line(job, resume_info),
            "skills": {"hit": h, "gap": g},
        })

    return {"summary": summary, "verdict": verdict, "per_job": per_job}


if __name__ == "__main__":
    # 确定性自测（不调用 LLM / 向量库）
    import json

    job = {
        "title": "AI Agent工程师",
        "required_skills": "Python,LangGraph,RAG,LLM,MCP",
        "education": "本科",
        "required_years": 3,
    }
    info = {
        "name": "张明",
        "education": "硕士",
        "work_year": 6,
        "career": "AI Agent工程师",
        "skill": ["Python", "LangGraph", "RAG", "LLM", "Docker"],
    }
    db = {job["title"]: job}
    scores = [{
        "job": "AI Agent工程师", "final_score": 86, "llm_score": 90,
        "rerank_score": 0.88, "reason": "技能高度匹配",
    }]
    print("=== 用例1：无 career 加分的强匹配 ===")
    print(json.dumps(build_explanation(db, scores, info), ensure_ascii=False, indent=2))

    # 用例2：career 命中职能类别 → verdict 应带"职业身份一致"，career 行应 +20
    cv_job = {
        "title": "计算机视觉算法工程师",
        "required_skills": "Python,PyTorch,视觉,图像处理",
        "education": "硕士",
        "required_years": 2,
    }
    cv_info = {
        "name": "王强",
        "education": "硕士",
        "work_year": 4,
        "career": "自动驾驶算法工程师",
        "skill": ["Python", "PyTorch", "视觉", "感知模型", "C++"],
    }
    cv_scores = [{
        "job": "计算机视觉算法工程师", "final_score": 84, "llm_score": 88,
        "rerank_score": 0.8, "reason": "感知算法经验强相关",
    }]
    print("=== 用例2：career 命中 → +20 / 职业身份一致 ===")
    out = build_explanation({cv_job["title"]: cv_job}, cv_scores, cv_info)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    assert "职业身份一致" in out["verdict"], "verdict 应带职业身份一致"
    assert out["per_job"][0]["career"].endswith("+20 确定性加分）"), "career 行应显示 +20"

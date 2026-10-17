# eval/label_review.py - 标答复核报告生成器（v2：原始域 vs 扩充域对比）
#
# 背景：评测集的"标准答案"(manual_answers.json) 是人工标的，可能存在错标。
#       更重要：A3.5 技能扩充(JOB_SKILL_EXPANSION) 会改变"标答岗位的技能域"，
#       ——如果用【扩充后】的域去审标答，标答会自己给自己加分（循环论证）。
#       例：R022 韩冰，数据分析师被塞进"推荐系统"后重合数凑到2 → 看起来"可信"。
#
# 工程原则（本项目最重要的方法论）：
#   * 评判"标答对不对"必须用【原始岗位要求】(未扩充)，那是唯一没被我们自己污染的 ground truth。
#   * A3.5 扩充属于【算法侧改进】，只能用来评估"系统匹配效果"，不能用来审计"标答是否合理"。
#
# 本脚本对每份有标答的简历，分别用【原始域】和【扩充域】计算重合度并分类，
# 重点输出两类判定的差异——这些差异点就是"算法在多大程度上扭曲了标答评价"的直接证据。
#
# 用法：python eval/label_review.py
# 输出：eval/label_review.md（客观版：用原始域判定的审计报告）

import json
import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from eval.eval_dataset import RESUMES
from database import get_all_jobs
from scoring_rules import _normalize_skill, JOB_SKILL_EXPANSION

# ============ 解析（从简历文本提取真实信息） ============

def extract_skills(text: str) -> set:
    """从简历文本提取技能（多来源兜底）。
    只提取简历里【真实出现的】技能词——这是客观评判的唯一依据。"""
    skills = set()

    m = re.search(r"技能：(.+)", text)
    if m:
        for s in m.group(1).split(","):
            s = re.sub(r"[（(].*?[)）]", "", s.strip()).strip()  # 去掉括号备注：英语(CET-6)->英语
            if s:
                skills.add(_normalize_skill(s))

    # 兜底1：技术栈：Java, Spring Boot, MySQL, Redis, Kafka
    m = re.search(r"技术栈：(.+)", text)
    if m:
        skills |= {_normalize_skill(s.strip()) for s in re.split(r"[,，]", m.group(1)) if s.strip()}

    # 兜底2：使用Excel、Python（pandas）、SQL 或 使用TensorFlow、Redis、Flink
    for m in re.finditer(r"使用([^。\n]+)", text):
        chunk = m.group(1)
        for s in re.split(r"[,，、]", chunk):
            s = s.strip()
            if not s:
                continue
            s = re.sub(r"[（(].*?[)）]", "", s).strip()
            if s and not any(kw in s for kw in ("负责", "参与", "实现", "开发", "精通")):
                skills.add(_normalize_skill(s))

    return skills


def extract_experience(text: str) -> list:
    """从简历文本提取工作经历行"""
    return [line.strip().lstrip("- ").strip() for line in text.splitlines()
            if line.strip().startswith("-")]


# ============ 岗位技能域 ============

def job_skill_domain(title: str, job_by_title: dict, use_expansion: bool) -> set:
    """岗位技能域。use_expansion=False 时只用【原始岗位要求】——客观审计的唯一依据。"""
    j = job_by_title.get(title)
    if not j:
        return set()
    base = {_normalize_skill(s) for s in j["required_skills"].split(",")}
    if not use_expansion:
        return base
    exp = {_normalize_skill(s) for s in JOB_SKILL_EXPANSION.get(title, [])}
    return base | exp


# ============ 单case判定 ============

def classify(skills, truth, job_by_title, use_expansion):
    """对一个case：返回 (和标答重合数, 全库最佳匹配, 全库最大重合, 分类, 全库最佳重合岗位技能域)"""
    truth_overlap = len(skills & job_skill_domain(truth, job_by_title, use_expansion))
    max_overlap, best_title = 0, None
    for t in job_by_title:
        o = len(skills & job_skill_domain(t, job_by_title, use_expansion))
        if o > max_overlap:
            max_overlap, best_title = o, t
    if truth_overlap == 0 and max_overlap == 0:
        cls = "岗位缺失"
    elif truth_overlap == 0:
        cls = "疑似错标"
    elif truth_overlap == 1:
        cls = "偏弱"
    else:
        cls = "可信"
    return truth_overlap, best_title, max_overlap, cls


def main():
    answers = json.load(open(Path(__file__).parent / "manual_answers.json", encoding="utf-8"))["answers"]
    jobs = get_all_jobs()
    job_by_title = {j["title"]: j for j in jobs}
    all_titles = list(job_by_title.keys())

    print(f"正在审计 {len(RESUMES)} 份简历、{len(jobs)} 个岗位...")
    print()

    # 两种判定都算
    results = {}  # rid -> {raw: {...}, exp: {...}}
    for r in RESUMES:
        rid = r["resume_id"]
        truth = answers.get(rid)
        if truth is None:
            continue
        skills = extract_skills(r["resume_text"])
        raw = classify(skills, truth, job_by_title, use_expansion=False)
        exp = classify(skills, truth, job_by_title, use_expansion=True)
        results[rid] = {"truth": truth, "skills": skills, "raw": raw, "exp": exp}

    # ===== 对比表：原始域 vs 扩充域 =====
    print("=" * 100)
    print("核心对比：原始域判定 vs 扩充域判定（差异 = A3.5 扭曲标答评价的直接证据）")
    print("=" * 100)
    print(f"{'case':<6}{'标答':<14}{'原始重合':<10}{'原始分类':<8}{'扩充重合':<10}{'扩充分类':<8}{'判定变化'}")
    print("-" * 100)
    changed = []
    for rid in sorted(results, key=lambda x: int(x[1:])):
        d = results[rid]
        truth = d["truth"]
        r_to, r_bt, r_mo, r_cls = d["raw"]
        e_to, e_bt, e_mo, e_cls = d["exp"]
        mark = "" if r_cls == e_cls else "  <<< 变化!"
        if r_cls != e_cls:
            changed.append(rid)
        print(f"{rid:<6}{truth:<14}{r_to!s:<10}{r_cls:<8}{e_to!s:<10}{e_cls:<8}{mark}")
    print("-" * 100)
    print(f"判定随扩充发生变化的 case：{len(changed)}个 {changed}")
    print()

    # ===== 汇总（以客观的原始域为准） =====
    cat = {"岗位缺失": [], "疑似错标": [], "偏弱": [], "可信": []}
    for rid, d in results.items():
        cat[d["raw"][3]].append(rid)

    print("=== 客观分类（原始域，未扩充）===")
    for k, v in cat.items():
        print(f"  {k}: {len(v)}份 {v}")
    print()

    # ===== 原始域判定下的"疑似错标/岗位缺失/偏弱" =====
    print("=== 需要人工复核的 case（原始域）===")
    for rid, d in sorted(results.items(), key=lambda x: x[0]):
        cls = d["raw"][3]
        if cls in ("疑似错标", "岗位缺失"):
            truth = d["truth"]
            bt = d["raw"][1]
            print(f"  {rid} 标答[{truth}] -> {cls} | 全库最佳: {bt or '无'}")

    # ============ 生成报告 ============
    lines = []
    lines.append("# 标答复核报告（客观版 · 原始岗位要求）\n")
    lines.append("> 依据：用**【原始岗位要求】**（未做任何技能扩充）判定每个标答是否成立。\n")
    lines.append("> **为什么必须用原始域**：A3.5 扩充改变了岗位技能域；若用扩充域审计标答，")
    lines.append("> 标答会被我们自己的算法'加分'，形成循环论证（例：R022 数据分析师被塞进'推荐系统'）。")
    lines.append("> 原始岗位要求是唯一没被我们自己污染的标准。\n\n")

    lines.append("## 汇总（原始域）\n")
    for k, v in cat.items():
        lines.append(f"- **{k}**：{len(v)}份 {', '.join(v) if v else ''}")
    lines.append("\n---\n")

    lines.append("## 逐case明细（原始重合 / 扩充重合 对比）\n")
    lines.append("| case | 标答 | 原始重合 | 扩充重合 | 原始分类 | 扩充分类 | 判定变化 |")
    lines.append("|---|---|---|---|---|---|---|")
    for rid in sorted(results, key=lambda x: int(x[1:])):
        d = results[rid]
        r_to, r_bt, r_mo, r_cls = d["raw"]
        e_to, e_bt, e_mo, e_cls = d["exp"]
        chg = "**变化**" if r_cls != e_cls else ""
        lines.append(f"| {rid} | {d['truth']} | {r_to} | {e_to} | {r_cls} | {e_cls} | {chg} |")
    lines.append("")

    # 存疑case证据（原始域判定）
    lines.append("---\n")
    lines.append("## 需人工复核的 case 简历证据（原始域判定）\n")
    for rid in sorted(results, key=lambda x: int(x[1:])):
        d = results[rid]
        if d["raw"][3] not in ("疑似错标", "岗位缺失"):
            continue
        truth = d["truth"]
        bt = d["raw"][1]
        lines.append(f"### {rid} · 标答「{truth}」\n")
        lines.append(f"- 简历真实技能：`{', '.join(sorted(d['skills']))}`")
        if bt:
            lines.append(f"- 全库最佳匹配：`{bt}`（原始域重合{d['raw'][2]}个）")
        else:
            lines.append(f"- 全库最佳匹配：**无**（数据库没有匹配岗位 → 岗位缺失）")
        lines.append("- 工作经历：")
        for e in extract_experience(next(r["resume_text"] for r in RESUMES if r["resume_id"] == rid)):
            lines.append(f"  - {e}")
        lines.append("")

    out = Path(__file__).parent / "label_review.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n报告已生成：{out}")


if __name__ == "__main__":
    main()
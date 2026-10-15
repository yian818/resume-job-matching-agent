# eval/recall_rate.py - 召回率诊断（P1）
#
# 目的：量化"真命岗位有没有被召回"。
# 在 RAG 链路里，rerank 只能重排【已经被召回的】候选；
# 如果真命岗位在召回阶段就漏了（没进 top-10 候选），rerank 再强也救不回来。
# 所以迭代前先分清：当前失败是【召回漏】还是【重排错】。
#
# 注意：本脚本只跑召回链路（SQL硬过滤 → BGE向量 → 关键词补足），
#       不调 LLM、不跑 rerank，所以比完整评测快得多（1-2分钟）。
#
# 用法：python eval/recall_rate.py
# 输出：
#   - 召回率 = 真命岗位进入 top-10 候选的样本占比
#   - 每个"召回漏"的 case 明细：真命岗位 vs 实际召回的候选

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from eval.eval_dataset import RESUMES
from retriever import search_similar_jobs

# 读修正后的标答
with open(Path(__file__).parent / "manual_answers.json", "r", encoding="utf-8") as f:
    ANSWERS = json.load(f)["answers"]


def recall_rate():
    """在28份有标答简历上，测真命岗位的召回情况"""
    total = 0
    recalled = 0
    misses = []  # (rid, truth, 召回列表)

    for r in RESUMES:
        rid = r["resume_id"]
        truth = ANSWERS.get(rid)
        if not truth:
            continue  # 无标答/已剔除，跳过

        total += 1

        # 从简历文本提取技能（和标答复核同一套提取逻辑）
        text = r["resume_text"]
        resume_skills = extract_skills_from_text(text)

        # 用完整简介里的技能构造 query 需要 work_year，但 search 需要 max_years
        # 这里直接从简历文本提取 work_year（简化：用于 SQL 硬过滤）
        work_year = extract_years_from_text(text)

        # ===== 只跑召回：SQL硬过滤 + 向量召回 + 关键词补足 =====
        try:
            candidates = search_similar_jobs(
                resume_skills,
                max_years=work_year,
                top_k=10,  # 和 match_jobs_node 里一致
            )
        except Exception as e:
            print(f"  {rid} 召回异常: {e}")
            continue

        # 真命岗位在不在候选里？（含部门后缀容错）
        hit = any(truth in c["title"] for c in candidates)
        if hit:
            recalled += 1
        else:
            candidates_titles = [c["title"] for c in candidates]
            misses.append((rid, truth, candidates_titles))

            # 打印召回漏的 case
            print(f"  ❌ {rid} 标答[{truth}] 未进候选 | 实际召回: {candidates_titles}")

    print(f"\n========== 召回率诊断 ==========")
    print(f"有标答简历: {total} 份")
    print(f"真命岗位被召回: {recalled} 份 = {recalled/total*100:.1f}%")
    print(f"召回漏: {len(misses)} 份 = {len(misses)/total*100:.1f}%")
    return total, recalled, misses


def extract_skills_from_text(text: str):
    """从简历文本提取技能列表（多来源兜底，提取的是真实技能词）"""
    import re

    skills = []
    m = re.search(r"技能：(.+)", text)
    if m:
        skills += [s.strip() for s in m.group(1).split(",") if s.strip()]
    m = re.search(r"技术栈：(.+)", text)
    if m:
        skills += [s.strip() for s in re.split(r"[,，]", m.group(1)) if s.strip()]
    # 兜底：使用XX、YY、ZZ
    for m in re.finditer(r"使用([^。\n]+)", text):
        chunk = m.group(1)
        for s in re.split(r"[,，、]", chunk):
            s = s.strip()
            if s and not any(kw in s for kw in ("负责", "参与", "实现", "开发", "精通")):
                skills.append(s)
    return skills


def extract_years_from_text(text: str):
    """从简历文本提取工作年限（毕业年份 → 到现在）"""
    import re

    m = re.search(r"(\d{4})年毕业", text)
    if m:
        grad_year = int(m.group(1))
        return max(1, 2026 - grad_year)
    # 兜底：从工作经历里的年份范围估一个
    years = []
    for mm in re.finditer(r"(\d{4})-(\d{4}|至今)", text):
        y1, y2 = int(mm.group(1)), mm.group(2)
        y2 = 2026 if y2 == "至今" else int(y2)
        years.append((y1, y2))
    if years:
        # 最早开始年 → 现在
        start = min(y1 for y1, _ in years)
        return max(1, 2026 - start)
    return 5  # 兜底默认


if __name__ == "__main__":
    recall_rate()
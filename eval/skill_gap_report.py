# eval/skill_gap_report.py - 精确列出每份简历技能 与 标答岗位技能 的差集
# 目的：找出"标答岗位技能表"缺了哪些词，导致规则引擎判定重合为0。
#       这是语言不统一（岗位英文/简历中文）的精确诊断。
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from eval.eval_dataset import RESUMES
from database import get_all_jobs
from scoring_rules import _normalize_skill

answers = json.load(open(Path(__file__).parent / "manual_answers.json", encoding="utf-8"))["answers"]
jobs = {j["title"]: j["required_skills"] for j in get_all_jobs()}


def extract_skills(text):
    import re
    skills = set()
    m = re.search(r"技能：(.+)", text)
    if m:
        skills |= {_normalize_skill(s.strip()) for s in m.group(1).split(",") if s.strip()}
    return skills


print(f"{'case':<6}{'标答岗位':<14}{'重合数':<6}简历技能 ∩ 岗位技能")
print("-" * 100)
for r in RESUMES:
    rid = r["resume_id"]
    truth = answers.get(rid)
    if not truth:
        continue
    skills = extract_skills(r["resume_text"])
    job_skills = {_normalize_skill(s) for s in jobs.get(truth, "").split(",")}
    overlap = skills & job_skills
    if len(overlap) < 2:  # 只看重合不足的（可能被 hard_cap 误伤）
        only_resume = skills - job_skills
        only_job = job_skills - skills
        print(f"{rid:<6}{truth:<14}{len(overlap):<6}重合={sorted(overlap)}")
        print(f"      简历独有(岗位缺这些词): {sorted(only_resume)}")
        print(f"      岗位独有(简历缺这些词): {sorted(only_job)}")
        print()

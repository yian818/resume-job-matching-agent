# eval/job_coverage_audit.py - 岗位库覆盖审计（矫正标答标准的前置检查）
#
# 目的：客观回答三个问题——
#   1. 50份简历里，现有20个岗位能覆盖多少个？（真命岗位在库里 = 标答"可判"）
#   2. 覆盖不到的简历，它们的真实职业是什么？（这些需要补岗位，而不是删简历）
#   3. 库里哪些岗位没有对应简历？（这些是"干扰岗位"——测试系统不瞎推）
#
# 原则：标答只能从【简历工作经历里真实出现的职位】里选，绝不凭空造。
#       这跟 label_review.py 的原始域原则一致——简历文本是唯一客观依据。

import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from eval.eval_dataset import RESUMES
from database import get_all_jobs


def extract_career(text: str) -> list:
    """从简历工作经历提取 (年份, 公司, 职位) 三元组。职位是客观证据。"""
    out = []
    for line in text.splitlines():
        line = line.strip().lstrip("- ").strip()
        m = re.match(r"(\d{4})-(\d{4}|至今)\s+(.+?)\s+(\S+)(?:[，,].*)?$", line)
        if m:
            _, _, company, role = m.groups()
            out.append((company, role))
    return out


def main():
    jobs = get_all_jobs()
    job_titles = [j["title"] for j in jobs]
    print(f"现有岗位库：{len(jobs)}个\n  {job_titles}")
    print()

    covered = []      # 简历工作经历里出现过的职位 = 现有岗位
    uncovered = []    # 简历里有、库里没有的职位（需要补岗）
    role_to_resumes = {}  # 职位 -> [rid...]

    for r in RESUMES:
        rid = r["resume_id"]
        roles = [role for _, role in extract_career(r["resume_text"])]
        for role in roles:
            role_to_resumes.setdefault(role, []).append(rid)

    # 判断：某个简历里出现过的职位，在不在现有岗位库里
    for role, rids in role_to_resumes.items():
        # 模糊匹配：岗位名包含该职位，或职位名包含岗位核心词
        hit = None
        for t in job_titles:
            # 精确/包含匹配，去掉修饰词
            if role in t or t in role:
                hit = t
                break
        entry = (role, rids)
        if hit:
            covered.append((role, hit, rids))
        else:
            uncovered.append((role, rids))

    print("=" * 78)
    print("A. 简历职业 在现有岗位库中能找到对应岗位的（标答可判）")
    print("=" * 78)
    for role, hit, rids in covered:
        print(f"  {role:<14} → {hit:<22} {rids}")

    print()
    print("=" * 78)
    print("B. 简历职业 库里没有对应岗位的（岗位缺失 → 需补岗）")
    print("=" * 78)
    for role, rids in sorted(uncovered, key=lambda x: -len(x[1])):
        print(f"  {role:<14} {rids}")

    print()
    print("=" * 78)
    print("C. 现有岗位中 没有简历对应它的（干扰岗位）")
    print("=" * 78)
    used_titles = {hit for _, hit, _ in covered}
    for t in job_titles:
        if t not in used_titles:
            print(f"  {t}")

    # 汇总
    all_roles = set(role_to_resumes.keys())
    print()
    print(f"简历中出现过的不同职位：{len(all_roles)}个")
    print(f"现有岗位能覆盖：{len(covered)}个职位")
    print(f"岗位缺失：{len(uncovered)}个职位")
    print(f"干扰岗位：{len(job_titles) - len(used_titles)}个")


if __name__ == "__main__":
    main()

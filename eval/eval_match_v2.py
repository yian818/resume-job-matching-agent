"""
eval_match_v2.py - 岗位匹配准确率评测（v2：用人工标注标准答案）
"""
import json
import time
import sys
from pathlib import Path

# 把项目根目录加到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from nodes import extract_resume_node, match_jobs_node
from eval_dataset import RESUMES, JOBS
from database import get_all_jobs

# 加载人工标注的标准答案
with open(Path(__file__).parent / "manual_answers.json", "r", encoding="utf-8") as f:
    MANUAL_ANSWERS = json.load(f)["answers"]

def main():
    print("=" * 60)
    print("P1-Step2 v2: 岗位匹配准确率评测（人工标注标准答案）")
    print("=" * 60)

    jobs_in_db = get_all_jobs()
    print(f"数据库岗位数：{len(jobs_in_db)}")
    print(f"测试简历数：{len(RESUMES)}")
    print()

    top1_hits = 0
    top3_hits = 0
    total_runs = 0
    has_truth_count = 0
    errors = []
    all_results = []

    for i, resume_data in enumerate(RESUMES):
        rid = f"R{i+1:03d}"
        resume_text = resume_data["resume_text"]

        # 人工标注的标准答案
        truth_job = MANUAL_ANSWERS.get(rid)

        state = {
            "resume_text": resume_text,
            "resume_info": None,
            "jobs": [],
            "report": "",
            "error": None,
            "info_complete": True,
            "missing_fields": [],
            "follow_up_question": "",
            "user_answer": "",
            "needs_human": False,
        }

        try:
            # 第1步：抽取
            state = extract_resume_node(state)
            # 第2步：匹配
            state = match_jobs_node(state)

            resume_info = state["resume_info"]
            scores = state.get("job_scores", [])

            if truth_job is None:
                # 没有标准答案的简历，跳过统计
                top_job = scores[0]["job"] if scores else "无"
                top_score = scores[0]["score"] if scores else 0
                print(f"-- [{i+1}/50] {rid} {resume_info['name']} | 无标准答案 | top1:{top_job}({top_score})")
                continue

            has_truth_count += 1
            total_runs += 1

            # 找标准答案在Agent推荐里排第几
            rank = -1
            for idx, s in enumerate(scores):
                if truth_job in s["job"]:
                    rank = idx + 1
                    break

            if rank == 1:
                top1_hits += 1
            if rank <= 3:
                top3_hits += 1

            top_job = scores[0]["job"] if scores else "无"
            top_score = scores[0]["score"] if scores else 0

            status = "OK" if rank <= 3 else "XX"
            print(f"{status} [{i+1}/50] {rid} {resume_info['name']} | truth:{truth_job} | top1:{top_job}({top_score}) | rank:{rank}")

            all_results.append({
                "rid": rid,
                "name": resume_info["name"],
                "truth": truth_job,
                "rank": rank,
                "top1": top_job,
                "top1_score": top_score,
            })

        except Exception as e:
            errors.append({"rid": rid, "error": str(e)})
            print(f"XX [{i+1}/50] {rid} failed: {e}")

        # 每跑5份休息一下，避免API限流
        if (i + 1) % 5 == 0:
            time.sleep(2)

    # 输出报告
    print("\n" + "=" * 60)
    print("评测报告")
    print("=" * 60)
    print(f"有人工标准答案的简历：{has_truth_count}份")
    print(f"成功跑通: {total_runs}/{has_truth_count}")
    print(f"失败: {len(errors)}")
    print()
    if total_runs > 0:
        print(f"Top-1命中率: {top1_hits}/{total_runs} = {top1_hits/total_runs*100:.1f}%")
        print(f"Top-3命中率: {top3_hits}/{total_runs} = {top3_hits/total_runs*100:.1f}%")

    if errors:
        print(f"\n失败详情:")
        for e in errors:
            print(f"  {e['rid']}: {e['error'][:80]}")

if __name__ == "__main__":
    main()

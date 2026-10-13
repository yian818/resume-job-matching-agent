# eval_match_v2_batch.py - 分批续跑评测（解决内存不足导致整批失败的问题）
#
# 背景：一次跑完50份评测，BGE嵌入模型 + bge-reranker-large + ChromaDB 常驻内存，
#      在内存不足的机器上会在中途被系统强杀，前功尽弃。
# 解法：支持指定起止区间分批跑，每批独立进程、跑完释放内存；
#      结果实时追加到同一份日志，批与批之间无缝衔接。
#
# 用法：
#   python eval/eval_match_v2_batch.py --start 1 --end 50 --log eval/output_a3_full.log
#   （--start 从1开始；--end 含；--log 指定追加日志文件，默认 output_a3_full.log）
#
# 断点续跑：评测被中断后，看日志里最后跑到的编号 N，
#   下一批从 N+1 开始即可，已跑的结果不丢失。

import argparse
import json
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from nodes import extract_resume_node, match_jobs_node
from eval_dataset import RESUMES
from database import get_all_jobs

# 加载人工标注的标准答案
with open(Path(__file__).parent / "manual_answers.json", "r", encoding="utf-8") as f:
    MANUAL_ANSWERS = json.load(f)["answers"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1, help="起始编号（含），从1开始")
    parser.add_argument("--end", type=int, default=len(RESUMES), help="结束编号（含）")
    parser.add_argument("--log", type=str, default="output_a3_full.log", help="结果日志文件（追加模式）")
    args = parser.parse_args()

    start, end = max(1, args.start), min(len(RESUMES), args.end)
    print(f"分批评测：第 {start}~{end} 份（共{len(RESUMES)}份），结果追加到 {args.log}")

    jobs_in_db = get_all_jobs()
    print(f"数据库岗位数：{len(jobs_in_db)}")

    log_path = Path(__file__).parent / args.log

    top1_hits = 0
    top3_hits = 0
    total_runs = 0
    errors = []

    for i in range(start - 1, end):
        rid = f"R{i+1:03d}"
        resume_data = RESUMES[i]
        resume_text = resume_data["resume_text"]
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
            state = extract_resume_node(state)
            state = match_jobs_node(state)
            resume_info = state["resume_info"]
            scores = state.get("job_scores", [])

            if truth_job is None:
                top_job = scores[0]["job"] if scores else "无"
                top_score = scores[0]["score"] if scores else 0
                line = f"-- [{i+1}/50] {rid} {resume_info['name']} | 无标准答案 | top1:{top_job}({top_score})"
                print(line)
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
                continue

            total_runs += 1
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
            line = f"{status} [{i+1}/50] {rid} {resume_info['name']} | truth:{truth_job} | top1:{top_job}({top_score}) | rank:{rank}"
            print(line)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

        except Exception as e:
            errors.append({"rid": rid, "error": str(e)})
            line = f"XX [{i+1}/50] {rid} failed: {e}"
            print(line)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

        if (i + 1) % 5 == 0:
            time.sleep(2)

    # 本批小结
    print(f"\n本批（{start}~{end}）完成：有答案 {total_runs} 份，Top-1 {top1_hits}，Top-3 {top3_hits}，失败 {len(errors)}")
    if errors:
        for e in errors:
            print(f"  {e['rid']}: {e['error'][:80]}")


if __name__ == "__main__":
    main()

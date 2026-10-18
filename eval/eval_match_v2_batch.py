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
import re
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


def already_done(log_path: Path) -> set:
    """读已有日志，找出已跑完的case（断点续跑用）。
    只跳过 OK/--（成功），绝不跳过 XX（失败）——失败的要重新跑。
    同时跳过 502 HTML 脏行（失败行内容可能跨多行）。"""
    done = set()
    if not log_path.exists():
        return done
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("--") and not line.startswith("OK"):
            continue  # 只认成功行；XX/脏行忽略
        m = re.search(r"\b(R\d{3})\b", line)
        if m:
            done.add(m.group(1))
    return done


def run_one(i: int) -> dict:
    """跑单份简历，返回 (line, state, error)。失败时内部重试。"""
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

    # 重试机制：API 抖动（502/Connection error）是评测失败主因，重试3次
    MAX_RETRY = 3
    last_err = None
    for attempt in range(MAX_RETRY):
        try:
            state = extract_resume_node(state)
            state = match_jobs_node(state)
            resume_info = state["resume_info"]
            scores = state.get("job_scores", [])

            if truth_job is None:
                top_job = scores[0]["job"] if scores else "无"
                top_score = scores[0]["score"] if scores else 0
                return {"rid": rid, "line": f"-- [{i+1}/50] {rid} {resume_info['name']} | 无标准答案 | top1:{top_job}({top_score})", "ok": True}

            rank = -1
            for idx, s in enumerate(scores):
                if truth_job in s["job"]:
                    rank = idx + 1
                    break

            top_job = scores[0]["job"] if scores else "无"
            top_score = scores[0]["score"] if scores else 0
            status = "OK" if rank <= 3 else "XX"
            line = f"{status} [{i+1}/50] {rid} {resume_info['name']} | truth:{truth_job} | top1:{top_job}({top_score}) | rank:{rank}"
            return {"rid": rid, "line": line, "rank": rank, "ok": True}

        except Exception as e:
            last_err = e
            if attempt < MAX_RETRY - 1:
                wait = 10 * (attempt + 1)  # 10s, 20s 递增等待
                print(f"  ⚠️ {rid} 第{attempt+1}次失败: {str(e)[:60]}，{wait}s后重试")
                time.sleep(wait)

    return {"rid": rid, "line": f"XX [{i+1}/50] {rid} failed: {last_err}", "ok": False, "error": str(last_err)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1, help="起始编号（含），从1开始")
    parser.add_argument("--end", type=int, default=len(RESUMES), help="结束编号（含）")
    parser.add_argument("--log", type=str, default="output_a3_full.log", help="结果日志文件（追加模式）")
    parser.add_argument("--resume", action="store_true", help="跳过日志中已跑过的case（断点续跑）")
    args = parser.parse_args()

    start, end = max(1, args.start), min(len(RESUMES), args.end)
    log_path = Path(__file__).parent / args.log

    # 断点续跑：跳过已完成的
    done = already_done(log_path) if args.resume else set()
    if done:
        print(f"断点续跑：日志中已有 {len(done)} 份已完成，跳过")

    print(f"分批评测：第 {start}~{end} 份（共{len(RESUMES)}份），结果追加到 {args.log}")

    jobs_in_db = get_all_jobs()
    print(f"数据库岗位数：{len(jobs_in_db)}")

    top1_hits = 0
    top3_hits = 0
    total_runs = 0
    errors = []

    for i in range(start - 1, end):
        rid = f"R{i+1:03d}"
        if rid in done:
            print(f"  跳过 {rid}（已跑过）")
            continue

        result = run_one(i)
        print(result["line"])
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(result["line"] + "\n")

        if not result["ok"]:
            errors.append({"rid": rid, "error": result.get("error", "未知")})
            continue

        # 有标答才算进正确率
        truth_job = MANUAL_ANSWERS.get(rid)
        if truth_job is None:
            continue
        total_runs += 1
        if result.get("rank") == 1:
            top1_hits += 1
        if result.get("rank") is not None and result["rank"] <= 3:
            top3_hits += 1

        if (i + 1) % 5 == 0:
            time.sleep(2)

    # 本批小结
    print(f"\n本批（{start}~{end}）完成：有答案 {total_runs} 份，Top-1 {top1_hits}，Top-3 {top3_hits}，失败 {len(errors)}")
    if errors:
        for e in errors:
            print(f"  {e['rid']}: {e['error'][:80]}")

    # P10：本批跑完自动算排序质量指标（MRR / NDCG@k），从日志里解析 rank
    try:
        from metrics import parse_rank, dcg_contrib

        _results = []
        for _line in log_path.read_text(encoding="utf-8").splitlines():
            _rid, _rank = parse_rank(_line)
            if _rid is not None:
                _results.append((_rid, _rank))
        if _results:
            _n = len(_results)
            _mrr = sum(1.0 / r if r >= 1 else 0.0 for _, r in _results) / _n
            _k = 3
            _ndcg = sum(dcg_contrib(r, _k) for _, r in _results) / _n
            print(f"排序质量（P10）：MRR={_mrr:.4f}  NDCG@{_k}={_ndcg:.4f}  （共{_n}份有标答）")
    except Exception as e:
        print(f"（排序指标计算失败，可手动跑 eval/metrics.py --log {args.log}）: {e}")


if __name__ == "__main__":
    main()

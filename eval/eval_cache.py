# eval_cache.py - 在线评测面板的信号缓存与模拟（P13）
#
# 设计动机：
#   全量评测要跑 50 份简历的完整流水线（LLM 抽取 + LLM 打分 + 重排），约 20-30 分钟。
#   如果面板上每拖一次权重就重跑一遍，既慢又烧钱。
#
# 解法（也是系统架构的自然延伸）：
#   1. build_cache：跑一次全量流水线，把每个岗位的**四信号原始值**缓存下来
#      （rule / llm / rerank / cap）——这些是"模型算出来的原料"。
#   2. simulate：调权重时只重算**融合层**（纯确定性函数 fuse_final），毫秒级出指标。
#
# 诚实性说明：面板上的指标是真实的——原料来自真实流水线，
#   只是融合层被交互式重算。这正好证明"四信号融合"是可解释、可调的确定性层。
#
# 用法：
#   python eval/eval_cache.py --limit 50          # 构建/续跑缓存
#   python eval/eval_cache.py --force             # 全量重建

import argparse
import json
import math
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

ROOT = Path(__file__).parent
CACHE_PATH = ROOT / "signal_cache.json"
ANSWERS_PATH = ROOT / "manual_answers.json"


def dcg_contrib(rank: int, k: int) -> float:
    """单个相关文档的 DCG 贡献（单标答，IDCG=1）"""
    if rank < 1 or rank > k:
        return 0.0
    return 1.0 / math.log2(rank + 1)


def _truth_rank(truth: str, jobs: list) -> int:
    if not truth:
        return -2
    for i, j in enumerate(jobs):
        if truth in j["job"]:
            return i + 1
    return -1


def build_cache(limit: int = 50, force: bool = False, progress=None) -> dict:
    """
    跑流水线，缓存每份简历每个候选岗位的四信号。
    断点续跑：已有缓存的 rid 默认跳过（--force 才重建）。
    """
    from eval_dataset import RESUMES
    from main_api import run_match
    import os

    answers = json.loads(ANSWERS_PATH.read_text(encoding="utf-8"))["answers"]
    cache = {"built_at": None, "config": {}, "cases": {}}
    if CACHE_PATH.exists() and not force:
        cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))

    ids = [f"R{i:03d}" for i in range(1, min(limit, len(RESUMES)) + 1)]
    todo = [rid for rid in ids if force or rid not in cache["cases"]]

    for n, rid in enumerate(todo, 1):
        idx = int(rid[1:]) - 1
        try:
            result = run_match(RESUMES[idx]["resume_text"], include_advice=False)
            jobs = []
            for m in result["matches"]:
                s = m.signals
                jobs.append({
                    "job": m.job,
                    "rule": s.rule,
                    "llm": s.llm,
                    "rerank": s.rerank,   # 已是 0-100 量纲（raw×100）
                    "cap": s.cap,
                    "final": m.score,
                })
            cache["cases"][rid] = {"truth": answers.get(rid) or "", "jobs": jobs}
        except Exception as e:
            # 失败不写缓存，下次续跑自动重试
            print(f"  {rid} 失败：{str(e)[:80]}")
            continue

        if progress:
            progress(n, len(todo), rid)
        if n % 5 == 0:
            _save(cache)

    cache["built_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    cache["config"] = {
        "temperature": os.getenv("LLM_TEMPERATURE", "0.1"),
        "score_runs": os.getenv("SCORE_RUNS", "1"),
    }
    _save(cache)
    return cache


def _save(cache: dict):
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def simulate(cache: dict, w_rule: float = 0.4, w_llm: float = 0.3,
             w_rerank: float = 0.3, use_cap: bool = True) -> dict:
    """
    用缓存的四信号，按给定权重重算融合分与排序指标（纯函数，毫秒级）。
    返回 {metrics, failures, cases}
    """
    from reranker import fuse_final

    w = {"rule": w_rule, "llm": w_llm, "rerank": w_rerank}
    ranks = []
    failures = []
    case_rows = []

    for rid, case in cache["cases"].items():
        jobs = case["jobs"]
        truth = case["truth"]
        if not jobs:
            continue
        scored = []
        for j in jobs:
            cap = (j.get("cap") if use_cap else 100) or 100
            fused = fuse_final(
                j.get("rule") or 0,
                j.get("llm") or 0,
                j.get("rerank") or 0,
                cap,
                w,
            )
            scored.append({"job": j["job"], "score": fused})
        scored.sort(key=lambda x: x["score"], reverse=True)

        rank = _truth_rank(truth, scored)
        if rank != -2:  # 有标答才参与计分
            ranks.append(rank)
        case_rows.append({
            "rid": rid,
            "truth": truth,
            "top1": scored[0]["job"] if scored else "",
            "top1_score": scored[0]["score"] if scored else 0,
            "truth_rank": rank,
        })
        if truth and rank != 1:
            failures.append({
                "rid": rid,
                "truth": truth,
                "top1": scored[0]["job"] if scored else "",
                "truth_rank": rank,
            })

    n = len(ranks) or 1
    metrics = {
        "n": len(ranks),
        "top1": round(sum(1 for r in ranks if r == 1) / n, 4),
        "top3": round(sum(1 for r in ranks if 1 <= r <= 3) / n, 4),
        "mrr": round(sum(1.0 / r for r in ranks if r >= 1) / n, 4),
        "ndcg3": round(sum(dcg_contrib(r, 3) for r in ranks) / n, 4),
        "recall": round(sum(1 for r in ranks if r >= 1) / n, 4),
    }
    failures.sort(key=lambda x: (x["truth_rank"] if x["truth_rank"] >= 1 else 99))
    return {"metrics": metrics, "failures": failures, "cases": case_rows}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    def show(done, total, rid):
        print(f"[{done}/{total}] {rid} 已缓存")

    cache = build_cache(limit=args.limit, force=args.force, progress=show)
    res = simulate(cache)
    print("\n模拟指标（生产权重 0.4/0.3/0.3，启用硬上限）：")
    print(json.dumps(res["metrics"], ensure_ascii=False, indent=2))
    print(f"失败案例：{len(res['failures'])} 个")
    for f in res["failures"][:10]:
        print(f"  {f['rid']} 标答={f['truth']} 排名={f['truth_rank']} Top1={f['top1']}")

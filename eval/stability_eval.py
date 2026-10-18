# stability_eval.py - 排序稳定性评测（P13）
#
# 目的：同一份简历重复跑 N 次，量化 Top-1 的翻转率与标答岗位排名波动。
# 这是对"Top-1 98%"这个单次评测指标的可信度检验——单次跑对，不代表每次都跑对。
#
# 用法：
#   python eval/stability_eval.py --runs 3 --rids R001,R003,R015 --tag before
#   python eval/stability_eval.py --runs 3 --tag after        # 默认子集
#
# 输出：终端表格 + eval/stability_<tag>.json

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from main_api import run_match
from eval_dataset import RESUMES

ROOT = Path(__file__).parent
ANSWERS = json.loads((ROOT / "manual_answers.json").read_text(encoding="utf-8"))["answers"]

# 默认子集：历史上出现过边界/翻转的简历 + 若干强匹配对照
DEFAULT_RIDS = ["R001", "R003", "R004", "R015", "R024", "R042"]

# 示例简历（不在50份评测集里，但已观察到 Top-1 会翻转），用于压力测试
SAMPLE_TEXT = (
    "张明，男，28岁。\n"
    "学历：北京大学，计算机科学，硕士，2020年毕业。\n"
    "工作经历：\n"
    "- 2020-2023 字节跳动 算法工程师，负责推荐系统优化，使用 Python、PyTorch、Transformer，上线后CTR提升12%。\n"
    "- 2023-至今 阿里云 高级算法工程师，负责LLM应用开发，精通LangGraph、RAG、向量数据库（Milvus）、Prompt Engineering。\n"
    "技能：Python, PyTorch, LangGraph, RAG, Milvus, LLM, Prompt Engineering, 大模型微调, Docker, Kubernetes。\n"
    "项目：独立完成一个基于LangGraph的AI客服Agent，支持多轮对话和工具调用，日均处理5000+请求。"
)


def _bare(title: str) -> str:
    """剥掉部门后缀：'AI Agent工程师（产品部）' -> 'AI Agent工程师'。
    同一岗位带不带后缀不是翻转，比较前必须归一。"""
    return title.split("（")[0].strip()


def truth_rank(truth: str, matches: list) -> int:
    """标答岗位在本次排序中的名次；召回漏则 -1。"""
    if not truth:
        return -2  # 无标答
    for i, m in enumerate(matches):
        if truth in _bare(m.job):
            return i + 1
    return -1


def run_once(rid: str):
    idx = int(rid[1:]) - 1
    text = RESUMES[idx]["resume_text"]
    result = run_match(text, include_advice=False)
    return result["matches"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3, help="每份简历重复次数")
    ap.add_argument("--rids", default=",".join(DEFAULT_RIDS), help="逗号分隔的简历ID")
    ap.add_argument("--tag", default="run", help="报告文件名标签")
    ap.add_argument("--include-sample", action="store_true", help="额外压测示例简历(张明)")
    args = ap.parse_args()

    rids = [r.strip() for r in args.rids.split(",") if r.strip()]
    report = {"tag": args.tag, "runs": args.runs, "cases": []}

    print(f"稳定性评测：{len(rids)} 份简历 × {args.runs} 次（tag={args.tag}）\n")

    def process(rid, truth, runner):
        tops, ranks, scores, rankings = [], [], [], []
        for _ in range(args.runs):
            try:
                matches = runner(rid)
                tops.append(matches[0].job)
                scores.append(matches[0].score)
                ranks.append(truth_rank(truth, matches))
                rankings.append([_bare(m.job) for m in matches])
            except Exception as e:
                tops.append(f"ERROR:{str(e)[:40]}")
                scores.append(None)
                ranks.append(-3)
                rankings.append([])

        ok_tops = [t for t in tops if not t.startswith("ERROR:")]
        bare_tops = [_bare(t) for t in ok_tops]
        stable = len(set(bare_tops)) == 1 if bare_tops else False  # 按裸标题比较，部门后缀不算翻转
        rank1_rate = sum(1 for r in ranks if r == 1) / args.runs
        ok_scores = [s for s in scores if s is not None]
        score_spread = (max(ok_scores) - min(ok_scores)) if ok_scores else 0
        case = {
            "rid": rid,
            "truth": truth,
            "top1": tops,
            "top1_bare": bare_tops,
            "top1_scores": scores,
            "truth_ranks": ranks,
            "stable": stable,
            "rank1_rate": round(rank1_rate, 3),
            "score_spread": score_spread,
            "rankings": rankings,   # 每 run 的完整排名（离线可复算任何指标）
        }
        report["cases"].append(case)

        flag = "✅稳定" if stable else ("❌失败" if not bare_tops else "⚠️翻转")
        print(f"{rid} [{flag}] 标答={truth or '—'}  分数波动±{score_spread}")
        for i, (t, s, r) in enumerate(zip(tops, scores, ranks), 1):
            print(f"   run{i}: {t} ({s}分) 标答排名={r}")
        if not stable and bare_tops:
            print(f"   分布: {dict(Counter(bare_tops))}")
        print()

    for rid in rids:
        process(rid, ANSWERS.get(rid) or "", run_once)
    if args.include_sample:
        process("SAMPLE", "", lambda _rid: run_match(SAMPLE_TEXT, include_advice=False)["matches"])

    # 翻转率只统计"至少有一次成功"的案例，纯失败案例不计入翻转
    valid = [c for c in report["cases"] if c["top1_bare"]]
    n = len(valid)
    flips = sum(1 for c in valid if not c["stable"])
    avg_rank1 = sum(c["rank1_rate"] for c in valid) / n if n else 0
    report["summary"] = {
        "cases": len(report["cases"]),
        "valid_cases": n,
        "flip_cases": flips,
        "flip_rate": round(flips / n, 3) if n else 0,
        "avg_label_rank1_rate": round(avg_rank1, 3),
    }
    out = ROOT / f"stability_{args.tag}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=" * 46)
    print(f"有效案例：{n} · Top-1 翻转：{flips}/{n}（翻转率 {report['summary']['flip_rate']:.1%}）")
    print(f"标答岗位平均 Top-1 命中率（跨重复）：{avg_rank1:.1%}")
    print(f"报告已写入：{out}")


if __name__ == "__main__":
    main()

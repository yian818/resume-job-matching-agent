# metrics.py - 排序质量指标：MRR / NDCG@K
#
# 背景：Top-1/Top-3 是"二值"指标——只问"正确岗位进没进前K"，
#       排第2 和排第40 对指标毫无区别。但真实推荐系统里，
#       正确岗位排第2 和排第40 是天壤之别。
# 本脚本把评测日志的 rank 转成两个排序质量指标：
#   - MRR   (Mean Reciprocal Rank)：平均倒数排名
#   - NDCG@K (Normalized Discounted Cumulative Gain@K)：归一化折损累计增益
#
# 单标答设定下（每个 case 只有一个正确岗位）：
#   rank=1  → MRR贡献1.0，NDCG@3贡献 1/log2(2) = 1.000
#   rank=2  → MRR贡献0.5，NDCG@3贡献 1/log2(3) = 0.631
#   rank=3  → MRR贡献0.333，NDCG@3贡献 1/log2(4) = 0.500
#   rank=4+ → MRR贡献0，NDCG@3贡献 0
#   rank=-1 → 召回漏（正确岗位没进候选），MRR/NDCG都计 0
#
# 用法：
#   python eval/metrics.py --log output_p9_1_full.log
#   （--log 相对 eval/ 目录，和 eval_match_v2_batch.py 一致）

import argparse
import re
from pathlib import Path

# 每个 position 在 NDCG 里的折损系数（position 从1开始）
def dcg_contrib(pos: int, k: int) -> float:
    """正确岗位排第 pos 时，对 NDCG@k 的贡献（只有1个相关文档）"""
    if pos < 1 or pos > k:
        return 0.0
    # DCG 公式：rel / log2(pos+1)，单标答 rel=1
    import math
    return 1.0 / math.log2(pos + 1)


def parse_rank(line: str):
    """
    从一行评测日志解析 (rid, rank)。
    返回 rid, rank；失败/无标答行返回 None。
    rank 规则：1/2/3... 为正确岗位所在位置，-1 表示召回漏（rank:None 当漏算）。
    """
    rid_m = re.search(r"\b(R\d{3})\b", line)
    if not rid_m:
        return None, None
    rid = rid_m.group(1)
    if line.startswith("--") or line.startswith("XX"):
        return None, None  # 无标答/失败，不计入
    rank_m = re.search(r"rank:(\d+|None|-1)", line)
    if not rank_m:
        return None, None
    rank_str = rank_m.group(1)
    if rank_str == "None":
        rank = -1  # 召回漏，当 rank=-1 处理
    else:
        rank = int(rank_str)
    return rid, rank


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="output_p9_1_full.log", help="评测日志（相对 eval/）")
    parser.add_argument("--k", type=int, default=3, help="NDCG@k 的 k（默认3）")
    args = parser.parse_args()

    log_path = Path(__file__).parent / args.log
    if not log_path.exists():
        print(f"日志不存在: {log_path}")
        return

    results = []  # (rid, rank)
    for line in log_path.read_text(encoding="utf-8").splitlines():
        rid, rank = parse_rank(line)
        if rid is not None:
            results.append((rid, rank))

    total = len(results)
    if total == 0:
        print("没有可解析的评测行")
        return

    mrr = sum(1.0 / r if r >= 1 else 0.0 for _, r in results) / total
    ndcg = sum(dcg_contrib(r, args.k) for _, r in results) / total
    top1 = sum(1 for _, r in results if r == 1) / total
    top3 = sum(1 for _, r in results if r in (1, 2, 3)) / total

    print(f"评测日志: {args.log}")
    print(f"有效 case: {total}")
    print(f"{'-'*50}")
    print(f"Top-1   : {top1*100:6.1f}%  ({sum(1 for _,r in results if r==1)}/{total})")
    print(f"Top-3   : {top3*100:6.1f}%  ({sum(1 for _,r in results if r in (1,2,3))}/{total})")
    print(f"MRR     : {mrr:.4f}")
    print(f"NDCG@{args.k} : {ndcg:.4f}")
    print(f"{'-'*50}")

    # 逐 case 明细：按 rank 排序，把"排第二/第三/漏"的都摊开
    print("\n逐case明细（非rank=1的）：")
    for rid, r in sorted(results, key=lambda x: (x[1] if x[1] >= 0 else 999, x[0])):
        if r != 1:
            label = "召回漏" if r == -1 else f"rank{r} (MRR+{1.0/r:.3f} NDCG@{args.k}+{dcg_contrib(r,args.k):.3f})"
            print(f"  {rid}: {label}")

    print(f"\n丢失点：MRR 未满 1.000 的部分 = {1-mrr:.4f}，NDCG@{args.k} 未满 1.000 = {1-ndcg:.4f}")
    print(f"（这丢失点主要来自 rank2/rank3 的 case——正是后续要打磨的排序精度）")


if __name__ == "__main__":
    main()

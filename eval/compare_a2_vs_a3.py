# compare_a2_vs_a3.py - 对比 A2 基线 vs A3+A3.5 的全量评测结果
#
# 用法：评测跑完后运行
#   python eval/compare_a2_vs_a3.py <a2日志> <a3日志>
#
# A2 基线日志：eval/output_a2_full.log（上一轮评测的 tee 输出）
# A3 日志：   eval/output_a3_full.log（本轮评测的 tee 输出）
#
# 输出：
#   1. 两份日志各自的 Top-1 / Top-3 命中率（从评测报告区解析）
#   2. 逐 case 的 rank 对比（哪些变好、哪些变坏、哪些不变）
#   3. 重点标注：目标 case（R022 等）是否修复

import re
import sys
from pathlib import Path


def parse_log(path: str):
    """解析评测日志，返回 {rid: (status, rank)} 和统计信息"""
    results = {}
    top1 = top3 = total = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            # 逐 case 行：OK [1/50] R001 张明 | truth:... | top1:... | rank:1
            m = re.match(r"^(OK|XX|--) \[(\d+)/50\] (R\d{3}) .*?rank:(-?\d+)", line)
            if m:
                status, idx, rid, rank = m.groups()
                results[rid] = (status, int(rank))
            # 评测报告统计区
            m2 = re.match(r"Top-1命中率:\s*(\d+)/(\d+)\s*=\s*([\d.]+)%", line)
            if m2:
                top1 = int(m2.group(1)); total = int(m2.group(2))
            m3 = re.match(r"Top-3命中率:\s*(\d+)/(\d+)", line)
            if m3:
                top3 = int(m3.group(1))
    return results, (top1, top3, total)


def main():
    a2_path = sys.argv[1] if len(sys.argv) > 1 else "eval/output_a2_full.log"
    a3_path = sys.argv[2] if len(sys.argv) > 2 else "eval/output_a3_full.log"

    a2, a2_stat = parse_log(a2_path)
    a3, a3_stat = parse_log(a3_path)

    print("=" * 64)
    print("A2 基线 vs A3+A3.5 全量评测对比")
    print("=" * 64)
    t1, t3, tot = a2_stat
    if t1 is not None:
        print(f"\nA2 基线 : Top-1 {t1}/{tot} = {t1/tot*100:.1f}% | Top-3 {t3}/{tot} = {t3/tot*100:.1f}%")
    t1, t3, tot = a3_stat
    if t1 is not None:
        print(f"A3 本轮 : Top-1 {t1}/{tot} = {t1/tot*100:.1f}% | Top-3 {t3}/{tot} = {t3/tot*100:.1f}%")

    # 逐 case 对比
    print("\n--- 逐 case rank 对比（+变好 / -变坏 / =不变）---")
    all_rids = sorted(set(a2) | set(a3), key=lambda r: int(r[1:]))
    better, worse, same, missing = [], [], [], []
    for rid in all_rids:
        if rid not in a2:
            missing.append(rid); continue
        if rid not in a3:
            missing.append(rid); continue
        r2, r3 = a2[rid][1], a3[rid][1]
        if r3 < r2:
            better.append((rid, r2, r3))
        elif r3 > r2:
            worse.append((rid, r2, r3))
        else:
            same.append((rid, r2))

    print(f"变好 {len(better)} 个：")
    for rid, r2, r3 in better:
        print(f"  {rid}: rank {r2} → {r3}")
    print(f"变坏 {len(worse)} 个：")
    for rid, r2, r3 in worse:
        print(f"  {rid}: rank {r2} → {r3}")
    print(f"不变 {len(same)} 个（其中 rank=1 的 {sum(1 for _, r in same if r == 1)} 个）")
    if missing:
        print(f"缺失 {len(missing)} 个：{missing}")


if __name__ == "__main__":
    main()

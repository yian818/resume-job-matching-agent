# eval/extraction_audit.py - 抽取层完整性体检（P7 第一步）
#
# 目的：量化 LLM 抽取简历技能时的"漏抽率"。
# 方法：拿真实评测日志里每份简历的 LLM 抽取结果，与简历原文的
#       「技能：」「技术栈：」行逐词对比，找出"原文有、但没被抽出"的技能。
#
# 为什么重要：抽取是整条链路源头。源头漏了技能 → 检索 query 缺特征词
#            → 真命岗位进不了候选（R015 就是这么漏的）。
#
# 用法：python eval/extraction_audit.py <评测输出日志路径>
# 输出：eval/extraction_audit.md

import ast
import json
import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from eval.eval_dataset import RESUMES
from scoring_rules import _normalize_skill


def parse_extractions(log_path: Path) -> dict:
    """从评测日志里解析 抽取成功：{'name':..., 'skill':[...]}"""
    by_name = {}
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "抽取成功：" not in line:
            continue
        payload = line.split("抽取成功：", 1)[1].strip()
        try:
            data = ast.literal_eval(payload)
        except Exception:
            continue
        if isinstance(data, dict) and data.get("name"):
            by_name[data["name"]] = data.get("skill", [])
    return by_name


def literal_skills(text: str) -> list:
    """从简历原文的 技能：/技术栈： 行提取技能词（客观原文，去括号备注）"""
    out = []
    for pattern in (r"技能：(.+)", r"技术栈：(.+)"):
        m = re.search(pattern, text)
        if not m:
            continue
        for s in re.split(r"[,，、]", m.group(1)):
            s = re.sub(r"[（(].*?[)）]", "", s.strip()).strip().rstrip("。")
            if s:
                out.append(s)
    return out


def main():
    if len(sys.argv) < 2:
        print("用法: python eval/extraction_audit.py <评测输出日志>")
        sys.exit(1)
    log_path = Path(sys.argv[1])
    extractions = parse_extractions(log_path)
    print(f"从日志解析到 {len(extractions)} 份抽取结果\n")

    rows = []
    total_literal = total_missing = 0

    for r in RESUMES:
        rid = r["resume_id"]
        name = r.get("expected_resume", {}).get("name", "")
        if name not in extractions:
            continue
        extracted = {_normalize_skill(s) for s in extractions[name]}
        literals = literal_skills(r["resume_text"])
        literal_norm = {_normalize_skill(s) for s in literals}

        missing = sorted(literal_norm - extracted)
        total_literal += len(literal_norm)
        total_missing += len(missing)
        rows.append((rid, name, sorted(literal_norm), sorted(extracted), missing))

    # 输出报告
    lines = ["# 抽取层完整性体检（P7）\n",
             "> 对比：简历原文「技能/技术栈」行 vs LLM 实际抽取结果。\n",
             "> 漏抽 = 原文写了、但 LLM 没抽出来的技能。\n"]
    lines.append(f"- 参与统计：{len(rows)} 份")
    lines.append(f"- 原文技能词总数：{total_literal}")
    lines.append(f"- 漏抽技能词总数：{total_missing}")
    lines.append(f"- 平均漏抽率：{total_missing/total_literal*100:.1f}%\n")
    lines.append("---\n")
    lines.append("## 有漏抽的简历\n")
    lines.append("| case | 姓名 | 原文技能 | LLM抽出 | **漏抽** |")
    lines.append("|---|---|---|---|---|")
    for rid, name, lit, ext, miss in rows:
        if not miss:
            continue
        lines.append(f"| {rid} | {name} | {', '.join(lit)} | {', '.join(ext)} | **{', '.join(miss)}** |")

    lines.append("\n---\n")
    lines.append("## 全部明细（含无漏抽）\n")
    lines.append("| case | 姓名 | 漏抽数 | 漏抽技能 |")
    lines.append("|---|---|---|---|")
    for rid, name, lit, ext, miss in rows:
        lines.append(f"| {rid} | {name} | {len(miss)} | {', '.join(miss) if miss else '—'} |")

    out = Path(__file__).parent / "extraction_audit.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    # 控制台摘要
    print(f"{'case':<6}{'姓名':<8}{'漏抽'}")
    print("-" * 70)
    for rid, name, lit, ext, miss in rows:
        if miss:
            print(f"{rid:<6}{name:<8}{', '.join(miss)}")
    print()
    print(f"漏抽率: {total_missing}/{total_literal} = {total_missing/total_literal*100:.1f}%")
    print(f"报告已生成: {out}")


if __name__ == "__main__":
    main()

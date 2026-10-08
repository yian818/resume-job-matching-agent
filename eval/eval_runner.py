"""
eval_runner.py - P1-Step1: 评测简历结构化抽取准确率

用法：
    python eval_runner.py              # 跑全部50份
    python eval_runner.py --limit 5    # 只跑前5份（先测试用）
"""

import sys
import time
import json
import re
from collections import defaultdict

from eval_dataset import RESUMES
from nodes import extract_resume_node
from state import AgentState


def run_parsing_eval(limit=None):
    """跑简历解析评测"""
    samples = RESUMES[:limit] if limit else RESUMES

    print("=" * 60)
    print(f"P1-Step1: 简历结构化抽取评测（共{len(samples)}份）")
    print("=" * 60)

    total = 0
    field_stats = defaultdict(lambda: {"correct": 0, "total": 0})
    errors = []
    time_records = []

    for i, sample in enumerate(samples):
        rid = sample["resume_id"]
        expected = sample["expected_resume"]

        state: AgentState = {
            "resume_text": sample["resume_text"],
            "resume_info": None,
            "jobs": [],
            "report": "",
            "error": None,
            "info_complete": True,
        }

        t0 = time.time()
        try:
            result_state = extract_resume_node(state)
            elapsed = time.time() - t0
            time_records.append(elapsed)
        except Exception as e:
            print(f"  ✗ [{i+1}/{len(samples)}] {rid}: 调用失败 - {e}")
            errors.append({"rid": rid, "error": str(e)})
            continue

        actual = result_state.get("resume_info", {})
        sample_errors = []

        # name 精确匹配
        field_stats["name"]["total"] += 1
        if actual.get("name", "").strip() == expected.get("name", "").strip():
            field_stats["name"]["correct"] += 1
        else:
            sample_errors.append(f"name: 期望[{expected.get('name')}] 实际[{actual.get('name')}]")

        # education 精确匹配
        field_stats["education"]["total"] += 1
        if actual.get("education", "").strip() == expected.get("education", "").strip():
            field_stats["education"]["correct"] += 1
        else:
            sample_errors.append(f"education: 期望[{expected.get('education')}] 实际[{actual.get('education')}]")

        # work_year 数字匹配（±1年算对）
        field_stats["work_year"]["total"] += 1
        exp_years = _extract_years(expected.get("work_year", ""))
        act_years = actual.get("work_year", -1)
        if exp_years is not None and act_years and act_years > 0:
            if abs(act_years - exp_years) <= 1:
                field_stats["work_year"]["correct"] += 1
            else:
                sample_errors.append(f"work_year: 期望{exp_years}年 实际{act_years}年")
        else:
            sample_errors.append(f"work_year: 无法解析 期望[{expected.get('work_year')}] 实际[{act_years}]")

        # skill 列表交集匹配
        field_stats["skill"]["total"] += 1
        actual_skills = _normalize_skills(actual.get("skill", []))
        expected_skills = _normalize_skills(expected.get("skills", []))
        if expected_skills:
            overlap = len(actual_skills & expected_skills)
            ratio = overlap / len(expected_skills)
            if ratio >= 0.5:
                field_stats["skill"]["correct"] += 1
            else:
                sample_errors.append(
                    f"skill: 命中{overlap}/{len(expected_skills)} 期望{expected_skills} 实际{list(actual_skills)[:6]}"
                )

        total += 1
        status = "✓" if not sample_errors else "✗"
        print(f"  {status} [{i+1}/{len(samples)}] {rid} ({elapsed:.1f}s)")
        for e in sample_errors[:2]:
            print(f"      → {e}")
        if sample_errors:
            errors.append({"rid": rid, "errors": sample_errors})

    # ============================================================
    # 输出报告
    # ============================================================
    print("\n" + "=" * 60)
    print("评测报告")
    print("=" * 60)

    print(f"\n成功解析: {total}/{len(samples)} 份")
    if time_records:
        avg_time = sum(time_records) / len(time_records)
        print(f"平均耗时: {avg_time:.1f}s/份")

    print(f"\n各字段准确率:")
    for field in ["name", "education", "work_year", "skill"]:
        s = field_stats[field]
        if s["total"] > 0:
            acc = s["correct"] / s["total"]
            bar = "█" * int(acc * 20) + "░" * (20 - int(acc * 20))
            print(f"  {field:12s} {acc:6.1%}  {bar}  ({s['correct']}/{s['total']})")

    total_correct = sum(s["correct"] for s in field_stats.values())
    total_fields = sum(s["total"] for s in field_stats.values())
    overall = total_correct / max(total_fields, 1)
    print(f"\n  {'总体字段':12s} {overall:6.1%}  ({total_correct}/{total_fields})")

    if errors:
        print(f"\n有错误的简历: {len(errors)} 份")
        error_types = defaultdict(int)
        for e in errors:
            for err in e.get("errors", []):
                field_name = err.split(":")[0].strip()
                error_types[field_name] += 1
        for field, count in sorted(error_types.items(), key=lambda x: -x[1]):
            print(f"    {field}: {count}次")

    report = {
        "total": total,
        "avg_time": sum(time_records) / len(time_records) if time_records else 0,
        "field_accuracy": {
            f: {"correct": s["correct"], "total": s["total"],
                "accuracy": round(s["correct"] / max(s["total"], 1), 3)}
            for f, s in field_stats.items()
        },
        "overall_accuracy": round(overall, 3),
        "errors": errors[:20],
    }
    with open("eval_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n详细报告已保存到 eval_report.json")
    return report


def _extract_years(text):
    if not text:
        return None
    match = re.search(r"(\d+)", str(text))
    return int(match.group(1)) if match else None

# 中英文技能同义词映射
SKILL_SYNONYMS = {
    "english": "英语", "german": "德语", "french": "法语",
    "project management": "项目管理", "team management": "团队管理",
    "cross-border e-commerce": "跨境电商", "supply chain": "供应链管理",
    "clinical medicine": "临床医学", "endocrinology": "内分泌",
    "ai healthcare": "ai医疗", "ai security": "ai安全",
    "llm security": "llm安全", "penetration testing": "渗透测试",
    "photoshop": "ps", "illustrator": "ai",
    "curriculum design": "课程设计", "brand strategy": "品牌策划",
    "copywriting": "文案", "performance": "表演", "acting": "表演",
    "surgery": "外科手术", "veterinary medicine": "兽医临床",
    "cultural heritage conservation": "文物保护", "ceramics": "陶瓷修复",
    "organic materials": "有机材料", "spectroscopy": "光谱分析",
    "food science": "食品科学", "r&d": "研发",
    "maritime navigation": "航海技术", "marine engineering": "轮机工程",
    "ic design": "芯片设计", "chip architecture": "芯片架构",
    "legal compliance": "法律合规", "ip law": "知识产权",
}


def _normalize_skills(skills):
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.replace("，", ",").replace("、", ",").split(",")]
    result = set()
    for s in skills:
        s = s.strip().lower()
        if not s:
            continue
        # 如果命中同义词映射，用中文形式
        s = SKILL_SYNONYMS.get(s, s)
        result.add(s)
    return result


if __name__ == "__main__":
    limit = None
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        limit = int(sys.argv[idx + 1])
    run_parsing_eval(limit)

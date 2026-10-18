# label_audit_v3.py - 标答 vs 简历客观事实 逐份复核
#
# 输出每份简历的：标答 / 工作经历职位行 / 技能行
# 用途：人工扫一遍，找出"标答与简历工作经历职位不符"的情况。
# 只读，不改任何数据。
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from eval_dataset import RESUMES

answers = json.load(open(Path(__file__).parent / "manual_answers.json", encoding="utf-8"))["answers"]

out = []
for r in RESUMES:
    rid = r["resume_id"]
    text = r["resume_text"]
    label = answers.get(rid)
    # 工作经历行：以 "- " 开头的行
    work_lines = [ln.strip() for ln in text.splitlines() if ln.strip().startswith("- ")]
    # 技能行
    skill_line = ""
    for ln in text.splitlines():
        if ln.strip().startswith("技能：") or ln.strip().startswith("技术栈："):
            skill_line = ln.strip()
            break
    out.append(f"### {rid} | 标答：{label}")
    for w in work_lines:
        out.append(f"  {w}")
    if skill_line:
        out.append(f"  {skill_line}")
    out.append("")

Path(Path(__file__).parent / "label_audit_v3.md").write_text("\n".join(out), encoding="utf-8")
print(f"已生成 eval/label_audit_v3.md（{len(RESUMES)} 份）")

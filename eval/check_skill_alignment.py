# eval/check_skill_alignment.py - 验证岗位技能(英文) 与 简历技能(中文) 是否归一化对齐
# 背景：标答复核出现10个疑似错标，怀疑根因是岗位key_skills用英文、
#       简历技能用中文，SKILL_SYNONYMS只做了单项映射，导致硬规则重合判定为0。
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from scoring_rules import _normalize_skill

pairs = [
    ("English", "英语"),
    ("Clinical Research", "临床医学"),
    ("PhD Medicine", "医学"),
    ("FDA", "药品"),
    ("AI Product", "产品管理"),
    ("Prompt Engineering", "提示词工程"),
    ("Data Analysis", "数据分析"),
    ("Mechanical Design", "机械设计"),
    ("Quantitative Trading", "量化"),
    ("Cross-border Trade", "跨境电商"),
    ("B2B", "外贸"),
    ("Sensor Fusion", "传感器融合"),
    ("Perception", "感知"),
    ("Computer Vision", "计算机视觉"),
    ("Penetration Testing", "渗透测试"),
    ("Extension Services", "农技推广"),
]

print(f"{'岗位技能(英文)':<22} {'简历技能(中文)':<16} {'归一化对齐?'}")
print("-" * 58)
for a, b in pairs:
    na = _normalize_skill(a)
    nb = _normalize_skill(b)
    mark = "✓" if na == nb else "✗"
    print(f"{a:<22} {b:<16} {mark}   ({na!r} vs {nb!r})")

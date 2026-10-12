# scoring_rules.py - 规则打分引擎（确定性基线 + 硬上限）
#
# 背景：P1 留下的 SCORING_RULES 只是配置表，从未真正生效；
# LLM 打分是概率性的，会出现"核心技能完全不沾边还给70分"的翻车（如R044）。
# 本模块把权重表升级成真正生效的规则引擎，做两件事：
#   1. compute_rule_score：纯规则确定性打分（0-100），给LLM分数做锚点
#   2. hard_cap：硬性分数上限——核心技能重合越少，上限越低，
#      从机制上保证"完全不匹配的岗位永远上不了Top-1"
#
# 面试点：这是"LLM打分不稳定"问题的工程解法——不赌LLM自觉，用确定性规则兜底。

# 四维权重（和 nodes.py 里 LLM prompt 的打分维度保持一致）
SCORING_RULES = {
    "skill_match": {"weight": 0.4, "description": "技能匹配度：岗位要求技能与候选人技能重合度"},
    "education":   {"weight": 0.1, "description": "学历匹配：本科及以上满足要求"},
    "experience":  {"weight": 0.3, "description": "工作年限匹配：候选人年限与岗位要求差距"},
    "project":     {"weight": 0.2, "description": "项目相关度：项目经历与岗位方向相关性"},
}

# 技能中英文同义词归一化（与 eval_runner.py 的 SKILL_SYNONYMS 同一套）
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

# 学历等级：数值越高学历越高
EDU_RANK = {"博士": 3, "硕士": 2, "本科": 1, "大专": 0, "高中": 0}


def _normalize_skill(skill: str) -> str:
    """技能词归一化：去空白、小写、同义词映射"""
    s = skill.strip().lower()
    return SKILL_SYNONYMS.get(s, s)


def skill_overlap(job: dict, resume_info: dict) -> set:
    """简历技能 ∩ 岗位要求技能 的重合集合（归一化后）"""
    job_skills = {_normalize_skill(s) for s in job["required_skills"].split(",")}
    resume_skills = {_normalize_skill(s) for s in resume_info.get("skill", [])}
    return job_skills & resume_skills


def hard_cap(job: dict, resume_info: dict) -> int:
    """
    硬性分数上限（0-100）：
      - 核心技能完全不沾边  → 25（永远不该排第一）
      - 只会1个核心技能      → 40
      - 只会2个核心技能      → 60
      - 会3个及以上          → 100（不限）
    无论LLM打多少分，最终分数 = min(融合分, 硬上限)。
    """
    n = len(skill_overlap(job, resume_info))
    if n == 0:
        return 25
    if n == 1:
        return 40
    if n == 2:
        return 60
    return 100


def compute_rule_score(job: dict, resume_info: dict) -> int:
    """
    纯规则确定性打分（0-100），四维加权，和LLM prompt的维度一一对应：
      - 技能(40) = 40 × (岗位要求技能中被候选人覆盖的比例)
      - 学历(10) = 候选人学历 >= 岗位要求 → 10，否则 3
      - 年限(30) = 达到要求30，差1年20，差2年12，差更多5
      - 项目(20) = 无法纯规则判断，给中性分10（语义交给LLM）
    最终再受 hard_cap 约束。
    """
    overlap = skill_overlap(job, resume_info)
    job_skills = {_normalize_skill(s) for s in job["required_skills"].split(",")}

    # 技能分（40）
    if job_skills:
        skill_score = 40 * len(overlap) / len(job_skills)
    else:
        skill_score = 20

    # 学历分（10）
    cand_edu = EDU_RANK.get(resume_info.get("education", ""), 0)
    req_edu = EDU_RANK.get(job.get("education", "本科"), 1)
    edu_score = 10 if cand_edu >= req_edu else 3

    # 年限分（30）
    years = resume_info.get("work_year", 0) or 0
    req_years = job.get("required_years", 1)
    gap = years - req_years
    if gap >= 0:
        years_score = 30
    elif gap >= -1:
        years_score = 20
    elif gap >= -2:
        years_score = 12
    else:
        years_score = 5

    # 项目分（20）——纯规则无法判断语义相关度，给中性分
    project_score = 10

    total = round(skill_score + edu_score + years_score + project_score)
    return min(total, hard_cap(job, resume_info))


if __name__ == "__main__":
    # 自测1：张明 vs AI Agent工程师（应该高分）
    zhang = {"skill": ["Python", "LangGraph", "RAG", "LLM"], "education": "硕士", "work_year": 6}
    agent_job = {"title": "AI Agent工程师", "required_skills": "Python,LangGraph,RAG,LLM", "education": "本科", "required_years": 3}
    print(f"张明 → AI Agent工程师：规则分{compute_rule_score(agent_job, zhang)}，硬上限{hard_cap(agent_job, zhang)}")

    # 自测2：张明 vs 农业技术推广专员（应该被硬上限压制）
    farm_job = {"title": "农业技术推广专员", "required_skills": "Agriculture,Extension Services", "education": "本科", "required_years": 1}
    print(f"张明 → 农业技术推广：规则分{compute_rule_score(farm_job, zhang)}，硬上限{hard_cap(farm_job, zhang)}")

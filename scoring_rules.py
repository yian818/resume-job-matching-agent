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
    "cross-border e-commerce": "跨境电商", "supply chain": "供应链",
    "供应链管理": "供应链", "跨境电商运营": "跨境电商",
    "clinical medicine": "临床医学", "endocrinology": "内分泌",
    "ai healthcare": "ai医疗", "ai security": "ai安全",
    "llm security": "llm安全", "penetration testing": "渗透测试",
    "photoshop": "ps", "illustrator": "ai",
    "curriculum design": "课程研发", "课程设计": "课程研发",
    "brand strategy": "品牌营销", "品牌策划": "品牌营销",
    "copywriting": "文案", "创意文案": "文案",
    "performance": "表演", "acting": "表演",
    "surgery": "外科手术", "veterinary medicine": "兽医", "兽医临床": "兽医",
    "cultural heritage conservation": "文物保护", "ceramics": "陶瓷修复",
    "organic materials": "有机材料", "spectroscopy": "光谱分析",
    "food science": "食品科学", "食品化学": "食品科学",
    "配方研发": "配方", "r&d": "研发",
    "maritime navigation": "航海技术", "marine engineering": "轮机工程",
    "ic design": "芯片设计", "chip architecture": "芯片架构",
    "legal compliance": "法律合规", "ip law": "知识产权",
    # 通用技术词等价（词粒度归一化）
    "5g协议": "5g", "c语言": "c",
    "product management": "产品管理",
    "尽职调查": "尽调",
    "纺织材料": "纺织工程",
}


def _normalize_skill(skill: str) -> str:
    """技能词归一化：去空白、小写、同义词映射"""
    s = skill.strip().lower()
    return SKILL_SYNONYMS.get(s, s)


# 学历等级：数值越高学历越高
EDU_RANK = {"博士": 3, "硕士": 2, "本科": 1, "大专": 0, "高中": 0}

# 岗位技能域扩充（A3.5 核心）：
# 解决"岗位技能表太薄导致字面重合稀疏"的根因问题（如R022韩冰：
# 做推荐系统/时空预测，字面上和数据分析师只有Python重合，被hard_cap误伤到40分）。
# 扩充的是【岗位侧】的技能域（行业知识，可补全），不动简历侧（真实数据）。
# 原则：
#   1. 只给"技能域广"的软技能岗/交叉岗扩充（技术岗技能已具体，不需要）
#   2. 扩充词只加该岗位真正的工作内容，不加泛词（如"沟通""办公软件"），避免人人匹配
#   3. hard_cap判定用扩充后重合数，但技能覆盖率分母用扩充后的完整技能域
JOB_SKILL_EXPANSION = {
    "数据分析师": ["数据挖掘", "统计分析", "推荐系统", "特征工程", "机器学习", "数据可视化", "AB测试", "ETL", "数据仓库"],
    "AI产品经理": ["产品管理", "需求分析", "数据分析", "AIGC", "大模型", "用户研究", "原型设计", "Prompt Engineering"],
    "产品运营专员": ["内容运营", "用户运营", "活动策划", "数据分析", "用户增长", "社区运营"],
    "AI Agent工程师": ["Agent", "工具调用", "Function Calling", "提示词工程", "应用开发", "MCP", "Prompt Engineering"],
    "量化交易研究员": ["量化", "金融建模", "因子分析", "回测", "高频交易", "机器学习", "风险管理"],
    "AI安全研究员": ["对抗攻击", "越狱防御", "安全评测", "红队", "模型安全", "漏洞分析"],
    "临床研发经理": ["临床试验", "药品注册", "医学事务", "临床运营", "GCP", "数据管理"],
    "外贸业务员": ["跨境电商", "海外市场", "客户开发", "商务英语", "外贸单证", "物流管理"],
    "人力资源BP": ["招聘", "绩效管理", "组织发展", "员工关系", "薪酬管理", "人才盘点"],
}


def _job_skill_domain(job: dict) -> set:
    """岗位完整技能域 = 原始必需技能 + 扩充技能（用于判定重合和覆盖率）"""
    base = {_normalize_skill(s) for s in job["required_skills"].split(",")}
    expanded = {_normalize_skill(s) for s in JOB_SKILL_EXPANSION.get(job.get("title", ""), [])}
    return base | expanded


def skill_overlap(job: dict, resume_info: dict) -> set:
    """简历技能 ∩ 岗位技能域 的重合集合（归一化后）"""
    job_skills = _job_skill_domain(job)
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

    P8 修复：硬上限只该挡"不相关岗位"。若候选人的职业身份(career)与
    岗位职能类别匹配（career_match_score=20），说明这是相关岗位，
    不该被字面技能重合数误伤（R004 AI产品经理 / R039 纺织面料 的教训：
    LLM/重排/职业身份都判对，却被 cap=60/40 压死）。
    """
    base = {0: 25, 1: 40, 2: 60}.get(len(skill_overlap(job, resume_info)), 100)
    if career_match_score(job, resume_info) == 20:
        return 100
    return base


# ===== P8：职业身份匹配 =====
# 问题：R004 金融产品经理 的 skills 含 SQL/Python/数据分析，规则层把它当"数据分析师"
#       压过"AI产品经理"。但候选人的真实职位是产品经理——职业身份是最强的匹配信号。
# 解法：把简历的 career（真实职位）与岗位标题做"职能类别"比对，类别有交集则加分。
#       这是确定性规则，不依赖 LLM；同时 reranker 的简历文本也会带上 career。
ROLE_SYNONYMS = {
    # 职能角色
    "产品经理": "产品", "产品负责人": "产品", "产品规划": "产品", "产品": "产品",
    "运营": "运营",
    "研究员": "研究", "行业研究": "研究", "研究": "研究",
    "数据分析": "数据", "数据分析师": "数据", "分析师": "分析", "分析": "分析",
    "设计师": "设计", "设计": "设计",
    "用户研究": "用户研究",
    "教师": "教育", "教研": "教育", "教学": "教育",
    "翻译": "翻译",
    "法务": "法务", "律师": "法务",
    "评估": "评估", "会计": "财务", "财务": "财务", "审计": "财务",
    "量化": "量化", "金融": "金融",
    # 技术/领域
    "算法": "算法", "视觉": "视觉", "视频": "视频", "nlp": "nlp", "大模型": "大模型",
    "自动驾驶": "自动驾驶", "机器人": "机器人", "芯片": "芯片", "量子": "量子",
    "通信": "通信", "协议": "通信", "网络运维": "运维", "运维": "运维", "测试": "测试",
    # 工程/行业
    "建筑": "建筑", "结构": "结构", "给排水": "给排水", "隧道": "隧道",
    "材料": "材料", "纺织": "纺织", "面料": "纺织", "显示": "显示", "oled": "显示",
    "食品": "食品", "供应链": "供应链", "跨境电商": "跨境", "外贸": "跨境",
    "海外运营": "跨境", "跨境": "跨境",   # P9.1：海外运营/跨境电商 = 跨境/外贸职能
    "自助驾驶": "自动驾驶",              # P9.1：错别字容错（真实简历常见"自助驾驶"）
    "临床": "医疗", "医学": "医疗", "医生": "医疗", "兽医": "兽医",
    "插画": "插画", "演员": "表演", "表演": "表演", "修复": "文博", "文物": "文博",
    "航海": "航运", "船长": "航运", "轮机": "航运", "航运": "航运",
}


def _role_categories(text: str) -> set:
    """从职位/岗位名中提取职能类别集合（按关键词命中）"""
    t = (text or "").lower()
    return {cat for word, cat in ROLE_SYNONYMS.items() if word in t}


def career_match_score(job: dict, resume_info: dict) -> int:
    """
    职业身份匹配分（0-20）：
      候选人真实职位(career) 与 岗位标题 的职能类别有交集 → 20 分，否则 0。
    例：career='金融产品经理' → {产品}；岗位'AI产品经理' → {产品} → 20 分
        岗位'数据分析师' → {数据,分析} → 无交集 → 0 分
    """
    career_cats = _role_categories(resume_info.get("career", ""))
    job_cats = _role_categories(job.get("title", ""))
    if career_cats and job_cats and (career_cats & job_cats):
        return 20
    return 0


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
    job_domain = _job_skill_domain(job)  # 扩充后的完整技能域（原始必需 + 同义扩充）

    # 技能分（40）：分子=触及技能数，分母=完整技能域（防止扩充稀释分数）
    if job_domain:
        skill_score = 40 * len(overlap) / len(job_domain)
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

    # 职业身份分（20，P8）——候选人真实职位与岗位职能类别匹配则加分
    career_score = career_match_score(job, resume_info)

    total = round(skill_score + edu_score + years_score + project_score + career_score)
    return min(total, hard_cap(job, resume_info))


if __name__ == "__main__":
    # 自测1：张明 vs AI Agent工程师（应该高分）
    zhang = {"skill": ["Python", "LangGraph", "RAG", "LLM"], "education": "硕士", "work_year": 6}
    agent_job = {"title": "AI Agent工程师", "required_skills": "Python,LangGraph,RAG,LLM", "education": "本科", "required_years": 3}
    print(f"张明 → AI Agent工程师：规则分{compute_rule_score(agent_job, zhang)}，硬上限{hard_cap(agent_job, zhang)}")

    # 自测2：张明 vs 农业技术推广专员（应该被硬上限压制）
    farm_job = {"title": "农业技术推广专员", "required_skills": "Agriculture,Extension Services", "education": "本科", "required_years": 1}
    print(f"张明 → 农业技术推广：规则分{compute_rule_score(farm_job, zhang)}，硬上限{hard_cap(farm_job, zhang)}")

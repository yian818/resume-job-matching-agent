# 打分规则配置
SCORING_RULES = {
    "skill_match": {
        "weight": 0.4,
        "description": "技能匹配度：岗位要求的技能与候选人技能重合度"
    },
    "education": {
        "weight": 0.1,
        "description": "学历匹配：本科及以上满足要求"
    },
    "experience": {
        "weight": 0.3,
        "description": "工作年限匹配：候选人年限与岗位要求差距"
    },
    "project": {
        "weight": 0.2,
        "description": "项目相关度：项目经历与岗位方向相关性"
    }
}

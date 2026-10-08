from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    # 原始简历文本
    resume_text: str
    # 抽取后的结构化简历信息
    resume_info: Optional[dict]
    # 匹配到的岗位列表
    jobs: List[dict]
    # 匹配报告
    report: str
    # 错误信息
    error: Optional[str]
    
    info_complete: bool
    
    # === Human-in-the-loop 新增字段 ===
    # 缺失的字段列表
    missing_fields: List[str]
    # 追问问题
    follow_up_question: str
    # 用户补充的回答
    user_answer: str
    # 是否需要人工介入
    needs_human: bool


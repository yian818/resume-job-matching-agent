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

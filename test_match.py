"""
test_match.py - 测试单份简历匹配
"""
from nodes import extract_resume_node, match_jobs_node

# 张明的简历测试
test_resume = """张明，男，30岁，硕士学历，6年工作经验。
技能：Python, PyTorch, LangGraph, RAG, LLM, FastAPI, Docker
项目经历：主导开发AI客服Agent，基于LangGraph搭建多节点工作流，支持多轮对话和工具调用，日均处理5000+请求。"""

state = {
    "resume_text": test_resume,
    "resume_info": None,
    "jobs": [],
    "report": "",
    "error": None,
    "info_complete": True,
}

print("=== 开始测试 ===")
state = extract_resume_node(state)
print("\n=== 匹配结果 ===")
state = match_jobs_node(state)
print("\n" + state["report"])

from langgraph.graph import StateGraph, END
from state import AgentState
from nodes import extract_resume_node, match_jobs_node

def build_agent():
    """构建简历撮合Agent"""
    # 创建状态图
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("extract_resume", extract_resume_node)
    workflow.add_node("match_jobs", match_jobs_node)
    
    # 设置入口
    workflow.set_entry_point("extract_resume")
    
    # 连线：抽取简历 → 匹配岗位 → 结束
    workflow.add_edge("extract_resume", "match_jobs")
    workflow.add_edge("match_jobs", END)
    
    return workflow.compile()

if __name__ == "__main__":
    # 测试用例：模拟一段简历文本
    test_resume = """
    李博文，北方民族大学计算机科学与技术本科，2026届。
    技能：Python, LangGraph, LLM, RAG, 智能体评测。
    项目：独立开发AI招聘Agent，基于LangGraph实现简历解析、岗位匹配打分全流程。
    """
    
    agent = build_agent()
    result = agent.invoke({
        "resume_text": test_resume,
        "resume_info": None,
        "jobs": [],
        "report": "",
        "error": None
    })
    
    print("\n" + "="*50)
    print("最终匹配报告：")
    print("="*50)
    print(result["report"])

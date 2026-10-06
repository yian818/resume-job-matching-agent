from langgraph.graph import StateGraph, END
from nodes import extract_resume_node, match_jobs_node, ask_more_node


from state import AgentState


def build_agent():
    """构建简历撮合Agent"""
    # 创建状态图
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("ask_more", ask_more_node)
    workflow.add_node("extract_resume", extract_resume_node)
    workflow.add_node("match_jobs", match_jobs_node)
    
    # 设置入口
    workflow.set_entry_point("extract_resume")
    
    # 连线：抽取简历 → 匹配岗位 → 结束
    # 条件分支：信息完整才匹配，不完整走追问
    def should_match(state: AgentState) -> str:
        if state['info_complete']:
            return "match_jobs"
        else:
            return "ask_more"

    workflow.add_conditional_edges("extract_resume", should_match, {
    "match_jobs": "match_jobs",
    "ask_more": "ask_more"
})
    workflow.add_edge("ask_more", END)


    workflow.add_edge("match_jobs", END)
    
    return workflow.compile()

if __name__ == "__main__":
    # 测试用例：模拟一段简历文本
    test_resume = """
    李博文，北方民族大学计算机科学与技术本科，2025届 签约AI评测工程师 工作2年。
    技能：Python, LangGraph, LLM, RAG, 智能体评测。
    项目：独立开发AI招聘Agent，基于LangGraph实现简历解析、岗位匹配打分全流程。
    """
    
    agent = build_agent()
    # 运行Agent
    result = agent.invoke({
        "resume_text": test_resume,
        "resume_info": None,
        "jobs": [],
        "report": "",
        "error": None,
        "info_complete": False
    })
    
    print("\n" + "="*50)
    print("最终匹配报告：")
    print("="*50)
    print(result["report"])

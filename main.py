from langgraph.graph import StateGraph, END
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from nodes import extract_resume_node, match_jobs_node, ask_more_node, resume_optimize_node, interview_question_node
from resume_parser import read_pdf


from state import AgentState


def build_agent():
    """构建简历撮合Agent"""
    # 创建状态图
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("resume_optimize", resume_optimize_node)
    workflow.add_node("interview_question", interview_question_node)
    workflow.add_node("ask_more", ask_more_node)
    workflow.add_node("extract_resume", extract_resume_node)
    workflow.add_node("match_jobs", match_jobs_node)
    
    # 设置入口
    workflow.set_entry_point("extract_resume")
    
    # 连线：抽取简历 → 匹配岗位 → 结束
    # 条件分支：信息完整才匹配，不完整走追问
    def should_match(state: AgentState) -> str:
        if state.get('info_complete', False):
            return "match_jobs"
        else:
            return "ask_more"
        

    workflow.add_conditional_edges("extract_resume", should_match, {
    "match_jobs": "match_jobs",
    "ask_more": "ask_more"
})
    workflow.add_edge("ask_more", "extract_resume")


    workflow.add_edge("match_jobs", "resume_optimize")
    workflow.add_edge("resume_optimize", "interview_question")
    workflow.add_edge("interview_question", END)
 
    
    return workflow.compile()

# 测试代码只在直接运行main.py时执行，import时不执行
if __name__ == "__main__":
    # 测试用例：模拟一段简历文本
    test_resume = read_pdf(r"C:\Users\LBW\Desktop\李博文-AI-Agent工程师求职简历.pdf")

    agent = build_agent()
    # 运行Agent
    result = agent.invoke({
        "resume_text": test_resume,
        "resume_info": None,
        "jobs": [],
        "report": "",
        "error": None,
        "info_complete": True
    })
    
    logger.info("\n" + "="*50)
    logger.info("最终匹配报告：")
    logger.info("="*50)
    logger.info(result["report"])

    # 保存报告到文件
    with open("匹配报告.md", "w", encoding="utf-8") as f:
        f.write(result['report'])
    logger.info("报告已保存到：匹配报告.md")

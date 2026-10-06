import json
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from state import AgentState
from database import get_all_jobs

# 配置大模型（用DeepSeek，兼容OpenAI接口）
llm = ChatOpenAI(
    model="deepseek-v4.1-flash",
    base_url="https://nb.deepsb.com/v1",
    api_key="sk-2c75082e7205130e4402ad83ef07480f5c7549043bbeae78db8220b3e82bd1d1",
    temperature=0.1
)

# 定义简历结构化输出模型
class ResumeInfo(BaseModel):
    name: str = Field(description="候选人姓名")
    education: str = Field(description="最高学历")
    work_year: str = Field(description="工作年限，信息缺失填【信息缺失】")
    skill: str = Field(description="掌握的技术栈")
    project: str = Field(description="项目经历摘要")

def extract_resume_node(state: AgentState) -> AgentState:
    """节点1：从简历文本抽取结构化信息"""
    print("=== 节点1：抽取简历信息 ===")
    
    prompt = f"""你是简历信息提取器。从以下简历文本中提取候选人信息，严格输出JSON格式。
如果某个信息找不到，值填"【信息缺失】"。

简历文本：
{state['resume_text']}

输出JSON格式：
{{"name":"姓名","education":"学历","work_year":"工作年限","skill":"技术栈","project":"项目经历"}}
只输出JSON，不要解释。"""
    
    response = llm.invoke(prompt)
    try:
        resume_info = json.loads(response.content)
        state['resume_info'] = resume_info
        print(f"抽取成功：{resume_info}")
    except Exception as e:
        state['error'] = f"简历解析失败：{e}"
        print(f"错误：{e}")
    
    return state

def match_jobs_node(state: AgentState) -> AgentState:
    """节点2：匹配岗位并打分"""
    print("=== 节点2：岗位匹配打分 ===")
    
    # 模拟岗位库
    jobs = get_all_jobs()
    state['jobs'] = jobs
    
    resume_info = state.get('resume_info', {})
    prompt = f"""你是招聘岗位匹配分析师。基于以下候选人简历信息和岗位列表，必须对岗位列表中的每一个岗位都进行分析，不能遗漏,生成匹配评估报告。

候选人简历：
{json.dumps(resume_info, ensure_ascii=False)}

岗位列表：岗位列表（共{len(jobs)}个岗位，必须逐个分析完，不能遗漏任何一个）：

{json.dumps(jobs, ensure_ascii=False)}

输出markdown格式报告：
1. 候选人基本信息摘要
2. 核心技能优势
3. 匹配到的岗位列表，逐个给出匹配度评分(0-100)和理由
4. 短板分析和建议"""
    
    response = llm.invoke(prompt)
    state['report'] = response.content
    print("报告生成完成")
    return state

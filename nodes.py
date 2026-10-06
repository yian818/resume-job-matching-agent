import os
import json
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from state import AgentState
from database import get_all_jobs

# 从.env文件读取配置
load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
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
    
        # 用Pydantic结构化输出，大模型直接返回对象
    structured_llm = llm.with_structured_output(ResumeInfo)
    result = structured_llm.invoke(prompt)
    
    # result就是一个ResumeInfo对象，直接转成字典存到state里
    state['resume_info'] = result.dict()

        # 判断信息是否完整
    if "【信息缺失】" in result.work_year:
        state['info_complete'] = False
    else:
        state['info_complete'] = True
    print(f"信息完整度：{state['info_complete']}")

    print(f"抽取成功：{state['resume_info']}")


    
    return state

def match_jobs_node(state: AgentState) -> AgentState:
    """节点2：匹配岗位并打分"""
    print("=== 节点2：岗位匹配打分 ===")
    
    # 模拟岗位库
    jobs = get_all_jobs()
    state['jobs'] = jobs
    job_list_text = "\n".join([f"{i+1}. {j['title']}（{j['department']}）- 要求{j['required_years']}年，技能：{j['required_skills']}" for i, j in enumerate(jobs)])

    resume_info = state.get('resume_info', {})
    prompt = f"""你是招聘岗位匹配分析师。基于以下候选人简历信息和岗位列表，必须对岗位列表中的每一个岗位都进行分析，不能遗漏,生成匹配评估报告。

候选人简历：
{json.dumps(resume_info, ensure_ascii=False)}

岗位列表：岗位列表（共{len(jobs)}个岗位，必须逐个分析完，不能遗漏任何一个）：
{job_list_text}

输出markdown格式报告：
1. 候选人基本信息摘要
2. 核心技能优势
3. 匹配到的岗位列表，逐个给出匹配度评分(0-100)和理由
4. 短板分析和建议"""
     # 如果信息不完整，在报告开头标注
    if not state['info_complete']:
        prefix = "⚠️ 注意：候选人简历信息不完整（工作年限缺失），以下匹配结果基于现有信息，仅供参考。\n\n"
    else:
        prefix = ""

    
        # 错误重试：最多3次
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = llm.invoke(prompt)
            state['report'] = prefix + response.content

            print("报告生成完成")
            break
        except Exception as e:
            print(f"第{attempt+1}次调用失败：{e}")
            if attempt == max_retries - 1:
                state['report'] = "系统错误，匹配失败，请稍后重试"
            else:
                import time
                time.sleep(2)

    return state

def ask_more_node(state: AgentState) -> AgentState:
    """信息不完整，追问用户补充"""
    print("=== 追问用户补充信息 ===")
    state['report'] = "你的简历信息不完整，缺少工作年限。请补充你的工作/实习经历后再进行匹配。"
    return state

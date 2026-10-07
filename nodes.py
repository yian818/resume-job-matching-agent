import os
import json
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from state import AgentState
from database import get_all_jobs
from scoring_rules import SCORING_RULES




# 从.env文件读取配置
load_dotenv()

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


llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.1
)


# 定义简历结构化输出模型
class ResumeInfo(BaseModel):
    name: str = Field(description="候选人姓名，只输出名字本身，不要加性别年龄")
    education: str = Field(description="最高学历，只能填：博士/硕士/本科/大专/高中，不要输出学校名")
    work_year: int = Field(description="总工作年限数字，按毕业年份到2026年计算，实习不算，无法确定填-1")
    skill: list[str] = Field(description="技术栈关键词列表，每个词单独一个元素")
    project: str = Field(description="项目经历一句话摘要")

def extract_resume_node(state: AgentState) -> AgentState:
    """节点1：从简历文本抽取结构化信息"""
    logger.info("=== 节点1：抽取简历信息 ===")

    prompt = f"""你是简历信息提取器。从以下简历文本中提取候选人信息。

严格规则：
1. name: 只输出姓名本身，不要加性别、年龄
2. education: 只能填"博士"/"硕士"/"本科"/"大专"/"高中"之一，不要输出学校名和专业
3. work_year: 只输出数字（整数），按毕业年份到2026年算总工作年限，无法确定填-1
4. skill: 技术栈列表，每个技术词单独一个元素
5. project: 一句话概括最重要的项目经历

简历文本：
{state['resume_text']}"""

        # 用Pydantic结构化输出，带重试
    try:
        structured_llm = llm.with_structured_output(ResumeInfo)
        result = structured_llm.invoke(prompt)
    except Exception as e:
        logger.warning(f"结构化输出失败，重试一次: {e}")
        # 兜底：直接调LLM，手动清洗JSON
        raw = llm.invoke(prompt + "\n\n重要：只输出纯JSON，不要用```json```包裹，不要有任何解释文字。")
        text = raw.content.strip()
        # 剥掉可能的 ```json``` 代码块
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            text = text.rsplit("```", 1)[0].strip()
        result = ResumeInfo(**json.loads(text))


    state['resume_info'] = result.dict()

    # 判断信息是否完整：work_year为-1表示缺失
    state['info_complete'] = result.work_year > 0
    logger.info(f"信息完整度：{state['info_complete']}")
    logger.info(f"抽取成功：{state['resume_info']}")

    return state

def match_jobs_node(state: AgentState) -> AgentState:
    """节点2：匹配岗位并打分"""
    logger.info("=== 节点2：岗位匹配打分 ===")
    
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
打分规则（总分100）：
- 技能匹配（权重40%）：岗位要求技能与候选人技能重合度
- 学历匹配（权重10%）：本科及以上满足要求
- 工作年限（权重30%）：候选人年限与岗位要求差距
- 项目相关度（权重20%）：项目经历与岗位方向相关性


输出markdown格式报告：
1. 候选人基本信息摘要
2. 核心技能优势
3. 匹配到的岗位列表，逐个给出匹配度评分(0-100)和理由
4. 短板分析和建议"""
    logger.info(f"开始匹配岗位，候选人信息：{resume_info}")

        # 错误重试：最多3次
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = llm.invoke(prompt)
            state['report'] = response.content
            logger.info("报告生成完成")
            break
        except Exception as e:
            logger.error(f"第{attempt+1}次调用失败：{e}")
            if attempt == max_retries - 1:
                state['report'] = "系统错误，匹配失败，请稍后重试"
            else:
                import time
                time.sleep(2)

        # 如果信息不完整，在报告开头标注
    if not state['info_complete']:
        prefix = "⚠️ 注意：候选人简历信息不完整（工作年限缺失），以下匹配结果基于现有信息，仅供参考。\n\n"
    else:
        prefix = ""

    
        # 错误重试：最多3次

    return state

def ask_more_node(state: AgentState) -> AgentState:
    """信息不完整，追问用户补充"""
    logger.info("=== 追问用户补充信息 ===")
    state['report'] = "你的简历信息不完整，缺少工作年限。请补充你的工作/实习经历后再进行匹配。"
    return state

def resume_optimize_node(state: AgentState) -> AgentState:
    """节点3：简历优化建议"""
    print("=== 节点3：简历优化建议 ===")
    resume_info = state.get('resume_info', {})
    prompt = f"""你是简历优化专家。基于以下候选人信息，给出3-5条具体的简历优化建议：
    
    候选人信息：
    {json.dumps(resume_info, ensure_ascii=False)}
    
    输出markdown格式：
    1. 每条建议包含问题和具体改法
    2. 建议要具体，不要空泛
    """
    response = llm.invoke(prompt)
    state['report'] += "\n\n---\n\n## 简历优化建议\n\n" + response.content
    return state

def interview_question_node(state: AgentState) -> AgentState:
    """节点4：生成模拟面试题"""
    logger.info("=== 节点4：生成模拟面试题 ===")
    resume_info = state.get('resume_info', {})
    prompt = f"""你是技术面试官。基于以下候选人信息，生成5道模拟面试题：
    
    候选人信息：
    {json.dumps(resume_info, ensure_ascii=False)}
    
    要求：
    1. 3道技术题（针对候选人技能栈）
    2. 2道项目题（针对候选人项目经历）
    3. 每道题给出考察点
    """
    response = llm.invoke(prompt)
    state['report'] += "\n\n---\n\n## 模拟面试题\n\n" + response.content
    return state

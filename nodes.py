import os
import json
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from state import AgentState
from database import get_all_jobs
from scoring_rules import SCORING_RULES
from retriever import search_similar_jobs




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
    
    # Human-in-the-loop：检查缺失字段
    missing = []
    if result.work_year <= 0:
        missing.append("work_year")
    if not result.skill or len(result.skill) == 0:
        missing.append("skill")
    
    state['missing_fields'] = missing
    state['needs_human'] = len(missing) > 0
    
    if state['needs_human']:
        state['follow_up_question'] = "你的简历信息不完整，缺少工作年限或技能列表，请补充一下你的工作/实习经历和技术栈。"
        logger.info(f"信息不完整，缺失字段：{missing}")
    
    logger.info(f"信息完整度：{state['info_complete']}")
    logger.info(f"抽取成功：{state['resume_info']}")

    return state

# 岗位匹配打分模型
class JobMatchScore(BaseModel):
    job_title: str = Field(alias="岗位名称")
    score: int = Field(alias="匹配分数")
    reason: str = Field(alias="理由")

    class Config:
        populate_by_name = True

class JobMatchResult(BaseModel):
    matches: list[JobMatchScore] = Field(description="所有岗位的匹配打分列表")

def match_jobs_node(state: AgentState) -> AgentState:
    """节点2：匹配岗位并打分（RAG召回 + LLM精排）"""
    logger.info("=== 节点2：岗位匹配打分 ===")

    resume_info = state.get('resume_info', {})
    skills = resume_info.get('skill', [])
    work_year = resume_info.get('work_year', 0)

    # 第一步：RAG语义检索Top-5相关岗位
    logger.info(f"RAG语义检索：技能={skills}, 年限={work_year}")
    rag_results = search_similar_jobs(skills, max_years=work_year, top_k=5)
    
    if not rag_results:
        # RAG没找到， fallback到全部岗位
        logger.warning("RAG未检索到合适岗位，使用全部岗位")
        jobs = get_all_jobs()
        rag_jobs = jobs
    else:
        # 从SQLite查询这5个岗位的完整信息
        all_jobs = get_all_jobs()
        rag_titles = [r['title'] for r in rag_results]
        rag_jobs = [j for j in all_jobs if j['title'] in rag_titles]
        logger.info(f"RAG召回{len(rag_jobs)}个候选岗位")

    state['jobs'] = rag_jobs
    job_list_text = "\n".join([f"{i+1}. {j['title']}（{j['department']}）- 要求{j['required_years']}年，技能：{j['required_skills']}" for i, j in enumerate(rag_jobs)])

    prompt = f"""你是招聘岗位匹配分析师。基于以下候选人简历信息和候选岗位列表，对每个岗位打分。

打分规则（严格执行，总分100）：
- 技能匹配（权重40%）：岗位要求的核心技能，候选人会几个？
  - 完全不会：0-10分
  - 会1-2个：10-20分
  - 会3个以上：20-40分
- 学历匹配（权重10%）：
  - 低于要求：0分
  - 刚好满足：5分
  - 高于要求：10分
- 工作年限（权重30%）：
  - 低于要求2年以上：0-10分
  - 低于要求1年：10-20分
  - 刚好满足：20-25分
  - 超过要求：25-30分
- 项目相关度（权重20%）：
  - 完全不相关：0-5分
  - 有点相关：5-10分
  - 高度相关：10-20分

重要原则：
1. 不匹配的岗位给30分以下，不要都给高分
2. 核心技能完全不沾边的，直接打20分以下
3. 有明显不匹配的，要在理由里说明

候选人简历：
{json.dumps(resume_info, ensure_ascii=False)}

候选岗位列表（共{len(rag_jobs)}个）：
{job_list_text}

输出JSON格式：{{"matches":[{{"岗位名称":"AI Agent工程师","匹配分数":85,"理由":"技能高度匹配"}}]}}"""


    logger.info(f"开始匹配岗位，候选人信息：{resume_info}")

    try:
        structured_llm = llm.with_structured_output(JobMatchResult)
        result = structured_llm.invoke(prompt)
        # 按分数降序排序
        sorted_matches = sorted(result.matches, key=lambda x: x.score, reverse=True)
        # 生成报告文本
        report_lines = ["## 岗位匹配报告\n"]
        for i, m in enumerate(sorted_matches):
            report_lines.append(f"{i+1}. **{m.job_title}** - {m.score}分\n   理由：{m.reason}\n")
        state['report'] = "\n".join(report_lines)
        state['job_scores'] = [{"job": m.job_title, "score": m.score, "reason": m.reason} for m in sorted_matches]
        logger.info(f"匹配完成，Top1: {sorted_matches[0].job_title} ({sorted_matches[0].score}分)")
        
    except Exception as e:
        logger.warning(f"结构化打分失败，重试一次: {e}")
        raw = llm.invoke(prompt + "\n\n重要：只输出纯JSON，不要用```json```包裹，不要有任何解释文字。")
        text = raw.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            text = text.rsplit("```", 1)[0].strip()
        parsed = json.loads(text)
        if isinstance(parsed, list):
            parsed = {"matches": parsed}

        # 手动映射中文键名→英文字段（模型可能用各种中文叫法）
        raw_matches = parsed.get("matches", parsed.get("岗位打分", []))
        normalized = []
        for item in raw_matches:
            job_title = item.get("岗位名称") or item.get("岗位") or item.get("职位") or item.get("job_title", "")
            score = item.get("匹配分数") or item.get("分数") or item.get("score") or item.get("匹配度", 0)
            reason = item.get("理由") or item.get("打分理由") or item.get("说明") or item.get("reason", "")
            normalized.append({"job_title": str(job_title), "score": int(score), "reason": str(reason)})

        result = JobMatchResult(matches=normalized)

        sorted_matches = sorted(result.matches, key=lambda x: x.score, reverse=True)
        report_lines = ["## 岗位匹配报告\n"]
        for i, m in enumerate(sorted_matches):
            report_lines.append(f"{i+1}. **{m.job_title}** - {m.score}分\n   理由：{m.reason}\n")
        state['report'] = "\n".join(report_lines)
        state['job_scores'] = [{"job": m.job_title, "score": m.score, "reason": m.reason} for m in sorted_matches]
        logger.info(f"重试成功，Top1: {sorted_matches[0].job_title} ({sorted_matches[0].score}分)")


    return state


def ask_more_node(state: AgentState) -> AgentState:
    """信息不完整，追问用户补充（Human-in-the-loop）"""
    logger.info("=== Human-in-the-loop：追问用户补充信息 ===")
    
    question = state.get('follow_up_question', "请补充你的工作年限和技能列表。")
    print(f"\n❓ {question}")
    
    # 等待用户输入
    user_answer = input("请输入补充信息：")
    
    logger.info(f"用户补充：{user_answer}")
    
    # 把用户补充的信息加到简历文本后面
    state['resume_text'] += f"\n\n补充信息：{user_answer}"
    state['user_answer'] = user_answer
    
    # 重置状态，让下一轮重新抽取
    state['resume_info'] = None
    state['info_complete'] = False
    state['needs_human'] = False
    
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

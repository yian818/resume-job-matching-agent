"""
main_api.py - FastAPI 服务（P11 工程化）
把命令行 Agent 变成可交付的 Web 服务：
  - /api/v1/match  结构化匹配接口（前端消费）
  - /api/match     旧版接口（返回 markdown，兼容）
  - /api/health    健康检查（无需鉴权）
  - /              前端页面
鉴权：Authorization: Bearer <API_TOKEN>（API_TOKEN 未配置时本地开发放行）
"""
import os
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import uvicorn

from nodes import extract_resume_node, match_jobs_node, resume_optimize_node, interview_question_node
from scoring_rules import compute_rule_score, hard_cap, career_match_score
from database import get_all_jobs
from state import AgentState

load_dotenv()
logger = logging.getLogger(__name__)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

app = FastAPI(
    title="简历-岗位智能匹配 Agent",
    description="LangGraph + RAG + 规则引擎 + cross-encoder 重排，Top-1 98%",
    version="2.0",
)

# ===== 鉴权 =====
def verify_token(authorization: Optional[str] = Header(None)):
    """
    简单 Bearer Token 鉴权。
    API_TOKEN 未配置时（本地开发）直接放行；配置后必须带正确 token。
    """
    expected = os.getenv("API_TOKEN", "")
    if not expected:
        return True
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少 Authorization: Bearer <token>")
    if authorization.split(" ", 1)[1].strip() != expected:
        raise HTTPException(status_code=401, detail="token 无效")
    return True


# ===== 请求/响应模型 =====
class MatchRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="简历文本")
    include_advice: bool = Field(False, description="是否生成简历优化建议和模拟面试题（更慢）")


class Signal(BaseModel):
    llm: Optional[int] = None
    rerank: Optional[float] = None
    rule: Optional[int] = None
    career: Optional[int] = None
    cap: Optional[int] = None


class JobMatch(BaseModel):
    rank: int
    job: str
    score: int
    reason: str
    signals: Signal


class Candidate(BaseModel):
    name: str = ""
    education: str = ""
    work_year: int = 0
    career: str = ""
    skills: list[str] = []
    project: str = ""


class MatchResponse(BaseModel):
    success: bool
    candidate: Optional[Candidate] = None
    matches: list[JobMatch] = []
    advice: Optional[str] = None
    error: Optional[str] = None


def _initial_state(resume_text: str) -> AgentState:
    return {
        "resume_text": resume_text,
        "resume_info": None,
        "jobs": [],
        "report": "",
        "error": None,
        "info_complete": True,
        "missing_fields": [],
        "follow_up_question": "",
        "user_answer": "",
        "needs_human": False,
    }


def run_match(resume_text: str, include_advice: bool = False) -> dict:
    """执行抽取 + 匹配（+ 可选建议），返回结构化结果。"""
    state = _initial_state(resume_text)
    state = extract_resume_node(state)
    state = match_jobs_node(state)

    info = state.get("resume_info") or {}
    scores = state.get("job_scores", [])

    # 岗位完整信息（用于补 rule/cap/career 三个信号）
    job_db = {j["title"]: j for j in get_all_jobs()}

    matches = []
    for idx, s in enumerate(scores):
        title = s["job"]
        bare = title.split("（")[0].strip()
        job = job_db.get(bare) or job_db.get(title)
        signals = Signal(llm=s.get("llm_score"))
        if s.get("rerank_score") is not None:
            signals.rerank = round(float(s["rerank_score"]) * 100, 1)
        if job:
            signals.rule = compute_rule_score(job, info)
            signals.cap = hard_cap(job, info)
            signals.career = career_match_score(job, info)
        matches.append(JobMatch(
            rank=idx + 1,
            job=title,
            score=s.get("final_score", s.get("score", 0)),
            reason=s.get("reason", ""),
            signals=signals,
        ))

    advice = None
    if include_advice:
        state = resume_optimize_node(state)
        state = interview_question_node(state)
        advice = state.get("report", "")

    return {
        "success": True,
        "candidate": Candidate(
            name=info.get("name", ""),
            education=info.get("education", ""),
            work_year=info.get("work_year", 0) or 0,
            career=info.get("career", ""),
            skills=info.get("skill", []) or [],
            project=info.get("project", ""),
        ),
        "matches": matches,
        "advice": advice,
    }


# ===== 接口 =====
@app.post("/api/v1/match", response_model=MatchResponse, summary="结构化匹配（需鉴权）")
def api_v1_match(request: MatchRequest, _: bool = Depends(verify_token)):
    try:
        return run_match(request.resume_text, request.include_advice)
    except Exception as e:
        logger.exception("匹配失败")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/match", summary="旧版匹配（返回 markdown，需鉴权）")
def api_match(request: MatchRequest, _: bool = Depends(verify_token)):
    try:
        result = run_match(request.resume_text, include_advice=True)
        lines = ["## 岗位匹配报告\n"]
        for m in result["matches"]:
            lines.append(f"{m.rank}. **{m.job}** - {m.score}分\n   理由：{m.reason}\n")
        report = "\n".join(lines) + (result.get("advice") or "")
        return {"success": True, "report": report, "error": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health", summary="健康检查（无需鉴权）")
def health():
    return {"status": "ok", "message": "Agent 服务运行中"}


# ===== 前端 =====
@app.get("/", include_in_schema=False)
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

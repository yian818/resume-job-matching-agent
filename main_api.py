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
import json
import sys
import threading
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
from explain import build_explanation
from database import get_all_jobs
from state import AgentState

# P13 在线评测面板：复用评测缓存模块（eval/ 不在包路径里，手动加）
EVAL_DIR = os.path.join(os.path.dirname(__file__), "eval")
sys.path.insert(0, EVAL_DIR)
from eval_cache import build_cache, simulate, CACHE_PATH  # noqa: E402

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


class ExplainSkills(BaseModel):
    hit: list[str] = []
    gap: list[str] = []


class JobExplain(BaseModel):
    job: str
    verdict: str = ""
    career: str = ""
    years: str = ""
    education: str = ""
    cap: str = ""
    skills: ExplainSkills = ExplainSkills()


class ExplainReport(BaseModel):
    summary: str = ""
    verdict: str = ""
    per_job: list[JobExplain] = []


class MatchResponse(BaseModel):
    success: bool
    candidate: Optional[Candidate] = None
    matches: list[JobMatch] = []
    explanation: Optional[ExplainReport] = None
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
            s["rule_score"] = compute_rule_score(job, info)   # 缓存，解释层复用
            signals.rule = s["rule_score"]
            signals.cap = hard_cap(job, info)
            signals.career = career_match_score(job, info)
        matches.append(JobMatch(
            rank=idx + 1,
            job=title,
            score=s.get("final_score", s.get("score", 0)),
            reason=s.get("reason", ""),
            signals=signals,
        ))

    # P12：可解释报告（纯确定性计算，不经过 LLM）
    explanation = ExplainReport(**build_explanation(job_db, scores, info))

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
        "explanation": explanation,
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


# ===== P13 在线评测面板 =====
# 缓存构建是长任务（全量 50 份），放后台线程；面板轮询状态
_ev_builder = {"lock": threading.Lock(), "running": False}


def _read_stability(tag: str):
    """读稳定性评测 JSON 报告（eval/stability_<tag>.json）"""
    p = os.path.join(EVAL_DIR, f"stability_{tag}.json")
    if not os.path.exists(p):
        return None
    return json.loads(open(p, encoding="utf-8").read())


@app.get("/api/eval/status", summary="评测面板状态（无需鉴权）")
def eval_status():
    has_cache = CACHE_PATH.exists()
    cache_n = 0
    config = {}
    built_at = None
    if has_cache:
        try:
            cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
            cache_n = len(cache.get("cases", {}))
            config = cache.get("config", {})
            built_at = cache.get("built_at")
        except Exception:
            pass
    return {
        "has_cache": has_cache,
        "cache_n": cache_n,
        "total": 50,
        "building": _ev_builder["running"],
        "built_at": built_at,
        "config": config,
    }


@app.get("/api/eval/simulate", summary="权重模拟：调权重→MRR/NDCG 即时刷新（需鉴权）")
def eval_simulate(w_rule: float = 0.4, w_llm: float = 0.3, w_rerank: float = 0.3,
                  use_cap: int = 1, _: bool = Depends(verify_token)):
    if not CACHE_PATH.exists():
        raise HTTPException(status_code=404, detail="评测缓存未构建，请先点【构建评测缓存】")
    try:
        cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"缓存读取失败：{e}")
    return simulate(cache, w_rule=w_rule, w_llm=w_llm, w_rerank=w_rerank,
                    use_cap=bool(use_cap))


@app.post("/api/eval/build", summary="后台构建评测缓存（需鉴权）")
def eval_build(limit: int = 50, force: bool = True, _: bool = Depends(verify_token)):
    with _ev_builder["lock"]:
        if _ev_builder["running"]:
            raise HTTPException(status_code=409, detail="正在构建中，请稍候")
        _ev_builder["running"] = True

    def _run():
        try:
            build_cache(limit=max(1, min(limit, 50)), force=force)
        finally:
            _ev_builder["running"] = False

    threading.Thread(target=_run, daemon=True).start()
    return {"started": True, "limit": limit,
            "detail": "构建已开始在后台执行，完成后状态自动更新"}


@app.get("/api/eval/stability", summary="稳定性评测报告（无需鉴权）")
def eval_stability(tag: str = "before"):
    rep = _read_stability(tag)
    if rep is not None:
        return rep
    return _read_stability("after") or {"tag": tag, "error": f"stability_{tag}.json 不存在"}


# ===== 前端 =====
@app.get("/", include_in_schema=False)
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/eval", include_in_schema=False)
def eval_page():
    return FileResponse(os.path.join(STATIC_DIR, "eval.html"))


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

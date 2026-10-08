"""
main_api.py - FastAPI接口
把命令行Agent变成Web服务
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

from main import build_agent
from state import AgentState

app = FastAPI(
    title="简历-岗位智能匹配Agent",
    description="基于LangGraph的AI招聘助手，支持简历解析、RAG语义检索、岗位匹配打分、简历优化建议",
    version="1.0"
)

# 请求体模型
class ResumeRequest(BaseModel):
    resume_text: str = Field(..., description="简历文本内容", example="张三，男，硕士学历，3年Python开发经验，会LangGraph、RAG、LLM")
    user_id: Optional[str] = Field(None, description="用户ID，可选")

# 响应体模型
class MatchResponse(BaseModel):
    success: bool = Field(..., description="是否成功")
    report: str = Field(..., description="匹配报告内容")
    error: Optional[str] = Field(None, description="错误信息")

# 全局Agent实例（启动时构建一次）
agent = None

@app.on_event("startup")
def startup_event():
    """启动时构建Agent"""
    global agent
    agent = build_agent()
    print("Agent启动完成")

@app.post("/api/match", response_model=MatchResponse, summary="简历匹配接口", description="传入简历文本，返回岗位匹配打分、简历优化建议和模拟面试题")
def match_resume(request: ResumeRequest):
    """简历匹配接口"""
    try:
        result = agent.invoke({
            "resume_text": request.resume_text,
            "resume_info": None,
            "jobs": [],
            "report": "",
            "error": None,
            "info_complete": True,
            "missing_fields": [],
            "follow_up_question": "",
            "user_answer": "",
            "needs_human": False
        })
        
        return MatchResponse(
            success=True,
            report=result.get("report", ""),
            error=result.get("error")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health", summary="健康检查", description="检查服务是否正常运行")
def health_check():
    """健康检查接口"""
    return {"status": "ok", "message": "Agent服务运行中"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


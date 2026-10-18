# smoke_p12_api.py - HTTP 层冒烟：验证 /api/v1/match 返回 explanation
#
# 用法：python eval/smoke_p12_api.py
# 起 uvicorn → 等 /api/health → POST 示例简历 → 断言 explanation 结构 → 停服务。

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8123  # 避开默认 8000，防止与已有服务冲突

SAMPLE = (
    "张明，男，28岁。\n"
    "学历：北京大学，计算机科学，硕士，2020年毕业。\n"
    "工作经历：\n"
    "- 2020-2023 字节跳动 算法工程师，负责推荐系统优化，使用 Python、PyTorch、Transformer，上线后CTR提升12%。\n"
    "- 2023-至今 阿里云 高级算法工程师，负责LLM应用开发，精通LangGraph、RAG、向量数据库（Milvus）、Prompt Engineering。\n"
    "技能：Python, PyTorch, LangGraph, RAG, Milvus, LLM, Prompt Engineering, 大模型微调, Docker, Kubernetes。\n"
    "项目：独立完成一个基于LangGraph的AI客服Agent，支持多轮对话和工具调用，日均处理5000+请求。"
)


def wait_health(timeout=180):
    url = f"http://{HOST}:{PORT}/api/health"
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def main():
    env = dict(os.environ, PYTHONIOENCODING="utf-8", HF_HUB_OFFLINE="1")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main_api:app",
         "--host", HOST, "--port", str(PORT), "--log-level", "warning"],
        env=env,
        cwd=str(Path(__file__).parent.parent),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        assert wait_health(), "服务未在超时内就绪"
        body = json.dumps({"resume_text": SAMPLE, "include_advice": False}).encode("utf-8")
        req = urllib.request.Request(
            f"http://{HOST}:{PORT}/api/v1/match",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=240) as r:
            data = json.load(r)
        assert data["success"], f"success=False: {data.get('error')}"
        ex = data.get("explanation") or {}
        assert ex.get("summary"), "explanation.summary 缺失"
        assert len(ex.get("per_job", [])) == len(data["matches"]), "per_job 数量不一致"
        top = data["matches"][0]
        print("HTTP OK → Top-1:", top["job"], top["score"], "分")
        print("verdict:", ex["verdict"])
        print(ex["summary"])
        print("\n逐岗位解读（前2）:")
        for p in ex["per_job"][:2]:
            print(f"  - {p['job']} [{p['verdict']}]")
            print(f"    命中{len(p['skills']['hit'])} / 缺口{len(p['skills']['gap'])}")
            if p["cap"]:
                print(f"    {p['cap']}")
        print("\n✅ HTTP 冒烟通过：/api/v1/match 已返回 explanation")
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()

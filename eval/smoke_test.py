"""
eval/smoke_test.py - 快速冒烟测试

用途：验证当前代码（top_k=10 + 关键词补足 + 项目摘要进query）能否端到端跑通。
不是正式评测，只跑前 N 份简历，打印每个候选的 Top-3 分数和召回岗位数，
方便快速发现崩溃/报错，避免直接跑 50 份全量评测浪费时间。

用法：
    python eval/smoke_test.py        # 默认跑前3份
    python eval/smoke_test.py 5      # 跑前5份
"""
import sys
from pathlib import Path

# 把项目根目录加到 Python 路径（和 eval_match_v2.py 一样）
sys.path.append(str(Path(__file__).parent.parent))

from nodes import extract_resume_node, match_jobs_node
from eval_dataset import RESUMES

# 默认跑前3份，也可以命令行指定份数
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 3

print(f"=== 冒烟测试：跑前 {LIMIT} 份简历 ===")

for i, sample in enumerate(RESUMES[:LIMIT]):
    rid = sample["resume_id"]
    # 简历第一行当标题（人名+学历那行）
    title = sample["resume_text"].splitlines()[0][:20]
    print(f"\n--- {rid} {title} ---")

    # 初始化 AgentState（和 eval_match_v2.py 完全一致）
    state = {
        "resume_text": sample["resume_text"],
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

    try:
        # 节点1：抽取
        state = extract_resume_node(state)
        # 节点2：匹配（RAG召回 + LLM精排）
        state = match_jobs_node(state)

        scores = state.get("job_scores", [])
        # 打印 Top-3 分数
        for j, s in enumerate(scores[:3]):
            print(f"  Top{j+1}: {s['job']} - {s['score']}分")
        # 打印本次召回了几个岗位（重点看 top_k=10 的效果）
        print(f"  召回岗位数: {len(state.get('jobs', []))}")
    except Exception as e:
        print(f"  FAILED: {e}")

print("\n=== 冒烟测试完成 ===")

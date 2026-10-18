# check_explain.py - P12 可解释报告回归测试
#
# 用法：python eval/check_explain.py
# 对示例简历跑完整流水线，校验解释层不变量并打印 Top-1 解读。
# 不变量（保证解释层与匹配结果一致，不漂移）：
#   1. explanation.per_job 数量 == matches 数量
#   2. 每个岗位都有 years/education/career 解读行
#   3. skills.hit / skills.gap 是列表（可为空）

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from main_api import run_match

SAMPLE = (
    "张明，男，28岁。\n"
    "学历：北京大学，计算机科学，硕士，2020年毕业。\n"
    "工作经历：\n"
    "- 2020-2023 字节跳动 算法工程师，负责推荐系统优化，使用 Python、PyTorch、Transformer，上线后CTR提升12%。\n"
    "- 2023-至今 阿里云 高级算法工程师，负责LLM应用开发，精通LangGraph、RAG、向量数据库（Milvus）、Prompt Engineering。\n"
    "技能：Python, PyTorch, LangGraph, RAG, Milvus, LLM, Prompt Engineering, 大模型微调, Docker, Kubernetes。\n"
    "项目：独立完成一个基于LangGraph的AI客服Agent，支持多轮对话和工具调用，日均处理5000+请求。"
)


def main():
    result = run_match(SAMPLE, include_advice=False)
    assert result["success"], f"匹配失败: {result.get('error')}"

    ex = result["explanation"]
    assert ex and ex.summary, "解释层缺失 summary"
    assert len(ex.per_job) == len(result["matches"]), "per_job 与 matches 数量不一致"

    top = ex.per_job[0]
    assert isinstance(top.skills.hit, list) and isinstance(top.skills.gap, list)
    for p in ex.per_job:
        assert p.years, f"{p.job} 缺年限解读"
        assert p.education, f"{p.job} 缺学历解读"
        assert p.career, f"{p.job} 缺职业身份解读"

    print("=== Top-1 ===")
    print(result["matches"][0].job, result["matches"][0].score, "分")
    print(ex.verdict)
    print(ex.summary)

    print("\n=== 逐岗位解读（前3）===")
    for p in ex.per_job[:3]:
        print(f"\n{p.job} [{p.verdict}]")
        print("  ", p.career)
        print("  ", p.years)
        print("  ", p.education)
        if p.cap:
            print("  ", p.cap)
        print("   命中:", "、".join(p.skills.hit) or "-")
        print("   缺口:", "、".join(p.skills.gap) or "-")

    print("\n✅ 解释层回归测试通过")


if __name__ == "__main__":
    main()

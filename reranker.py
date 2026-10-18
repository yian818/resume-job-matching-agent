# reranker.py - A3 cross-encoder 语义重排器
#
# 背景：A2 的硬上限用"字面技能重合数"做判据，会误伤"语义匹配、字面弱重合"的岗位。
# 例：R022 韩冰（做推荐系统/时空预测）语义上就是数据分析师，但字面只重合 Python 一词，
#     被硬上限压到 40 分，反而排不过 NLP 的 60 分。
#
# 解法：在 LLM 打分之后，加一层 cross-encoder 语义重排。
# 对比 Bi-encoder（BGE，召回用）：
#   - Bi-encoder：简历和岗位各自编码成向量，算夹角。快但粗，只看表面。
#   - Cross-encoder：把"简历文本 + 岗位文本"拼成一句话喂给模型，直接输出匹配分。
#     慢但准，能理解"推荐系统=数据分析"这类语义关系。
# 这就是业界标准的"召回-精排"两阶段架构：召回用 Bi-encoder（快），精排用 Cross-encoder（准）。

import logging

logger = logging.getLogger(__name__)

# 全局单例：模型只加载一次，避免每次匹配都重新加载（耗时约1-2秒/次）
_RERANKER = None


def get_reranker():
    """懒加载 cross-encoder 模型（首次调用才加载）"""
    global _RERANKER
    if _RERANKER is None:
        from sentence_transformers import CrossEncoder
        logger.info("加载 bge-reranker-large 重排模型...")
        _RERANKER = CrossEncoder(
            "BAAI/bge-reranker-large",
            max_length=512,  # 输入文本长度上限（简历+岗位拼接后）
        )
        logger.info("重排模型加载完成")
    return _RERANKER


def build_resume_text(resume_info: dict) -> str:
    """把结构化简历信息拼成一段文本，供 cross-encoder 理解"""
    parts = []
    parts.append(f"候选人：{resume_info.get('name', '')}")
    parts.append(f"学历：{resume_info.get('education', '')}")
    parts.append(f"工作年限：{resume_info.get('work_year', 0)}年")
    if resume_info.get('career'):
        parts.append(f"职业身份：{resume_info['career']}")   # P8：让重排器也看到真实职位
    parts.append(f"技能：{', '.join(resume_info.get('skill', []))}")
    if resume_info.get('project'):
        parts.append(f"项目：{resume_info['project']}")
    return "；".join(parts)


def build_job_text(job: dict) -> str:
    """把岗位信息拼成一段文本，供 cross-encoder 理解"""
    return (
        f"岗位：{job['title']}（{job['department']}）"
        f"；要求{job['required_years']}年经验"
        f"；学历要求：{job['education']}"
        f"；核心技能：{job['required_skills']}"
    )


def rerank_scores(job_scores: list, resume_info: dict, job_info_map: dict) -> list:
    """
    对融合后的岗位分数，用 cross-encoder 语义分做三信号融合。

    输入：job_scores = [{"job":标题, "score":A2融合分, "reason":理由, "llm_score":...}]
    返回：加了 rerank_score 和 final_score 的新列表（按 final_score 降序）

    三信号融合（A3 核心）：
        final_score = min(0.4×规则分 + 0.3×LLM分 + 0.3×rerank分, 硬上限)

    - 规则分：确定性锚点（技能/学历/年限/项目）
    - LLM分：语义理解（项目相关度、理由）
    - rerank分：cross-encoder 深度语义（能理解"推荐系统≈数据分析"这类关系）
    三个信号投票，抵消单一模型偏差（LLM会翻车、rerank也会翻车，但它们同时翻车概率低）。
    找不到完整岗位信息的，保留原A2融合分不误伤。
    """
    from scoring_rules import compute_rule_score, hard_cap

    model = get_reranker()
    job_by_title = {j['title']: j for j in job_info_map.values()}

    # 构造 (简历文本, 岗位文本) 对，一次批量交给模型打分
    pairs = []
    valid_indices = []
    for idx, s in enumerate(job_scores):
        job = job_by_title.get(s["job"]) or job_by_title.get(_strip_department(s["job"]))
        if job is None:
            continue  # 查不到完整信息的岗位，跳过重排（保留原分）
        resume_text = build_resume_text(resume_info)
        job_text = build_job_text(job)
        pairs.append((resume_text, job_text))
        valid_indices.append(idx)

    if not pairs:
        return job_scores  # 没有能重排的，原样返回

    # cross-encoder 批量打分（分数越高越匹配）
    rerank_scores_list = model.predict(pairs)

    # 把 rerank 分数合并，并计算三信号融合分
    for idx, rerank_score in zip(valid_indices, rerank_scores_list):
        s = job_scores[idx]
        job = job_by_title.get(s["job"]) or job_by_title.get(_strip_department(s["job"]))

        # rerank分是 sigmoid 输出(0~1)，放大到 0~100 和规则分/LLM分同量纲
        rerank_100 = float(rerank_score) * 100
        rule = compute_rule_score(job, resume_info)
        cap = hard_cap(job, resume_info)
        llm = s.get("llm_score", s["score"])

        # 三信号融合 + 硬上限兜底
        final = int(min(round(0.4 * rule + 0.3 * llm + 0.3 * rerank_100), cap))

        s["rerank_score"] = float(rerank_score)
        s["final_score"] = final
        s["score"] = final  # 同步 score = final，保证报告/评测/日志的"分数"永远一致
        s["reason"] = f"{s['reason']}（语义分{rerank_100:.0f}）"

    # 按三信号融合分降序
    job_scores.sort(key=lambda x: x.get("final_score", x["score"]), reverse=True)
    return job_scores


def _strip_department(title: str) -> str:
    """剥离岗位名的部门后缀（复用 nodes.py 的逻辑，保持模块独立）"""
    return title.split("（")[0].strip()


if __name__ == "__main__":
    # 离线自测：用 R022 韩冰案例验证重排器能不能理解"推荐系统=数据分析"
    print("=== A3 离线自测：R022 韩冰 ===")
    resume_info = {
        "name": "韩冰",
        "education": "硕士",
        "work_year": 6,
        "skill": ["Python", "TensorFlow", "PyTorch", "Flink", "Redis", "推荐系统", "时空预测"],
        "project": "开发实时需求预测系统，预测准确率提升15%，日均节省运力10万单",
    }
    jobs = [
        {"title": "数据分析师", "department": "技术部", "required_years": 2, "education": "本科", "required_skills": "SQL,Python,Tableau,AB Testing"},
        {"title": "NLP算法工程师", "department": "技术部", "required_years": 3, "education": "硕士", "required_skills": "Python,PyTorch,NLP,Transformer"},
        {"title": "农业技术推广专员", "department": "市场部", "required_years": 1, "education": "本科", "required_skills": "Agriculture,Extension Services"},
    ]
    job_info_map = {j["title"]: j for j in jobs}
    # 模拟 A2 融合后的分数（数据分析师被硬上限误伤只有40）
    job_scores = [
        {"job": "NLP算法工程师", "score": 60, "reason": "技能重合2个"},
        {"job": "数据分析师", "score": 40, "reason": "技能只重合Python被硬上限压"},
        {"job": "农业技术推广专员", "score": 25, "reason": "完全不匹配"},
    ]
    print("重排前（A2融合分）：")
    for s in job_scores:
        print(f"  {s['job']}: {s['score']}分")

    reranked = rerank_scores(job_scores, resume_info, job_info_map)
    print("\n重排后（cross-encoder语义分）：")
    for s in reranked:
        print(f"  {s['job']}: {s['score']}分 (语义分{s.get('rerank_score', 'N/A'):.4f})")

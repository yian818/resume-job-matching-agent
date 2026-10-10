"""
retriever.py - RAG语义检索层（混合检索架构）
用ChromaDB + BGE嵌入模型做岗位语义匹配
架构：SQL硬过滤 → 向量语义召回
"""
import os
# 必须在import sentence_transformers之前设置，否则不生效
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import chromadb
import sqlite3
from pathlib import Path
from sentence_transformers import SentenceTransformer
from database import get_all_jobs

# 项目根目录
BASE_DIR = Path(__file__).parent

# 加载中文嵌入模型
print("正在加载BGE嵌入模型...")
encoder = SentenceTransformer('BAAI/bge-large-zh-v1.5')

# 初始化ChromaDB
chroma_client = chromadb.PersistentClient(path=str(BASE_DIR / "data" / "chroma_db"))
collection = chroma_client.get_or_create_collection("jobs")

DB_FILE = str(BASE_DIR / "data" / "jobs.db")

def init_jobs_to_db():
    """把20个岗位的JD文本存入向量库"""
    jobs = get_all_jobs()
    
    # 清空旧数据
    try:
        collection.delete(where={})
    except:
        pass
    
    # 准备数据
    ids = []
    documents = []
    metadatas = []
    
    for i, job in enumerate(jobs):
        # 岗位描述文本
        doc = f"{job['title']}（{job['department']}）\n要求：{job['required_years']}年经验\n技能：{job['required_skills']}"
        
        ids.append(f"job_{i}")
        documents.append(doc)
        metadatas.append({
            "job_id": i,
            "title": job["title"],
            "department": job["department"],
            "required_years": job["required_years"],
        })
    
    # 生成嵌入并存入ChromaDB
    embeddings = encoder.encode(documents).tolist()
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )
    print(f"已存入{len(jobs)}个岗位到向量库")

def sql_hard_filter(max_years: int, min_education: str = "本科"):
    """
    SQL硬过滤：先筛掉年限不满足的岗位
    返回通过硬过滤的岗位完整信息列表
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM jobs WHERE required_years <= ?",
        (max_years,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    jobs = []
    for row in rows:
        jobs.append({
            "title": row["title"],
            "department": row["department"],
            "required_years": row["required_years"],
            "required_skills": row["required_skills"],
            "education": row["education"]
        })
    return jobs

def keyword_recall(filtered_jobs: list, resume_skills: list, top_k: int = 5):
    """
    关键词召回：按技能匹配数量排序，补足向量召回的不足
    """
    scored = []
    for job in filtered_jobs:
        job_skills = [s.strip() for s in job["required_skills"].split(",")]
        # 计算简历技能和岗位要求技能的交集数量
        overlap = len(set(resume_skills) & set(job_skills))
        scored.append((overlap, job))
    
    # 按交集数量降序排序
    scored.sort(key=lambda x: x[0], reverse=True)
    
    return [job for overlap, job in scored[:top_k] if overlap > 0]

def search_similar_jobs(resume_skills: list, project_text: str = "", max_years: int = 10, top_k: int = 10):
    """
    混合检索：SQL硬过滤 + 向量语义召回 + 关键词召回补足
    """
    # 第一步：SQL硬过滤
    filtered_jobs = sql_hard_filter(max_years)
    print(f"SQL硬过滤：年限<={max_years}年，保留{len(filtered_jobs)}个岗位")
    
    # 第二步：向量语义检索（query里拼上项目信息）
    query = " ".join(resume_skills) + " " + project_text
    query_embedding = encoder.encode(query).tolist()
    
    # 多召回一些，后面再筛
    vector_k = min(top_k + 5, len(filtered_jobs))
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=vector_k
    )
    
    # 第三步：过滤掉硬条件不满足的岗位
    vector_results = []
    vector_titles = set()
    for doc, meta, distance in zip(
        results['documents'][0], 
        results['metadatas'][0],
        results['distances'][0]
    ):
        if meta['title'] in [j["title"] for j in filtered_jobs]:
            vector_results.append({
                "title": meta['title'],
                "department": meta['department'],
                "required_years": meta['required_years'],
                "distance": distance,
                "source": "vector"
            })
            vector_titles.add(meta['title'])
    
    print(f"向量召回：{len(vector_results)}个岗位")
    
    # 第四步：关键词召回补足（如果向量召回不足top_k）
    if len(vector_results) < top_k:
        keyword_jobs = keyword_recall(filtered_jobs, resume_skills, top_k - len(vector_results))
        for job in keyword_jobs:
            if job["title"] not in vector_titles:
                vector_results.append({
                    "title": job["title"],
                    "department": job["department"],
                    "required_years": job["required_years"],
                    "distance": 999,  # 关键词召回的距离设大一点
                    "source": "keyword"
                })
                vector_titles.add(job["title"])
        print(f"关键词补足后：{len(vector_results)}个岗位")
    
    # 按距离排序（向量召回在前，关键词召回在后）
    vector_results.sort(key=lambda x: x["distance"])
    
    # 只返回top_k个
    return vector_results[:top_k]

if __name__ == "__main__":
    # 初始化岗位到向量库
    init_jobs_to_db()
    
    # 测试1：张明（6年经验）
    print("\n=== 测试1：张明（硕士6年，Python/LangGraph/RAG/LLM） ===")
    test_skills = ["Python", "PyTorch", "LangGraph", "RAG", "LLM"]
    results = search_similar_jobs(test_skills, max_years=6, top_k=5)
    
    print(f"\n语义检索Top-{len(results)}岗位：")
    for i, job in enumerate(results):
        print(f"  {i+1}. {job['title']}（{job['department']}）- {job['required_years']}年要求 - 距离：{job['distance']:.3f}")
    
    # 测试2：刚毕业的应届生（1年经验）
    print("\n=== 测试2：应届生（本科1年，Python/数据分析/SQL） ===")
    test_skills2 = ["Python", "SQL", "数据分析", "Excel"]
    results2 = search_similar_jobs(test_skills2, max_years=1, top_k=5)
    
    print(f"\n语义检索Top-{len(results2)}岗位：")
    for i, job in enumerate(results2):
        print(f"  {i+1}. {job['title']}（{job['department']}）- {job['required_years']}年要求 - 距离：{job['distance']:.3f}")


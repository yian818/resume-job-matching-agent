"""
retriever.py - RAG语义检索层（混合检索架构）
用ChromaDB + BGE嵌入模型做岗位语义匹配
架构：SQL硬过滤 → 向量语义召回
"""
import chromadb
import sqlite3
from sentence_transformers import SentenceTransformer
from database import get_all_jobs

# 加载中文嵌入模型
print("正在加载BGE嵌入模型...")
encoder = SentenceTransformer('BAAI/bge-large-zh-v1.5')

# 初始化ChromaDB
chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
collection = chroma_client.get_or_create_collection("jobs")

DB_FILE = "data/jobs.db"

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
    返回通过硬过滤的岗位title列表
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 筛选年限不超过max_years的岗位
    cursor.execute(
        "SELECT title FROM jobs WHERE required_years <= ?",
        (max_years,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [row[0] for row in rows]

def search_similar_jobs(resume_skills: list, max_years: int = 10, top_k: int = 5):
    """
    混合检索：SQL硬过滤 + 向量语义召回
    """
    # 第一步：SQL硬过滤
    filtered_jobs = sql_hard_filter(max_years)
    print(f"SQL硬过滤：年限<={max_years}年，保留{len(filtered_jobs)}个岗位")
    
    # 第二步：向量语义检索
    query = " ".join(resume_skills)
    query_embedding = encoder.encode(query).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    # 第三步：过滤掉硬条件不满足的岗位
    final_results = []
    for doc, meta, distance in zip(
        results['documents'][0], 
        results['metadatas'][0],
        results['distances'][0]
    ):
        if meta['title'] in filtered_jobs:
            final_results.append({
                "title": meta['title'],
                "department": meta['department'],
                "required_years": meta['required_years'],
                "distance": distance
            })
    
    return final_results

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

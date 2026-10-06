import sqlite3

DB_FILE = "jobs.db"

def init_db():
    """初始化数据库，创建岗位表并插入测试数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 创建岗位表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            department TEXT,
            required_years INTEGER,
            required_skills TEXT,
            education TEXT
        )
    ''')
    
    # 插入测试数据（如果表是空的）
    cursor.execute("SELECT COUNT(*) FROM jobs")
    if cursor.fetchone()[0] == 0:
        jobs = [
            ("AI评测工程师", "AI产品部", 3, "Python,LangGraph,LLM,RAG", "本科"),
            ("后端开发工程师", "技术部", 2, "Java,MySQL,SpringBoot", "本科"),
            ("AI产品经理", "产品部", 1, "AI产品设计,需求分析,数据分析", "本科"),
        ]
        cursor.executemany(
            "INSERT INTO jobs (title, department, required_years, required_skills, education) VALUES (?,?,?,?,?)",
            jobs
        )
    
    conn.commit()
    conn.close()
    print("数据库初始化完成")

def get_all_jobs():
    """从数据库读取所有岗位"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # 让结果可以用列名访问
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM jobs")
    rows = cursor.fetchall()
    
    jobs = []
    for row in rows:
        jobs.append({
            "title": row["title"],
            "department": row["department"],
            "required_years": row["required_years"],
            "required_skills": row["required_skills"],
            "education": row["education"]
        })
    
    conn.close()
    return jobs

if __name__ == "__main__":
    init_db()
    jobs = get_all_jobs()
    print(f"读取到 {len(jobs)} 个岗位：")
    for job in jobs:
        print(f"  - {job['title']}（{job['department']}）")

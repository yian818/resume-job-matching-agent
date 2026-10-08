"""
db_queries.py - SQL查询练习
学习SQL常用操作：增删改查、条件筛选、分组统计
"""
import sqlite3

DB_FILE = "data/jobs.db"

def connect():
    """连接数据库"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # 让结果可以用列名访问
    return conn

def show_all_jobs():
    """1. 查询所有岗位"""
    print("\n=== 1. 查询所有岗位 ===")
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row['id']}. {row['title']}（{row['department']}）- 要求{row['required_years']}年经验")
    conn.close()

def show_jobs_by_years(max_years: int):
    """2. 条件查询：查年限不超过max_years的岗位"""
    print(f"\n=== 2. 查询{max_years}年经验就能投的岗位 ===")
    conn = connect()
    cursor = conn.cursor()
    # ?是占位符，防止SQL注入
    cursor.execute("SELECT title, required_years FROM jobs WHERE required_years <= ?", (max_years,))
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row['title']} - 要求{row['required_years']}年")
    conn.close()

def show_jobs_by_department(dept: str):
    """3. 模糊查询：按部门查岗位"""
    print(f"\n=== 3. 查询{dept}的所有岗位 ===")
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM jobs WHERE department = ?", (dept,))
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row['title']}")
    conn.close()

def count_jobs_by_department():
    """4. 分组统计：每个部门有多少岗位"""
    print("\n=== 4. 各部门岗位数量统计 ===")
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT department, COUNT(*) as count FROM jobs GROUP BY department")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row['department']}: {row['count']}个岗位")
    conn.close()

def search_jobs_by_keyword(keyword: str):
    """5. 模糊搜索：按技能关键词搜岗位"""
    print(f"\n=== 5. 搜索包含'{keyword}'技能的岗位 ===")
    conn = connect()
    cursor = conn.cursor()
    # LIKE是模糊匹配，%是通配符
    cursor.execute("SELECT title, required_skills FROM jobs WHERE required_skills LIKE ?", (f"%{keyword}%",))
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row['title']} - 技能要求：{row['required_skills']}")
    conn.close()

if __name__ == "__main__":
    show_all_jobs()
    show_jobs_by_years(2)
    show_jobs_by_department("产品部")
    count_jobs_by_department()
    search_jobs_by_keyword("Python")

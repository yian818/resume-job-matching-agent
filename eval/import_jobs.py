"""
import_jobs.py - 把eval_dataset.py里的20个JD导入SQLite
"""
import sqlite3
from pathlib import Path
from eval_dataset import JOBS

DB_DIR = Path(__file__).parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "jobs.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# 清空旧数据
cursor.execute("DELETE FROM jobs")
print(f"清空旧岗位数据")

# 导入新岗位
count = 0
for job in JOBS:
    jd_text = job["jd_text"]
    # 从jd_text第一行提取岗位名称（去掉地点、经验等后缀）
    first_line = jd_text.split("\n")[0]
    # 提取括号前的岗位名
    title = first_line.split("（")[0].split("(")[0].strip()

    # 部门：从jd_text里推断，简单处理
    department = "技术部"  # 默认
    if "产品" in jd_text or "运营" in jd_text:
        department = "产品部"
    elif "设计" in jd_text:
        department = "设计部"

    required_years = job.get("required_years", 1)
    required_skills = ",".join(job.get("key_skills", []))
    education = job.get("education", "本科")

    cursor.execute(
        "INSERT INTO jobs (title, department, required_years, required_skills, education) VALUES (?,?,?,?,?)",
        (title, department, required_years, required_skills, education)
    )
    count += 1
    print(f"  ✓ {title} | {department} | {required_years}年 | {required_skills}")

conn.commit()
conn.close()
print(f"\n完成！共导入 {count} 个岗位")

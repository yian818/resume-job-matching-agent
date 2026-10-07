"""测试匹配打分功能"""
from nodes import extract_resume_node, match_jobs_node
from eval_dataset import RESUMES

# 用第1份简历（张明）
s = {
    "resume_text": RESUMES[0]["resume_text"],
    "resume_info": None,
    "jobs": [],
    "report": "",
    "error": None,
    "info_complete": True,
}

print("=== 第1步：简历抽取 ===")
r1 = extract_resume_node(s)
print(f"姓名: {r1['resume_info']['name']}")
print(f"学历: {r1['resume_info']['education']}")
print(f"年限: {r1['resume_info']['work_year']}")
print(f"技能: {r1['resume_info']['skill']}")

print("\n=== 第2步：岗位匹配打分 ===")
r2 = match_jobs_node(r1)
print("\n匹配报告:")
print(r2["report"])
print("\n结构化分数:")
for item in r2.get("matches", []):
    print(f"  {item['score']:3d}分 - {item['job_title']}")
    print(f"       理由: {item['reason']}")

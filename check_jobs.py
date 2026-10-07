"""查看数据库里有多少岗位"""
from database import get_all_jobs

jobs = get_all_jobs()
print(f"共 {len(jobs)} 个岗位：")
print(f"字段名：{list(jobs[0].keys()) if jobs else '空'}")
print()
for j in jobs:
    print(j)
    print()

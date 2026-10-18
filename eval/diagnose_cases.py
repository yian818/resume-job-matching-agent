# diagnose_cases.py - 单案例四信号诊断
#
# 用途：对指定简历跑完整流水线，打印每个候选岗位的
#   llm / rerank / rule / cap / career / final 明细，
# 定位"为什么 truth 岗位没排第一"。
#
# 用法：python eval/diagnose_cases.py R003 R015 R042

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from nodes import extract_resume_node, match_jobs_node
from eval_dataset import RESUMES
from scoring_rules import compute_rule_score, hard_cap, career_match_score, skill_overlap
from database import get_all_jobs


def main():
    rids = sys.argv[1:] or ["R003"]
    jobs_db = {j["title"]: j for j in get_all_jobs()}

    for rid in rids:
        idx = int(rid[1:]) - 1
        resume_text = RESUMES[idx]["resume_text"]
        state = {
            "resume_text": resume_text, "resume_info": None, "jobs": [], "report": "",
            "error": None, "info_complete": True, "missing_fields": [],
            "follow_up_question": "", "user_answer": "", "needs_human": False,
        }
        state = extract_resume_node(state)
        state = match_jobs_node(state)
        info = state["resume_info"]
        scores = state.get("job_scores", [])

        print(f"\n{'='*70}")
        print(f"{rid} name={info.get('name')} career={info.get('career')}")
        print(f"  skills={info.get('skill')}")
        print(f"  work_year={info.get('work_year')} education={info.get('education')}")
        print(f"{'-'*70}")
        for s in scores[:6]:
            title = s["job"]
            bare = title.split("（")[0].strip()
            job = jobs_db.get(bare) or jobs_db.get(title)
            if job:
                rule = compute_rule_score(job, info)
                cap = hard_cap(job, info)
                career = career_match_score(job, info)
                overlap = skill_overlap(job, info)
                print(f"  {title:<28} final={s.get('final_score', s['score']):>3} "
                      f"llm={s.get('llm_score', '?'):>3} rerank={s.get('rerank_score', 0)*100:>5.1f} "
                      f"rule={rule:>3} cap={cap:>3} career={career:>2} overlap={sorted(overlap)}")
            else:
                print(f"  {title:<28} final={s.get('final_score', s['score']):>3} (查不到完整岗位信息)")


if __name__ == "__main__":
    main()

import json
import os
from collections import defaultdict, Counter
from statistics import mean
from typing import Any, Dict, List, Optional, Tuple


DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "seed.json")


def load_data(path: Optional[str] = None) -> Dict[str, Any]:
    p = path or DATA_PATH
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _filter(records: List[dict], **kwargs) -> List[dict]:
    if not kwargs:
        return records
    out = []
    for r in records:
        ok = True
        for k, v in kwargs.items():
            if v is None:
                continue
            if str(r.get(k)) != str(v):
                ok = False
                break
        if ok:
            out.append(r)
    return out


def compute_kpis(data: Dict[str, Any], company_id: Optional[str] = None, cohort_id: Optional[str] = None) -> Dict[str, Any]:
    # Filters
    cohorts = data["cohorts"]
    if company_id:
        cohorts = _filter(cohorts, company_id=company_id)
    if cohort_id:
        cohorts = _filter(cohorts, id=str(cohort_id))
    cohort_ids = {c["id"] for c in cohorts}

    # Attendance
    attendance = [a for a in data["attendance"] if a["cohort_id"] in cohort_ids]
    if attendance:
        present = sum(1 for a in attendance if a.get("status") == "present")
        attendance_rate = present / len(attendance)
    else:
        attendance_rate = 0.0

    # Assessments (assignment completion and quiz average)
    assess = [a for a in data["assessments"] if a["cohort_id"] in cohort_ids]
    if assess:
        completed = sum(1 for a in assess if a.get("submitted", False))
        assignment_completion_rate = completed / len(assess)
        quiz_scores = [a["score"] for a in assess if a.get("type") == "quiz"]
        quiz_avg = mean(quiz_scores) if quiz_scores else 0.0
    else:
        assignment_completion_rate = 0.0
        quiz_avg = 0.0

    # Completion rate (proxy: learners with avg score >= 60 and attendance >= 70%)
    learners = [l for l in data["learners"] if l["cohort_id"] in cohort_ids]
    learner_ids = {l["id"] for l in learners}
    # per-learner attendance ratio
    att_map: Dict[str, Tuple[int, int]] = defaultdict(lambda: [0, 0])  # present, total
    for a in attendance:
        lid = a["learner_id"]
        att_map[lid][1] += 1
        if a.get("status") == "present":
            att_map[lid][0] += 1
    # per-learner avg score
    score_map: Dict[str, List[float]] = defaultdict(list)
    for a in assess:
        score_map[a["learner_id"]].append(a["score"]) 
    completed_learners = 0
    for lid in learner_ids:
        p, t = att_map[lid]
        att_ratio = (p / t) if t else 0.0
        s_list = score_map.get(lid, [])
        avg_score = mean(s_list) if s_list else 0.0
        if att_ratio >= 0.7 and avg_score >= 60:
            completed_learners += 1
    completion_rate = (completed_learners / len(learner_ids)) if learner_ids else 0.0

    # Satisfaction and NPS (NPS from 0-10 scale, approximate from 1-5 by *2 and clamp)
    sats = [s for s in data["satisfaction"] if s["cohort_id"] in cohort_ids]
    ratings = [s["rating"] for s in sats]
    satisfaction_avg = mean(ratings) if ratings else 0.0
    nps_scores = []
    for r in ratings:
        x = int(round(min(10, max(0, r * 2))))
        nps_scores.append(x)
    if nps_scores:
        detractors = sum(1 for x in nps_scores if x <= 6)
        promoters = sum(1 for x in nps_scores if x >= 9)
        total = len(nps_scores)
        nps = ((promoters - detractors) / total) * 100.0
    else:
        nps = 0.0

    return {
        "attendance_rate": round(attendance_rate, 3),
        "assignment_completion_rate": round(assignment_completion_rate, 3),
        "quiz_avg": round(quiz_avg, 1),
        "completion_rate": round(completion_rate, 3),
        "satisfaction_avg": round(satisfaction_avg, 2),
        "nps": round(nps, 1),
        "cohorts": sorted(list(cohort_ids)),
    }


def risk_scores(data: Dict[str, Any], cohort_id: str) -> List[Tuple[str, float, Dict[str, Any]]]:
    # Simple weighted score: low attendance (w=0.5), low score (w=0.3), low satisfaction (w=0.2)
    learners = [l for l in data["learners"] if l["cohort_id"] == cohort_id]
    learner_ids = {l["id"] for l in learners}
    att = [a for a in data["attendance"] if a["cohort_id"] == cohort_id]
    assess = [a for a in data["assessments"] if a["cohort_id"] == cohort_id]
    sats = [s for s in data["satisfaction"] if s["cohort_id"] == cohort_id]

    att_ratio: Dict[str, float] = {}
    tmp = defaultdict(lambda: [0, 0])
    for a in att:
        lid = a["learner_id"]
        tmp[lid][1] += 1
        if a.get("status") == "present":
            tmp[lid][0] += 1
    for lid, (p, t) in tmp.items():
        att_ratio[lid] = (p / t) if t else 0.0

    score_avg: Dict[str, float] = {}
    tmp2 = defaultdict(list)
    for a in assess:
        tmp2[a["learner_id"]].append(a["score"]) 
    for lid, arr in tmp2.items():
        score_avg[lid] = mean(arr) if arr else 0.0

    sat_avg: Dict[str, float] = {}
    tmp3 = defaultdict(list)
    for s in sats:
        tmp3[s["learner_id"]].append(s["rating"]) 
    for lid, arr in tmp3.items():
        sat_avg[lid] = mean(arr) if arr else 0.0

    out = []
    for lid in learner_ids:
        ar = att_ratio.get(lid, 0.0)
        sc = score_avg.get(lid, 0.0)
        sa = sat_avg.get(lid, 0.0)
        # Risk increases when metrics are low
        risk = (1 - ar) * 0.5 + (max(0, (60 - sc)) / 60) * 0.3 + (max(0, (3.5 - sa)) / 3.5) * 0.2
        out.append((lid, round(risk, 3), {"attendance": round(ar, 2), "score": round(sc, 1), "satisfaction": round(sa, 2)}))
    out.sort(key=lambda x: x[1], reverse=True)
    return out


def recommend_modules(data: Dict[str, Any], role: str, level: str, duration_weeks: int, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    tags = [t.lower() for t in (tags or [])]
    modules = data["modules"]
    # Score modules by tag overlap and level match
    scores = []
    for m in modules:
        base = 0
        if m.get("level") == level:
            base += 2
        if tags:
            overlap = len(set([t.lower() for t in m.get("tags", [])]) & set(tags))
            base += overlap
        if role.lower() in ("pm", "product manager") and "pm" in [t.lower() for t in m.get("tags", [])]:
            base += 1
        scores.append((base, m))
    scores.sort(key=lambda x: x[0], reverse=True)
    # Pick top N modules proportional to duration (assume 2 modules/week)
    count = max(2, duration_weeks * 2)
    picked = [m for _, m in scores[:count]]
    total_hours = sum(m.get("duration_hours", 2) for m in picked)
    return {"role": role, "level": level, "weeks": duration_weeks, "modules": picked, "total_hours": total_hours}


def generate_aar(data: Dict[str, Any], cohort_id: str) -> str:
    kpis = compute_kpis(data, cohort_id=cohort_id)
    risks = risk_scores(data, cohort_id)
    top_risk = risks[:3]
    issues = []
    if kpis["attendance_rate"] < 0.8:
        issues.append("출석률 저하")
    if kpis["assignment_completion_rate"] < 0.7:
        issues.append("과제 완료율 저하")
    if kpis["quiz_avg"] < 60:
        issues.append("퀴즈 평균 저하")
    if kpis["satisfaction_avg"] < 3.5:
        issues.append("만족도 저하")
    if kpis["nps"] < 0:
        issues.append("NPS 음수")

    actions = []
    if "출석률 저하" in issues:
        actions.append("주중 리마인드 및 보강 세션 제공")
    if "과제 완료율 저하" in issues:
        actions.append("마감 전 알림 자동화 및 과제 가이드 간소화")
    if "퀴즈 평균 저하" in issues:
        actions.append("난이도 재조정 및 사전 예습 자료 배포")
    if "만족도 저하" in issues:
        actions.append("강사별 피드백 공유와 인터랙션 강화 활동")
    if "NPS 음수" in issues:
        actions.append("고객사 커뮤니케이션 빈도 상향 및 성과 공유")

    txt = []
    txt.append(f"AAR - Cohort {cohort_id}")
    txt.append("요약 KPI:")
    txt.append(str(kpis))
    if issues:
        txt.append("핵심 이슈: " + ", ".join(issues))
    else:
        txt.append("핵심 이슈: 특별한 이슈 없음")
    if top_risk:
        txt.append("고위험 학습자 TOP3: " + ", ".join([f"{lid}(risk={r})" for lid, r, _ in top_risk]))
    txt.append("개선 액션 제안:")
    txt.extend([f"- {a}" for a in (actions or ["다음 기수 동일 운영 유지"])])
    return "\n".join(txt)


def weekly_report(data: Dict[str, Any], company_id: str, cohort_id: str) -> str:
    kpis = compute_kpis(data, company_id=company_id, cohort_id=cohort_id)
    risks = risk_scores(data, cohort_id)
    high_risk = [x for x in risks if x[1] >= 0.5][:5]
    lines = []
    lines.append(f"주간 리포트 - Company {company_id}, Cohort {cohort_id}")
    lines.append("핵심 KPI: " + ", ".join([f"출석 {kpis['attendance_rate']*100:.0f}%",
                                          f"과제 {kpis['assignment_completion_rate']*100:.0f}%",
                                          f"퀴즈 {kpis['quiz_avg']}",
                                          f"완료 {kpis['completion_rate']*100:.0f}%",
                                          f"만족도 {kpis['satisfaction_avg']}",
                                          f"NPS {kpis['nps']:.1f}"]))
    if high_risk:
        lines.append("고위험 학습자: " + ", ".join([f"{lid}(r={r})" for lid, r, _ in high_risk]))
    else:
        lines.append("고위험 학습자: 없음")
    # Simple next steps based on KPI
    recs = []
    if kpis['attendance_rate'] < 0.85:
        recs.append("다음 주 초 리마인드 메시지 자동 발송")
    if kpis['assignment_completion_rate'] < 0.75:
        recs.append("과제 마감 48/12시간 전 이중 알림")
    if kpis['satisfaction_avg'] < 3.8:
        recs.append("세션 중 체크인 질문 2개 추가")
    if not recs:
        recs.append("현재 운영 유지, 베스트 프랙티스 문서화")
    lines.append("다음 단계:")
    lines.extend([f"- {r}" for r in recs])
    return "\n".join(lines)


def parse_kv_args(parts: List[str]) -> Dict[str, str]:
    out = {}
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            out[k.strip()] = v.strip()
    return out

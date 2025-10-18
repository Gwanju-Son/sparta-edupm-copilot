import argparse
from chatbot.core import load_data, compute_kpis, weekly_report, risk_scores, recommend_modules, generate_aar, parse_kv_args


def main():
    parser = argparse.ArgumentParser(description="Training Ops Chatbot (CLI)")
    sub = parser.add_subparsers(dest="cmd")

    p_kpi = sub.add_parser("kpi", help="Compute KPIs")
    p_kpi.add_argument("--company", dest="company_id", default=None)
    p_kpi.add_argument("--cohort", dest="cohort_id", default=None)

    p_week = sub.add_parser("weekly", help="Weekly report")
    p_week.add_argument("--company", dest="company_id", required=True)
    p_week.add_argument("--cohort", dest="cohort_id", required=True)

    p_risk = sub.add_parser("risk", help="Risk scores per learner")
    p_risk.add_argument("--cohort", dest="cohort_id", required=True)
    p_risk.add_argument("--top", dest="top", type=int, default=5)

    p_rec = sub.add_parser("recommend", help="Recommend modules")
    p_rec.add_argument("--role", required=True)
    p_rec.add_argument("--level", required=True)
    p_rec.add_argument("--weeks", type=int, required=True)
    p_rec.add_argument("--tags", nargs="*", default=[])

    p_aar = sub.add_parser("aar", help="Generate AAR for cohort")
    p_aar.add_argument("--cohort", dest="cohort_id", required=True)

    args = parser.parse_args()
    data = load_data()

    if args.cmd == "kpi":
        kpis = compute_kpis(data, company_id=args.company_id, cohort_id=args.cohort_id)
        print(kpis)
    elif args.cmd == "weekly":
        print(weekly_report(data, args.company_id, args.cohort_id))
    elif args.cmd == "risk":
        rows = risk_scores(data, args.cohort_id)[: args.top]
        for lid, r, detail in rows:
            print(lid, r, detail)
    elif args.cmd == "recommend":
        rec = recommend_modules(data, args.role, args.level, args.weeks, args.tags)
        print(f"추천 요약: role={rec['role']} level={rec['level']} weeks={rec['weeks']} total_hours={rec['total_hours']}")
        for m in rec["modules"]:
            print(f"- {m['id']} | {m['topic']} ({m.get('duration_hours', 2)}h) | tags={','.join(m.get('tags', []))}")
    elif args.cmd == "aar":
        print(generate_aar(data, args.cohort_id))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

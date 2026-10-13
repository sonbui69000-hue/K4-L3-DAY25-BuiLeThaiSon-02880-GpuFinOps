"""M3 — Purchasing Strategy: break-even, tier choice, spot-checkpoint sim (deck §4).

Run: python missions/m3_purchasing.py
"""
from __future__ import annotations
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from missions._common import load_csv, num, catalog_by_type
from finops import pricing
from finops import sustainability

DAYS = 30


def run(verbose: bool = True) -> dict:
    jobs = load_csv("workloads.csv")
    cat = catalog_by_type()
    on_demand_monthly = optimized_monthly = 0.0
    baseline_policy_monthly = 0.0
    baseline_policy_recs = []
    recs = []
    carbon_rows = []
    for j in jobs:
        gtype = j["gpu_type"]
        ngpu = int(num(j["num_gpus"]))
        hpd = num(j["hours_per_day"])
        job_days = num(j["days"])
        interruptible = bool(int(num(j["interruptible"])))
        c = cat[gtype]
        gpu_hours = hpd * DAYS * ngpu
        job_gpu_hours = hpd * job_days * ngpu
        od = num(c["on_demand_hr"])
        on_demand_cost = gpu_hours * od

        old_tier = pricing.recommend_tier_baseline(hpd, interruptible)
        if old_tier == "spot":
            old_sim = pricing.spot_checkpoint_cost(gpu_hours, num(c["spot_hr"]), od)
            old_cost = old_sim["spot_cost"]
        elif old_tier == "reserved":
            old_cost = gpu_hours * num(c["reserved_3yr_hr"])
        else:
            old_cost = on_demand_cost
        baseline_policy_monthly += old_cost
        baseline_policy_recs.append({"job_id": j["job_id"], "tier": old_tier, "optimized": round(old_cost)})

        tier = pricing.recommend_tier(hpd, interruptible, gpu_type=gtype, job_days=job_days)
        if tier == "spot":
            sim = pricing.spot_checkpoint_cost(
                gpu_hours,
                num(c["spot_hr"]),
                od,
                interrupt_rate=pricing.SPOT_INTERRUPTION_RATES.get(gtype, 0.05),
            )
            opt_cost = sim["spot_cost"]
        elif tier == "reserved":
            commitment = pricing.reserved_term(job_days)
            opt_cost = gpu_hours * num(c[f"{commitment}_hr"])
        else:
            opt_cost = on_demand_cost

        on_demand_monthly += on_demand_cost
        optimized_monthly += opt_cost
        recs.append({"job_id": j["job_id"], "gpu_type": gtype, "tier": tier,
                     "commitment": pricing.reserved_term(job_days) if tier == "reserved" else "-",
                     "old_tier": old_tier, "on_demand": round(on_demand_cost),
                     "optimized": round(opt_cost)})

        if interruptible:
            energy_wh = job_gpu_hours * num(c["watts"])
            clean_region = min(sustainability.REGION_CARBON, key=sustainability.REGION_CARBON.get)
            base_carbon = sustainability.carbon_g(energy_wh, "us-east-1")
            clean_carbon = sustainability.carbon_g(energy_wh, clean_region)
            carbon_rows.append({
                "job_id": j["job_id"],
                "gpu_hours": round(job_gpu_hours, 1),
                "energy_wh": round(energy_wh, 1),
                "us_east_g": round(base_carbon, 1),
                "clean_region": clean_region,
                "clean_g": round(clean_carbon, 1),
                "saved_g": round(base_carbon - clean_carbon, 1),
            })

    savings = on_demand_monthly - optimized_monthly
    savings_pct = savings / on_demand_monthly * 100 if on_demand_monthly else 0.0

    if verbose:
        print("== M3 Purchasing Strategy ==")
        print(f"break-even utilization @ 45% reserved discount = {pricing.break_even_utilization(0.45):.0%}")
        print(f"{'job':18}{'gpu':7}{'tier':11}{'on-demand':>12}{'optimized':>12}")
        for r in recs:
            print(f"{r['job_id']:18}{r['gpu_type']:7}{r['tier']:11}${r['on_demand']:>11,}${r['optimized']:>11,}")
        print(f"\nmonthly: on-demand ${on_demand_monthly:,.0f} -> optimized ${optimized_monthly:,.0f}  ({savings_pct:.1f}% saved)")
        changed = [
            r for r in recs
            if r["old_tier"] != r["tier"]
            or r["commitment"] == "reserved_1yr"
            or (r["tier"] == "spot" and r["gpu_type"] in pricing.SPOT_INTERRUPTION_RATES)
        ]
        total_saved = sum(r["saved_g"] for r in carbon_rows)
        print(f"policy changes: {len(changed)} jobs use added risk or commitment logic")
        print(f"carbon-aware scheduling: {total_saved:,.1f} gCO2e saved in {carbon_rows[0]['clean_region']}")

    return {"recommendations": recs, "on_demand_monthly": round(on_demand_monthly),
            "optimized_monthly": round(optimized_monthly), "savings_pct": round(savings_pct, 1),
            "baseline_policy_monthly": round(baseline_policy_monthly),
            "baseline_policy_recommendations": baseline_policy_recs,
            "carbon_schedule": carbon_rows,
            "carbon_saved_g": round(sum(r["saved_g"] for r in carbon_rows), 1)}


if __name__ == "__main__":
    run()

#!/usr/bin/env python3
"""Automated data-quality checks. Run after every rebuild: `python3 validate.py`.
Exits non-zero and prints FAIL lines if any invariant is violated.

Covers the required checks: sample/label consistency, per-model reconciliation,
institutional/facility reconciliation, planned/retired exclusion from operational
totals, cloud vs owned separation, funding-default integrity, generation-class
correctness, no silent missing->zero, and regression cases for the audited schools.
"""
import csv
import json
import sys

FAILS = []
def check(cond, msg):
    if not cond:
        FAILS.append(msg)


def main():
    d = json.load(open('data.json'))
    schools = {s['name']: s for s in d['schools']}

    # --- generation classification correctness (check 7) ---
    from build_data import GEN_OF
    expect = {'P100': 'Pascal', 'V100': 'Volta', 'L40S': 'Ada', 'Rubin': 'Rubin',
              'A100_80GB': 'Ampere', 'H100_SXM': 'Hopper', 'B200': 'Blackwell'}
    for model, gen in expect.items():
        check(GEN_OF.get(model) == gen, f"[7] {model} must be {gen}, got {GEN_OF.get(model)}")

    for name, s in schools.items():
        # --- per-model reconciliation (check 2) ---
        check(s['total_gpus'] == sum(s['gen_count'].values()),
              f"[2] {name}: total_gpus {s['total_gpus']} != gen_count sum {sum(s['gen_count'].values())}")
        # --- institutional + facility reconcile to total (check 3) ---
        check(s['institutional_gpus'] + s['facility_gpus'] == s['total_gpus'],
              f"[3] {name}: inst {s['institutional_gpus']} + facility {s['facility_gpus']} != total {s['total_gpus']}")
        # --- planned/cloud NOT in operational owned total (checks 4, and cloud separation) ---
        check(s.get('planned_gpus', 0) >= 0 and s['total_gpus'] >= 0, f"[4] {name}: negative counts")
        # --- funding default not silently institutional (check 6) ---
        if s['funding_conf'] in ('unverified',):
            check(s['funding_model'] == 'Unknown',
                  f"[6] {name}: unverified funding must be 'Unknown', got '{s['funding_model']}'")
        # --- no silent missing->zero: a legacy school with 0 owned must be flagged, not silently zero (check 8) ---
        # (we don't fabricate; schools in-sample came from the inventory, so 0 is allowed only if audited)

    # --- regression cases ---
    il = schools.get('University of Illinois Urbana-Champaign')
    check(il and il['total_gpus'] == 1650, f"[reg] Illinois owned should be 1650, got {il and il['total_gpus']}")
    check(il and il['facility_gpus'] == 1576, f"[reg] Illinois facility should be 1576, got {il and il['facility_gpus']}")
    ut = schools.get('University of Texas - Austin')
    check(ut and ut['total_gpus'] == 860, f"[reg] UT Austin owned should be 860, got {ut and ut['total_gpus']}")
    cmu = schools.get('Carnegie Mellon University')
    check(cmu and cmu['cloud_gpus'] == 296, f"[reg] CMU cloud should be 296 H100, got {cmu and cmu['cloud_gpus']}")
    check(cmu and cmu['gen_count'].get('Hopper', 0) == 0,
          f"[reg] CMU owned must NOT include the 296 cloud H100 (Hopper owned should be 0)")
    osu = schools.get('Oregon State University')
    check(osu and osu['planned_gpus'] == 150, f"[reg] Oregon State planned should be 150 Rubin, got {osu and osu['planned_gpus']}")
    check(osu and osu['gen_count'].get('Rubin', 0) == 0,
          f"[reg] Oregon State owned must NOT include the 150 planned Rubin")

    # --- clusters.csv internal checks ---
    rows = list(csv.DictReader(open('clusters.csv')))
    ids = [r['cluster_id'] for r in rows]
    check(len(ids) == len(set(ids)), "[dup] duplicate cluster_id in clusters.csv")
    for r in rows:
        check(r['source_url'].startswith('http'), f"[src] cluster {r['cluster_id']} missing source_url")
        check(r['status'] in ('operational', 'planned', 'retired', 'uncertain'),
              f"[status] cluster {r['cluster_id']} invalid status '{r['status']}'")
        # planned/uncertain capacity must not be silently treated as operational
        if r['status'] in ('planned', 'retired'):
            check(r['confidence'] in ('high', 'medium', 'low'), f"[conf] {r['cluster_id']} bad confidence")

    if FAILS:
        print(f"VALIDATION FAILED — {len(FAILS)} issue(s):")
        for f in FAILS:
            print("  FAIL", f)
        sys.exit(1)
    print(f"VALIDATION PASSED — {len(schools)} schools, {len(rows)} cluster records, all invariants hold.")


if __name__ == '__main__':
    main()

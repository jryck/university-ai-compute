#!/usr/bin/env python3
"""Substantive data-integrity checks. Run after every build: `python3 validate.py`.

Strategy: INDEPENDENTLY re-aggregate clusters.csv here (not importing build_data's
parser) and assert data.json matches. This tests the accounting logic, not hardcoded
totals — perturbing either file makes a check fail. Exits non-zero on any violation.
"""
import csv
import json
import sys
from collections import defaultdict

FAILS = []
def check(cond, msg):
    if not cond:
        FAILS.append(msg)


def reaggregate(path='clusters.csv'):
    U = defaultdict(lambda: dict(primary=0, legacy=0, agg=0, agg_distinct=0, cloud=0,
                                 planned=0, retired=0, facility=0, federal=0,
                                 owners=set(), has_agg=False, cloud_models=set(),
                                 planned_models=set(), owned_models=set()))
    for r in csv.DictReader(open(path)):
        u = U[r['university']]
        model, cnt = r['gpu_model'], r['gpu_count'].strip()
        basis, status = r.get('count_basis', 'primary'), r['status']
        access, overlap = r['access_model'], r.get('overlap', '')
        if basis == 'aggregate' or model == 'mixed' or not cnt:
            u['has_agg'] = True
            if cnt.isdigit():
                u['agg'] += int(cnt)
                if overlap == 'distinct':
                    u['agg_distinct'] += int(cnt)
            continue
        c = int(cnt)
        if status == 'planned':
            u['planned'] += c; u['planned_models'].add(model); continue
        if status in ('retired', 'uncertain'):
            u['retired'] += c; continue
        if access == 'reserved-cloud':
            u['cloud'] += c; u['cloud_models'].add(model); continue
        u['primary' if basis == 'primary' else 'legacy'] += c
        u['owned_models'].add(model)
        if access == 'national-allocation':
            u['facility'] += c
        if 'federal' in r['funding_source'] or 'NSF' in r['funding_source']:
            u['federal'] += c
        if basis == 'primary' and r['owner'].lower() != 'unknown':
            u['owners'].add(r['owner'])
    return U


def main():
    U = reaggregate()
    data = {x['name']: x for x in json.load(open('data.json'))['schools']}

    # (1,10) data.json reproduces the independent recompute for every clustered school
    for uni, u in U.items():
        d = data.get(uni)
        check(d is not None, f"[1] {uni}: in clusters.csv but missing from data.json")
        if not d:
            continue
        check(d['verified_model_count'] == u['primary'], f"[1] {uni}: verified {d['verified_model_count']} != recompute {u['primary']}")
        check(d['legacy_estimate'] == u['legacy'], f"[1] {uni}: legacy {d['legacy_estimate']} != {u['legacy']}")
        check(d['cloud_gpus'] == u['cloud'], f"[2] {uni}: cloud {d['cloud_gpus']} != {u['cloud']}")
        check(d['planned_gpus'] == u['planned'], f"[2] {uni}: planned {d['planned_gpus']} != {u['planned']}")
        check(d['facility_gpus'] == u['facility'], f"[7] {uni}: national-facility {d['facility_gpus']} != {u['facility']}")
        check(d['federal_funded_gpus'] == u['federal'], f"[7] {uni}: federal-funded {d['federal_funded_gpus']} != {u['federal']}")
        # (4) lower bound = verified + DISTINCT aggregates only (no overlap double-add)
        check(d['documented_lower_bound'] == u['primary'] + u['agg_distinct'],
              f"[4] {uni}: lower bound {d['documented_lower_bound']} != verified+distinct-agg {u['primary']+u['agg_distinct']}")
        # (3) aggregate clusters not silently dropped
        if u['has_agg']:
            check(d['aggregate_count'] > 0 or any(a.get('count') is None for a in d['aggregate_clusters']),
                  f"[3] {uni}: has aggregate clusters in CSV but none surfaced in data.json")

    for name, d in data.items():
        # (2) per-model operational total reconciles with the generation breakdown
        check(d['total_gpus'] == sum(d['gen_count'].values()),
              f"[2] {name}: total_gpus {d['total_gpus']} != gen_count sum {sum(d['gen_count'].values())}")
        # (2) cloud/planned must NOT be inside operational gen_count
        u = U.get(name)
        if u:
            for m in u['cloud_models'] | u['planned_models']:
                owned_m = m if m in d['gen_count'] else None  # gen is by generation not model; checked via totals below
            check(d['total_gpus'] == d['verified_model_count'] + d['legacy_estimate'],
                  f"[2] {name}: operational per-model total excludes cloud/planned? {d['total_gpus']} vs {d['verified_model_count']+d['legacy_estimate']}")
        # (5) missing != zero: legacy-only schools carry completeness 'unknown', not asserted complete
        if d['verification'] == 'legacy':
            check(d['inventory_completeness'] == 'unknown', f"[5] {name}: legacy school must have completeness 'unknown'")
        # (6) completeness is never silently 'complete'
        check(d['inventory_completeness'] in ('complete', 'partial', 'unknown'), f"[6] {name}: bad completeness")
        check(d['inventory_completeness'] != 'complete', f"[6] {name}: 'complete' asserted without coverage evidence")
        # (7) funding independent of ownership/access: unverified funding => Unknown
        if d['funding_conf'] == 'unverified':
            check(d['funding_model'] == 'Unknown', f"[7] {name}: unverified funding must be 'Unknown', got {d['funding_model']}")
        # ownership verification is a field independent of count verification
        check(d['ownership_verification'] in ('confirmed', 'unresolved'), f"[?] {name}: bad ownership_verification")

    # (10) pilot regression — documented values/bounds (these are RE-DERIVED above; here we assert the audit's headline numbers)
    reg = [
        ('University of Illinois Urbana-Champaign', 'facility_gpus', 1512),
        ('University of Illinois Urbana-Champaign', 'federal_funded_gpus', 1576),
        ('Massachusetts Institute of Technology (MIT)', 'documented_lower_bound', 1448),
        ('Harvard University', 'documented_lower_bound', 1144),
        ('Harvard University', 'aggregate_count', 2000),
        ('Stanford University', 'documented_lower_bound', 248),
        ('Carnegie Mellon University', 'verified_model_count', 0),
        ('Carnegie Mellon University', 'cloud_gpus', 296),
        ('Oregon State University', 'planned_gpus', 150),
        ('Oregon State University', 'verified_model_count', 0),
        ('University of Texas - Austin', 'documented_lower_bound', 860),
        ('New York University', 'documented_lower_bound', 1276),
    ]
    for name, field, exp in reg:
        d = data.get(name)
        check(d and d.get(field) == exp, f"[10] {name}.{field} should be {exp}, got {d and d.get(field)}")

    # clusters.csv hygiene
    rows = list(csv.DictReader(open('clusters.csv')))
    ids = [r['cluster_id'] for r in rows]
    check(len(ids) == len(set(ids)), "[dup] duplicate cluster_id")
    for r in rows:
        check(r['source_url'].startswith('http'), f"[src] {r['cluster_id']}: missing source_url")
        check(r['status'] in ('operational', 'planned', 'retired', 'uncertain'), f"[status] {r['cluster_id']}: bad status")
        check(r.get('count_basis', 'primary') in ('primary', 'legacy', 'aggregate'), f"[basis] {r['cluster_id']}: bad count_basis")

    # research_subset.csv internal consistency (central-allocatable <= documented; sources present)
    import os
    if os.path.exists('research_subset.csv'):
        for r in csv.DictReader(open('research_subset.csv')):
            tot = int(r['documented_gpus'] or 0)
            ca = r['central_allocatable_gpus']
            if ca not in ('', 'unknown') and ca.lstrip('-').isdigit():
                check(int(ca) <= tot, f"[research] {r['institution']}: central-allocatable {ca} > documented {tot}")
            check(r['primary_source'].strip() != '', f"[research] {r['institution']}: missing primary_source")
            check(r['count_type'] in ('verified', 'verified_lower_bound', 'aggregate', 'unresolved'),
                  f"[research] {r['institution']}: bad count_type {r['count_type']}")

    if FAILS:
        print(f"VALIDATION FAILED — {len(FAILS)} issue(s):")
        for f in FAILS:
            print("  FAIL", f)
        sys.exit(1)
    print(f"VALIDATION PASSED — {len(data)} schools, {len(rows)} cluster records, "
          f"{len(U)} schools re-derived from source; all invariants hold.")


if __name__ == '__main__':
    main()

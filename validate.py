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
        if status in ('planned', 'early-operations'):
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
    PAYLOAD = json.load(open('data.json'))
    data = {x['name']: x for x in PAYLOAD['schools']}

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
        ('Harvard University', 'documented_lower_bound', 1384),  # Kempner 1144 + Cannon general 240 (144 A100 + 96 H200)
        ('Harvard University', 'aggregate_count', 0),  # Cannon now model-level; ~2000 combined figure (incl MIG) not used
        ('Stanford University', 'documented_lower_bound', 1504),  # Marlowe 248 + Sherlock 1256 (aggregate, distinct)
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
        check(r['status'] in ('operational', 'planned', 'early-operations', 'retired', 'uncertain'), f"[status] {r['cluster_id']}: bad status")
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

    # [recon] ONE authoritative universe — the same documented total everywhere.
    herd = {h['institution']: h for h in PAYLOAD.get('herd50', [])}
    gen = {e['name']: e for e in PAYLOAD.get('gen_chart', [])}
    hl = PAYLOAD.get('headline', {})

    # gen_chart reconciles exactly to the HERD-50 documented universe
    documented_herd = [h for h in herd.values() if h['documented_gpus'] > 0]
    check(len(gen) == len(documented_herd),
          f"[recon] gen_chart has {len(gen)} entries, {len(documented_herd)} herd50 documented")
    check(sum(e['documented'] for e in gen.values()) == hl.get('total_documented_gpus'),
          "[recon] gen_chart documented sum != headline total_documented_gpus")
    for name, e in gen.items():
        h = herd.get(name)
        check(h is not None, f"[recon] gen_chart {name} not in herd50")
        check(e['documented'] == (h['documented_gpus'] if h else None),
              f"[recon] {name}: gen_chart documented {e['documented']} != herd50 {h and h['documented_gpus']}")
        check(e['classified_count'] + e['unknown_count'] == e['documented'],
              f"[recon] {name}: classified+unknown {e['classified_count']}+{e['unknown_count']} != documented {e['documented']}")
        check(e['classified_count'] <= e['documented'],
              f"[recon] {name}: classified {e['classified_count']} > documented {e['documented']}")
        # generations assigned only where model-level evidence exists
        if not e['has_model_evidence']:
            check(e['classified_count'] == 0,
                  f"[recon] {name}: has generation counts without model-level evidence")

    # research_subset (allocation-regime chart) uses the SAME documented totals as herd50
    for r in PAYLOAD.get('research_subset', []):
        h = herd.get(r['institution'])
        if h:
            check(int(r['documented_gpus'] or 0) == h['documented_gpus'],
                  f"[recon] research_subset {r['institution']} documented {r['documented_gpus']} != herd50 {h['documented_gpus']}")

    # named cross-chart test schools: identical documented total in every structure
    for name, exp in [('Massachusetts Institute of Technology', 1448), ('New York University', 1276),
                      ('Harvard University', 1384), ('University of Illinois Urbana-Champaign', 1650),
                      ('Cornell University', 755)]:
        check(herd.get(name, {}).get('documented_gpus') == exp, f"[recon] herd50 {name} != {exp}")
        check(gen.get(name, {}).get('documented') == exp, f"[recon] gen_chart {name} != {exp}")

    # reference points are NEVER folded into HERD-50 figures
    for rp in PAYLOAD.get('reference_points', []):
        check(rp['institution'] not in herd, f"[recon] reference point {rp['institution']} leaked into herd50")

    # CS R&D (NSF HERD FY2024 field data): present for all herd50; reported 0 kept distinct from missing
    cs_present = [h for h in herd.values() if h.get('cs_rd_fy2024_m') is not None]
    check(len(cs_present) == len(herd), f"[cs] cs_rd present for {len(cs_present)}/{len(herd)} herd50 schools")
    for h in herd.values():
        v = h.get('cs_rd_fy2024_m')
        check(v is None or (isinstance(v, (int, float)) and v >= 0),
              f"[cs] {h['institution']}: bad cs_rd_fy2024_m {v!r}")
    # medical centers with no CS-field R&D must be reported 0.0, NOT null (zero != missing)
    for name in ['University of California San Francisco', 'Icahn School of Medicine at Mount Sinai',
                 'UT Southwestern Medical Center']:
        if name in herd:
            check(herd[name].get('cs_rd_fy2024_m') == 0,
                  f"[cs] {name}: expected reported 0 CS R&D, got {herd[name].get('cs_rd_fy2024_m')!r}")

    # facility-capacity subtraction: never exceeds documented; separable flag is consistent
    fac_hosts = [h for h in herd.values() if h.get('facility_gpus', 0) > 0]
    check(len(fac_hosts) >= 6, f"[facility] expected >=6 facility hosts, got {len(fac_hosts)}")
    for h in herd.values():
        fac = h.get('facility_gpus', 0)
        check(0 <= fac <= h['documented_gpus'],
              f"[facility] {h['institution']}: facility_gpus {fac} out of range vs documented {h['documented_gpus']}")
        exp_sep = (fac == 0) or ((h['documented_gpus'] - fac) > 0)
        check(h.get('residual_separable') == exp_sep,
              f"[facility] {h['institution']}: residual_separable flag inconsistent")

    if FAILS:
        print(f"VALIDATION FAILED — {len(FAILS)} issue(s):")
        for f in FAILS:
            print("  FAIL", f)
        sys.exit(1)
    print(f"VALIDATION PASSED — {len(data)} schools, {len(rows)} cluster records, "
          f"{len(U)} schools re-derived from source; all invariants hold.")


if __name__ == '__main__':
    main()

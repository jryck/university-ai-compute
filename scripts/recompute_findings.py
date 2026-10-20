#!/usr/bin/env python3
"""Recompute the headline findings (Obs. 1-3) directly from the CSVs, with
sensitivity variants. Reads only herd50.csv + herd_cs.csv (plus a small set of
documented national/state-facility figures that mirror build_data's
HERD_FACILITY_GPUS, and the Horizon early-operations figure). Prints correlations
(Pearson + Spearman, raw + log) and concentration under each variant so the prose
in RESEARCH_FINDINGS.md / the site can be regenerated or checked.

Run: python3 scripts/recompute_findings.py
"""
import csv
import math
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Documented national/state-facility capacity contained within each school's
# HERD-50 figure (mirrors build_data.HERD_FACILITY_GPUS; primary sources in
# clusters.csv / herd50 notes). residual_separable = documented > facility.
FACILITY = {
    'University of Illinois Urbana-Champaign': 1512,
    'University of Texas at Austin': 600,
    'Purdue University': 148,
    'University of California San Diego': 344,
    'Ohio State University': 904,
    'University of Pittsburgh': 264,
}
# Horizon (TACC) GB200, early-operations as of 2026-08 (TACC docs); excluded from
# the documented lower bound by default. Variant (iii) adds it to UT Austin.
HORIZON_SCHOOL = 'University of Texas at Austin'
HORIZON_GPUS = 4000


def load():
    rows = []
    cs = {}
    with open(os.path.join(HERE, 'herd_cs.csv')) as f:
        for r in csv.DictReader(f):
            cs[r['institution']] = float(r['cs_rd_fy2024_m'])
    with open(os.path.join(HERE, 'herd50.csv')) as f:
        for r in csv.DictReader(f):
            doc = int(r['documented_gpus'] or 0)
            rows.append({
                'inst': r['institution'],
                'doc': doc,
                'rd': float(r['rd_fy2024_m'] or 0),
                'endow': float(r['endowment_b']) if r['endowment_b'] else None,
                'cs': cs.get(r['institution']),
                'facility': FACILITY.get(r['institution'], 0),
            })
    return rows


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return cov / (sx * sy) if sx and sy else None


def rank(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(xs, ys):
    return pearson(rank(xs), rank(ys)) if len(xs) >= 3 else None


def corr_line(sample, xkey, yf):
    pairs = [(s[xkey], yf(s)) for s in sample if s[xkey] is not None and yf(s) is not None]
    if len(pairs) < 3:
        return f"n={len(pairs)} (too few)"
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    pr = pearson(xs, ys)
    sr = spearman(xs, ys)
    # log transform on strictly-positive pairs only
    logp = [(x, y) for x, y in pairs if x > 0 and y > 0]
    if len(logp) >= 3:
        lpr = pearson([math.log10(x) for x, y in logp], [math.log10(y) for x, y in logp])
        lsr = spearman([math.log10(x) for x, y in logp], [math.log10(y) for x, y in logp])
        logs = f"log r={lpr:+.2f} rho={lsr:+.2f} n={len(logp)}"
    else:
        logs = "log n<3"
    return f"raw r={pr:+.2f} rho={sr:+.2f} n={len(pairs)} | {logs}"


def concentration(sample, yf):
    vals = sorted((yf(s) for s in sample), reverse=True)
    tot = sum(vals)
    if tot <= 0:
        return None
    t5 = sum(vals[:5]) / tot * 100
    t10 = sum(vals[:10]) / tot * 100
    return t5, t10, tot


def report():
    rows = load()
    doc = [r for r in rows if r['doc'] > 0]
    print("=" * 72)
    print("RECOMPUTED FINDINGS (source: herd50.csv + herd_cs.csv)")
    print("=" * 72)

    variants = {}
    # (i) all documented, y = documented
    variants['(i) all documented'] = (doc, lambda s: s['doc'])
    # (ii) excluding national/state-facility GPUs: y = documented - facility,
    #      drop schools whose residual is not separable (documented == facility)
    exfac = [r for r in doc if not (r['facility'] > 0 and r['doc'] - r['facility'] <= 0)]
    variants['(ii) excl. national/state-facility'] = (exfac, lambda s: s['doc'] - s['facility'])
    # (iii-excl) Horizon excluded (default state)
    variants['(iii-excl) Horizon excluded'] = (doc, lambda s: s['doc'])
    # (iii-incl) Horizon included: add 4000 to UT Austin's documented
    def y_horizon(s):
        return s['doc'] + (HORIZON_GPUS if s['inst'] == HORIZON_SCHOOL else 0)
    variants['(iii-incl) Horizon included (+4000 UT Austin)'] = (doc, y_horizon)

    for label, (sample, yf) in variants.items():
        print(f"\n--- {label} ---")
        print(f"  documented GPUs vs Total R&D : {corr_line(sample, 'rd', yf)}")
        print(f"  documented GPUs vs CS R&D    : {corr_line(sample, 'cs', yf)}")
        print(f"  documented GPUs vs Endowment : {corr_line(sample, 'endow', yf)}")
        c = concentration(sample, yf)
        if c:
            t5, t10, tot = c
            print(f"  concentration: top-5={t5:.0f}%  top-10={t10:.0f}%  (total documented={tot:.0f})")

    # national-facility share (Obs. 3): sum of facility GPUs / total documented
    tot_doc = sum(r['doc'] for r in doc)
    fac_sum = sum(r['facility'] for r in doc)
    print(f"\n--- Obs. 3: national/state-facility share (all documented) ---")
    print(f"  facility GPUs = {fac_sum} of {tot_doc} documented = {fac_sum/tot_doc*100:.0f}%")
    print(f"  facility hosts: {', '.join(k for k in FACILITY)}")

    # R&D top-10 share, for the Obs. 2 concentration comparison
    rd_sorted = sorted((r['rd'] for r in doc), reverse=True)
    print(f"\n--- Obs. 2 reference: R&D concentration (documented schools) ---")
    print(f"  top-5 R&D share={sum(rd_sorted[:5])/sum(rd_sorted)*100:.0f}%  "
          f"top-10 R&D share={sum(rd_sorted[:10])/sum(rd_sorted)*100:.0f}%")


if __name__ == '__main__':
    report()

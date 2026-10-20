#!/usr/bin/env python3
"""Recurrence guard: fail if a number quoted in the prose (.md files, static site
text) disagrees with what the current data produce. Canonical values come from the
built payload data.json (which build_data.py derives from the CSVs), plus herd50.csv
for per-school totals. Run after editing data or prose:

    python3 scripts/build_data.py && python3 scripts/check_numbers.py

Add a check below when you introduce a new quoted figure. Targeted (labeled-regex)
rather than a blanket number scan, to avoid false positives on legitimate repeats.
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def canonical():
    d = json.load(open(os.path.join(HERE, 'data.json')))
    hl = d['headline']
    h = d['herd50']
    docs = sorted((x['documented_gpus'] for x in h), reverse=True)
    tot = sum(docs)
    fac = sum(x.get('facility_gpus', 0) for x in h)
    by = {x['institution']: x['documented_gpus'] for x in h}
    return {
        'total': hl['total_documented_gpus'],
        'top10_gpu': hl['top10_gpu_share'],
        'top10_rd': hl['top10_rd_share'],
        'top5_gpu': round(100 * sum(docs[:5]) / tot),
        'facility_share': round(100 * fac / tot),
        'corr_rd': hl['corr_rd_gpu'],
        'corr_endow': hl['corr_endow_gpu'],
        'harvard': by.get('Harvard University'),
        'jhu': by.get('Johns Hopkins University'),
    }


# (file, human label, regex w/ one capture group, key into canonical, parse fn)
def _int(s):
    return int(s.replace(',', ''))


CHECKS = [
    ('README.md', 'same-total example: Harvard', r'Harvard ≥([\d,]+)', 'harvard', _int),
    ('template.html', 'methodology example: Harvard', r'Harvard ≥([\d,]+)', 'harvard', _int),
    ('README.md', 'findings: R&D Pearson r', r'R&D vs\. documented\s*\n?\s*GPUs \(Pearson r ≈ (−?\+?[\d.]+)', 'corr_rd',
     lambda s: float(s.replace('−', '-').replace('+', ''))),
    ('README.md', 'findings: endowment Pearson r', r'endowment vs\. documented GPUs \(r ≈ \+?([\d.]+)', 'corr_endow', float),
    ('README.md', 'findings: top-10 GPU share', r'top-10 fleets hold \*\*(\d+)%\*\*', 'top10_gpu', int),
    ('README.md', 'findings: top-10 R&D share', r'of documented GPUs vs (\d+)% of R&D', 'top10_rd', int),
    ('RESEARCH_FINDINGS.md', 'header: total documented', r'Total documented: \*\*≥([\d,]+) GPUs', 'total', _int),
    ('RESEARCH_FINDINGS.md', 'Obs.2: top-10 GPU share', r'top-10\s+schools\s*\n?\s*hold \*\*(\d+)% of documented GPUs', 'top10_gpu', int),
    ('RESEARCH_FINDINGS.md', 'Obs.2: top-10 R&D share', r'but only (\d+)% of R&D', 'top10_rd', int),
    ('RESEARCH_FINDINGS.md', 'Obs.2: top-5 GPU share', r'top-5,? \*\*(\d+)%', 'top5_gpu', int),
    ('RESEARCH_FINDINGS.md', 'Obs.3: national-facility share', r'account for \*\*≥?(\d+)% of all', 'facility_share', int),
]


def main():
    can = canonical()
    print(f"Canonical (from data.json / CSVs): {can}\n")
    fails = []
    for fname, label, rx, key, parse in CHECKS:
        path = os.path.join(HERE, fname)
        if not os.path.exists(path):
            continue
        text = open(path, encoding='utf-8').read()
        m = re.search(rx, text)
        if not m:
            print(f"  ? {fname}: '{label}' pattern not found (skipped)")
            continue
        got = parse(m.group(1))
        exp = can[key]
        ok = (abs(got - exp) < 0.005) if isinstance(exp, float) else (got == exp)
        print(f"  {'OK ' if ok else 'FAIL'} {fname}: {label} = {m.group(1)!r} (expected {exp})")
        if not ok:
            fails.append(f"{fname}: {label} says {m.group(1)!r}, current data = {exp}")
    print()
    if fails:
        print(f"NUMBER CHECK FAILED — {len(fails)} stale figure(s):")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("NUMBER CHECK PASSED — all quoted figures match current data.")


if __name__ == '__main__':
    main()

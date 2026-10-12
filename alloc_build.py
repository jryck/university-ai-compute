#!/usr/bin/env python3
"""Build the national leadership-computing / accessible-compute dataset -> alloc.json.

Per university, combines three documented signals:
  - INCITE 2025 (ALL facilities: Frontier/Aurora/Polaris) — parsed from the official
    INCITE fact-sheet PDF (pdfs/incite2025.pdf, retrieved via the Wayback Machine).
  - ALCC 2025 (ALL facilities incl. Perlmutter) — parsed from the ASCR fact-sheet PDF
    (pdfs/alcc2025.pdf).
  - NAIRR pilot project counts — from the nairrpilot.org awards CSV (AI-specific access).

Leadership node-hours = INCITE + ALCC (both complete across facilities). NSF ACCESS is
not quantified (no public per-institution totals). Node-hours and NAIRR project counts
are distinct units and are never mixed with owned-GPU counts.
"""
import re
import json
import os

# ---- canonical name -> exact source-institution strings (sum these) ----
# Disambiguation traps handled explicitly: "University of Illinois" / "Univ. of
# Illinois at Urbana-Champaign" are UIUC, but "University of Illinois Chicago" is UIC
# (NOT in our set). "Harvard University" != "Harvard-Smithsonian Center". PPPL/SLAC
# stay with the national lab (Tier 3), not folded into the university.
INCITE_NAME_MAP = {
    'University of Illinois Urbana-Champaign': ['Univ. of Illinois at Urbana-Champaign', 'University of Illinois'],
    'Princeton University': ['Princeton University'],
    'Stanford University': ['Stanford University'],
    'University of Southern California': ['University of Southern California'],
    'University of Michigan - Ann Arbor': ['University of Michigan'],
    'University of Notre Dame': ['University of Notre Dame'],
    'Massachusetts Institute of Technology (MIT)': ['Massachusetts Institute of Technology'],
    'Columbia University': ['Columbia University'],
    'Duke University': ['Duke University'],
    'Georgia Institute of Technology': ['Georgia Institute of Technology'],
    'Harvard University': ['Harvard University'],
    'University of Chicago': ['University of Chicago'],
}
ALCC_NAME_MAP = {
    'Stanford University': 'Stanford University',
    'Georgia Institute of Technology': 'Georgia Institute of Technology',
    'Massachusetts Institute of Technology (MIT)': 'MIT',
    'California Institute of Technology': 'California Institute of Technology',
    'University of Kentucky': 'University of Kentucky',
    'University of Michigan - Ann Arbor': 'University of Michigan, Ann Arbor',
    'University of Chicago': 'University of Chicago',
}
NAIRR_MAP = {
    'University of Illinois Urbana-Champaign': 'University of Illinois Urbana-Champaign',
    'University of Texas - Austin': 'University of Texas at Austin',
    'New York University': 'New York University', 'University of Florida': 'University of Florida',
    'Texas A&M University': 'Texas A&M University', 'Princeton University': 'Princeton University',
    'Stanford University': 'Stanford University', 'Harvard University': 'Harvard University',
    'Massachusetts Institute of Technology (MIT)': 'Massachusetts Institute of Technology',
    'University of Washington': 'University of Washington',
    'Georgia Institute of Technology': 'Georgia Institute of Technology',
    'Yale University': 'Yale University', 'Carnegie Mellon University': 'Carnegie Mellon University',
    'Johns Hopkins University': 'Johns Hopkins University', 'Oregon State University': 'Oregon State University',
    'Rensselaer Polytechnic Institute': 'Rensselaer Polytechnic Institute', 'Clemson University': 'Clemson University',
    'Washington University in St. Louis': 'Washington University in St. Louis', 'University of Vermont': 'University of Vermont',
    'California Institute of Technology': 'California Institute of Technology', 'Rice University': 'Rice University',
    'Boston University': 'Boston University', 'University of Virginia': 'University of Virginia',
    'Arizona State University': 'Arizona State University', 'Michigan State University': 'Michigan State University',
    'Northeastern University': 'Northeastern University', 'University of Wyoming': 'University of Wyoming',
    'University of Wisconsin - Madison': 'University of Wisconsin-Madison',
    'University of Central Florida': 'University of Central Florida', 'Southern Methodist University': 'Southern Methodist University',
    'University of Chicago': 'University of Chicago', 'University of California, Los Angeles': 'University of California, Los Angeles',
    'University of Pittsburgh': 'University of Pittsburgh', 'University of Kentucky': 'University of Kentucky',
    'University of Utah': 'University of Utah', 'Case Western Reserve University': 'Case Western Reserve University',
    'University of Louisville': 'University of Louisville', 'University of Oklahoma': 'University of Oklahoma',
    'University of South Carolina': 'University of South Carolina', 'University of Michigan - Ann Arbor': 'University of Michigan',
    'University of Alabama - Birmingham': 'University of Alabama, Birmingham',
    'Columbia University': 'Columbia University in the City of New York', 'Tufts University': 'Tufts University',
    'University of Nebraska - Lincoln': 'University of Nebraska, Lincoln', 'Duke University': 'Duke University',
    'University of Notre Dame': 'University of Notre Dame', 'University of Southern California': 'University of Southern California',
}
NOTABLE = {
    'Princeton University': 'Core-collapse supernova + fusion simulations (INCITE, 3.8M node-hrs)',
    'Stanford University': 'Engine-inlet flow + photocatalyst discovery (INCITE+ALCC)',
    'University of Southern California': 'AI-guided quantum-materials simulation (INCITE)',
    'University of Michigan - Ann Arbor': 'Foundation models for crystals (INCITE)',
    'University of Notre Dame': 'High-fidelity combustion/CFD on Frontier (INCITE)',
    'University of Illinois Urbana-Champaign': 'QMC-HAMM multiscale materials (INCITE)',
    'Massachusetts Institute of Technology (MIT)': 'ML for lattice QCD (INCITE+ALCC)',
    'Columbia University': 'OpenFold protein-interaction ML (INCITE)',
    'Duke University': 'Digital twins for blood-cell analysis (INCITE)',
    'Georgia Institute of Technology': 'Bubble-laden turbulent flows (ALCC, 2M node-hrs)',
    'Harvard University': 'Materials for energy storage (INCITE)',
    'University of Chicago': 'Inner-ear mechanotransduction; neutrino science (INCITE+ALCC)',
    'California Institute of Technology': 'ALCC leadership allocation (820K node-hrs)',
    'University of Kentucky': 'ALCC leadership allocation (477K node-hrs)',
}


def _agg_pdf(path, split_re, inst_re, machine_re):
    import pypdf
    txt = "\n".join((p.extract_text() or '') for p in pypdf.PdfReader(path).pages)
    agg = {}
    for b in re.split(split_re, txt):
        m = re.search(inst_re, b)
        if not m:
            continue
        inst = m.group(1).strip().rstrip('.')
        tot = sum(int(a.replace(',', '')) for a in re.findall(machine_re, b))
        if tot:
            cur = agg.get(inst, [0, 0])
            agg[inst] = [cur[0] + tot, cur[1] + 1]
    return agg


def parse_incite(path='pdfs/incite2025.pdf'):
    return _agg_pdf(path, r'(?:^|\n)\s*Type:\s',
                    r'Principal Investigator:\s*[^,\n]+,\s*([^\n]+)',
                    r'([\d,]{4,})\s+(?:Aurora|Frontier|Polaris)\s+node-?hours')


def parse_alcc(path='pdfs/alcc2025.pdf'):
    return _agg_pdf(path, r'\d{4} ASCR Leadership Computing Challenge Award',
                    r'Principal\s+[^\n(]*\(([^)]+)\)\s*\n?\s*Investigator',
                    r'[\d,]{4,}(?=\s+on\s+(?:Frontier|Aurora|Polaris|Perlmutter))')


def main():
    incite = parse_incite() if os.path.exists('pdfs/incite2025.pdf') else {}
    alcc = parse_alcc() if os.path.exists('pdfs/alcc2025.pdf') else json.load(open('pdfs/alcc_by_inst.json'))
    nairr = json.load(open('pdfs/nairr_by_inst.json')) if os.path.exists('pdfs/nairr_by_inst.json') else {}

    canon_names = set(INCITE_NAME_MAP) | set(ALCC_NAME_MAP) | set(NAIRR_MAP)
    alloc = {}
    for canon in canon_names:
        inc_nh = sum(incite.get(s, [0, 0])[0] for s in INCITE_NAME_MAP.get(canon, []))
        inc_p = sum(incite.get(s, [0, 0])[1] for s in INCITE_NAME_MAP.get(canon, []))
        alcc_nh, alcc_p = alcc.get(ALCC_NAME_MAP.get(canon, '__none__'), [0, 0])
        nairr_p = nairr.get(NAIRR_MAP.get(canon, '__none__'), 0)
        if inc_nh or alcc_nh or nairr_p:
            alloc[canon] = {
                'incite_nh': inc_nh, 'alcc_nh': alcc_nh, 'total_nh': inc_nh + alcc_nh,
                'projects': inc_p + alcc_p, 'nairr_projects': nairr_p,
                'notable': NOTABLE.get(canon, ''),
            }

    json.dump(alloc, open('alloc.json', 'w'), indent=2)
    print(f'Wrote alloc.json: {len(alloc)} schools with documented national access')
    for name, a in sorted(alloc.items(), key=lambda x: (-x[1]['total_nh'], -x[1]['nairr_projects'])):
        print(f"  {name[:40]:40} lead {a['total_nh']:>9,} nh (INCITE {a['incite_nh']:>9,}+ALCC {a['alcc_nh']:>9,}) | NAIRR {a['nairr_projects']:>2}")


if __name__ == '__main__':
    main()

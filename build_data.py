#!/usr/bin/env python3
"""Build the merged university-compute dataset.

Joins the GPU inventory (gpusperstudent.org master_data.csv) with the most
recent available university endowment figures (FY2025 where reported, else
FY2024) and computes derived economics metrics. Outputs data.json which is
embedded into index.html.
"""
import csv
import json
import os

GPU_MODELS = ['H100_SXM', 'H100_PCIe', 'H200', 'A100_80GB', 'A100_40GB',
              'B200', 'B100', 'Rubin', 'A40', 'RTX_A6000', 'L40S',
              'V100', 'P100', 'GH200', 'A10']

# Endowment figures keyed by the EXACT university name in the GPU CSV.
# value = endowment in $B, fy = fiscal year of the figure, note = caveat.
# FY2025 = year ending ~June 30 2025 (latest reported as of Oct 2026).
ENDOWMENTS = {
    'University of Illinois Urbana-Champaign':      (3.80, 2025, 'U of Illinois System & Foundations'),
    'University of Texas - Austin':                 (6.49, 2025, 'UT Austin institutional (UT System total $27.2B)'),
    'New York University':                          (7.28, 2025, ''),
    'University of Florida':                         (2.69, 2025, 'UF Foundation'),
    'Texas A&M University':                          (22.23, 2025, 'Texas A&M System & foundations (system-level)'),
    'Princeton University':                          (36.42, 2025, ''),
    'Stanford University':                           (40.79, 2025, ''),
    'Harvard University':                            (56.90, 2025, ''),
    'Massachusetts Institute of Technology (MIT)':   (27.37, 2025, ''),
    'University of Washington':                      (6.00, 2025, 'Consolidated Endowment Fund'),
    'Georgia Institute of Technology':               (3.51, 2025, 'incl. related foundations'),
    'Yale University':                               (44.15, 2025, ''),
    'Carnegie Mellon University':                    (4.29, 2025, ''),
    'Johns Hopkins University':                      (13.73, 2025, ''),
    'Oregon State University':                       (0.90, 2024, 'FY2024; FY2025 not yet reported'),
    'Rensselaer Polytechnic Institute':              (1.03, 2025, ''),
    'Clemson University':                            (1.24, 2025, ''),
    'Washington University in St. Louis':            (13.30, 2025, ''),
    'University of Vermont':                         (0.90, 2024, 'FY2024; FY2025 not yet reported'),
    'California Institute of Technology':            (4.32, 2025, ''),
    'Rice University':                               (8.50, 2025, ''),
    'Boston University':                             (4.02, 2025, ''),
    'University of Virginia':                        (11.23, 2025, 'incl. UVIMCO/foundation'),
    'Arizona State University':                      (1.76, 2025, 'ASU Foundation'),
    'Michigan State University':                     (4.61, 2025, ''),
    'Northeastern University':                       (2.10, 2025, ''),
    'University of Wyoming':                          (0.70, 2024, 'FY2024; approximate'),
    'University of Wisconsin - Madison':             (4.92, 2025, 'UW Foundation'),
    'University of Central Florida':                 (0.26, 2024, 'UCF Foundation, FY2024'),
    'Southern Methodist University':                 (2.34, 2025, ''),
    'University of Chicago':                         (10.62, 2025, ''),
    'Mississippi State University':                  (0.89, 2024, 'FY2024; approximate'),
    'University of California, Los Angeles':         (4.77, 2025, 'UCLA Foundation (UC System total $20.2B)'),
    'University of Pittsburgh':                      (6.15, 2025, ''),
    'University of Kentucky':                        (2.17, 2025, ''),
    'University of Utah':                            (2.07, 2025, ''),
    'Case Western Reserve University':               (2.52, 2025, ''),
    'New Jersey Institute of Technology':            (0.20, 2024, 'FY2024; approximate'),
    'University of Louisville':                       (1.01, 2024, 'FY2024'),
    'University of Oklahoma':                         (2.00, 2024, 'OU Norman, FY2024; approximate'),
    'University of South Carolina':                  (1.04, 2024, 'FY2024'),
    'University of Michigan - Ann Arbor':            (21.20, 2025, ''),
    'University of Alabama - Birmingham':             (2.59, 2025, 'Univ. of Alabama SYSTEM total; UAB-only is far smaller'),
    'Columbia University':                           (15.92, 2025, ''),
    'Tufts University':                              (2.71, 2025, ''),
    'University of Nebraska - Lincoln':              (2.72, 2025, 'U of Nebraska system/foundation'),
    'Duke University':                               (12.32, 2025, ''),
    'Boston College':                                (4.24, 2025, ''),
    'University of Notre Dame':                      (20.09, 2025, ''),
    'University of Southern California':             (9.03, 2025, ''),
}


PRIVATE = {
    'New York University', 'Princeton University', 'Stanford University',
    'Harvard University', 'Massachusetts Institute of Technology (MIT)',
    'Yale University', 'Carnegie Mellon University', 'Johns Hopkins University',
    'Rensselaer Polytechnic Institute', 'Washington University in St. Louis',
    'California Institute of Technology', 'Rice University', 'Boston University',
    'Northeastern University', 'Southern Methodist University',
    'University of Chicago', 'Case Western Reserve University',
    'Columbia University', 'Tufts University', 'Duke University',
    'Boston College', 'University of Notre Dame',
    'University of Southern California',
}


# Prior-year (FY2024) endowments, to compute year-over-year change. Keyed by the
# exact GPU-CSV name. Only schools where a reliable FY2024 figure exists.
ENDOWMENTS_FY24 = {
    'University of Illinois Urbana-Champaign': 2.99,
    'University of Texas - Austin': 6.08,
    'New York University': 6.65,
    'University of Florida': 2.50,
    'Texas A&M University': 20.38,
    'Princeton University': 34.05,
    'Stanford University': 37.63,
    'Harvard University': 51.98,
    'Massachusetts Institute of Technology (MIT)': 24.57,
    'University of Washington': 4.90,
    'Georgia Institute of Technology': 3.17,
    'Yale University': 41.44,
    'Carnegie Mellon University': 4.00,
    'Johns Hopkins University': 13.06,
    'Oregon State University': 0.90,
    'Rensselaer Polytechnic Institute': 0.80,
    'Clemson University': 1.12,
    'Washington University in St. Louis': 11.98,
    'California Institute of Technology': 4.14,
    'Rice University': 8.06,
    'Boston University': 3.54,
    'University of Virginia': 10.22,
    'Arizona State University': 1.59,
    'Michigan State University': 4.42,
    'Northeastern University': 1.83,
    'University of Wisconsin - Madison': 4.30,
    'Southern Methodist University': 2.12,
    'University of Chicago': 10.10,
    'University of California, Los Angeles': 4.30,
    'University of Pittsburgh': 5.80,
    'University of Kentucky': 1.98,
    'University of Utah': 1.86,
    'Case Western Reserve University': 2.40,
    'University of Michigan - Ann Arbor': 19.17,
    'Columbia University': 14.78,
    'Tufts University': 2.53,
    'University of Nebraska - Lincoln': 2.53,
    'Duke University': 11.89,
    'Boston College': 3.78,
    'University of Notre Dame': 17.90,
    'University of Southern California': 8.15,
}

# FY2024 total R&D expenditure ($M), from the NSF HERD survey. Actuals where
# directly reported; others derived from the HERD FY2024 base. Keyed by GPU-CSV
# name. RD_APPROX flags figures that are estimates (school not individually pulled).
RD_FY24 = {
    'University of Illinois Urbana-Champaign': 907,
    'University of Texas - Austin': 1144,
    'New York University': 1501,
    'University of Florida': 1273,
    'Texas A&M University': 1394,
    'Princeton University': 559,
    'Stanford University': 1642,
    'Harvard University': 1495,
    'Massachusetts Institute of Technology (MIT)': 1066,
    'University of Washington': 1691,
    'Georgia Institute of Technology': 1529,
    'Yale University': 1520,
    'Carnegie Mellon University': 505,
    'Johns Hopkins University': 4129,
    'Oregon State University': 372,
    'Rensselaer Polytechnic Institute': 100,
    'Clemson University': 290,
    'Washington University in St. Louis': 1243,
    'University of Vermont': 246,
    'California Institute of Technology': 445,
    'Rice University': 278,
    'Boston University': 784,
    'University of Virginia': 814,
    'Arizona State University': 1003,
    'Michigan State University': 932,
    'Northeastern University': 347,
    'University of Wyoming': 167,
    'University of Wisconsin - Madison': 1933,
    'University of Central Florida': 285,
    'Southern Methodist University': 63,
    'University of Chicago': 681,
    'Mississippi State University': 342,
    'University of California, Los Angeles': 1896,
    'University of Pittsburgh': 1505,
    'University of Kentucky': 528,
    'University of Utah': 789,
    'Case Western Reserve University': 643,
    'New Jersey Institute of Technology': 172,
    'University of Louisville': 225,
    'University of Oklahoma': 474,
    'University of South Carolina': 277,
    'University of Michigan - Ann Arbor': 2111,
    'University of Alabama - Birmingham': 866,
    'Columbia University': 1450,
    'Tufts University': 278,
    'University of Nebraska - Lincoln': 657,
    'Duke University': 1581,
    'Boston College': 96,
    'University of Notre Dame': 346,
    'University of Southern California': 1264,
}
RD_APPROX = {'Rensselaer Polytechnic Institute', 'Clemson University'}

# Flagship GPU deployments over time — the documented AI buildout wave. These are
# the marquee systems schools have publicly announced (counts/dates from press
# releases, HPC-center docs, and TOP500). conf: high | med. Not exhaustive — it
# tracks headline clusters, not every incremental node. Generations drive color.
MILESTONES = [
    # school, date(YYYY-MM), system, gpus, gpu_type, generation, funding, conf, note
    ('Massachusetts Institute of Technology (MIT)', '2019-08', 'TX-GAIA / SuperCloud', 896, 'V100', 'Volta', 'Federal (Lincoln Lab)', 'high', 'Fastest university system at launch'),
    ('University of Florida', '2021-01', 'HiPerGator AI', 1120, 'A100', 'Ampere', 'NVIDIA + UF ($70M partnership)', 'high', '140 DGX A100 nodes; landmark vendor donation'),
    ('University of Texas - Austin', '2022-01', 'Lonestar6 (GPU)', 84, 'A100', 'Ampere', 'State / UT', 'med', 'A100 partition added to Lonestar6'),
    ('University of Illinois Urbana-Champaign', '2022-04', 'Delta', 800, 'A100 / A40', 'Ampere', 'NSF', 'high', 'NSF-funded national resource (ACCESS)'),
    ('Harvard University', '2022-09', 'Kempner Institute (initial)', 384, 'A100', 'Ampere', 'Donation (Chan Zuckerberg-linked gift)', 'med', 'Initial Kempner AI cluster'),
    ('Princeton University', '2024-03', 'Della — PLI partition', 336, 'H100', 'Hopper', 'Internal', 'high', 'Dedicated to Princeton Language & Intelligence'),
    ('University of Texas - Austin', '2024-09', 'Vista', 600, 'GH200 / H200', 'Hopper', 'NSF', 'high', 'Grace Hopper; bridge to Horizon'),
    ('University of Illinois Urbana-Champaign', '2024-10', 'DeltaAI', 608, 'GH200 (H100)', 'Hopper', 'NSF', 'high', '114 quad Grace Hopper nodes'),
    ('Stanford University', '2024-12', 'Marlowe', 248, 'H100', 'Hopper', 'Internal / Stanford Data Science', 'high', '31 DGX H100 nodes; first GPU supercomputer'),
    ('Harvard University', '2025-06', 'Kempner (expansion)', 808, 'H200 / H100', 'Hopper', 'Internal / donation', 'high', '424 H200 + 384 H100 added'),
    ('University of Florida', '2025-06', 'HiPerGator (Blackwell upgrade)', 504, 'B200', 'Blackwell', 'UF ($24M)', 'high', '63 DGX B200 systems'),
    ('Massachusetts Institute of Technology (MIT)', '2026-02', 'ORCD Engaging (Blackwell)', 200, 'B200', 'Blackwell', 'State grant ($31M match)', 'high', '200+ B200 GPUs'),
    ('University of Texas - Austin', '2026-06', 'Horizon', 4032, 'B200 (GB200)', 'Blackwell', 'NSF (Leadership-Class Facility)', 'med', 'Planned 2026; 2,016 GB200 NVL4 nodes'),
]


# Hardware-level corrections, applied at the per-model record level (not by
# overriding summary totals) so every aggregate — physical count, generation
# breakdown, institutional/facility split — reconciles automatically. Each entry
# may provide: 'owned' (corrected operational owned-GPU model dict, replaces the
# legacy row), 'facility_models' (the NSF national-facility slice), 'cloud_models'
# (reserved cloud, NOT owned hardware), 'planned_models' (announced/under-construction,
# excluded from operational totals). Sources documented per entry.
# Audited schools are now in clusters.csv (the verified spine). This legacy-era
# override remains only for schools with a known facility split but no full cluster
# audit yet (Texas A&M / ACES). Marked as legacy-adjusted, not verified.
TIER_OVERRIDES = {
    'Texas A&M University': {
        'facility_models': {'H100_PCIe': 30, 'GH200': 1},
        'facility_systems': 'ACES — NSF-funded, ACCESS-allocated (DGX SuperPOD is institutional)',
        'source': 'gpusperstudent notes; ACES is NSF/ACCESS. Not yet independently cluster-audited.',
    },
}

# Access models that count as the university operating a national/shared facility.
FACILITY_ACCESS = {'national-allocation'}
FEDERAL_OWNERS = ('NSF', 'US (NSF)', 'federal')


def parse_clusters(path='clusters.csv'):
    """Aggregate the cluster-level inventory per university into DISTINCT count
    concepts (a verified cluster-count is NOT a verified university inventory):

      owned_primary        per-model, primary-sourced, operational, university hardware
      owned_legacy         per-model, but GPUs-Per-Student-derived (unverified estimate)
      aggregate            independently-sourced totals w/o model breakdown (w/ overlap flag)
      cloud / planned      reserved-cloud and planned/under-construction (NOT operational)
      facility_national    operational owned where access = national-allocation
      federal_funded       operational owned where funding is federal (a SEPARATE attribute)
      ownership_confirmed  true iff a primary owned record documents a specific owner
    """
    import os
    if not os.path.exists(path):
        return {}
    agg = {}
    for r in csv.DictReader(open(path)):
        uni = r['university']
        d = agg.setdefault(uni, {'owned_primary': {}, 'owned_legacy': {}, 'facility_national': {},
                                 'federal_funded': {}, 'cloud': {}, 'planned': {}, 'aggregate': [],
                                 'sources': set(), 'source_dates': set(), 'ownership_confirmed': False})
        d['sources'].add(r['source_url'])
        d['source_dates'].add(r.get('source_date', ''))
        model, cnt, status = r['gpu_model'], r['gpu_count'], r['status']
        access, owner = r['access_model'], r['owner']
        basis = r.get('count_basis', 'primary')
        overlap = r.get('overlap', '')
        # aggregate / unquantified clusters: kept separate, never summed into per-model
        if basis == 'aggregate' or model == 'mixed' or not cnt.strip():
            d['aggregate'].append({'cluster': r['cluster_name'], 'count': (int(cnt) if cnt.strip().isdigit() else None),
                                   'overlap': overlap, 'note': r['notes'], 'source': r['source_url']})
            continue
        cnt = int(cnt)
        if status == 'planned':
            d['planned'][model] = d['planned'].get(model, 0) + cnt
            continue
        if status in ('retired', 'uncertain'):
            continue  # excluded from operational
        if access == 'reserved-cloud':
            d['cloud'][model] = d['cloud'].get(model, 0) + cnt
            continue
        # operational, university-operated hardware
        bucket = 'owned_primary' if basis == 'primary' else 'owned_legacy'
        d[bucket][model] = d[bucket].get(model, 0) + cnt
        if access in FACILITY_ACCESS:                       # nationally allocated
            d['facility_national'][model] = d['facility_national'].get(model, 0) + cnt
        if any(f in r['funding_source'] for f in ('federal', 'NSF')):  # funding attribute (separate)
            d['federal_funded'][model] = d['federal_funded'].get(model, 0) + cnt
        if basis == 'primary' and owner and owner.lower() != 'unknown':
            d['ownership_confirmed'] = True
    return agg


# Primary funding model for each school's compute. Documented where a dominant
# external source is identifiable; otherwise defaults to Institutional (inferred) —
# the accurate default, as universities buy clusters with their own funds absent
# evidence of a major donation, NSF facility, or state program. (model, conf, note)
FUNDING = {
    'University of Illinois Urbana-Champaign': ('NSF facility', 'documented', 'NCSA Delta/DeltaAI are NSF-funded national resources'),
    'University of Texas - Austin': ('NSF facility', 'documented', 'TACC systems (Vista, Frontera) are NSF-funded'),
    'University of Florida': ('Vendor donation', 'documented', 'HiPerGator AI launched via a ~$70M NVIDIA partnership/gift'),
    'Texas A&M University': ('Mixed', 'documented', 'Institutional DGX SuperPOD + NSF-funded ACES'),
    'Massachusetts Institute of Technology (MIT)': ('Mixed', 'documented', 'Federal (Lincoln Lab) + institutional + $31M MA state grant'),
    'New York University': ('Mixed', 'documented', 'Institutional (Greene) + NY State Empire AI consortium ($25M + state)'),
    'Columbia University': ('Mixed', 'documented', 'Institutional + NY State Empire AI consortium'),
    'Rensselaer Polytechnic Institute': ('Mixed', 'documented', 'IBM-partnership AiMOS + NY State Empire AI consortium'),
    'Georgia Institute of Technology': ('Mixed', 'documented', 'Institutional PACE + NVIDIA AI Makerspace partnership'),
}
FUNDING_DEFAULT = ('Unknown', 'unverified', 'Funding source not verified against primary documentation')
FUNDING_MODELS = ['Institutional', 'NSF facility', 'Vendor donation', 'Mixed', 'Unknown']

# National leadership-computing allocations — the "accessible compute" spine.
# Source: full ALCF (Argonne) 2025 award list — Aurora/Polaris INCITE + ALCC +
# Early Science + Director's Discretionary. Node-hours per top-50 school (ESP/DD
# projects list as a project with 0 published hours). This is DOCUMENTED, not a
# census: OLCF/Frontier, NERSC/Perlmutter, and NSF ACCESS allocations are
# additional and NOT captured here. Node-hours are a different unit than owned
# GPUs — never mix them. (node_hours, n_projects, notable_project)
ALLOC_ALCF_2025 = {
    'Columbia University': (1850000, 1, 'OpenFold protein-interaction ML (INCITE)'),
    'Stanford University': (1800000, 2, 'Serpentine engine-inlet flow simulation (ALCC)'),
    'Georgia Institute of Technology': (1000000, 1, 'Bubble-laden turbulent flows (ALCC)'),
    'University of Southern California': (925000, 2, 'AI-guided quantum-materials simulation (INCITE)'),
    'University of Illinois Urbana-Champaign': (760000, 1, 'QMC-HAMM multiscale materials (INCITE)'),
    'University of Chicago': (400000, 2, 'Neutrino science; inner-ear mechanotransduction (INCITE)'),
    'Princeton University': (250000, 1, 'Core-collapse supernova simulations (INCITE); PPPL adds more'),
    'Duke University': (200000, 1, 'Digital twins for blood-cell analysis (INCITE)'),
    'University of Michigan - Ann Arbor': (200000, 1, 'Foundation models for crystals (INCITE)'),
    'Harvard University': (50000, 1, 'Materials for energy storage (INCITE)'),
    'Massachusetts Institute of Technology (MIT)': (0, 1, 'ML for lattice QCD (Aurora Early Science)'),
    'Carnegie Mellon University': (0, 1, 'Many-body perturbation theory + ML (Aurora Early Science)'),
    'Rensselaer Polytechnic Institute': (0, 1, '2D magnetic-materials informatics (Director\'s Discretionary)'),
}

# TIER 3 — federal national labs in the university orbit. These are DOE facilities
# a university *manages or operates* (not institutionally owns), running largely
# non-NVIDIA accelerators. Shown as CONTEXT ONLY — never summed into the top-50
# metrics, which count institutional/NSF compute. Attribution is the management
# contract. Counts are native GPU/accelerator units (not H100-equivalents).
NATIONAL_LABS = [
    # lab, managing university / consortium, flagship system, gpus, approx?, accelerator, top500, note, highlight
    ('Lawrence Berkeley (NERSC)', 'University of California', 'Perlmutter', 6144, False, 'NVIDIA A100', '#19',
     'DOE open-science facility; UC is the prime contractor for LBNL', True),
    ('Oak Ridge (OLCF)', 'University of Tennessee (UT-Battelle)', 'Frontier', 37888, False, 'AMD MI250X', '#2',
     'First US exascale system; DOE Office of Science', False),
    ('Argonne (ALCF)', 'University of Chicago (UChicago Argonne)', 'Aurora', 63744, False, 'Intel Data Center Max', '#3',
     'Exascale; UChicago also runs Polaris (2,240 A100) and Fermilab', False),
    ('Lawrence Livermore (LLNL)', 'Univ. of California (LLNS partner)', 'El Capitan', 44000, True, 'AMD MI300A', '#1',
     'NNSA; Bechtel-led consortium in which UC is a partner', False),
    ('Los Alamos (LANL)', 'UC + Texas A&M (Triad)', 'Venado', 2560, True, 'NVIDIA GH200', '—',
     'NNSA weapons lab; managed by a UC/Texas A&M/Battelle consortium', False),
    ('SLAC', 'Stanford University', 'S3DF / shared', None, False, 'NVIDIA (mixed)', '—',
     'DOE lab operated by Stanford; modest, growing GPU footprint', False),
    ('Princeton Plasma Physics (PPPL)', 'Princeton University', '—', None, False, '—', '—',
     'DOE fusion lab operated by Princeton; limited GPU compute', False),
    ('Brookhaven (BNL)', 'Stony Brook University (BSA)', '—', None, False, 'NVIDIA (mixed)', '—',
     'DOE lab co-managed by Stony Brook; GPU for sPHENIX / data science', False),
    ('Ames National Laboratory', 'Iowa State University', '—', None, False, '—', '—',
     'DOE materials lab operated by Iowa State; limited GPU compute', False),
]


# GPU microarchitecture generation, by NVIDIA's actual lineage. Used to show fleet
# composition/vintage. (P100=Pascal, V100=Volta, A100/A40/A10/A6000=Ampere,
# L40S=Ada Lovelace, H100/H200/GH200=Hopper, B200/B100=Blackwell, Rubin=Rubin.)
GEN_OF = {
    'P100': 'Pascal', 'V100': 'Volta', 'RTX8000': 'Turing',
    'A100_80GB': 'Ampere', 'A100_40GB': 'Ampere', 'A100': 'Ampere', 'A40': 'Ampere',
    'A10': 'Ampere', 'RTX_A6000': 'Ampere',
    'L40S': 'Ada', 'L4': 'Ada',
    'H100_SXM': 'Hopper', 'H100_PCIe': 'Hopper', 'H100': 'Hopper', 'H200': 'Hopper', 'GH200': 'Hopper',
    'B200': 'Blackwell', 'B100': 'Blackwell', 'RTX_PRO_6000': 'Blackwell', 'Rubin': 'Rubin',
}
# Price-based weights (NOT performance): approximate share of the value-derived
# "H100 price-equivalent", used only to apportion that metric across generations.
GEN_W = {'P100': 0.05, 'V100': 0.12, 'RTX8000': 0.1, 'A100_80GB': 0.6, 'A100_40GB': 0.5,
         'A100': 0.55, 'A40': 0.2, 'A10': 0.15, 'RTX_A6000': 0.25, 'L40S': 0.4, 'L4': 0.15,
         'H100_SXM': 1.0, 'H100_PCIe': 0.9, 'H100': 1.0, 'H200': 1.1, 'GH200': 1.0,
         'B200': 2.2, 'B100': 1.8, 'RTX_PRO_6000': 0.8, 'Rubin': 3.0}
GENS_ORDER = ['Pascal', 'Volta', 'Turing', 'Ampere', 'Ada', 'Hopper', 'Blackwell', 'Rubin']


def gen_split(gpus, total_h100e):
    """Apportion total H100-equivalent across generations (effective compute)."""
    raw = {g: 0.0 for g in GENS_ORDER}
    for model, n in gpus.items():
        raw[GEN_OF[model]] += n * GEN_W.get(model, 0.3)
    s = sum(raw.values())
    if s <= 0:
        return {g: 0 for g in GENS_ORDER}
    scale = total_h100e / s
    return {g: round(raw[g] * scale, 1) for g in GENS_ORDER}


def gen_count(gpus):
    """Raw GPU counts by generation (shows fleet age/modernity directly)."""
    c = {g: 0 for g in GENS_ORDER}
    for model, n in gpus.items():
        c[GEN_OF[model]] += n
    return c


def num(r, k):
    try:
        return float(r[k] or 0)
    except ValueError:
        return 0


def main():
    alloc_data = json.load(open('alloc.json')) if os.path.exists('alloc.json') else {}
    clusters = parse_clusters()
    rows = list(csv.DictReader(open('raw_gpus.csv')))
    rows.sort(key=lambda r: num(r, 'h100_equivalent'), reverse=True)
    top = rows[:50]

    out = []
    for r in top:
        name = r['university']
        legacy_gpus = {m: int(num(r, m)) for m in GPU_MODELS if num(r, m) > 0}

        # SPINE: cluster records first (distinct count concepts); TIER_OVERRIDES; legacy.
        cl = clusters.get(name)
        ov = TIER_OVERRIDES.get(name, {})
        aggregate_clusters, sources, source_dates = [], [], []
        owned_primary, owned_legacy = {}, {}
        facility_models, federal_models, cloud_models, planned_models = {}, {}, {}, {}
        ownership_verification = 'unresolved'
        if cl:
            owned_primary = dict(cl['owned_primary'])
            owned_legacy = dict(cl['owned_legacy'])
            facility_models = cl['facility_national']
            federal_models = cl['federal_funded']
            cloud_models = cl['cloud']
            planned_models = cl['planned']
            aggregate_clusters = cl['aggregate']
            sources = sorted(u for u in cl['sources'] if u)
            source_dates = sorted(x for x in cl['source_dates'] if x)
            ownership_verification = 'confirmed' if cl['ownership_confirmed'] else 'unresolved'
        elif ov:
            owned_legacy = dict(ov.get('owned', legacy_gpus))
            facility_models = ov.get('facility_models', {})
            cloud_models = ov.get('cloud_models', {})
            planned_models = ov.get('planned_models', {})
            sources = [ov.get('source', '')]
        else:
            owned_legacy = dict(legacy_gpus)

        def h100e_of(g):  # transparent price-equivalent: sum(count * price-weight)
            return round(sum(g.get(m, 0) * GEN_W.get(m, 0.3) for m in g), 1)

        per_model = {}                                     # verified + legacy per-model (reconciles w/ gen breakdown)
        for src in (owned_primary, owned_legacy):
            for m, n in src.items():
                per_model[m] = per_model.get(m, 0) + n

        # distinct count concepts (a verified cluster-count is NOT a university total)
        verified_model_count = sum(owned_primary.values())
        legacy_estimate = sum(owned_legacy.values())
        aggregate_count = sum(a['count'] for a in aggregate_clusters if a['count'])
        distinct_agg = sum(a['count'] for a in aggregate_clusters if a['count'] and a['overlap'] == 'distinct')
        documented_lower_bound = verified_model_count + distinct_agg   # non-overlap aggregates only

        total_gpus = sum(per_model.values())
        gpus = per_model
        h100e = h100e_of(per_model)
        gpu_value = round(h100e * 35000)
        facility_gpus = sum(facility_models.values())
        facility_h100e = h100e_of(facility_models)
        federal_funded_gpus = sum(federal_models.values())
        inst_gpus = total_gpus - facility_gpus
        inst_h100e = round(h100e - facility_h100e, 1)
        cloud_gpus = sum(cloud_models.values())
        planned_gpus = sum(planned_models.values())

        if cl:
            verification = 'verified' if (verified_model_count and not owned_legacy and not aggregate_clusters) else 'partial'
            completeness = 'partial'                        # no pilot school is asserted complete
        elif ov:
            verification, completeness = 'legacy-adjusted', 'unknown'
        else:
            verification, completeness = 'legacy', 'unknown'
        # headline display: lower bound for audited schools, legacy estimate for the rest
        display_gpus = documented_lower_bound if verification in ('verified', 'partial') else total_gpus
        display_is_lower_bound = verification in ('verified', 'partial') and completeness != 'complete'
        endow, fy, enote = ENDOWMENTS.get(name, (None, None, 'endowment not found'))
        endow_prior = ENDOWMENTS_FY24.get(name)
        # YoY change only meaningful when current figure is FY2025 (same basis)
        yoy = None
        if endow and endow_prior and fy == 2025:
            yoy = round(100 * (endow - endow_prior) / endow_prior, 1)

        rec = {
            'name': name,
            'url': r['url'],
            'sector': 'Private' if name in PRIVATE else 'Public',
            'funding_model': FUNDING.get(name, FUNDING_DEFAULT)[0],
            'funding_conf': FUNDING.get(name, FUNDING_DEFAULT)[1],
            'funding_note': FUNDING.get(name, FUNDING_DEFAULT)[2],
            'alloc_nodehours': alloc_data.get(name, {}).get('total_nh', 0),
            'alloc_incite_nh': alloc_data.get(name, {}).get('incite_nh', 0),
            'alloc_alcc_nh': alloc_data.get(name, {}).get('alcc_nh', 0),
            'alloc_notable': alloc_data.get(name, {}).get('notable', ''),
            'nairr_projects': alloc_data.get(name, {}).get('nairr_projects', 0),
            'has_alloc': alloc_data.get(name, {}).get('total_nh', 0) > 0,
            'has_access': name in alloc_data,
            'gpus': gpus,
            'total_gpus': total_gpus,
            'verified_model_count': verified_model_count,
            'legacy_estimate': legacy_estimate,
            'aggregate_count': aggregate_count,
            'documented_lower_bound': documented_lower_bound,
            'display_gpus': display_gpus,
            'display_is_lower_bound': display_is_lower_bound,
            'inventory_completeness': completeness,
            'ownership_verification': ownership_verification,
            'federal_funded_gpus': federal_funded_gpus,
            'source_dates': source_dates,
            'h100_equivalent': round(h100e, 1),
            'institutional_gpus': inst_gpus,
            'institutional_h100e': inst_h100e,
            'facility_gpus': facility_gpus,
            'facility_h100e': facility_h100e,
            'facility_systems': ov.get('facility_systems', '') or ('NSF / national facility (see cluster records)' if (cl and facility_gpus > 0) else ''),
            'has_facility': facility_h100e > 0,
            'cloud_gpus': cloud_gpus,
            'cloud_models': cloud_models,
            'planned_gpus': planned_gpus,
            'planned_models': planned_models,
            'verification': verification,
            'sources': sources,
            'aggregate_clusters': aggregate_clusters,
            'correction_source': ov.get('source', ''),
            'gen_h100e': gen_split(gpus, h100e),
            'gen_count': gen_count(gpus),
            'gpu_value_usd': int(gpu_value),
            'endowment_b': endow,
            'endowment_fy': fy,
            'endowment_b_prior': endow_prior,
            'endowment_yoy_pct': yoy,
            'endowment_note': enote,
            'rd_expenditure_b': round(RD_FY24[name] / 1000, 3) if name in RD_FY24 else None,
            'rd_approx': name in RD_APPROX,
            # derived economics
            'h100e_per_b_endowment': round(h100e / endow, 1) if endow else None,
            'h100e_per_b_rd': round(h100e / (RD_FY24[name] / 1000), 1) if name in RD_FY24 else None,
            'gpu_value_pct_of_endowment': round(100 * gpu_value / (endow * 1e9), 3) if endow else None,
            'students': int(num(r, 'weighted_students')),
            'gpus_per_student': round(num(r, 'gpus_per_student'), 3),
            'notes': r['Notes'],
            'num_sources': int(num(r, 'sources')),
        }
        out.append(rec)

    meta = {
        'title': 'The State of US University AI Compute',
        'sampling_method': 'Top 50 by documented GPU inventory in the GPUs Per Student dataset (NOT an NSF-R&D-defined "top 50 research universities"). Migration to an R&D-defined universe + source-verified inventory is in progress.',
        'gpu_data_asof': 'Legacy inventory: late 2025 / early 2026 (gpusperstudent.org + TOP500 Nov 2025). Audited records (Illinois, UT Austin, Harvard, CMU, Oregon State + pilot) verified against primary sources, Oct 2026.',
        'metric_note': 'H100 price-equivalent = estimated GPU market value / $35,000 (a PRICE proxy, NOT performance). Physical GPU count is the primary unit. No performance normalization is claimed.',
        'endowment_data_asof': 'FY2025 (year ending ~June 30 2025) where reported; FY2024 for a few smaller schools',
        'built': '2026-10-11',
        'n_schools': len(out),
        'gpu_source': 'LEGACY candidate source: gpusperstudent.org (master_data.csv). Being replaced by independently source-verified cluster records (clusters.csv); see PILOT_AUDIT.md.',
        'endowment_source': '2025 NACUBO-Commonfund Study; statranker/altss FY2025 compilations; university treasury reports',
        'rd_source': 'NSF HERD survey, FY2024 (total R&D expenditures; year ending ~June 30 2024)',
        'rd_data_asof': 'FY2024 (NSF HERD, released Nov 2025)',
        'alloc_source': 'DOE INCITE 2025 + ALCC 2025 — both complete across all facilities (Frontier/Aurora/Polaris/Perlmutter), parsed from the official ASCR/INCITE fact-sheet PDFs; NAIRR pilot project counts (nairrpilot.org awards CSV, 1,212 awards)',
        'alloc_caveat': 'Leadership node-hours = INCITE 2025 + ALCC 2025, both complete across all leadership facilities. NSF ACCESS and routine NERSC/ERCAP allocations are not quantified (no clean per-institution public totals). NAIRR is a project count (AI-specific national access), a distinct signal. Node-hours/project-counts are not comparable to owned-GPU counts.',
        'caveats': [
            'SAMPLE: these 50 are the schools with the most documented GPU inventory in the legacy source — NOT an NSF-R&D-defined "top 50 research universities." Selection-bias fix in progress.',
            'DATA PROVENANCE: most rows are still legacy (GPUs Per Student) candidate data, not independently verified. Audited schools (Illinois, UT Austin, Harvard, CMU, Oregon State + pilot) are corrected against primary sources; see clusters.csv and PILOT_AUDIT.md. Missing inventory ≠ zero GPUs.',
            'H100 PRICE-EQUIVALENT = estimated GPU value / $35,000. It is a PRICE proxy, NOT a performance measure, and NOT actual institutional spending. Physical GPU count is the primary unit.',
            'PLANNED and RESERVED-CLOUD capacity are excluded from operational owned totals and tracked separately (e.g., Oregon State 150 Rubin = under construction to 2027; CMU 296 H100 = Google Cloud reserved, not owned).',
            'FUNDING source defaults to "Unknown / not verified" unless documented against a primary source. Unknown is NOT counted as institutional.',
            'Ownership tiers: institutional vs NSF national facility (TACC/Illinois NCSA/TAMU ACES) are distinct. National labs a university merely operates/neighbors (NERSC, Frontier, Aurora...) are a separate context layer, never summed in.',
            'Grace Hopper double-counting (listed under both H100 and GH200) corrected at the per-model level for Illinois and UT Austin; all aggregates reconcile to non-overlapping hardware counts.',
            'National access = DOE INCITE 2025 + ALCC 2025 (complete, all leadership facilities) + NAIRR project counts. NSF ACCESS and routine NERSC/ERCAP not quantified; absence ≠ no access. Node-hours/project-counts are distinct units from GPU counts.',
            'Public-university endowments are often reported at SYSTEM level (Texas A&M, U of Alabama), inflating per-campus figures; flagged in the endowment note.',
        ],
    }

    gens = ['Volta', 'Ampere', 'Hopper', 'Blackwell']
    milestones = [{
        'name': m[0], 'date': m[1], 'system': m[2], 'gpus': m[3],
        'gpu_type': m[4], 'generation': m[5], 'funding': m[6],
        'conf': m[7], 'note': m[8],
    } for m in sorted(MILESTONES, key=lambda x: x[1])]

    national_labs = [{
        'lab': n[0], 'manager': n[1], 'system': n[2], 'gpus': n[3], 'gpus_approx': n[4],
        'accelerator': n[5], 'top500': n[6], 'note': n[7], 'highlight': n[8],
    } for n in NATIONAL_LABS]

    herd50 = []
    if os.path.exists('herd50.csv'):
        for h in csv.DictReader(open('herd50.csv')):
            h['rank'] = int(h['rank'])
            h['rd_fy2024_m'] = float(h['rd_fy2024_m'] or 0)
            h['endowment_b'] = float(h['endowment_b']) if h['endowment_b'] else None
            h['documented_gpus'] = int(h['documented_gpus'] or 0)
            herd50.append(h)

    # headline metrics, recomputed from herd50 (reproducible, not hardcoded)
    def _corr(xs, ys):
        n = len(xs)
        if n < 3:
            return None
        mx, my = sum(xs) / n, sum(ys) / n
        cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        sx = sum((x - mx) ** 2 for x in xs) ** 0.5
        sy = sum((y - my) ** 2 for y in ys) ** 0.5
        return round(cov / (sx * sy), 2) if sx and sy else None

    doc = [h for h in herd50 if h['documented_gpus'] > 0]
    rd_pairs = [(h['rd_fy2024_m'], h['documented_gpus']) for h in doc if h['rd_fy2024_m']]
    en_pairs = [(h['endowment_b'], h['documented_gpus']) for h in doc if h['endowment_b']]
    tot_doc = sum(h['documented_gpus'] for h in herd50)
    top10 = sum(sorted((h['documented_gpus'] for h in herd50), reverse=True)[:10])
    rd_sorted = sorted((h['rd_fy2024_m'] for h in herd50), reverse=True)
    headline = {
        'corr_rd_gpu': _corr([p[0] for p in rd_pairs], [p[1] for p in rd_pairs]),
        'corr_rd_n': len(rd_pairs),
        'corr_endow_gpu': _corr([p[0] for p in en_pairs], [p[1] for p in en_pairs]),
        'corr_endow_n': len(en_pairs),
        'top10_gpu_share': round(100 * top10 / tot_doc) if tot_doc else None,
        'top10_rd_share': round(100 * sum(rd_sorted[:10]) / sum(rd_sorted)) if rd_sorted else None,
        'n_documented': len(doc), 'n_total': len(herd50), 'total_documented_gpus': tot_doc,
    }

    research_subset = []
    if os.path.exists('research_subset.csv'):
        for rr in csv.DictReader(open('research_subset.csv')):
            rr['rd_rank'] = int(rr['rd_rank'])
            rr['documented_gpus'] = int(rr['documented_gpus'] or 0)
            research_subset.append(rr)

    payload = {'meta': meta, 'schools': out, 'milestones': milestones,
               'generations': gens, 'national_labs': national_labs,
               'funding_models': FUNDING_MODELS, 'gens_order': GENS_ORDER,
               'research_subset': research_subset, 'herd50': herd50, 'headline': headline}
    json.dump(payload, open('data.json', 'w'), indent=2)

    # archive a dated snapshot so the per-school series accumulates over rebuilds.
    # Each snapshot is the compute state at build time; re-running later adds points.
    os.makedirs('snapshots', exist_ok=True)
    snap_date = meta['built'][:7]  # YYYY-MM
    snap = {'date': meta['built'], 'schools': [
        {'name': r['name'], 'total_gpus': r['total_gpus'],
         'h100_equivalent': r['h100_equivalent'], 'gpu_value_usd': r['gpu_value_usd'],
         'endowment_b': r['endowment_b']} for r in out]}
    json.dump(snap, open(f'snapshots/{snap_date}.json', 'w'), indent=2)

    # inject into the standalone HTML template -> self-contained index.html
    tpl = open('template.html').read()
    html = tpl.replace('__DATA_JSON__', json.dumps(payload))
    open('index.html', 'w').write(html)
    print(f'Wrote data.json + index.html + snapshots/{snap_date}.json with {len(out)} schools')
    print(f'Milestones: {len(milestones)}')
    missing = [r['name'] for r in out if r['endowment_b'] is None]
    if missing:
        print('MISSING ENDOWMENTS:', missing)
    # quick sanity print
    print(f'\n{"school":42} {"H100e":>7} {"endow$B":>8} {"H100e/$B":>9}')
    for r in out[:15]:
        print(f'{r["name"][:42]:42} {r["h100_equivalent"]:>7.0f} {str(r["endowment_b"]):>8} {str(r["h100e_per_b_endowment"]):>9}')


if __name__ == '__main__':
    main()

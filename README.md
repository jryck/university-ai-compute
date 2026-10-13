# The State of US University AI Compute

**▶ Live dashboard: https://jryck.github.io/university-ai-compute/**

An interactive dashboard on AI compute across US research universities — who owns it,
who can access it, and how it maps to institutional wealth and research spending.

## Expanded dataset & findings (top 50 by R&D)

- **[`herd50.csv`](herd50.csv)** — the full **50 highest-R&D US universities** (NSF HERD FY2024),
  with documented GPU capacity (lower bounds), control model, endowment, sector, and primary
  source. Coverage: **41/50 documented, 9 unresolved** (condo clusters / medical centers).
- **[`RESEARCH_FINDINGS.md`](RESEARCH_FINDINGS.md)** — five observations on the 50-school set.
  Headline: **research spending barely predicts documented GPU capacity** (r ≈ −0.05 with R&D,
  0.19 with endowment), and **GPU capacity is ~2× more concentrated than R&D** (top-10 hold 62%
  of documented GPUs vs 31% of R&D). ~24% of documented academic GPUs are federal/state shared
  facilities, not institutional.
- Dashboard themes: **capacity** (generation bar + ranking), **financial** ("Compute vs.
  financial resources (HERD top-50)" scatter), **ownership/access** ("who can actually get the
  compute?" allocation-regime chart).

## Research output (methodology artifacts)

- **[`DATA_INSIGHT_DRAFT.md`](DATA_INSIGHT_DRAFT.md)** — *"At most leading US research
  universities, the AI compute isn't the university's."* Of the 20 highest-R&D US
  universities (NSF HERD FY2024), only **5** run a large dedicated institution-controlled
  GPU cluster; the rest rely on **condo** (PI-owned) hardware or **NSF/state shared
  facilities**. Based on primary-source classification; counts are documented lower bounds.
- **[`herd_universe.csv`](herd_universe.csv)** — the independent sample (top 50 by R&D,
  unbiased vs. GPU holdings). **[`research_subset.csv`](research_subset.csv)** — the top-20
  control-model classification with sources.
- The **"Research: who controls the compute?"** section on the dashboard is the chart.

## Data quality & methodology

An **independently source-verified, auditable** dataset (10-university pilot done; 38
schools still legacy). Key documents:

- **[`PILOT_AUDIT.md`](PILOT_AUDIT.md)** — primary-source audit of 10 universities with a
  reconciliation table. Calibrated finding: the legacy source has **substantial, non-uniform
  errors** (duplicate accelerators, cloud-as-owned, planned/decommissioned-as-live,
  MIG-as-physical, wrong generation records) — but **not** a uniform overstatement (Harvard
  was *under*-counted), and for several schools public docs can't establish a total.
- **[`RESEARCH_FINDINGS.md`](RESEARCH_FINDINGS.md)** — what the corrected evidence supports:
  established vs. suggestive vs. retracted vs. unanswered.
- **[`clusters.csv`](clusters.csv)** — the **cluster-level** inventory: one row per deployment
  with `count_basis` (primary / legacy / aggregate), `overlap`, status, owner, funding,
  access model, source URL + date, confidence.
- **[`validate.py`](validate.py)** — substantive checks that **independently re-aggregate
  `clusters.csv` and assert `data.json` matches** (so perturbing either file fails a check),
  plus pilot regressions. `python3 validate.py`.

### Count concepts (a verified cluster-count is NOT a university total)

Per school the dataset tracks these **distinct** quantities — never collapsed into one total:

| Field | Meaning |
|---|---|
| `verified_model_count` | per-model GPUs from primary sources |
| `aggregate_count` | independently-sourced totals w/o model breakdown (w/ overlap flag) |
| `legacy_estimate` | GPUs-Per-Student-derived, kept separate as *unverified* |
| `documented_lower_bound` | verified + **non-overlapping** aggregates (the headline "≥" figure) |
| `cloud_gpus` / `planned_gpus` | reserved cloud / under-construction — **excluded** from operational |
| `facility_gpus` (national-allocation) vs `federal_funded_gpus` | **separate** attributes |
| `inventory_completeness` / `ownership_verification` | coverage and ownership flags, independent of count verification |

**Known limitations (plainly):**
- **Sample:** the 50 are those with the most documented GPU inventory in the legacy source —
  **not** an NSF-R&D-defined "top 50." Fix pending.
- **Metric:** "H100 price-equivalent" = estimated GPU value ÷ $35,000 — a **price proxy, not
  performance**, and not actual spending. Physical GPU count is primary.
- **Provenance:** 38 of 50 rows are still unverified legacy. Audited figures are **lower bounds**.
  Missing inventory ≠ zero. Funding defaults to **Unknown**, never silently institutional.

Build: `python3 alloc_build.py && python3 build_data.py && python3 validate.py`.

## What it shows

- **GPU inventories** per school: total GPUs, breakdown by model (H100, H200,
  A100, V100, B200, L40S, …), and an **H100-equivalent** compute figure that
  normalizes different GPU generations onto one scale.
- **Endowments** (most recent fiscal year) joined to each school.
- **Derived economics**: H100-equivalents per $B of endowment (who is
  compute-rich vs compute-poor relative to their wealth), **H100-equivalents per
  $B of R&D spending** (compute *intensity* of research — NSF HERD FY2024),
  estimated GPU dollar value, and GPUs per student.
- The compute-vs-X scatter has a **toggle** between *Endowment* and *R&D spending*
  on the x-axis — the two lenses rank schools very differently.
- A **log-log scatter** (compute vs endowment, colored by public/private) and a
  **sortable, filterable table** with expandable per-school GPU breakdowns.
- A **stacked bar** of owned compute per school, segmented by GPU generation
  (Volta→Blackwell), with a toggle between effective compute (H100e) and raw GPU count
  — shows fleet ranking *and* vintage (e.g., Florida skipped Hopper; NYU/RPI carry legacy V100s).
- A **buildout timeline (2019–2026)** of flagship GPU deployments, as swimlanes by
  school, colored by GPU generation (Volta→Ampere→Hopper→Blackwell) and sized by
  GPUs added — the "velocity" view of the AI compute wave and who funds it.
- **Endowment year-over-year** (FY2024→FY2025) shown inline in the table.

## Time dimension & snapshots

Every rebuild archives the current compute state to `snapshots/YYYY-MM.json`. Re-run
periodically and the per-school series accumulates over time — that's how the full
50-school GPU trajectory gets built going forward (the flagship timeline is the
hand-curated historical backbone until enough snapshots exist).

## Ownership tiers (institutional vs. NSF national facility)

Compute is split into two tiers, toggleable on the scatter and reflected in the table:

- **Institutional** — bought with university/donor funds for the university's own
  use (e.g., Harvard Cannon, Stanford Marlowe, UF HiPerGator).
- **NSF national facility** — federally funded, nationally allocated compute the
  university *operates* but doesn't own in the institutional sense: NCSA (Illinois),
  TACC (UT Austin), ACES (Texas A&M). Flagged with an "NSF facility" badge.

The **"Institutional only"** view excludes the facility tier — which is the honest
measure of a school's *own* commitment to compute. It collapses Illinois (from
~880 to ~25 H100e) and UT Austin, revealing their dominance is federal
infrastructure, not institutional investment.

National labs a university merely manages or operates are a **separate category**
(see Tier 3 below) and are **not counted** in any of the metrics above.

## Tier 3: national labs in the university orbit (context panel)

A standalone section lists the federal (mostly DOE) facilities universities manage
or operate — Perlmutter/NERSC (UC/Berkeley), Frontier/Oak Ridge (Tennessee),
Aurora/Argonne (UChicago), El Capitan/Livermore (UC), Venado/Los Alamos (UC +
Texas A&M), SLAC (Stanford), PPPL (Princeton), Brookhaven (Stony Brook), Ames
(Iowa State). This is where Berkeley's real compute lives (via NERSC). It is shown
as **context only**, in native accelerator counts (largely non-NVIDIA — AMD/Intel),
**never summed** into the institutional/NSF metrics. Attribution is the management
contract; these are federal facilities, not university-owned.

Note: the source dataset double-counts Grace Hopper systems (under both H100 and
GH200); this was corrected for Illinois and UT Austin, lowering their totals vs.
the raw source.

## Funding model

Each school is tagged with its **primary funding model** — color the scatter by it
("Color: Funding") and sort/read it in the table:

- **NSF facility** — NSF-funded national resource dominates (Illinois, UT Austin).
- **Vendor donation** — a major vendor gift established the flagship (Florida / NVIDIA).
- **Mixed** — multiple major sources (Texas A&M, MIT, Georgia Tech, and the NY
  Empire-AI consortium schools: NYU, Columbia, RPI).
- **Institutional** — the university's own funds/endowment. The default, and
  marked `(inferred)` where no dominant external source was identified — which
  applies to 41 of 50 schools. That most schools fund compute themselves, with
  donations/NSF as rare exceptions, is itself the finding.

## National allocations & accessible compute

**Two national-access signals** — leadership node-hours and NAIRR project count — are
columns in the main table (merged there in the consolidation), covering **47 of 50**
schools:

- **Leadership node-hours** — DOE **INCITE 2025 + ALCC 2025**, both **complete across
  all leadership facilities** (Frontier/Aurora/Polaris/Perlmutter), parsed from the
  official ASCR/INCITE fact-sheet PDFs. Elite HPC.
- **NAIRR projects** — count of NAIRR-pilot AI allocations per school (from the
  nairrpilot.org awards CSV, 1,212 awards). Broad AI-research access.

The point is **access ≠ ownership**, and the two signals are different games: USC,
Michigan, Notre Dame command ~1–1.5M node-hours while owning ~30–40 H100-equivalents;
UCLA, UW, CMU rack up *NAIRR* projects with small fleets; GPU-rich NYU/Florida/Texas A&M
win almost none of either; Stanford, Princeton, UIUC do both.

Built by `alloc_build.py` — parses `pdfs/incite2025.pdf` (retrieved via the Wayback
Machine; the live URL is behind an anti-bot block) + `pdfs/alcc2025.pdf` + the NAIRR
awards CSV, maps to canonical names → `alloc.json` → read by `build_data.py`.
**Remaining gap:** NSF ACCESS and routine NERSC/ERCAP allocations aren't quantified
(no clean per-institution public totals). Node-hours and project counts are distinct
units, never mixed with owned-GPU counts.

## Owned vs. rented compute

This tracks **owned** hardware only. Universities publish detailed cluster specs,
but **rented/cloud GPU usage is not publicly disclosed** — schools provide cloud
access (AWS/Azure/GCP accounts, neocloud deals) without reporting consumption or
spend. A credible rented-GPU count per school is not obtainable from public data.
Future proxy signals worth mining: disclosed cloud partnerships, NSF cloud-credit
allocations (ACCESS/CloudBank), and compute-acknowledgments in the schools' arXiv
papers.

## Files

| File | Purpose |
|------|---------|
| `index.html`   | **The dashboard.** Self-contained — open directly in a browser. |
| `data.json`    | The clean merged dataset (GPU inventory + endowments + derived metrics). |
| `build_data.py`| Build script: joins `raw_gpus.csv` with endowment figures, computes metrics, and injects the data into `template.html` → `index.html`. |
| `template.html`| HTML/CSS/JS template with a `__DATA_JSON__` placeholder. |
| `raw_gpus.csv` | Source GPU inventory (from gpusperstudent.org). |
| `snapshots/`   | Dated archives of the compute state, one per rebuild — the growing time-series. |

## Rebuild

```bash
python3 build_data.py      # regenerates data.json and index.html
open index.html
```

To update endowments or add schools, edit the `ENDOWMENTS` dict (and `PRIVATE`
set) in `build_data.py` and rebuild.

## Data sources & currency

- **GPU inventory:** gpusperstudent.org `master_data.csv`, cross-referenced with
  the TOP500 (Nov 2025) list and university HPC documentation. Reflects late-2025
  / early-2026 state.
- **Endowments:** 2025 NACUBO-Commonfund Study and FY2025 compilations
  (year ending ~June 30, 2025) where reported; FY2024 for a few smaller schools
  that haven't reported FY2025 yet (flagged "FY24" in the table).

## Caveats

- GPU counts for research clusters are inherently approximate; private/
  departmental clusters are often undercounted, and vendor-donated systems vary
  in how much they disclose.
- H100-equivalent is an **estimate** of relative compute, not a benchmark.
- Public-university endowments are often reported at **system level** (e.g.,
  Texas A&M System, University of Alabama System), which inflates the per-campus
  figure. These are flagged in each school's endowment note.
- GPU dollar values are rough list-price estimates, not purchase prices (which
  are often discounted or donated).

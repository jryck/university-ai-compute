# University AI Compute

**▶ Live dashboard: https://jryck.github.io/university-ai-compute/**

Mapping the computing infrastructure of America's leading research universities — and
how it relates to institutional wealth, research spending, and access.

## One authoritative data pipeline

Every ranking, financial comparison, summary figure, table, and the hardware-generation
chart draws on a **single source of truth**:

- **[`herd50.csv`](herd50.csv)** — the **50 highest-R&D US universities** (NSF HERD FY2024),
  defined independently of GPU holdings. Per school: documented GPU capacity (a **lower
  bound**), count type, control model, endowment, sector, key systems, and a primary source.
  Coverage: **41/50 documented, 9 unresolved** (condo clusters / medical centers that publish
  no count — never set to zero).
- **[`clusters.csv`](clusters.csv)** — the **cluster-level** inventory: one row per deployment
  with `gpu_model`, `count_basis` (primary / legacy / aggregate), `overlap`, status, owner,
  funding, access model, source URL + date, confidence. This is the only source of **model-level
  (generation) evidence**.

A given university reports the **same documented total everywhere** — e.g. MIT ≥1,448,
NYU ≥1,276, Harvard ≥1,144, Illinois ≥1,650, Cornell ≥755. `validate.py` enforces this.

The legacy **GPUs-Per-Student-derived** estimates (`raw_gpus.csv` → `data.json` `"schools"`)
are retained **only** for historical comparison and data discovery. They are **never combined**
with the authoritative counts and drive no headline figure, ranking, or chart.

## The dashboard (six sections)

1. **Key findings** — three relationships recomputed live from the data: R&D vs. documented
   GPUs (Pearson r ≈ −0.04, n=41), endowment vs. documented GPUs (r ≈ +0.19, n=38), and
   concentration (top-10 fleets hold **62%** of documented GPUs vs 31% of R&D).
2. **Compute vs. university resources** — the principal log–log scatter of documented GPUs
   against R&D spending / endowment, with an *exclude NSF/state facilities* toggle and optional,
   clearly-marked **reference points** for endowment-heavy schools outside the HERD-50
   (Princeton, Rice; see [`reference_points.csv`](reference_points.csv)) that are **excluded from
   all correlations and aggregates**.
3. **Distribution & concentration** — documented-GPU ranking, plus **documented GPU capacity by
   generation**. Generations are assigned **only where model-level cluster evidence exists**
   (8 of the 41 documented schools); the rest is aggregate-only and shown as **"Generation
   unknown,"** never omitted and never given an invented breakdown. The chart **reconciles to the
   same documented totals** used elsewhere.
4. **Who pays for & controls academic compute** — allocation-regime classification (top-20 by
   R&D): central-allocatable vs faculty/stakeholder-priority vs national/state facility.
5. **Explore the full dataset** — the searchable HERD-50 table (click a row for systems +
   source), buildout timeline, and a national-labs context panel (not counted in any metric).
6. **Methodology, sources & limitations** — the pipeline, the generation-evidence rule, the
   data-quality audit, and caveats.

## Headline metric

Physical **GPU count** (documented lower bound) is the primary unit. The generation chart's
optional "H100 price-equivalent" view = estimated GPU value ÷ $35,000 — a **price proxy, NOT a
performance measure**, shown **only** for GPUs whose generation is documented.

## Data quality & methodology

- **[`PILOT_AUDIT.md`](PILOT_AUDIT.md)** — primary-source audit of a 10-university pilot with a
  reconciliation table. Calibrated finding: legacy third-party estimates carry **substantial,
  non-uniform errors** (duplicate accelerators, cloud-as-owned, planned/decommissioned-as-live,
  MIG-as-physical) — but **not** a uniform overstatement (Harvard was *under*-counted).
- **[`RESEARCH_FINDINGS.md`](RESEARCH_FINDINGS.md)** — five observations on the 50-school set;
  established vs. suggestive vs. unanswered, with uncertainty flags preserved.
- **[`DATA_INSIGHT_DRAFT.md`](DATA_INSIGHT_DRAFT.md)** — the allocation-regime finding (where you
  can get a guaranteed large allocation is a minority of the headline count).
- **[`validate.py`](validate.py)** — substantive checks that **independently re-aggregate
  `clusters.csv` and assert `data.json` matches**, plus **cross-chart reconciliation** (the
  generation chart, scatter, ranking, table, and allocation-regime chart must report identical
  documented totals; `classified + unknown == documented`; generations only where evidence
  exists; reference points never fold into HERD-50). `python3 validate.py`.

### Count concepts (a verified cluster-count is NOT a university total)

| Field | Meaning |
|---|---|
| `verified_model_count` | per-model GPUs from primary sources |
| `aggregate_count` | independently-sourced totals w/o model breakdown (w/ overlap flag) |
| `documented_lower_bound` | verified + **non-overlapping** aggregates (the "≥" figure) |
| `cloud_gpus` / `planned_gpus` | reserved cloud / under-construction — **excluded** |
| `facility_gpus` vs `federal_funded_gpus` | national-allocation vs funding — **separate** attributes |
| `legacy_estimate` | GPUs-Per-Student-derived, kept separate as *unverified* (discovery only) |

**Known limitations (plainly):**
- **Documented ≠ complete.** Condo/aggregate clusters often publish no per-model count; figures
  are lower bounds. Missing inventory ≠ zero.
- **Generation data is sparse.** Only 8 of 41 documented schools have model-level evidence; the
  rest is "Generation unknown."
- **Correlations are exploratory** Pearson on lower bounds; association, not causation, and not
  evidence of under-investment.
- **Reference schools** (Princeton, Rice) sit outside the HERD-50 sample and are excluded from
  every statistic.

## National allocations & context

- **Leadership node-hours** — DOE **INCITE 2025 + ALCC 2025**, complete across all leadership
  facilities, parsed from the official ASCR/INCITE fact-sheet PDFs (`alloc_build.py`).
- **NAIRR projects** — AI-pilot allocation counts (nairrpilot.org awards CSV).
- **National labs** a university merely manages/operates (NERSC, Frontier, Aurora, SLAC, PPPL…)
  are a **context panel only**, in native accelerator counts, **never summed** into any metric.

Node-hours and project counts are distinct units, never mixed with owned-GPU counts. NSF ACCESS
and routine NERSC/ERCAP allocations are not quantified (no clean per-institution public totals).

## Files

| File | Purpose |
|------|---------|
| `index.html` | **The dashboard.** Self-contained — open directly in a browser. |
| `herd50.csv` | **Authoritative** 50-university inventory (documented lower bounds). |
| `clusters.csv` | Cluster-level records — the model-level / generation evidence. |
| `research_subset.csv` | Top-20 allocation-regime classification (matches herd50 totals). |
| `herd_cs.csv` | Computer & information sciences R&D (NSF HERD FY2024, Table 15) per school, with the source HERD table name — the optional "vs. CS R&D" scatter axis. |
| `reference_points.csv` | Endowment-heavy schools outside HERD-50 (scatter reference only). |
| `data.json` | Built payload: `herd50`, `gen_chart`, `headline`, `research_subset`, `reference_points`, and legacy `schools`. |
| `build_data.py` | Build script: assembles `data.json` and injects it into `template.html` → `index.html`. |
| `template.html` | HTML/CSS/JS template with a `__DATA_JSON__` placeholder. |
| `raw_gpus.csv` | **Legacy** GPUs-Per-Student inventory — discovery only, never in headline figures. |
| `validate.py` | Data-integrity + cross-chart reconciliation checks. |
| `snapshots/` | Dated archives of the compute state, one per rebuild. |

## Rebuild

```bash
python3 alloc_build.py && python3 build_data.py && python3 validate.py
open index.html
```

## Data currency

- **GPU capacity:** primary sources (university research-computing docs, NSF/DOE facility pages,
  official announcements), verified through Oct 2026. Documented lower bounds.
- **R&D:** NSF HERD FY2024 (released Nov 2025). **CS R&D:** NSF HERD FY2024 Table 15 (R&D by
  field), "Computer and information sciences," institution-level — an optional scatter axis; a
  reported $0 (e.g. medical centers) is kept distinct from missing. CS R&D is a proxy for
  relevant research activity, not a comprehensive measure of AI-research demand (AI research is
  often classified under other fields). **Endowments:** 2025 NACUBO-Commonfund Study /
  FY2025 compilations where reported; FY2024 for a few smaller schools.

# Pilot audit — 10 universities, independent primary-source verification

**Date:** 2026-10-11 (rev. 2) · **Method:** each school's GPU inventory reconstructed from
primary sources (university research-computing docs, official announcements, NSF/DOE
facility docs), compared against the legacy GPUs-Per-Student (GPS) figures. Cluster-level
records with source URLs, `count_basis` (primary / legacy / aggregate), status, and
overlap flags are in `clusters.csv`. **This is a verification exercise on a non-random
set of 10 schools, not a representative sample.** Work stops here for review before
expanding.

## Calibrated conclusion

> An independent audit of ten universities identified **substantial errors and
> inconsistent accounting** in the legacy academic-GPU inventory — including **duplicate
> accelerators** (Illinois, UT Austin), **cloud capacity classified as locally owned**
> (CMU), **planned equipment counted as operational** (Oregon State), **virtual MIG
> partitions counted as physical GPUs** (Princeton), and **incomplete or wrong
> hardware-generation records** (Harvard, NYU). **For several universities (Stanford,
> MIT, Johns Hopkins, and Harvard's Cannon), public documentation is insufficient to
> establish comprehensive totals** — so a *lower discrepancy* there reflects incomplete
> coverage, not a confirmed legacy overcount.

Crucially, the errors are **not uniformly in one direction**: Harvard's legacy row
actually **under**-stated its current Kempner cluster (wrong H200 count, missing 192 RTX
PRO 6000) while also omitting Cannon. So "legacy consistently overstates" is **too strong**
and has been retracted. Where a stronger per-institution claim is warranted (Illinois, UT
Austin, CMU, Oregon State), it is made individually with evidence below.

## Reconciliation table

"Best-supported" is a documented **lower bound (≥)** where the inventory is incomplete.

| University | Legacy GPS | New evidence | Best-supported | Classification |
|---|--:|---|--:|---|
| Illinois | 2,212 | 608 DeltaAI GH200 double-counted as H100 | **≥1,604** verified (+46 legacy) | **Confirmed overcount** |
| UT Austin | 1,890 | 600 Vista GH200 double-counted; 430 decommissioned V100/P100 | **≥860** verified | **Confirmed overcount + misclassification** |
| CMU | 367 | 296 H100 are GCP reserved cloud, not owned | **0 verified owned** (+71 legacy, +296 cloud) | **Confirmed misclassification** |
| Oregon State | 274 | 150 Rubin = Huang Complex, opens 2027 | **0 verified** (+124 legacy, +150 planned) | **Confirmed misclassification** |
| NYU | 2,134 | primary shows 60 H100, not 780; Greene=RTX8000+V100 | **≥1,108** verified | **Confirmed overcount** (esp. H100) |
| Princeton | 2,092 | MIG slices counted as physical; Tiger/Stellar not enumerated | **≥756** verified | **Overcount (MIG) + unresolved (coverage)** |
| Harvard | 1,258 | legacy missed 192 RTX PRO 6000 & understated H200; Cannon unresolved | **≥1,144** (Kempner) | **Misclassification (composition); legacy likely UNDER-counted** |
| Florida | 1,752 | A100 SuperPOD being replaced by B200; L4 added | **≥1,104** (504 B200 + 600 L4) | **Different measurement definition** |
| MIT | 1,636 | Engaging ≥1,000 (aggregate, distinct) + SuperCloud 448 | **≥1,448** | **Unresolved** (per-model unknown) |
| Stanford | 1,822 | Marlowe 248 verified; Sherlock unquantified | **≥248** | **Unresolved** (incomplete coverage) |
| Johns Hopkins | 484 | Rockfish 144 verified; DSAI unquantified | **≥144** | **Unresolved** (incomplete coverage) |

**Tally:** 3 confirmed overcounts (Illinois, UT Austin, NYU), 3 confirmed
misclassifications (CMU cloud, Oregon State planned, Harvard composition), 1 mixed
(Princeton), 1 different-definition (Florida), 3 unresolved from incomplete coverage
(MIT, Stanford, JHU). **Not** a uniform overstatement.

## Illinois — funding vs allocation vs ownership (reconciling 1,512 vs 1,576)

These measure different attributes and both are now reported:
- **Nationally-allocated facility = 1,512** (Delta + DeltaAI; access = national-allocation via ACCESS).
- **Federally-funded = 1,576** (adds HAL's 64 V100 — NSF-MRI *funded* but **university-access**, not nationally allocated).
- **Institutionally-accessed** includes HAL + campus/Radiant.
Federal *funding*, national *allocation/access*, and *ownership* are tracked as three
independent attributes, not collapsed into one "facility" classification.

## Per-institution notes (evidence)
- **Harvard:** Kempner verified 1,144 (424 H200 + 384 H100 + 144 A100 + 192 RTX PRO 6000; kempnerinstitute.harvard.edu). Cannon (~2,000, mixed) kept as an **aggregate with overlap-vs-Kempner UNRESOLVED → excluded from the lower bound**.
- **MIT:** SuperCloud 448 V100 (primary); Engaging "over 1,000" (aggregate, established **distinct** from SuperCloud → included in lower bound as ≥1,000). Per-model Engaging unknown. B200 (~200) planned.
- **Stanford:** Marlowe 248 (primary); Sherlock condo model, aggregate unquantified.
- **JHU:** Rockfish 144 (primary); DSAI aggregate unquantified.
- **CMU:** 296 H100 = GCP reserved VMs (cmu.edu/rcd). Local ~71 are legacy-sourced (confidence low), kept as a separate unverified estimate — **not** counted as verified owned, **not** counted as zero.
- **Oregon State:** operational ~124 are legacy-sourced; 150 Rubin planned (opens 2027).
- **Illinois / UT Austin / NYU / Princeton / Florida:** see table + `clusters.csv`.

## Dashboard status
- Audited schools derive from `clusters.csv` with explicit **verified / aggregate /
  legacy / lower-bound** accounting. "Documented GPUs" is a **lower bound (≥)**. Cloud and
  planned are separated and excluded from operational. Provenance badges + a verification
  filter are live; expand any row for the full count breakdown and sources.

## Highest-priority data gaps (ranked by impact on conclusions)
1. **Stanford Sherlock, MIT Engaging per-model, Harvard Cannon, JHU DSAI** — the four
   unresolved aggregates; resolving them would convert "unresolved" into confirmed figures.
2. **CMU & Oregon State local counts** — currently legacy-sourced; need primary confirmation.
3. **Florida A100 SuperPOD status** — operational, partially retired, or fully replaced?
4. **Princeton non-Della clusters** (Tiger/Stellar) and MIG accounting.
5. **Ownership/funding attributes** for NYU/OSU (currently "unknown").

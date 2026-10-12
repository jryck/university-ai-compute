# Pilot audit — 10 universities, independent primary-source verification

**Date:** 2026-10-11 · **Method:** each school's GPU inventory reconstructed from
primary sources (university research-computing docs, official announcements, NSF/DOE
facility docs), then compared against the legacy GPUs-Per-Student (GPS) figures the
dashboard previously treated as authoritative. Cluster-level records with source URLs
are in `clusters.csv`. **This pilot is a verification exercise, not a representative
sample.** Per instruction, work stops here for review before expanding to the other 40.

> **Headline:** the legacy source **consistently and substantially overstates** owned
> GPUs — via double-counting, "highest-estimate" inflation, MIG slices counted as
> physical GPUs, decommissioned hardware, and cloud/planned systems counted as owned.
> Of the 10, not one legacy figure was confirmed; most were materially too high.

## Summary

| University | Legacy GPS (owned) | Independently verified | Δ | Direction | Coverage |
|---|--:|--:|--:|---|---|
| Harvard | 1,258 | Kempner 1,144 (verified); +FASRC Cannon unresolved | n/a | legacy miscomposed | partial |
| Stanford | 1,822 | Marlowe 248 (verified); Sherlock unresolved | −1,574 vs documented | legacy ≫ documented | low |
| MIT | 1,636 | Engaging "1,000+" + SuperCloud 448 (no per-model) | n/a | aggregate only | medium |
| Illinois | 2,212 | 1,650 (double-count fixed) | −562 | overstated | high |
| UT Austin | 1,890 | 860 (double-count + decommissioned removed) | −1,030 | overstated | high |
| Florida | 1,752 | HG4: 504 B200 + 600 L4; A100 SuperPOD being replaced | ~ | recomposed | medium |
| Carnegie Mellon | 367 | 71 owned (296 H100 are GCP cloud, not owned) | −296 owned | miscategorized | high |
| Johns Hopkins | 484 | Rockfish 144 (verified); DSAI partial | n/a | partial | partial |
| Princeton | 2,092 | Della ~756 physical (336 H100 + 144 H200 + 276 A100) | −1,336 | overstated | medium |
| NYU | 2,134 | Greene 332 + Torch 776 = 1,108 (only 60 H100) | −1,026 | overstated | medium |

## Per-institution detail

### Harvard — legacy 1,258; miscomposed
- **Verified (Kempner AI Cluster):** 424 H200 + 384 H100 + 144 A100 + 192 RTX PRO 6000 (Blackwell) = **1,144**. Source: kempnerinstitute.harvard.edu/kempner-ai-cluster (phases: A100 2023-03, H100 2023-09, H200+RTX PRO 2026-03; fully online Spring 2026).
- **Legacy error:** legacy row has H200 = 96 (should be 424) and **zero RTX PRO 6000** (should be 192) — it captured an earlier Kempner phase. It also carried 200 V100 + 124 L40S + 170/210 A100 attributed to FASRC Cannon/HMS.
- **Open:** FASRC Cannon's own GPU count (~2,000 cited on rc.fas.harvard.edu) is **not independently resolved per-model**, and its overlap with Kempner is unclear. HMS O2 not verified.

### Stanford — legacy 1,822; only 248 documented
- **Verified:** Marlowe = **248 H100** (31 DGX H100 × 8). Source: news.stanford.edu 2024-12.
- **Open:** Sherlock is a condo/PI-owned model; Stanford does not publish an aggregate GPU count. The legacy 1,822 could not be substantiated from primary sources. **Largest unresolved gap in the pilot.**

### MIT — legacy 1,636; aggregate-only
- **Verified:** Engaging = "**over 1,000 GPUs**" (A100/RTX6000/L40S/H100/H200) — per-model counts not published (orcd.mit.edu). SuperCloud = **448 V100** (joint with Lincoln Lab). B200 (~200) is **planned/installing** (state grant). 
- **Open:** no per-model Engaging breakdown is public; only an aggregate is verifiable.

### Illinois — legacy 2,212; corrected 1,650
- **Error:** 608 DeltaAI Grace Hopper counted **twice** (as H100_SXM *and* GH200). Corrected per-model: H100 4, GH200 608, A100-40 440, A40 400, H200 64, V100 64, A10 46, A100-80 24 = **1,650**. Of this, **1,576 is the NCSA national facility** (Delta/DeltaAI/HAL — NSF, nationally allocated); only **74 is institutional**. Sources: docs.ncsa.illinois.edu (Delta, DeltaAI).

### UT Austin — legacy 1,890; corrected 860
- **Error:** Vista's 600 Grace Hopper counted twice (H200 + GH200); decommissioned Longhorn/Maverick2 (424 V100 + 6 P100) still counted. Corrected: GH200 600 (Vista, NSF facility) + A100-40 252 + H100 8 (Lonestar6, UT-funded) = **860**. Source: docs.tacc.utexas.edu.

### Florida — legacy 1,752; recomposed
- **Verified (HiPerGator 4.0, production Fall 2025):** 504 B200 (63 DGX B200) + 600 L4. Source: news.ufl.edu 2025-10.
- **Issue:** the legacy 1,248 A100 is the 2020-era DGX A100 SuperPOD, which UF says the B200 SuperPOD **replaces** — its current operational status is **unresolved**, so legacy likely double-books old + new. L4 (600) was absent from legacy.

### Carnegie Mellon — legacy 367; owned 71
- **Error:** the 296 H100 are **Google Cloud reserved-instance VMs**, not owned hardware (cmu.edu/rcd/faq.html — FLAME 256 + Community 40). Reclassified to a cloud tier. Owned ≈ **71** (A40 29, L40S 18, P100 20, A6000 4).

### Johns Hopkins — legacy 484; Rockfish 144 verified
- **Verified (Rockfish):** 72 A100-40 + 40 A100-80 + 32 L40S = **144** (docs.arch.jhu.edu). 
- **Open:** DSAI cluster (A100/H100/L40S) per-model counts **not independently confirmed**; JHPCE (medical) not verified.

### Princeton — legacy 2,092; Della ~756 physical
- **Verified (Della):** 336 H100 (PLI) + 144 H200 (AI Lab) + ~276 physical A100 = **~756**. Source: researchcomputing.princeton.edu/systems/della.
- **Legacy error:** 2,092 appears to count **MIG slices as physical GPUs** and includes high "Claude/Gemini"-estimated A100-40 counts plus legacy Tiger/Traverse. Physical Della is far lower. MIG-partitioned nodes excluded from the physical count here.

### NYU — legacy 2,134; verified 1,108
- **Verified:** Greene 332 (292 RTX8000 + 40 V100) + Torch 776 (60 H100 + 172 A100 + 272 H200 + 272 L40S) = **1,108**. Source: nyu.edu HPC cluster pages.
- **Legacy error:** legacy claims **780 H100**; primary sources show **60**. The legacy H100 figure is overstated ~13×. (RTX8000 is a Turing/Quadro card absent from the legacy model schema.)

## Cross-cutting findings

1. **Direction of error is one-sided: legacy overstates.** Double-counts (Illinois, UT Austin), MIG-as-physical (Princeton), cloud-as-owned (CMU), decommissioned-as-live (UT Austin), planned-as-live (Oregon State, outside pilot), and "highest-estimate" inflation (NYU H100, Princeton A100).
2. **Condo/aggregate clusters resist per-model verification** (Stanford Sherlock, MIT Engaging, Harvard Cannon, JHU DSAI) — primary sources give totals or model lists but not clean per-model counts.
3. **Schema gaps:** legacy omits models that primary sources show (RTX PRO 6000, L4, RTX8000), so even its model mix is incomplete.

## Status of the dashboard after this pilot
- **Phase 2 done:** the dashboard now **derives all audited schools from `clusters.csv`**, not GPUs Per Student. Every school carries a provenance badge — `verified` / `partial` / `legacy` / `legacy-adjusted` — and a verification filter. The 10 pilot schools (+ Oregon State) are verified/partial from primary sources; the other 40 remain `legacy` (clearly marked, likely overstated) until audited. Expand each row for per-school sources, cloud/planned splits, and unresolved aggregate clusters.
- Remaining UI gap: the scatter/bar charts still plot legacy and verified points with the same styling (the table distinguishes them). Per-point provenance styling is a Phase-2b polish.
- Funding default is now **Unknown** (not Institutional). Generation classes corrected (Pascal/Ada/Rubin). Metric relabeled **H100 price-equivalent** (value ÷ $35k), not performance.

## Recommended next steps (post-pilot)
1. **Migrate the dashboard university totals to derive from `clusters.csv`** (verified) with a visible verified/legacy badge per school; keep legacy visible but clearly marked.
2. **Resolve the condo/aggregate clusters** (Sherlock, Engaging, Cannon, DSAI) by contacting RC offices or citing facilities PDFs; until then mark coverage = partial.
3. **Build the R&D-defined (NSF HERD) sample** and join GPU coverage, with null (not zero) where undocumented.
4. **Add a transparent performance-normalized metric** (dense BF16/FP16 tensor throughput vs H100) as a *separate* field, leaving pre-BF16 parts explicit.
5. **Expand verification** to the next ~15 schools by documented compute, prioritizing the largest legacy figures (highest overstatement risk).

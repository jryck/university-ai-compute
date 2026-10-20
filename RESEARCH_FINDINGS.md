# Research findings — top-50 US universities by R&D (NSF HERD FY2024)

**Sample:** the 50 highest-R&D US universities (NSF HERD FY2024), defined independently of
GPU holdings. **Coverage:** 41 of 50 have documented GPU capacity from primary sources; 9
are unresolved (condo clusters that publish no count, or medical centers). All GPU figures
are **documented lower bounds** (`herd50.csv`). Total documented: **≥19,796 GPUs**. Date:
2026-10-19.

> Caveat applied throughout: lower bounds + 18% unresolved means absolute totals understate
> reality and correlations are noisy. Findings are framed to survive that.

## Five observations

**1. R&D is a weak positive predictor of documented GPU capacity; endowment moderate.**
**R&D spending vs documented GPUs ≈ +0.12** (Pearson, raw; +0.22 log; Spearman +0.23; n=41),
and **endowment vs documented GPUs ≈ +0.39** (Pearson; +0.26 log; Spearman +0.27; n=38).
These are higher than earlier estimates (which had R&D ≈ −0.05, endowment ≈ 0.19) largely
because better documentation of a few large schools (Stanford Sherlock, JHU Skipjack, Harvard
Cannon) raised their counts — i.e. the relationship is **sensitive to documentation
completeness**, not a stable structural estimate. The highest-R&D institutions are still *not*
the highest-compute: Johns Hopkins (#1 in R&D, $4.1B) documents 636; the largest documented
fleets are Illinois (1,650), Stanford (1,504), MIT (1,448), Harvard (1,384), NYU (1,276).
*Direction (endowment > R&D) is robust; magnitude is coverage-sensitive.*

**2. Documented GPU capacity is more concentrated than research spending.** Among documented
fleets, the top-10 schools hold **61% of documented GPUs but only 31% of R&D**; top-5, **37%
vs 18%** (still ≈2× more concentrated than research spending). *This describes documented capacity, not necessarily actual capacity: documentation
is incomplete and uneven, so the undocumented and lower-bound portions could move measured
concentration in **either** direction. The descriptive figures stand; the inference to true
concentration does not.*

**3. A substantial share of documented academic GPUs is federal/state shared infrastructure,
not institutional.** Six national/state-facility hosts (UCSD/SDSC, UT Austin/TACC,
Illinois/NCSA, Pittsburgh/PSC, Ohio State/OSC, Purdue/Anvil) account for **≥19% of all
documented GPUs** (3,772 of 19,796) — and within those hosts it is the large majority (e.g.,
Illinois 1,512 of 1,650; UT Austin 600 of 860 are nationally allocated, not
institution-exclusive). The share fell from an earlier ~24% as more non-facility capacity
became documented (Sherlock, Skipjack, Cannon) while facility counts held — so this is a
lower-bound floor on the facility share, not a fixed quarter. The "university" GPU total
conflates institutional hardware with federal infrastructure. *Robust lower bound.*

**4. Central-institutional is the most common model, but not where the capacity is.** By
count, 22 of 50 run a central institutional cluster, 14 are condo/faculty-priority, 6 are
national/state facilities. But most central clusters are **small** (Cincinnati 14, Wisconsin
72, Maryland 80); the capacity concentrates in a few national facilities plus a handful of
large institutional clusters (Harvard, NYU, MIT, Florida). **Model prevalence ≠ capacity** —
a school can "have a central cluster" that is tiny. *Robust.*

**5. Compute-per-endowment ratios are not interpretable from current data.** Documented GPUs
per $B of endowment vary widely across schools, but we do **not** report a specific range,
ratio, or ranking: the spread is dominated by documentation gaps (some inventories are
near-complete, others are lower bounds or unresolved) and by heavy cloud/national-facility
reliance. Incomplete inventories undermine any per-wealth comparison, and the variation is
**not** evidence of over- or under-investment.

## The five guiding questions, answered
- **Q1 wealth→compute:** weakly related — R&D r≈+0.12, endowment r≈+0.39 (documentation-sensitive). See Obs. 1/5.
- **Q2 concentration:** *documented* GPUs are more concentrated than R&D (descriptive only; the inference to actual capacity does not hold — see Obs. 2). See Obs. 2.
- **Q3 government infrastructure:** ≥19% of documented GPUs are national/state facilities. Obs. 3.
- **Q4 hardware generations:** *partially answerable.* Per-generation data exists for the ~20
  audited schools (Hopper-dominant, with Florida on Blackwell and legacy V100/RTX8000 fleets at
  NYU/UW) but is not uniform across all 50 — recorded as a gap, not forced.
- **Q5 strategies:** four live models (central, condo/faculty-priority, national/state, cloud),
  most schools hybrid; central is most common by count, national facilities largest by capacity.

## Potential Data Insights
1. **"Documented academic AI compute is more concentrated than, and weakly related to, research spending."**
   (Obs. 1 + 2.) A descriptive statement about documented capacity, not actual capacity; quantified on an
   unbiased sample. Strongest candidate, but see the Obs. 2 caveat on inference.
2. **"Where you can get a guaranteed large allocation is a minority of the headline count"**
   (the Phase-4 allocation-regime finding, `DATA_INSIGHT_DRAFT.md`) — complementary and still valid.

## Coverage summary
- **41/50 (82%)** have primary-source documented GPU capacity; **9 unresolved**: Michigan,
  UCLA, UNC, Penn State, Berkeley (condo, no published count) and MD Anderson, Baylor CoM, UAB,
  Colorado Anschutz (medical/hosted-elsewhere).
- Of the 41, ~18 are single-cluster verified; the rest are aggregates or partial inventories.
- Endowment available for all non-medical schools; medical-center endowments mostly n/a.

## Recommended next steps (max 3)
1. **Resolve the 9 unresolved schools** (mostly condo clusters) via RC-office queries — would
   lift coverage to ~100% and firm up Obs. 1–2.
2. **Systematic per-generation capture** across all 50 to answer Q4 (modernization) properly.
3. **Pressure-test Obs. 1–2** with sensitivity analysis (exclude aggregates; vary lower-bound
   assumptions) before any external publication.

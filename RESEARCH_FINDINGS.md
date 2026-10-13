# Research findings — top-50 US universities by R&D (NSF HERD FY2024)

**Sample:** the 50 highest-R&D US universities (NSF HERD FY2024), defined independently of
GPU holdings. **Coverage:** 41 of 50 have documented GPU capacity from primary sources; 9
are unresolved (condo clusters that publish no count, or medical centers). All GPU figures
are **documented lower bounds** (`herd50.csv`). Total documented: **≥17,808 GPUs**. Date:
2026-10-12.

> Caveat applied throughout: lower bounds + 18% unresolved means absolute totals understate
> reality and correlations are noisy. Findings are framed to survive that.

## Five observations

**1. R&D spending barely predicts documented GPU capacity.** Across the 38 schools with both
an endowment and documented GPUs, the correlation between **R&D spending and documented GPUs
is ≈ −0.05** (none), and between **endowment and documented GPUs ≈ 0.19** (weak). The
highest-R&D institutions are *not* the highest-compute: Johns Hopkins (#1 in R&D, $4.1B)
documents ~144; the largest documented fleets are Illinois, MIT, NYU, Harvard, UCSD. *Robust
in direction; magnitude is coverage-sensitive.*

**2. GPU capacity is about twice as concentrated as research spending.** The top-10 schools
hold **62% of documented GPUs but only 31% of R&D**; top-5, **37% vs 18%**. Academic AI
compute is markedly more unequal than the research enterprise it serves. *Robust (lower
bounds only compress this).*

**3. Roughly a quarter of documented academic GPUs is federal/state shared infrastructure,
not institutional.** Six national/state-facility hosts (UCSD/SDSC, UT Austin/TACC,
Illinois/NCSA, Pittsburgh/PSC, Ohio State/OSC, Purdue/Anvil) account for **≥24% of all
documented GPUs** — and within those hosts it is the large majority (e.g., Illinois 1,512 of
1,650; UT Austin 600 of 860 are nationally allocated, not institution-exclusive). The
"university" GPU total conflates institutional hardware with federal infrastructure. *Robust
lower bound.*

**4. Central-institutional is the most common model, but not where the capacity is.** By
count, 22 of 50 run a central institutional cluster, 14 are condo/faculty-priority, 6 are
national/state facilities. But most central clusters are **small** (Cincinnati 14, Wisconsin
72, Maryland 80); the capacity concentrates in a few national facilities plus a handful of
large institutional clusters (Harvard, NYU, MIT, Florida). **Model prevalence ≠ capacity** —
a school can "have a central cluster" that is tiny. *Robust.*

**5. Compute-per-wealth spans ~600×, and wealthy privates cluster at the bottom.** Documented
GPUs per $B of endowment range from **~434 (Illinois), ~410 (Florida)** to **<1 (Emory
0.7)**, with Yale, Duke, and Stanford also near the bottom. *Exploratory:* this partly
reflects incomplete inventories and heavy cloud/national reliance (Emory runs AI.Humanity on
AWS; Stanford's Sherlock is unresolved) — it is **not** evidence of underinvestment, and is
the most coverage-sensitive observation here.

## The five guiding questions, answered
- **Q1 wealth→compute:** essentially decoupled (R&D r≈−0.05; endowment r≈0.19). See Obs. 1/5.
- **Q2 concentration:** GPUs ~2× more concentrated than R&D. See Obs. 2.
- **Q3 government infrastructure:** ≥24% of documented GPUs are national/state facilities. Obs. 3.
- **Q4 hardware generations:** *partially answerable.* Per-generation data exists for the ~20
  audited schools (Hopper-dominant, with Florida on Blackwell and legacy V100/RTX8000 fleets at
  NYU/UW) but is not uniform across all 50 — recorded as a gap, not forced.
- **Q5 strategies:** four live models (central, condo/faculty-priority, national/state, cloud),
  most schools hybrid; central is most common by count, national facilities largest by capacity.

## Potential Data Insights
1. **"Academic AI compute is more concentrated than, and decoupled from, research spending."**
   (Obs. 1 + 2.) Novel, quantified on an unbiased sample, defensible with lower-bound framing.
   Strongest candidate.
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

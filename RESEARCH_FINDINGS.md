# Research findings — what the corrected pilot data supports

**Scope:** 10 pilot universities verified against primary sources (+ Oregon State); the
other 38 schools remain **unverified legacy data**. All verified figures are **documented
lower bounds** with partial coverage. These findings are deliberately conservative.

Date: 2026-10-12.

---

## A. Established (definitively supported by the evidence)

**A1. Specific, confirmed accounting errors in the legacy inventory.** Not inference —
each is reproducible from primary sources:
- **Duplicate accelerators:** Illinois (608 DeltaAI GH200 counted twice), UT Austin (600 Vista GH200 counted twice).
- **Cloud counted as owned:** CMU's 296 H100 are Google Cloud reserved VMs.
- **Planned counted as operational:** Oregon State's 150 Rubin (opens 2027).
- **Virtual MIG partitions as physical GPUs:** Princeton.
- **Wrong hardware-generation composition:** Harvard (missing 192 RTX PRO 6000, understated H200); NYU (780 H100 claimed, 60 documented).
- **Decommissioned hardware as current:** UT Austin (430 V100/P100).

**A2. These errors change apparent rankings.** After correction, Illinois and UT Austin
fall sharply (their bulk is a nationally-allocated NSF facility, not institutional
hardware); NYU falls; CMU's "owned" fleet is ~0. So legacy-based league tables are not
reliable.

**A3. Ownership ≠ access ≠ funding — and the distinction is material.** Among the pilot:
- Of ~7,400 verified GPUs, **~2,100 (28%) are nationally-allocated NSF facilities** (Illinois NCSA, UT Austin TACC), not institutional hardware.
- CMU's largest compute (296 H100) is **reserved cloud**, not owned.
- Illinois's ≥1,604 is ~94% national facility; its *institutional* owned fleet is ≈90 GPUs.
A single "owned GPUs" number conflates categories that behave very differently.

**A4. For several universities, public documentation cannot establish a total.** Stanford
(Sherlock), MIT (Engaging per-model), Harvard (Cannon), and JHU (DSAI) publish aggregate
or no counts. Their verified figures are floors (e.g., Stanford **≥248**, not 1,822 and
not a reliable 248-as-total).

---

## B. Suggestive (patterns consistent with the data, not established)

**B1. Funding is more often federal or unknown than demonstrably institutional.** Of the
11 pilot schools, 6 have **Unknown** (unverified) funding, 2 are NSF-facility, 2 Mixed, 1
vendor-donation. The earlier claim that "most universities fund their own compute" is
**not supported**; where funding is documented, it is frequently federal or donated.

**B2. Compute composition / vintage varies.** Florida is Blackwell-forward (skipped
Hopper at scale: B200 + L4); NYU carries large Turing/Volta legacy fleets; Illinois/UT are
Grace-Hopper-heavy via NSF facilities. Descriptive only.

---

## C. Weakened or overturned since the first round

**C1. "The wealthiest universities own the least compute per dollar" — NOT ESTABLISHED
(weakened to unsupported).** This pattern was an artifact of (a) legacy *overstatement*
for some public/GPU-heavy schools and (b) *incomplete coverage* understating wealthy
privates. Stanford and Harvard's true totals are unknown (Sherlock/Cannon undocumented),
so we cannot claim they "own little." This headline has been removed/qualified on the site.

**C2. "Legacy data consistently overstates owned GPUs" — RETRACTED.** True for several
schools, but Harvard's legacy row *under*-counted current Kempner, and 3 pilot schools are
unresolved (not confirmed overcounts). Correct statement: legacy contains **substantial,
non-uniform errors.**

**C3. "Access ≠ ownership" (USC/Michigan own little but win big allocations) — UNTESTED
for this pilot.** Those schools are still legacy/unverified; the claim cannot be made from
verified data yet. The *concept* (allocations are a distinct axis) stands; the specific
examples do not until verified.

---

## D. Unanswered (require more verification)

1. **True totals for the four unresolved aggregates** (Sherlock, Engaging, Cannon, DSAI).
2. **How much of all US academic AI compute is institutional vs federal vs cloud** — needs
   the sample verified and a defined universe (NSF-R&D top-N), not GPU-selected.
3. **Whether any wealth/compute or R&D/compute relationship survives** once coverage is
   comparable across schools (currently it is not).
4. **Ownership and funding attributes** for schools currently marked Unknown.

---

## Bottom line
The defensible claims today are **(A1–A4)**: the legacy inventory has specific confirmed
errors, those errors move rankings, and ownership/access/funding must be separated. Broad
cross-institutional claims about wealth, research, or investment behavior are **not yet
supportable** with verified data and should not be presented as findings.

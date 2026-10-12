# At most leading US research universities, the AI compute isn't the university's

**Finding.** Among the 20 US universities with the largest research-and-development
budgets (NSF HERD, FY2024), only **5 — Harvard, NYU, Penn, Stanford, and Georgia Tech —
operate a large, dedicated, centrally-funded GPU cluster that the institution itself
owns and controls.** In the majority of the rest, the GPUs that exist are owned by
*individual labs* (the "condo" model, ≥8 of 20) or by *federal or state agencies* (NSF/
state shared facilities, 3 of 20). At the institutional level, the university frequently
*operates* compute it does not *own* or *control*.

## Why it matters

Public discussion of academic AI compute treats "the university" as the unit that has
(or lacks) GPUs — e.g., "University X has N H100s." Our primary-source audit of the
top-20-by-R&D universities shows this unit is usually wrong. The dominant arrangements
place control somewhere other than the central institution:

- **Condo clusters.** The central HPC cluster is a shared host for hardware purchased by
  individual PIs, labs, or departments. Cornell's shared cluster spans **755 GPUs across
  70 distinct resource owners**; Columbia's Insomnia was a **joint purchase by 21 research
  groups**; Washington's Hyak and UCLA's Hoffman2 are explicit condo models. The
  institution schedules the hardware but does not own most of it, and typically does not
  publish a per-model inventory because there isn't a single institutional one.
- **National / state facilities.** The largest GPU systems "at" some universities are
  federally or state funded and allocated beyond the host. UC San Diego's SDSC (Expanse +
  Voyager) and Pittsburgh's PSC (Bridges-2) are **NSF facilities allocated nationally via
  ACCESS**; Ohio State's OSC is a **state facility serving all of Ohio**. These are not
  institutional AI capacity in any ownership sense.
- **Dedicated institutional clusters — the exception.** Only Harvard (Kempner, ≥1,144
  GPUs), NYU (Greene + Torch, ≥1,108), Penn (Betty DGX B200 SuperPOD), Stanford (Marlowe,
  248 H100), and Georgia Tech (AI Makerspace, ≥344) run a large GPU supercomputer the
  institution funded and controls centrally. **Every one is recent (2023–2026)**, and
  where funding is documented it traces to philanthropy or one-time institutional/state
  capital (e.g., Harvard's Kempner gift; Florida's NVIDIA-gift HiPerGator, outside this
  sample) — **not** recurring research budgets.

## Evidence

The primary chart classifies each of the 20 universities by its principal
compute-control model, with documented GPU counts (verified lower bounds) where primary
sources publish them and an explicit *unresolved* marker where they do not. Sources are
each university's own research-computing documentation, NSF/DOE facility pages, and
official announcements (`research_subset.csv`, column `primary_source`).

| Control model | Universities (of 20) |
|---|---|
| Dedicated institutional cluster | 5 — Harvard, NYU, Penn, Stanford, Georgia Tech |
| Institutional shared (modest central) | 4 — Johns Hopkins, Wisconsin, Maryland, Yale |
| Condo (PI/department-owned) | 7 — Michigan, UCLA, UW, Cornell, UNC, Duke, Columbia |
| National / state facility host | 3 — UC San Diego, Ohio State, Pittsburgh |
| Minimal / cloud-reliant | 1 — UCSF |

The point is not the exact counts (which are incomplete; see Limitations) but the
**category distribution**: dedicated institutional control is a minority arrangement.

## What drives it

The condo model is an equilibrium: central IT provides power, cooling, networking, and
staff, while faculty buy GPUs from their own grants. It is administratively convenient and
spreads capital cost across PIs, but it produces a fleet that is fragmented (owned by
dozens of parties), hard to marshal for a single large job, and invisible as an
institutional total. A dedicated institutional cluster requires a large, lumpy capital
outlay that recurring research budgets don't fund — which is why the five that exist were
enabled by donors, vendor partnerships, or one-time state/institutional commitments, and
why they appeared only once frontier AI made the case urgent.

## Implications

- **"Who has the most university AI compute" is largely a category error.** Rankings that
  sum GPUs "at" a university conflate PI-owned, federally-owned, and institution-owned
  hardware that behave completely differently.
- **It explains the pull of national programs.** If most universities cannot marshal
  institutional compute, shared federal infrastructure (NSF ACCESS, NAIRR, DOE INCITE) is
  not a supplement but the primary path to scale for most academic researchers.
- **It reframes "underinvestment."** Low institution-controlled compute is not obviously
  under-investment; for many universities the condo model *is* the investment strategy.

## Limitations

- **Sample.** 20 universities, defined independently by R&D rank (not by GPU holdings) to
  avoid selection bias — but 20, not a census; not generalizable to all US universities.
- **Completeness.** Condo and aggregate clusters do not publish per-model counts; GPU
  figures are **documented lower bounds**, and several are unresolved. Counts should not be
  compared as if complete, which is precisely why the finding is about **control model**,
  a variable we *can* establish, not about precise GPU totals.
- **Classification.** Some universities span models (Stanford: dedicated Marlowe + condo
  Sherlock); each is assigned its principal arrangement, with specifics in
  `research_subset.csv`. Ownership and funding are recorded separately from operation and
  access and are "unknown" where not documented.
- **Timing.** This is a late-2025/2026 snapshot; dedicated clusters are being built quickly
  (Penn's Betty, MIT's incoming B200s), so the count of "dedicated" is a rising floor.

## Is this publishable?

The control-model classification of the top-20-by-R&D universities, from primary sources,
is — to our knowledge — **not available elsewhere** and overturns the common "GPUs per
university" framing. It is a defensible, specific, novel result suitable for a short Data
Insight, provided it is presented as a **structural classification with documented lower
bounds**, not as precise aggregate GPU shares.

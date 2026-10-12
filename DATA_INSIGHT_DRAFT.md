# The AI GPUs at top US universities are mostly faculty-priority, not centrally allocatable

**Finding.** At leading US research universities, the hardware is almost always
university-owned — but a general researcher's *guaranteed* access runs through a
**central/public allocation pool that is a minority of the headline GPU count**. Where
universities disclose the split, the centrally-allocatable share is small: at **NYU, 232
of 944 Torch GPUs** are the general "IT-public" pool (the other 712 are stakeholder-
priority); at **UCSF, 88 of 235** Wynton GPUs are communal (147 are PI-contributed); at
**Columbia, the general/free tier has *zero* GPUs** — GPU access requires a group to buy
in. The dominant governance model is *faculty- or stakeholder-priority allocation*, not
central institutional control.

Two things this is **not**. It is **not** "universities don't own their GPUs" — legal
ownership is almost always the university's, even for PI-funded "condo" hardware. And it is
**not** that fragmentation strands idle capacity: idle priority-GPUs are **near-universally
shared** through preemptible or time-limited queues (Cornell's three-tier preemptible
partitions; UCLA's 24-hour "shared" jobs on others' idle nodes; Yale's `scavenge_gpu`;
Wisconsin's HTCondor backfill; UCSF's 2-hour cap for non-contributors). Opportunistic
access to the full fleet is broad.

The binding constraint is instead **guaranteed, non-preemptible scale for a single
coordinated job** — and that is capped by (a) the size of the central pool and (b) explicit
per-job scheduling limits. Princeton's PLI partition illustrates the latter: it has 336
dedicated H100s, yet its published QOS caps a single job at roughly 16–35 GPUs.

## Why it matters

The standard way to describe academic AI compute — "University X has N GPUs" — answers the
wrong question. N conflates three different things a researcher experiences very
differently: GPUs they can get a large guaranteed block of (central pool), GPUs they can
use opportunistically but can be preempted from (idle priority capacity), and GPUs that are
effectively someone else's (another group's priority, or a nationally-allocated federal
facility). For the question that matters to large coordinated experiments — *how many GPUs
can I count on, uninterrupted, at once?* — the relevant number is usually far below N and is
set by scheduling policy, not hardware.

## Evidence

The chart shows, for the 20 highest-R&D US universities (NSF HERD FY2024, an independent
sample not selected on GPU holdings), documented GPUs split by **allocation regime**:
central/generally-allocatable, faculty/stakeholder-priority, nationally/state-allocated
facility, and unresolved. Counts are documented **lower bounds** from each university's own
research-computing documentation (`research_subset.csv`); where the central-vs-priority
split is not disclosed, capacity is shown as unresolved rather than guessed.

Three structural facts are well supported:
- **Central-allocatable is a minority where disclosed.** NYU 232/944; UCSF 88/235; Columbia
  0 general-tier GPUs. Dedicated central clusters that *are* broadly allocatable exist
  (Stanford's Marlowe, 248 GPUs / 500+ accounts; Penn's Betty; Maryland's Zaratan; Wisconsin's
  CHTC) but are modest in size.
- **Idle-sharing is the norm, not the exception** — documented preemptible/scavenge/time-
  limited queues at Cornell, UCLA, UW, Yale, UCSF, Wisconsin, Duke.
- **"Dedicated" ≠ "central."** Even flagship institute clusters are priority-gated: Harvard's
  Kempner (1,144 GPUs) prioritizes institute members, opening to 6,000+ other Harvard
  researchers only when idle; NYU's Torch is ~75% stakeholder-priority.

## What drives it

The condo / stakeholder-priority model is how universities finance GPUs at all: central IT
supplies power, space, networking, and staff; faculty buy accelerators from grants and get
scheduling priority in return. It maximizes total hardware and utilization (via backfill)
but minimizes the centrally-marshalable pool. Large central clusters require lumpy capital
that recurring research budgets don't provide, which is why the broadly-allocatable ones are
recent and typically donor-, vendor-, or one-time-institution-funded.

## Implications — and non-implications

- **Compute-leaderboards by total GPUs are misleading** for coordinated-research capacity.
- **It clarifies why shared federal infrastructure is load-bearing**: for a researcher
  needing a large guaranteed allocation, NSF ACCESS / DOE / NAIRR is often the realistic
  path, because the home institution's central pool is small.
- **Non-implication:** this is *not* evidence of under-investment, and *not* evidence that
  these universities cannot do large-scale work — idle-sharing and national facilities both
  provide routes. We make no claim about realized training-run sizes.

## Limitations

- **Sample:** 20 universities by R&D (unbiased vs. GPU holdings), not a census.
- **Disclosure:** the central-vs-priority split is published by only ~6 of 20; others are
  structurally priority-based but unquantified, and condo totals are lower bounds. We
  therefore report the split as a documented minority *where disclosed*, not as a sample-wide
  percentage.
- **Effective-access (max coordinated job):** documented for few institutions (e.g.,
  Princeton's QOS caps); recorded as unknown elsewhere. The claim that fragmentation limits
  guaranteed scale is **supported but not yet systematically quantified** — it is the
  strongest next target.

## Novelty

Academic-HPC literature has long described the condo model, and Epoch's compute work focuses
on frontier/industry systems and training runs. What appears absent elsewhere is a
primary-source classification of the top-R&D universities by **allocation regime**, with the
central-allocatable-vs-priority distinction made explicit and quantified where disclosed.
That distinction — and the "idle-shared but not guaranteed-at-scale" characterization — is a
modest but genuine contribution to how academic AI-compute capacity is measured.

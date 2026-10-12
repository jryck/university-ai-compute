# Overnight build log — national-allocations / accessible-compute layer

Built autonomously while you slept (night of 2026-10-10 → 11). No blocking questions;
every call documented below. Open `index.html` to see it (new section near the bottom:
**"National allocations & accessible compute"**).

## What I built

The measurable spine of the "accessible compute for meaningful research" idea: a layer
showing which schools' researchers win **DOE leadership-computing allocations** (INCITE /
ALCC on Aurora/Polaris), displayed next to their owned compute so the **access ≠ ownership**
contrast is visible. Plus a clear framing that NSF ACCESS is a free national baseline for all.

## The headline finding

Access does **not** track ownership:
- **Columbia** owns ~36 H100-equivalents but won the **single largest documented Aurora
  allocation (1.85M node-hours)**. **USC** owns ~30, won 925K. Duke/Michigan own ~35, won 200K.
- Meanwhile the GPU-ownership leaders — **NYU, Florida, Texas A&M** — do **not** appear in the
  allocation list at all. They run on owned hardware; others win national time instead.
- A few schools do both (Stanford, Illinois, Princeton own a lot *and* win allocations).

This is a genuinely different lens from everything else in the tool, and it directly supports
the thesis that "owned GPUs" undercounts real research-compute capability for some schools and
overcounts it for others.

## Decisions I made (and why)

1. **Scoped the quantitative metric to the ALCF 2025 award list only.** It's the one complete,
   fully-extractable source (an HTML page listing every Aurora/Polaris project with institution
   and node-hours). I labeled it precisely as such everywhere.
2. **Did NOT fabricate a full census.** OLCF/Frontier, NERSC/Perlmutter, and NSF ACCESS
   allocation lists are locked in PDFs or not published per-institution. Rather than invent
   numbers, I marked the layer "documented highlights, not a census" and stated plainly that
   absence from the table ≠ no national access. This keeps the rigor bar you've set.
3. **Node-hours kept separate from owned-GPU/H100e counts** — different unit, never summed or
   mixed into any existing metric. The allocations layer is its own section, like Tier 3.
4. **Attribution by exact institution name.** PPPL/SLAC etc. awards stay under the national-lab
   (Tier 3) entity, not folded into the university, except where the PI's listed institution is
   the university itself (e.g., Princeton's Burrows award). Princeton's row notes "PPPL adds more."

## Data limitations I hit (worth knowing)

- **PDF award lists won't parse.** The ALCC 2025 and INCITE 2026 fact-sheet PDFs are the
  complete source, but this machine has no PDF text tooling (no poppler, no python PDF lib,
  couldn't install one). So I used the ALCF HTML list + web-search highlights instead.
- **INCITE announcement pages only detail ~13 of ~80 projects.** The rest are in those PDFs.
- **NSF ACCESS has no public per-institution allocation totals** (credit-based, not published
  by school). Captured only as a qualitative baseline note.

## For your review (nothing urgent)

- The allocation figures are ALCF-2025 only. If you want OLCF/Frontier + NERSC included for a
  fuller picture, the clean path is to get those PDFs into a parseable form (or I install PDF
  tooling with your OK) — that's the main thing standing between "documented highlights" and a
  real census.
- Everything is reproducible: `python3 build_data.py` rebuilds `data.json` + `index.html`.

## Suggested next steps

1. **Complete the allocation census** (OLCF/Frontier + NERSC) if we can parse the PDFs — would
   make this the definitive public view of academic national-compute access.
2. **NAIRR** (National AI Research Resource) pilot allocations — newer, AI-specific, possibly
   more web-accessible than INCITE; another access signal worth adding.
3. Return to **owned-vs-rented** (commercial cloud) only if a credible signal emerges — still
   undisclosed as of this build.

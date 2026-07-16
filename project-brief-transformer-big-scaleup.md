# Project brief: transformer-big scale-up

This is the first series in the `ebible-mt` repository, the continuation of the
closed-text Bible machine-translation work begun in `m2m_bible_mt`. That repo
established the from-scratch pipeline and ran the experiments at
transformer-**base** scale on a local RTX 3090. This series re-runs the key
experiments at transformer-**big** scale on remote H100s / an A100, to measure
how much the larger model actually buys.

## Outline

<!-- What should this series find out or produce? One or two sentences. -->

The question: **how much does transformer-big (~210M) improve closed-text
translation over transformer-base (~61M), at matched data and holdouts?** The
headline comparison is the Indo-European from-scratch run — `ie_base`
(transformer-base) versus a new `ie_big` (transformer-big) on identical data,
holdouts and evaluation — with the option to scale further experiments once the
first comparison is in.

## Where the last work left off (`m2m_bible_mt`)

- **`ie_base`** (transformer-base ~61M, Greek source, one-to-many, 34
  Indo-European languages, whole OT withheld from English/German/Hindi, 60k
  steps ≈ 2.1 h on the 3090): held-out whole-OT chrF3 **40.7 / 40.5 / 38.1**
  for eng / deu / hin. This is the base-scale baseline to beat.
- **NLLB many-to-one series**: fine-tuning findings — learning rate dominates
  (3e-4 works, 3e-5 fails); real source proximity is the ceiling. A separate
  track (brings outside knowledge), reported apart from the from-scratch work.
- **vref-source series** (this year): putting only a verse reference + target
  tag on the source, no source text, **failed at base scale** — the model
  could not store verse content in ~61-82M parameters and did not improve with
  25× more training. Published as a negative-result HF dataset. It left one
  open question a bigger model could probe (see below).

## What to scale (for the planning interview to pin down)

- **Primary — `ie_big`**: `ie_base`'s exact config and data at transformer-big
  (6+6, d_model 1024, 16 heads, FFN 4096, ~210M), long schedule on an H100/A100.
  The clean "how much does big help" comparison. This is the anchor deliverable.
- **Optional — vref at big scale**: the vref negative result raised the
  capacity hypothesis (H2) — does ~210M cross the threshold the base model
  never reached? A single `vref_ie_big` run would answer it. Genuinely
  uncertain; worth deciding whether it earns the compute.
- **Optional — scaled data / other families**: the roadmap items (all ~179
  full Bibles; single-family vs diverse at matched scale; many-to-many with
  source+target tags). Likely later series, but flag any that belong here.

## Constraints

- **Compute**: remote H100s (40 GB) via ClearML (queue `jobs_backlog`), and an
  A100 (80 GB) for research runs; the local 3090 for smoke tests and data prep.
  **Prerequisite/risk**: the ClearML agent bootstrap for the remote H100s was
  an open blocker at the end of `m2m_bible_mt` — confirm it works (a git remote
  the agents can clone; rclone-over-WireGuard file transfer) before scheduling
  real runs. The WireGuard split-DNS fix from the last series is recorded.
- **Publishing / licence policy** carries over: a publishable run trains on a
  licence-filtered, shareable-only selection so others can verify it; restricted
  sources (e.g. `deuelbbk`, by-nc-nd) make a run research-only. Run the
  `data-licence-check` skill during planning. Aggregate scores/curves are
  always shareable even when the underlying text is not.

## Data source

Hugging Face dataset `DavidCBaines/ebible_corpus`, as before.

## Reuse from `m2m_bible_mt`

The `samileides` package is the reusable core — data pipeline, composite Greek
source, tokeniser, book-level splits/holdouts, training loop, the probe /
early-stopping / best-checkpoint machinery, generation, evaluation, and the
licence/publishing gates. Decide during planning which modules to copy versus
import, and whether to depend on the old repo or vendor the code in.

## Approach

Run `/interview-and-plan project-brief-transformer-big-scaleup.md` in a new
session to turn this into an agreed `spec.md` and `todo.md`. The design tree to
resolve there: exact transformer-big config and batch/schedule for the H100/A100
memory budget; how the base-vs-big comparison is held fair (same data, holdouts,
seeds, evaluation); whether to include the vref-big capacity test; the ClearML
run/track/transfer workflow; and the shareable-selection for any publishable run.

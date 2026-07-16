# Spec: transformer-big scale-up

**Status: skeleton.** This spec is to be completed by the planning interview
(`/interview-and-plan project-brief-transformer-big-scaleup.md`). The sections
below seed the decisions already fixed and mark what the interview must resolve.
`project-brief-transformer-big-scaleup.md` is the "why"; this becomes the stable
"why and what"; `todo.md` is the living "where we are".

## Goal

Measure how much transformer-big (~210M) improves closed-text Bible translation
over transformer-base (~61M), at matched data and holdouts. Headline
comparison: `ie_base` (base) vs `ie_big` (big) on identical data, holdouts and
evaluation.

## Fixed anchors (decided before the interview)

- **Comparison must be fair**: `ie_big` uses `ie_base`'s exact data, holdouts
  (whole OT withheld from eng/deu/hin), tokeniser scheme and evaluation, so the
  only deliberate change is model size. Baseline to beat: held-out whole-OT
  chrF3 40.7 / 40.5 / 38.1 (eng/deu/hin).
- **Model**: transformer-big — 6+6 layers, d_model 1024, 16 heads, FFN 4096,
  ~210M params, dropout 0.1, label smoothing 0.1.
- **Reuse** the `samileides` package from `m2m_bible_mt` (data pipeline, Greek
  source, tokeniser, splits/holdouts, train, probe/early-stop/best-checkpoint,
  generate, evaluate, licence/publishing gates).
- **Evaluation** unchanged: chrF3 headline (+ chrF3+/++, spBLEU, BLEU); the
  held-out probe curve during training; results always reported beside the
  `ie_base` row.
- **Publishing/licence policy** carries over; publishable runs use a
  shareable-only selection (`data-licence-check` skill).

## To be decided in the interview

- Exact batch size, gradient accumulation, schedule and step budget for the
  H100 (40 GB) / A100 (80 GB) memory envelope; whether gradient checkpointing
  is needed at ~210M.
- Fair-comparison controls: seeds, whether the probe/early-stop regime matches
  `ie_base` or runs to a fixed budget; matched-compute vs matched-steps framing.
- Whether to include the `vref_ie_big` capacity test (the H2 question from the
  vref negative result).
- ClearML workflow: run submission to `jobs_backlog`, experiment tracking,
  git remote for agents, rclone/WireGuard file transfer — and confirming the
  agent bootstrap actually works before real runs.
- Code reuse mechanism: copy modules in vs depend on `m2m_bible_mt`.
- Repository layout and which selections/configs are committed for
  reproducibility.

## Verification

To be completed in the interview. Carry over the `m2m_bible_mt` verification
conventions: alignment tests on known verses, holdout leakage tests, tokeniser
round-trip, an overfit sanity check, a tiny end-to-end run producing every
artefact before spending H100 time, metric checks against known values, and
reproducibility (selection list, config, git commit and seed recorded per run).

## Decisions log

- 2026-07-16 — Repo `ebible-mt` created; first series `transformer-big-scaleup`
  scoped from `m2m_bible_mt`'s roadmap. Series question and fixed anchors above
  agreed; full design to be resolved in the planning interview.

## Maintaining these documents

`spec.md` is the stable "why and what"; `todo.md` (with its "Current status"
block) is the living "where we are". At the end of each working session: update
the status block, tick completed tasks, record new decisions here, and drop run
results into `experiments/` linked from `todo.md`.

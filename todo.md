# Todo

Working list for the `transformer-big-scaleup` series. `spec.md` is the stable
"why and what" (still a skeleton until the planning interview);
`project-brief-transformer-big-scaleup.md` is the brief. Keep the Current status
block current and tick tasks `[x]` as they are completed.

## Current status

- **Done**: repo `ebible-mt` scaffolded 2026-07-16 (git initialised; LICENSE
  Apache-2.0; .gitignore; brief, spec skeleton, this file). Continuation of
  `m2m_bible_mt` (base-scale work).
- **Next**: run **`/interview-and-plan project-brief-transformer-big-scaleup.md`**
  to turn the brief into an agreed spec and task list.
- **Blocked**: remote H100 runs depend on the ClearML agent bootstrap working
  (open blocker at the end of `m2m_bible_mt`) — verify before scheduling.

## First steps (before/at the planning interview)

- [ ] Run `/interview-and-plan project-brief-transformer-big-scaleup.md`.
- [ ] Decide code reuse from `m2m_bible_mt` (copy the `samileides` package vs
      depend on it); bring the pipeline into this repo.
- [ ] Confirm the ClearML agent bootstrap on the remote H100s (git remote to
      clone, rclone/WireGuard transfer, queue `jobs_backlog`).
- [ ] Create the GitHub repo `ebible-mt` under `davidbaines` and push the
      scaffold (gh is installed and authed).

## Series plan (to be refined by the interview)

- [ ] `ie_big`: transformer-big re-run of `ie_base` at matched data/holdouts;
      headline base-vs-big comparison (baseline chrF3 40.7 / 40.5 / 38.1).
- [ ] (Optional) `vref_ie_big`: capacity test of the vref approach at ~210M.
- [ ] Results doc in `experiments/`, always reporting beside the base-scale row.

## Reference

- Prior repo: `../m2m_bible_mt` (base-scale pipeline, results, and the
  `samileides` package to reuse).
- Data: `DavidCBaines/ebible_corpus`.
- Skills: `data-licence-check` (shareable-selection during planning),
  `interview-and-plan`, `restart`.

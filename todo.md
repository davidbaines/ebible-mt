# Todo

Working list for the `transformer-big-scaleup` series. `spec.md` is the stable
"why and what"; `project-brief-transformer-big-scaleup.md` is the brief. Keep
the Current status block current and tick tasks `[x]` as they are completed.

## Current status

- **Done** (2026-07-16): planning interview; licence check (shareable selection
  clean → cc-by-sa-4.0); samileides core vendored, 70 tests + 6 integration
  green; 3090 smokes green; **ClearML round-trip gate passed** — `smoke_big`
  trained on an H100 and its artifacts fetched back (task
  `ceedae3b4b0c4b9483b34bbac4e9a280`). Took five attempts; fixes recorded in
  spec.md "Worker env facts" (docker image, poetry not uv, torch<2.7/cu124).
- **Done** (2026-07-17): **`ie_big` trained and scored** — held-out whole-OT
  chrF3 **48.06 / 48.43 / 43.99** (eng/deu/hin) vs ie_base 40.73/40.51/38.08:
  **+5.9 to +7.9**. 87k steps (early stop; best probe 47.36 @ 85k), 8.04 h on
  one H100. Results: `experiments/ie-big-results.md`. Caveat: the run artifact
  (weights, spBLEU/BLEU) was lost to a full file server (ENOSPC); chrF3
  recovered from the console log; mitigations in place (see results doc).
- **Done** (2026-07-17): **`ie_big_shareable` trained, scored and published**
  — chrF3 **47.01 / 37.03 / 43.82** (eng/deutkw/hin) vs base twin
  41.00/32.69/38.72: **+4.3 to +6.0**. Best probe 42.52 @ 72k, 6.86 h H100;
  trimmed 1.56 GB artifact uploaded and fetched cleanly. Published:
  https://huggingface.co/DavidCBaines/ebible_m2m-ie-big-shareable
  (cc-by-sa-4.0). Results: `experiments/ie-big-shareable-results.md`.
- **Series question answered**: transformer-big + tuned longer schedule is
  worth +4 to +8 chrF3 over base at matched data/holdouts, on both selections.

## Tasks

### 1. Package scaffold
- [x] `pyproject.toml` (samileides 0.2.0, no `tabulate`, `train` extra, pytest
      ini with `integration` marker) + `.python-version`.
- [x] `uv sync --extra train`; `uv run python -c "import samileides"` works.

### 2. Vendor samileides core
- [x] Copy the 24 core modules verbatim into `src/samileides/`.
- [x] Copy tests (17 verbatim + adapted `test_config.py`).
- [x] Copy configs: `holdouts-ie.yaml`, `holdouts-ie-shareable.yaml`,
      `holdouts-smoke.yaml`, `language_families.csv`, `passages.yaml`,
      `families/indo_european.csv`, `configs/experiments/smoke.yaml`.
- [x] Copy selections: `selection-ie.csv`, `selection-ie-shareable.csv`,
      `selection-smoke.csv` into `experiments/`.
- [x] `uv run pytest` green (integration skipped by default).
- [x] One-off `uv run pytest -m integration` to confirm corpus access.

### 3. ClearML diff + experiment configs
- [x] `train.py`: project `ebible-mt`; `--docker-image` flag;
      `set_base_docker(..., docker_arguments="-e PYTHONPATH=src")` before
      `execute_remotely`.
- [x] `fetch.py`: project `ebible-mt`.
- [x] `configs/experiments/ie_big.yaml`, `ie_big_shareable.yaml`,
      `smoke_big.yaml` (see spec for exact settings).
- [x] Adapted `test_config.py` asserts the new configs; pytest green.

### 4. Smokes
- [x] 3090: `smoke.yaml`, then `smoke_big.yaml --generate-after` — probe.csv,
      best checkpoint, generated Jonah scored, cosine LR visible in logs.
- [x] Commit + push (agents clone from GitHub).
- [x] **ClearML round-trip gate**: `smoke_big.yaml --clearml --remote-queue
      jobs_backlog --generate-after`; `python -m samileides.fetch --name
      smoke_big`; artifacts inspected. Iterate `--docker-image` if bootstrap
      fails; escalate with `m2m_bible_mt/experiments/clearml-agent-issue.md`.

### 5. Runs
- [x] `ie_big` on H100 (`--generate-after`); 256×1 OOM'd → 128×2; early stop
      87k, best 85k, 8.04 h. Artifact upload failed (server ENOSPC) — scores
      recovered from console; weights not retained (research-only anyway).
- [x] `experiments/ie-big-results.md` — beside `ie_base` 40.73/40.51/38.08,
      probe curve, schedule-framing caveat.
- [x] `ie_big_shareable` (H100; effective batch 256); fetched (1.56 GB).
- [x] `experiments/ie-big-shareable-results.md` — beside `ie_base_shareable`
      41.00/32.69/38.72.

### 6. Publish + wrap up
- [x] `publish --run checkpoints/ie_big_shareable --dry-run`; staging inspected.
- [x] Pushed to `DavidCBaines/ebible_m2m-ie-big-shareable` (cc-by-sa-4.0);
      both gates passed.
- [ ] Final spec.md decisions-log entries; README; memory note on the outcome.

## Reference

- Prior repo: `../m2m_bible_mt` (frozen base-scale record; donor for the
  vendored code; `experiments/clearml-agent-issue.md` for the agent blocker).
- Data: HF `DavidCBaines/ebible_corpus`.
- ClearML: server `app.sil.hosted.allegro.ai`, project `ebible-mt`, queue
  `jobs_backlog`; WireGuard configs in `../silnlp/scripts/clearml_agent/` and
  `../silnlp/scripts/rclone/`.

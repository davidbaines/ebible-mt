# Todo

Working list for the `transformer-big-scaleup` series. `spec.md` is the stable
"why and what"; `project-brief-transformer-big-scaleup.md` is the brief. Keep
the Current status block current and tick tasks `[x]` as they are completed.

## Current status

- **Done**: repo scaffolded 2026-07-16; planning interview completed 2026-07-16
  (design in `spec.md`, decisions log there); licence check done (shareable
  selection clean → cc-by-sa-4.0).
- **Next**: vendor the samileides core and get the test suite green.
- **Gate**: the ClearML `smoke_big` round trip on `jobs_backlog` must pass
  before any real H100 run is enqueued.

## Tasks

### 1. Package scaffold
- [ ] `pyproject.toml` (samileides 0.2.0, no `tabulate`, `train` extra, pytest
      ini with `integration` marker) + `.python-version`.
- [ ] `uv sync --extra train`; `uv run python -c "import samileides"` works.

### 2. Vendor samileides core
- [ ] Copy the 24 core modules verbatim into `src/samileides/`.
- [ ] Copy tests (17 verbatim + adapted `test_config.py`).
- [ ] Copy configs: `holdouts-ie.yaml`, `holdouts-ie-shareable.yaml`,
      `holdouts-smoke.yaml`, `language_families.csv`, `passages.yaml`,
      `families/indo_european.csv`, `configs/experiments/smoke.yaml`.
- [ ] Copy selections: `selection-ie.csv`, `selection-ie-shareable.csv`,
      `selection-smoke.csv` into `experiments/`.
- [ ] `uv run pytest` green (integration skipped by default).
- [ ] One-off `uv run pytest -m integration` to confirm corpus access.

### 3. ClearML diff + experiment configs
- [ ] `train.py`: project `ebible-mt`; `--docker-image` flag;
      `set_base_docker(..., docker_arguments="-e PYTHONPATH=src")` before
      `execute_remotely`.
- [ ] `fetch.py`: project `ebible-mt`.
- [ ] `configs/experiments/ie_big.yaml`, `ie_big_shareable.yaml`,
      `smoke_big.yaml` (see spec for exact settings).
- [ ] Adapted `test_config.py` asserts the new configs; pytest green.

### 4. Smokes
- [ ] 3090: `smoke.yaml`, then `smoke_big.yaml --generate-after` — probe.csv,
      best checkpoint, generated Jonah scored, cosine LR visible in logs.
- [ ] Commit + push (agents clone from GitHub).
- [ ] **ClearML round-trip gate**: `smoke_big.yaml --clearml --remote-queue
      jobs_backlog --generate-after`; `python -m samileides.fetch --name
      smoke_big`; artifacts inspected. Iterate `--docker-image` if bootstrap
      fails; escalate with `m2m_bible_mt/experiments/clearml-agent-issue.md`.

### 5. Runs
- [ ] `ie_big` on H100 (`--generate-after`); monitor probe curve; OOM
      fallbacks 192×1 then 128×2; fetch; record peak memory, stop step,
      wall time.
- [ ] `experiments/ie-big-results.md` — beside `ie_base` 40.73/40.51/38.08,
      probe curve, schedule-framing caveat.
- [ ] `ie_big_shareable` (H100 or A100; effective batch stays 256); fetch.
- [ ] `experiments/ie-big-shareable-results.md` — beside `ie_base_shareable`
      41.00/32.69/38.72.

### 6. Publish + wrap up
- [ ] `publish --run checkpoints/ie_big_shareable --dry-run`; inspect staging.
- [ ] Push to `DavidCBaines/ebible_m2m-ie-big-shareable` (cc-by-sa-4.0) —
      or scores/write-up/code only if the quality gate fails (record the
      decision in spec.md).
- [ ] Final spec.md decisions-log entries; README; memory note on the outcome.

## Reference

- Prior repo: `../m2m_bible_mt` (frozen base-scale record; donor for the
  vendored code; `experiments/clearml-agent-issue.md` for the agent blocker).
- Data: HF `DavidCBaines/ebible_corpus`.
- ClearML: server `app.sil.hosted.allegro.ai`, project `ebible-mt`, queue
  `jobs_backlog`; WireGuard configs in `../silnlp/scripts/clearml_agent/` and
  `../silnlp/scripts/rclone/`.

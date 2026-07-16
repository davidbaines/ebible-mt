# Spec: transformer-big scale-up

First series in `ebible-mt`, continuing the closed-text Bible MT work from
`m2m_bible_mt`. `project-brief-transformer-big-scaleup.md` is the "why"; this
file is the stable "why and what"; `todo.md` is the living "where we are".

## Goal

Measure how much transformer-big (~210M params) improves closed-text Bible
translation over transformer-base (~61M), at matched data and holdouts.
Headline comparison: `ie_base` (base, from `m2m_bible_mt`) vs `ie_big` (big) on
identical data, holdouts and evaluation. Baseline to beat: held-out whole-OT
chrF3 **40.73 / 40.51 / 38.08** (eng / deu / hin).

**Framing caveat (decided 2026-07-16):** the schedule is *tuned for big*, not
matched. `ie_base` ran 60k steps at effective batch 96 with inverse-sqrt decay
and loss-based early stopping; `ie_big` runs up to 100k steps at effective
batch 256 with cosine decay and probe-based early stopping — roughly 4–5× the
training tokens. Results are therefore reported as **"big + longer tuned
schedule" vs base**, not matched-compute. Scale is the headline variable; the
schedule change is deliberate and documented.

## Runs

| Run | Selection | Languages | Holdouts | Status |
|---|---|---|---|---|
| `ie_big` | `experiments/selection-ie.csv` | 34 IE | `configs/holdouts-ie.yaml` (whole OT from `engbsb`, `deuelbbk`, `hin2017`) | research-only |
| `ie_big_shareable` | `experiments/selection-ie-shareable.csv` | 32 IE | `configs/holdouts-ie-shareable.yaml` (German = `deutkw`) | publishable, cc-by-sa-4.0 |

`vref_ie_big` (the H2 capacity test from the vref negative result) is
**deferred to a later series** — this series is purely the base-vs-big
comparison.

### Licence check (run during planning, 2026-07-16)

- `selection-ie.csv`: 4 non-shareable sources — `deuelbbk` (by-nc-nd), `bel`
  (by-nc), `polubg` (by-nd), `swef` (Unknown) → `ie_big` is research-only;
  aggregate scores/curves are still shareable.
- `selection-ie-shareable.csv`: clean (17 by-sa, 15 Public Domain) →
  propagated model licence **cc-by-sa-4.0**.
- Greek composite sources `grcbrent` (Brenton LXX) and `grc-tisch`
  (Tischendorf NT) are Public Domain.

## Model

Transformer-big, built by `samileides.model.build_model` (Marian, from
scratch): 6 encoder + 6 decoder layers, d_model 1024, 16 heads, FFN 4096,
dropout 0.1, label smoothing 0.1, SentencePiece BPE vocab 32000, shared
embeddings — ~210M params. Source: composite Koine Greek (`greek.py`),
one-to-many with target-language tags, max_len 192.

## Training

- AdamW, peak LR 5e-4, warmup 4000, **cosine decay** to ~0 over a
  **100k-step ceiling** (`lr_scheduler: cosine` is a straight passthrough to HF
  `Seq2SeqTrainingArguments`; if the probe early-stops, the cosine cycle is
  simply truncated — record the stop step).
- bf16, max_grad_norm 1.0, seed 13 (single seed, matching `ie_base`).
- **Batch**: per_device 128, grad-accum 2 → effective 256 sequences (~2.7×
  `ie_base`'s 96), chosen to cut wall time on the H100 at the cost of strict
  comparability. (256×1 OOM'd on the 40 GB H100 at a long batch — the fp32
  log-softmax over the 32k vocab; 128×2 keeps the same effective batch.
  `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` is set on remote tasks
  to curb fragmentation.) Record actual peak memory.
  Note: `max_tokens_per_batch` in the old configs was dead config (never read
  by `train.py`) and is omitted here.
- **Probe machinery** (`probe.py`): held-out chrF3 probe every 1000 steps
  (250 verses/language, batch 64, seed 13); early stop on min_gain 1.0 chrF3
  within patience 20000 steps; best-probe checkpoint kept and reloaded before
  save. (`ie_base` predates this machinery and used loss-based stopping — part
  of the framing caveat above.)

## Evaluation

Unchanged from `m2m_bible_mt`: `generate_holdouts` (beam 5, length_penalty
1.0, max_length 192) over the held-out OT books, scored per (book, language)
with chrF3 headline (+ chrF3+/++, spBLEU, BLEU) against the reference, with
source-copy and best-other-language baselines. Results in
`experiments/ie-big-results.md` / `ie-big-shareable-results.md`, always beside
the base-scale rows (`ie_base` 40.73/40.51/38.08; `ie_base_shareable`
41.00/32.69/38.72 eng/deu/hin).

## Code: vendored samileides core

`samileides` is **vendored core-only** from `m2m_bible_mt` into
`src/samileides` (package name kept, version 0.2.0). The old repo stays frozen
as the base-scale record.

- **Vendored (24 modules, verbatim)**: `__init__ canon config data
  data_pipeline dataset evaluate family fetch generate greek hf_export
  holdouts licensing model pilot preprocess probe publish selection sheets
  splits tokenizer train` — plus `train.py`/`fetch.py` carrying the ClearML
  diff below.
- **Left behind**: `align_score manytomany nllb nllb_m2o publish_nllb rescore
  train_nllb train_nllb_m2o vref` (NLLB track, m2o alignment scoring, vref
  series). No kept module imports them at module level. Three **lazy,
  config-gated imports** of `vref`/`manytomany` remain in `data_pipeline.py`,
  `train.py` and `generate.py`; they only execute for vref/many-to-many
  configs, which this series never sets. Files are kept byte-identical to the
  donor so future diffs stay trivial.
- **Tests**: donor tests vendored verbatim except `test_config.py` (adapted to
  the new configs) and the dropped `test_manytomany/test_vref/
  test_publish_nllb`. `pyproject.toml` drops the unused `tabulate` dependency.

## Infrastructure (ClearML)

- Server `app.sil.hosted.allegro.ai`, project **`ebible-mt`**, queue
  **`jobs_backlog`** (H100 40 GB workers); A100 80 GB as the second target if
  the first run shows promise; local 3090 (24 GB) for smokes and data prep.
- `train.py --clearml --remote-queue jobs_backlog` uses
  `Task.execute_remotely` (captures the git commit; **commit + push before
  enqueueing** — repo is public at `github.com/davidbaines/ebible-mt` so
  agents can clone).
- **Agent bootstrap workaround**: the queue's default image
  (`python:3.12-bullseye`) breaks agent bootstrap (clearml-agent 2.0.4 +
  setuptools≥81 → `pkg_resources` ImportError; see
  `m2m_bible_mt/experiments/clearml-agent-issue.md`). Remote tasks therefore
  set a base docker image (default
  `pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime`, overridable via
  `--docker-image`) with `PYTHONPATH=src` so the src-layout package imports in
  the agent's clone without installation.
- **Worker env facts** (learned closing the gate, 2026-07-16): the agents
  resolve dependencies with **poetry**, which ignores `[tool.uv]` index pins
  and skips optional extras — hence the train stack is a *default dependency
  group* and the CUDA constraint lives in the version bound
  (`torch>=2.4,<2.7`: the workers' driver supports exactly CUDA 12.4, and
  torch 2.6.0 is the last PyPI release built on cu124; cu130/cu126 wheels fail
  CUDA init there). Locally, uv additionally pins the cu124 wheel index.
- Artifacts: the run dir is zipped and uploaded on completion
  (`_upload_artifacts`); retrieved with `python -m samileides.fetch --name
  <run>`. Generation + scoring run on the worker via `--generate-after`.
- **Gate**: a `smoke_big` round trip on `jobs_backlog` must complete (train →
  artifact upload → fetch) before any real H100 hours are spent.
- **Plan B** if ClearML stays broken: both runs fit the 3090 at per_device 64 /
  grad_accum 4 (effective 256) with gradient checkpointing, ~1.5–2 days each.

## Publishing

`ie_big_shareable` publishes to HF **`DavidCBaines/ebible_m2m-ie-big-shareable`**
(mirrors the base twin's naming) under cc-by-sa-4.0, via `samileides.publish`
(`--dry-run` first; quality gate: every held-out book beats source-copy chrF3
and each language beats the best other-language baseline; licence gate
re-checks the selection). If quality is very poor, omit the model weights but
still publish the write-up, scores and code. `ie_big` is research-only:
aggregate scores and curves only, never the model or generated text.

## Verification

- `uv run pytest` green after vendoring (integration tests skipped by
  default); one-off `pytest -m integration` confirms corpus access.
- Adapted `test_config.py` asserts the ie_big / ie_big_shareable / smoke_big
  dims, cosine scheduler, batch and probe settings.
- `smoke.yaml` (tiny model) then `smoke_big.yaml` (full big dims, vocab 4000,
  400 steps) on the 3090 prove the exact big-model path — build, bf16, cosine,
  probe early-stop/best-checkpoint, generation — in minutes.
- The ClearML round-trip smoke proves clone → docker bootstrap → train →
  artifact upload → fetch before real runs.
- `assert_no_leakage` runs inside training; publish `--dry-run` staging is
  inspected before any Hub push.
- Reproducibility per run: selection CSV, config YAML, git commit and seed
  recorded; results markdown quotes them.

## Decisions log

- 2026-07-16 — Repo `ebible-mt` created; series scoped from `m2m_bible_mt`'s
  roadmap.
- 2026-07-16 — Planning interview: vendor samileides core-only; run both twins
  (`ie_big`, `ie_big_shareable`); defer `vref_ie_big`; schedule tuned for big
  (5e-4 peak, cosine over 100k, probe stopping) rather than matched;
  effective batch scaled to 256 (2.7×) for wall time; single seed 13; H100
  via ClearML first, A100 second if promising; publish the shareable model
  under the `ebible_m2m-*` naming unless quality is very poor (then scores +
  code only). Licence check done: shareable selection clean → cc-by-sa-4.0.

## Maintaining these documents

`spec.md` is the stable "why and what"; `todo.md` (with its "Current status"
block) is the living "where we are". At the end of each working session:
update the status block, tick completed tasks, record new decisions here, and
drop run results into `experiments/` linked from `todo.md`.

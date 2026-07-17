# Results: transformer-big shareable run `ie_big_shareable`

Publishable twin of `ie_big`, trained 2026-07-17 on ClearML queue
`jobs_backlog` (task `3ef0001678b94cdbb0478174009f55ca`, git commit
`ef0c7cc`). Baseline: `../m2m_bible_mt/experiments/ie-base-shareable-results.md`.

## Setup

- Identical to `ie_big` (see `ie-big-results.md`) except the licence-clean
  32-language selection (`experiments/selection-ie-shareable.csv`), with
  Public-Domain `deutkw` replacing by-nc-nd `deuelbbk` as the German holdout.
  Every source is Public Domain or by-sa → the model publishes under
  **cc-by-sa-4.0**.
- Model: transformer-big, 209.5M parameters; 684,605 train pairs.
- Training: cosine from 5e-4 over a 100k ceiling, effective batch 256
  (128×2), bf16, seed 13. Probe early stop; best-probe checkpoint at
  **72k steps** (macro-chrF3 42.52) used for generation. 28.0 epochs,
  train runtime 6.86 h on one H100 40 GB. Artifact upload (1.56 GB, minus
  intermediate checkpoints) succeeded; full metrics retained.

## Scores

Verse-weighted over each language's generated Old Testament (36 books,
~20,830 scored verses per language), beside the base-scale twin.

| Language | chrF3 (big) | chrF3 (base) | Δ | spBLEU | BLEU | source-copy | best-other |
|---|---|---|---|---|---|---|---|
| English | **47.01** | 41.00 | +6.01 | 26.42 | 25.23 | 0.34 | 19.57 |
| German (deutkw) | **37.03** | 32.69 | +4.34 | 12.58 | 11.00 | 0.32 | 21.22 |
| Hindi | **43.82** | 38.72 | +5.10 | 26.25 | 20.71 | 0.25 | 32.79 |

The pattern mirrors the research pair (`ie_big` vs `ie_base`: +5.9 to +7.9):
transformer-big with the tuned longer schedule is worth **+4.3 to +6.0
chrF3** on the licence-clean selection. German remains the lowest scorer, as
at base scale — `deutkw` is an archaic (1878) translation, so reference
divergence, not model quality, drives the gap (the research twin's modern
German reference scores 48.43 under the same regime.)

Every held-out book beats both the source-copy and best-other-language
baselines; the weakest books are the usual poetic ones (worst: German Psalms
30.71 vs copy 0.33).

The same framing caveat as `ie_big` applies: base ran 60k steps at effective
batch 96 with inverse-sqrt decay; this is "big + longer tuned schedule".

## Publication

Model, tokenizer, probe curve, generated books, metrics and sample sheets:
`checkpoints/ie_big_shareable/`. Published to Hugging Face as
**`DavidCBaines/ebible_m2m-ie-big-shareable`** (cc-by-sa-4.0) via
`samileides.publish` after the licence and quality gates.

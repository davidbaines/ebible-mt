# Results: transformer-big Indo-European run `ie_big`

First H100 run of the series, 2026-07-17, on ClearML queue `jobs_backlog`
(task `f0a4776fa1cb4bd0ae4a03cef4df90c4`, git commit `62d2669`). See `spec.md`
for the design; baseline numbers from
`../m2m_bible_mt/experiments/ie-base-results.md`.

## Setup

- Data, source, holdouts and evaluation identical to `ie_base`: composite
  Koine Greek → 34 Indo-European languages, whole OT withheld from English
  (`engbsb`), German (`deuelbbk`) and Hindi (`hin2017`); SentencePiece BPE
  32k; generation beam 5, hard length cap 192, no truncations.
- Model: transformer-big, **209.5M parameters** (vs 60.7M).
- Training: cosine decay from peak 5e-4 (warmup 4000) over a 100k-step
  ceiling; effective batch 256 sequences (128 per device × grad-accum 2,
  ~2.7× ie_base's 96); bf16; seed 13. Probe-driven early stopping fired at
  **87k steps** (<1.0 macro-chrF3 gain over 20k steps); best-probe checkpoint
  at **85k steps** (macro-chrF3 47.36) used for generation. 29.3 epochs,
  train runtime 8.04 h on one H100 40 GB.
- **Framing caveat**: the schedule was tuned for big, not matched — `ie_base`
  ran 60k steps at effective batch 96 with inverse-sqrt decay and loss-based
  stopping. This comparison is **"big + longer tuned schedule" vs base**
  (~6× the training tokens), with scale as the headline variable.
- Batch note: 256×1 OOM'd on the 40 GB H100 (fp32 log-softmax over the 32k
  vocab on a long batch); 128×2 keeps the same effective batch.

## Scores

Verse-weighted over each language's generated Old Testament (36 books,
20,833 scored verses per language — the same evaluation set as `ie_base`).
Baselines: source-copy returns the Greek source verse unchanged; best-other
copies the closest other-language translation (verse-weighted over each
book's best candidate).

| Language | chrF3 (ie_big) | chrF3 (ie_base) | Δ | source-copy | best-other |
|---|---|---|---|---|---|
| English | **48.06** | 40.73 | +7.33 | 0.34 | 19.49 |
| German | **48.43** | 40.51 | +7.92 | 0.33 | 20.62 |
| Hindi | **43.99** | 38.08 | +5.91 | 0.25 | 32.79 |

Transformer-big improves held-out whole-OT chrF3 by **+5.9 to +7.9 points**
across all three holdout languages. Every one of the 108 held-out books beats
both baselines; the weakest books are the same ones as at base scale (Psalms,
Job, Jeremiah — poetic language and versification differences).

The probe curve rose smoothly throughout — no instability under cosine decay:
macro-chrF3 11.6 @ 1k → 30.9 @ 8k → 40.9 @ 30k → 45.5 @ 57k → 47.4 @ 85k,
with the seen-verse probe reaching 78.0 (memorisation headroom well above the
held-out transfer curve).

## Per-book chrF3

| Book | Verses | English | German | Hindi |
|---|---|---|---|---|
| 1CH | 914 | 53.35 | 51.16 | 47.86 |
| 1KI | 730 | 48.83 | 50.50 | 45.22 |
| 1SA | 769 | 50.91 | 52.73 | 49.27 |
| 2CH | 818 | 52.74 | 53.50 | 47.92 |
| 2KI | 718 | 53.08 | 54.66 | 49.81 |
| 2SA | 692 | 51.97 | 53.49 | 48.73 |
| AMO | 146 | 47.83 | 49.21 | 45.16 |
| DEU | 956 | 50.63 | 52.66 | 44.01 |
| ECC | 221 | 45.50 | 47.03 | 42.90 |
| EXO | 1158 | 48.51 | 49.17 | 45.02 |
| EZK | 1260 | 48.74 | 48.35 | 42.29 |
| EZR | 280 | 53.00 | 52.74 | 47.54 |
| GEN | 1530 | 52.97 | 55.94 | 49.50 |
| HAB | 56 | 44.37 | 42.22 | 40.00 |
| HAG | 38 | 53.87 | 52.54 | 46.06 |
| HOS | 193 | 46.89 | 46.84 | 40.08 |
| ISA | 1287 | 47.79 | 46.64 | 41.01 |
| JDG | 618 | 50.78 | 53.25 | 48.71 |
| JER | 1117 | 43.39 | 42.91 | 37.34 |
| JOB | 1060 | 41.24 | 40.97 | 40.42 |
| JOL | 68 | 50.21 | 48.82 | 41.59 |
| JON | 47 | 43.34 | 48.59 | 44.36 |
| JOS | 643 | 50.26 | 50.35 | 45.06 |
| LAM | 150 | 46.95 | 47.51 | 38.75 |
| LEV | 852 | 44.61 | 47.60 | 44.47 |
| MAL | 55 | 51.63 | 51.57 | 44.96 |
| MIC | 104 | 48.93 | 48.09 | 40.86 |
| NAM | 46 | 41.31 | 42.23 | 36.58 |
| NUM | 1274 | 46.95 | 47.82 | 44.09 |
| OBA | 21 | 49.34 | 48.36 | 41.70 |
| PRO | 847 | 44.92 | 43.13 | 39.68 |
| PSA | 1704 | 39.92 | 37.03 | 37.80 |
| RUT | 85 | 51.17 | 54.11 | 48.64 |
| SNG | 116 | 44.72 | 48.13 | 41.67 |
| ZEC | 207 | 53.56 | 53.04 | 43.82 |
| ZEP | 53 | 50.70 | 50.69 | 41.65 |

## Artifact-loss caveat

The 5.95 GB run artifact (model weights, per-book `metrics.csv` with
spBLEU/BLEU, sample sheets) failed to upload — the ClearML file server ran
out of disk space (`ENOSPC`). All chrF3 numbers above were recovered from the
task's console log and scalar streams; spBLEU/BLEU and the qualitative sample
sheets are not available for this run, and the trained weights were not
retained. This run is research-only (its selection includes `deuelbbk`
by-nc-nd), so the weights would never have been published; a rerun costs
~8 H100-hours if they are ever needed. Mitigations applied for subsequent
runs: artifact upload now excludes intermediate trainer checkpoints (~4× size
reduction), and 5.1 GB of smoke-test artifacts were deleted from the server.

## Status

The headline question of the series is answered: at matched data and
holdouts, transformer-big with a tuned longer schedule beats transformer-base
by +5.9 to +7.9 chrF3 on held-out whole-OT translation. The publishable twin
`ie_big_shareable` runs next.

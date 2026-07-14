# Claudette-1 — your own language model, from scratch

A complete, working GPT-style language model in ~350 lines of commented Python. Same
architecture family as Claude, GPT-4, and Llama — a decoder-only transformer — at about
one-millionth the scale. Trained from randomly initialized weights on the Federalist
Papers and the U.S. Constitution.

This is not a wrapper around an API. The weights start as noise and learn English (in
the voice of Hamilton and Madison) from nothing, on your CPU, in ~20 minutes.

## Run it

```bash
pip install torch
python3 prepare_data.py   # downloads + cleans the corpus (public domain)
python3 train.py          # pretrains from scratch; checkpoints to checkpoints/
python3 generate.py --prompt "To the People of the State of New York" --tokens 400
```

## What each file teaches

| File | What it is |
|---|---|
| `model.py` | The transformer itself: attention, MLPs, embeddings, the sampling loop. Read this to understand what "a GPT" literally is. |
| `prepare_data.py` | Data collection & cleaning — at frontier scale, this step is a huge share of the work. |
| `train.py` | Pretraining: next-token prediction, cross-entropy loss, AdamW, warmup + cosine LR decay, train/val split. The exact recipe frontier labs use, minus ~30,000 GPUs. |
| `generate.py` | Inference: autoregressive sampling with temperature and top-k. |

## The scale gap, concretely

| | Claudette-1 | Frontier models (order of magnitude) |
|---|---|---|
| Parameters | ~820 thousand | ~1 trillion |
| Training tokens | ~1.2 million (chars) | ~15+ trillion (subwords) |
| Context window | 128 tokens | 200,000+ |
| Hardware | 4 CPU cores | tens of thousands of GPUs |
| Training time | ~20 minutes | months |
| Cost | $0 | $100M+ |

And after pretraining, frontier models go through instruction tuning and reinforcement
learning from human feedback — that's what turns "a model that continues text" into
"an assistant that answers you." Claudette-1 stops at pretraining, so it continues
text: prompt it with a phrase and it writes onward in 1787 constitutional English.

It will produce period-appropriate, grammatical-ish, mostly meaningless prose. That's
the honest output of a million-parameter model — and watching it go from random
characters to structured English in 20 minutes is the whole lesson.

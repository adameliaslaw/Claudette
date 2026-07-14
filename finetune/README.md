# Fine-tuning: your own *useful* model

Claudette-1 (in `../claudette-1/`) teaches you how LLMs work. This directory is the
practical path: take a strong open-weight model that already speaks fluent English and
reasons decently, and fine-tune it on **your** writing so it drafts like you — a model
you own, running on hardware you control, with client data that never leaves it.

This is called **LoRA fine-tuning** (Low-Rank Adaptation): instead of retraining all
~8 billion weights, you train small adapter matrices on top of them — cheap enough for
one rented GPU or a good desktop, while the base model's general intelligence stays
intact.

## Honest expectations

- A fine-tuned 7–8B model will genuinely absorb your **tone, formats, and phrasing**
  (letters, memos, clause style). That's what fine-tuning is good at.
- It will **not** absorb reliable legal knowledge, and it will not reach frontier-model
  reasoning quality. Facts and case law belong in retrieval (your research tools), not
  in the weights.
- Anything it drafts still gets attorney review — same rule as everything else.

## What you need

| Route | Hardware | Cost | Notes |
|---|---|---|---|
| Rented GPU | RunPod / Lambda / Vast.ai, one 24 GB GPU (e.g. A10G, RTX 4090) | ~$0.30–0.80/hr, a run is 1–4 hrs | Easiest. Destroy the instance after; adapters download in seconds. |
| Your own machine | Any 24 GB NVIDIA GPU | electricity | Most private option. |
| Apple Silicon Mac | M-series, 32 GB+ RAM | free | Use [MLX](https://github.com/ml-explore/mlx-examples/tree/main/llms) instead of these scripts (`mlx_lm.lora`) — same data format. |

**Confidentiality note:** this pipeline is designed so client data stays on the training
machine. If you rent a GPU, use a provider you're comfortable with, transfer data over
SSH, and wipe the instance after — or keep truly sensitive matters out of the training
set entirely and tune only on style/format examples.

## Base model

Default is `Qwen/Qwen2.5-7B-Instruct` (Apache 2.0 — no usage restrictions, strong
quality). `meta-llama/Llama-3.1-8B-Instruct` and `mistralai/Mistral-7B-Instruct-v0.3`
are fine substitutes; pass `--base-model` to any script.

## The pipeline

```bash
pip install -r requirements.txt

# 1. Build training data from your documents + curated Q&A pairs
python3 prepare_data.py --docs ~/my-writing/ --pairs pairs.jsonl --out data/

# 2. Train (on the GPU machine)
python3 train_lora.py --data data/ --out adapters/claudette-ft

# 3. Merge the adapter into the base model and export
python3 merge_and_export.py --adapter adapters/claudette-ft --out merged/
```

Then run it locally with [Ollama](https://ollama.com) (`merge_and_export.py` prints the
exact GGUF conversion + `ollama create claudette` steps) — after which
`ollama run claudette` gives you your own private model in a terminal, or behind any
OpenAI-compatible app.

## Training data is everything

The model becomes whatever `data/train.jsonl` shows it. Two kinds of examples, and
quality beats quantity — 200 excellent pairs outperform 5,000 sloppy ones:

1. **Curated instruction pairs** (`pairs.jsonl`) — the high-value signal. Each line:
   `{"prompt": "Draft a demand letter for ...", "response": "<the letter as you would
   actually write it>"}`. Best source: real (redacted) instructions you'd give and
   final documents you actually sent. Start with 50–200; add more over time.
2. **Raw writing** (`--docs`) — your memos, letters, briefs as `.txt`/`.md` files.
   `prepare_data.py` chunks these into continuation examples that teach tone and
   rhythm. Useful supplement, weaker signal than pairs.

Redact before training: names, addresses, case numbers. `prepare_data.py --scrub`
applies a basic regex pass, but review the output yourself — you know what's
identifying; a regex doesn't.

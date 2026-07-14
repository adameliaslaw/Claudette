"""Train Claudette-1 from scratch.

Usage:
    python3 prepare_data.py          # once, to build data/corpus.txt
    python3 train.py                 # ~20-40 min on a laptop CPU

This is genuine pretraining — the same procedure that produces every frontier
model: show the network text, ask it to predict each next token, nudge the
weights toward being less wrong, repeat. The only differences from Claude's
pretraining are scale (a million-fold) and what happens afterwards
(instruction tuning and RLHF, which turn a text predictor into an assistant).
"""

import argparse
import math
import pathlib
import time

import torch

from model import GPT, Config

HERE = pathlib.Path(__file__).parent


def get_args():
    p = argparse.ArgumentParser()
    p.add_argument("--max-iters", type=int, default=3000)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--eval-every", type=int, default=250)
    p.add_argument("--sample-every", type=int, default=1000)
    p.add_argument("--out", type=str, default=str(HERE / "checkpoints" / "claudette1.pt"))
    return p.parse_args()


def main():
    args = get_args()
    torch.manual_seed(1787)  # the year the corpus was written

    # ------- tokenize: one token per character -------
    corpus_path = HERE / "data" / "corpus.txt"
    if not corpus_path.exists():
        raise SystemExit("run prepare_data.py first to build data/corpus.txt")
    text = corpus_path.read_text(encoding="utf-8")
    chars = sorted(set(text))
    stoi = {ch: i for i, ch in enumerate(chars)}
    data = torch.tensor([stoi[c] for c in text], dtype=torch.long)

    # hold out the last 5% as validation: text the model never trains on,
    # so val loss measures generalization rather than memorization
    split = int(0.95 * len(data))
    train_data, val_data = data[:split], data[split:]
    print(f"corpus: {len(data):,} tokens | train {len(train_data):,} | val {len(val_data):,} | vocab {len(chars)}")

    config = Config(vocab_size=len(chars))
    model = GPT(config)
    print(f"model: {model.num_params():,} parameters "
          f"({config.n_layer} layers, {config.n_head} heads, {config.n_embd} wide)")

    def get_batch(source):
        ix = torch.randint(len(source) - config.block_size - 1, (args.batch_size,))
        x = torch.stack([source[i:i + config.block_size] for i in ix])
        y = torch.stack([source[i + 1:i + 1 + config.block_size] for i in ix])
        return x, y

    @torch.no_grad()
    def eval_loss(source, iters=40):
        model.eval()
        losses = torch.zeros(iters)
        for k in range(iters):
            x, y = get_batch(source)
            _, loss = model(x, y)
            losses[k] = loss.item()
        model.train()
        return losses.mean().item()

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, betas=(0.9, 0.95), weight_decay=0.1)

    def lr_at(it):  # short warmup, then cosine decay to 10% — standard LLM schedule
        warmup = 100
        if it < warmup:
            return args.lr * (it + 1) / warmup
        progress = (it - warmup) / max(1, args.max_iters - warmup)
        return args.lr * (0.1 + 0.45 * (1 + math.cos(math.pi * progress)))

    ckpt_path = pathlib.Path(args.out)
    ckpt_path.parent.mkdir(exist_ok=True)
    log_path = ckpt_path.parent / "train_log.tsv"
    log = open(log_path, "w")
    log.write("iter\ttrain_loss\tval_loss\telapsed_s\n")

    best_val = float("inf")
    t0 = time.time()
    model.train()
    for it in range(args.max_iters + 1):
        for group in optimizer.param_groups:
            group["lr"] = lr_at(it)

        if it % args.eval_every == 0:
            tr, va = eval_loss(train_data), eval_loss(val_data)
            elapsed = time.time() - t0
            print(f"iter {it:5d} | train {tr:.4f} | val {va:.4f} | {elapsed:6.0f}s", flush=True)
            log.write(f"{it}\t{tr:.4f}\t{va:.4f}\t{elapsed:.0f}\n")
            log.flush()
            if va < best_val:
                best_val = va
                torch.save(
                    {"model": model.state_dict(), "config": vars(config) | {"vocab_size": len(chars)},
                     "chars": chars, "iter": it, "val_loss": va},
                    ckpt_path,
                )

        if it % args.sample_every == 0 and it > 0:
            seed = torch.tensor([[stoi["\n"]]], dtype=torch.long)
            sample = model.generate(seed, max_new_tokens=200)[0].tolist()
            print("--- sample ---\n" + "".join(chars[i] for i in sample) + "\n--------------", flush=True)
            model.train()

        x, y = get_batch(train_data)
        _, loss = model(x, y)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)  # keeps training stable
        optimizer.step()

    log.close()
    print(f"done. best val loss {best_val:.4f}; checkpoint at {ckpt_path}")


if __name__ == "__main__":
    main()

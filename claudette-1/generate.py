"""Talk to Claudette-1: generate text from a trained checkpoint.

Usage:
    python3 generate.py --prompt "To the People of the State of New York" --tokens 400
"""

import argparse
import pathlib

import torch

from model import GPT, Config

HERE = pathlib.Path(__file__).parent


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", default=str(HERE / "checkpoints" / "claudette1.pt"))
    p.add_argument("--prompt", default="\n")
    p.add_argument("--tokens", type=int, default=400)
    p.add_argument("--temperature", type=float, default=0.8,
                   help="lower = more conservative, higher = more adventurous")
    p.add_argument("--top-k", type=int, default=40)
    args = p.parse_args()

    ckpt = torch.load(args.checkpoint, map_location="cpu")
    chars = ckpt["chars"]
    stoi = {ch: i for i, ch in enumerate(chars)}

    model = GPT(Config(**ckpt["config"]))
    model.load_state_dict(ckpt["model"])
    model.eval()

    unknown = [c for c in args.prompt if c not in stoi]
    if unknown:
        raise SystemExit(f"prompt contains characters not in the training vocabulary: {unknown!r}")
    idx = torch.tensor([[stoi[c] for c in args.prompt]], dtype=torch.long)

    out = model.generate(idx, max_new_tokens=args.tokens,
                         temperature=args.temperature, top_k=args.top_k)
    print("".join(chars[i] for i in out[0].tolist()))


if __name__ == "__main__":
    main()

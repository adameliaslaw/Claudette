"""Build a fine-tuning dataset from your documents and curated Q&A pairs.

Two input kinds:
  --pairs pairs.jsonl   lines of {"prompt": "...", "response": "..."}  (high-value)
  --docs  <dir>         .txt/.md files of your own writing              (style signal)

Output: data/train.jsonl and data/val.jsonl in chat-messages format, ready for
train_lora.py (and compatible with mlx_lm and most other SFT tooling).

Run with --scrub for a basic redaction pass — then REVIEW THE OUTPUT YOURSELF.
A regex cannot know what identifies your client; you can.
"""

import argparse
import json
import pathlib
import random
import re

SYSTEM_PROMPT = (
    "You are Claudette, the drafting assistant for Adam Elias Law. "
    "Write in the firm's voice: clear, direct, professionally warm. "
    "Your output is a draft for attorney review, never final legal advice."
)

# crude redaction: emails, phone numbers, SSNs, street addresses, case numbers
SCRUB_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[EMAIL]"),
    (re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[PHONE]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
    (re.compile(r"\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b"), "[ADDRESS]"),
    (re.compile(r"\b(?:Case|Docket|Matter)\s*(?:No\.?|Number|#)\s*[\w:-]+\b", re.I), "[CASE-NO]"),
]


def scrub(text: str) -> str:
    for pattern, repl in SCRUB_PATTERNS:
        text = pattern.sub(repl, text)
    return text


def chunk_document(text: str, target_chars: int = 3000) -> list[str]:
    """Split a document on paragraph boundaries into roughly target-sized chunks."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current = [], ""
    for p in paragraphs:
        if current and len(current) + len(p) > target_chars:
            chunks.append(current)
            current = p
        else:
            current = f"{current}\n\n{p}" if current else p
    if current:
        chunks.append(current)
    return [c for c in chunks if len(c) > 400]  # drop fragments too short to teach anything


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=pathlib.Path, help="JSONL of {prompt, response} pairs")
    ap.add_argument("--docs", type=pathlib.Path, help="directory of .txt/.md writing samples")
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("data"))
    ap.add_argument("--scrub", action="store_true", help="basic PII redaction pass")
    ap.add_argument("--val-fraction", type=float, default=0.05)
    args = ap.parse_args()

    if not args.pairs and not args.docs:
        raise SystemExit("provide --pairs and/or --docs")

    examples = []

    if args.pairs:
        for line in args.pairs.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            prompt, response = row["prompt"], row["response"]
            if args.scrub:
                prompt, response = scrub(prompt), scrub(response)
            examples.append(
                {"messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": response},
                ]}
            )
        print(f"pairs: {len(examples)} instruction examples")

    if args.docs:
        n_chunks = 0
        for path in sorted(args.docs.rglob("*")):
            if path.suffix.lower() not in {".txt", ".md"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if args.scrub:
                text = scrub(text)
            for chunk in chunk_document(text):
                # continuation-style: teach the voice by having the model
                # reproduce your writing from a generic drafting instruction
                examples.append(
                    {"messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": "Continue drafting in the firm's voice."},
                        {"role": "assistant", "content": chunk},
                    ]}
                )
                n_chunks += 1
        print(f"docs: {n_chunks} writing-sample chunks")

    if not examples:
        raise SystemExit("no examples produced — check your inputs")

    random.seed(7)
    random.shuffle(examples)
    n_val = max(1, int(len(examples) * args.val_fraction))
    val, train = examples[:n_val], examples[n_val:]

    args.out.mkdir(parents=True, exist_ok=True)
    for name, rows in (("train.jsonl", train), ("val.jsonl", val)):
        with open(args.out / name, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(train)} train / {len(val)} val examples to {args.out}/")
    if args.scrub:
        print("NOTE: --scrub is a first pass only. Read the output files and redact what it missed.")


if __name__ == "__main__":
    main()

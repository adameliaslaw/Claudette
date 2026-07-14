"""Merge the trained LoRA adapter into the base model and print export steps.

    python3 merge_and_export.py --adapter adapters/claudette-ft --out merged/

The merged model is a standard Hugging Face model directory. To run it
locally with Ollama, convert to GGUF (steps printed at the end).
"""

import argparse
import pathlib

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-model", default="Qwen/Qwen2.5-7B-Instruct")
    ap.add_argument("--adapter", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("merged"))
    args = ap.parse_args()

    print(f"loading base model {args.base_model} (full precision — needs RAM, not GPU)")
    base = AutoModelForCausalLM.from_pretrained(args.base_model, torch_dtype=torch.bfloat16)
    model = PeftModel.from_pretrained(base, str(args.adapter))
    merged = model.merge_and_unload()

    args.out.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(str(args.out))
    AutoTokenizer.from_pretrained(args.base_model).save_pretrained(str(args.out))
    print(f"merged model saved to {args.out}/")

    print(
        f"""
To run locally with Ollama:

  git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp
  pip install -r requirements.txt
  python3 convert_hf_to_gguf.py {args.out.resolve()} --outfile claudette-ft.gguf --outtype q4_k_m

  cat > Modelfile <<'EOF'
FROM ./claudette-ft.gguf
SYSTEM You are Claudette, the drafting assistant for Adam Elias Law. Your output is a draft for attorney review, never final legal advice.
EOF

  ollama create claudette -f Modelfile
  ollama run claudette
"""
    )


if __name__ == "__main__":
    main()

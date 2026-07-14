"""QLoRA fine-tune of an open-weight chat model on your data.

Run on a machine with a 24 GB NVIDIA GPU (rented or owned):

    python3 train_lora.py --data data/ --out adapters/claudette-ft

The base model loads in 4-bit (QLoRA), so an 8B model fits comfortably in
24 GB. Only the LoRA adapter weights train — a few tens of MB — which is why
this costs dollars instead of the base model's millions.

On Apple Silicon, use mlx_lm.lora with the same data files instead.
"""

import argparse
import pathlib

import torch
from datasets import load_dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-model", default="Qwen/Qwen2.5-7B-Instruct")
    ap.add_argument("--data", type=pathlib.Path, default=pathlib.Path("data"))
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("adapters/claudette-ft"))
    ap.add_argument("--epochs", type=float, default=3.0)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--max-seq-len", type=int, default=4096)
    args = ap.parse_args()

    dataset = load_dataset(
        "json",
        data_files={"train": str(args.data / "train.jsonl"), "validation": str(args.data / "val.jsonl")},
    )
    print(f"train examples: {len(dataset['train'])}, val: {len(dataset['validation'])}")

    tokenizer = AutoTokenizer.from_pretrained(args.base_model)

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        ),
        device_map="auto",
    )

    lora = LoraConfig(
        r=16,                 # adapter rank: capacity of what can be learned
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        # adapt every attention and MLP projection — standard for style transfer
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )

    config = SFTConfig(
        output_dir=str(args.out),
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,   # effective batch of 16
        gradient_checkpointing=True,
        bf16=True,
        max_length=args.max_seq_len,
        logging_steps=5,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        args=config,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        processing_class=tokenizer,
        peft_config=lora,
    )
    trainer.train()
    trainer.save_model(str(args.out))
    print(f"adapter saved to {args.out} — next: merge_and_export.py")


if __name__ == "__main__":
    main()

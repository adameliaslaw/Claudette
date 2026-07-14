# Your Own AI on Your Own Mac — the complete beginner's walkthrough

This guide takes you from a brand-new Mac to a private AI model, trained on your own
writing, running entirely on your desk. No prior technical experience assumed. Every
command is copy-paste. Nothing you do here can break your Mac.

**Why this is worth an afternoon:** everything happens on your machine. Your documents,
your clients' matters, your drafts — none of it ever leaves your Mac. No subscription,
no cloud, no vendor. The model you end up with is a file on your hard drive that you
own, the same way you own a Word document.

**What you need:**
- A Mac with an Apple Silicon chip (any M1, M2, M3, or M4 — every Mac sold since 2021)
- Ideally 16 GB of memory or more (check:  → About This Mac). 8 GB works with the
  smaller model noted in Step 4.
- About 10 GB of free disk space and an hour, most of it waiting.

---

## Part 1 — Meet the Terminal (5 minutes)

Terminal is a Mac app where you type instructions instead of clicking. That's the whole
trick. Open it: press **⌘ + Space**, type `terminal`, press **Return**. A plain window
appears with a blinking cursor.

Three rules for this entire guide:

1. **Copy the whole command, paste it, press Return.** One command at a time.
2. **Wait for the prompt to come back.** When the cursor sits after something like
   `adam@Adams-MacBook ~ %`, the command is done and it's ready for the next one.
3. **Errors are normal and fixable.** If something red or alarming appears, don't
   close the window — copy the message and check the Troubleshooting section at the
   bottom (or paste it to Claude and ask).

Try it. Type this and press Return:

```
echo "hello from my Mac"
```

It echoes the text back. You're now a Terminal user.

---

## Part 2 — Install the tools (15 minutes, one-time)

### Step 1: Homebrew — the Mac's app store for tools

Paste this (it's the official installer from [brew.sh](https://brew.sh)):

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

It will ask for your Mac login password — typing it shows **nothing on screen**, which
is normal; type it blind and press Return. It may also install "Command Line Tools"
first. Total: 5–10 minutes.

**Important:** at the end, Homebrew prints a box titled **"Next steps"** containing two
commands with `eval` in them. Copy and run those two lines — they connect Homebrew to
your Terminal. (New Terminal windows will have it automatically.)

### Step 2: Python — the language all of this runs on

```
brew install python@3.12
```

### Step 3: A clean workspace and the AI toolkit

Paste these four lines one at a time:

```
mkdir -p ~/claudette-ai && cd ~/claudette-ai
```

```
python3.12 -m venv env
```

```
source env/bin/activate
```

```
pip install --upgrade mlx-lm
```

What just happened: you made a folder called `claudette-ai` in your home folder,
created an isolated Python "environment" inside it (a sandbox, so nothing here touches
the rest of your Mac), switched it on, and installed **MLX** — Apple's own open-source
machine-learning toolkit, built specifically for the chip in your Mac.

**Remember this one thing:** whenever you open a new Terminal window to work on this,
run these two lines first to get back into the workspace:

```
cd ~/claudette-ai && source env/bin/activate
```

You'll know it worked because `(env)` appears at the start of the prompt line.

---

## Part 3 — Talk to a real AI on your own Mac (10 minutes)

Before any training, prove the whole thing works. This downloads a genuinely good open
model — Qwen 2.5, 7 billion parameters, compressed to ~4.5 GB — and starts a chat with
it. The download happens once; after that it loads from disk in seconds.

```
mlx_lm.chat --model mlx-community/Qwen2.5-7B-Instruct-4bit
```

*(On an 8 GB Mac use `mlx-community/Qwen2.5-3B-Instruct-4bit` instead — here and
everywhere the model name appears below.)*

When `>>` appears, type a message and press Return. Ask it anything — draft a
paragraph, explain a concept, summarize something you paste in. When you're done, type
`q` and press Return to quit.

Pause on what just happened: **a capable AI ran entirely on your desk.** No internet
needed after the download (feel free to test that with Wi-Fi off), no account, nothing
transmitted anywhere. This alone — never mind training — is a private drafting
scratchpad you can paste confidential material into.

Honest expectations: this model is roughly "a smart intern" — very useful, but well
below Claude. It will occasionally say wrong things confidently. Treat everything it
produces as a first draft, and never trust it on legal substance — facts and case law
come from your research tools, not from any model's memory.

---

## Part 4 — Teach it to write like you (the training)

Fine-tuning nudges that model toward *your* voice: your letter openings, your memo
structure, your phrasing. It learns style and format from examples — it does not
reliably learn facts, so don't try to teach it law; teach it *how you write*.

### Step 1: Gather your writing

Create two things on your Mac:

**A folder of your writing** at `~/claudette-ai/my-writing/`. Fill it with your own
letters, memos, and briefs as plain text (`.txt`) or Markdown (`.md`) files. In Word:
File → Save As → Plain Text. Ten documents is a start; fifty is good.

**A pairs file** at `~/claudette-ai/pairs.jsonl` — the highest-value ingredient. Each
line is one example of an instruction and the response *you* would write, in exactly
this format:

```
{"prompt": "Draft a letter to opposing counsel requesting a two-week extension on discovery responses.", "response": "Dear Counsel:\n\nI write regarding the discovery responses currently due..."}
```

The easiest way to build this file: open a Claude session in this repo and say *"help
me turn these documents into a pairs.jsonl file"* — Claudette can draft the pairs from
your real documents while you review each one. Aim for 50–200 pairs. Quality beats
quantity by a wide margin.

**Redact first.** Replace client names, addresses, and case numbers before anything
goes in the training folder. The training is private, but the finished model can echo
its training text back — a model that absent-mindedly types a real client's name into
an unrelated draft is a problem you prevent now.

### Step 2: Get this repo's data-preparation script onto the Mac

Download this repository: on its GitHub page, click the green **Code** button →
**Download ZIP**, unzip it, and note where the folder landed (likely
`~/Downloads/Claudette-main`). Then convert your writing into training files:

```
python3 ~/Downloads/Claudette-main/finetune/prepare_data.py --docs ~/claudette-ai/my-writing --pairs ~/claudette-ai/pairs.jsonl --scrub --out ~/claudette-ai/data
```

It prints how many training examples it built. The `--scrub` flag auto-redacts
emails, phone numbers, and case-number patterns as a backstop — but it's a backstop,
not a substitute for your own redaction pass.

### Step 3: Train

```
mlx_lm.lora --model mlx-community/Qwen2.5-7B-Instruct-4bit --train --data ~/claudette-ai/data --batch-size 2 --iters 600
```

Numbers scroll by — each line shows the **loss**, the model's error score. Watch it
drift downward: that is the model learning your voice, live. Expect roughly 30–90
minutes depending on your Mac and data size. Your Mac stays usable meanwhile (the fans
may speak up). If you need to stop, press **Ctrl + C** — no harm done, just start the
command again later.

The result lands in a folder called `adapters` — a small file holding everything the
model learned from you. Your writing itself is not in there; only the *adjustments* are.

### Step 4: Meet your model

```
mlx_lm.chat --model mlx-community/Qwen2.5-7B-Instruct-4bit --adapter-path adapters
```

Same chat as before — but now ask it to draft something you'd normally write, and
compare against Part 3. Run both side by side with your own real prompts; the
difference in voice is the payoff.

### Step 5 (optional): Seal it into a single permanent model

```
mlx_lm.fuse --model mlx-community/Qwen2.5-7B-Instruct-4bit --adapter-path adapters --save-path ~/claudette-ai/claudette-mac
```

This bakes the adapter into the base model, producing one self-contained folder —
**your model**, finished. From now on you can start it with just:

```
mlx_lm.chat --model ~/claudette-ai/claudette-mac
```

Back up the `~/claudette-ai/claudette-mac` folder like any important file (Time
Machine covers it automatically).

---

## Part 5 — Beyond: living with your model

**Daily use.** Open Terminal, then:

```
cd ~/claudette-ai && source env/bin/activate && mlx_lm.chat --model ~/claudette-ai/claudette-mac
```

Select all three lines and paste them together — Terminal runs them in sequence.
That's your whole startup ritual.

**Make it better over time.** The model is only as good as its examples. When it drafts
something and you find yourself heavily editing the result, that's a training pair
waiting to happen: save your *corrected* version into `pairs.jsonl` and re-run Steps
2–5 every month or two. Each round sounds a little more like you. (Re-training starts
from the original base model plus all your accumulated pairs — so the file of pairs is
the real asset. Guard it.)

**A friendlier window than Terminal.** If you'd rather click than type for everyday
stock-model chat, [LM Studio](https://lmstudio.ai) is a free Mac app with a normal
chat interface that runs the same kinds of local models. Your custom fused model is
easiest to reach through the Terminal command above, though — one is for comfort, the
other is for *your* model.

**Where each tool fits.** After all this you'll have three AIs, and they don't compete:

| | Best at | Confidential client material? |
|---|---|---|
| Claude / Claudette (this repo) | Reasoning, research, verified citations, complex drafting | Via the firm's authorized tools |
| Your Mac model | Fast private first drafts in your voice, offline work | Yes — never leaves the machine |
| Claudette-1 (`../claudette-1/`) | Understanding how all of this works | It writes 1787 gibberish; nothing to leak |

**The one rule that never changes:** every model output — cloud or local, tuned or not
— is a draft for attorney review. Verify citations against real sources. Models are
eloquent; eloquence is not accuracy.

---

## Troubleshooting

**"command not found: brew"** — Homebrew's "Next steps" `eval` lines weren't run.
Easiest fix: close Terminal, open a fresh window, try again. If it persists, run:
`eval "$(/opt/homebrew/bin/brew shellenv)"`

**"command not found: mlx_lm.chat" (or pip, or python3.12)** — you're not in the
workspace. Run `cd ~/claudette-ai && source env/bin/activate` and look for `(env)` in
the prompt.

**Password prompt shows nothing while typing** — normal. Type it and press Return.

**Download is huge/slow** — the ~4.5 GB model downloads once, then it's cached. On a
slow connection, let it run; it resumes if interrupted.

**Training crashes or the Mac becomes unusable** — memory pressure. Close other apps
and retry with `--batch-size 1`. Still stuck? Switch to the 3B model
(`mlx-community/Qwen2.5-3B-Instruct-4bit`) — noticeably less capable but light.

**"ValueError: … train.jsonl / valid.jsonl"** — the `--data` folder must contain
`train.jsonl` and `valid.jsonl`; `prepare_data.py` creates both, so check the path you
passed to `--data`.

**The tuned model sounds *too much* like the training data / repeats itself** —
overfit. Retrain with fewer passes: add `--iters 300` in Step 3, or add more varied
pairs.

**Anything else** — paste the exact error into a Claude session in this repo and ask.
Debugging someone's first Terminal error is squarely Claudette's job.

---

## Glossary

- **Terminal** — the Mac app where you type commands instead of clicking.
- **Homebrew** — an installer for developer tools, run from Terminal.
- **Python** — the programming language; you run scripts with it, you never write it.
- **venv / environment** — a sandboxed folder for a project's tools, so they can't
  interfere with the rest of the Mac. `source env/bin/activate` steps into it.
- **MLX** — Apple's machine-learning toolkit, tuned for the M-series chips.
- **Model / weights** — the AI itself: a file of billions of learned numbers.
- **Open-weight model** — a model whose file anyone may download and modify (Qwen,
  Llama, Mistral), as opposed to Claude or GPT, which live behind an API.
- **Fine-tuning / LoRA** — nudging an existing model with your examples; LoRA is the
  efficient technique that stores those nudges in a small "adapter" file.
- **Fusing** — permanently merging the adapter into the model, yielding one
  self-contained folder.
- **Loss** — the error score printed during training. Down is good.
- **Tokens** — the word-fragments models read and write; you'll see counts of them in
  the tools' output.
- **Hugging Face** — the website models download from; the GitHub of AI models.

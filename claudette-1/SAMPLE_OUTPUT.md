# What Claudette-1 writes

Samples from the trained checkpoint (3,000 iterations, best validation loss 1.333).
The prompt is in **bold**; everything after it is the model, character by character.

## The learning curve, visible in text

**Iteration 0** — random weights, uniform gibberish (loss 4.35, exactly ln(77)):
the model knows nothing, every character equally likely.

**Iteration 1000** (loss ~1.66) — word-shaped, English-flavored:

> the and the sprident of the subliated of the pressive no not the power
> expressed admonan in the power have the predent coction with the collace
> disppacts and the will depresssion of than expedent of t

**Iteration 2000** (loss ~1.40) — real words, real phrases surfacing:

> the people of the United States, when all same confederate excluded and
> spiret severed to on convention the admit not only impercious in for the
> number of our the contendsion of such excepts of the ca

## The trained model

**To the People of the State of New York**

> : Personal States. The contentions of the policy of the constitution of the
> secure of the State of the Union, which excepted a great strade in the
> natural by such of the legislative, when the destrain suppose, that a number
> over the legislative of the courts of the distinct of the people which more
> to be perjuded to the government which in the State government with each
> other of a considerable and extended is interestible to them...

**The judicial power of the United States**

> , who all attacles to be desired the armies of impressions and may faction
> of the proposed such a power. But a power, of propriety the secure of the
> great of the confederacy of men may be some, to a confederacies and with
> every one all conclusive by the dispose of the security of leady it to rule
> the privation of founds in the part of the efformeration of the constitution...

## What this shows

An 820,000-parameter model trained for ten minutes learned — from raw characters,
with no dictionary and no grammar rules — spelling, capitalization after periods,
Publius's sentence rhythm, and phrases like "the people of the United States."
What it cannot do at this scale is *mean* anything: there aren't enough parameters
to hold facts or logic, so it produces the music of the Federalist Papers without
the message.

Scale this same code and recipe up about a million times, add instruction tuning
and RLHF, and the music starts carrying meaning. That gap — and that continuity —
is the whole story of modern LLMs.

Reproduce these samples:

```bash
python3 generate.py --prompt "To the People of the State of New York" --tokens 500 --temperature 0.7
```

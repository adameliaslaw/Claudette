"""Claudette-1: a small GPT-style language model, written to be read.

This is the same architecture family as GPT and Claude — a decoder-only
transformer — at roughly one-millionth the scale. Every large language model
you have used is, at its core, this file with bigger numbers.

The model's entire job: given a sequence of tokens, predict the next one.
Everything an LLM appears to "know" emerges from learning that task well.
"""

import math

import torch
import torch.nn as nn
from torch.nn import functional as F


class Config:
    """Hyperparameters. Claude-scale models differ mainly in these numbers
    (plus a smarter tokenizer, vastly more data, and post-training)."""

    block_size: int = 128   # max context length, in tokens (Claude: ~200,000)
    vocab_size: int = 96    # set from data; we tokenize per character (Claude: ~65,000 subwords)
    n_layer: int = 4        # transformer blocks stacked (frontier models: ~100)
    n_head: int = 4         # parallel attention heads per block
    n_embd: int = 128       # width of the token representation (frontier: ~16,000)
    dropout: float = 0.1

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class CausalSelfAttention(nn.Module):
    """The heart of the transformer.

    Each token builds a query ("what am I looking for?"), and compares it
    against every earlier token's key ("what do I contain?"). The match
    scores decide how much of each earlier token's value to blend into this
    token's representation. "Causal" means a token may only look backwards —
    that is what makes next-token prediction honest.
    """

    def __init__(self, config: Config):
        super().__init__()
        assert config.n_embd % config.n_head == 0
        # one linear layer produces queries, keys, and values for all heads
        self.c_attn = nn.Linear(config.n_embd, 3 * config.n_embd)
        self.c_proj = nn.Linear(config.n_embd, config.n_embd)
        self.dropout = nn.Dropout(config.dropout)
        self.n_head = config.n_head
        self.n_embd = config.n_embd

    def forward(self, x):
        B, T, C = x.shape  # batch, sequence length, embedding width
        q, k, v = self.c_attn(x).split(self.n_embd, dim=2)
        # split into heads: each head attends independently, letting the
        # model track several kinds of relationships at once
        q = q.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        k = k.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        v = v.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        # fused attention: softmax(q @ k^T / sqrt(d)) @ v, with causal mask
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        y = y.transpose(1, 2).contiguous().view(B, T, C)  # re-merge heads
        return self.dropout(self.c_proj(y))


class MLP(nn.Module):
    """After attention gathers context, this two-layer network processes it.
    Most of a transformer's parameters — and, loosely, its stored 'facts' —
    live in these layers."""

    def __init__(self, config: Config):
        super().__init__()
        self.c_fc = nn.Linear(config.n_embd, 4 * config.n_embd)
        self.c_proj = nn.Linear(4 * config.n_embd, config.n_embd)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x):
        return self.dropout(self.c_proj(F.gelu(self.c_fc(x))))


class Block(nn.Module):
    """One transformer block: attend, then think. Residual connections
    (the x + ...) let gradients flow through many stacked blocks."""

    def __init__(self, config: Config):
        super().__init__()
        self.ln_1 = nn.LayerNorm(config.n_embd)
        self.attn = CausalSelfAttention(config)
        self.ln_2 = nn.LayerNorm(config.n_embd)
        self.mlp = MLP(config)

    def forward(self, x):
        x = x + self.attn(self.ln_1(x))
        x = x + self.mlp(self.ln_2(x))
        return x


class GPT(nn.Module):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.transformer = nn.ModuleDict(
            dict(
                wte=nn.Embedding(config.vocab_size, config.n_embd),  # token embeddings
                wpe=nn.Embedding(config.block_size, config.n_embd),  # position embeddings
                drop=nn.Dropout(config.dropout),
                h=nn.ModuleList(Block(config) for _ in range(config.n_layer)),
                ln_f=nn.LayerNorm(config.n_embd),
            )
        )
        # maps the final representation back to a score per vocabulary token
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False)
        # weight tying: the same matrix embeds tokens and un-embeds them
        self.transformer.wte.weight = self.lm_head.weight
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def num_params(self) -> int:
        return sum(p.numel() for p in self.parameters())

    def forward(self, idx, targets=None):
        B, T = idx.shape
        pos = torch.arange(T, device=idx.device)
        x = self.transformer.drop(self.transformer.wte(idx) + self.transformer.wpe(pos))
        for block in self.transformer.h:
            x = block(x)
        x = self.transformer.ln_f(x)
        logits = self.lm_head(x)

        loss = None
        if targets is not None:
            # cross-entropy against the true next token at every position.
            # This single number is what training minimizes — all capability
            # falls out of pushing it down.
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens: int, temperature: float = 0.8, top_k: int = 40):
        """Autoregressive sampling: predict a distribution over the next
        token, sample one, append it, repeat. This loop IS text generation —
        Claude answering you is this loop at scale."""
        self.eval()
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.config.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / temperature
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float("inf")
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx

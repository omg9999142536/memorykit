---
name: memory-kit
description: Memory system kit for AI agents — orthogonal axes, daily GC, hash-chained clock, heartbeat panel. Solve context bloat with a proven file-based memory architecture.
---

# Memory Kit 🧠

A battle-tested memory architecture for AI agents (built on Hermes Agent, adaptable to any file-based agent).

Born from a real problem: agent memory hit its 4,000-char limit after 10 days of heavy use. This kit is the system that fixed it — now running daily in production.

## The Problem It Solves

Agent long-term memory fails in a predictable loop:

1. Memory fills up → you delete old entries → you lose something important
2. You keep everything → context bloats → slow and expensive
3. Memory tools are flaky (fuzzy matching fails on batch edits) → corruption risk

**The fix is architectural, not tactical**: keep only 3 things in hot memory (red lines / current task / pointers), externalize everything else into *orthogonal axes*, and let a daily GC compress the cold parts automatically.

## What's Inside

```
memory-kit/
├── SKILL.md              ← this file (agent-facing instructions)
├── scripts/
│   ├── memory_gc.py      ← daily GC: compress closed projects & stale entries
│   ├── sj_clock.py       ← hash-chained clock (append-only, tamper-evident)
│   ├── heartbeat_panel.py← hourly "learning progress" panel to chat
│   └── bayes_update.py   ← user-decision priors (Beta distribution updates)
├── templates/
│   ├── MEMORY.md         ← hot memory skeleton (red lines / tasks / pointers)
│   ├── MEMORY-INDEX.md   ← axis registry & lookup table
│   └── axes/             ← axis file seeds (project / research / preference...)
└── docs/
    └── ARCHITECTURE.md   ← full design rationale + pitfalls
```

## Core Concepts

### 1. Orthogonal Axes (正交轴)

Memory is split into axis files by *kind*, not by *time*:

| Axis | Meaning |
|------|---------|
| `xm` | projects |
| `yj` | research |
| `ph` | user preferences |
| `ff` | methodology |
| `hb` | environment facts |
| `rw` | tasks |
| `jn` | memory system itself |
| `sj` | time/clock |
| `gj` | tools |

Rules:
- **Adding a new category = adding a new axis. Never re-sort old axes.** (orthogonality = add dimensions, never reorder)
- Hot memory (MEMORY.md) holds only: red lines + current tasks + one-line pointers
- Everything else is *born externalized* — written directly to its axis file

### 2. Daily GC (memory_gc.py)

Four compression rules, one iron rule:

- ✅ Closed project sections → one-line pointer (original archived)
- ✅ Task entries with dates > 7 days old → one line
- ✅ Undated environment facts > 150 chars → one line
- 🔒 **Red lines / discipline / constitution sections — NEVER touched**

Run it: `python3 scripts/memory_gc.py --dry` first (preview), then without flag.

### 3. Hash-Chained Clock (sj_clock.py)

LLMs hallucinate time. This gives your agent a tamper-evident timeline:

```bash
python3 scripts/sj_clock.py status   # chain health
python3 scripts/sj_clock.py note "shipped v1.2"  # append event anchor
python3 scripts/sj_clock.py verify   # full hash-chain verification + NTP cross-check
python3 scripts/sj_clock.py when "v1.2"  # causal query
```

Chain file is append-only JSONL — any byte tampered, `verify` breaks.

### 4. Heartbeat Panel (heartbeat_panel.py)

Hourly "am I actually learning?" check pushed to your chat. Not a status dump — a learning-progress panel: inventory / new entries / axes touched / prior shifts / one-line summary per axis. Empty day prints 「未更新」 (nothing to report), honestly.

### 5. Bayesian Priors (bayes_update.py)

Your agent asks permission a lot. Each user decision (approve/reject) is an observation that updates a Beta(α,β) prior per action type. Over time the agent stops asking about things you always approve — and stays cautious on things you've rejected.

## Quick Start

1. Copy `templates/` into your agent's memory directory
2. Copy `scripts/` somewhere on PATH
3. Set up a daily cron: `15 9 * * * python3 /path/to/memory_gc.py`
4. Read `docs/ARCHITECTURE.md` for the full write/retrieve discipline

## Design Philosophy

> Memory exists to free your hands, not to hoard. Closed projects sink into archives — that's *evidence of having lived*. Forgetting isn't loss, it's relocation.

Three questions before writing to hot memory:
1. If I delete this, will the next session break? (yes → keep)
2. Can I re-derive this from the environment? (yes → don't memorize)
3. Is this a red line, a current task, or a pointer? (if none → it goes to an axis)

## Requirements

- Python 3.8+ (stdlib only — no dependencies)
- Any agent that reads/writes markdown files (built for [Hermes Agent](https://github.com/NousResearch/hermes-agent), works with Claude Code / custom agents)

## License

MIT © 2026 Rui

## Support / 赞助

如果对你有帮助，欢迎[赞助作者](https://afdian.com/a/3d28com)。

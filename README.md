# Memory Kit 🧠

**A memory architecture for AI agents that actually survives daily use.**

Most agent memory systems fail the same way: memory fills up, you delete things, you lose context, you repeat solved problems. This kit is the fix — an orthogonal-axis memory system with daily GC, battle-tested in production for weeks.

## The Idea in One Sentence

Keep only **red lines + current tasks + pointers** in hot memory; everything else is *born externalized* into axis files; a daily GC compresses the cold zone automatically.

## What You Get

| Component | What it does |
|---|---|
| **Orthogonal axes** | Memory split by kind (projects/research/preferences/methodology/env/time), not by time. Add dimensions freely — never re-sort. |
| **Daily GC** | `memory_gc.py` compresses closed projects & stale entries to one-liners. Red lines untouched forever. |
| **Hash-chained clock** | `sj_clock.py` — append-only, tamper-evident timeline. LLMs hallucinate time; this fixes it. |
| **Heartbeat panel** | Hourly "am I actually learning?" check instead of a status dump. |
| **Bayesian priors** | Every approve/reject updates a Beta prior per action — the agent learns what to stop asking about. |

## Why It Works

Agent memory problems are **architectural, not budget problems**. Raising the limit just delays the collapse. This system's core moves:

- **Born externalized** — new facts land in their axis file, not in hot memory
- **Closed = archived** — finished projects move to a works ledger; forgetting is relocation, not loss
- **Three-question gate before writing hot memory**:
  1. If deleted, does the next session break? (yes → keep)
  2. Can I re-derive it from the environment? (yes → don't memorize)
  3. Is it a red line, a current task, or a pointer? (none → goes to an axis)

## Install

```bash
git clone https://github.com/<your-name>/memory-kit.git ~/.memory-kit
cd ~/.memory-kit
bash install.sh          # copies scripts to ~/.hermes/scripts (or your agent's dir)
```

Then wire the daily GC cron:

```bash
15 9 * * * python3 ~/.hermes/scripts/memory_gc.py
```

## Usage

```bash
python3 scripts/memory_gc.py --dry     # preview what would be compressed
python3 scripts/memory_gc.py           # run it

python3 scripts/sj_clock.py note "shipped memory-kit v1.0"
python3 scripts/sj_clock.py verify     # hash-chain + NTP cross-check
python3 scripts/sj_clock.py when "v1.0"

python3 scripts/heartbeat_panel.py     # learning panel to stdout
python3 scripts/bayes_update.py --help # update decision priors
```

## Requirements

- Python 3.8+ — **stdlib only**, zero dependencies
- Any markdown-file-based agent (built on Hermes Agent; works with Claude Code or custom agents)

## Files

```
memory-kit/
├── SKILL.md                  ← agent-facing instructions
├── scripts/                  ← the four tools (100-200 lines each, auditable)
├── templates/                ← MEMORY.md skeleton + axis registry + axis seeds
└── docs/ARCHITECTURE.md      ← full design rationale + 8 battle-tested pitfalls
```

## Design Philosophy

> Memory exists to free your hands, not to hoard.
> Closed projects sink into archives — that's evidence of having lived.
> Forgetting isn't loss, it's relocation.

## License

MIT © 2026 Rui

---

## Related Projects

- **[agentguard-skill](https://github.com/omg9999142536/agentguard-skill)** 🛡️ — Budget fuse for AI agents: local proxy caps paid API spend with hard cutoffs, live cost panel. Same author, same production-tested approach.

---

## Related Projects

- **[agentwalls](https://github.com/omg9999142536/agentwalls)** 🏛️ — closed-loop economy kernel for AI agents (stake, settle, verify, govern)
- **[agentguard-skill](https://github.com/omg9999142536/agentguard-skill)** 🛡️ — budget fuse for AI agent API spend

*Same author, same production-tested approach: memory, economy, budget — the three organs of a durable agent.*

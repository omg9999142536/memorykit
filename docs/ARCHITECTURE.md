# Memory Kit — Architecture

Why this system exists, and every pitfall that shaped it.

## Origin

Ten days of heavy agent use filled a 4,000-character memory budget to 94%. Naive fixes all fail:

- **Delete old entries** → lose context, agent repeats solved problems
- **Raise the limit** → context bloat, cost and latency grow with it
- **Summarize aggressively** → summaries drift, details evaporate silently

The root cause wasn't the budget. It was that *everything* was being kept in hot memory — including things that could be re-derived from the environment, and closed projects that would never be touched again.

## The Architecture

```
┌─────────────────────────────────────────────┐
│ HOT MEMORY (MEMORY.md, tiny)                │
│   red lines │ current tasks │ pointers      │
└──────────────┬──────────────────────────────┘
               │ born-externalized writes
               ▼
┌─────────────────────────────────────────────┐
│ AXIS FILES (orthogonal, unlimited)          │
│   xm  yj  ph  ff  hb  rw  jn  sj  gj  ...   │
└──────────────┬──────────────────────────────┘
               │ daily GC compresses cold zone
               ▼
┌─────────────────────────────────────────────┐
│ ARCHIVE (axes/ GC-section, works.json)      │
│   closed projects = evidence of having lived│
└─────────────────────────────────────────────┘
```

### Orthogonality

Axes split by *kind*, not time. A project's status goes to `xm`, the research behind it to `yj`, user's preference about how to work on it to `ph`. One fact, one axis — and the axis registry (MEMORY-INDEX.md) is the single lookup table.

**Iron rule**: new category = new axis file + one registry row. Never re-sort, never merge, never redefine. Orthogonality means *adding dimensions is safe; reordering is corruption.*

### The GC Contract

`memory_gc.py` runs daily and compresses exactly four things — nothing else:

1. Closed project sections (marked 已归档/已放下/done/shipped) → one-line pointer, original text archived
2. Dated task entries older than 7 days → one line
3. Undated environment-fact paragraphs > 150 chars → one line
4. **Red lines / discipline / constitution sections are untouchable** — the script's first job is to identify and skip them

Always `--dry` first. Write-side discipline ("born externalized") is the real fix; GC is the safety net, not the garbage disposal.

### The Clock Chain

LLMs confabulate time ("last week" can mean anything). `sj_clock.py` maintains an append-only JSONL with a hash chain — each entry hashes the previous one, so any tampering breaks `verify`. Events are appended via `note`; `when <keyword>` answers "when did X happen" causally. NTP cross-check in `verify` gives machine-time authority.

### Heartbeats Over Status Dumps

The hourly heartbeat is a *learning panel*, not a status report: did inventory grow, which axes were touched, did priors shift. Rules: no changes → print "no update" (honest); changes → bold the numbers; end with a one-line verdict classified as "learning running / retrieval calibrating / standing by."

### Priors, Not Permissions

Every user decision updates a Beta(α,β) per action class. High-mean actions stop being asked about; low-mean actions escalate. Crucially: *backfilled* historical decisions must be reported as a prior jump, not as today's observations — otherwise users think the agent is acting up daily.

## Pitfalls (all battle-tested)

1. **Memory tools are unreliable for batch edits.** Fuzzy-match replace returns `? on ?` or rejects silently when old_text has been rewritten by earlier ops. Fix: read the file's *current real text* with code, then do exact string replacement in Python. Batch-lose-field → `unknown action` → whole op discarded.

2. **Environment facts are zero-memory-value.** Package versions, script paths, port numbers — all re-derivable. They commonly eat 30%+ of hot memory. Grep for a copy in configs before deleting; keep a one-line pointer.

3. **Project status entries rot.** Write the *restart condition* when you write the status. When a project closes, externalize immediately to an archive file; hot memory keeps one pointer.

4. **Splitting axes dilutes navigation.** Past ~100 entries per axis, add internal sections instead of new axes.

5. **Use code-append, not patch tools, for axis files.** Entries contain pipes/special chars; fuzzy matchers misjudge.

6. **Verification entries need negative controls.** Recording "all green" proves nothing — write down *which counterexamples must fail*, or future sessions can't tell if the check has any discriminating power.

7. **Prediction-then-compare discipline.** Before acting, write down the expected result. After, compare. No expectation = no delta = the experiment was theater.

8. **The user's "I can't compress it further" usually means "you should have externalized more," not "we hit the limit."**

## Scaling

- 10 entries: flat files, anything works
- 100 entries: this kit as-is (registry + GC covers it)
- 1,000+ entries: add a spatial index layer (see our Hilbert-curve experiment: coordinates from a semantic taxonomy, neighbors-by-location retrieval) — but note the lesson: *position must come from meaning; hashing coordinates destroys locality semantics*
- Memory tool failures at any scale: fall back to direct file edits via code

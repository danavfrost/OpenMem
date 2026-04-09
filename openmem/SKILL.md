---
name: openmem
description: "SQLite long-term memory for OpenClaw. Use when: storing facts/preferences permanently, recalling past context, compressing sessions, or user says 'remember this'. Tools: memory_add, memory_search, memory_update, memory_delete, memory_list, memory_stats."
metadata:
  {
    "openclaw": {
      "emoji": "🧠",
      "requires": { "bins": ["python3"] }
    }
  }
---

# OpenMem v1.0.9

SQLite-backed long-term memory. All data stays local — no network calls, no external services.

MIT License — free to use, modify, redistribute. No attribution required.

## Privacy & Scope

- **Local only.** All data stays on your machine. No network calls are made at any point.
- **Full session content is read during compression.** `compress.py read <session_id>` outputs the complete raw session transcript and passes it to the agent so it can decide what to extract. The agent sees everything in that session. Only the 3–10 items it selects are written to the DB — the raw content is never stored — but the agent processes the full log during that turn.
- **Cache file is plaintext.** After every memory write, the top memories are written to `openmem-cache.json` (same directory as the DB) in unencrypted JSON. This is the same trust level as the SQLite DB itself — both are local files readable by any process running as your user.
- **Persistent presence.** `setup.py` registers an MCP server (memory tool calls) and a cron job (background compression checks) with your OpenClaw gateway. This gives OpenMem ongoing read access to session files and write access to the local DB while enabled. To remove, run `uninstall.py` (see [Uninstall](#uninstall) below).

## MCP Tool Calls

When the OpenMem MCP server is registered, use these native tool calls directly:

| Tool | Purpose |
|---|---|
| `memory_add` | Store a new memory (content, category, importance, source) |
| `memory_search` | FTS search with relevance + importance + recency ranking |
| `memory_update` | Change content, category, or importance by ID |
| `memory_delete` | Remove a memory by ID |
| `memory_list` | List memories sorted by importance / recency / access |
| `memory_stats` | Total count, breakdown by category, date range |

## Installation

After `openclaw skills install openmem`, run setup once:

```bash
python3 ~/.openclaw/workspace/skills/openmem/scripts/setup.py
```

This creates the database, checks requirements, registers the MCP server, and prints the next steps (hook enable). No cron job is registered — compression runs on demand only.

## Uninstall

Removes the cron job, MCP server, and bootstrap hook. **Your database is not deleted** — its path is printed so you can export or remove it yourself.

```bash
python3 ~/.openclaw/workspace/skills/openmem/scripts/uninstall.py
```

## CLI Quick Reference

```bash
SCRIPTS=~/.openclaw/workspace/skills/openmem/scripts

# Add a memory
python3 $SCRIPTS/mem.py add "User prefers concise responses" --category preference

# Search
python3 $SCRIPTS/mem.py search "response style"

# List top memories
python3 $SCRIPTS/mem.py list --limit 20

# Stats
python3 $SCRIPTS/mem.py stats

# --- Session compression ---
# List uncompressed sessions
python3 $SCRIPTS/compress.py pending

# Read a session (then you summarize it into mem.py add calls)
python3 $SCRIPTS/compress.py read <session-id>

# Mark compressed after adding memories
python3 $SCRIPTS/compress.py mark-done <session-id> --memory-count 5
```

## Categories

`fact` · `insight` · `preference` · `correction` · `event` · `general`

## Compression Workflow

Compression is on-demand only. Trigger it by saying something like:
- *"compress my sessions"*
- *"save this to long-term memory"*
- *"compress now"*

The agent will find uncompressed sessions, read each one, extract 3–10 memories, and mark them done.

If you want it to run automatically, add it to your OpenClaw heartbeat or a cron job yourself.

**Step by step:**

1. `python3 $SCRIPTS/compress.py pending` — find sessions not yet compressed
2. `python3 $SCRIPTS/compress.py read <id>` — read the conversation
3. Extract 3–10 key facts, corrections, preferences, and insights
4. Use `memory_add` tool call (or `mem.py add`) for each memory
5. `python3 $SCRIPTS/compress.py mark-done <id> --memory-count <N>`

**What to extract:**
- Facts the user stated about their system, preferences, or projects
- Mistakes made and the correct approach
- Decisions reached and why
- Important events (deploys, incidents, milestones)

**What to skip:** Raw command output, transient errors, small talk.

## Importance Guide

| Score | Meaning |
|---|---|
| 0.9–1.0 | Critical — always surface (key preferences, major corrections) |
| 0.7–0.8 | Important — surface often |
| 0.5–0.6 | Normal (default) |
| 0.3–0.4 | Low — background context |
| 0.0–0.2 | Archive only |

## Bootstrap Hook

The bootstrap hook auto-injects your top memories at session start.

Enable once:
```bash
openclaw hooks enable openmem
```

Memories appear in `OPENMEM.md` at the start of every session.
Control injection count with `OPENMEM_BOOTSTRAP_LIMIT` (default: 12).

## Database Schema

See [references/schema.md](references/schema.md) for full schema details.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENMEM_DB` | `~/.openclaw/workspace/memory/openmem.db` | Database path |
| `OPENMEM_BOOTSTRAP_LIMIT` | `12` | Memories injected at bootstrap |
| `OPENMEM_SESSIONS_DIR` | `~/.openclaw/agents/main/sessions` | Session files location |
| `OPENMEM_PYTHON` | `python3` | Python interpreter |

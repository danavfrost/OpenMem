# OpenMem

Long-term memory for [OpenClaw](https://openclaw.ai) agents. Stores facts, preferences, corrections, and insights in a local SQLite database and injects the most important ones into every session automatically.

All data stays on your machine. No network calls, no external services, no models required — pure Python stdlib.

MIT License.

---

## How it works

- **Bootstrap hook** — at the start of each session, your top memories are injected into the agent context as `OPENMEM.md`
- **MCP tools** — the agent can add, search, update, and delete memories mid-session via native tool calls
- **Session compression** — on demand, the agent reads past OpenClaw session logs and extracts 3–10 durable memories from each one
- **FTS5 search** — full-text search with BM25 ranking, weighted by importance and recency. Wildcard search (`*`, `?`) also supported.

## Installation

Requires [OpenClaw](https://openclaw.ai) and Python 3.8+.

```bash
openclaw skills install openmem
python3 ~/.openclaw/workspace/skills/openmem/scripts/setup.py
openclaw hooks enable openmem
openclaw gateway restart
```

## MCP Tools

| Tool | Purpose |
|---|---|
| `memory_add` | Store a new memory |
| `memory_search` | Search by keyword or wildcard |
| `memory_update` | Edit content, category, or importance |
| `memory_delete` | Remove a memory by ID |
| `memory_list` | List memories by importance / recency |
| `memory_stats` | Count and breakdown by category |

## Session Compression

Compression is on-demand. Ask the agent:

> "compress my sessions" / "save this to long-term memory" / "compress now"

The agent finds uncompressed sessions, reads each one, extracts key memories, and marks them done. If you want it automatic, wire `compress.py` into your own heartbeat or cron job.

## CLI

```bash
SCRIPTS=~/.openclaw/workspace/skills/openmem/scripts

python3 $SCRIPTS/mem.py add "Prefers dark mode" --category preference
python3 $SCRIPTS/mem.py search "dark mode"
python3 $SCRIPTS/mem.py search "*prefer*"
python3 $SCRIPTS/mem.py list --limit 20
python3 $SCRIPTS/mem.py stats
python3 $SCRIPTS/mem.py export --format md > memories.md

python3 $SCRIPTS/compress.py pending
python3 $SCRIPTS/compress.py read <session-id>
python3 $SCRIPTS/compress.py mark-done <session-id> --memory-count 5
```

## Categories

`fact` · `insight` · `preference` · `correction` · `event` · `general`

## Importance

| Score | Meaning |
|---|---|
| 0.9–1.0 | Critical — always surface |
| 0.7–0.8 | Important |
| 0.5–0.6 | Normal (default) |
| 0.3–0.4 | Low — background context |
| 0.0–0.2 | Archive only |

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENMEM_DB` | `~/.openclaw/workspace/memory/openmem.db` | Database path |
| `OPENMEM_BOOTSTRAP_LIMIT` | `12` | Memories injected at session start |
| `OPENMEM_SESSIONS_DIR` | `~/.openclaw/agents/main/sessions` | Session files location |

## Uninstall

```bash
python3 ~/.openclaw/workspace/skills/openmem/scripts/uninstall.py
```

Your database is not deleted. The uninstaller prints its path and the commands to export or remove it.

## Privacy

- All data is local — no network calls ever
- During compression, the agent reads the full session transcript to decide what to extract. Raw content is never stored in the DB.
- The memory cache (`openmem-cache.json`) and database are unencrypted local files, readable by any process running as your user

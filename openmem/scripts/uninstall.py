#!/usr/bin/env python3
"""
OpenMem - uninstall.py
Removes OpenMem's registered components from OpenClaw.

Your memory database is NOT deleted. Its location is printed at the end
so you can back it up, migrate it, or delete it yourself.

Run:
  python3 ~/.openclaw/workspace/skills/openmem/scripts/uninstall.py
"""

import os
import shutil
import subprocess
from pathlib import Path

DEFAULT_DB = Path(
    os.environ.get("OPENMEM_DB", "~/.openclaw/workspace/memory/openmem.db")
).expanduser()

MCP_NAME = "openmem"
HOOK_NAME = "openmem"


def _openclaw(*args) -> subprocess.CompletedProcess:
    openclaw_bin = shutil.which("openclaw")
    if not openclaw_bin:
        raise FileNotFoundError("openclaw not found in PATH")
    return subprocess.run(
        [openclaw_bin, *args],
        capture_output=True, text=True, timeout=10
    )


def remove_mcp() -> str:
    try:
        r = _openclaw("mcp", "unset", MCP_NAME)
        return "removed" if r.returncode == 0 else f"failed ({r.stderr.strip()})"
    except FileNotFoundError:
        return "skipped (openclaw not in PATH)"
    except Exception as e:
        return f"failed ({e})"


def disable_hook() -> str:
    try:
        r = _openclaw("hooks", "disable", HOOK_NAME)
        if r.returncode == 0:
            return "disabled"
        return f"failed ({r.stderr.strip()})" if r.stderr.strip() else "not enabled"
    except FileNotFoundError:
        return "skipped (openclaw not in PATH)"
    except Exception as e:
        return f"failed ({e})"


def main():
    print("OpenMem Uninstall\n")

    mcp_status  = remove_mcp()
    hook_status = disable_hook()

    print(f"  MCP server ({MCP_NAME}):  {mcp_status}")
    print(f"  Bootstrap hook:           {hook_status}")

    db_path = Path(os.environ.get("OPENMEM_DB", str(DEFAULT_DB))).expanduser()
    cache_path = db_path.parent / "openmem-cache.json"

    print()
    print("Your memory database was NOT deleted.")
    print(f"  Database:  {db_path}")
    if cache_path.exists():
        print(f"  Cache:     {cache_path}")
    print()
    print("To export your memories before deleting:")
    skill_dir = Path(__file__).parent
    print(f"  python3 {skill_dir / 'mem.py'} export --format md > memories.md")
    print()
    print("To delete the database permanently:")
    print(f"  rm {db_path}")
    if cache_path.exists():
        print(f"  rm {cache_path}")
    print()
    skill_path = Path(__file__).parent.parent
    print("OpenMem components have been removed from OpenClaw.")
    print("To remove the skill directory itself:")
    print(f"  rm -rf {skill_path}")
    print()
    print("Restart the gateway for changes to take effect:")
    print("  openclaw gateway restart")
    print()


if __name__ == "__main__":
    main()

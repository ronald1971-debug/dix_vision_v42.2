#!/usr/bin/env python3
"""
Check and manage auto GitHub push status
"""

import json
from pathlib import Path


def check_status():
    """Check the current auto-push status."""
    state_file = Path("c:\\dix_vision_v42.2\\.devin\\auto_push_state.json")

    if state_file.exists():
        with open(state_file, "r") as f:
            state = json.load(f)

        print("Auto GitHub Push Status")
        print("=" * 40)
        print(f"Files accumulated: {state['files_changed']}/30")
        print(f"Last push: {state.get('last_push', 'Never')}")
        print(f"Last commit: {state.get('last_commit', 'Never')}")

        if state["files_changed"] >= 30:
            print("\n[OK] Threshold reached - Ready to push")
        else:
            remaining = 30 - state["files_changed"]
            print(f"\n[WAIT] {remaining} more files needed before auto-push")
    else:
        print("Auto GitHub Push Status")
        print("=" * 40)
        print("No state file found - starting fresh")


if __name__ == "__main__":
    check_status()

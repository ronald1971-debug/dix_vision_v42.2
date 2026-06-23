#!/usr/bin/env python3
"""
Check and manage auto GitHub PR status
"""

import json
from pathlib import Path


def check_status():
    """Check the current auto-PR status."""
    state_file = Path("c:\\dix_vision_v42.2\\.devin\\auto_pr_state.json")

    if state_file.exists():
        with open(state_file, "r") as f:
            state = json.load(f)

        print("Auto GitHub PR Status")
        print("=" * 40)
        print(f"Files accumulated: {state['files_changed']}/30")
        print(f"Last PR: #{state.get('pr_number', 0)}")
        print(f"Last PR created: {state.get('last_pr', 'Never')}")

        if state["files_changed"] >= 30:
            print("\n[OK] Threshold reached - Ready to create PR")
        else:
            remaining = 30 - state["files_changed"]
            print(f"\n[WAIT] {remaining} more files needed before auto-PR")
    else:
        print("Auto GitHub PR Status")
        print("=" * 40)
        print("No state file found - starting fresh")


if __name__ == "__main__":
    check_status()

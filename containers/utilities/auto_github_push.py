#!/usr/bin/env python3
"""
Auto GitHub Push System
Automatically force pushes to GitHub every 30 files changed.
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path


class AutoGitHubPush:
    def __init__(self, repo_path="c:\\dix_vision_v42.2", files_threshold=30):
        self.repo_path = Path(repo_path)
        self.files_threshold = files_threshold
        self.state_file = self.repo_path / ".devin" / "auto_push_state.json"
        self.git_exe = "git"

    def load_state(self):
        """Load the current state from file."""
        if self.state_file.exists():
            with open(self.state_file, "r") as f:
                return json.load(f)
        return {"files_changed": 0, "last_push": None, "last_commit": None}

    def save_state(self, state):
        """Save the current state to file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def run_git_command(self, command):
        """Run a git command and return the output."""
        try:
            result = subprocess.run(
                command, shell=True, cwd=self.repo_path, capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def get_changed_files(self):
        """Get the number of changed files."""
        success, stdout, _ = self.run_git_command("git status --porcelain")
        if success:
            changed_files = [line for line in stdout.split("\n") if line.strip()]
            return len(changed_files)
        return 0

    def commit_changes(self, message="Auto commit by Devin"):
        """Commit all changes."""
        # Add all changes
        self.run_git_command("git add -A")

        # Commit with message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"{message} - {timestamp}\n\nGenerated with [Devin](https://devin.ai)\n\nCo-Authored-By: Devin <158243242+devin-ai-integration[bot]@users.noreply.github.com>"

        success, _, stderr = self.run_git_command(f'git commit -m "{commit_message}"')
        if success:
            print(f"[OK] Changes committed: {message}")
            return True
        else:
            print(f"[ERROR] Commit failed: {stderr}")
            return False

    def force_push(self):
        """Force push to GitHub."""
        print("Force pushing to GitHub...")
        success, stdout, stderr = self.run_git_command("git push --force")
        if success:
            print("[OK] Force push successful")
            return True
        else:
            print(f"[ERROR] Force push failed: {stderr}")
            return False

    def check_and_push(self):
        """Check if threshold reached and push if needed."""
        state = self.load_state()
        changed_files = self.get_changed_files()

        total_files = state["files_changed"] + changed_files

        print(f"Current changed files: {changed_files}")
        print(f"Accumulated files: {total_files}/{self.files_threshold}")

        if changed_files > 0:
            if total_files >= self.files_threshold:
                print(f"\n[INFO] Threshold reached ({self.files_threshold} files)")

                # Commit changes
                if self.commit_changes(f"Auto commit: {total_files} files changed"):
                    # Force push
                    if self.force_push():
                        # Reset state
                        state["files_changed"] = 0
                        state["last_push"] = datetime.now().isoformat()
                        self.save_state(state)
                        print("[OK] Auto-push cycle complete")
                        return True
            else:
                # Update state with accumulated count
                state["files_changed"] = total_files
                self.save_state(state)

        return False

    def monitor_and_push(self, interval_seconds=60):
        """Continuously monitor and push when threshold reached."""
        print(f"[START] Auto GitHub Push System started")
        print(f"[REPO] Repository: {self.repo_path}")
        print(f"[THRESHOLD] Files threshold: {self.files_threshold} files")
        print(f"[INTERVAL] Check interval: {interval_seconds} seconds")
        print(f"[INFO] Press Ctrl+C to stop\n")

        try:
            while True:
                self.check_and_push()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n[STOP] Auto GitHub Push System stopped")


def main():
    """Main entry point."""
    pusher = AutoGitHubPush(repo_path="c:\\dix_vision_v42.2", files_threshold=30)

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run once
        pusher.check_and_push()
    else:
        # Continuous monitoring
        pusher.monitor_and_push(interval_seconds=60)


if __name__ == "__main__":
    main()

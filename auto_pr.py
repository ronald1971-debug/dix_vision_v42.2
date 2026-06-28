#!/usr/bin/env python3
"""
Auto GitHub PR System
Automatically creates PRs every 30 files changed.
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path


class AutoGitHubPR:
    def __init__(self, repo_path="c:\\dix_vision_v42.2", files_threshold=30):
        self.repo_path = Path(repo_path)
        self.files_threshold = files_threshold
        self.state_file = self.repo_path / ".devin" / "auto_pr_state.json"
        self.git_exe = "git"
        self.github_repo = "ronald1971-debug/dix_vision_v42.2"

    def load_state(self):
        """Load the current state from file."""
        if self.state_file.exists():
            with open(self.state_file, "r") as f:
                return json.load(f)
        return {"files_changed": 0, "last_pr": None, "last_commit": None, "pr_number": 0}

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

    def create_branch(self, branch_name):
        """Create and checkout a new branch."""
        success, _, stderr = self.run_git_command(f"git checkout -b {branch_name}")
        if success:
            print(f"[OK] Created branch: {branch_name}")
            return True
        else:
            print(f"[ERROR] Failed to create branch: {stderr}")
            return False

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

    def push_branch(self, branch_name):
        """Push branch to GitHub."""
        print(f"Pushing branch {branch_name} to GitHub...")
        success, stdout, stderr = self.run_git_command(f"git push -u origin {branch_name}")
        if success:
            print(f"[OK] Branch {branch_name} pushed successfully")
            return True
        else:
            print(f"[ERROR] Failed to push branch: {stderr}")
            return False

    def create_pr(self, branch_name, pr_number):
        """Create a pull request using gh CLI."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pr_title = f"Auto PR #{pr_number} - {timestamp} - {self.files_threshold} files changed"
        pr_body = f"""
## Auto-generated PR #{pr_number}

- **Files changed**: {self.files_threshold}
- **Generated**: {timestamp}
- **Branch**: {branch_name}

This PR was automatically created by the Auto GitHub PR system.

Generated with [Devin](https://devin.ai)
"""

        print(f"Creating PR #{pr_number}...")
        command = (
            f'gh pr create --base main --head {branch_name} --title "{pr_title}" --body "{pr_body}"'
        )
        success, stdout, stderr = self.run_git_command(command)

        if success:
            print(f"[OK] PR #{pr_number} created successfully")
            print(f"[INFO] PR URL: {stdout.strip() if stdout.strip() else 'Check GitHub'}")
            return True
        else:
            print(f"[ERROR] Failed to create PR: {stderr}")
            return False

    def switch_to_main(self):
        """Switch back to main branch."""
        success, _, stderr = self.run_git_command("git checkout main")
        if success:
            print("[OK] Switched to main branch")
            return True
        else:
            print(f"[ERROR] Failed to switch to main: {stderr}")
            return False

    def check_and_create_pr(self):
        """Check if threshold reached and create PR if needed."""
        state = self.load_state()
        changed_files = self.get_changed_files()

        total_files = state["files_changed"] + changed_files

        print(f"Current changed files: {changed_files}")
        print(f"Accumulated files: {total_files}/{self.files_threshold}")

        if changed_files > 0:
            if total_files >= self.files_threshold:
                print(f"\n[INFO] Threshold reached ({self.files_threshold} files)")

                # Increment PR number
                new_pr_number = state["pr_number"] + 1
                branch_name = f"auto-pr-{new_pr_number}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

                # Create branch
                if self.create_branch(branch_name):
                    # Commit changes
                    if self.commit_changes(
                        f"Auto PR #{new_pr_number}: {total_files} files changed"
                    ):
                        # Push branch
                        if self.push_branch(branch_name):
                            # Create PR
                            if self.create_pr(branch_name, new_pr_number):
                                # Switch back to main
                                if self.switch_to_main():
                                    # Reset state
                                    state["files_changed"] = 0
                                    state["last_pr"] = datetime.now().isoformat()
                                    state["pr_number"] = new_pr_number
                                    self.save_state(state)
                                    print("[OK] Auto-PR cycle complete")
                                    return True
            else:
                # Update state with accumulated count
                state["files_changed"] = total_files
                self.save_state(state)

        return False

    def monitor_and_create_pr(self, interval_seconds=60):
        """Continuously monitor and create PRs when threshold reached."""
        print(f"[START] Auto GitHub PR System started")
        print(f"[REPO] Repository: {self.github_repo}")
        print(f"[THRESHOLD] Files threshold: {self.files_threshold} files")
        print(f"[INTERVAL] Check interval: {interval_seconds} seconds")
        print(f"[INFO] Press Ctrl+C to stop\n")

        try:
            while True:
                self.check_and_create_pr()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n[STOP] Auto GitHub PR System stopped")


def main():
    """Main entry point."""
    pr_system = AutoGitHubPR(repo_path="c:\\dix_vision_v42.2", files_threshold=30)

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run once
        pr_system.check_and_create_pr()
    else:
        # Continuous monitoring
        pr_system.monitor_and_create_pr(interval_seconds=60)


if __name__ == "__main__":
    main()

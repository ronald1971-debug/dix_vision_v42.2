# Auto GitHub PR System

## Overview
This system automatically creates Pull Requests every 30 files that are modified by Devin.

## Components

### 1. auto_pr.py
Main script that monitors file changes and automatically creates PRs when the threshold is reached.

**Usage:**
```bash
# Run once (check and create PR if needed)
python auto_pr.py --once

# Run continuously (monitor every 60 seconds)
python auto_pr.py
```

**Features:**
- Tracks number of files changed
- Creates new branch when threshold (30 files) is reached
- Commits changes to the new branch
- Pushes branch to GitHub
- Creates Pull Request using GitHub CLI
- Switches back to main branch
- Maintains state between runs
- Configurable threshold and check interval

**Requirements:**
- GitHub CLI (`gh`) must be installed and authenticated
- Git must be installed
- Write access to the target repository

### 2. check_pr_status.py
Utility script to check the current status of the auto-PR system.

**Usage:**
```bash
python check_pr_status.py
```

**Output:**
- Shows number of files accumulated toward threshold
- Shows last PR number created
- Shows last PR creation timestamp
- Indicates if threshold is reached or how many more files needed

### 3. .devin/config.json
Configuration file for Devin integration.

**Settings:**
- `auto_github_push.enabled`: Enable/disable auto-PR (legacy name, still used)
- `auto_github_push.files_threshold`: Number of files before auto-PR (default: 30)
- `auto_github_push.repo_path`: Repository path
- `auto_github_push.force_push`: Now ignored (system uses PRs instead)

### 4. .devin/auto_pr_state.json
State file that tracks:
- Number of files changed since last PR
- Last PR timestamp
- Last PR number
- Last commit hash

## How It Works

1. **File Change Detection**: The script checks git status for modified/added files
2. **Accumulation**: Changes are accumulated until the threshold (30 files) is reached
3. **Branch Creation**: When threshold reached, a new branch is created (e.g., `auto-pr-1-20240618-143000`)
4. **Auto Commit**: Changes are committed to the new branch
5. **Branch Push**: The new branch is pushed to GitHub
6. **PR Creation**: A Pull Request is created using GitHub CLI
7. **Main Switch**: System switches back to main branch
8. **State Reset**: Counter resets after successful PR creation

## Configuration

To change the threshold or other settings, edit `.devin/config.json`:

```json
{
  "auto_github_push": {
    "enabled": true,
    "files_threshold": 30,
    "repo_path": "c:\\dix_vision_v42.2",
    "auto_commit_message": "Auto commit by Devin",
    "force_push": false
  }
}
```

## Manual Override

To manually check and create a PR:
```bash
python auto_pr.py --once
```

To check current status:
```bash
python check_pr_status.py
```

## Integration with Devin

The system is configured to run automatically after file edits through the Devin hooks in `.devin/config.json`.

## Target Repository

- **Repository**: https://github.com/ronald1971-debug/dix_vision_v42.2
- **Branch**: main (base for all PRs)
- **PR Method**: GitHub CLI (`gh pr create`)

## GitHub CLI Setup

If GitHub CLI is not installed:

**Windows:**
```bash
winget install --id GitHub.cli
```

**Authentication:**
```bash
gh auth login
```

## Important Notes

- This system creates Pull Requests instead of force pushing
- Each PR contains exactly 30 files (or the threshold configured)
- PR branches are named with format: `auto-pr-{number}-{timestamp}`
- GitHub CLI must be installed and authenticated
- State is preserved between script runs
- Works with any git repository with GitHub remote

## PR Workflow

1. Files are modified by Devin during work
2. Every 30 files, a new PR is automatically created
3. PR includes detailed information about changes
4. You can review and merge PRs as needed
5. System continues tracking for next batch of 30 files

## Benefits Over Force Push

- Safer workflow (no history rewriting)
- Better change tracking and review
- Easier to revert if needed
- Clear separation of work batches
- Better collaboration support
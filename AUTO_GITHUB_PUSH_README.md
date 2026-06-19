# Auto GitHub Push System

## Overview
This system automatically force pushes changes to GitHub every 30 files that are modified by Devin.

## Components

### 1. auto_github_push.py
Main script that monitors file changes and automatically commits/force pushes when the threshold is reached.

**Usage:**
```bash
# Run once (check and push if needed)
python auto_github_push.py --once

# Run continuously (monitor every 60 seconds)
python auto_github_push.py
```

**Features:**
- Tracks number of files changed
- Automatically commits changes when threshold (30 files) is reached
- Force pushes to GitHub repository
- Maintains state between runs
- Configurable threshold and check interval

### 2. check_push_status.py
Utility script to check the current status of the auto-push system.

**Usage:**
```bash
python check_push_status.py
```

**Output:**
- Shows number of files accumulated toward threshold
- Shows last push timestamp
- Shows last commit hash
- Indicates if threshold is reached or how many more files needed

### 3. .devin/config.json
Configuration file for Devin integration.

**Settings:**
- `auto_github_push.enabled`: Enable/disable auto-push
- `auto_github_push.files_threshold`: Number of files before auto-push (default: 30)
- `auto_github_push.repo_path`: Repository path
- `auto_github_push.force_push`: Use force push (true/false)

### 4. .devin/auto_push_state.json
State file that tracks:
- Number of files changed since last push
- Last push timestamp
- Last commit hash

## How It Works

1. **File Change Detection**: The script checks git status for modified/added files
2. **Accumulation**: Changes are accumulated until the threshold (30 files) is reached
3. **Auto Commit**: When threshold reached, changes are automatically committed
4. **Force Push**: Committed changes are force pushed to GitHub
5. **State Reset**: Counter resets after successful push

## Configuration

To change the threshold or other settings, edit `.devin/config.json`:

```json
{
  "auto_github_push": {
    "enabled": true,
    "files_threshold": 30,
    "repo_path": "c:\\dix_vision_v42.2",
    "auto_commit_message": "Auto commit by Devin",
    "force_push": true
  }
}
```

## Manual Override

To manually check and push:
```bash
python auto_github_push.py --once
```

To check current status:
```bash
python check_push_status.py
```

## Integration with Devin

The system is configured to run automatically after file edits through the Devin hooks in `.devin/config.json`.

## Target Repository

- **Repository**: https://github.com/ronald1971-debug/dix_vision_v42.2
- **Branch**: main
- **Push Method**: force push

## Important Notes

- This system uses force push, which rewrites git history
- The threshold is set to 30 files by default
- State is preserved between script runs
- Works with any git repository
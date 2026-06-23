# How to Delete Archived Sessions from Inside the IDE

## 📋 **From Within VS Code / Windsurf**

### **Method 1: Using Command Palette (F1 or Ctrl+Shift+P)**

1. **Open Command Palette**: Press `F1` or `Ctrl+Shift+P`
2. **Type**: "Delete File" or "File: Delete"
3. **Navigate to**: `containers/development/checkpoints/`
4. **Select the session files** you want to delete
5. **Confirm deletion**

### **Method 2: Using Integrated Terminal**

1. **Open Terminal**: Press `Ctrl+`` ` (backtick) or `View` → `Terminal`
2. **Navigate to session directory**:
   ```bash
   cd containers/development/checkpoints
   ```
3. **List files**: `ls` or `dir`
4. **Delete specific files**:
   ```bash
   rm integrated_*.json
   rm test_*.json
   ```
5. **Or delete all session files**:
   ```bash
   rm *.json
   ```

### **Method 3: Using File Explorer Panel**

1. **Open File Explorer**: Press `Ctrl+Shift+E` or click the File icon in the left sidebar
2. **Navigate to**: `containers/development/checkpoints/`
3. **Right-click on session files** you want to delete
4. **Select "Delete"**

### **Method 4: Using Source Control Panel**

If the session files are tracked in git:
1. **Open Source Control**: Click the Git icon (Ctrl+Shift+G)
2. **Select the session files** from Changes view
3. **Right-click** → "Delete"

### **Method 5: Using Search and Delete**

1. **Open Search**: Press `Ctrl+Shift+F`
2. **Search for**: `*.json` in `containers/development/checkpoints`
3. **Right-click results** → "Delete"

## 🔄 **Built-in IDE Session Management**

### **VS Code / Windsurf Session Management**

1. **Open Settings**: Press `Ctrl+,` (comma)
2. **Search for**: "restore windows"
3. **Setting**: `window.restoreWindows`
   - **"all"**: Opens all sessions (may cause OOM)
   - **"folders"**: Opens only folders
   - **"one"**: Opens only one folder (RECOMMENDED)
   - **"none"**: Starts fresh (RECOMMENDED for OOM issues)

### **Clear Recent Files/Folders**

1. **File** → `Open Recent` → `Clear Recently Opened`
2. **File** → `Open Recent` → `Clear Recently Opened Folders`

### **Delete Workspace/Session State**

1. **File** → `Close Folder` (if a folder is open)
2. **File** → `Save Workspace As...` (optional, to save current state)
3. **File** → `Close Workspace`

## 🎯 **Recommended Approach for Your OOM Issue**

### **Step-by-Step from Inside IDE:**

1. **Close current workspace/session**:
   ```
   File → Close Workspace
   ```

2. **Open Integrated Terminal**:
   ```
   Ctrl+` (backtick)
   ```

3. **Navigate and delete session files**:
   ```bash
   cd containers/development/checkpoints
   rm *.json
   ```

4. **Clear remaining caches**:
   ```bash
   # From project root
   cd ../../..
   python memory_optimization.ps1
   ```

5. **Restart IDE**:
   ```
   File → Exit
   (reopen IDE)
   ```

6. **Change session restore setting**:
   ```
   Press Ctrl+, → search "window.restoreWindows"
   Set to: "none" or "one"
   ```

## 💡 **Quick Commands from Terminal**

### **Delete all checkpoint sessions**:
```bash
rm containers/development/checkpoints/*.json
```

### **Delete specific session types**:
```bash
# Only integrated sessions
rm containers/development/checkpoints/integrated_*.json

# Only test sessions
rm containers/development/checkpoints/test_*.json
```

### **Delete from archive folder**:
```bash
rm containers/development/checkpoints/archive/*.json
```

### **Clear all project caches**:
```bash
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
rm -rf temp_extract
```

## ⚠️ **Important Settings to Change from IDE**

### **Prevent Automatic Session Restoration (Causes OOM)**

1. **Press**: `Ctrl+,` (settings)
2. **Search**: "restore windows"
3. **Change**: `window.restoreWindows: "all"` → `"none"` or `"one"`
4. **Search**: "restore folders"
5. **Change**: `window.restoreFolders: true` → `false`

### **Disable Unnecessary Features**

1. **Settings**: `Ctrl+,`
2. **Search**: "enable session restore"
3. **Disable**: Any session-related features that restore state

## 🔧 **Run Memory Tools from Terminal**

From the IDE's integrated terminal, you can run:

```bash
# Memory optimization
python memory_optimization.ps1

# Devin memory check
python devin_memory_optimizer.py

# Targeted OOM fix
python targeted_oom_fix.py

# Session manager (interactive)
python delete_archived_sessions.py
```

## 📱 **One-Liner Commands for Quick Action**

Copy and paste these into your terminal:

```bash
# Delete all session files at once
rm containers/development/checkpoints/*.json && echo "Sessions deleted"

# Delete and then clear caches
rm containers/development/checkpoints/*.json && python memory_optimization.ps1

# Delete sessions, clear caches, restart later
rm containers/development/checkpoints/*.json && rm -rf __pycache__ && rm -rf temp_extract
```

The easiest method from inside the IDE is to use the **integrated terminal** and delete the session files directly. This gives you immediate control and you can see the results in real-time.
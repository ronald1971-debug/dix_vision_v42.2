# Create Desktop Shortcut for DIX VISION Desktop AgentOS

$DesktopPath = "C:\Users\prive\Desktop"
$ProjectPath = "C:\dix_vision_v42.2"
$ShortcutPath = "$DesktopPath\DIX DESKTOP.lnk"
$PythonScript = "$ProjectPath\launch_dix_vision_desktop.py"
$PythonExe = "python"

# Create WScript Shell object
$WshShell = New-Object -ComObject WScript.Shell

# Create shortcut
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $PythonExe
$Shortcut.Arguments = "`"$PythonScript`""
$Shortcut.WorkingDirectory = $ProjectPath
$Shortcut.Description = "DIX VISION Desktop AgentOS - Interactive Cognitive Environment Platform"
$Shortcut.IconLocation = "$ProjectPath\komorebi_desktop\src-tauri\icons\128x128.png"

# Save shortcut
$Shortcut.Save()

Write-Host "Desktop shortcut created: $ShortcutPath" -ForegroundColor Green

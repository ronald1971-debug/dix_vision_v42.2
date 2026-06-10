# Create Desktop Shortcut for DIX VISION Desktop AgentOS

$DesktopPath = "C:\Users\prive\Desktop"
$ProjectPath = "C:\dix_vision_v42.2"
$ShortcutPath = "$DesktopPath\DIX DESKTOP.lnk"
$TargetPath = "C:\dix_vision_v42.2\LAUNCH_DIX_VISION_DESKTOP.bat"

# Create WScript Shell object
$WshShell = New-Object -ComObject WScript.Shell

# Create shortcut
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $ProjectPath
$Shortcut.Description = "DIX VISION Desktop AgentOS - Interactive Cognitive Environment Platform"

# Try to set icon (will fail if icon doesn't exist, but won't crash)
try {
    $IconPath = "$ProjectPath\dix_desktop\src-tauri\icons\128x128.png"
    if (Test-Path $IconPath) {
        $Shortcut.IconLocation = $IconPath
    }
} catch {
    # Icon not available, continue without it
}

# Save shortcut
$Shortcut.Save()

Write-Host "Desktop shortcut created: $ShortcutPath" -ForegroundColor Green

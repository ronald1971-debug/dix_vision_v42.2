# DIX VISION v42.2+ Desktop Shortcut Creator
# Creates Windows desktop shortcut for DIX VISION launcher

$WshShell = New-Object -ComObject WScript.Shell

# Script paths
$ProjectDir = "C:\dix_vision_v42.2"
$ScriptPath = "$ProjectDir\start_dix_vision_system.bat"
$ShortcutPath = "$env:USERPROFILE\Desktop\DIX VISION Desktop Agent.lnk"

# Create shortcut
Write-Host "Creating desktop shortcut..." -ForegroundColor Cyan
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)

$Shortcut.TargetPath = $ScriptPath
$Shortcut.WorkingDirectory = $ProjectDir
$Shortcut.Description = "DIX VISION v42.2+ Complete System Launcher with INDIRA Cognitive Center"
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully: $ShortcutPath" -ForegroundColor Green
Write-Host "You can now launch DIX VISION Complete System from your desktop!" -ForegroundColor Green
Write-Host ""
Write-Host "To remove the shortcut, delete: $ShortcutPath" -ForegroundColor Yellow
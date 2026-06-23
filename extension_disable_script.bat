@echo off
echo Extension Management for Language Server Error
echo.

echo This script will help identify problematic extensions
echo.

echo Step 1: Check installed extensions...
if exist "%USERPROFILE%\.vscode\extensions" (
    echo Found extensions directory:
    dir "%USERPROFILE%\.vscode\extensions" /b
) else (
    echo No extensions directory found
)

echo.
echo Step 2: Common problematic extensions for this error:
echo - Python extension (ms-python.python)
echo - Pylance extension (ms-python.vscode-pylance)
echo - Jupyter extension (ms-toolsai.jupyter)
echo - Copilot/Chat extensions
echo.

echo Step 3: Manual extension disable instructions:
echo 1. Open your IDE
echo 2. Press Ctrl+Shift+X to open Extensions
echo 3. Disable ALL extensions
echo 4. Restart IDE
echo 5. Check if error is gone
echo 6. If gone, re-enable extensions one by one
echo 7. Identify which extension causes the error
echo.

echo Step 4: Alternative - create clean workspace:
echo 1. Close IDE
echo 2. Rename .vscode folder to .vscode_backup
echo 3. Restart IDE
echo 4. Test if error persists
echo.

pause
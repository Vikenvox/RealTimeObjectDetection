@echo off
echo Creating desktop shortcut...
set "shortcut_path=%USERPROFILE%\Desktop\Real-Time Object Detection.lnk"
set "target_path=%~dp0run_detection.bat"
set "icon_path=%~dp0run_detection.bat"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%shortcut_path%'); $Shortcut.TargetPath = '%target_path%'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Real-Time Object Detection with YOLOv8'; $Shortcut.Save()"

echo Desktop shortcut created successfully!
echo You can now double-click "Real-Time Object Detection" on your desktop to run the app.
pause

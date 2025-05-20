@echo off
echo Cleaning up AI-Assistant face data...
rmdir /s /q "%LOCALAPPDATA%\AI-Assistant\face_data" 2>nul
rmdir /s /q "%LOCALAPPDATA%\AI-Assistant" 2>nul
echo Cleanup complete.
exit 0 
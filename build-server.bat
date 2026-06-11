@echo off
echo Starting Odysseus Backend Compilation...

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo Virtual environment not found! Run launch-windows.ps1 first.
    pause
    exit /b 1
)

REM Ensure Nuitka is installed
echo Installing/updating Nuitka...
call venv\Scripts\python.exe -m pip install Nuitka zstandard --quiet

REM Nuitka command
echo Compiling server.exe (this will take a while)...
call venv\Scripts\python.exe -m nuitka ^
    --standalone ^
    --windows-disable-console ^
    --show-progress ^
    --show-memory ^
    --jobs=10 ^
    --include-data-dir=static=static ^
    --include-data-dir=integrations=integrations ^
    --include-data-dir=mcp_servers=mcp_servers ^
    --nofollow-import-to=*.tests,*.testing,PIL ^
    --output-dir=build ^
    server.py

echo Compilation Complete! Server.exe is in build\server.dist\
pause
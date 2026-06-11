@echo off
setlocal enabledelayedexpansion

REM Odysseus - Desktop Build Script
REM Compiles the Electron wrapper into a native Windows .exe.

echo.
echo ^=^=^> Step 2: Building Electron Desktop Wrapper...
set "desktopDir=%CD%\desktop"

if not exist "%desktopDir%\node_modules" (
    echo.
    echo ^=^=^> Installing Desktop dependencies...
    pushd "%desktopDir%"
    call npm install
    popd
)

echo.
echo ^=^=^> Cleaning up previous desktop build...

REM Kill any running Electron processes
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq electron.exe" /fo csv 2^>nul ^| findstr /i "electron"') do (
    taskkill /f /pid %%~a >nul 2>&1
)

timeout /t 1 /nobreak >nul

if exist "%desktopDir%\dist" (
    rmdir /s /q "%desktopDir%\dist" 2>nul
)

echo.
echo ^=^=^> Packaging Odysseus Native App...
pushd "%desktopDir%"
call npm run dist
popd

echo.
echo ^=^=^> Master Build Complete!
echo You can find the integrated native app in: desktop\dist\
echo The app now contains the Nuitka-compiled backend inside the package.
echo.

pause
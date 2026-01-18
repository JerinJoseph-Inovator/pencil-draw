@echo off
echo ============================================
echo   Building Pencil Draw Executable
echo ============================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install PyInstaller if not present
pip install pyinstaller --quiet

REM Clean previous builds
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo.
echo Building executable...
echo.

REM Build the executable
pyinstaller build.spec --clean

echo.
if exist "dist\PencilDraw.exe" (
    echo ============================================
    echo   BUILD SUCCESSFUL!
    echo ============================================
    echo.
    echo Executable created at:
    echo   dist\PencilDraw.exe
    echo.
    echo To use:
    echo   1. Copy dist\PencilDraw.exe to any folder
    echo   2. Double-click to start the server
    echo   3. Open https://jerinjoseph-inovator.github.io/pencil-draw
    echo.
) else (
    echo ============================================
    echo   BUILD FAILED
    echo ============================================
    echo Check the error messages above.
)

pause

@echo off
REM Install required Python packages for Stripe Snoop

echo Installing required Python packages...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install Python packages. Make sure pip is installed and in your PATH.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Installation complete!
echo.
echo To launch the application, run:
echo    python launch_gui.py
echo.
pause

@echo off
echo.
echo ========================================
echo   EventSpot Research Tool - Setup
echo ========================================
echo.
echo Installing required packages...
echo.
python -m pip install "scrapling[all]" firebase-admin requests playwright
echo.
echo Setting up browser for scraping...
echo.
python -m playwright install chromium
echo.
echo ========================================
echo   Setup complete!
echo ========================================
echo.
echo NEXT STEP: You need a Firebase service account key.
echo   1. Go to https://console.firebase.google.com
echo   2. Open your project "eventspot-zurich"
echo   3. Click the gear icon (Project Settings)
echo   4. Go to "Service Accounts" tab
echo   5. Click "Generate New Private Key"
echo   6. Save the downloaded file as:
echo      research-tool\service-account-key.json
echo.
echo Once you have the key file, run "run.bat" to start scraping!
echo.
pause

@echo off
echo.
echo ========================================
echo   EventSpot Research Tool
echo ========================================
echo.

REM Check if service account key exists
if not exist "%~dp0service-account-key.json" (
    echo ERROR: service-account-key.json not found!
    echo.
    echo You need to download it first:
    echo   1. Go to https://console.firebase.google.com
    echo   2. Open project "eventspot-zurich"
    echo   3. Click gear icon ^> Project Settings
    echo   4. Go to "Service Accounts" tab
    echo   5. Click "Generate New Private Key"
    echo   6. Save the file in this folder as "service-account-key.json"
    echo.
    pause
    exit /b 1
)

echo What would you like to do?
echo.
echo   1 = Preview events (dry run, no changes)
echo   2 = Scrape and add events to EventSpot
echo   3 = Scrape only Gemeinde calendars
echo   4 = Scrape only Ron Orp
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Running dry run (preview only)...
    echo.
    python "%~dp0scraper.py" --dry-run
) else if "%choice%"=="2" (
    echo.
    echo Scraping all sources and adding to EventSpot...
    echo.
    python "%~dp0scraper.py"
) else if "%choice%"=="3" (
    echo.
    echo Scraping Gemeinde calendars...
    echo.
    python "%~dp0scraper.py" --source gemeinde
) else if "%choice%"=="4" (
    echo.
    echo Scraping Ron Orp...
    echo.
    python "%~dp0scraper.py" --source ronorp
) else (
    echo Invalid choice. Please enter 1, 2, 3, or 4.
)

echo.
pause

@echo off
REM ========================================
REM   EventSpot Research Tool - Scheduled Run
REM ========================================
REM This script is designed to run automatically via Windows Task Scheduler.
REM It scrapes all sources and adds new events to EventSpot.
REM Duplicates are automatically skipped.
REM
REM TO SET UP AUTOMATIC DAILY RUNS:
REM   1. Press Windows key, type "Task Scheduler", open it
REM   2. Click "Create Basic Task" on the right
REM   3. Name: "EventSpot Research"
REM   4. Trigger: Daily, pick a time (e.g. 08:00)
REM   5. Action: Start a program
REM   6. Program: Browse to this file (scheduled-run.bat)
REM   7. Start in: Enter the folder path of this file
REM   8. Click Finish
REM
REM The script logs output to "last-run.log" so you can check what happened.

cd /d "%~dp0"
echo [%date% %time%] Starting scheduled scrape... >> last-run.log
python "%~dp0scraper.py" >> last-run.log 2>&1
echo [%date% %time%] Done. >> last-run.log
echo. >> last-run.log

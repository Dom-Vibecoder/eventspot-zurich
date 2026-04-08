=============================================
  EventSpot Research Tool - Quick Guide
=============================================

This tool scrapes event websites and adds real events to your EventSpot app.

FIRST TIME SETUP (only once):
-----------------------------
1. Double-click "setup.bat"
   -> This installs everything automatically

2. Get your Firebase key:
   -> Go to https://console.firebase.google.com
   -> Open your project "eventspot-zurich"
   -> Click the gear icon (top left) > "Project Settings"
   -> Click "Service Accounts" tab
   -> Click "Generate New Private Key"
   -> Save the downloaded .json file into THIS folder
   -> Rename it to: service-account-key.json

RUNNING THE TOOL:
-----------------
1. Double-click "run.bat"
2. Choose an option:
   - Option 1: Preview only (see what events it finds, no changes)
   - Option 2: Scrape all sources and add events to EventSpot
   - Option 3: Scrape only Gemeinde calendars
   - Option 4: Scrape only Ron Orp

IMPORTANT:
----------
- Always try Option 1 (preview) first to check everything works!
- Events appear in your app within seconds after scraping
- The tool skips events that already exist (no duplicates)
- Each event shows "EventSpot Research · via [source]" as the poster

NEED HELP?
----------
Ask Claude Code! Just describe what's happening and paste any error messages.

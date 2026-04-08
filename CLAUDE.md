# EventSpot Zürich — Project Memory

## What this is
A web app for discovering spontaneous and planned local events in Zürich. Full-screen Google Maps with real-time event markers, floating search bar, and filter pills.

**Local testing:** VS Code Live Server at http://127.0.0.1:5500
**GitHub:** `Dom-Vibecoder/eventspot-zurich` → auto-deploys to Vercel
**Live URL:** https://eventspot-zurich-tc3f.vercel.app (also aliased to eventspot-zurich.vercel.app)

---

## Workflow
1. Build one feature at a time
2. Test at http://127.0.0.1:5500
3. Confirm with Domenic → then continue
4. Update CLAUDE.md at end of session

---

## Tech Stack
- **Google Maps API** — standard markers only (NOT AdvancedMarkerElement)
- **Firebase Firestore** — real-time event sync
- **Firebase Auth** — Google sign-in + anonymous
- **Vercel** — hosting (auto-deploy from GitHub main branch)
- **PWA** — service worker + manifest
- **Scrapling** — Python scraping library for AI research tool (`research-tool/`)
- **Firebase Admin SDK** — server-side Firestore writes from research tool
- **Community Skills** — installed at `.claude/skills/` (ui-ux-pro-max, ui-ux-designer, etc.)

---

## Architecture — CRITICAL RULES

**1. Never replace innerHTML of the map container.**
Google Maps is destroyed if its parent div is removed. This was the #1 recurring bug.

**2. Zone-based rendering** — `#map` is ALWAYS persistent, never touched after `initMap()`:

| Zone | Purpose | Z-index |
|------|---------|---------|
| `#zH` | Search bar + filter pills | 150 |
| `#zM` | Map container (100dvh) | — |
| `#map` | Google Maps inside #zM | — |
| `#zB` | Bottom sheet (event feed list) | 8 |
| `#zO` | HUD: locbtn, list-toggle, FAB | 10 |
| `#zC` | Event card (peek + full) | 200 |
| `#zMo` | Add event modal | 500 |
| `#zA` | Auth screen | 800 |
| `#zT` | Toast notifications | 900 |

**3. Single-file architecture** — ALL code lives in `index.html`. No separate JS/CSS files.

---

## Design System

### Colors (CSS variables)
```css
:root {
  --bg:#0a0818; --card:#14112e; --surface:#1c1838; --raised:#28234a;
  --accent:#7c6aff; --accent2:#a99cff; --glow:rgba(124,106,255,.2);
  --green:#34d399; --greend:#0d9f6e; --red:#f87171;
  --t1:#ede8ff; --t2:#a49bbe; --t3:#7a7394;
  --border:rgba(255,255,255,.07);
}
```

### Typography
- Font: **Outfit** (Google Fonts) — geometric modern
- Body: 400-600 weight, Headings: 700-900 weight

### Glassmorphic UI
- Dark purple theme on a **bright white Google Map**
- Semi-transparent backgrounds (`rgba(20,17,46,.72)`) + `backdrop-filter:blur(14px)`
- Text shadow on map-overlaying elements: `text-shadow:0 1px 3px rgba(0,0,0,.3)`
- Mobile-first, safe-area insets (`--top`, `--bot`)

### Filter Pills
- Default (`.fp`): dark glass bg, light text (`--t1`), subtle border
- Selected (`.fp.on`): bright accent bg (`rgba(124,106,255,.35)`), **dark text** (`#1a1730`), accent border, no text-shadow
- Category emojis on markers (🎵🍔🎉) are intentional brand identity — NOT functional UI icons

### SVG Icon System
- `IC` object with factory functions: `music`, `food`, `bonfire`, `party`, `community`, `protest`, `market`, `sport`, `art`, `plus`, `x`, `check`, `xc`, `clock`, `eye`, `nav`, `pin`, `cross`, `share`, `search`, `user`
- All functional UI uses SVG icons (no emojis for buttons/controls)

---

## Accessibility (implemented)
- **Focus states:** `:focus-visible` outline on all interactive elements (2px solid accent)
- **Reduced motion:** `@media(prefers-reduced-motion:reduce)` disables animations
- **ARIA labels:** All icon-only buttons have `aria-label` (Mein Standort, Schliessen, Teilen, Suche löschen, Profil, Events suchen)
- **Touch targets:** Minimum 44x44px on primary buttons (locbtn), 36x36px on secondary (closex, avatar)
- **Cursor:** `cursor:pointer` on all clickable elements
- **Touch delay:** `touch-action:manipulation` on body (eliminates 300ms delay)
- **Color contrast:** `--t2` at ~4.8:1 ratio on dark bg, `--t3` at ~3.2:1 (large text only)

---

## Current Features

- **Map:** Full-screen Google Maps, emoji SVG markers (44x44), radar pulse rings on spontaneous events
- **Search bar:** Floating glassmorphic pill, real-time text filter, SVG search icon, avatar with sign-in/out
- **Filter pills:** Category filters, toggleable, date filter row (Heute/Morgen/Wochenende/custom), dark text on selected
- **Bottom sheet:** Draggable event feed, distance-sorted, respects filters + search
- **Event cards:** Tap marker → peek card with slide-up, expand to full, swipe-down to close, share button
- **Voting:** Confirm/decline within 300m, one vote per device (localStorage), Firestore sync with rollback
- **Add event:** FAB → modal, spontaneous (duration) or planned (date+time required)
- **Event auto-expiry:** Spontaneous events expire after their duration (1h/2h/5h/18h), planned events 3h after start. Live countdown shown in feed and cards ("LIVE · Noch 45 Min"). UI refreshes every 60s. Expired events auto-hide from map/feed.
- **Extend event:** Creators of spontaneous events can extend by +1/+2/+3 Std. Updates the `time` field (e.g. "Jetzt · ~4 Std"). No new Firestore fields needed — `durToHours()` parses extended format.
- **Share:** Native Web Share API + clipboard fallback, deep links via `#event=<id>` in URL hash
- **Auth:** Google sign-in or anonymous, SVG avatar fallback
- **PWA:** Installable, service worker
- **Google Maps error suppression:** CSS + MutationObserver auto-dismisses Maps error dialogs

---

## Key State Variables
```js
curFilter = 'all'       // filter pill key (toggleable)
searchQuery = ''        // text search
cardMode = 'none'       // 'none' | 'peek' | 'full'
listMode = false        // list view
selEv = null            // selected event
vState = 'idle'         // verify: idle|checking|nearby|too_far|denied|unavailable
myPos = null            // {lat,lng}
dateFilter = null       // null | 'YYYY-MM-DD' | ['start','end']
deepLinkHandled = false // prevents re-trigger on Firestore snapshots
// Expiry functions: durToHours(), getExpiry(), isExpired(), timeLeft(), extendEvent()
// 60s setInterval refreshes UI for live countdowns
```

---

## Firestore Data
- Collection: `events`, ordered by `createdAt desc`
- Fields: `name`, `type`, `category`, `lat`, `lng`, `time`, `description`, `confirmed`, `declined`, `postedBy`, `postedByUid`, `createdAt`, `eventDate`, `infoUrl`
- **Do NOT add new fields** — Firestore rules reject unknown fields. Use existing fields creatively (e.g. extend uses `time` field).

---

## Known Issues & Notes
- **Markers disappearing** = innerHTML replacement near map div. Use zone rendering.
- **Local dev:** Add `localhost` + `127.0.0.1` to Google Cloud API key + Firebase authorized domains
- **Firestore rules:** Updated 2026-04-07 — test mode rules had expired. Now using proper rules: public read, auth required for create/update, only creator can delete. Rules are in Firebase Console → Firestore → Rules.
- **Expiry is client-side only** — no `expiresAt` field in Firestore (rules reject unknown fields). Expiry calculated from `createdAt` + parsed duration. Extend works by updating the `time` field.
- **Image upload:** BLOCKED — Firebase Storage not activated. Needs: activate in console (europe-west6), set rules (5MB limit, auth required), add SDK script tag, then build upload UI
- **Windows Python scripts:** Use `PYTHONIOENCODING=utf-8` prefix when running `.claude/skills/` Python scripts (Windows cp1252 encoding breaks emoji output)

---

## Research Tool (`research-tool/`)

Local Python script that scrapes Zürich event websites and writes to Firestore.

### File Structure
```
research-tool/
├── setup.bat                 # Double-click to install everything (first time only)
├── run.bat                   # Double-click to run scraper (menu with options)
├── README.txt                # Quick guide for Domenic
├── scraper.py                # Main entry: orchestrates sources, dedup, Firestore writes
├── category_map.py           # Maps scraped categories → EventSpot's 9 categories + skip filter
├── geocoder.py               # Address → lat/lng via Google Maps Geocoding API
├── requirements.txt          # scrapling[all], firebase-admin, requests
├── .gitignore                # Excludes service-account-key.json
├── service-account-key.json  # Firebase Admin credentials (GITIGNORED, NOT in repo)
└── sources/
    ├── gemeinde.py           # Gemeinde calendar scraper — WORKING (tested 17 events)
    └── ronorp.py             # Ron Orp event scraper — NOT WORKING YET (SPA empty)
```

### Usage (simple .bat scripts for Domenic)
1. **First time:** Double-click `setup.bat` → installs everything automatically
2. **Get Firebase key:** Firebase Console → Project Settings → Service Accounts → Generate New Private Key → save as `service-account-key.json` in the `research-tool/` folder
3. **Run:** Double-click `run.bat` → choose option 1 (preview) or 2 (scrape + add to app)

### Advanced usage (terminal)
```bash
cd research-tool
python scraper.py --dry-run          # Preview without writing to Firestore
python scraper.py                    # Scrape all sources → write to Firestore
python scraper.py --source gemeinde  # Scrape only Gemeinde calendars
python scraper.py --source ronorp    # Scrape only Ron Orp
python scraper.py --days 60          # Scrape 60 days ahead (default: 30)
```

### How it works
1. Scrapling `StealthyFetcher`/`DynamicFetcher` loads JS-rendered pages
2. CSS selectors extract event title, date, time, location, category
3. `category_map.py` maps to EventSpot's 9 categories
4. `geocoder.py` converts addresses → lat/lng (Google Maps Geocoding API)
5. Deduplication checks Firestore (name + date) before inserting
6. Firebase Admin SDK writes events with `postedBy: "EventSpot Research · via {source}"`

### Prerequisites
1. Service account key: Firebase Console → Project Settings → Service Accounts → Generate New Private Key → save as `research-tool/service-account-key.json`
2. Geocoding API enabled in Google Cloud Console (same project as Maps API)
3. Python 3.10+

---

## Roadmap

### Phase 1 — Prototype (current)
- [x] Core features (map, markers, search, filters, cards, list, voting, auth, PWA)
- [x] Planned events with date+time
- [x] Date filter row
- [x] Owner can delete own events
- [x] Share button + deep linking
- [x] Vercel hosting
- [x] Filter toggle (click to deselect)
- [x] UI/UX audit: accessibility, touch targets, SVG icons, contrast, cursor states
- [x] Event auto-expiry + live countdowns + extend feature
- [x] Firestore security rules (proper auth-based rules)
- [ ] Image upload ← BLOCKED on Firebase Storage

### Phase 2 — Real Data (IN PROGRESS)
- [ ] AI event research tool — local Python script using **Scrapling** library
  - **Status:** Gemeinde scraper WORKING + TESTED. 17 real events written to Firestore on 2026-04-08 from Üetikon am See. Firebase service account key is in place. Deduplication works (re-run skips existing events).
  - **What works:** Gemeinde scraper end-to-end (scrape → parse → geocode → dedup → Firestore write). `run.bat` double-click workflow.
  - **What doesn't work yet:** Ron Orp (SPA content comes back empty via StealthyFetcher), Eventfrog (not built yet), Stadt Zürich (not built yet)
  - **Dependencies installed on Domenic's machine:** `scrapling[all]`, `firebase-admin`, `playwright`, `requests` + Chromium browser
  - **Next steps:**
    1. Fix Ron Orp scraper (investigate SPA rendering / try different page URLs or API endpoints)
    2. Add more Gemeinden (uncomment/add lines in `sources/gemeinde.py` — same platform, just different URLs)
    3. Add Eventfrog + Stadt Zürich scrapers
    4. Improve geocoding accuracy (currently all events geocode to general "Üetikon am See" area — could use venue-specific addresses)
  - **Skip filter:** `category_map.py` auto-skips non-events (Altpapier, Karton, Sonderabfälle, etc.)
  - **Category mapping:** Checks both organizer name AND event name for keywords (e.g. "Djembé-Treff" → music, "Frühlingsfest" → party)

### Phase 2.5 — UX Polish
- [ ] Default to "Heute" date filter on load (users see today's events first)
- [ ] "Add to Calendar" button on planned event cards (generates .ics file with event name, date, time, location/coordinates, description)

### Phase 3 — Engagement
- [ ] Push notifications, user profiles, saved events

### Phase 4 — Mobile Apps
- [ ] Capacitor (iOS + Android)

### Phase 5 — Monetization
- [ ] Promoted events

---

## Owner
Domenic, Zürich. **Non-technical, no coding experience** — building entirely with AI assistance. Needs clear, step-by-step instructions without jargon. Prefers simple .bat scripts over terminal commands. Goal: validate concept with real users.

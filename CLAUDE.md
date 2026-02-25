# EventSpot Zürich — Project Memory

## What this is
A web app for discovering spontaneous and planned local events in Zürich. Targeted at business travelers and locals exploring the city. The core UI is a full-screen Google Maps interface with real-time event markers, a floating search bar, and filter pills.

**Local testing:** VS Code Live Server at http://127.0.0.1:5500
**GitHub:** connected to Netlify for auto-deploy (push to GitHub = live in ~1 min)
**Hosting:** Netlify free tier limit reached — switch to Vercel or Cloudflare Pages

---

## Development Workflow — BUILD → TEST → REPEAT

**This is mandatory for every feature going forward.**

1. **Plan** the feature (read PLAN.md, interview Domenic)
2. **Build** one feature at a time
3. **Test** it at http://127.0.0.1:5500 before moving on
4. **Confirm** it works with Domenic — only then continue to next feature
5. **Update CLAUDE.md** at the end of each session

Never stack multiple untested features. If something breaks, fix it before building anything new.

---

## Tech Stack
- **Google Maps API** — standard markers only (NOT AdvancedMarkerElement — caused bugs)
- **Firebase Firestore** — events stored and synced in real-time
- **Firebase Auth** — Google sign-in + anonymous access
- **GitHub** — version control
- **PWA** — service worker + manifest, installable on mobile

---

## Architecture — CRITICAL RULES

**1. Never replace the full innerHTML of the map container.**
Google Maps instances are destroyed if their parent div is removed or replaced. This was the core recurring bug. If markers disappear, check for any `container.innerHTML = ...` near the map div.

**2. Zone-based rendering**
- `#map` is ALWAYS persistent — never touched after `initMap()` runs
- UI updates happen in independent zones, each with its own draw function:

| Zone | Purpose | Z-index |
|------|---------|---------|
| `#zH` | Floating search bar + filter pills (position:absolute over map) | 150 |
| `#zM` | Map container (fills full screen, position:relative) | — |
| `#map` | Google Maps instance inside #zM | — |
| `#zL` | List view (position:absolute inside #zM) | 8 |
| `#zO` | HUD overlay — locbtn, list-toggle, FAB (position:absolute inside #zM) | 10 |
| `#zC` | Event card zone — peek + full card (position:absolute inside #zM) | 200 |
| `#zMo` | Add event modal (position:fixed) | 500 |
| `#zA` | Auth screen (position:fixed) | 800 |
| `#zT` | Toast notifications (position:fixed) | 900 |

**3. `#app` has `position:relative`** so `#zH` (position:absolute) is anchored to it correctly.

---

## File Structure
```
/index.html    — EVERYTHING lives here: HTML, CSS, JS (single-file architecture)
/manifest.json — PWA manifest
/sw.js         — PWA service worker
/icon-192.png  — PWA icon
/icon-512.png  — PWA icon
/CLAUDE.md     — project memory (this file)
/PLAN.md       — interview guide for planning new features
```
**No separate JS or CSS files — all code is in index.html.**

---

## Current Features (v4 — after UI redesign)

### Map & Markers
- Full-screen Google Maps (no header taking up space)
- Emoji SVG markers per category (44×44px)
- Spontaneous event markers pulse with radar rings (20px base, 2.5× scale, 2s, 3 rings staggered)
- Planned events have NO radar rings

### Search Bar (floating, Apple Maps style)
- `#zH` is `position:absolute` overlaying the map — map fills 100dvh
- Pill-shaped bar: 🔍 icon + text input + clear button (✕) + avatar
- Placeholder text: "EventSpot Zürich"
- Real-time text search: filters markers and list view as user types
- `searchQuery` state variable drives `getVis()` filtering
- Avatar: shows photo if Google-signed-in, 👤 otherwise; tap → sign out / sign in
- Avatar has `onerror` fallback — if photo URL fails to load, shows 👤 instead of broken image

### Filter Pills (persistent)
- Always-visible horizontal scrollable row below the search bar
- Categories: Alle, 🟣 Spontan, 🟢 Geplant, Musik, Essen, Lagerfeuer, Party, Community, Demo, Markt, Sport, Kunst
- `drawFilter()` renders into `#filterPills` div (never replaces full `#zH`)
- Active pill highlighted in purple

### HUD Controls (bottom of screen)
- **Location button** (`.locbtn`): bottom-left, `calc(100px + var(--bot))`
- **List toggle** (`.list-toggle`): bottom-left next to locbtn, switches ☰ / 🗺️
- **FAB** (`+` button): bottom-right, hidden when event card is open
- Legend and stats box removed

### Event Cards (2-state)
- `cardMode` variable: `'none' | 'peek' | 'full'`
- **Tap marker → full card opens directly** (peek mode no longer used for marker taps)
- **Peek card CSS**: still in code for potential future use, not triggered by marker taps
- **Full card**: detail view (title, time, description, credibility bar, verify + vote buttons)
  - Opens with `slideUp` animation
  - Closes with `slideDown` animation (220ms, then state clears)
  - Swipe down (>60px from top of sheet) → closes card
  - ✕ button or backdrop tap → closes with animation

### List View
- `listMode` boolean, `#zL` zone (z-index 8, inside `#zM`)
- Events sorted by distance from user (`hav()` computed at render time)
- Respects active filter + search query via `getVis()`
- Tap list item → `pickEvent(id)` → closes list, opens peek card on map
- `renderList()` called from `toggleListMode()`, `setFil()`, `onSearch()`, Firestore snapshot

### Auth
- Google sign-in or anonymous via Firebase Auth
- `avatarTap()` handles both sign-out (if logged in) and sign-in trigger
- Auth screen (`#zA`) covers everything at z-index 800

### Add Event (FAB)
- `+` button opens add event modal (`#zMo`)
- Fields: name, category (grid), description, duration (spontaneous) or date + time (planned)
- **Planned events require both date AND time** — validated in `submitEv()`, label shows "Uhrzeit *"
- Submit button stays grayed out until all required fields are filled
- Submits to Firestore with user's current location
- Firestore errors caught with `.catch()` — shows toast instead of false success

### Voting
- Confirm / Decline buttons in full card
- Requires location verification within 300m (`doVerify()`)
- **One vote per event per device** — tracked in `localStorage` (`ev_votes` key)
- After voting: buttons replaced by a read-only "Du hast bestätigt / abgelehnt" badge
- Vote persists across sessions (localStorage survives refresh)
- Updates `confirmed` / `declined` fields in Firestore
- Firestore errors caught — on failure, vote is rolled back (removed from localStorage) and error toast shown

---

## Key State Variables
```js
var curFilter = 'all';     // active filter pill key
var searchQuery = '';      // text search string
var cardMode = 'none';     // 'none' | 'peek' | 'full'
var listMode = false;      // list view open/closed
var selEv = null;          // currently selected event object
var vState = 'idle';       // verify state: idle | checking | nearby | too_far | denied | unavailable
var myPos = null;          // {lat, lng} user location
var mapOk = false;         // initMap guard — runs only once
var authShown = true;      // auth screen visibility
var votes = {};            // {eventId: 'confirm'|'decline'} — loaded from localStorage('ev_votes')
var dateFilter = null;     // null | 'YYYY-MM-DD' | ['YYYY-MM-DD','YYYY-MM-DD'] — date row filter
var fType = 'spontaneous'; // modal: 'spontaneous' | 'planned'
var fDate = '';            // modal: planned event date (YYYY-MM-DD)
var fTime = '';            // modal: planned event time (HH:MM)
```

---

## Known Bugs & Fixes
- **Markers disappearing:** Caused by replacing map container innerHTML. Fixed with zone-based architecture.
- **Map not loading locally:** Add `localhost` and `127.0.0.1` to Google Cloud Console API key restrictions and Firebase authorized domains.
- **Auth not working locally:** Same fix — Firebase Console → Authentication → Settings → Authorized domains.
- **Planned events without time:** Users could submit planned events without a time → people show up and nothing's happening. Fixed: time is now required (validated in `submitEv()`).
- **Firestore errors silently swallowed:** `add()` and `update()` calls had no `.catch()` → user saw success toast even when save failed. Fixed: all Firestore writes now have error handling with toast feedback. Vote rollback on failure.
- **Avatar broken image:** Google profile photo URL could fail to load → broken image icon. Fixed: `onerror` fallback shows 👤.
- **Date filter not filtering feed:** Date filter only dimmed markers but `getVis()` didn't filter by date → feed showed all events. Fixed: `getVis()` now includes date filter logic.
- **Splash screen staying in DOM:** Splash faded out with CSS but element remained. Fixed: `s.remove()` after animation.
- **Image upload CORS error:** Firebase Storage not activated or rules blocking. To fix:
  1. Firebase Console → Storage → activate (region: europe-west6)
  2. Storage → Rules → set:
     ```
     rules_version = '2';
     service firebase.storage {
       match /b/{bucket}/o {
         match /events/{fileName} {
           allow read: if true;
           allow write: if request.auth != null
                        && request.resource.size < 5 * 1024 * 1024
                        && request.resource.contentType.matches('image/.*');
         }
       }
     }
     ```
  3. Re-add `<script src="https://www.gstatic.com/firebasejs/10.12.0/firebase-storage-compat.js"></script>` after Firestore script tag
  4. Uncomment `var storage = firebase.storage();` in JS

---

## Data
- Events stored in **Firebase Firestore** (`events` collection, ordered by `createdAt desc`)
- Firestore listener (`onSnapshot`) keeps events live in real-time
- Event fields: `name`, `type` (spontaneous/planned), `category`, `lat`, `lng`, `time`, `description`, `confirmed`, `declined`, `postedBy`, `postedByUid`, `createdAt`, `eventDate` (YYYY-MM-DD — used by date filter; spontaneous = today, planned = user-selected date), `infoUrl` (optional link)
- Note: older events in Firestore may still have `imageUrl` field from before image upload code was removed — these are still displayed if present in the detail card

---

## Product Roadmap
### Phase 1 — Prototype (current)
- [x] Map with emoji category markers
- [x] Radar rings on spontaneous markers
- [x] Filter system (persistent pills)
- [x] Real-time text search
- [x] Floating Apple Maps-style search bar
- [x] Peek card + full card (2-state)
- [x] Event list view with distance sort
- [x] Vote system (confirm/decline)
- [x] Firebase auth (Google + anonymous)
- [x] PWA / installable
- [x] Test all v4 features end-to-end
- [x] Full card opens directly on marker tap (no peek intermediate)
- [x] Animated close (slide-down) + swipe-down-to-close gesture
- [x] One vote per device per event (localStorage)
- [x] Button press animations + filter pill transitions
- [x] Planned events (Spontan/Geplant toggle in modal, date + time pickers, stored with `eventDate`)
- [x] Date filter row (Heute / Morgen / Wochenende / 📅 custom) — dims non-matching markers to 25% opacity AND filters feed/list
- [x] Event creator can delete/end their own events ("Event beenden" button, only visible to owner via `postedByUid`)
- [ ] Image upload on events (Foto hinzufügen) ← **BLOCKED — needs Firebase Storage setup**
  - **All image upload code was removed** (dead code cleanup, 2025-02-24) — needs clean rebuild when ready
  - **Blocker:** Firebase Storage needs to be activated & CORS/rules configured (see Known Bugs section)
  - **End goal:** On mobile, tapping the image picker opens the camera directly, user takes a photo, it gets attached to the event
  - When ready: add Firebase Storage SDK, build image picker UI, compress + upload, display in card
- [x] Bug fix round (2025-02-24): time validation, Firestore error handling, avatar fallback, date filter in feed, dead code cleanup, splash DOM removal
- [ ] Share button on event cards (native share sheet) ← **NEXT**
- [ ] Switch hosting from Netlify to free alternative
- [ ] Event auto-expiry (remove spontaneous events older than 24h, planned events after their date)

### Phase 2 — Real Data
- [ ] AI scraper pulls events daily from Ron Orp, Eventfrog
- [ ] AI Events filter populated automatically

### Phase 3 — Engagement
- [ ] Push notifications / reminders for planned events
- [ ] User profiles and saved events
- [ ] Crowdsourced live event reporting

### Phase 4 — Mobile Apps
- [ ] Wrap with Capacitor for iOS and Android

### Phase 5 — Monetization
- [ ] Promoted events for local businesses

---

## Design Principles
- Map is the hero — full screen, everything else overlays it
- Apple Maps feel — minimal floating chrome, clean search bar
- Dark purple theme — `#0a0818` background, `#7c6aff` accent, `#34d399` green
- Mobile-first — respect safe-area insets (`var(--top)`, `var(--bot)`)
- One-tap actions wherever possible

---

## How to Continue Development
1. Run `claude` from inside the project folder
2. Say: *"Read CLAUDE.md and my project files, then let's continue building EventSpot Zürich"*
3. **Follow the Build → Test → Repeat workflow** — test each feature before moving on

**At the end of each session, say:**
*"Update CLAUDE.md with everything we built or changed today"*

---

## Background & Owner
- Owner: Domenic, based in Zürich
- Non-coder building this with AI assistance
- Goal: validate the concept with real users before investing in paid development

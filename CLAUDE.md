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
```

---

## Firestore Data
- Collection: `events`, ordered by `createdAt desc`
- Fields: `name`, `type`, `category`, `lat`, `lng`, `time`, `description`, `confirmed`, `declined`, `postedBy`, `postedByUid`, `createdAt`, `eventDate`, `infoUrl`

---

## Known Issues & Notes
- **Markers disappearing** = innerHTML replacement near map div. Use zone rendering.
- **Local dev:** Add `localhost` + `127.0.0.1` to Google Cloud API key + Firebase authorized domains
- **Image upload:** BLOCKED — Firebase Storage not activated. Needs: activate in console (europe-west6), set rules (5MB limit, auth required), add SDK script tag, then build upload UI
- **Windows Python scripts:** Use `PYTHONIOENCODING=utf-8` prefix when running `.claude/skills/` Python scripts (Windows cp1252 encoding breaks emoji output)

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
- [ ] Image upload ← BLOCKED on Firebase Storage
- [ ] Event auto-expiry (spontaneous >24h, planned after date)

### Phase 2 — Real Data
- [ ] AI scraper (Ron Orp, Eventfrog)

### Phase 3 — Engagement
- [ ] Push notifications, user profiles, saved events

### Phase 4 — Mobile Apps
- [ ] Capacitor (iOS + Android)

### Phase 5 — Monetization
- [ ] Promoted events

---

## Owner
Domenic, Zürich. Non-coder building with AI. Goal: validate concept with real users.

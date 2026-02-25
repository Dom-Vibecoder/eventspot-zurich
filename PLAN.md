# Feature Planning Interview Guide

## Purpose
Before building any new feature, read this file and conduct a thorough interview with Domenic using the ask_user_input tool. Cover every section below. Do not skip sections or assume answers. The goal is to fully understand what needs to be built before writing a single line of code.

---

## How to Use This File
When Domenic says "Read PLAN.md and interview me about [feature]", you must:
1. Read this file fully
2. Read CLAUDE.md for project context
3. Interview Domenic section by section using structured questions
4. Summarize what you understood at the end and ask for confirmation
5. Only then start building

---

## Interview Sections

### 1. Feature Overview
Ask open-ended questions to understand the feature at a high level:
- What is the feature and what problem does it solve?
- Who is it for? (the event creator, the viewer, everyone?)
- Can you describe how it should work in plain language, step by step?
- Do you have a reference app or example you've seen that does something similar?

### 2. User Experience & Flow
Understand exactly how the user interacts with it:
- Where does the user start? (which screen, which button?)
- What happens step by step after they trigger it?
- What does success look like to the user?
- What should happen if something goes wrong?
- Should it work differently on mobile vs desktop?

### 3. Visual Design
Nail down the look and feel:
- Should it follow the existing dark theme with purple accents?
- Is it a modal, a bottom sheet, a new screen, a button, an overlay, or something else?
- Are there any animations or transitions needed?
- Should it appear immediately or after a delay/trigger?
- Any specific colors, sizes, or icons in mind?

### 4. Data & Logic
Understand what data is involved:
- Does this feature need to save anything? (to Firestore, localStorage, or nowhere?)
- Does it need to read existing data?
- Does it need the user's location?
- Does it require the user to be logged in, or can anonymous users use it?
- Are there any rules or conditions? (e.g. "only if within 300m", "only once per day")

### 5. Edge Cases & Concerns
Anticipate problems before they happen:
- What should happen if the user has no internet?
- What if location is not available?
- Can a user do this action more than once? Should there be a limit?
- What happens on a slow connection?
- Any privacy or security concerns?

### 6. Priority & Scope
Set realistic expectations:
- Is this a must-have or a nice-to-have?
- Should we build the full version or a simple version first to test?
- Are there parts of this feature that can be left for later?
- Does this depend on any other feature that isn't built yet?

### 7. Technical Considerations
Check for architectural fit:
- Does this touch the map? (remember: never modify the #map div after init)
- Does this need a new zone/section in the UI or does it fit in an existing one?
- Does it need any new Firebase collections or fields?
- Does it need any external API or service?

---

## After the Interview

Once all sections are covered:
1. Write a clear summary: "Here's what I understood — [feature description in detail]"
2. List the exact changes you plan to make to which files
3. Flag any risks or things you're uncertain about
4. Ask: "Does this match what you had in mind? Should I proceed?"
5. Wait for confirmation before touching any code

---

## Project Reminders (always keep in mind)
- All code lives in index.html — no separate JS/CSS files
- Never replace or touch the #map div after initMap() runs
- Use zone-based rendering — each UI section has its own draw function
- Dark theme, purple accents (#7c3aed range)
- Mobile-first — most users will be on phones
- Keep it simple — Domenic is validating a concept, not building enterprise software

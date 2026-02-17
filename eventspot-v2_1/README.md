# EventSpot Zürich 📍 – Setup Guide

This is the real, working version of EventSpot with:
- ✅ Google Maps (real streets, zoom, GPS)
- ✅ Firebase backend (real-time database, user accounts)
- ✅ GPS verification (must be within 300m to vote)
- ✅ Google sign-in + anonymous mode
- ✅ PWA (installable on phones)

---

## 📁 Files in this folder

```
eventspot-v2/
├── index.html         ← The main app (everything in one file)
├── manifest.json      ← PWA config
├── sw.js              ← Service worker (offline support)
├── icon-192.png       ← App icon (small)
├── icon-512.png       ← App icon (large)
├── seed-events.html   ← Run ONCE to add sample events to your database
├── firestore.rules    ← Security rules (paste into Firebase console)
└── README.md          ← This file
```

---

## 🚀 Setup (20 minutes, one-time)

### Step 1: Create Firebase Project

1. Go to https://console.firebase.google.com
2. Click **"Create a project"**
3. Name it `eventspot-zurich`
4. Disable Google Analytics → Create
5. Once ready, click the **web icon `</>`** on the project overview
6. Nickname: `eventspot-web` → Register app
7. **Copy the `firebaseConfig` object** — you'll need it in Step 3

### Step 2: Enable Firebase Services

**Firestore (database):**
1. Left menu → Build → **Firestore Database**
2. Click **Create database**
3. Start in **test mode**
4. Location: `europe-west6` (Zürich) → Enable

**Authentication:**
1. Left menu → Build → **Authentication** → Get started
2. Click **Google** → Enable → add your email as support email → Save

**Security Rules:**
1. Go to Firestore → **Rules** tab
2. Replace everything with the content of `firestore.rules`
3. Click **Publish**

### Step 3: Get Google Maps API Key

1. Go to https://console.cloud.google.com
2. The project `eventspot-zurich` should already exist (Firebase created it)
3. Select it in the top dropdown
4. In the search bar, search and **Enable** these 3 APIs:
   - **Maps JavaScript API**
   - **Places API**
   - **Geocoding API**
5. Go to **APIs & Services → Credentials**
6. Click **Create Credentials → API Key**
7. Copy the key

### Step 4: Add your keys to the app

Open `index.html` in a text editor (Notepad, TextEdit, VS Code — anything).

Find these lines near the top (around line 20):

```js
window.MAPS_KEY = "YOUR_GOOGLE_MAPS_API_KEY";
```

Replace with your Google Maps API key.

Find the Firebase config block:

```js
window.FIREBASE_CONFIG = {
  apiKey: "YOUR_FIREBASE_API_KEY",
  ...
};
```

Replace the entire object with the config you copied from Firebase.

**Also do the same in `seed-events.html`** — paste the Firebase config there too.

### Step 5: Deploy to Netlify

1. Go to https://www.netlify.com → Sign up (free)
2. Dashboard → **Add new site → Deploy manually**
3. Drag & drop the entire `eventspot-v2` folder
4. Done! You get a URL like `https://your-site.netlify.app`

### Step 6: Seed initial events

1. Open `https://your-site.netlify.app/seed-events.html` in your browser
2. Click **"Seed Events into Firestore"**
3. Wait until all 12 events show green checkmarks
4. Close the page — your app now has sample data!

### Step 7: Configure Google Auth redirect

1. Go to Firebase Console → Authentication → Settings → **Authorized domains**
2. Add your Netlify domain: `your-site.netlify.app`
3. Go to Google Cloud Console → APIs & Services → Credentials
4. Click your API key → Under **Website restrictions**, add your Netlify URL

### Step 8: Share with friends! 🎉

Send your friends the Netlify URL. They can:
- Open it in any browser
- Add to home screen (Safari: Share → Add to Home Screen / Chrome: Menu → Install)
- Sign in with Google to add their own events

---

## 📱 How your friends install it

**iPhone:**
Safari → Open the URL → Tap share icon ⬆️ → "Add to Home Screen"

**Android:**
Chrome → Open the URL → Tap menu ⋮ → "Install app" or "Add to Home Screen"

---

## 💡 Tips

- The app updates in **real-time** — when someone adds an event, everyone sees it instantly
- Users must be **within 300 meters** of an event to confirm/decline it
- Anonymous users can browse but their events show as "Anonym"
- Google-signed-in users get their name and photo shown

---

## 🔒 Security

- Firestore rules prevent users from reading/writing data they shouldn't
- GPS verification prevents remote vote manipulation
- Google Auth provides verified identities
- Update `firestore.rules` when you're ready to tighten permissions further

---

## 💰 Cost

Everything is free within these limits:
- **Firebase:** 50K reads/day, 20K writes/day, 1GB storage (more than enough)
- **Google Maps:** ~28,000 free map loads/month
- **Netlify:** 100GB bandwidth/month free

You'll only start paying if the app gets very popular — and by then you'll have revenue options.

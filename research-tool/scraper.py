#!/usr/bin/env python3
"""EventSpot Zürich — AI Event Research Tool

Scrapes events from Zürich-area websites and writes them to Firestore.

Usage:
    python scraper.py                    # Scrape all sources
    python scraper.py --source gemeinde  # Scrape only Gemeinde calendars
    python scraper.py --source ronorp    # Scrape only Ron Orp
    python scraper.py --dry-run          # Scrape but don't write to Firestore

Prerequisites:
    1. pip install scrapling firebase-admin requests
    2. scrapling install  (sets up browser)
    3. Place service-account-key.json in this directory
       (Firebase Console → Project Settings → Service Accounts → Generate New Private Key)
"""

import sys
import os
import argparse
import asyncio
from datetime import datetime

# Add research-tool dir to path so modules can import each other
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import firebase_admin
from firebase_admin import credentials, firestore
from category_map import map_category, should_skip
from geocoder import geocode


# --- Firebase setup ---

SERVICE_ACCOUNT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "service-account-key.json"
)


def init_firestore():
    """Initialize Firebase Admin SDK and return Firestore client."""
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print("ERROR: service-account-key.json not found!")
        print("Download it from Firebase Console → Project Settings → Service Accounts → Generate New Private Key")
        print(f"Save it to: {SERVICE_ACCOUNT_PATH}")
        sys.exit(1)

    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)
    return firestore.client()


# --- Deduplication ---

def get_existing_events(db):
    """Load existing event names + dates from Firestore for dedup."""
    existing = set()
    docs = db.collection('events').stream()
    for doc in docs:
        data = doc.to_dict()
        key = (data.get('name', '').lower().strip(), data.get('eventDate', ''))
        existing.add(key)
    print(f"  Loaded {len(existing)} existing events for deduplication")
    return existing


def is_duplicate(event, existing):
    """Check if an event already exists in Firestore."""
    key = (event['name'].lower().strip(), event.get('eventDate', ''))
    return key in existing


# --- Write to Firestore ---

def write_event(db, event):
    """Write a single event to Firestore with the correct schema."""
    lat, lng = geocode(event.get('location', ''), event.get('region_hint', 'Zürich, Schweiz'))
    category = map_category(event.get('category_hint', ''), event.get('name', ''))

    source_name = event.get('source_name', 'Unknown')
    posted_by = f"EventSpot Research · via {source_name}"

    doc = {
        'name': event['name'][:100],
        'type': 'planned',
        'category': category,
        'lat': lat,
        'lng': lng,
        'eventDate': event.get('eventDate') or datetime.now().strftime('%Y-%m-%d'),
        'time': event.get('time', ''),
        'description': (event.get('description', '') or event['name'])[:500],
        'infoUrl': event.get('infoUrl'),
        'confirmed': 0,
        'declined': 0,
        'postedBy': posted_by,
        'postedByUid': None,
        'createdAt': firestore.SERVER_TIMESTAMP,
    }

    db.collection('events').add(doc)
    print(f"    + {event['name'][:60]} ({category}, {event.get('eventDate', 'no date')})")


# --- Main orchestrator ---

async def run_scraping(sources):
    """Run scrapers for specified sources and collect events."""
    all_events = []

    if 'gemeinde' in sources:
        print("\n--- Gemeinde calendars ---")
        from sources.gemeinde import scrape_all as gemeinde_scrape
        events = await gemeinde_scrape()
        all_events.extend(events)

    if 'ronorp' in sources:
        print("\n--- Ron Orp ---")
        from sources.ronorp import scrape_all as ronorp_scrape
        events = await ronorp_scrape()
        all_events.extend(events)

    return all_events


def main():
    parser = argparse.ArgumentParser(description="EventSpot Zürich — Event Research Tool")
    parser.add_argument(
        '--source', choices=['gemeinde', 'ronorp', 'all'], default='all',
        help='Which source to scrape (default: all)'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Scrape but do not write to Firestore'
    )
    parser.add_argument(
        '--days', type=int, default=30,
        help='How many days ahead to scrape (default: 30)'
    )
    args = parser.parse_args()

    sources = ['gemeinde', 'ronorp'] if args.source == 'all' else [args.source]

    print(f"EventSpot Research Tool — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Sources: {', '.join(sources)}")
    print(f"Days ahead: {args.days}")
    print(f"Dry run: {args.dry_run}")

    # Step 1: Scrape
    print("\n=== SCRAPING ===")
    all_events = asyncio.run(run_scraping(sources))
    print(f"\nTotal scraped: {len(all_events)} events")

    if not all_events:
        print("No events found. Check if the source sites are accessible.")
        return

    # Filter out events without a name and skip non-events (recycling, garbage, etc.)
    all_events = [e for e in all_events if e.get('name') and not should_skip(e['name'])]
    print(f"After filtering: {len(all_events)} real events")

    if args.dry_run:
        print("\n=== DRY RUN — Events found: ===")
        for ev in all_events:
            cat = map_category(ev.get('category_hint', ''), ev.get('name', ''))
            print(f"  [{cat}] {ev['name'][:60]} | {ev.get('eventDate', '?')} | {ev.get('location', '?')} | {ev.get('source_name')}")
        print(f"\nTotal: {len(all_events)} events (not written to Firestore)")
        return

    # Step 2: Init Firestore + dedup
    print("\n=== FIRESTORE ===")
    db = init_firestore()
    existing = get_existing_events(db)

    # Step 3: Write new events
    new_count = 0
    skip_count = 0
    for event in all_events:
        if is_duplicate(event, existing):
            skip_count += 1
            continue
        try:
            write_event(db, event)
            new_count += 1
        except Exception as e:
            print(f"    ERROR writing '{event.get('name', '?')}': {e}")

    print(f"\n=== DONE ===")
    print(f"  New events added: {new_count}")
    print(f"  Duplicates skipped: {skip_count}")
    print(f"  Total in scrape: {len(all_events)}")


if __name__ == '__main__':
    main()

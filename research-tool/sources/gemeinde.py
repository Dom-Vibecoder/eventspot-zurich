"""Scraper for Gemeinde (municipality) event calendars.

Many Gemeinden around Zürich use the same calendar platform with a shared URL pattern:
  {gemeinde}.ch/anlaesseaktuelles?datumVon=DD.MM.YYYY&datumBis=DD.MM.YYYY

Events load dynamically after page render, so we use Scrapling's DynamicFetcher
to execute JavaScript and wait for content.
"""

import asyncio
from datetime import datetime, timedelta
from scrapling.fetchers import DynamicFetcher
from category_map import map_category

# Gemeinde sources: (name, base_url, region_hint for geocoding)
GEMEINDE_SOURCES = [
    ("Gemeinde Üetikon am See", "https://www.uetikonamsee.ch/anlaesseaktuelles", "Üetikon am See, Schweiz"),
    # Add more Gemeinden here as needed:
    # ("Gemeinde Meilen", "https://www.meilen.ch/anlaesseaktuelles", "Meilen, Schweiz"),
    # ("Gemeinde Männedorf", "https://www.maennedorf.ch/anlaesseaktuelles", "Männedorf, Schweiz"),
    # ("Gemeinde Küsnacht", "https://www.kuesnacht.ch/anlaesseaktuelles", "Küsnacht, Schweiz"),
]


def _build_url(base_url, days_ahead=30):
    """Build the calendar URL with date range parameters."""
    today = datetime.now()
    end = today + timedelta(days=days_ahead)
    return (
        f"{base_url}"
        f"?datumVon={today.strftime('%d.%m.%Y')}"
        f"&datumBis={end.strftime('%d.%m.%Y')}"
    )


def _parse_date(date_str):
    """Parse various German date formats to YYYY-MM-DD.

    Handles: 'DD.MM.YYYY', 'DD. Monat YYYY', 'Montag, DD.MM.YYYY', etc.
    """
    if not date_str:
        return None

    date_str = date_str.strip()

    # Remove weekday prefix like "Montag, " or "Di, "
    if ',' in date_str:
        date_str = date_str.split(',', 1)[1].strip()

    # Try DD.MM.YYYY
    for fmt in ('%d.%m.%Y', '%d.%m.%y'):
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue

    # Try German month names
    months_de = {
        'januar': 1, 'februar': 2, 'märz': 3, 'april': 4,
        'mai': 5, 'juni': 6, 'juli': 7, 'august': 8,
        'september': 9, 'oktober': 10, 'november': 11, 'dezember': 12,
    }
    parts = date_str.lower().replace('.', '').split()
    if len(parts) >= 3:
        try:
            day = int(parts[0])
            month = months_de.get(parts[1])
            year = int(parts[2])
            if month:
                return f"{year}-{month:02d}-{day:02d}"
        except (ValueError, IndexError):
            pass

    return None


def _parse_time(time_str):
    """Extract time from strings like '19:30', '19:30 Uhr', '19.30 Uhr'."""
    if not time_str:
        return None

    time_str = time_str.strip().replace('.', ':').replace(' Uhr', '').replace('Uhr', '')
    parts = time_str.split(':')
    if len(parts) == 2:
        try:
            h, m = int(parts[0]), int(parts[1])
            if 0 <= h <= 23 and 0 <= m <= 59:
                return f"{h:02d}:{m:02d} Uhr"
        except ValueError:
            pass
    return None


async def _scrape_one(name, base_url, region_hint, days_ahead=30):
    """Scrape events from a single Gemeinde calendar."""
    url = _build_url(base_url, days_ahead)
    print(f"  Scraping {name}: {url}")

    events = []
    try:
        page = await DynamicFetcher.async_fetch(
            url,
            headless=True,
            wait_selector="table, .veranstaltung, .event, .anlassRow, [class*='event'], [class*='anlass']",
            timeout=20000,
        )
    except Exception as e:
        print(f"  [gemeinde] Failed to load {name}: {e}")
        # Fallback: try without wait_selector
        try:
            page = await DynamicFetcher.async_fetch(url, headless=True, timeout=20000)
        except Exception as e2:
            print(f"  [gemeinde] Fallback also failed for {name}: {e2}")
            return events

    # Try multiple selector patterns — Gemeinde platforms vary
    rows = (
        page.css('tr[class*="anlass"], tr[class*="event"], tr[class*="veranstaltung"]')
        or page.css('.veranstaltung, .event-item, .anlassRow, .event-row')
        or page.css('table.list tbody tr, table tbody tr')
    )

    if not rows:
        # Debug: show what we got
        body = page.css('body')
        text = body[0].text if body else ''
        preview = text[:500] if text else '(empty)'
        print(f"  [gemeinde] No event rows found on {name}. Page preview: {preview}")
        return events

    print(f"  Found {len(rows)} potential event rows on {name}")

    for row in rows:
        cells = row.css('td')
        if not cells:
            continue

        # Event name is the link text inside the row
        link = row.css('a')
        if not link:
            continue
        name_text = link[0].text.strip() if hasattr(link[0], 'text') else ''
        if not name_text or len(name_text) < 2:
            continue

        # Detail URL from the link href
        detail_url = None
        href = link[0].attrib.get('href', '') if hasattr(link[0], 'attrib') else link[0].attributes.get('href', '')
        if href and not href.startswith('#') and not href.startswith('javascript'):
            if href.startswith('/'):
                from urllib.parse import urlparse
                parsed = urlparse(base_url)
                detail_url = f"{parsed.scheme}://{parsed.netloc}{href}"
            elif href.startswith('http'):
                detail_url = href

        # Date is in first cell's span.text-nowrap
        date_text = ''
        if cells:
            date_spans = cells[0].css('span.text-nowrap')
            if date_spans:
                date_text = date_spans[0].text.strip() if hasattr(date_spans[0], 'text') else ''

        # Location from second cell, organizer from third
        location_text = cells[1].text.strip() if len(cells) > 1 and hasattr(cells[1], 'text') else ''
        organizer_text = cells[2].text.strip() if len(cells) > 2 and hasattr(cells[2], 'text') else ''

        # Parse date — handle "DD.MM.YYYY" and "DD.MM.YYYY - DD.MM.YYYY" ranges
        raw_date = date_text.split(' - ')[0].strip() if ' - ' in date_text else date_text
        # Split off time if present (e.g. "09.04.2026\n18.30 Uhr - 20.30 Uhr")
        date_parts = raw_date.replace('\n', ' ').split()
        event_date = _parse_date(date_parts[0]) if date_parts else None

        # Parse time from date text (e.g. "18.30 Uhr")
        event_time = None
        for part in date_text.replace('\n', ' ').split():
            t = _parse_time(part)
            if t:
                event_time = t
                break

        category_hint = organizer_text or name_text

        event = {
            'name': name_text,
            'eventDate': event_date,
            'time': event_time or '',
            'location': location_text or region_hint.split(',')[0],
            'category_hint': category_hint,
            'description': f"{name_text} — {organizer_text}" if organizer_text else name_text,
            'infoUrl': detail_url,
            'source_name': name,
            'region_hint': region_hint,
        }
        events.append(event)

    print(f"  Parsed {len(events)} events from {name}")
    return events


async def scrape_all(days_ahead=30):
    """Scrape events from all configured Gemeinde calendars."""
    all_events = []
    for name, base_url, region_hint in GEMEINDE_SOURCES:
        try:
            events = await _scrape_one(name, base_url, region_hint, days_ahead)
            all_events.extend(events)
        except Exception as e:
            print(f"  [gemeinde] Error scraping {name}: {e}")
    return all_events


def scrape(days_ahead=30):
    """Synchronous entry point."""
    return asyncio.run(scrape_all(days_ahead))

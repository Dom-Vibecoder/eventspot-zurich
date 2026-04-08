"""Scraper for Ron Orp Zürich events.

Ron Orp (ronorp.net) is a Next.js SPA — event data loads via JavaScript.
The /zuerich/veranstaltung URL redirects to /zurich/rons-tips.
Uses Scrapling's StealthyFetcher for anti-bot bypass + JS rendering.
"""

import asyncio
from datetime import datetime
from scrapling.fetchers import StealthyFetcher
from category_map import map_category

# Ron Orp redirects /zuerich/veranstaltung → /zurich/rons-tips
RONORP_URLS = [
    "https://www.ronorp.net/zurich/rons-tips",
    "https://www.ronorp.net/zurich/market/events/rons-event-tipps",
]


def _get_attr(el, attr, default=''):
    """Safely get an attribute from a Scrapling element."""
    try:
        if hasattr(el, 'attrib'):
            return el.attrib.get(attr, default)
        if hasattr(el, 'attributes'):
            return el.attributes.get(attr, default)
    except Exception:
        pass
    return default


def _get_text(el, default=''):
    """Safely get text from a Scrapling element."""
    try:
        if hasattr(el, 'text'):
            return el.text or default
        if hasattr(el, 'get_text'):
            return el.get_text() or default
    except Exception:
        pass
    return default


def _parse_ronorp_date(date_str):
    """Parse Ron Orp date formats to YYYY-MM-DD."""
    if not date_str:
        return None

    date_str = date_str.strip()

    if date_str.lower() in ('heute', 'today'):
        return datetime.now().strftime('%Y-%m-%d')
    if date_str.lower() in ('morgen', 'tomorrow'):
        from datetime import timedelta
        return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    # Remove weekday prefix
    if ' ' in date_str:
        parts = date_str.split()
        for part in parts:
            if '.' in part and len(part) >= 8:
                date_str = part
                break

    for fmt in ('%d.%m.%Y', '%d.%m.%y'):
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue

    return None


async def _scrape():
    """Scrape events from Ron Orp Zürich."""
    events = []

    for url in RONORP_URLS:
        print(f"  Scraping Ron Orp: {url}")
        try:
            page = await StealthyFetcher.async_fetch(
                url,
                headless=True,
                timeout=30000,
            )
        except Exception as e:
            print(f"  [ronorp] Failed to load {url}: {e}")
            continue

        # Ron Orp uses various card/list layouts — try multiple patterns
        items = (
            page.css('[class*="event"], [class*="Event"]')
            or page.css('article, .card, .list-item, .tip-item')
            or page.css('a[href*="/event"], a[href*="/veranstaltung"]')
        )

        if not items:
            body = page.css('body')
            text = _get_text(body[0]) if body else ''
            preview = text[:500] if text else '(empty)'
            print(f"  [ronorp] No event items found at {url}. Page preview: {preview}")
            continue

        print(f"  Found {len(items)} potential event items on Ron Orp")

        for item in items:
            # Extract title
            title_el = item.css('h2, h3, h4, .title, [class*="title"]')
            title = _get_text(title_el[0]).strip() if title_el else _get_text(item).strip()[:100]

            if not title or len(title) < 3:
                continue

            # Extract date
            date_el = item.css('[class*="date"], [class*="Date"], time, .meta')
            date_text = _get_text(date_el[0]).strip() if date_el else ''
            event_date = _parse_ronorp_date(date_text)

            # Extract time
            time_el = item.css('[class*="time"], [class*="Time"]')
            time_text = ''
            if time_el:
                time_text = _get_text(time_el[0]).strip()
                if ':' in time_text and len(time_text) <= 10:
                    time_text = time_text.replace(' Uhr', '') + ' Uhr'
                else:
                    time_text = ''

            # Extract location
            loc_el = item.css('[class*="location"], [class*="Location"], [class*="venue"], [class*="ort"]')
            location = _get_text(loc_el[0]).strip() if loc_el else ''

            # Extract category
            cat_el = item.css('[class*="category"], [class*="tag"], [class*="label"], .badge')
            category_hint = _get_text(cat_el[0]).strip() if cat_el else ''

            # Extract description
            desc_el = item.css('p, .description, [class*="desc"], [class*="teaser"]')
            description = _get_text(desc_el[0]).strip() if desc_el else title

            # Extract link
            link = item.css('a[href]')
            detail_url = None
            if link:
                href = _get_attr(link[0], 'href')
                if href.startswith('/'):
                    detail_url = f"https://www.ronorp.net{href}"
                elif href.startswith('http'):
                    detail_url = href

            event = {
                'name': title,
                'eventDate': event_date,
                'time': time_text,
                'location': location or 'Zürich',
                'category_hint': category_hint or title,
                'description': description[:300],
                'infoUrl': detail_url,
                'source_name': 'Ron Orp',
                'region_hint': 'Zürich, Schweiz',
            }
            events.append(event)

    print(f"  Parsed {len(events)} events from Ron Orp")
    return events


async def scrape_all():
    """Async entry point."""
    return await _scrape()


def scrape():
    """Synchronous entry point."""
    return asyncio.run(scrape_all())

# Maps scraped event categories from various sources to EventSpot's 9 categories.
# EventSpot categories: music, food, bonfire, party, community, protest, market, sport, art

# Keywords (lowercase) mapped to EventSpot category
KEYWORD_MAP = {
    # music
    'musik': 'music', 'konzert': 'music', 'konzerte': 'music', 'jazz': 'music',
    'rock': 'music', 'pop': 'music', 'klassik': 'music', 'oper': 'music',
    'chor': 'music', 'dj': 'music', 'live music': 'music', 'livemusik': 'music',
    'open air': 'music', 'festival': 'music', 'karaoke': 'music',
    'djembe': 'music', 'djembé': 'music', 'trommeln': 'music', 'singen': 'music',
    # food
    'essen': 'food', 'food': 'food', 'kulinarisch': 'food', 'kochen': 'food',
    'brunch': 'food', 'dinner': 'food', 'degustation': 'food', 'wein': 'food',
    'bier': 'food', 'streetfood': 'food', 'gastronomie': 'food',
    'food & shopping': 'food',
    # bonfire
    'lagerfeuer': 'bonfire', 'feuer': 'bonfire', 'grillieren': 'bonfire',
    'grillen': 'bonfire', 'bbq': 'bonfire',
    # party
    'party': 'party', 'clubbing': 'party', 'nightlife': 'party',
    'nachtleben': 'party', 'feste': 'party', 'fest': 'party',
    'ausgang': 'party', 'tanzen': 'party', 'salsa': 'party',
    # community
    'community': 'community', 'gemeinschaft': 'community', 'verein': 'community',
    'treffpunkt': 'community', 'networking': 'community', 'meetup': 'community',
    'workshop': 'community', 'kurs': 'community', 'bildung': 'community',
    'vortrag': 'community', 'lesung': 'community', 'führung': 'community',
    'fuehrung': 'community', 'religion': 'community', 'senioren': 'community',
    'familie': 'community', 'kinder': 'community', 'jugend': 'community',
    'für kinder': 'community',
    # protest
    'demo': 'protest', 'protest': 'protest', 'demonstration': 'protest',
    'kundgebung': 'protest', 'politik': 'protest', 'streik': 'protest',
    # market
    'markt': 'market', 'flohmarkt': 'market', 'messe': 'market',
    'basar': 'market', 'ausstellung': 'market', 'ausstellungen': 'market',
    'shopping': 'market', 'börse': 'market',
    # sport
    'sport': 'sport', 'yoga': 'sport', 'laufen': 'sport', 'wandern': 'sport',
    'fitness': 'sport', 'fussball': 'sport', 'basketball': 'sport',
    'schwimmen': 'sport', 'tennis': 'sport', 'velo': 'sport',
    'volleyball': 'sport', 'turnen': 'sport',
    # art
    'kunst': 'art', 'theater': 'art', 'kino': 'art', 'film': 'art',
    'galerie': 'art', 'museum': 'art', 'fotografie': 'art', 'malerei': 'art',
    'tanz': 'art', 'kabarett': 'art', 'comedy': 'art', 'literatur': 'art',
    'kultur': 'art',
}



# Event names that are NOT real events (municipal services, recycling, etc.)
SKIP_KEYWORDS = [
    'altpapier', 'karton', 'grüngut', 'kehricht', 'sonderabfälle',
    'sonderabfalle', 'sonderabfall', 'papiersammlung', 'sammelstelle',
    'abfallkalender', 'entsorgung',
]

# Exact names that are recycling/waste collection, not events
SKIP_EXACT = ['metall', 'papier', 'karton', 'grüngut', 'kehricht']


def should_skip(event_name):
    """Return True if the event name looks like a municipal service, not an event."""
    if not event_name:
        return False
    text = event_name.lower().strip()
    if text in SKIP_EXACT:
        return True
    return any(kw in text for kw in SKIP_KEYWORDS)


def map_category(scraped_category, event_name=''):
    """Map a scraped category string to one of EventSpot's 9 categories.

    Checks for keyword matches in category text AND event name.
    Falls back to 'community' if no match is found.
    """
    # Check both category hint and event name
    texts = [
        (scraped_category or '').lower().strip(),
        (event_name or '').lower().strip(),
    ]

    for text in texts:
        if not text:
            continue

        # Direct match
        if text in KEYWORD_MAP:
            return KEYWORD_MAP[text]

        # Substring match
        for keyword, category in KEYWORD_MAP.items():
            if keyword in text:
                return category

    return 'community'

"""RSS source configurations."""

SOURCES = {
    # English - High Priority
    "motorsport": {
        "name": "Motorsport.com",
        "feed_url": "https://www.motorsport.com/rss/f1/news/",
        "lang": "en",
        "priority": 100,
        "fetch_interval": 300,
    },
    "autosport": {
        "name": "Autosport",
        "feed_url": "https://www.autosport.com/rss/f1/news/",
        "lang": "en",
        "priority": 95,
        "fetch_interval": 300,
    },
    "the-race": {
        "name": "The Race",
        "feed_url": "https://www.the-race.com/formula-1/feed/",
        "lang": "en",
        "priority": 95,
        "fetch_interval": 300,
    },

    # English - Medium Priority
    "racefans": {
        "name": "RaceFans",
        "feed_url": "https://www.racefans.net/feed/",
        "lang": "en",
        "priority": 85,
        "fetch_interval": 900,
    },
    "f1i": {
        "name": "F1i",
        "feed_url": "https://f1i.com/feed",
        "lang": "en",
        "priority": 75,
        "fetch_interval": 900,
    },
    "planetf1": {
        "name": "PlanetF1",
        "feed_url": "https://www.planetf1.com/feed/",
        "lang": "en",
        "priority": 70,
        "fetch_interval": 900,
    },

    # German
    "formel1-de": {
        "name": "Formel1.de",
        "feed_url": "https://www.formel1.de/rss",
        "lang": "de",
        "priority": 80,
        "fetch_interval": 1800,
    },

    # Italian
    "motorsport-it": {
        "name": "Motorsport.com Italia",
        "feed_url": "https://it.motorsport.com/rss/f1/news/",
        "lang": "it",
        "priority": 80,
        "fetch_interval": 1800,
    },

    # Spanish
    "motorsport-es": {
        "name": "Motorsport.com España",
        "feed_url": "https://es.motorsport.com/rss/f1/news/",
        "lang": "es",
        "priority": 80,
        "fetch_interval": 1800,
    },

    # Portuguese
    "motorsport-br": {
        "name": "Motorsport.com Brasil",
        "feed_url": "https://motorsport.uol.com.br/rss/f1/news/",
        "lang": "pt-BR",
        "priority": 80,
        "fetch_interval": 1800,
    },
}

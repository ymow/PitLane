"""RSS source configurations."""

SOURCES = {
    # --- GLOBAL / ENGLISH (Tier 1) ---
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

    # --- CHINESE MARKETS (Tier 1) ---
    # Traditional Chinese (Taiwan)
    "sportsv-f1": {
        "name": "Sports Vision F1",
        "feed_url": "https://www.sportsv.net/feed/category/auto/f1",
        "lang": "zh-TW",
        "priority": 90,
        "fetch_interval": 1800,
    },
    # Simplified Chinese (China)
    "motorsport-cn": {
        "name": "Motorsport.com China",
        "feed_url": "https://cn.motorsport.com/rss/f1/news/",
        "lang": "zh-CN",
        "priority": 90,
        "fetch_interval": 1800,
    },

    # --- EUROPEAN MARKETS (Tier 2) ---
    # German
    "formel1-de": {
        "name": "Formel1.de",
        "feed_url": "https://www.formel1.de/rss/news/feed.xml",
        "lang": "de",
        "priority": 85,
        "fetch_interval": 1800,
    },
    "motorsport-total": {
        "name": "Motorsport-Total",
        "feed_url": "https://www.motorsport-total.com/rss/formel-1",
        "lang": "de",
        "priority": 80,
        "fetch_interval": 1800,
    },

    # Italian
    "motorsport-it": {
        "name": "Motorsport.com Italia",
        "feed_url": "https://it.motorsport.com/rss/f1/news/",
        "lang": "it",
        "priority": 85,
        "fetch_interval": 1800,
    },
    "f1grandprix-it": {
        "name": "F1GrandPrix.it",
        "feed_url": "https://www.f1grandprix.it/feed/",
        "lang": "it",
        "priority": 80,
        "fetch_interval": 1800,
    },

    # Spanish
    "motorsport-es": {
        "name": "Motorsport.com España",
        "feed_url": "https://es.motorsport.com/rss/f1/news/",
        "lang": "es",
        "priority": 85,
        "fetch_interval": 1800,
    },
    "f1latam": {
        "name": "F1Latam",
        "feed_url": "https://www.f1latam.com/rss/rss.php",
        "lang": "es",
        "priority": 80,
        "fetch_interval": 1800,
    },

    # Portuguese (Brazil)
    "motorsport-br": {
        "name": "Motorsport.com Brasil",
        "feed_url": "https://motorsport.uol.com.br/rss/f1/news/",
        "lang": "pt-BR",
        "priority": 85,
        "fetch_interval": 1800,
    },
    "autoracing": {
        "name": "Autoracing",
        "feed_url": "https://www.autoracing.com.br/feed/",
        "lang": "pt-BR",
        "priority": 80,
        "fetch_interval": 1800,
    },

    # Dutch
    "headliner-nl": {
        "name": "Headliner.nl",
        "feed_url": "https://www.headliner.nl/rss/formule-1",
        "lang": "nl",
        "priority": 85,
        "fetch_interval": 1800,
    },
    "motorsport-nl": {
        "name": "Motorsport.com Nederland",
        "feed_url": "https://nl.motorsport.com/rss/f1/news/",
        "lang": "nl",
        "priority": 80,
        "fetch_interval": 1800,
    },

    # French
    "motorsport-fr": {
        "name": "Motorsport.com France",
        "feed_url": "https://fr.motorsport.com/rss/f1/news/",
        "lang": "fr",
        "priority": 85,
        "fetch_interval": 1800,
    },
    "f1only": {
        "name": "F1Only.fr",
        "feed_url": "https://f1only.fr/feed/",
        "lang": "fr",
        "priority": 80,
        "fetch_interval": 1800,
    },

    # Japanese
    "motorsport-jp": {
        "name": "Motorsport.com Japan",
        "feed_url": "https://jp.motorsport.com/rss/f1/news/",
        "lang": "ja",
        "priority": 85,
        "fetch_interval": 1800,
    },
}
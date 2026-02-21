"""RSS feed fetching and parsing."""
import re
import feedparser
import hashlib
import requests
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from django.utils.text import slugify
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Common HTML entities not defined in XML but often found in RSS feeds
_HTML_ENTITIES = {
    '&nbsp;': ' ', '&copy;': '©', '&reg;': '®', '&trade;': '™',
    '&mdash;': '—', '&ndash;': '–', '&hellip;': '…', '&middot;': '·',
    '&laquo;': '«', '&raquo;': '»', '&ldquo;': '\u201c', '&rdquo;': '\u201d',
    '&lsquo;': '\u2018', '&rsquo;': '\u2019', '&amp;amp;': '&amp;',
    '&eacute;': 'é', '&egrave;': 'è', '&agrave;': 'à', '&ugrave;': 'ù',
    '&oacute;': 'ó', '&uacute;': 'ú', '&ntilde;': 'ñ', '&ccedil;': 'ç',
}

# Regex for characters invalid in XML 1.0
_INVALID_XML_CHARS = re.compile(
    r'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]'
)

_USER_AGENT = 'PitLaneBot/1.0 (+http://pitlane.com)'


@dataclass
class RSSItem:
    """Parsed RSS feed item."""
    external_id: str
    title: str
    slug: str
    body: str
    url: str
    published_at: datetime
    image_url: Optional[str] = None


class RSSFetcher:
    """Fetch and parse RSS feeds with robust XML handling."""

    def __init__(self, feed_url: str):
        self.feed_url = feed_url

    def fetch(self) -> List[RSSItem]:
        """
        Fetch and parse RSS feed.
        Tries robust path (requests + XML cleaning) first,
        falls back to direct feedparser URL fetch.
        """
        feed = self._fetch_robust()

        if not feed or not getattr(feed, 'entries', None):
            logger.warning(f"No entries found in feed {self.feed_url}")
            return []

        items = []
        for entry in feed.entries:
            try:
                item = self._parse_entry(entry)
                if item:
                    items.append(item)
            except Exception as e:
                logger.error(f"Error parsing entry from {self.feed_url}: {e}")
                continue

        logger.info(f"Fetched {len(items)} items from {self.feed_url}")
        return items

    def _fetch_robust(self):
        """
        Fetch feed via requests, clean XML, then parse with feedparser.
        Falls back to direct feedparser URL fetch on any error.
        """
        try:
            response = requests.get(
                self.feed_url,
                headers={'User-Agent': _USER_AGENT},
                timeout=30,
            )
            response.raise_for_status()
            cleaned = self._clean_xml(response.content)
            feed = feedparser.parse(cleaned)

            if feed.bozo and not getattr(feed, 'entries', None):
                # Cleaned content still broken — fall back to direct URL
                raise ValueError(f"Cleaned feed still invalid: {feed.bozo_exception}")

            if feed.bozo:
                logger.debug(
                    f"Feed has minor issues but entries found for {self.feed_url}: "
                    f"{feed.bozo_exception}"
                )
            return feed

        except Exception as e:
            logger.warning(
                f"Robust fetch failed for {self.feed_url}: {e}. "
                f"Falling back to direct feedparser."
            )
            return feedparser.parse(self.feed_url, agent=_USER_AGENT)

    def _clean_xml(self, content: bytes) -> bytes:
        """
        Clean raw feed bytes before parsing:
        1. Detect encoding from XML declaration or HTTP headers
        2. Remove XML 1.0 invalid characters
        3. Replace undefined HTML entities
        """
        # Detect encoding
        encoding = 'utf-8'
        sniff = content[:200]
        match = re.search(rb'encoding=["\']([^"\']+)["\']', sniff)
        if match:
            encoding = match.group(1).decode('ascii', errors='ignore')

        text = content.decode(encoding, errors='replace')

        # Strip XML-invalid characters
        text = _INVALID_XML_CHARS.sub('', text)

        # Replace undefined HTML entities
        for entity, replacement in _HTML_ENTITIES.items():
            text = text.replace(entity, replacement)

        return text.encode('utf-8')

    def _clean_body(self, body: str) -> str:
        """Remove common RSS clutter."""
        if not body:
            return ""
        cleaned = body.strip()
        cleaned = cleaned.replace("Read more...", "")
        cleaned = cleaned.replace("Continue reading...", "")
        return cleaned

    def _parse_entry(self, entry) -> RSSItem:
        """Parse a single feed entry."""
        url = entry.get('link', '')
        guid = entry.get('id', entry.get('guid', url))
        external_id = hashlib.md5(guid.encode()).hexdigest()

        title = entry.get('title', 'Untitled')

        body = entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
        if not body:
            body = entry.get('summary', entry.get('description', ''))
        body = self._clean_body(body)

        published_at = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published_at = timezone.make_aware(datetime(*entry.published_parsed[:6]))
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            published_at = timezone.make_aware(datetime(*entry.updated_parsed[:6]))
        else:
            published_at = timezone.now()

        image_url = None
        if hasattr(entry, 'media_content') and entry.media_content:
            image_url = entry.media_content[0].get('url')
        elif hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if enclosure.get('type', '').startswith('image/'):
                    image_url = enclosure.get('href')
                    break

        return RSSItem(
            external_id=external_id,
            title=title,
            slug=slugify(title),
            body=body,
            url=url,
            published_at=published_at,
            image_url=image_url,
        )

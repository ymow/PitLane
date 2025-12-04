"""RSS feed fetching and parsing."""
import feedparser
import hashlib
from datetime import datetime
from dataclasses import dataclass
from typing import List
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)


@dataclass
class RSSItem:
    """Parsed RSS feed item."""
    external_id: str
    title: str
    slug: str
    body: str
    url: str
    published_at: datetime
    image_url: str = None


class RSSFetcher:
    """Fetch and parse RSS feeds."""

    def __init__(self, feed_url: str):
        """Initialize with feed URL."""
        self.feed_url = feed_url

    def fetch(self) -> List[RSSItem]:
        """
        Fetch and parse RSS feed.

        Returns:
            List of RSSItem objects
        """
        try:
            # Polite fetching with custom User-Agent
            feed = feedparser.parse(
                self.feed_url,
                agent='PitLaneBot/1.0 (+http://pitlane.com)'
            )

            if feed.bozo:
                logger.warning(f"Feed parsing warning for {self.feed_url}: {feed.bozo_exception}")

            items = []
            for entry in feed.entries:
                try:
                    item = self._parse_entry(entry)
                    if item:
                        items.append(item)
                except Exception as e:
                    logger.error(f"Error parsing entry: {e}")
                    continue

            logger.info(f"Fetched {len(items)} items from {self.feed_url}")
            return items

        except Exception as e:
            logger.error(f"Error fetching feed {self.feed_url}: {e}")
            return []

    def _clean_body(self, body: str) -> str:
        """Remove common RSS clutter."""
        if not body:
            return ""
            
        # Basic cleanup (can be expanded)
        cleaned = body.strip()
        
        # Remove common "Read more" patterns
        cleaned = cleaned.replace("Read more...", "")
        cleaned = cleaned.replace("Continue reading...", "")
        
        return cleaned

    def _parse_entry(self, entry) -> RSSItem:
        """Parse a single feed entry."""
        # Generate external ID from URL or guid
        url = entry.get('link', '')
        guid = entry.get('id', entry.get('guid', url))
        external_id = hashlib.md5(guid.encode()).hexdigest()

        # Get title
        title = entry.get('title', 'Untitled')

        # Get body content
        body = entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
        if not body:
            body = entry.get('summary', entry.get('description', ''))
            
        body = self._clean_body(body)

        # Get published date
        published_at = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published_at = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            published_at = datetime(*entry.updated_parsed[:6])
        else:
            published_at = datetime.now()

        # Get image URL
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
            image_url=image_url
        )

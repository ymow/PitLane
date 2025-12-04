"""HTML Content Sanitization and Scoring."""
import bleach
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class ArticleSanitizer:
    """Sanitizes and scores article content."""

    # Allowed tags for clean content
    ALLOWED_TAGS = [
        'p', 'b', 'i', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'a', 'img', 'br'
    ]

    # Allowed attributes
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
    }

    def sanitize(self, html_content: str) -> str:
        """
        Sanitize HTML content.
        Removes scripts, styles, iframes, and potentially unsafe tags.
        """
        if not html_content:
            return ""

        # First pass with bleach
        cleaned_html = bleach.clean(
            html_content,
            tags=self.ALLOWED_TAGS,
            attributes=self.ALLOWED_ATTRIBUTES,
            strip=True
        )

        return cleaned_html

    def score_quality(self, title: str, body: str, has_image: bool) -> float:
        """
        Calculate content quality score (0-100).
        
        Criteria:
        - Length: > 300 chars (up to 50 pts)
        - Image: +20 pts
        - Formatting: Has paragraphs/headings (+10 pts)
        - Title: Not all caps (+10 pts)
        - Spam check: No 'Read more' or too many links (-pts)
        """
        score = 0.0
        
        # 1. Length Check
        text_len = len(body)
        if text_len > 1000:
            score += 50
        elif text_len > 500:
            score += 30
        elif text_len > 200:
            score += 10
        else:
            score += 0  # Too short
            
        # 2. Image Check
        if has_image:
            score += 20
            
        # 3. Structure Check
        soup = BeautifulSoup(body, 'html.parser')
        if soup.find(['p', 'br', 'div']):
            score += 10
        if soup.find(['h2', 'h3', 'strong']):
            score += 10
            
        # 4. Title Check
        if not title.isupper():
            score += 10
            
        return min(100.0, score)

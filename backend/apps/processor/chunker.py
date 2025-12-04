"""HTML content chunking service."""
from bs4 import BeautifulSoup, Tag, NavigableString
from apps.news.models import ChunkType
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class HTMLChunker:
    """
    Splits HTML content into semantic chunks.
    Preserves structure for AI processing while maintaining readability.
    """

    BLOCK_TAGS = {
        'p': ChunkType.PARAGRAPH,
        'h1': ChunkType.HEADING,
        'h2': ChunkType.HEADING,
        'h3': ChunkType.HEADING,
        'h4': ChunkType.HEADING,
        'h5': ChunkType.HEADING,
        'h6': ChunkType.HEADING,
        'ul': ChunkType.LIST,
        'ol': ChunkType.LIST,
        'blockquote': ChunkType.QUOTE,
        'img': ChunkType.IMAGE,
    }

    def chunk_article(self, html_content: str) -> List[Dict]:
        """
        Parse HTML and return list of chunks.
        
        Args:
            html_content: Raw HTML string
            
        Returns:
            List of dicts: [{'type': ChunkType, 'content': str, 'sequence': int}]
        """
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        chunks = []
        sequence = 1

        # If the content is just text without block tags, wrap it in a paragraph
        if not soup.find(list(self.BLOCK_TAGS.keys())):
            return [{
                'type': ChunkType.PARAGRAPH,
                'content': html_content.strip(),
                'sequence': 1
            }]

        for element in soup.children:
            if isinstance(element, NavigableString):
                text = str(element).strip()
                if text:
                    chunks.append({
                        'type': ChunkType.PARAGRAPH,
                        'content': text,
                        'sequence': sequence
                    })
                    sequence += 1
                continue

            if isinstance(element, Tag):
                # Determine chunk type
                chunk_type = self.BLOCK_TAGS.get(element.name, ChunkType.OTHER)
                
                # Clean content (keep inner HTML for lists/quotes, text for others?)
                # For now, we keep the outer HTML to preserve formatting (like <b>, <a>) within the block
                content = str(element).strip()
                
                # Skip empty elements
                if not element.get_text(strip=True) and element.name != 'img':
                    continue

                chunks.append({
                    'type': chunk_type,
                    'content': content,
                    'sequence': sequence
                })
                sequence += 1

        logger.debug(f"Split article into {len(chunks)} chunks")
        return chunks

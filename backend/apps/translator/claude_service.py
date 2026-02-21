"""Claude AI translation service for F1 content."""
import anthropic
import json
import os
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class TranslationResult:
    """Translation result from Claude."""
    title: str
    body: str
    summary: str
    confidence: float


class ClaudeTranslator:
    """
    F1-specialized translator using Claude API.
    Preserves technical terms and driver/team names.
    """

    MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")

    # Terms to preserve unchanged across all languages
    PRESERVE_TERMS = {
        # Drivers (2025 grid)
        "Verstappen", "Norris", "Leclerc", "Hamilton", "Sainz",
        "Russell", "Piastri", "Alonso", "Pérez", "Stroll",
        "Gasly", "Albon", "Tsunoda", "Hülkenberg", "Ocon",
        "Bearman", "Bortoleto", "Colapinto", "Lawson", "Hadjar",
        "Antonelli", "Doohan",

        # Teams
        "Red Bull Racing", "McLaren", "Ferrari", "Mercedes",
        "Aston Martin", "Alpine", "Williams", "Racing Bulls",
        "Haas", "Kick Sauber", "Audi",

        # Technical terms
        "DRS", "ERS", "MGU-K", "MGU-H", "PU", "ICE",
        "DNF", "DNS", "DSQ", "SC", "VSC", "FCY",
        "pole position", "pit stop", "pit lane",
        "undercut", "overcut", "box box",
        "soft", "medium", "hard", "intermediate", "wet",
        "FIA", "FOM", "parc fermé",
        "downforce", "drag", "sidepod",
        "floor", "diffuser", "front wing", "rear wing"
    }

    LANG_NAMES = {
        "en": "English",
        "zh-TW": "Traditional Chinese (Taiwan)",
        "zh-CN": "Simplified Chinese (Mainland China)",
        "es": "Spanish",
        "pt-BR": "Brazilian Portuguese",
        "it": "Italian",
        "nl": "Dutch",
        "de": "German",
        "ja": "Japanese",
        "fr": "French"
    }

    def __init__(self, api_key: str):
        """Initialize Claude client."""
        self.client = anthropic.Anthropic(api_key=api_key)

    def translate(
        self,
        title: str,
        body: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """
        Translate F1 article with domain-specific awareness.

        Args:
            title: Original article title
            body: Original article body (HTML)
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            TranslationResult with title, body, summary, confidence
        """
        prompt = self._build_prompt(title, body, source_lang, target_lang)

        try:
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}]
            )

            return self._parse_response(response.content[0].text)
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise

    def _build_prompt(
        self,
        title: str,
        body: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """Build translation prompt."""
        source_name = self.LANG_NAMES.get(source_lang, source_lang)
        target_name = self.LANG_NAMES.get(target_lang, target_lang)

        preserve_list = ", ".join(sorted(self.PRESERVE_TERMS)[:30])  # Top 30

        return f"""You are an expert Formula 1 journalist and professional translator.
Translate this F1 news article from {source_name} to {target_name}.

## CRITICAL RULES

1. **PRESERVE THESE TERMS UNCHANGED:**
   {preserve_list}
   (and similar F1 technical terms, driver names, team names)

2. **TRANSLATION GUIDELINES:**
   - Maintain journalistic tone appropriate for {target_name} readers
   - Localize idioms and cultural references naturally
   - Keep HTML tags intact (<p>, <strong>, <em>, etc.)
   - Preserve paragraph structure
   - Numbers, dates, times should follow {target_name} conventions

3. **SUMMARY:**
   - Write a 2-3 sentence summary of the key news
   - Focus on the most newsworthy element
   - Written in {target_name}

4. **CONFIDENCE SCORING:**
   - 0.95-1.0: Perfect translation, no ambiguity
   - 0.85-0.94: Good translation, minor uncertainties
   - 0.70-0.84: Acceptable, some terms unclear
   - <0.70: Significant issues, needs human review

## SOURCE ARTICLE

**Title:** {title}

**Body:**
{body}

## OUTPUT FORMAT (JSON ONLY)

```json
{{
  "title": "translated title",
  "body": "translated body with HTML preserved",
  "summary": "2-3 sentence summary",
  "confidence": 0.95
}}
```

IMPORTANT: Output ONLY valid JSON. No additional text."""

    def _parse_response(self, response: str) -> TranslationResult:
        """Parse Claude's JSON response."""
        # Clean up response
        text = response.strip()

        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
            if text.startswith("json"):
                text = text[4:]

        data = json.loads(text.strip())

        return TranslationResult(
            title=data.get("title") or "",
            body=data.get("body") or "",
            summary=data.get("summary") or "",
            confidence=float(data.get("confidence", 0.7))
        )

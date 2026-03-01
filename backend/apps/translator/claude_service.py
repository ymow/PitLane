"""Claude AI translation service for F1 content."""
import anthropic
import json
import os
import re
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
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""


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

    # Max retries for malformed JSON responses before giving up
    _JSON_PARSE_MAX_RETRIES = 2

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
        last_parse_error: Optional[Exception] = None
        total_input_tokens = 0
        total_output_tokens = 0

        for attempt in range(self._JSON_PARSE_MAX_RETRIES + 1):
            prompt = self._build_prompt(title, body, source_lang, target_lang)
            if attempt > 0:
                prompt += (
                    "\n\nCRITICAL: Your previous response could not be parsed as JSON. "
                    "Output ONLY a raw JSON object — no markdown fences, no explanation, "
                    "no text before or after the JSON."
                )

            try:
                response = self.client.messages.create(
                    model=self.MODEL,
                    max_tokens=8192,
                    messages=[{"role": "user", "content": prompt}]
                )
                raw = response.content[0].text
                total_input_tokens += response.usage.input_tokens
                total_output_tokens += response.usage.output_tokens

                result = self._parse_response(raw)
                result.input_tokens = total_input_tokens
                result.output_tokens = total_output_tokens
                result.model = self.MODEL
                return result

            except json.JSONDecodeError as exc:
                last_parse_error = exc
                logger.warning(
                    f"Translation JSON parse error (attempt {attempt + 1}/{self._JSON_PARSE_MAX_RETRIES + 1}) "
                    f"lang={target_lang}: {exc}"
                )
                continue

            except Exception as e:
                logger.error(f"Translation failed: {e}")
                raise

        # All retry attempts exhausted — try regex fallback before raising
        logger.error(
            f"All {self._JSON_PARSE_MAX_RETRIES + 1} translation attempts returned malformed JSON "
            f"for lang={target_lang}. Attempting regex fallback."
        )
        try:
            result = self._parse_response_fallback(raw, target_lang)
            result.input_tokens = total_input_tokens
            result.output_tokens = total_output_tokens
            result.model = self.MODEL
            return result
        except Exception as fallback_exc:
            logger.error(f"Regex fallback also failed for lang={target_lang}: {fallback_exc}")
            raise last_parse_error

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
        """Parse Claude's JSON response.

        Raises json.JSONDecodeError if the response cannot be parsed as valid JSON.
        """
        text = response.strip()

        # Strip markdown code fences: ```json ... ``` or ``` ... ```
        if text.startswith("```"):
            # Remove opening fence (with optional language tag) and closing fence
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            text = text.strip()

        # Extract first JSON object/array if surrounded by stray text
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            text = json_match.group(0)

        data = json.loads(text)

        return TranslationResult(
            title=data.get("title") or "",
            body=data.get("body") or "",
            summary=data.get("summary") or "",
            confidence=float(data.get("confidence", 0.7))
        )

    def _parse_response_fallback(self, response: str, target_lang: str) -> TranslationResult:
        """Last-resort regex extraction when JSON is hopelessly malformed.

        Attempts to pull field values from the raw text using regex.
        Returns a low-confidence result marked for human review.
        """
        def _extract_field(field: str) -> str:
            # Match "field": "value" allowing escaped quotes inside
            pattern = rf'"{field}"\s*:\s*"((?:[^"\\]|\\.)*)"'
            m = re.search(pattern, response, re.DOTALL)
            return m.group(1).encode().decode('unicode_escape', errors='replace') if m else ""

        title = _extract_field("title")
        body = _extract_field("body")
        summary = _extract_field("summary")

        if not title and not body:
            raise ValueError(f"Regex fallback could not extract any content from response (lang={target_lang})")

        logger.warning(
            f"Translation for lang={target_lang} recovered via regex fallback. "
            "Confidence forced to 0.5 for human review."
        )
        return TranslationResult(
            title=title,
            body=body,
            summary=summary,
            confidence=0.5,  # Force DRAFT status; requires human review
        )

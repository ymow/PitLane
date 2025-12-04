"""F1 entity extraction from article text."""
import re
from typing import List, Set
from apps.news.models import Driver, Team
import logging

logger = logging.getLogger(__name__)


class F1EntityExtractor:
    """
    Extract F1 driver and team mentions from article text.
    Uses pattern matching (can be enhanced with NLP later).
    """

    def __init__(self):
        """Initialize and load entities from database."""
        self.drivers = {}
        self.teams = {}
        self._load_entities()

    def _load_entities(self):
        """Load drivers and teams from database."""
        # Load drivers
        for driver in Driver.objects.all():
            # Map various name forms to driver
            self.drivers[driver.code.upper()] = driver
            self.drivers[driver.last_name.upper()] = driver
            self.drivers[f"{driver.first_name} {driver.last_name}".upper()] = driver

        # Load teams
        for team in Team.objects.all():
            self.teams[team.code.upper()] = team
            self.teams[team.name.upper()] = team
            self.teams[team.short_name.upper()] = team

        logger.info(f"Loaded {len(set(self.drivers.values()))} drivers and {len(set(self.teams.values()))} teams")

    def _calculate_score(self, text: str, title: str, pattern: str) -> int:
        """Calculate relevance score for an entity."""
        score = 0
        text_upper = text.upper()
        title_upper = title.upper()
        pattern_upper = pattern.upper()
        
        # Title mentions are worth 10 points
        if re.search(rf'\b{re.escape(pattern_upper)}\b', title_upper):
            score += 10
            
        # Body mentions are worth 1 point each
        matches = re.findall(rf'\b{re.escape(pattern_upper)}\b', text_upper)
        score += len(matches)
        
        return score

    def extract_drivers(self, title: str, body: str) -> List[dict]:
        """Extract drivers with relevance scoring."""
        full_text = f"{title} {body}"
        scores = {}  # driver_id -> {'entity': driver, 'score': 0}

        for pattern, driver in self.drivers.items():
            if driver.id in scores:
                continue
                
            # Check if mentioned at all first to save regex cycles
            if pattern in full_text.upper():
                score = self._calculate_score(body, title, pattern)
                if score > 0:
                    if driver.id in scores:
                        scores[driver.id]['score'] = max(scores[driver.id]['score'], score)
                    else:
                        scores[driver.id] = {
                            'entity': driver,
                            'score': score
                        }

        # Determine primary status (Top 2 or score > 5)
        results = []
        if not scores:
            return results

        sorted_drivers = sorted(scores.values(), key=lambda x: x['score'], reverse=True)
        
        for i, item in enumerate(sorted_drivers):
            # Primary if rank <= 1 (top 2) OR score >= 10 (in title)
            is_primary = i <= 1 or item['score'] >= 10
            results.append({
                'entity': item['entity'],
                'is_primary': is_primary,
                'score': item['score']
            })
            
        return results

    def extract_teams(self, title: str, body: str) -> List[dict]:
        """Extract teams with relevance scoring."""
        full_text = f"{title} {body}"
        scores = {}

        for pattern, team in self.teams.items():
            if team.id in scores:
                continue

            if pattern in full_text.upper():
                score = self._calculate_score(body, title, pattern)
                if score > 0:
                    if team.id in scores:
                        scores[team.id]['score'] = max(scores[team.id]['score'], score)
                    else:
                        scores[team.id] = {
                            'entity': team,
                            'score': score
                        }

        results = []
        if not scores:
            return results

        sorted_teams = sorted(scores.values(), key=lambda x: x['score'], reverse=True)
        
        for i, item in enumerate(sorted_teams):
            is_primary = i <= 0 or item['score'] >= 10  # Only top 1 team is primary usually
            results.append({
                'entity': item['entity'],
                'is_primary': is_primary,
                'score': item['score']
            })

        return results

    def process_article(self, title: str, body: str) -> dict:
        """
        Process article and return extracted entities with primary status.

        Returns:
            {
                'drivers': [{'entity': Driver, 'is_primary': bool}, ...],
                'teams': [{'entity': Team, 'is_primary': bool}, ...]
            }
        """
        return {
            'drivers': self.extract_drivers(title, body),
            'teams': self.extract_teams(title, body)
        }

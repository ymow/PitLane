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

    def extract_drivers(self, text: str) -> Set[Driver]:
        """Extract mentioned drivers from text."""
        text_upper = text.upper()
        found = set()

        for pattern, driver in self.drivers.items():
            # Word boundary matching
            if re.search(rf'\b{re.escape(pattern)}\b', text_upper):
                found.add(driver)

        return found

    def extract_teams(self, text: str) -> Set[Team]:
        """Extract mentioned teams from text."""
        text_upper = text.upper()
        found = set()

        for pattern, team in self.teams.items():
            if re.search(rf'\b{re.escape(pattern)}\b', text_upper):
                found.add(team)

        return found

    def process_article(self, title: str, body: str) -> dict:
        """
        Process article and return extracted entities.

        Returns:
            {
                'drivers': [Driver, ...],
                'teams': [Team, ...]
            }
        """
        full_text = f"{title} {body}"

        return {
            'drivers': list(self.extract_drivers(full_text)),
            'teams': list(self.extract_teams(full_text))
        }

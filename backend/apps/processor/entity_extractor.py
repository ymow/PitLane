import re
from typing import List, Set, Dict
from apps.teams.models import Driver, Team
from apps.processor.monitoring import monitor_memory
import logging

logger = logging.getLogger(__name__)


class F1EntityExtractor:
    """
    Extract F1 driver and team mentions using Spacy NER (Primary) 
    or Regex (Fallback) + Database matching.
    """

    def __init__(self, nlp=None):
        """Initialize with Spacy model and load entities from database."""
        # Use shared NLP model if provided (for performance in Celery)
        self.nlp = nlp
        
        if not self.nlp:
            try:
                import spacy
                # Try to load if available, but don't crash if not
                self.nlp = spacy.load("en_core_web_sm")
            except (ImportError, Exception):
                # If spacy is missing or model not found, we will use regex fallback
                logger.warning("Spacy not available, using Regex fallback for entity extraction")
                self.nlp = None

        self.drivers_by_name = {}
        self.teams_by_name = {}
        self._load_entities()

    def _load_entities(self):
        """Load drivers and teams from database for matching."""
        # Load drivers
        for driver in Driver.objects.all():
            # Map various name forms (Uppercase for case-insensitive match)
            if driver.last_name:
                self.drivers_by_name[driver.last_name.upper()] = driver
            if driver.full_name:
                self.drivers_by_name[driver.full_name.upper()] = driver
            if driver.code:
                self.drivers_by_name[driver.code.upper()] = driver

        # Load teams
        for team in Team.objects.all():
            if team.base_name:
                self.teams_by_name[team.base_name.upper()] = team
            if team.code:
                self.teams_by_name[team.code.upper()] = team

        logger.info(f"Loaded {len(set(self.drivers_by_name.values()))} drivers and {len(set(self.teams_by_name.values()))} teams")

    def _calculate_relevance(self, title: str, body: str, entity_name: str) -> int:
        """Score relevance based on frequency and position."""
        if not entity_name:
            return 0
        score = 0
        # Use word boundaries to avoid partial matches
        pattern = rf'\b{re.escape(entity_name)}\b'
        
        # Title mentions = 10 pts
        if re.search(pattern, title, re.IGNORECASE):
            score += 10
            
        # Body mentions = 1 pt each
        matches = re.findall(pattern, body, re.IGNORECASE)
        score += len(matches)
        
        return score

    @monitor_memory("entity_extractor")
    def process_article(self, title: str, body: str) -> dict:
        """
        Process article using Spacy NER or Regex fallback.
        """
        found_drivers = {} # driver_id -> {entity, score}
        found_teams = {}   # team_id -> {entity, score}

        if self.nlp:
            # --- PRIMARY: Spacy NER ---
            full_text = f"{title}. {body}"
            doc = self.nlp(full_text)

            for ent in doc.ents:
                ent_text_upper = ent.text.upper()
                if ent.label_ == "PERSON" and ent_text_upper in self.drivers_by_name:
                    driver = self.drivers_by_name[ent_text_upper]
                    if driver.id not in found_drivers:
                        score = self._calculate_relevance(title, body, ent.text)
                        found_drivers[driver.id] = {'entity': driver, 'score': score}
                elif ent.label_ == "ORG" and ent_text_upper in self.teams_by_name:
                    team = self.teams_by_name[ent_text_upper]
                    if team.id not in found_teams:
                        score = self._calculate_relevance(title, body, ent.text)
                        found_teams[team.id] = {'entity': team, 'score': score}
        else:
            # --- FALLBACK: Simple Keyword Match ---
            # Search for each driver in title/body
            for name, driver in self.drivers_by_name.items():
                if driver.id in found_drivers: continue
                score = self._calculate_relevance(title, body, name)
                if score > 0:
                    found_drivers[driver.id] = {'entity': driver, 'score': score}
            
            # Search for each team in title/body
            for name, team in self.teams_by_name.items():
                if team.id in found_teams: continue
                score = self._calculate_relevance(title, body, name)
                if score > 0:
                    found_teams[team.id] = {'entity': team, 'score': score}

        # Finalize and Sort Results
        # is_primary = ranked first (highest score) OR mentioned in title (score >= 10)
        driver_results = []
        sorted_drivers = sorted(found_drivers.values(), key=lambda x: x['score'], reverse=True)
        for i, item in enumerate(sorted_drivers):
            driver_results.append({
                'entity': item['entity'],
                'is_primary': i == 0 and item['score'] >= 10,
                'score': item['score']
            })

        team_results = []
        sorted_teams = sorted(found_teams.values(), key=lambda x: x['score'], reverse=True)
        for i, item in enumerate(sorted_teams):
            team_results.append({
                'entity': item['entity'],
                'is_primary': i == 0 and item['score'] >= 10,
                'score': item['score']
            })

        return {'drivers': driver_results, 'teams': team_results}

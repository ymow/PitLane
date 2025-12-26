import re
import spacy
from typing import List, Set, Dict
from apps.teams.models import Driver, Team
from apps.processor.monitoring import monitor_memory
import logging

logger = logging.getLogger(__name__)


class F1EntityExtractor:
    """
    Extract F1 driver and team mentions using Spacy NER + Database matching.
    """

    def __init__(self, nlp=None):
        """Initialize with Spacy model and load entities from database."""
        # Use shared NLP model if provided (for performance in Celery)
        if nlp:
            self.nlp = nlp
        else:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                logger.error(f"Failed to load Spacy model: {e}")
                self.nlp = None

        self.drivers_by_name = {}
        self.teams_by_name = {}
        self._load_entities()

    def _load_entities(self):
        """Load drivers and teams from database for matching."""
        # Load drivers
        for driver in Driver.objects.all():
            # Map various name forms (Uppercase for case-insensitive match)
            self.drivers_by_name[driver.last_name.upper()] = driver
            self.drivers_by_name[driver.full_name.upper()] = driver
            self.drivers_by_name[driver.code.upper()] = driver

        # Load teams
        for team in Team.objects.all():
            self.teams_by_name[team.base_name.upper()] = team
            self.teams_by_name[team.code.upper()] = team

        logger.info(f"Loaded {len(set(self.drivers_by_name.values()))} drivers and {len(set(self.teams_by_name.values()))} teams")

    def _calculate_relevance(self, title: str, body: str, entity_name: str) -> int:
        """Score relevance based on frequency and position."""
        score = 0
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
        Process article using Spacy NER and filter against F1 database.
        """
        if not self.nlp:
            return {'drivers': [], 'teams': []}

        # Combine for NER
        full_text = f"{title}. {body}"
        doc = self.nlp(full_text)

        found_drivers = {} # driver_id -> {entity, score}
        found_teams = {}   # team_id -> {entity, score}

        # 1. Iterate over entities found by Spacy
        for ent in doc.ents:
            ent_text_upper = ent.text.upper()
            
            # Case A: PERSON -> Check Drivers
            if ent.label_ == "PERSON":
                if ent_text_upper in self.drivers_by_name:
                    driver = self.drivers_by_name[ent_text_upper]
                    if driver.id not in found_drivers:
                        score = self._calculate_relevance(title, body, ent.text)
                        found_drivers[driver.id] = {'entity': driver, 'score': score}

            # Case B: ORG -> Check Teams
            elif ent.label_ == "ORG":
                if ent_text_upper in self.teams_by_name:
                    team = self.teams_by_name[ent_text_upper]
                    if team.id not in found_teams:
                        score = self._calculate_relevance(title, body, ent.text)
                        found_teams[team.id] = {'entity': team, 'score': score}

        # 2. Finalize Driver Results
        driver_results = []
        sorted_drivers = sorted(found_drivers.values(), key=lambda x: x['score'], reverse=True)
        for i, item in enumerate(sorted_drivers):
            driver_results.append({
                'entity': item['entity'],
                'is_primary': i == 0 or item['score'] >= 10, # Top result or in Title
                'score': item['score']
            })

        # 3. Finalize Team Results
        team_results = []
        sorted_teams = sorted(found_teams.values(), key=lambda x: x['score'], reverse=True)
        for i, item in enumerate(sorted_teams):
            team_results.append({
                'entity': item['entity'],
                'is_primary': i == 0 or item['score'] >= 10,
                'score': item['score']
            })

        return {
            'drivers': driver_results,
            'teams': team_results
        }

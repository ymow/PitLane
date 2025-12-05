"""Jolpica F1 API Client."""
import requests
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class JolpicaClient:
    """
    Client for the Jolpica F1 API (Ergast compatible).
    Documentation: https://github.com/jolpica/jolpica-f1
    Base URL: http://api.jolpi.ca/ergast/f1
    """

    BASE_URL = "http://api.jolpi.ca/ergast/f1"
    TIMEOUT = 10  # seconds

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make GET request to API."""
        url = f"{self.BASE_URL}/{endpoint}.json"
        try:
            response = requests.get(url, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Jolpica API error ({endpoint}): {e}")
            return None

    def get_season_races(self, year: int) -> Optional[Dict]:
        """Get all races for a specific season."""
        return self._get(f"{year}")

    def get_race_results(self, year: int, round_number: int) -> Optional[Dict]:
        """Get results for a specific race."""
        return self._get(f"{year}/{round_number}/results")

    def get_driver_standings(self, year: int) -> Optional[Dict]:
        """Get driver standings for a specific season."""
        return self._get(f"{year}/driverStandings")

    def get_constructor_standings(self, year: int) -> Optional[Dict]:
        """Get constructor standings for a specific season."""
        return self._get(f"{year}/constructorStandings")

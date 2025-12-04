"""F1 Data Normalizer (Jolpica/Ergast to Django Models)."""
from datetime import datetime, timezone as dt_timezone
from django.utils import timezone
from apps.championships.models import Season, DriverStanding, ConstructorStanding
from apps.racing.models import Race, Session, RaceResult
from apps.circuits.models import Circuit
from apps.teams.models import Driver, Team
# Import analysis task
from apps.analysis.tasks import generate_session_analysis
import logging

logger = logging.getLogger(__name__)


class F1DataNormalizer:
    """Transform raw API data into Model instances."""

    def __init__(self):
        self.teams_map = self._build_team_map()
        self.drivers_map = self._build_driver_map()

    def _build_team_map(self):
        """Map Jolpica constructorId to Team database objects."""
        # Simple map based on known 2025 grid.
        # Keys are Jolpica IDs, Values are Team objects
        # In production, this should be more robust or stored in DB.
        mapping = {}
        teams = Team.objects.all()
        for team in teams:
            # Normalize team name for matching
            key = team.base_name.lower().replace(" ", "_")
            mapping[key] = team
            
            # Handle specific mappings
            if "red_bull" in key: mapping["red_bull"] = team
            if "ferrari" in key: mapping["ferrari"] = team
            if "mclaren" in key: mapping["mclaren"] = team
            if "mercedes" in key: mapping["mercedes"] = team
            if "aston" in key: mapping["aston_martin"] = team
            if "alpine" in key: mapping["alpine"] = team
            if "williams" in key: mapping["williams"] = team
            if "haas" in key: mapping["haas"] = team
            if "sauber" in key: mapping["sauber"] = team
            if "rb" in key or "racing_bulls" in key: mapping["rb"] = team
            
        return mapping

    def _build_driver_map(self):
        """Map Jolpica driverId to Driver objects."""
        mapping = {}
        drivers = Driver.objects.all()
        for driver in drivers:
            # Jolpica usually uses 'lastname' or 'firstname_lastname'
            mapping[driver.last_name.lower()] = driver
            mapping[f"{driver.first_name.lower()}_{driver.last_name.lower()}"] = driver
            if driver.code:
                mapping[driver.code.lower()] = driver
        return mapping

    def _parse_datetime(self, date_str, time_str=None):
        """Combine date and time strings into aware datetime."""
        if not date_str:
            return None
        
        dt_str = date_str
        fmt = "%Y-%m-%d"
        
        if time_str:
            # Time often comes as "14:00:00Z"
            dt_str = f"{date_str} {time_str}"
            fmt = "%Y-%m-%d %H:%M:%SZ"
            
        try:
            dt = datetime.strptime(dt_str, fmt)
            return timezone.make_aware(dt, dt_timezone.utc)
        except ValueError:
            return None

    def sync_season_calendar(self, season_year: int, api_data: dict):
        """Sync races and circuits for a season."""
        season, _ = Season.objects.get_or_create(year=season_year)
        
        race_table = api_data.get("MRData", {}).get("RaceTable", {})
        races = race_table.get("Races", [])

        for item in races:
            # 1. Circuit
            circuit_data = item.get("Circuit", {})
            circuit, _ = Circuit.objects.update_or_create(
                code=circuit_data.get("circuitId"),
                defaults={
                    "name": circuit_data.get("circuitName"),
                    "country": circuit_data.get("Location", {}).get("country"),
                    "city": circuit_data.get("Location", {}).get("locality"),
                    "latitude": circuit_data.get("Location", {}).get("lat"),
                    "longitude": circuit_data.get("Location", {}).get("long"),
                    "website": circuit_data.get("url"),
                }
            )

            # 2. Race
            round_num = int(item.get("round"))
            race_date = self._parse_datetime(item.get("date"), item.get("time"))
            
            race, _ = Race.objects.update_or_create(
                season=season,
                round_number=round_num,
                defaults={
                    "circuit": circuit,
                    "official_name": item.get("raceName"),
                    "race_date": race_date.date() if race_date else None,
                    "race_time": race_date.time() if race_date else None,
                    "status": "COMPLETED" if race_date and race_date < timezone.now() else "SCHEDULED",
                    "is_sprint_weekend": "Sprint" in item
                }
            )
            
            logger.info(f"Synced Race: {race}")

    def sync_standings(self, season_year: int, driver_data: dict = None, constructor_data: dict = None):
        """Sync championship standings."""
        season = Season.objects.get(year=season_year)

        # Drivers
        if driver_data:
            standings = driver_data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [{}])[0].get("DriverStandings", [])
            for item in standings:
                driver_id = item.get("Driver", {}).get("driverId")
                driver = self.drivers_map.get(driver_id) or self.drivers_map.get(item.get("Driver", {}).get("familyName").lower())
                
                if driver:
                    DriverStanding.objects.update_or_create(
                        season=season,
                        driver=driver,
                        defaults={
                            "position": item.get("position"),
                            "points": item.get("points"),
                            "wins": item.get("wins"),
                        }
                    )

        # Constructors
        if constructor_data:
            standings = constructor_data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [{}])[0].get("ConstructorStandings", [])
            for item in standings:
                constr_id = item.get("Constructor", {}).get("constructorId")
                team = self.teams_map.get(constr_id)
                
                if team:
                    ConstructorStanding.objects.update_or_create(
                        season=season,
                        team=team,
                        defaults={
                            "position": item.get("position"),
                            "points": item.get("points"),
                            "wins": item.get("wins"),
                        }
                    )
        
        logger.info(f"Synced Standings for {season_year}")

    def sync_race_results(self, season_year: int, round_num: int, api_data: dict):
        """Sync results for a specific race."""
        try:
            race = Race.objects.get(season__year=season_year, round_number=round_num)
        except Race.DoesNotExist:
            logger.error(f"Race not found: {season_year} R{round_num}")
            return

        # Create Session (RACE) if missing
        session, _ = Session.objects.get_or_create(
            race=race,
            session_type='RACE',
            defaults={
                "session_name": "Race",
                "scheduled_start": timezone.make_aware(datetime.combine(race.race_date, race.race_time)) if race.race_time else timezone.now()
            }
        )

        results = api_data.get("MRData", {}).get("RaceTable", {}).get("Races", [{}])[0].get("Results", [])
        
        for item in results:
            driver_id = item.get("Driver", {}).get("driverId")
            constr_id = item.get("Constructor", {}).get("constructorId")
            
            driver = self.drivers_map.get(driver_id) or self.drivers_map.get(item.get("Driver", {}).get("familyName").lower())
            team = self.teams_map.get(constr_id)

            if driver and team:
                status_map = {
                    "Finished": "FINISHED",
                    "Collision": "ACCIDENT",
                    "Accident": "ACCIDENT",
                    "Disqualified": "DSQ",
                }
                status = status_map.get(item.get("status"), "FINISHED" if "Lap" in item.get("status", "") else "DNF")

                RaceResult.objects.update_or_create(
                    session=session,
                    driver=driver,
                    defaults={
                        "team": team,
                        "grid_position": item.get("grid"),
                        "finish_position": item.get("position"),
                        "classified_position": item.get("position"),
                        "finish_status": status,
                        "points": item.get("points"),
                        "laps_completed": item.get("laps"),
                        "fastest_lap_point": item.get("FastestLap", {}).get("rank") == "1"
                    }
                )
        
        logger.info(f"Synced Results for {race}")
        
        # Trigger Post-Race Analysis (FastF1)
        generate_session_analysis.delay(session.id)

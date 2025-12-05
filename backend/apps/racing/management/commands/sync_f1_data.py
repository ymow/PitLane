"""Management command to sync F1 data from Jolpica."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.fetcher.jolpica import JolpicaClient
from apps.processor.f1_normalizer import F1DataNormalizer
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Sync F1 season data from Jolpica API."""
    help = 'Sync F1 calendar, results, and standings from Jolpica'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            default=timezone.now().year,
            help='Season year to sync (default: current year)'
        )
        parser.add_argument(
            '--action',
            type=str,
            choices=['all', 'calendar', 'standings', 'results'],
            default='all',
            help='Type of data to sync'
        )

    def handle(self, *args, **options):
        year = options['year']
        action = options['action']
        
        self.stdout.write(f"Syncing F1 data for {year} ({action})...")
        
        client = JolpicaClient()
        normalizer = F1DataNormalizer()

        # 1. Calendar (Races & Circuits)
        if action in ['all', 'calendar']:
            self.stdout.write("Fetching calendar...")
            data = client.get_season_races(year)
            if data:
                normalizer.sync_season_calendar(year, data)
                self.stdout.write(self.style.SUCCESS("Calendar synced"))

        # 2. Standings
        if action in ['all', 'standings']:
            self.stdout.write("Fetching standings...")
            drivers = client.get_driver_standings(year)
            constructors = client.get_constructor_standings(year)
            if drivers or constructors:
                normalizer.sync_standings(year, drivers, constructors)
                self.stdout.write(self.style.SUCCESS("Standings synced"))

        # 3. Results (for completed races)
        if action in ['all', 'results']:
            self.stdout.write("Fetching results...")
            # Get calendar first to know how many rounds
            cal_data = client.get_season_races(year)
            if cal_data:
                races = cal_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
                current_date = timezone.now().date()
                
                for race in races:
                    round_num = int(race.get("round"))
                    date_str = race.get("date")
                    
                    # Only fetch past races
                    if date_str and date_str < str(current_date):
                        self.stdout.write(f"  Fetching Round {round_num}...")
                        res_data = client.get_race_results(year, round_num)
                        if res_data:
                            normalizer.sync_race_results(year, round_num, res_data)
            
            self.stdout.write(self.style.SUCCESS("Results synced"))

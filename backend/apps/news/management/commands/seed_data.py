"""Management command to seed database with F1 2025 data."""
from django.core.management.base import BaseCommand
from apps.news.models import Team, Driver, Source
from apps.fetcher.sources import SOURCES


class Command(BaseCommand):
    help = 'Seed database with 2025 F1 teams, drivers, and RSS sources'

    def handle(self, *args, **options):
        self.stdout.write('Seeding F1 2025 data...')

        # Create teams
        teams_data = [
            {"code": "RBR", "name": "Red Bull Racing", "short_name": "Red Bull", "color": "#3671C6"},
            {"code": "FER", "name": "Scuderia Ferrari", "short_name": "Ferrari", "color": "#E80020"},
            {"code": "MCL", "name": "McLaren F1 Team", "short_name": "McLaren", "color": "#FF8000"},
            {"code": "MER", "name": "Mercedes-AMG Petronas", "short_name": "Mercedes", "color": "#27F4D2"},
            {"code": "AMR", "name": "Aston Martin Aramco", "short_name": "Aston Martin", "color": "#229971"},
            {"code": "ALP", "name": "Alpine F1 Team", "short_name": "Alpine", "color": "#FF87BC"},
            {"code": "WIL", "name": "Williams Racing", "short_name": "Williams", "color": "#64C4FF"},
            {"code": "RBT", "name": "Racing Bulls", "short_name": "RB", "color": "#6692FF"},
            {"code": "HAA", "name": "MoneyGram Haas F1 Team", "short_name": "Haas", "color": "#B6BABD"},
            {"code": "SAU", "name": "Kick Sauber", "short_name": "Sauber", "color": "#52E252"},
        ]

        teams = {}
        for team_data in teams_data:
            team, created = Team.objects.get_or_create(
                code=team_data["code"],
                defaults={
                    "name": team_data["name"],
                    "short_name": team_data["short_name"],
                    "primary_color": team_data["color"]
                }
            )
            teams[team.code] = team
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created team: {team.name}'))
            else:
                self.stdout.write(f'  Team exists: {team.name}')

        # Create drivers
        drivers_data = [
            # Red Bull Racing
            {"code": "VER", "number": 1, "first_name": "Max", "last_name": "Verstappen", "team": "RBR", "nationality": "Dutch"},
            {"code": "LAW", "number": 30, "first_name": "Liam", "last_name": "Lawson", "team": "RBR", "nationality": "New Zealand"},

            # Ferrari
            {"code": "LEC", "number": 16, "first_name": "Charles", "last_name": "Leclerc", "team": "FER", "nationality": "Monegasque"},
            {"code": "HAM", "number": 44, "first_name": "Lewis", "last_name": "Hamilton", "team": "FER", "nationality": "British"},

            # McLaren
            {"code": "NOR", "number": 4, "first_name": "Lando", "last_name": "Norris", "team": "MCL", "nationality": "British"},
            {"code": "PIA", "number": 81, "first_name": "Oscar", "last_name": "Piastri", "team": "MCL", "nationality": "Australian"},

            # Mercedes
            {"code": "RUS", "number": 63, "first_name": "George", "last_name": "Russell", "team": "MER", "nationality": "British"},
            {"code": "ANT", "number": 12, "first_name": "Andrea Kimi", "last_name": "Antonelli", "team": "MER", "nationality": "Italian"},

            # Aston Martin
            {"code": "ALO", "number": 14, "first_name": "Fernando", "last_name": "Alonso", "team": "AMR", "nationality": "Spanish"},
            {"code": "STR", "number": 18, "first_name": "Lance", "last_name": "Stroll", "team": "AMR", "nationality": "Canadian"},

            # Alpine
            {"code": "GAS", "number": 10, "first_name": "Pierre", "last_name": "Gasly", "team": "ALP", "nationality": "French"},
            {"code": "DOO", "number": 7, "first_name": "Jack", "last_name": "Doohan", "team": "ALP", "nationality": "Australian"},

            # Williams
            {"code": "ALB", "number": 23, "first_name": "Alexander", "last_name": "Albon", "team": "WIL", "nationality": "Thai"},
            {"code": "SAI", "number": 55, "first_name": "Carlos", "last_name": "Sainz", "team": "WIL", "nationality": "Spanish"},

            # Racing Bulls
            {"code": "TSU", "number": 22, "first_name": "Yuki", "last_name": "Tsunoda", "team": "RBT", "nationality": "Japanese"},
            {"code": "HAD", "number": 6, "first_name": "Isack", "last_name": "Hadjar", "team": "RBT", "nationality": "French"},

            # Haas
            {"code": "BEA", "number": 50, "first_name": "Oliver", "last_name": "Bearman", "team": "HAA", "nationality": "British"},
            {"code": "OCO", "number": 31, "first_name": "Esteban", "last_name": "Ocon", "team": "HAA", "nationality": "French"},

            # Kick Sauber
            {"code": "HUL", "number": 27, "first_name": "Nico", "last_name": "Hülkenberg", "team": "SAU", "nationality": "German"},
            {"code": "BOR", "number": 5, "first_name": "Gabriel", "last_name": "Bortoleto", "team": "SAU", "nationality": "Brazilian"},
        ]

        for driver_data in drivers_data:
            team = teams.get(driver_data["team"])
            driver, created = Driver.objects.get_or_create(
                code=driver_data["code"],
                defaults={
                    "number": driver_data["number"],
                    "first_name": driver_data["first_name"],
                    "last_name": driver_data["last_name"],
                    "nationality": driver_data["nationality"],
                    "team": team
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created driver: {driver.first_name} {driver.last_name}'))
            else:
                self.stdout.write(f'  Driver exists: {driver.first_name} {driver.last_name}')

        # Create RSS sources
        for slug, source_data in SOURCES.items():
            source, created = Source.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": source_data["name"],
                    "feed_url": source_data["feed_url"],
                    "lang": source_data["lang"],
                    "priority": source_data["priority"],
                    "fetch_interval": source_data["fetch_interval"],
                    "is_active": True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created source: {source.name}'))
            else:
                self.stdout.write(f'  Source exists: {source.name}')

        self.stdout.write(self.style.SUCCESS('\n✓ Database seeding completed!'))
        self.stdout.write(f'  Teams: {Team.objects.count()}')
        self.stdout.write(f'  Drivers: {Driver.objects.count()}')
        self.stdout.write(f'  Sources: {Source.objects.count()}')

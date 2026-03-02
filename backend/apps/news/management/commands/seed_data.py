"""Management command to seed database with F1 2025 data."""
from django.core.management.base import BaseCommand
from apps.news.models import Source, NewsCategory
from apps.teams.models import Team, Driver
from apps.fetcher.sources import SOURCES


class Command(BaseCommand):
    help = 'Seed database with 2025 F1 teams, drivers, and RSS sources'

    def handle(self, *args, **options):
        self.stdout.write('Seeding F1 2025 data...')

        # Create teams
        teams_data = [
            {"code": "RBR", "base_name": "Red Bull Racing", "country": "Austria", "founded_year": 2005, "color": "#3671C6"},
            {"code": "FER", "base_name": "Scuderia Ferrari", "country": "Italy", "founded_year": 1950, "color": "#E80020"},
            {"code": "MCL", "base_name": "McLaren F1 Team", "country": "United Kingdom", "founded_year": 1966, "color": "#FF8000"},
            {"code": "MER", "base_name": "Mercedes-AMG Petronas", "country": "Germany", "founded_year": 2010, "color": "#27F4D2"},
            {"code": "AMR", "base_name": "Aston Martin Aramco", "country": "United Kingdom", "founded_year": 2021, "color": "#229971"},
            {"code": "ALP", "base_name": "Alpine F1 Team", "country": "France", "founded_year": 2021, "color": "#FF87BC"},
            {"code": "WIL", "base_name": "Williams Racing", "country": "United Kingdom", "founded_year": 1977, "color": "#64C4FF"},
            {"code": "RBT", "base_name": "Racing Bulls", "country": "Italy", "founded_year": 2024, "color": "#6692FF"},
            {"code": "HAA", "base_name": "MoneyGram Haas F1 Team", "country": "United States", "founded_year": 2016, "color": "#B6BABD"},
            {"code": "SAU", "base_name": "Kick Sauber", "country": "Switzerland", "founded_year": 1993, "color": "#52E252"},
            {"code": "CAD", "base_name": "Cadillac F1 Team", "country": "United States", "founded_year": 2026, "color": "#041E42"},
        ]

        teams = {}
        for team_data in teams_data:
            team, created = Team.objects.get_or_create(
                code=team_data["code"],
                defaults={
                    "base_name": team_data["base_name"],
                    "country": team_data["country"],
                    "founded_year": team_data["founded_year"],
                    "primary_color": team_data["color"]
                }
            )
            teams[team.code] = team
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created team: {team.base_name}'))
            else:
                self.stdout.write(f'  Team exists: {team.base_name}')

        # Create news categories
        categories_data = [
            {"name": "Breaking News", "slug": "breaking", "color": "#DC2626", "display_order": 1},
            {"name": "Race Reports", "slug": "race-reports", "color": "#2563EB", "display_order": 2},
            {"name": "Qualifying", "slug": "qualifying", "color": "#7C3AED", "display_order": 3},
            {"name": "Practice", "slug": "practice", "color": "#059669", "display_order": 4},
            {"name": "Technical", "slug": "technical", "color": "#EA580C", "display_order": 5},
            {"name": "Transfers", "slug": "transfers", "color": "#DB2777", "display_order": 6},
            {"name": "Interviews", "slug": "interviews", "color": "#0891B2", "display_order": 7},
            {"name": "Opinion", "slug": "opinion", "color": "#65A30D", "display_order": 8},
        ]

        for category_data in categories_data:
            category, created = NewsCategory.objects.get_or_create(
                slug=category_data["slug"],
                defaults=category_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created category: {category.name}'))
            else:
                self.stdout.write(f'  Category exists: {category.name}')

        # Create drivers
        drivers_data = [
            # Red Bull Racing
            {"code": "VER", "number": 1, "first_name": "Max", "last_name": "Verstappen", "dob": "1997-09-30", "nationality": "Dutch"},
            {"code": "LAW", "number": 30, "first_name": "Liam", "last_name": "Lawson", "dob": "2002-02-11", "nationality": "New Zealand"},

            # Ferrari
            {"code": "LEC", "number": 16, "first_name": "Charles", "last_name": "Leclerc", "dob": "1997-10-16", "nationality": "Monegasque"},
            {"code": "HAM", "number": 44, "first_name": "Lewis", "last_name": "Hamilton", "dob": "1985-01-07", "nationality": "British"},

            # McLaren
            {"code": "NOR", "number": 4, "first_name": "Lando", "last_name": "Norris", "dob": "1999-11-13", "nationality": "British"},
            {"code": "PIA", "number": 81, "first_name": "Oscar", "last_name": "Piastri", "dob": "2001-04-06", "nationality": "Australian"},

            # Mercedes
            {"code": "RUS", "number": 63, "first_name": "George", "last_name": "Russell", "dob": "1998-02-15", "nationality": "British"},
            {"code": "ANT", "number": 12, "first_name": "Andrea Kimi", "last_name": "Antonelli", "dob": "2006-08-25", "nationality": "Italian"},

            # Aston Martin
            {"code": "ALO", "number": 14, "first_name": "Fernando", "last_name": "Alonso", "dob": "1981-07-29", "nationality": "Spanish"},
            {"code": "STR", "number": 18, "first_name": "Lance", "last_name": "Stroll", "dob": "1998-10-29", "nationality": "Canadian"},

            # Alpine
            {"code": "GAS", "number": 10, "first_name": "Pierre", "last_name": "Gasly", "dob": "1996-02-07", "nationality": "French"},

            # Williams
            {"code": "ALB", "number": 23, "first_name": "Alexander", "last_name": "Albon", "dob": "1996-03-23", "nationality": "Thai"},
            {"code": "SAI", "number": 55, "first_name": "Carlos", "last_name": "Sainz", "dob": "1994-09-01", "nationality": "Spanish"},

            # Racing Bulls
            {"code": "TSU", "number": 22, "first_name": "Yuki", "last_name": "Tsunoda", "dob": "2000-05-11", "nationality": "Japanese"},
            {"code": "HAD", "number": 6, "first_name": "Isack", "last_name": "Hadjar", "dob": "2004-09-28", "nationality": "French"},

            # Haas
            {"code": "OCO", "number": 31, "first_name": "Esteban", "last_name": "Ocon", "dob": "1996-09-17", "nationality": "French"},

            # Kick Sauber
            {"code": "HUL", "number": 27, "first_name": "Nico", "last_name": "Hülkenberg", "dob": "1987-08-19", "nationality": "German"},
            {"code": "BOR", "number": 5, "first_name": "Gabriel", "last_name": "Bortoleto", "dob": "2004-10-14", "nationality": "Brazilian"},

            # Cadillac F1 Team
            {"code": "BEA", "number": 50, "first_name": "Oliver", "last_name": "Bearman", "dob": "2005-05-08", "nationality": "British"},
            {"code": "DOO", "number": 7, "first_name": "Jack", "last_name": "Doohan", "dob": "2003-01-20", "nationality": "Australian"},
        ]

        for driver_data in drivers_data:
            driver, created = Driver.objects.get_or_create(
                code=driver_data["code"],
                defaults={
                    "racing_number": driver_data["number"],
                    "first_name": driver_data["first_name"],
                    "last_name": driver_data["last_name"],
                    "full_name": f"{driver_data['first_name']} {driver_data['last_name']}",
                    "nationality": driver_data["nationality"],
                    "date_of_birth": driver_data["dob"]
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created driver: {driver.full_name}'))
            else:
                self.stdout.write(f'  Driver exists: {driver.full_name}')

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
        self.stdout.write(f'  Categories: {NewsCategory.objects.count()}')
        self.stdout.write(f'  Sources: {Source.objects.count()}')

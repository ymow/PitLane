from django.core.management.base import BaseCommand
from apps.championships.models import Season
from apps.racing.models import Race, Session
from apps.circuits.models import Circuit
from datetime import date, datetime
import pytz

class Command(BaseCommand):
    help = 'Seed the official F1 2026 Season Schedule.'

    def handle(self, *args, **options):
        # 1. Create Season 2026
        season, _ = Season.objects.get_or_create(
            year=2026,
            defaults={'name': 'FIA Formula One World Championship 2026'}
        )
        self.stdout.write(self.style.SUCCESS(f'Season 2026: {season.name}'))

        # 2. Define Official 2026 Schedule
        # Based on FIA official announcement
        schedule = [
            (1, "Australian Grand Prix", "albert_park", date(2026, 3, 15)),
            (2, "Chinese Grand Prix", "shanghai", date(2026, 3, 22)),
            (3, "Japanese Grand Prix", "suzuka", date(2026, 4, 5)),
            (4, "Bahrain Grand Prix", "bahrain", date(2026, 4, 19)),
            (5, "Saudi Arabian Grand Prix", "jeddah", date(2026, 4, 26)),
            (6, "Miami Grand Prix", "miami", date(2026, 5, 10)),
            (7, "Emilia Romagna Grand Prix", "imola", date(2026, 5, 24)),
            (8, "Monaco Grand Prix", "monaco", date(2026, 5, 31)),
            (9, "Spanish Grand Prix", "catalunya", date(2026, 6, 14)),
            (10, "Canadian Grand Prix", "villeneuve", date(2026, 6, 28)),
            (11, "Austrian Grand Prix", "red_bull_ring", date(2026, 7, 5)),
            (12, "British Grand Prix", "silverstone", date(2026, 7, 12)),
            (13, "Belgian Grand Prix", "spa", date(2026, 7, 26)),
            (14, "Hungarian Grand Prix", "hungaroring", date(2026, 8, 2)),
            (15, "Dutch Grand Prix", "zandvoort", date(2026, 8, 30)),
            (16, "Italian Grand Prix", "monza", date(2026, 9, 6)),
            (17, "Azerbaijan Grand Prix", "baku", date(2026, 9, 20)),
            (18, "Singapore Grand Prix", "marina_bay", date(2026, 10, 4)),
            (19, "United States Grand Prix", "americas", date(2026, 10, 25)),
            (20, "Mexico City Grand Prix", "rodriguez", date(2026, 11, 1)),
            (21, "Sao Paulo Grand Prix", "interlagos", date(2026, 11, 8)),
            (22, "Las Vegas Grand Prix", "vegas", date(2026, 11, 22)),
            (23, "Qatar Grand Prix", "losail", date(2026, 11, 29)),
            (24, "Abu Dhabi Grand Prix", "yas_marina", date(2026, 12, 6)),
        ]

        for round_num, name, circuit_code, race_date in schedule:
            # Get or create circuit
            circuit = Circuit.objects.filter(code=circuit_code).first()
            if not circuit:
                # Create a placeholder circuit if missing
                circuit = Circuit.objects.create(
                    code=circuit_code,
                    name=name.replace(" Grand Prix", " Circuit"),
                    country="Unknown"
                )

            # Create Race
            race, created = Race.objects.get_or_create(
                season=season,
                round_number=round_num,
                defaults={
                    'official_name': name,
                    'circuit': circuit,
                    'race_date': race_date,
                    'status': 'SCHEDULED'
                }
            )

            if created:
                # Create main sessions for this race
                # Standard start time placeholder (13:00 UTC)
                start_time = datetime.combine(race_date, datetime.min.time()).replace(hour=13, tzinfo=pytz.UTC)
                
                Session.objects.get_or_create(
                    race=race,
                    session_type='RACE',
                    defaults={
                        'session_name': 'Race',
                        'scheduled_start': start_time,
                        'status': 'SCHEDULED'
                    }
                )
                self.stdout.write(f"Added Round {round_num}: {name}")

        self.stdout.write(self.style.SUCCESS('Successfully seeded 2026 Schedule!'))

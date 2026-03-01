from django.core.management.base import BaseCommand
from apps.championships.models import Season
from apps.racing.models import Race, Session
from apps.circuits.models import Circuit
from datetime import date, datetime
import pytz

class Command(BaseCommand):
    help = 'Seed the official F1 2026 Season Schedule (24 races, corrected dates).'

    def handle(self, *args, **options):
        # 1. Create Season 2026
        season, _ = Season.objects.get_or_create(
            year=2026,
            defaults={'name': 'FIA Formula One World Championship 2026'}
        )
        self.stdout.write(self.style.SUCCESS(f'Season 2026: {season.name}'))

        # 2. Official 2026 Schedule — race day (Sunday) dates
        # Source: formula1.com/en/racing/2026 (verified 2026-03-01)
        # Notes:
        #   - Australia opens the season (March 8), NOT Bahrain
        #   - No Emilia Romagna/Imola in 2026; Canada replaces it (Round 7)
        #   - Two Spanish GPs: Barcelona (Round 9, June) + Madrid (Round 16, Sep)
        #   - Abu Dhabi finale: December 6
        schedule = [
            (1,  "Australian Grand Prix",          "albert_park",   date(2026, 3,  8)),
            (2,  "Chinese Grand Prix",             "shanghai",      date(2026, 3, 15)),
            (3,  "Japanese Grand Prix",            "suzuka",        date(2026, 3, 29)),
            (4,  "Bahrain Grand Prix",             "bahrain",       date(2026, 4, 12)),
            (5,  "Saudi Arabian Grand Prix",       "jeddah",        date(2026, 4, 19)),
            (6,  "Miami Grand Prix",               "miami",         date(2026, 5,  3)),
            (7,  "Canadian Grand Prix",            "villeneuve",    date(2026, 5, 24)),
            (8,  "Monaco Grand Prix",              "monaco",        date(2026, 6,  7)),
            (9,  "Gran Premio de Barcelona-Catalunya", "catalunya", date(2026, 6, 14)),
            (10, "Austrian Grand Prix",            "red_bull_ring", date(2026, 6, 28)),
            (11, "British Grand Prix",             "silverstone",   date(2026, 7,  5)),
            (12, "Belgian Grand Prix",             "spa",           date(2026, 7, 19)),
            (13, "Hungarian Grand Prix",           "hungaroring",   date(2026, 7, 26)),
            (14, "Dutch Grand Prix",               "zandvoort",     date(2026, 8, 23)),
            (15, "Italian Grand Prix",             "monza",         date(2026, 9,  6)),
            (16, "Gran Premio de España",          "madrid",        date(2026, 9, 13)),
            (17, "Azerbaijan Grand Prix",          "baku",          date(2026, 9, 26)),
            (18, "Singapore Grand Prix",           "marina_bay",    date(2026, 10, 11)),
            (19, "United States Grand Prix",       "americas",      date(2026, 10, 25)),
            (20, "Mexico City Grand Prix",         "rodriguez",     date(2026, 11,  1)),
            (21, "Sao Paulo Grand Prix",           "interlagos",    date(2026, 11,  8)),
            (22, "Las Vegas Grand Prix",           "vegas",         date(2026, 11, 21)),
            (23, "Qatar Grand Prix",               "losail",        date(2026, 11, 29)),
            (24, "Abu Dhabi Grand Prix",           "yas_marina",    date(2026, 12,  6)),
        ]

        # Circuit country lookup for placeholder creation
        circuit_countries = {
            "albert_park":   ("Albert Park Circuit",          "Australia"),
            "shanghai":      ("Shanghai International Circuit","China"),
            "suzuka":        ("Suzuka Circuit",               "Japan"),
            "bahrain":       ("Bahrain International Circuit", "Bahrain"),
            "jeddah":        ("Jeddah Corniche Circuit",      "Saudi Arabia"),
            "miami":         ("Miami International Autodrome","United States"),
            "villeneuve":    ("Circuit Gilles Villeneuve",    "Canada"),
            "monaco":        ("Circuit de Monaco",            "Monaco"),
            "catalunya":     ("Circuit de Barcelona-Catalunya","Spain"),
            "red_bull_ring": ("Red Bull Ring",                "Austria"),
            "silverstone":   ("Silverstone Circuit",          "United Kingdom"),
            "spa":           ("Circuit de Spa-Francorchamps", "Belgium"),
            "hungaroring":   ("Hungaroring",                  "Hungary"),
            "zandvoort":     ("Circuit Zandvoort",            "Netherlands"),
            "monza":         ("Autodromo Nazionale Monza",    "Italy"),
            "madrid":        ("Circuito de Madrid",           "Spain"),
            "baku":          ("Baku City Circuit",            "Azerbaijan"),
            "marina_bay":    ("Marina Bay Street Circuit",    "Singapore"),
            "americas":      ("Circuit of the Americas",      "United States"),
            "rodriguez":     ("Autodromo Hermanos Rodriguez",  "Mexico"),
            "interlagos":    ("Autodromo Jose Carlos Pace",   "Brazil"),
            "vegas":         ("Las Vegas Strip Circuit",      "United States"),
            "losail":        ("Losail International Circuit", "Qatar"),
            "yas_marina":    ("Yas Marina Circuit",           "United Arab Emirates"),
        }

        created_count = 0
        skipped_count = 0

        for round_num, name, circuit_code, race_date in schedule:
            circuit = Circuit.objects.filter(code=circuit_code).first()
            if not circuit:
                circuit_name, country = circuit_countries.get(
                    circuit_code,
                    (name.replace(" Grand Prix", " Circuit"), "Unknown")
                )
                circuit = Circuit.objects.create(
                    code=circuit_code,
                    name=circuit_name,
                    country=country,
                )
                self.stdout.write(f"  Created circuit: {circuit_name} ({circuit_code})")

            race, created = Race.objects.get_or_create(
                season=season,
                round_number=round_num,
                defaults={
                    'official_name': name,
                    'circuit':       circuit,
                    'race_date':     race_date,
                    'status':        'SCHEDULED',
                }
            )

            if created:
                start_time = datetime.combine(
                    race_date, datetime.min.time()
                ).replace(hour=13, tzinfo=pytz.UTC)
                Session.objects.get_or_create(
                    race=race,
                    session_type='RACE',
                    defaults={
                        'session_name':    'Race',
                        'scheduled_start': start_time,
                        'status':          'SCHEDULED',
                    }
                )
                self.stdout.write(f"  Added Round {round_num:2d}: {name} ({race_date})")
                created_count += 1
            else:
                self.stdout.write(f"  Exists Round {round_num:2d}: {name}")
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone — {created_count} created, {skipped_count} already existed.'
        ))
        self.stdout.write(
            f'Total races in DB for 2026: {Race.objects.filter(season=season).count()}'
        )

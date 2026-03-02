from django.core.management.base import BaseCommand
from apps.championships.models import Season
from apps.racing.models import Race, Session
from apps.circuits.models import Circuit
from datetime import date, datetime, timedelta
import pytz

# 2026 Sprint weekends (same 6 circuits as 2025 pattern)
SPRINT_WEEKENDS = {'shanghai', 'miami', 'spa', 'americas', 'interlagos', 'losail'}

# Full circuit data: code -> (name, country, city, lat, lng, timezone, circuit_type)
CIRCUITS_2026 = {
    'albert_park':  ('Albert Park Circuit',         'Australia',     'Melbourne',    -37.8497,  144.9680,  'Australia/Melbourne',   'STREET'),
    'shanghai':     ('Shanghai International Circuit','China',        'Shanghai',      31.3389,  121.2197,  'Asia/Shanghai',         'PERMANENT'),
    'suzuka':       ('Suzuka International Racing Course','Japan',    'Suzuka',        34.8431,  136.5407,  'Asia/Tokyo',            'PERMANENT'),
    'bahrain':      ('Bahrain International Circuit', 'Bahrain',      'Sakhir',        26.0325,   50.5106,  'Asia/Bahrain',          'PERMANENT'),
    'jeddah':       ('Jeddah Corniche Circuit',       'Saudi Arabia', 'Jeddah',        21.6319,   39.1044,  'Asia/Riyadh',           'STREET'),
    'miami':        ('Miami International Autodrome', 'USA',          'Miami',         25.9581,  -80.2389,  'America/New_York',      'PERMANENT'),
    'imola':        ('Autodromo Enzo e Dino Ferrari', 'Italy',        'Imola',         44.3439,   11.7167,  'Europe/Rome',           'PERMANENT'),
    'monaco':       ('Circuit de Monaco',             'Monaco',       'Monte Carlo',   43.7347,    7.4205,  'Europe/Monaco',         'STREET'),
    'catalunya':    ('Circuit de Barcelona-Catalunya', 'Spain',       'Barcelona',     41.5700,    2.2611,  'Europe/Madrid',         'PERMANENT'),
    'villeneuve':   ('Circuit Gilles Villeneuve',     'Canada',       'Montreal',      45.5000,  -73.5228,  'America/Toronto',       'STREET'),
    'red_bull_ring':('Red Bull Ring',                 'Austria',      'Spielberg',     47.2197,   14.7647,  'Europe/Vienna',         'PERMANENT'),
    'silverstone':  ('Silverstone Circuit',           'Great Britain','Silverstone',   52.0786,   -1.0169,  'Europe/London',         'PERMANENT'),
    'spa':          ('Circuit de Spa-Francorchamps',  'Belgium',      'Stavelot',      50.4372,    5.9714,  'Europe/Brussels',       'PERMANENT'),
    'hungaroring':  ('Hungaroring',                   'Hungary',      'Budapest',      47.5830,   19.2511,  'Europe/Budapest',       'PERMANENT'),
    'zandvoort':    ('Circuit Zandvoort',             'Netherlands',  'Zandvoort',     52.3888,    4.5409,  'Europe/Amsterdam',      'PERMANENT'),
    'monza':        ('Autodromo Nazionale di Monza',  'Italy',        'Monza',         45.6156,    9.2811,  'Europe/Rome',           'PERMANENT'),
    'baku':         ('Baku City Circuit',             'Azerbaijan',   'Baku',          40.3725,   49.8533,  'Asia/Baku',             'STREET'),
    'marina_bay':   ('Marina Bay Street Circuit',     'Singapore',    'Singapore',      1.2914,  103.8640,  'Asia/Singapore',        'STREET'),
    'americas':     ('Circuit of The Americas',       'USA',          'Austin',        30.1328, -97.6411,  'America/Chicago',       'PERMANENT'),
    'rodriguez':    ('Autodromo Hermanos Rodriguez',  'Mexico',       'Mexico City',   19.4042,  -99.0907,  'America/Mexico_City',   'PERMANENT'),
    'interlagos':   ('Autodromo Jose Carlos Pace',    'Brazil',       'São Paulo',    -23.7036,  -46.6997,  'America/Sao_Paulo',     'PERMANENT'),
    'vegas':        ('Las Vegas Strip Circuit',       'USA',          'Las Vegas',     36.1147, -115.1728,  'America/Los_Angeles',   'STREET'),
    'losail':       ('Lusail International Circuit',  'Qatar',        'Lusail',        25.4900,   51.4542,  'Asia/Qatar',            'PERMANENT'),
    'yas_marina':   ('Yas Marina Circuit',            'UAE',          'Abu Dhabi',     24.4672,   54.6031,  'Asia/Dubai',            'PERMANENT'),
}

# Session schedule offsets from race_date (Sunday = 0)
# (session_type, session_name, day_offset, hour_utc, minute_utc)
STANDARD_SESSIONS = [
    ('FP1',        'Practice 1',    -2, 11, 30),
    ('FP2',        'Practice 2',    -2, 15,  0),
    ('FP3',        'Practice 3',    -1, 11, 30),
    ('QUALIFYING', 'Qualifying',    -1, 15,  0),
    ('RACE',       'Race',           0, 13,  0),
]

SPRINT_SESSIONS = [
    ('FP1',               'Practice 1',        -2, 11, 30),
    ('SPRINT_QUALIFYING', 'Sprint Qualifying',  -2, 15,  0),
    ('SPRINT',            'Sprint',             -1, 11,  0),
    ('QUALIFYING',        'Qualifying',         -1, 15,  0),
    ('RACE',              'Race',                0, 13,  0),
]


class Command(BaseCommand):
    help = 'Seed the official F1 2026 Season Schedule (24 rounds, full sessions, circuit data).'

    def handle(self, *args, **options):
        # 1. Create Season 2026
        season, _ = Season.objects.get_or_create(
            year=2026,
            defaults={
                'name': 'FIA Formula One World Championship 2026',
                'total_races': 24,
            }
        )
        if not _:
            season.total_races = 24
            season.save(update_fields=['total_races'])
        self.stdout.write(self.style.SUCCESS(f'Season 2026: {season.name}'))

        # 2. Define Official 2026 Schedule (24 rounds)
        schedule = [
            (1,  "Australian Grand Prix",      "albert_park",   date(2026, 3, 15)),
            (2,  "Chinese Grand Prix",          "shanghai",      date(2026, 3, 22)),
            (3,  "Japanese Grand Prix",         "suzuka",        date(2026, 4,  5)),
            (4,  "Bahrain Grand Prix",          "bahrain",       date(2026, 4, 19)),
            (5,  "Saudi Arabian Grand Prix",    "jeddah",        date(2026, 4, 26)),
            (6,  "Miami Grand Prix",            "miami",         date(2026, 5, 10)),
            (7,  "Emilia Romagna Grand Prix",   "imola",         date(2026, 5, 24)),
            (8,  "Monaco Grand Prix",           "monaco",        date(2026, 5, 31)),
            (9,  "Spanish Grand Prix",          "catalunya",     date(2026, 6, 14)),
            (10, "Canadian Grand Prix",         "villeneuve",    date(2026, 6, 28)),
            (11, "Austrian Grand Prix",         "red_bull_ring", date(2026, 7,  5)),
            (12, "British Grand Prix",          "silverstone",   date(2026, 7, 12)),
            (13, "Belgian Grand Prix",          "spa",           date(2026, 7, 26)),
            (14, "Hungarian Grand Prix",        "hungaroring",   date(2026, 8,  2)),
            (15, "Dutch Grand Prix",            "zandvoort",     date(2026, 8, 30)),
            (16, "Italian Grand Prix",          "monza",         date(2026, 9,  6)),
            (17, "Azerbaijan Grand Prix",       "baku",          date(2026, 9, 20)),
            (18, "Singapore Grand Prix",        "marina_bay",    date(2026, 10,  4)),
            (19, "United States Grand Prix",    "americas",      date(2026, 10, 25)),
            (20, "Mexico City Grand Prix",      "rodriguez",     date(2026, 11,  1)),
            (21, "Sao Paulo Grand Prix",        "interlagos",    date(2026, 11,  8)),
            (22, "Las Vegas Grand Prix",        "vegas",         date(2026, 11, 22)),
            (23, "Qatar Grand Prix",            "losail",        date(2026, 11, 29)),
            (24, "Abu Dhabi Grand Prix",        "yas_marina",    date(2026, 12,  6)),
        ]

        for round_num, name, circuit_code, race_date in schedule:
            is_sprint = circuit_code in SPRINT_WEEKENDS

            # Upsert circuit with full data
            circuit_data = CIRCUITS_2026.get(circuit_code)
            if circuit_data:
                cname, country, city, lat, lng, tz, ctype = circuit_data
                circuit, _ = Circuit.objects.update_or_create(
                    code=circuit_code,
                    defaults={
                        'name': cname,
                        'country': country,
                        'city': city,
                        'latitude': lat,
                        'longitude': lng,
                        'timezone': tz,
                        'circuit_type': ctype,
                    }
                )
            else:
                circuit, _ = Circuit.objects.get_or_create(
                    code=circuit_code,
                    defaults={'name': name.replace(" Grand Prix", " Circuit"), 'country': 'Unknown'}
                )

            # Upsert Race
            race, created = Race.objects.update_or_create(
                season=season,
                round_number=round_num,
                defaults={
                    'official_name': name,
                    'circuit': circuit,
                    'race_date': race_date,
                    'status': 'SCHEDULED',
                    'is_sprint_weekend': is_sprint,
                }
            )

            # Create sessions (skip if already exist)
            session_template = SPRINT_SESSIONS if is_sprint else STANDARD_SESSIONS
            utc = pytz.UTC
            for stype, sname, day_offset, hour, minute in session_template:
                session_date = race_date + timedelta(days=day_offset)
                start_dt = datetime(session_date.year, session_date.month, session_date.day,
                                    hour, minute, 0, tzinfo=utc)
                Session.objects.get_or_create(
                    race=race,
                    session_type=stype,
                    defaults={
                        'session_name': sname,
                        'scheduled_start': start_dt,
                        'status': 'SCHEDULED',
                    }
                )

            action = 'Created' if created else 'Updated'
            sprint_tag = ' [SPRINT]' if is_sprint else ''
            self.stdout.write(f"{action} R{round_num:02d}: {name}{sprint_tag}")

        self.stdout.write(self.style.SUCCESS('Successfully seeded 2026 Schedule (24 rounds).'))

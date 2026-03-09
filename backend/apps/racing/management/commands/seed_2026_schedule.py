"""Seed the official F1 2026 Season Schedule.

Source: Jolpica API (https://api.jolpi.ca/ergast/f1/2026/races/)
Fetched: 2026-03-10

24 rounds, 6 sprint weekends:
  R02 Shanghai, R06 Miami, R07 Canada, R11 British, R14 Dutch, R18 Singapore
"""
from django.core.management.base import BaseCommand
from apps.championships.models import Season
from apps.racing.models import Race, Session
from apps.circuits.models import Circuit
from datetime import datetime
import pytz


# Circuit metadata: circuitId -> (name, country, city, lat, lng, timezone, circuit_type)
CIRCUITS = {
    'albert_park': ('Albert Park Grand Prix Circuit', 'Australia',    'Melbourne',  -37.8497,  144.9680, 'Australia/Melbourne',  'STREET'),
    'shanghai':    ('Shanghai International Circuit',  'China',        'Shanghai',    31.3389,  121.2200, 'Asia/Shanghai',        'PERMANENT'),
    'suzuka':      ('Suzuka Circuit',                  'Japan',        'Suzuka',      34.8431,  136.5410, 'Asia/Tokyo',           'PERMANENT'),
    'bahrain':     ('Bahrain International Circuit',   'Bahrain',      'Sakhir',      26.0325,   50.5106, 'Asia/Bahrain',         'PERMANENT'),
    'jeddah':      ('Jeddah Corniche Circuit',         'Saudi Arabia', 'Jeddah',      21.6319,   39.1044, 'Asia/Riyadh',          'STREET'),
    'miami':       ('Miami International Autodrome',   'USA',          'Miami',       25.9581,  -80.2389, 'America/New_York',     'PERMANENT'),
    'villeneuve':  ('Circuit Gilles Villeneuve',       'Canada',       'Montreal',    45.5000,  -73.5228, 'America/Toronto',      'STREET'),
    'monaco':      ('Circuit de Monaco',               'Monaco',       'Monte Carlo', 43.7347,    7.4206, 'Europe/Monaco',        'STREET'),
    'catalunya':   ('Circuit de Barcelona-Catalunya',  'Spain',        'Barcelona',   41.5700,    2.2611, 'Europe/Madrid',        'PERMANENT'),
    'red_bull_ring':('Red Bull Ring',                  'Austria',      'Spielberg',   47.2197,   14.7647, 'Europe/Vienna',        'PERMANENT'),
    'silverstone': ('Silverstone Circuit',             'UK',           'Silverstone', 52.0786,   -1.0169, 'Europe/London',        'PERMANENT'),
    'spa':         ('Circuit de Spa-Francorchamps',    'Belgium',      'Spa',         50.4372,    5.9714, 'Europe/Brussels',      'PERMANENT'),
    'hungaroring': ('Hungaroring',                     'Hungary',      'Budapest',    47.5789,   19.2486, 'Europe/Budapest',      'PERMANENT'),
    'zandvoort':   ('Circuit Park Zandvoort',          'Netherlands',  'Zandvoort',   52.3888,    4.5409, 'Europe/Amsterdam',     'PERMANENT'),
    'monza':       ('Autodromo Nazionale di Monza',    'Italy',        'Monza',       45.6156,    9.2811, 'Europe/Rome',          'PERMANENT'),
    'madring':     ('Madring',                         'Spain',        'Madrid',      40.4653,   -3.6153, 'Europe/Madrid',        'PERMANENT'),
    'baku':        ('Baku City Circuit',               'Azerbaijan',   'Baku',        40.3725,   49.8533, 'Asia/Baku',            'STREET'),
    'marina_bay':  ('Marina Bay Street Circuit',       'Singapore',    'Marina Bay',   1.2914,  103.8640, 'Asia/Singapore',       'STREET'),
    'americas':    ('Circuit of the Americas',         'USA',          'Austin',      30.1328,  -97.6411, 'America/Chicago',      'PERMANENT'),
    'rodriguez':   ('Autódromo Hermanos Rodríguez',    'Mexico',       'Mexico City', 19.4042,  -99.0907, 'America/Mexico_City',  'PERMANENT'),
    'interlagos':  ('Autódromo José Carlos Pace',      'Brazil',       'São Paulo',  -23.7036,  -46.6997, 'America/Sao_Paulo',    'PERMANENT'),
    'vegas':       ('Las Vegas Strip Street Circuit',  'USA',          'Las Vegas',   36.1147, -115.1730, 'America/Los_Angeles',  'STREET'),
    'losail':      ('Losail International Circuit',    'Qatar',        'Lusail',      25.4900,   51.4542, 'Asia/Qatar',           'PERMANENT'),
    'yas_marina':  ('Yas Marina Circuit',              'UAE',          'Abu Dhabi',   24.4672,   54.6031, 'Asia/Dubai',           'PERMANENT'),
}

# Official 2026 schedule — sourced from Jolpica API 2026-03-10
# fmt: (round, race_name, circuit_id, race_date_utc, sessions)
# sessions: list of (session_type, session_name, datetime_utc_str)
SCHEDULE_2026 = [
    (1, 'Australian Grand Prix', 'albert_park', '2026-03-08T04:00:00Z', [
        ('FP1',        'Practice 1',       '2026-03-06T01:30:00Z'),
        ('FP2',        'Practice 2',       '2026-03-06T05:00:00Z'),
        ('FP3',        'Practice 3',       '2026-03-07T01:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-03-07T05:00:00Z'),
        ('RACE',       'Race',             '2026-03-08T04:00:00Z'),
    ]),
    (2, 'Chinese Grand Prix', 'shanghai', '2026-03-15T07:00:00Z', [
        ('FP1',               'Practice 1',        '2026-03-13T03:30:00Z'),
        ('SPRINT_QUALIFYING', 'Sprint Qualifying',  '2026-03-13T07:30:00Z'),
        ('SPRINT',            'Sprint',             '2026-03-14T03:00:00Z'),
        ('QUALIFYING',        'Qualifying',         '2026-03-14T07:00:00Z'),
        ('RACE',              'Race',               '2026-03-15T07:00:00Z'),
    ]),
    (3, 'Japanese Grand Prix', 'suzuka', '2026-03-29T05:00:00Z', [
        ('FP1',        'Practice 1',       '2026-03-27T02:30:00Z'),
        ('FP2',        'Practice 2',       '2026-03-27T06:00:00Z'),
        ('FP3',        'Practice 3',       '2026-03-28T02:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-03-28T06:00:00Z'),
        ('RACE',       'Race',             '2026-03-29T05:00:00Z'),
    ]),
    (4, 'Bahrain Grand Prix', 'bahrain', '2026-04-12T15:00:00Z', [
        ('FP1',        'Practice 1',       '2026-04-10T11:30:00Z'),
        ('FP2',        'Practice 2',       '2026-04-10T15:00:00Z'),
        ('FP3',        'Practice 3',       '2026-04-11T12:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-04-11T16:00:00Z'),
        ('RACE',       'Race',             '2026-04-12T15:00:00Z'),
    ]),
    (5, 'Saudi Arabian Grand Prix', 'jeddah', '2026-04-19T17:00:00Z', [
        ('FP1',        'Practice 1',       '2026-04-17T13:30:00Z'),
        ('FP2',        'Practice 2',       '2026-04-17T17:00:00Z'),
        ('FP3',        'Practice 3',       '2026-04-18T13:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-04-18T17:00:00Z'),
        ('RACE',       'Race',             '2026-04-19T17:00:00Z'),
    ]),
    (6, 'Miami Grand Prix', 'miami', '2026-05-03T20:00:00Z', [
        ('FP1',               'Practice 1',        '2026-05-01T16:30:00Z'),
        ('SPRINT_QUALIFYING', 'Sprint Qualifying',  '2026-05-01T20:30:00Z'),
        ('SPRINT',            'Sprint',             '2026-05-02T16:00:00Z'),
        ('QUALIFYING',        'Qualifying',         '2026-05-02T20:00:00Z'),
        ('RACE',              'Race',               '2026-05-03T20:00:00Z'),
    ]),
    (7, 'Canadian Grand Prix', 'villeneuve', '2026-05-24T20:00:00Z', [
        ('FP1',               'Practice 1',        '2026-05-22T16:30:00Z'),
        ('SPRINT_QUALIFYING', 'Sprint Qualifying',  '2026-05-22T20:30:00Z'),
        ('SPRINT',            'Sprint',             '2026-05-23T16:00:00Z'),
        ('QUALIFYING',        'Qualifying',         '2026-05-23T20:00:00Z'),
        ('RACE',              'Race',               '2026-05-24T20:00:00Z'),
    ]),
    (8, 'Monaco Grand Prix', 'monaco', '2026-06-07T13:00:00Z', [
        ('FP1',        'Practice 1',       '2026-06-05T11:30:00Z'),
        ('FP2',        'Practice 2',       '2026-06-05T15:00:00Z'),
        ('FP3',        'Practice 3',       '2026-06-06T10:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-06-06T14:00:00Z'),
        ('RACE',       'Race',             '2026-06-07T13:00:00Z'),
    ]),
    (9, 'Barcelona Grand Prix', 'catalunya', '2026-06-14T13:00:00Z', [
        ('FP1',        'Practice 1',       '2026-06-12T11:30:00Z'),
        ('FP2',        'Practice 2',       '2026-06-12T15:00:00Z'),
        ('FP3',        'Practice 3',       '2026-06-13T10:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-06-13T14:00:00Z'),
        ('RACE',       'Race',             '2026-06-14T13:00:00Z'),
    ]),
    (10, 'Austrian Grand Prix', 'red_bull_ring', '2026-06-28T13:00:00Z', [
        ('FP1',        'Practice 1',       '2026-06-26T11:30:00Z'),
        ('FP2',        'Practice 2',       '2026-06-26T15:00:00Z'),
        ('FP3',        'Practice 3',       '2026-06-27T10:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-06-27T14:00:00Z'),
        ('RACE',       'Race',             '2026-06-28T13:00:00Z'),
    ]),
    (11, 'British Grand Prix', 'silverstone', '2026-07-05T14:00:00Z', [
        ('FP1',               'Practice 1',        '2026-07-03T11:30:00Z'),
        ('SPRINT_QUALIFYING', 'Sprint Qualifying',  '2026-07-03T15:30:00Z'),
        ('SPRINT',            'Sprint',             '2026-07-04T11:00:00Z'),
        ('QUALIFYING',        'Qualifying',         '2026-07-04T15:00:00Z'),
        ('RACE',              'Race',               '2026-07-05T14:00:00Z'),
    ]),
    (12, 'Belgian Grand Prix', 'spa', '2026-07-19T13:00:00Z', [
        ('FP1',        'Practice 1',       '2026-07-17T11:30:00Z'),
        ('FP2',        'Practice 2',       '2026-07-17T15:00:00Z'),
        ('FP3',        'Practice 3',       '2026-07-18T10:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-07-18T14:00:00Z'),
        ('RACE',       'Race',             '2026-07-19T13:00:00Z'),
    ]),
    (13, 'Hungarian Grand Prix', 'hungaroring', '2026-07-26T13:00:00Z', [
        ('FP1',        'Practice 1',       '2026-07-24T11:30:00Z'),
        ('FP2',        'Practice 2',       '2026-07-24T15:00:00Z'),
        ('FP3',        'Practice 3',       '2026-07-25T10:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-07-25T14:00:00Z'),
        ('RACE',       'Race',             '2026-07-26T13:00:00Z'),
    ]),
    (14, 'Dutch Grand Prix', 'zandvoort', '2026-08-23T13:00:00Z', [
        ('FP1',               'Practice 1',        '2026-08-21T10:30:00Z'),
        ('SPRINT_QUALIFYING', 'Sprint Qualifying',  '2026-08-21T14:30:00Z'),
        ('SPRINT',            'Sprint',             '2026-08-22T10:00:00Z'),
        ('QUALIFYING',        'Qualifying',         '2026-08-22T14:00:00Z'),
        ('RACE',              'Race',               '2026-08-23T13:00:00Z'),
    ]),
    (15, 'Italian Grand Prix', 'monza', '2026-09-06T13:00:00Z', [
        ('FP1',        'Practice 1',       '2026-09-04T10:30:00Z'),
        ('FP2',        'Practice 2',       '2026-09-04T14:00:00Z'),
        ('FP3',        'Practice 3',       '2026-09-05T10:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-09-05T14:00:00Z'),
        ('RACE',       'Race',             '2026-09-06T13:00:00Z'),
    ]),
    (16, 'Spanish Grand Prix', 'madring', '2026-09-13T13:00:00Z', [
        ('FP1',        'Practice 1',       '2026-09-11T11:30:00Z'),
        ('FP2',        'Practice 2',       '2026-09-11T15:00:00Z'),
        ('FP3',        'Practice 3',       '2026-09-12T10:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-09-12T14:00:00Z'),
        ('RACE',       'Race',             '2026-09-13T13:00:00Z'),
    ]),
    (17, 'Azerbaijan Grand Prix', 'baku', '2026-09-26T11:00:00Z', [
        ('FP1',        'Practice 1',       '2026-09-24T08:30:00Z'),
        ('FP2',        'Practice 2',       '2026-09-24T12:00:00Z'),
        ('FP3',        'Practice 3',       '2026-09-25T08:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-09-25T12:00:00Z'),
        ('RACE',       'Race',             '2026-09-26T11:00:00Z'),
    ]),
    (18, 'Singapore Grand Prix', 'marina_bay', '2026-10-11T12:00:00Z', [
        ('FP1',               'Practice 1',        '2026-10-09T08:30:00Z'),
        ('SPRINT_QUALIFYING', 'Sprint Qualifying',  '2026-10-09T12:30:00Z'),
        ('SPRINT',            'Sprint',             '2026-10-10T09:00:00Z'),
        ('QUALIFYING',        'Qualifying',         '2026-10-10T13:00:00Z'),
        ('RACE',              'Race',               '2026-10-11T12:00:00Z'),
    ]),
    (19, 'United States Grand Prix', 'americas', '2026-10-25T20:00:00Z', [
        ('FP1',        'Practice 1',       '2026-10-23T17:30:00Z'),
        ('FP2',        'Practice 2',       '2026-10-23T21:00:00Z'),
        ('FP3',        'Practice 3',       '2026-10-24T17:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-10-24T21:00:00Z'),
        ('RACE',       'Race',             '2026-10-25T20:00:00Z'),
    ]),
    (20, 'Mexico City Grand Prix', 'rodriguez', '2026-11-01T20:00:00Z', [
        ('FP1',        'Practice 1',       '2026-10-30T18:30:00Z'),
        ('FP2',        'Practice 2',       '2026-10-30T22:00:00Z'),
        ('FP3',        'Practice 3',       '2026-10-31T17:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-10-31T21:00:00Z'),
        ('RACE',       'Race',             '2026-11-01T20:00:00Z'),
    ]),
    (21, 'Brazilian Grand Prix', 'interlagos', '2026-11-08T17:00:00Z', [
        ('FP1',        'Practice 1',       '2026-11-06T15:30:00Z'),
        ('FP2',        'Practice 2',       '2026-11-06T19:00:00Z'),
        ('FP3',        'Practice 3',       '2026-11-07T14:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-11-07T18:00:00Z'),
        ('RACE',       'Race',             '2026-11-08T17:00:00Z'),
    ]),
    (22, 'Las Vegas Grand Prix', 'vegas', '2026-11-22T04:00:00Z', [
        ('FP1',        'Practice 1',       '2026-11-20T00:30:00Z'),
        ('FP2',        'Practice 2',       '2026-11-20T04:00:00Z'),
        ('FP3',        'Practice 3',       '2026-11-21T00:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-11-21T04:00:00Z'),
        ('RACE',       'Race',             '2026-11-22T04:00:00Z'),
    ]),
    (23, 'Qatar Grand Prix', 'losail', '2026-11-29T16:00:00Z', [
        ('FP1',        'Practice 1',       '2026-11-27T13:30:00Z'),
        ('FP2',        'Practice 2',       '2026-11-27T17:00:00Z'),
        ('FP3',        'Practice 3',       '2026-11-28T14:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-11-28T18:00:00Z'),
        ('RACE',       'Race',             '2026-11-29T16:00:00Z'),
    ]),
    (24, 'Abu Dhabi Grand Prix', 'yas_marina', '2026-12-06T13:00:00Z', [
        ('FP1',        'Practice 1',       '2026-12-04T09:30:00Z'),
        ('FP2',        'Practice 2',       '2026-12-04T13:00:00Z'),
        ('FP3',        'Practice 3',       '2026-12-05T10:30:00Z'),
        ('QUALIFYING', 'Qualifying',       '2026-12-05T14:00:00Z'),
        ('RACE',       'Race',             '2026-12-06T13:00:00Z'),
    ]),
]

SPRINT_CIRCUITS = {'shanghai', 'miami', 'villeneuve', 'silverstone', 'zandvoort', 'marina_bay'}

SESSION_NAME_MAP = {
    'FP1': 'Practice 1', 'FP2': 'Practice 2', 'FP3': 'Practice 3',
    'QUALIFYING': 'Qualifying', 'SPRINT_QUALIFYING': 'Sprint Qualifying',
    'SPRINT': 'Sprint', 'RACE': 'Race',
}


def _parse_utc(dt_str):
    return datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.UTC)


class Command(BaseCommand):
    help = 'Seed the official F1 2026 Season Schedule (24 rounds, sourced from Jolpica 2026-03-10).'

    def handle(self, *args, **options):
        utc = pytz.UTC

        # 1. Season
        season, _ = Season.objects.get_or_create(
            year=2026,
            defaults={'name': 'FIA Formula One World Championship 2026', 'total_races': 24},
        )
        season.total_races = 24
        season.save(update_fields=['total_races'])
        self.stdout.write(self.style.SUCCESS(f'Season: {season.name}'))

        # 2. Clear stale 2026 Race + Session data to avoid round-number conflicts
        old_races = Race.objects.filter(season=season)
        if old_races.exists():
            Session.objects.filter(race__in=old_races).delete()
            old_races.delete()
            self.stdout.write('Cleared stale 2026 Race + Session rows.')

        # 3. Seed circuits
        for cid, (cname, country, city, lat, lng, tz, ctype) in CIRCUITS.items():
            Circuit.objects.update_or_create(
                code=cid,
                defaults={
                    'name': cname, 'country': country, 'city': city,
                    'latitude': lat, 'longitude': lng,
                    'timezone': tz, 'circuit_type': ctype,
                },
            )

        # 4. Seed races + sessions
        for round_num, race_name, circuit_id, race_dt_str, sessions in SCHEDULE_2026:
            is_sprint = circuit_id in SPRINT_CIRCUITS
            race_date = _parse_utc(race_dt_str).date()

            # Determine status: R01 Australia has already been completed
            status = 'COMPLETED' if round_num == 1 else 'SCHEDULED'

            circuit = Circuit.objects.get(code=circuit_id)
            race = Race.objects.create(
                season=season,
                round_number=round_num,
                official_name=race_name,
                circuit=circuit,
                race_date=race_date,
                status=status,
                is_sprint_weekend=is_sprint,
            )

            for stype, sname, sdt_str in sessions:
                Session.objects.create(
                    race=race,
                    session_type=stype,
                    session_name=sname,
                    scheduled_start=_parse_utc(sdt_str),
                    status='COMPLETED' if (round_num == 1) else 'SCHEDULED',
                )

            sprint_tag = ' [SPRINT]' if is_sprint else ''
            status_tag = ' ✓ COMPLETED' if status == 'COMPLETED' else ''
            self.stdout.write(f'R{round_num:02d} {race_date} {race_name}{sprint_tag}{status_tag}')

        self.stdout.write(self.style.SUCCESS(
            'Done. 24 rounds seeded. Sprint weekends: Shanghai, Miami, Canada, British, Dutch, Singapore.'
        ))

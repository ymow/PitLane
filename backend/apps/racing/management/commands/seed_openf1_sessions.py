"""Management command: seed OpenF1 session keys into Session.openf1_session_key.

Usage:
    python manage.py seed_openf1_sessions [--year 2026] [--dry-run]

Fetches session list from OpenF1 API and matches each entry to a Session
record by meeting name + session type, then stores the session_key.
"""
import requests
import logging
from django.core.management.base import BaseCommand
from apps.racing.models import Session

logger = logging.getLogger(__name__)

OPENF1_BASE = "https://api.openf1.org/v1"

# OpenF1 session_type string → our Session.session_type choice
OPENF1_TYPE_MAP = {
    'Practice 1': 'FP1',
    'Practice 2': 'FP2',
    'Practice 3': 'FP3',
    'Qualifying': 'QUALIFYING',
    'Sprint Qualifying': 'SPRINT_QUALIFYING',
    'Sprint': 'SPRINT',
    'Race': 'RACE',
}


class Command(BaseCommand):
    help = 'Seed OpenF1 session_key values into Session records for a given year.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year', type=int, default=2026,
            help='Season year to seed (default: 2026)',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Preview matches without writing to DB',
        )

    def handle(self, *args, **options):
        year = options['year']
        dry_run = options['dry_run']

        self.stdout.write(f"Fetching OpenF1 sessions for year={year}...")

        try:
            resp = requests.get(
                f"{OPENF1_BASE}/sessions",
                params={'year': year},
                timeout=15,
            )
            resp.raise_for_status()
            openf1_sessions = resp.json()
        except requests.RequestException as e:
            self.stderr.write(self.style.ERROR(f"OpenF1 API error: {e}"))
            return

        if not openf1_sessions:
            self.stdout.write(self.style.WARNING(
                f"OpenF1 returned 0 sessions for year={year}. "
                "Season data may not be available yet."
            ))
            return

        self.stdout.write(f"  Got {len(openf1_sessions)} sessions from OpenF1.")

        # Pre-load all our sessions for this year to avoid N+1 queries
        our_sessions = list(
            Session.objects.filter(race__season__year=year)
            .select_related('race')
        )

        matched = 0
        skipped = 0
        not_found = 0

        for item in openf1_sessions:
            session_key = item.get('session_key')
            session_type_raw = item.get('session_type') or ''
            meeting_name = (item.get('meeting_name') or '').strip()

            our_type = OPENF1_TYPE_MAP.get(session_type_raw)
            if not our_type:
                self.stdout.write(
                    f"  [SKIP] Unknown session_type '{session_type_raw}' "
                    f"(meeting='{meeting_name}', key={session_key})"
                )
                skipped += 1
                continue

            # Match by meeting name substring + session_type
            session_obj = _find_session(our_sessions, meeting_name, our_type)

            if not session_obj:
                self.stdout.write(
                    f"  [NOT FOUND] '{meeting_name}' {our_type} (key={session_key})"
                )
                not_found += 1
                continue

            if not dry_run:
                session_obj.openf1_session_key = session_key
                session_obj.save(update_fields=['openf1_session_key'])

            action = '[DRY-RUN]' if dry_run else '[UPDATED]'
            self.stdout.write(
                f"  {action} {session_obj.race.official_name} {our_type} "
                f"→ openf1_session_key={session_key}"
            )
            matched += 1

        summary = f"Done. matched={matched}, not_found={not_found}, skipped={skipped}"
        self.stdout.write(
            self.style.SUCCESS(summary) if not_found == 0 else self.style.WARNING(summary)
        )


def _find_session(
    our_sessions: list,
    meeting_name: str,
    our_type: str,
) -> 'Session | None':
    """Find the best-matching Session by meeting name and session type."""
    meeting_lower = meeting_name.lower()
    for s in our_sessions:
        if s.session_type != our_type:
            continue
        official_lower = s.race.official_name.lower()
        if meeting_lower in official_lower or official_lower in meeting_lower:
            return s
    return None

"""Seed DriverContract entries for paddock staff (non-driver roles)."""
import json
from datetime import date
from django.core.management.base import BaseCommand, CommandError
from apps.teams.models import Team, DriverContract


class Command(BaseCommand):
    help = 'Seed DriverContract staff entries from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('--file', required=True, help='Path to JSON seed file')
        parser.add_argument('--season', required=True, type=int, help='Season year (e.g. 2026)')
        parser.add_argument('--dry-run', action='store_true', help='Preview without saving')

    def handle(self, *args, **options):
        path     = options['file']
        year     = options['season']
        dry_run  = options['dry_run']

        # Resolve Season (get or create to allow seeding before official season object exists)
        from apps.championships.models import Season
        season, _ = Season.objects.get_or_create(year=year, defaults={'is_current': False})

        try:
            with open(path) as fh:
                entries = json.load(fh)
        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON: {exc}")

        DRIVER_ROLES = {'RACE', 'RESERVE', 'TEST', 'DEVELOPMENT', 'LOAN', 'GUEST'}
        created = updated = skipped = 0

        for entry in entries:
            team_code   = entry.get('team_code')
            person_name = entry.get('person_name', '').strip()
            role        = entry.get('role')

            if not all([team_code, person_name, role]):
                self.stderr.write(f"Skipping incomplete entry: {entry}")
                skipped += 1
                continue

            if role in DRIVER_ROLES:
                self.stderr.write(f"Skipping driver role '{role}' for {person_name} — use seed_social_handles for drivers")
                skipped += 1
                continue

            try:
                team = Team.objects.get(code=team_code)
            except Team.DoesNotExist:
                self.stderr.write(f"Team not found: {team_code} — skipping {person_name}")
                skipped += 1
                continue

            valid_from = entry.get('valid_from')
            if valid_from:
                from datetime import datetime
                valid_from = datetime.strptime(valid_from, '%Y-%m-%d').date()
            else:
                valid_from = date(year, 1, 1)

            defaults = {
                'is_active':   entry.get('is_active', True),
                'valid_from':  valid_from,
                'valid_until': None,
                'notes':       entry.get('notes'),
            }

            if dry_run:
                self.stdout.write(f"[DRY-RUN] Would upsert: {person_name} | {role} | {team_code}")
                created += 1
                continue

            obj, was_created = DriverContract.objects.get_or_create(
                team=team,
                season=season,
                role=role,
                person_name=person_name,
                driver=None,
                defaults=defaults,
            )
            if not was_created:
                for field, value in defaults.items():
                    setattr(obj, field, value)
                obj.save()
                updated += 1
            else:
                created += 1

        label = 'Dry-run complete' if dry_run else 'Done'
        self.stdout.write(self.style.SUCCESS(
            f"{label} — created: {created}, updated: {updated}, skipped: {skipped}"
        ))

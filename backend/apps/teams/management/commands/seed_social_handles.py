"""Bulk seed social handles from a JSON file."""
import json
from django.core.management.base import BaseCommand, CommandError
from apps.teams.models import Driver, Team, SocialHandle


class Command(BaseCommand):
    help = 'Bulk import paddock social handles from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('--file', required=True, help='Path to JSON seed file')
        parser.add_argument('--dry-run', action='store_true', help='Preview changes without saving')

    def handle(self, *args, **options):
        path = options['file']
        dry_run = options['dry_run']

        try:
            with open(path) as fh:
                entries = json.load(fh)
        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON: {exc}")

        created = updated = skipped = 0

        for entry in entries:
            platform = entry.get('platform')
            handle   = entry.get('handle')

            if not platform or not handle:
                self.stderr.write(f"Skipping entry missing platform/handle: {entry}")
                skipped += 1
                continue

            # Resolve FKs
            driver = None
            if entry.get('driver_code'):
                try:
                    driver = Driver.objects.get(code=entry['driver_code'])
                except Driver.DoesNotExist:
                    self.stderr.write(f"Driver not found: {entry['driver_code']} — skipping")
                    skipped += 1
                    continue

            team = None
            if entry.get('team_code'):
                try:
                    team = Team.objects.get(code=entry['team_code'])
                except Team.DoesNotExist:
                    self.stderr.write(f"Team not found: {entry['team_code']} — skipping")
                    skipped += 1
                    continue

            defaults = {
                'url':          entry.get('url', ''),
                'entity_type':  entry.get('entity_type', 'DRIVER'),
                'driver':       driver,
                'team':         team,
                'staff_name':   entry.get('staff_name'),
                'role':         entry.get('role'),
                'is_verified':  entry.get('is_verified', False),
                'is_active':    entry.get('is_active', True),
                'follower_count': entry.get('follower_count'),
            }

            if dry_run:
                self.stdout.write(f"[DRY-RUN] Would upsert {platform} {handle}")
                created += 1
                continue

            _, was_created = SocialHandle.objects.update_or_create(
                platform=platform,
                handle=handle,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"Dry-run complete — {created} would be created/updated, {skipped} skipped"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Done — created: {created}, updated: {updated}, skipped: {skipped}"
            ))

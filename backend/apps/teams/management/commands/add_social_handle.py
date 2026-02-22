"""Add a single social handle via the CLI."""
from django.core.management.base import BaseCommand, CommandError
from apps.teams.models import Driver, Team, SocialHandle, Platform, SocialEntityType


class Command(BaseCommand):
    help = 'Add or update a single paddock social handle'

    def add_arguments(self, parser):
        parser.add_argument('--platform', required=True,
                            choices=[c.value for c in Platform],
                            help='Platform (TWITTER, INSTAGRAM, …)')
        parser.add_argument('--handle', required=True, help='Handle, e.g. @LewisHamilton')
        parser.add_argument('--url', required=True, help='Profile URL')
        parser.add_argument('--entity-type', required=True,
                            choices=[c.value for c in SocialEntityType],
                            dest='entity_type')
        parser.add_argument('--driver', dest='driver_code', help='Driver code, e.g. HAM')
        parser.add_argument('--team', dest='team_code', help='Team code, e.g. FER')
        parser.add_argument('--staff-name', dest='staff_name')
        parser.add_argument('--role')
        parser.add_argument('--verified', action='store_true', dest='is_verified')
        parser.add_argument('--follower-count', type=int, dest='follower_count')

    def handle(self, *args, **options):
        driver = None
        if options['driver_code']:
            try:
                driver = Driver.objects.get(code=options['driver_code'])
            except Driver.DoesNotExist:
                raise CommandError(f"Driver not found: {options['driver_code']}")

        team = None
        if options['team_code']:
            try:
                team = Team.objects.get(code=options['team_code'])
            except Team.DoesNotExist:
                raise CommandError(f"Team not found: {options['team_code']}")

        obj, created = SocialHandle.objects.update_or_create(
            platform=options['platform'],
            handle=options['handle'],
            defaults={
                'url':            options['url'],
                'entity_type':    options['entity_type'],
                'driver':         driver,
                'team':           team,
                'staff_name':     options.get('staff_name'),
                'role':           options.get('role'),
                'is_verified':    options['is_verified'],
                'follower_count': options.get('follower_count'),
            },
        )

        verb = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f"{verb} {obj.platform} handle {obj.handle} (id={obj.id})"
        ))

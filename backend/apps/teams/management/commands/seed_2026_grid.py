"""
Idempotent management command: sync 2026 F1 grid data.

What it does
------------
1. Rename Kick Sauber → Audi F1 Team (SAU → AUD, new color, country).
2. Create Cadillac F1 Team (CAD) if not present — the 11th team in 2026.
3. Create/update RACE DriverContract rows for all 22 2026 race drivers
   (11 teams × 2), linked to the correct team via DriverContract.driver FK
   and season FK.

Usage
-----
    python manage.py seed_2026_grid
    python manage.py seed_2026_grid --dry-run
"""
from datetime import date
from django.core.management.base import BaseCommand


# 2026 race grid: (driver_code, team_code)
RACE_GRID_2026 = [
    ("VER", "RBR"),
    ("LAW", "RBR"),
    ("LEC", "FER"),
    ("HAM", "FER"),
    ("NOR", "MCL"),
    ("PIA", "MCL"),
    ("RUS", "MER"),
    ("ANT", "MER"),
    ("ALO", "AMR"),
    ("STR", "AMR"),
    ("GAS", "ALP"),
    ("DOO", "ALP"),
    ("ALB", "WIL"),
    ("SAI", "WIL"),
    ("TSU", "RBT"),
    ("HAD", "RBT"),
    ("BEA", "HAA"),
    ("OCO", "HAA"),
    ("HUL", "AUD"),
    ("BOR", "AUD"),
    # Cadillac F1 Team — 11th constructor, 2026 entry
    ("PER", "CAD"),
    ("BOT", "CAD"),
]

SEASON_YEAR = 2026
VALID_FROM   = date(2026, 1, 1)


class Command(BaseCommand):
    help = "Sync 2026 F1 grid: Audi rebrand + Cadillac creation + 22 RACE DriverContract rows"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Preview changes without writing to the database'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        from apps.teams.models import Team, Driver, DriverContract
        from apps.championships.models import Season

        # ── Step 1: Audi rebrand ─────────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("Step 1 — Audi rebrand"))
        try:
            sauber = Team.objects.get(code="SAU")
            if dry_run:
                self.stdout.write(
                    f"  [DRY-RUN] Would rename '{sauber.base_name}' (SAU) → "
                    f"'Audi F1 Team' (AUD), color #BB0000, country Germany"
                )
            else:
                sauber.code          = "AUD"
                sauber.base_name     = "Audi F1 Team"
                sauber.primary_color = "#BB0000"
                sauber.country       = "Germany"
                sauber.save()
                self.stdout.write(self.style.SUCCESS("  ✓ Team renamed → Audi F1 Team (AUD)"))
        except Team.DoesNotExist:
            # Already renamed or never seeded as SAU
            try:
                Team.objects.get(code="AUD")
                self.stdout.write("  Audi team (AUD) already exists — skipping rebrand")
            except Team.DoesNotExist:
                self.stderr.write(self.style.ERROR(
                    "  Neither SAU nor AUD team found — run seed_data first"
                ))
                return

        # ── Step 2: Cadillac F1 Team ─────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("Step 2 — Cadillac F1 Team (CAD)"))
        if dry_run:
            self.stdout.write("  [DRY-RUN] Would get_or_create Team(code=CAD)")
        else:
            cad, cad_created = Team.objects.get_or_create(
                code="CAD",
                defaults={
                    'base_name':     'Cadillac F1 Team',
                    'country':       'United States',
                    'founded_year':  2026,
                    'primary_color': '#000000',
                }
            )
            label = "created" if cad_created else "exists"
            self.stdout.write(self.style.SUCCESS(f"  ✓ Cadillac F1 Team (CAD) — {label}"))

        # ── Step 3: Season ───────────────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("Step 3 — Season"))
        if dry_run:
            self.stdout.write(f"  [DRY-RUN] Would get_or_create Season(year={SEASON_YEAR})")
            season = None
        else:
            season, created = Season.objects.get_or_create(
                year=SEASON_YEAR,
                defaults={'is_current': True}
            )
            label = "created" if created else "exists"
            self.stdout.write(self.style.SUCCESS(f"  ✓ Season {SEASON_YEAR} ({label})"))

        # ── Step 4: RACE contracts ───────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("Step 4 — RACE DriverContracts (22 drivers)"))
        created_count = updated_count = skipped_count = 0

        for driver_code, team_code in RACE_GRID_2026:
            try:
                driver = Driver.objects.get(code=driver_code)
            except Driver.DoesNotExist:
                self.stderr.write(f"  Driver not found: {driver_code} — skipping")
                skipped_count += 1
                continue

            try:
                team = Team.objects.get(code=team_code)
            except Team.DoesNotExist:
                if dry_run and team_code == "AUD":
                    # SAU not yet renamed in dry-run — simulate
                    try:
                        team = Team.objects.get(code="SAU")
                    except Team.DoesNotExist:
                        self.stderr.write(f"  Team not found: {team_code} — skipping {driver_code}")
                        skipped_count += 1
                        continue
                else:
                    self.stderr.write(f"  Team not found: {team_code} — skipping {driver_code}")
                    skipped_count += 1
                    continue

            if dry_run:
                self.stdout.write(
                    f"  [DRY-RUN] {driver.full_name:25} → {team.base_name} ({team_code}) [RACE]"
                )
                created_count += 1
                continue

            obj, was_created = DriverContract.objects.get_or_create(
                driver=driver,
                team=team,
                season=season,
                role='RACE',
                defaults={
                    'is_active':   True,
                    'valid_from':  VALID_FROM,
                    'valid_until': None,
                },
            )
            if not was_created:
                # Ensure is_active is current
                if not obj.is_active:
                    obj.is_active = True
                    obj.save(update_fields=['is_active', 'updated_at'])
                    updated_count += 1
                    self.stdout.write(f"  ~ updated: {driver.full_name} @ {team.base_name}")
                else:
                    self.stdout.write(f"  = exists:  {driver.full_name} @ {team.base_name}")
            else:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ created: {driver.full_name} @ {team.base_name}")
                )

        # ── Summary ──────────────────────────────────────────────────────────
        label = "Dry-run complete" if dry_run else "Done"
        self.stdout.write(self.style.SUCCESS(
            f"\n{label} — created: {created_count}, "
            f"updated: {updated_count}, skipped: {skipped_count}"
        ))
        if not dry_run:
            self.stdout.write(
                "\nNext step: run seed_staff_contracts to load TP/staff roles:\n"
                "  python manage.py seed_staff_contracts "
                "--file data/staff_contracts_2026.json --season 2026"
            )

"""
Team and driver models for PitLane F1 platform.
"""
from django.db import models
from config.utils import generate_id


class Team(models.Model):
    """
    Core team entity - represents an F1 team/constructor across all seasons.
    Temporal team identities (names, branding) are tracked via TeamIdentity.
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    code = models.CharField(max_length=10, unique=True, db_index=True)  # e.g., "RBR", "FER"
    base_name = models.CharField(max_length=200)  # Base name, e.g., "Red Bull Racing"
    country = models.CharField(max_length=100)
    headquarters = models.CharField(max_length=200, null=True, blank=True)
    founded_year = models.IntegerField()

    # Current manufacturers and suppliers (versioned via TeamIdentity)
    manufacturer = models.ForeignKey(
        'brands.Manufacturer',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='teams'
    )
    current_engine_supplier = models.ForeignKey(
        'brands.EngineSupplier',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='teams'
    )

    # Branding
    primary_color = models.CharField(max_length=7, null=True, blank=True)  # Hex color
    secondary_color = models.CharField(max_length=7, null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teams'
        ordering = ['base_name']

    def __str__(self):
        return self.base_name


class Driver(models.Model):
    """
    Core driver entity - represents an F1 driver across their entire career.
    Temporal contracts and team assignments are tracked via DriverContract.
    """
    DRIVER_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('RESERVE', 'Reserve'),
        ('RETIRED', 'Retired'),
        ('INACTIVE', 'Inactive'),
    ]

    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    code = models.CharField(max_length=10, unique=True, db_index=True)  # e.g., "VER", "HAM"

    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200, db_index=True)
    nationality = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=200, null=True, blank=True)

    # Racing information
    racing_number = models.IntegerField(null=True, blank=True, db_index=True)  # Permanent number (post-2014)

    # Career stats (can be computed but cached for performance)
    debut_year = models.IntegerField(null=True, blank=True)
    total_races = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_podiums = models.IntegerField(default=0)
    total_poles = models.IntegerField(default=0)
    total_fastest_laps = models.IntegerField(default=0)
    championships = models.IntegerField(default=0)

    # Media
    headshot_url = models.URLField(null=True, blank=True)
    profile_image_url = models.URLField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=DRIVER_STATUS_CHOICES, default='ACTIVE', db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'drivers'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['nationality']),
        ]

    def __str__(self):
        return self.full_name


class TeamIdentity(models.Model):
    """
    Temporal team identity - tracks team name changes, branding, and supplier changes per season.
    Supports full team history (e.g., "Oracle Red Bull Racing" → "Red Bull Racing").
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='identities'
    )
    season = models.ForeignKey(
        'championships.Season',
        on_delete=models.CASCADE,
        related_name='team_identities'
    )

    # Versioned team identity
    official_name = models.CharField(max_length=200)  # Full official name for that season
    short_name = models.CharField(max_length=100, null=True, blank=True)
    display_name = models.CharField(max_length=200, null=True, blank=True)

    # Versioned suppliers
    manufacturer = models.ForeignKey(
        'brands.Manufacturer',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='team_identities'
    )
    engine_supplier = models.ForeignKey(
        'brands.EngineSupplier',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='team_identities'
    )

    # Versioned branding
    primary_color = models.CharField(max_length=7, null=True, blank=True)
    secondary_color = models.CharField(max_length=7, null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)

    # Temporal tracking
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'team_identities'
        unique_together = [['team', 'season']]
        ordering = ['-season__year', 'team']
        indexes = [
            models.Index(fields=['team', 'valid_from', 'valid_until']),
            models.Index(fields=['season']),
        ]

    def __str__(self):
        return f"{self.official_name} ({self.season.year})"


class DriverContract(models.Model):
    """
    Temporal driver/staff contract - tracks driver and paddock staff assignments per team.
    Supports full history including race drivers, reserve/test drivers, and staff roles
    (team principals, engineers, mechanics, etc.).
    """
    CONTRACT_ROLE_CHOICES = [
        # Driver roles
        ('RACE',        'Race Driver'),
        ('RESERVE',     'Reserve Driver'),
        ('TEST',        'Test Driver'),
        ('DEVELOPMENT', 'Development Driver'),
        ('LOAN',        'On Loan'),
        ('GUEST',       'Guest Driver'),
        # Staff / paddock roles
        ('TEAM_PRINCIPAL',       'Team Principal'),
        ('TECHNICAL_DIRECTOR',   'Technical Director'),
        ('RACE_ENGINEER',        'Race Engineer'),
        ('PERFORMANCE_ENGINEER', 'Performance Engineer'),
        ('HEAD_AERO',            'Head of Aerodynamics'),
        ('MECHANIC',             'Mechanic'),
        ('STAFF',                'Staff (Other)'),
    ]

    DRIVER_ROLES = {'RACE', 'RESERVE', 'TEST', 'DEVELOPMENT', 'LOAN', 'GUEST'}

    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    driver = models.ForeignKey(
        Driver,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='contracts'
    )
    person_name = models.CharField(max_length=200, null=True, blank=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='driver_contracts'
    )
    season = models.ForeignKey(
        'championships.Season',
        on_delete=models.CASCADE,
        related_name='driver_contracts'
    )

    # Contract details
    role = models.CharField(max_length=30, choices=CONTRACT_ROLE_CHOICES, db_index=True)
    car_number = models.IntegerField(null=True, blank=True)  # Pre-2014 variable numbers
    is_active = models.BooleanField(default=True, db_index=True)

    # Temporal tracking
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    # Contract metadata
    announcement_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)  # For loan details, special conditions, etc.

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'driver_contracts'
        ordering = ['-season__year', 'team', 'role']
        indexes = [
            models.Index(fields=['driver', 'valid_from', 'valid_until']),
            models.Index(fields=['team', 'season']),
            models.Index(fields=['season', 'role']),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.role in self.DRIVER_ROLES and not self.driver_id:
            raise ValidationError("Driver roles require a linked Driver.")
        if self.role not in self.DRIVER_ROLES and not self.person_name:
            raise ValidationError("Staff roles require a person_name.")

    def __str__(self):
        person = self.driver.full_name if self.driver else self.person_name
        return f"{person} - {self.team.base_name} ({self.season.year}) [{self.get_role_display()}]"


class TeamSponsor(models.Model):
    """
    Team sponsor relationships - tracks sponsor associations with temporal validity.
    """
    SPONSORSHIP_TYPE_CHOICES = [
        ('TITLE', 'Title Sponsor'),
        ('PRINCIPAL', 'Principal Partner'),
        ('TECHNICAL', 'Technical Partner'),
        ('OFFICIAL', 'Official Partner'),
        ('SUPPLIER', 'Official Supplier'),
    ]

    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='sponsor_relationships'
    )
    sponsor = models.ForeignKey(
        'brands.Sponsor',
        on_delete=models.CASCADE,
        related_name='team_relationships'
    )
    season = models.ForeignKey(
        'championships.Season',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='team_sponsors'
    )

    # Sponsorship details
    sponsorship_type = models.CharField(max_length=20, choices=SPONSORSHIP_TYPE_CHOICES, db_index=True)
    is_title_sponsor = models.BooleanField(default=False)

    # Temporal tracking
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'team_sponsors'
        ordering = ['-valid_from', 'team']
        indexes = [
            models.Index(fields=['team', 'valid_from', 'valid_until']),
            models.Index(fields=['sponsor', 'valid_from', 'valid_until']),
            models.Index(fields=['season']),
        ]

    def __str__(self):
        return f"{self.sponsor.name} - {self.team.base_name} ({self.get_sponsorship_type_display()})"


class DriverSponsor(models.Model):
    """
    Driver sponsor relationships - tracks personal driver sponsors with temporal validity.
    """
    SPONSORSHIP_TYPE_CHOICES = [
        ('PERSONAL', 'Personal Sponsor'),
        ('HELMET', 'Helmet Sponsor'),
        ('CLOTHING', 'Clothing Sponsor'),
        ('EQUIPMENT', 'Equipment Sponsor'),
    ]

    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name='sponsor_relationships'
    )
    sponsor = models.ForeignKey(
        'brands.Sponsor',
        on_delete=models.CASCADE,
        related_name='driver_relationships'
    )

    # Sponsorship details
    sponsorship_type = models.CharField(max_length=20, choices=SPONSORSHIP_TYPE_CHOICES, db_index=True)

    # Temporal tracking
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'driver_sponsors'
        ordering = ['-valid_from', 'driver']
        indexes = [
            models.Index(fields=['driver', 'valid_from', 'valid_until']),
            models.Index(fields=['sponsor', 'valid_from', 'valid_until']),
        ]

    def __str__(self):
        return f"{self.sponsor.name} - {self.driver.full_name} ({self.get_sponsorship_type_display()})"


class Platform(models.TextChoices):
    TWITTER   = 'TWITTER',   'Twitter / X'
    INSTAGRAM = 'INSTAGRAM', 'Instagram'
    TIKTOK    = 'TIKTOK',    'TikTok'
    YOUTUBE   = 'YOUTUBE',   'YouTube'
    FACEBOOK  = 'FACEBOOK',  'Facebook'
    LINKEDIN  = 'LINKEDIN',  'LinkedIn'


class SocialEntityType(models.TextChoices):
    DRIVER  = 'DRIVER',  'Driver'
    TEAM    = 'TEAM',    'Team'
    STAFF   = 'STAFF',   'Staff / Engineer / Mechanic'
    PARTNER = 'PARTNER', 'Partner / Brand'


class SocialHandle(models.Model):
    id            = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    platform      = models.CharField(max_length=20, choices=Platform.choices, db_index=True)
    handle        = models.CharField(max_length=100)           # e.g. "@LewisHamilton"
    url           = models.URLField(max_length=500)
    entity_type   = models.CharField(max_length=20, choices=SocialEntityType.choices, db_index=True)

    # Per-type nullable FKs (Phase 1). Migrates to universal Entity FK in PL-018.
    driver        = models.ForeignKey('Driver', null=True, blank=True,
                                      on_delete=models.SET_NULL, related_name='social_handles')
    team          = models.ForeignKey('Team', null=True, blank=True,
                                      on_delete=models.SET_NULL, related_name='social_handles')
    staff_name    = models.CharField(max_length=200, null=True, blank=True)
    role          = models.CharField(max_length=100, null=True, blank=True)

    is_verified   = models.BooleanField(default=False)
    is_active     = models.BooleanField(default=True, db_index=True)
    valid_from    = models.DateField(null=True, blank=True)
    valid_until   = models.DateField(null=True, blank=True)
    follower_count = models.IntegerField(null=True, blank=True)

    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_handles'
        unique_together = [['platform', 'handle']]
        ordering = ['entity_type', 'platform']
        verbose_name_plural = 'Social Handles'

    def __str__(self):
        return f"{self.handle} ({self.platform})"

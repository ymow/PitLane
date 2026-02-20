"""
Circuit models for PitLane F1 platform.
"""
from django.db import models
from config.utils import generate_id


class Circuit(models.Model):
    """
    Core circuit entity - represents an F1 circuit across all seasons.
    Temporal configurations (layout changes, characteristics) are tracked via CircuitConfiguration.
    """
    CIRCUIT_TYPE_CHOICES = [
        ('PERMANENT', 'Permanent Race Circuit'),
        ('STREET', 'Street Circuit'),
        ('SEMI_PERMANENT', 'Semi-Permanent Circuit'),
    ]

    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    code = models.CharField(max_length=10, unique=True, db_index=True)  # e.g., "MON", "SPA"
    name = models.CharField(max_length=200, db_index=True)
    full_name = models.CharField(max_length=300, null=True, blank=True)

    # Location
    country = models.CharField(max_length=100, db_index=True)
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    timezone = models.CharField(max_length=50, null=True, blank=True)

    # Circuit characteristics
    circuit_type = models.CharField(max_length=20, choices=CIRCUIT_TYPE_CHOICES, default='PERMANENT')
    direction = models.CharField(max_length=20, null=True, blank=True)  # Clockwise/Anticlockwise
    opened_year = models.IntegerField(null=True, blank=True)

    # Current configuration (versioned via CircuitConfiguration)
    current_length_km = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    current_corners = models.IntegerField(null=True, blank=True)
    current_drs_zones = models.IntegerField(null=True, blank=True)

    # Media
    track_map_url = models.URLField(null=True, blank=True)
    aerial_image_url = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'circuits'
        ordering = ['name']
        indexes = [
            models.Index(fields=['country', 'name']),
        ]

    def __str__(self):
        return self.name


class CircuitConfiguration(models.Model):
    """
    Temporal circuit configuration - tracks layout changes and characteristics per season.
    Supports versioned circuit configs (different lap lengths, corner counts, DRS zones, etc.).
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    circuit = models.ForeignKey(
        Circuit,
        on_delete=models.CASCADE,
        related_name='configurations'
    )
    season = models.ForeignKey(
        'championships.Season',
        on_delete=models.CASCADE,
        related_name='circuit_configurations'
    )

    # Layout configuration
    layout_name = models.CharField(max_length=200, null=True, blank=True)  # e.g., "Grand Prix Circuit", "National Circuit"
    length_km = models.DecimalField(max_digits=6, decimal_places=3)
    corners = models.IntegerField()
    left_corners = models.IntegerField(null=True, blank=True)
    right_corners = models.IntegerField(null=True, blank=True)
    drs_zones = models.IntegerField(default=0)

    # Track characteristics
    lap_record_time = models.CharField(max_length=20, null=True, blank=True)  # e.g., "1:13.078"
    lap_record_driver = models.ForeignKey(
        'teams.Driver',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='circuit_lap_records'
    )
    lap_record_year = models.IntegerField(null=True, blank=True)

    # Additional characteristics
    longest_straight_m = models.IntegerField(null=True, blank=True)
    elevation_change_m = models.IntegerField(null=True, blank=True)
    pit_lane_length_m = models.IntegerField(null=True, blank=True)
    pit_speed_limit_kph = models.IntegerField(null=True, blank=True)

    # Media
    track_map_url = models.URLField(null=True, blank=True)

    # Temporal tracking
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    # Configuration notes
    notes = models.TextField(null=True, blank=True)  # Track changes description

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'circuit_configurations'
        unique_together = [['circuit', 'season']]
        ordering = ['-season__year', 'circuit']
        indexes = [
            models.Index(fields=['circuit', 'valid_from', 'valid_until']),
            models.Index(fields=['season']),
        ]

    def __str__(self):
        layout = f" - {self.layout_name}" if self.layout_name else ""
        return f"{self.circuit.name}{layout} ({self.season.year})"

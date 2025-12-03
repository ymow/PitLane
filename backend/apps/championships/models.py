"""
Championship and points system models for PitLane F1 platform.
"""
from django.db import models
from config.utils import generate_id


class Season(models.Model):
    """
    F1 Season - represents a single F1 championship year
    """
    id = models.CharField(max_length=25, primary_key=True, default=generate_id, editable=False)
    year = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    total_races = models.IntegerField(default=23)
    tire_supplier = models.ForeignKey(
        'brands.TireSupplier',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='seasons'
    )
    points_system = models.ForeignKey(
        'PointsSystem',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='seasons'
    )
    is_current = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'seasons'
        ordering = ['-year']

    def __str__(self):
        return f"{self.year} Season"


class PointsSystem(models.Model):
    """
    Track different points systems across F1 eras
    """
    id = models.CharField(max_length=25, primary_key=True, default=generate_id, editable=False)
    name = models.CharField(max_length=100)
    valid_from_year = models.IntegerField(db_index=True)
    valid_until_year = models.IntegerField(null=True, blank=True)
    p1_points = models.IntegerField()  # 1st place
    p2_points = models.IntegerField()
    p3_points = models.IntegerField()
    p4_points = models.IntegerField()
    p5_points = models.IntegerField()
    p6_points = models.IntegerField()
    p7_points = models.IntegerField()
    p8_points = models.IntegerField()
    p9_points = models.IntegerField()
    p10_points = models.IntegerField()
    has_fastest_lap_point = models.BooleanField(default=False)
    fastest_lap_point = models.IntegerField(default=0)
    fastest_lap_min_position = models.IntegerField(null=True, blank=True)
    has_sprint_points = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'points_systems'
        ordering = ['-valid_from_year']

    def __str__(self):
        return self.name


class DriverStanding(models.Model):
    """
    Driver championship standings per season
    """
    id = models.CharField(max_length=25, primary_key=True, default=generate_id, editable=False)
    driver = models.ForeignKey(
        'teams.Driver',
        on_delete=models.CASCADE,
        related_name='standings'
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name='driver_standings'
    )
    position = models.IntegerField()
    points = models.DecimalField(max_digits=7, decimal_places=2)
    wins = models.IntegerField(default=0)
    podiums = models.IntegerField(default=0)
    pole_positions = models.IntegerField(default=0)
    fastest_laps = models.IntegerField(default=0)
    races_entered = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'driver_standings'
        unique_together = [['season', 'driver']]
        ordering = ['season', 'position']
        indexes = [
            models.Index(fields=['season', 'position']),
        ]

    def __str__(self):
        return f"{self.driver} - {self.season.year} (P{self.position})"


class ConstructorStanding(models.Model):
    """
    Constructor championship standings per season
    """
    id = models.CharField(max_length=25, primary_key=True, default=generate_id, editable=False)
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='standings'
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name='constructor_standings'
    )
    position = models.IntegerField()
    points = models.DecimalField(max_digits=7, decimal_places=2)
    wins = models.IntegerField(default=0)
    podiums = models.IntegerField(default=0)
    pole_positions = models.IntegerField(default=0)
    fastest_laps = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'constructor_standings'
        unique_together = [['season', 'team']]
        ordering = ['season', 'position']
        indexes = [
            models.Index(fields=['season', 'position']),
        ]

    def __str__(self):
        return f"{self.team} - {self.season.year} (P{self.position})"

"""
Racing infrastructure models for PitLane F1 platform.
"""
from django.db import models
from config.utils import generate_id


class Race(models.Model):
    """
    A race weekend (Grand Prix) - contains multiple sessions.
    """
    RACE_STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('ONGOING', 'Ongoing'),
        ('PROVISIONAL', 'Provisional'), # Added: Post-race investigation period
        ('COMPLETED', 'Completed'),
        ('OFFICIAL', 'Official'),       # Added: Final validated result
        ('CANCELLED', 'Cancelled'),
        ('POSTPONED', 'Postponed'),
    ]

    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    season = models.ForeignKey(
        'championships.Season',
        on_delete=models.CASCADE,
        related_name='races'
    )
    circuit = models.ForeignKey(
        'circuits.Circuit',
        on_delete=models.CASCADE,
        related_name='races'
    )
    circuit_configuration = models.ForeignKey(
        'circuits.CircuitConfiguration',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='races'
    )

    # Race details
    round_number = models.IntegerField(db_index=True)
    official_name = models.CharField(max_length=200)  # e.g., "Monaco Grand Prix"
    short_name = models.CharField(max_length=100, null=True, blank=True)

    # Dates
    race_date = models.DateField(db_index=True)
    race_time = models.TimeField(null=True, blank=True)
    weekend_start_date = models.DateField(null=True, blank=True)
    weekend_end_date = models.DateField(null=True, blank=True)

    # Sprint weekend flag
    is_sprint_weekend = models.BooleanField(default=False, db_index=True)

    # Status
    status = models.CharField(max_length=20, choices=RACE_STATUS_CHOICES, default='SCHEDULED', db_index=True)

    # Additional info
    total_laps = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'races'
        unique_together = [['season', 'round_number']]
        ordering = ['season', 'round_number']
        indexes = [
            models.Index(fields=['season', 'round_number']),
            models.Index(fields=['race_date']),
        ]

    def __str__(self):
        return f"{self.season.year} {self.official_name} (R{self.round_number})"


class Session(models.Model):
    """
    Base session model - represents any track session (practice, qualifying, or race).
    Uses polymorphic pattern with type-specific models via OneToOne relationships.
    """
    SESSION_TYPE_CHOICES = [
        ('FP1', 'Free Practice 1'),
        ('FP2', 'Free Practice 2'),
        ('FP3', 'Free Practice 3'),
        ('QUALIFYING', 'Qualifying'),
        ('SPRINT_QUALIFYING', 'Sprint Qualifying'),
        ('SPRINT', 'Sprint'),
        ('RACE', 'Race'),
    ]

    SESSION_STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('SUSPENDED', 'Suspended'),
        ('RED_FLAG', 'Red Flag'),
    ]

    WEATHER_CHOICES = [
        ('SUNNY', 'Sunny'),
        ('CLOUDY', 'Cloudy'),
        ('OVERCAST', 'Overcast'),
        ('RAINY', 'Rainy'),
        ('DRIZZLE', 'Drizzle'),
        ('STORMY', 'Stormy'),
    ]

    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='sessions'
    )

    # Session details
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, db_index=True)
    session_name = models.CharField(max_length=100)

    # Timing
    scheduled_start = models.DateTimeField(db_index=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='SCHEDULED', db_index=True)

    # External Link
    openf1_session_key = models.IntegerField(null=True, blank=True, help_text="Session key for OpenF1/FastF1 API")

    # Weather and track conditions
    weather = models.CharField(max_length=20, choices=WEATHER_CHOICES, null=True, blank=True)
    air_temp_celsius = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    track_temp_celsius = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity_percent = models.IntegerField(null=True, blank=True)
    wind_speed_kph = models.IntegerField(null=True, blank=True)
    rainfall = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sessions'
        ordering = ['race', 'scheduled_start']
        indexes = [
            models.Index(fields=['race', 'session_type']),
            models.Index(fields=['scheduled_start']),
        ]

    def __str__(self):
        return f"{self.race.official_name} - {self.session_name}"


class PracticeSession(models.Model):
    """
    Practice session details - extends Session via OneToOne.
    Tracks practice-specific data.
    """
    session = models.OneToOneField(
        Session,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='practice_details'
    )

    # Practice session stats
    total_laps_completed = models.IntegerField(default=0)
    fastest_lap_time = models.CharField(max_length=20, null=True, blank=True)
    fastest_lap_driver = models.ForeignKey(
        'teams.Driver',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='practice_fastest_laps'
    )

    # Session incidents
    red_flags = models.IntegerField(default=0)
    yellow_flags = models.IntegerField(default=0)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'practice_sessions'

    def __str__(self):
        return f"Practice: {self.session.session_name}"


class QualifyingSession(models.Model):
    """
    Qualifying session details - extends Session via OneToOne.
    Tracks Q1/Q2/Q3 knockout format and results.
    """
    session = models.OneToOneField(
        Session,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='qualifying_details'
    )

    # Qualifying format
    has_q1 = models.BooleanField(default=True)
    has_q2 = models.BooleanField(default=True)
    has_q3 = models.BooleanField(default=True)

    # Q1 timing
    q1_start = models.DateTimeField(null=True, blank=True)
    q1_end = models.DateTimeField(null=True, blank=True)
    q1_fastest_time = models.CharField(max_length=20, null=True, blank=True)

    # Q2 timing
    q2_start = models.DateTimeField(null=True, blank=True)
    q2_end = models.DateTimeField(null=True, blank=True)
    q2_fastest_time = models.CharField(max_length=20, null=True, blank=True)

    # Q3 timing
    q3_start = models.DateTimeField(null=True, blank=True)
    q3_end = models.DateTimeField(null=True, blank=True)
    q3_fastest_time = models.CharField(max_length=20, null=True, blank=True)

    # Pole position
    pole_position_driver = models.ForeignKey(
        'teams.Driver',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='pole_positions'
    )
    pole_position_time = models.CharField(max_length=20, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'qualifying_sessions'

    def __str__(self):
        return f"Qualifying: {self.session.session_name}"


class RaceSession(models.Model):
    """
    Race session details - extends Session via OneToOne.
    Tracks the actual race or sprint race.
    """
    RACE_TYPE_CHOICES = [
        ('GRAND_PRIX', 'Grand Prix'),
        ('SPRINT', 'Sprint Race'),
    ]

    session = models.OneToOneField(
        Session,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='race_details'
    )

    # Race format
    race_type = models.CharField(max_length=20, choices=RACE_TYPE_CHOICES, default='GRAND_PRIX')
    total_laps = models.IntegerField()
    planned_distance_km = models.DecimalField(max_digits=7, decimal_places=3)
    actual_laps_completed = models.IntegerField(null=True, blank=True)

    # Race results summary
    winner = models.ForeignKey(
        'teams.Driver',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='race_wins'
    )
    winning_time = models.CharField(max_length=20, null=True, blank=True)
    fastest_lap_driver = models.ForeignKey(
        'teams.Driver',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='race_fastest_laps'
    )
    fastest_lap_time = models.CharField(max_length=20, null=True, blank=True)
    fastest_lap_number = models.IntegerField(null=True, blank=True)

    # Safety car / VSC
    safety_car_periods = models.IntegerField(default=0)
    virtual_safety_car_periods = models.IntegerField(default=0)
    red_flag_periods = models.IntegerField(default=0)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'race_sessions'

    def __str__(self):
        return f"Race: {self.session.session_name}"


class Car(models.Model):
    """
    Team's car for a specific season - tracks car identity and components.
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='cars'
    )
    season = models.ForeignKey(
        'championships.Season',
        on_delete=models.CASCADE,
        related_name='cars'
    )

    # Car details
    chassis_code = models.CharField(max_length=50, db_index=True)  # e.g., "RB19", "SF-23"
    full_name = models.CharField(max_length=200, null=True, blank=True)

    # Technical specs
    engine_supplier = models.ForeignKey(
        'brands.EngineSupplier',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cars'
    )
    manufacturer = models.ForeignKey(
        'brands.Manufacturer',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cars'
    )

    # Launch info
    launch_date = models.DateField(null=True, blank=True)
    livery_image_url = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cars'
        unique_together = [['team', 'season']]
        ordering = ['season', 'team']
        indexes = [
            models.Index(fields=['season', 'team']),
            models.Index(fields=['chassis_code']),
        ]

    def __str__(self):
        return f"{self.team.base_name} {self.chassis_code} ({self.season.year})"


class Component(models.Model):
    """
    Individual car component tracking - supports full lifecycle tracking.
    Tracks engines, gearboxes, turbochargers, etc. with usage hours/kilometers.
    """
    COMPONENT_TYPE_CHOICES = [
        ('ENGINE', 'Engine'),
        ('TURBOCHARGER', 'Turbocharger'),
        ('MGU_K', 'MGU-K'),
        ('MGU_H', 'MGU-H'),
        ('ENERGY_STORE', 'Energy Store'),
        ('CONTROL_ELECTRONICS', 'Control Electronics'),
        ('GEARBOX', 'Gearbox'),
        ('CHASSIS', 'Chassis'),
        ('FRONT_WING', 'Front Wing'),
        ('REAR_WING', 'Rear Wing'),
        ('FLOOR', 'Floor'),
        ('SUSPENSION', 'Suspension'),
    ]

    COMPONENT_STATUS_CHOICES = [
        ('NEW', 'New'),
        ('IN_USE', 'In Use'),
        ('WORN', 'Worn'),
        ('DAMAGED', 'Damaged'),
        ('RETIRED', 'Retired'),
        ('PENALIZED', 'Penalized'),  # Grid penalty applied
    ]

    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='components'
    )
    driver = models.ForeignKey(
        'teams.Driver',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='car_components'
    )

    # Component details
    component_type = models.CharField(max_length=30, choices=COMPONENT_TYPE_CHOICES, db_index=True)
    component_number = models.IntegerField()  # Sequential number within type (Engine #1, #2, etc.)
    serial_number = models.CharField(max_length=100, null=True, blank=True)

    # Supplier
    supplier = models.ForeignKey(
        'brands.EngineSupplier',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='supplied_components'
    )

    # Lifecycle tracking
    first_used_race = models.ForeignKey(
        Race,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='component_debuts'
    )
    last_used_race = models.ForeignKey(
        Race,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='component_finals'
    )

    # Usage metrics
    total_races = models.IntegerField(default=0)
    total_kilometers = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Status
    status = models.CharField(max_length=20, choices=COMPONENT_STATUS_CHOICES, default='NEW', db_index=True)
    caused_grid_penalty = models.BooleanField(default=False)
    penalty_positions = models.IntegerField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'components'
        ordering = ['car', 'component_type', 'component_number']
        indexes = [
            models.Index(fields=['car', 'component_type']),
            models.Index(fields=['driver', 'component_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.car.chassis_code} - {self.get_component_type_display()} #{self.component_number}"


class LapTime(models.Model):
    """
    Individual lap time data - records every lap completed by every driver.
    Supports corner-by-corner, mini-sectors, and speed trap data.
    """
    LAP_STATUS_CHOICES = [
        ('VALID', 'Valid'),
        ('INVALID', 'Invalid'),
        ('DELETED', 'Deleted'),
        ('PERSONAL_BEST', 'Personal Best'),
        ('SESSION_BEST', 'Session Best'),
        ('FASTEST_LAP', 'Fastest Lap'),
    ]

    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='lap_times'
    )
    driver = models.ForeignKey(
        'teams.Driver',
        on_delete=models.CASCADE,
        related_name='lap_times'
    )
    car = models.ForeignKey(
        Car,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='lap_times'
    )

    # Lap details
    lap_number = models.IntegerField(db_index=True)
    lap_time = models.CharField(max_length=20)  # e.g., "1:23.456"
    lap_time_ms = models.IntegerField()  # Milliseconds for sorting/comparison

    # Sector times
    sector_1_time = models.CharField(max_length=20, null=True, blank=True)
    sector_1_ms = models.IntegerField(null=True, blank=True)
    sector_2_time = models.CharField(max_length=20, null=True, blank=True)
    sector_2_ms = models.IntegerField(null=True, blank=True)
    sector_3_time = models.CharField(max_length=20, null=True, blank=True)
    sector_3_ms = models.IntegerField(null=True, blank=True)

    # Speed trap data
    speed_i1_kph = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # Intermediate 1
    speed_i2_kph = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # Intermediate 2
    speed_fl_kph = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # Finish line
    speed_st_kph = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # Speed trap

    # Lap status and flags
    status = models.CharField(max_length=20, choices=LAP_STATUS_CHOICES, default='VALID')
    is_pit_lap = models.BooleanField(default=False, db_index=True)
    pit_duration_ms = models.IntegerField(null=True, blank=True)

    # Track position
    position_at_completion = models.IntegerField(null=True, blank=True)
    gap_to_leader = models.CharField(max_length=20, null=True, blank=True)
    interval_to_ahead = models.CharField(max_length=20, null=True, blank=True)

    # Tire information
    tire_compound = models.CharField(max_length=20, null=True, blank=True)  # Soft, Medium, Hard, Intermediate, Wet
    tire_age_laps = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lap_times'
        ordering = ['session', 'lap_number', 'driver']
        indexes = [
            models.Index(fields=['session', 'driver', 'lap_number']),
            models.Index(fields=['session', 'lap_time_ms']),
            models.Index(fields=['driver', 'status']),
        ]
        unique_together = [['session', 'driver', 'lap_number']]

    def __str__(self):
        return f"{self.driver.code} - L{self.lap_number}: {self.lap_time}"


class TelemetryData(models.Model):
    """
    Detailed telemetry data for corner-by-corner analysis.
    Time-series data at specific points on track.
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    lap_time = models.ForeignKey(
        LapTime,
        on_delete=models.CASCADE,
        related_name='telemetry_points'
    )

    # Position on track
    distance_from_start_m = models.DecimalField(max_digits=10, decimal_places=2)
    corner_number = models.IntegerField(null=True, blank=True)
    mini_sector = models.IntegerField(null=True, blank=True)

    # Time
    elapsed_time_ms = models.IntegerField()

    # Telemetry values
    speed_kph = models.DecimalField(max_digits=6, decimal_places=2)
    throttle_percent = models.IntegerField(null=True, blank=True)  # 0-100
    brake_percent = models.IntegerField(null=True, blank=True)  # 0-100
    gear = models.IntegerField(null=True, blank=True)
    rpm = models.IntegerField(null=True, blank=True)
    drs_open = models.BooleanField(default=False)

    # Position data
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'telemetry_data'
        ordering = ['lap_time', 'elapsed_time_ms']
        indexes = [
            models.Index(fields=['lap_time', 'distance_from_start_m']),
            models.Index(fields=['lap_time', 'corner_number']),
        ]

    def __str__(self):
        return f"{self.lap_time.driver.code} L{self.lap_time.lap_number} @ {self.distance_from_start_m}m"


class QualifyingResult(models.Model):
    """
    Qualifying results for a driver in a qualifying session.
    Tracks individual Q1/Q2/Q3 times and final grid position.
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='qualifying_results'
    )
    driver = models.ForeignKey(
        'teams.Driver',
        on_delete=models.CASCADE,
        related_name='qualifying_results'
    )
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='qualifying_results'
    )
    car = models.ForeignKey(
        Car,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='qualifying_results'
    )

    # Final position
    position = models.IntegerField(db_index=True)
    grid_position = models.IntegerField(null=True, blank=True)  # May differ due to penalties

    # Q1 result
    q1_time = models.CharField(max_length=20, null=True, blank=True)
    q1_time_ms = models.IntegerField(null=True, blank=True)
    q1_position = models.IntegerField(null=True, blank=True)
    advanced_to_q2 = models.BooleanField(default=False)

    # Q2 result
    q2_time = models.CharField(max_length=20, null=True, blank=True)
    q2_time_ms = models.IntegerField(null=True, blank=True)
    q2_position = models.IntegerField(null=True, blank=True)
    advanced_to_q3 = models.BooleanField(default=False)

    # Q3 result
    q3_time = models.CharField(max_length=20, null=True, blank=True)
    q3_time_ms = models.IntegerField(null=True, blank=True)
    q3_position = models.IntegerField(null=True, blank=True)

    # Gap to pole
    gap_to_pole = models.CharField(max_length=20, null=True, blank=True)
    gap_to_pole_ms = models.IntegerField(null=True, blank=True)

    # Penalties
    grid_penalty_positions = models.IntegerField(default=0)
    penalty_reason = models.TextField(null=True, blank=True)

    # Tire used for fastest lap
    fastest_tire_compound = models.CharField(max_length=20, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'qualifying_results'
        unique_together = [['session', 'driver']]
        ordering = ['session', 'position']
        indexes = [
            models.Index(fields=['session', 'position']),
            models.Index(fields=['driver']),
            models.Index(fields=['team']),
        ]

    def __str__(self):
        return f"{self.driver.code} - P{self.position} ({self.session.race.official_name})"


class RaceResult(models.Model):
    """
    Race results for a driver in a race session.
    Tracks finishing position, points, and race performance.
    """
    FINISH_STATUS_CHOICES = [
        ('FINISHED', 'Finished'),
        ('DNF', 'Did Not Finish'),
        ('DSQ', 'Disqualified'),
        ('DNS', 'Did Not Start'),
        ('RETIRED', 'Retired'),
        ('ACCIDENT', 'Accident'),
        ('MECHANICAL', 'Mechanical'),
        ('+LAPS', 'Lapped'),
    ]

    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='race_results'
    )
    driver = models.ForeignKey(
        'teams.Driver',
        on_delete=models.CASCADE,
        related_name='race_results'
    )
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='race_results'
    )
    car = models.ForeignKey(
        Car,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='race_results'
    )

    # Starting position
    grid_position = models.IntegerField(db_index=True)

    # Finishing position
    finish_position = models.IntegerField(null=True, blank=True, db_index=True)
    classified_position = models.IntegerField(null=True, blank=True)  # After penalties
    finish_status = models.CharField(max_length=20, choices=FINISH_STATUS_CHOICES, db_index=True)

    # Timing
    total_race_time = models.CharField(max_length=20, null=True, blank=True)
    total_race_time_ms = models.BigIntegerField(null=True, blank=True)
    gap_to_winner = models.CharField(max_length=20, null=True, blank=True)
    gap_to_winner_ms = models.IntegerField(null=True, blank=True)
    laps_behind = models.IntegerField(default=0)

    # Performance
    laps_completed = models.IntegerField(default=0)
    fastest_lap_number = models.IntegerField(null=True, blank=True)
    fastest_lap_time = models.CharField(max_length=20, null=True, blank=True)
    fastest_lap_time_ms = models.IntegerField(null=True, blank=True)
    fastest_lap_rank = models.IntegerField(null=True, blank=True)

    # Points
    points = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fastest_lap_point = models.BooleanField(default=False)

    # Analysis
    telemetry_chart = models.ImageField(upload_to='telemetry_charts/', null=True, blank=True)

    # Pit stops
    pit_stops = models.IntegerField(default=0)

    # Penalties
    time_penalties_seconds = models.IntegerField(default=0)
    penalty_reason = models.TextField(null=True, blank=True)

    # Position changes
    positions_gained = models.IntegerField(default=0)  # Can be negative

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'race_results'
        unique_together = [['session', 'driver']]
        ordering = ['session', 'classified_position']
        indexes = [
            models.Index(fields=['session', 'classified_position']),
            models.Index(fields=['driver']),
            models.Index(fields=['team']),
            models.Index(fields=['finish_status']),
        ]

    def __str__(self):
        if self.classified_position:
            return f"{self.driver.code} - P{self.classified_position} ({self.session.race.official_name})"
        return f"{self.driver.code} - {self.finish_status} ({self.session.race.official_name})"


class RaceEvent(models.Model):
    """
    Race events - significant incidents during a session (flags, safety cars, DRS, etc.).
    """
    EVENT_TYPE_CHOICES = [
        ('GREEN_FLAG', 'Green Flag'),
        ('YELLOW_FLAG', 'Yellow Flag'),
        ('DOUBLE_YELLOW', 'Double Yellow Flag'),
        ('RED_FLAG', 'Red Flag'),
        ('BLUE_FLAG', 'Blue Flag'),
        ('BLACK_FLAG', 'Black Flag'),
        ('SAFETY_CAR', 'Safety Car'),
        ('VSC', 'Virtual Safety Car'),
        ('DRS_ENABLED', 'DRS Enabled'),
        ('DRS_DISABLED', 'DRS Disabled'),
        ('SESSION_START', 'Session Start'),
        ('SESSION_END', 'Session End'),
        ('FORMATION_LAP', 'Formation Lap'),
    ]

    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='race_events'
    )

    # Event details
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES, db_index=True)
    event_time = models.DateTimeField(db_index=True)
    lap_number = models.IntegerField(null=True, blank=True)

    # Location (if applicable)
    track_sector = models.IntegerField(null=True, blank=True)  # 1, 2, or 3
    corner_number = models.IntegerField(null=True, blank=True)

    # Related drivers (if applicable)
    involved_drivers = models.ManyToManyField(
        'teams.Driver',
        blank=True,
        related_name='race_events'
    )

    # Event duration (for safety car, VSC, etc.)
    duration_laps = models.IntegerField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    # Notes
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'race_events'
        ordering = ['session', 'event_time']
        indexes = [
            models.Index(fields=['session', 'event_time']),
            models.Index(fields=['event_type']),
        ]

    def __str__(self):
        lap_info = f" (Lap {self.lap_number})" if self.lap_number else ""
        return f"{self.get_event_type_display()}{lap_info} - {self.session.session_name}"


class PitStop(models.Model):
    """
    Pit stop data - tracks every pit stop with timing and tire changes.
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='pit_stops'
    )
    driver = models.ForeignKey(
        'teams.Driver',
        on_delete=models.CASCADE,
        related_name='pit_stops'
    )
    car = models.ForeignKey(
        Car,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='pit_stops'
    )

    # Timing
    lap_number = models.IntegerField(db_index=True)
    pit_time = models.DateTimeField()
    pit_duration = models.CharField(max_length=20)  # e.g., "2.3s"
    pit_duration_ms = models.IntegerField()

    # Stop details
    stop_number = models.IntegerField()  # 1st stop, 2nd stop, etc.

    # Tire changes
    tire_removed = models.CharField(max_length=20, null=True, blank=True)  # Compound removed
    tire_fitted = models.CharField(max_length=20, null=True, blank=True)  # Compound fitted
    tire_age_removed = models.IntegerField(null=True, blank=True)  # Laps on removed tires

    # Pit work
    front_wing_changed = models.BooleanField(default=False)
    rear_wing_changed = models.BooleanField(default=False)
    repairs_made = models.BooleanField(default=False)
    repair_description = models.TextField(null=True, blank=True)

    # Penalties
    unsafe_release = models.BooleanField(default=False)
    speeding_in_pit_lane = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pit_stops'
        ordering = ['session', 'lap_number', 'pit_time']
        indexes = [
            models.Index(fields=['session', 'driver']),
            models.Index(fields=['lap_number']),
            models.Index(fields=['pit_duration_ms']),
        ]

    def __str__(self):
        return f"{self.driver.code} - Stop {self.stop_number}, Lap {self.lap_number} ({self.pit_duration})"


class Overtake(models.Model):
    """
    Overtake tracking - records overtaking maneuvers during sessions.
    """
    OVERTAKE_TYPE_CHOICES = [
        ('ON_TRACK', 'On Track'),
        ('DRS', 'DRS Assisted'),
        ('PIT_STRATEGY', 'Pit Strategy'),
        ('SLIPSTREAM', 'Slipstream'),
        ('OFF_TRACK', 'Off Track'),
        ('GIVEN_BACK', 'Position Given Back'),
    ]

    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='overtakes'
    )

    # Overtaking driver
    overtaking_driver = models.ForeignKey(
        'teams.Driver',
        on_delete=models.CASCADE,
        related_name='overtakes_made'
    )

    # Overtaken driver
    overtaken_driver = models.ForeignKey(
        'teams.Driver',
        on_delete=models.CASCADE,
        related_name='overtakes_received'
    )

    # Timing and location
    lap_number = models.IntegerField(db_index=True)
    overtake_time = models.DateTimeField()
    corner_number = models.IntegerField(null=True, blank=True)
    track_sector = models.IntegerField(null=True, blank=True)

    # Type and validity
    overtake_type = models.CharField(max_length=20, choices=OVERTAKE_TYPE_CHOICES)
    was_legal = models.BooleanField(default=True)
    under_investigation = models.BooleanField(default=False)

    # Position change
    position_before = models.IntegerField(null=True, blank=True)
    position_after = models.IntegerField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'overtakes'
        ordering = ['session', 'overtake_time']
        indexes = [
            models.Index(fields=['session', 'lap_number']),
            models.Index(fields=['overtaking_driver']),
            models.Index(fields=['overtaken_driver']),
        ]

    def __str__(self):
        return f"{self.overtaking_driver.code} overtakes {self.overtaken_driver.code} (L{self.lap_number})"


class TyreStint(models.Model):
    """
    Tire stint tracking - records tire usage periods during a session.
    """
    COMPOUND_CHOICES = [
        ('C1', 'C1 - Hard'),
        ('C2', 'C2 - Medium'),
        ('C3', 'C3 - Soft'),
        ('C4', 'C4 - Super Soft'),
        ('C5', 'C5 - Hyper Soft'),
        ('SOFT', 'Soft'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
        ('INTERMEDIATE', 'Intermediate'),
        ('WET', 'Wet'),
    ]

    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='tyre_stints'
    )
    driver = models.ForeignKey(
        'teams.Driver',
        on_delete=models.CASCADE,
        related_name='tyre_stints'
    )
    car = models.ForeignKey(
        Car,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tyre_stints'
    )

    # Stint details
    stint_number = models.IntegerField()  # 1st stint, 2nd stint, etc.
    compound = models.CharField(max_length=20, choices=COMPOUND_CHOICES)
    tire_age_at_start = models.IntegerField(default=0)  # Laps already on these tires

    # Stint range
    start_lap = models.IntegerField()
    end_lap = models.IntegerField(null=True, blank=True)
    total_laps = models.IntegerField(null=True, blank=True)

    # Performance
    fastest_lap_in_stint = models.CharField(max_length=20, null=True, blank=True)
    fastest_lap_number = models.IntegerField(null=True, blank=True)
    average_lap_time = models.CharField(max_length=20, null=True, blank=True)

    # Degradation
    tire_wear_percent = models.IntegerField(null=True, blank=True)  # 0-100
    graining = models.BooleanField(default=False)
    blistering = models.BooleanField(default=False)

    # End reason
    ended_by_pit_stop = models.BooleanField(default=False)
    ended_by_session_end = models.BooleanField(default=False)
    ended_by_retirement = models.BooleanField(default=False)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tyre_stints'
        ordering = ['session', 'driver', 'stint_number']
        indexes = [
            models.Index(fields=['session', 'driver']),
            models.Index(fields=['compound']),
        ]

    def __str__(self):
        return f"{self.driver.code} - Stint {self.stint_number}: {self.compound} (L{self.start_lap}-{self.end_lap or '?'})"

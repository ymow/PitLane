"""
Steward decision and penalty models for PitLane F1 platform.
"""
from django.db import models
from config.utils import generate_id


class Incident(models.Model):
    """
    Racing incidents - track limit violations, collisions, unsafe releases, etc.
    """
    INCIDENT_TYPE_CHOICES = [
        ('COLLISION', 'Collision'),
        ('TRACK_LIMITS', 'Track Limits Violation'),
        ('UNSAFE_RELEASE', 'Unsafe Pit Release'),
        ('SPEEDING_PIT', 'Speeding in Pit Lane'),
        ('IGNORING_FLAGS', 'Ignoring Flags'),
        ('CAUSING_COLLISION', 'Causing a Collision'),
        ('FORCING_OFF_TRACK', 'Forcing Another Driver Off Track'),
        ('BLOCKING', 'Blocking/Impeding'),
        ('FALSE_START', 'False Start'),
        ('ILLEGAL_OVERTAKE', 'Illegal Overtake'),
        ('CAR_UNDERWEIGHT', 'Car Underweight'),
        ('TECHNICAL_INFRINGEMENT', 'Technical Infringement'),
        ('SPORTING_INFRINGEMENT', 'Sporting Infringement'),
        ('OTHER', 'Other'),
    ]

    INCIDENT_STATUS_CHOICES = [
        ('REPORTED', 'Reported'),
        ('UNDER_INVESTIGATION', 'Under Investigation'),
        ('NO_ACTION', 'No Action Taken'),
        ('NOTED', 'Noted'),
        ('PENALTY_ISSUED', 'Penalty Issued'),
        ('DISMISSED', 'Dismissed'),
    ]

    id = models.CharField(max_length=25, primary_key=True, default=generate_id, editable=False)
    session = models.ForeignKey(
        'racing.Session',
        on_delete=models.CASCADE,
        related_name='incidents'
    )

    # Incident details
    incident_number = models.IntegerField(db_index=True)  # Sequential number per session
    incident_type = models.CharField(max_length=30, choices=INCIDENT_TYPE_CHOICES, db_index=True)
    incident_time = models.DateTimeField()
    lap_number = models.IntegerField(null=True, blank=True)

    # Location
    track_sector = models.IntegerField(null=True, blank=True)
    corner_number = models.IntegerField(null=True, blank=True)
    location_description = models.CharField(max_length=200, null=True, blank=True)

    # Involved parties
    involved_drivers = models.ManyToManyField(
        'teams.Driver',
        related_name='incidents'
    )
    involved_teams = models.ManyToManyField(
        'teams.Team',
        blank=True,
        related_name='incidents'
    )

    # Description
    description = models.TextField()
    video_url = models.URLField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=30, choices=INCIDENT_STATUS_CHOICES, default='REPORTED', db_index=True)
    reported_by = models.CharField(max_length=100, null=True, blank=True)  # e.g., "Race Control", "Team"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'incidents'
        unique_together = [['session', 'incident_number']]
        ordering = ['session', 'incident_number']
        indexes = [
            models.Index(fields=['session', 'incident_time']),
            models.Index(fields=['incident_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Incident #{self.incident_number} - {self.get_incident_type_display()} ({self.session.session_name})"


class StewardInvestigation(models.Model):
    """
    Steward investigations - formal investigations into incidents with decisions and appeals.
    """
    DECISION_CHOICES = [
        ('PENDING', 'Pending Decision'),
        ('NO_PENALTY', 'No Penalty'),
        ('REPRIMAND', 'Reprimand'),
        ('WARNING', 'Warning'),
        ('FINE', 'Fine'),
        ('TIME_PENALTY', 'Time Penalty'),
        ('GRID_PENALTY', 'Grid Penalty'),
        ('DRIVE_THROUGH', 'Drive-Through Penalty'),
        ('STOP_GO', 'Stop-Go Penalty'),
        ('DISQUALIFICATION', 'Disqualification'),
        ('POINTS_PENALTY', 'License Points Penalty'),
    ]

    APPEAL_STATUS_CHOICES = [
        ('NOT_APPEALED', 'Not Appealed'),
        ('APPEAL_PENDING', 'Appeal Pending'),
        ('APPEAL_UPHELD', 'Appeal Upheld'),
        ('APPEAL_REJECTED', 'Appeal Rejected'),
        ('APPEAL_WITHDRAWN', 'Appeal Withdrawn'),
    ]

    id = models.CharField(max_length=25, primary_key=True, default=generate_id, editable=False)
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='investigations'
    )

    # Investigation details
    investigation_number = models.CharField(max_length=50, db_index=True)  # e.g., "INV-2024-01-003"
    opened_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)

    # Investigated parties
    investigated_drivers = models.ManyToManyField(
        'teams.Driver',
        related_name='steward_investigations'
    )
    investigated_teams = models.ManyToManyField(
        'teams.Team',
        blank=True,
        related_name='steward_investigations'
    )

    # Steward panel
    chief_steward = models.CharField(max_length=200, null=True, blank=True)
    stewards = models.TextField(null=True, blank=True)  # List of stewards

    # Evidence and hearing
    evidence_reviewed = models.TextField(null=True, blank=True)
    hearing_held = models.BooleanField(default=False)
    hearing_time = models.DateTimeField(null=True, blank=True)

    # Decision
    decision = models.CharField(max_length=30, choices=DECISION_CHOICES, default='PENDING', db_index=True)
    decision_time = models.DateTimeField(null=True, blank=True)
    decision_document_url = models.URLField(null=True, blank=True)
    reasoning = models.TextField(null=True, blank=True)

    # Appeal
    appeal_status = models.CharField(max_length=30, choices=APPEAL_STATUS_CHOICES, default='NOT_APPEALED')
    appeal_submitted_at = models.DateTimeField(null=True, blank=True)
    appeal_decided_at = models.DateTimeField(null=True, blank=True)
    appeal_reasoning = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'steward_investigations'
        ordering = ['-opened_at']
        indexes = [
            models.Index(fields=['investigation_number']),
            models.Index(fields=['decision']),
            models.Index(fields=['opened_at']),
        ]

    def __str__(self):
        return f"{self.investigation_number} - {self.get_decision_display()}"


class Penalty(models.Model):
    """
    Penalties issued to drivers or teams - tracks all penalties with enforcement details.
    """
    PENALTY_TYPE_CHOICES = [
        ('REPRIMAND', 'Reprimand'),
        ('WARNING', 'Warning'),
        ('FINE', 'Fine'),
        ('TIME_5S', '5 Second Time Penalty'),
        ('TIME_10S', '10 Second Time Penalty'),
        ('TIME_30S', '30 Second Time Penalty'),
        ('GRID_3', '3 Place Grid Penalty'),
        ('GRID_5', '5 Place Grid Penalty'),
        ('GRID_10', '10 Place Grid Penalty'),
        ('GRID_BACK', 'Back of Grid'),
        ('GRID_PIT_LANE', 'Pit Lane Start'),
        ('DRIVE_THROUGH', 'Drive-Through Penalty'),
        ('STOP_GO_10S', '10s Stop-Go Penalty'),
        ('POINTS_DEDUCTION', 'Championship Points Deduction'),
        ('LICENSE_POINTS', 'License Points'),
        ('DISQUALIFICATION', 'Disqualification'),
        ('RACE_BAN', 'Race Ban'),
    ]

    PENALTY_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SERVED', 'Served'),
        ('APPLIED', 'Applied'),
        ('CARRIED_OVER', 'Carried Over'),
        ('SUSPENDED', 'Suspended'),
        ('RESCINDED', 'Rescinded'),
    ]

    id = models.CharField(max_length=25, primary_key=True, default=generate_id, editable=False)
    investigation = models.ForeignKey(
        StewardInvestigation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='penalties'
    )
    incident = models.ForeignKey(
        Incident,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='penalties'
    )
    session = models.ForeignKey(
        'racing.Session',
        on_delete=models.CASCADE,
        related_name='penalties'
    )

    # Penalized party
    driver = models.ForeignKey(
        'teams.Driver',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='penalties'
    )
    team = models.ForeignKey(
        'teams.Team',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='penalties'
    )

    # Penalty details
    penalty_type = models.CharField(max_length=30, choices=PENALTY_TYPE_CHOICES, db_index=True)
    penalty_value = models.IntegerField(null=True, blank=True)  # seconds, positions, points, etc.
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # in EUR
    license_points = models.IntegerField(null=True, blank=True)

    # Timing
    issued_at = models.DateTimeField()
    served_at = models.DateTimeField(null=True, blank=True)
    applied_to_race = models.ForeignKey(
        'racing.Race',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='penalties_applied'
    )

    # Status
    status = models.CharField(max_length=20, choices=PENALTY_STATUS_CHOICES, default='PENDING', db_index=True)

    # Description
    infringement = models.TextField()
    reason = models.TextField(null=True, blank=True)
    document_url = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'penalties'
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['driver', 'issued_at']),
            models.Index(fields=['team', 'issued_at']),
            models.Index(fields=['penalty_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        target = self.driver.code if self.driver else self.team.base_name
        return f"{target} - {self.get_penalty_type_display()} ({self.session.session_name})"

from django.test import TestCase
from apps.teams.models import Driver, Team
from apps.brands.models import Manufacturer
from datetime import date

class TeamModelTest(TestCase):
    """Test suite for the Team model."""

    def setUp(self):
        self.team = Team.objects.create(
            code="FER",
            base_name="Scuderia Ferrari",
            country="Italy",
            founded_year=1929
        )

    def test_team_creation(self):
        """Test if team is created correctly with default values."""
        self.assertEqual(self.team.code, "FER")
        self.assertEqual(str(self.team), "Scuderia Ferrari")
        self.assertTrue(self.team.is_active)

class DriverModelTest(TestCase):
    """Test suite for the Driver model."""

    def setUp(self):
        self.team = Team.objects.create(
            code="FER",
            base_name="Scuderia Ferrari",
            country="Italy",
            founded_year=1929
        )
        self.driver = Driver.objects.create(
            code="LEC",
            first_name="Charles",
            last_name="Leclerc",
            full_name="Charles Leclerc",
            nationality="Monegasque",
            date_of_birth=date(1997, 10, 16),
            status='ACTIVE'
        )

    def test_driver_creation(self):
        """Test if driver is created correctly."""
        self.assertEqual(self.driver.code, "LEC")
        self.assertEqual(self.driver.full_name, "Charles Leclerc")
        self.assertEqual(str(self.driver), "Charles Leclerc")

    def test_driver_active_status(self):
        """Test default active status."""
        self.assertTrue(self.driver.is_active)
        self.assertEqual(self.driver.status, 'ACTIVE')

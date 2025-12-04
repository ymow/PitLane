import os
import sys
import django
from datetime import date, time, datetime

# Add backend to python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from django.utils import timezone
from django.core.files.base import ContentFile
import io
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development') # Or 'production'
django.setup()

from apps.championships.models import Season
from apps.racing.models import Race, Session, RaceResult
from apps.teams.models import Driver, Team
from apps.circuits.models import Circuit
from apps.analysis.fastf1_service import generate_driver_pace_chart # Use the actual service

# --- 1. Create Dummy Data (2025 Qatar) ---
print("Creating dummy data for 2025 F1 Qatar...")

# Create/Get Season 2025
season, created = Season.objects.get_or_create(year=2025, defaults={'name': 'Formula 1 2025 Season'})
print(f"Season 2025 {'created' if created else 'exists'}.")

# Create/Get Circuit Qatar
qatar_circuit, created = Circuit.objects.get_or_create(
    code='losail',
    defaults={
        'name': 'Losail International Circuit',
        'country': 'Qatar',
        'city': 'Lusail',
        'latitude': '25.49000',
        'longitude': '51.45000',
    }
)
print(f"Qatar Circuit {'created' if created else 'exists'}.")

# Create/Get Race (2025 Qatar Grand Prix, Round 1 for simplicity)
qatar_race, created = Race.objects.get_or_create(
    season=season,
    round_number=1, # Assign to round 1 for simplicity
    defaults={
        'circuit': qatar_circuit,
        'official_name': 'Qatar Grand Prix',
        'race_date': date(2025, 3, 2),
        'race_time': time(17, 0, 0),
        'status': 'COMPLETED',
        'openf1_session_key': 9999 # Dummy session key for OpenF1
    }
)
print(f"2025 Qatar Race {'created' if created else 'exists'}.")

# Create/Get Race Session
qatar_session, created = Session.objects.get_or_create(
    race=qatar_race,
    session_type='RACE',
    defaults={
        'session_name': 'Race',
        'scheduled_start': timezone.make_aware(datetime(2025, 3, 2, 17, 0, 0)),
        'status': 'COMPLETED',
        'openf1_session_key': 9999
    }
)
print(f"Race Session {'created' if created else 'exists'}.")

# Create/Get Dummy Drivers and Teams
redbull, _ = Team.objects.get_or_create(code='RBR', defaults={'base_name': 'Red Bull Racing'})
mercedes, _ = Team.objects.get_or_create(code='MER', defaults={'base_name': 'Mercedes-AMG F1'})

max_verstappen, _ = Driver.objects.get_or_create(code='VER', defaults={'first_name': 'Max', 'last_name': 'Verstappen', 'racing_number': 1})
lewis_hamilton, _ = Driver.objects.get_or_create(code='HAM', defaults={'first_name': 'Lewis', 'last_name': 'Hamilton', 'racing_number': 44})

# Create/Get RaceResults
print("Creating RaceResults...")
max_result, _ = RaceResult.objects.get_or_create(
    session=qatar_session,
    driver=max_verstappen,
    defaults={
        'team': redbull,
        'grid_position': 1,
        'finish_position': 1,
        'classified_position': 1,
        'finish_status': 'FINISHED',
        'points': 25,
        'laps_completed': 57
    }
)

lewis_result, _ = RaceResult.objects.get_or_create(
    session=qatar_session,
    driver=lewis_hamilton,
    defaults={
        'team': mercedes,
        'grid_position': 3,
        'finish_position': 2,
        'classified_position': 2,
        'finish_status': 'FINISHED',
        'points': 18,
        'laps_completed': 57
    }
)
print("RaceResults created.")

# --- 2. Simulate FastF1 Chart Generation ---
print("Simulating FastF1 chart generation...")

# Mock FastF1 session data for chart generation
class MockLaps:
    def __init__(self, data_list):
        self._laps_data = []
        for driver, lap_times in data_list.items():
            for i, lt in enumerate(lap_times):
                self._laps_data.append({
                    "LapNumber": i + 1,
                    "LapTime": pd.Timedelta(seconds=lt),
                    "Driver": driver
                })
        self.df = pd.DataFrame(self._laps_data)
        self.columns = self.df.columns # Mock column access

    def pick_driver(self, driver_code):
        return self.df[self.df["Driver"] == driver_code]

class MockFastF1Session:
    def __init__(self):
        self.laps = MockLaps({
            'VER': [95, 94, 93, 94, 95, 96],
            'HAM': [96, 95, 95, 95, 96, 97]
        })
        self.results = pd.DataFrame([{'Abbreviation': 'VER'}]) # Mock results for winner code

    def load(self):
        print("Mock FastF1 session loaded.")

mock_fastf1_session = MockFastF1Session()

# Generate charts for each driver result
for result_obj in [max_result, lewis_result]:
    chart_file = generate_driver_pace_chart(
        session_f1=mock_fastf1_session,
        driver_code=result_obj.driver.code,
        winner_code=max_verstappen.code # Verstappen is our dummy winner
    )
    if chart_file:
        result_obj.telemetry_chart.save(
            f"qatar_2025_{result_obj.driver.code}_pace.png",
            chart_file,
            save=True
        )
        print(f"Chart saved for {result_obj.driver.code}: {result_obj.telemetry_chart.url}")
    else:
        print(f"Failed to generate chart for {result_obj.driver.code}")

print("\n--- Demonstration Complete ---")

# --- 3. Verification ---
print("\n--- Verification of Backend Data ---")
updated_max_result = RaceResult.objects.get(pk=max_result.pk)
updated_lewis_result = RaceResult.objects.get(pk=lewis_result.pk)

print(f"Max Verstappen Telemetry Chart URL: {updated_max_result.telemetry_chart.url if updated_max_result.telemetry_chart else 'N/A'}")
print(f"Lewis Hamilton Telemetry Chart URL: {updated_lewis_result.telemetry_chart.url if updated_lewis_result.telemetry_chart else 'N/A'}")
print(f"Qatar Session OpenF1 Key: {qatar_session.openf1_session_key}")

print("\n--- Expected API Responses ---")
print("1. F1LiveDataAPIView (for 2025 Qatar as next/current race):")
print(f"   - 'next_race.openf1_session_key' would be: {qatar_session.openf1_session_key}")
print(f"   - 'next_race.status' would be: {qatar_session.status}")
print("2. F1RaceResultsAPIView (for 2025 Qatar):")
print(f"   - Each driver's result would include 'telemetry_chart_url' pointing to: {updated_max_result.telemetry_chart.url if updated_max_result.telemetry_chart else 'N/A'} (and similar for Lewis).")
print("3. F1RaceScheduleAPIView (for 2025 Qatar):")
print(f"   - The 'Qatar Grand Prix' entry would include 'openf1_session_key': {qatar_session.openf1_session_key} and 'status': {qatar_session.status}.")

print("\n--- Expected Frontend Behavior ---")
print("1. Dashboard (index/+Page.tsx):")
print("   - If 2025 Qatar were ONGOING, the 'Live Race Session Banner' would show.")
print(f"   - The 'Live Telemetry Widget' would appear, fetching data from OpenF1 using session key {qatar_session.openf1_session_key}.")
print("   - It would display live speed, RPM, gear, throttle for drivers.")
print("2. Race Calendar (races/+Page.tsx):")
print(f"   - The 2025 Qatar Grand Prix entry would show its status as 'Completed'.")
print("   - It would have a button labeled 'View Analysis' (since it's completed and has telemetry_chart_url data from FastF1).")
print("   - Clicking this button would lead to a detail page showing the generated charts.")
print("3. Race Detail Page (if implemented):")
print("   - Would display the 'telemetry_chart_url' generated by FastF1 for each driver.")
print("   - Would have options to view lap times, pit stop data (if populated by FastF1).")

print("\nTo run this demo: Save this script as a .py file (e.g., demo_qatar.py), ensure your Django environment is set up (database running), and execute it with `python demo_qatar.py`.")

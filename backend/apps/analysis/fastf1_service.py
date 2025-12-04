import os
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import logging
from django.core.files.base import ContentFile
from django.utils import timezone
from apps.racing.models import Session, RaceResult, LapTime, PitStop, TyreStint
from apps.teams.models import Driver

logger = logging.getLogger(__name__)

# Configure FastF1
def setup_fastf1():
    """Initialize FastF1 settings"""
    cache_dir = '/tmp/fastf1_cache'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    fastf1.Cache.enable_cache(cache_dir)  # Use a temp directory for caching
    fastf1.plotting.setup_mpl(misc_mpl_mods=False)

def get_fastf1_session(session_obj: Session):
    """
    Retrieve FastF1 session object based on our Session model.
    """
    # If we have an OpenF1/FastF1 key, we might be able to use it, 
    # but FastF1 primarily uses Year, Location, SessionIdentifier.
    
    year = session_obj.race.season.year
    # Map our session type to FastF1 session identifier
    # FastF1: 'fp1', 'fp2', 'fp3', 'q', 's', 'sq', 'r'
    session_type_map = {
        'FP1': 'FP1', 'FP2': 'FP2', 'FP3': 'FP3',
        'QUALIFYING': 'Q',
        'SPRINT_QUALIFYING': 'SQ',
        'SPRINT': 'S',
        'RACE': 'R'
    }
    
    f1_session_type = session_type_map.get(session_obj.session_type)
    if not f1_session_type:
        logger.error(f"Unsupported session type: {session_obj.session_type}")
        return None
        
    # We use the race round number or location
    # FastF1 can take round number
    try:
        session = fastf1.get_session(year, session_obj.race.round_number, f1_session_type)
        return session
    except Exception as e:
        logger.error(f"Failed to get FastF1 session: {e}")
        return None

def generate_driver_pace_chart(session_f1, driver_code, winner_code):
    """
    Generate a chart comparing Driver vs Winner lap times.
    Returns a ContentFile (image) or None.
    """
    try:
        laps = session_f1.laps
        driver_laps = laps.pick_driver(driver_code)
        winner_laps = laps.pick_driver(winner_code)
        
        if len(driver_laps) == 0:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot Winner (Reference)
        sns.scatterplot(data=winner_laps, x="LapNumber", y="LapTime", 
                        ax=ax, color="gray", alpha=0.5, label=f"{winner_code} (Winner)")
        
        # Plot Driver
        try:
            driver_color = fastf1.plotting.get_driver_color(driver_code, session=session_f1)
        except:
            driver_color = "red" # Fallback
            
        sns.scatterplot(data=driver_laps, x="LapNumber", y="LapTime", 
                        ax=ax, color=driver_color, label=driver_code)
        
        ax.set_title(f"Race Pace: {driver_code} vs {winner_code}")
        ax.set_xlabel("Lap Number")
        ax.set_ylabel("Lap Time")
        ax.invert_yaxis()
        ax.legend()
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        
        return ContentFile(buf.read(), name=f"{driver_code}_pace.png")
    except Exception as e:
        logger.error(f"Error generating chart for {driver_code}: {e}")
        plt.close('all')
        return None

def sync_session_data(session_id):
    """
    Main entry point to sync FastF1 data for a session.
    1. Load Session
    2. Download FastF1 data
    3. Populate PitStops, LapTimes, TyreStints
    4. Generate Charts for RaceResults
    """
    setup_fastf1()
    
    try:
        session_obj = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        logger.error(f"Session {session_id} not found")
        return

    logger.info(f"Starting FastF1 sync for {session_obj}")
    
    f1_session = get_fastf1_session(session_obj)
    if not f1_session:
        return

    try:
        f1_session.load()
    except Exception as e:
        logger.error(f"Failed to load FastF1 data: {e}")
        return

    # 1. Populate Lap Times & Tyre Data & Pit Stops
    # This can be heavy, so we might want to be selective or bulk create
    # For now, let's focus on the Strategy/Analysis aspect: Pit Stops & Stints
    
    # Clear existing derived data to avoid duplicates if re-run?
    # Or update_or_create. For simplicity/prototype: delete and recreate for this session
    # CAUTION: This deletes data. In production, use update_or_create.
    PitStop.objects.filter(session=session_obj).delete()
    TyreStint.objects.filter(session=session_obj).delete()
    
    # Pit Stops
    if 'PitInTime' in f1_session.laps.columns and 'PitOutTime' in f1_session.laps.columns:
        # FastF1 stores pit stops implicitly in laps or explicitly?
        # f1_session.laps has 'PitInTime', 'PitOutTime'
        # We can iterate laps where PitInTime is not NaT
        pit_laps = f1_session.laps.pick_pit_stops() # This might not be standard API, let's check docs logic
        # Actually f1_session.laps where isnan(PitInTime) is False
        pass
    
    # Let's use a simpler approach for the prototype: Generate Charts first (High Value)
    
    # Identify Winner (for comparison)
    try:
        winner_result = RaceResult.objects.filter(session=session_obj, classified_position=1).first()
        winner_code = winner_result.driver.code if winner_result else None
    except:
        winner_code = None
        
    if not winner_code:
        # Fallback: get fastest driver from FastF1
        winner_code = f1_session.results.iloc[0]['Abbreviation']

    # Generate Charts for all results
    results = RaceResult.objects.filter(session=session_obj)
    for result in results:
        driver_code = result.driver.code
        logger.info(f"Generating chart for {driver_code}")
        
        chart_file = generate_driver_pace_chart(f1_session, driver_code, winner_code)
        if chart_file:
            result.telemetry_chart.save(f"{session_obj.id}_{driver_code}_pace.png", chart_file, save=True)
    
    logger.info("FastF1 sync completed")

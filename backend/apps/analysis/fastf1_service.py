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
        except Exception:
            driver_color = "red"  # Fallback
            
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
    
    # Pit Stops & Tyre Stints
    if 'PitInTime' in f1_session.laps.columns and 'PitOutTime' in f1_session.laps.columns:
        try:
            pit_laps = f1_session.laps[f1_session.laps['PitInTime'].notna()]
            stop_counters = {}  # driver_code -> stop number

            pit_stops_to_create = []
            for _, lap in pit_laps.iterrows():
                driver_code = lap.get('Driver')
                if not driver_code:
                    continue
                try:
                    driver_obj = Driver.objects.get(code=driver_code)
                except Driver.DoesNotExist:
                    continue

                stop_counters[driver_code] = stop_counters.get(driver_code, 0) + 1
                pit_in = lap['PitInTime']
                pit_out = lap['PitOutTime']

                # Duration in ms
                duration_ms = 0
                if pd.notna(pit_in) and pd.notna(pit_out):
                    duration_ms = int((pit_out - pit_in).total_seconds() * 1000)
                duration_str = f"{duration_ms / 1000:.1f}s"

                pit_stops_to_create.append(PitStop(
                    session=session_obj,
                    driver=driver_obj,
                    lap_number=int(lap.get('LapNumber', 0)),
                    pit_time=session_obj.scheduled_start,  # approximate
                    pit_duration=duration_str,
                    pit_duration_ms=duration_ms,
                    stop_number=stop_counters[driver_code],
                    tire_removed=str(lap.get('Compound', '')),
                    tire_age_removed=int(lap['TyreLife']) if pd.notna(lap.get('TyreLife')) else None,
                ))

            PitStop.objects.bulk_create(pit_stops_to_create, ignore_conflicts=True)
            logger.info(f"Synced {len(pit_stops_to_create)} pit stops")

        except Exception as e:
            logger.error(f"Failed to sync pit stops: {e}")

    # Tyre Stints
    if 'Stint' in f1_session.laps.columns and 'Compound' in f1_session.laps.columns:
        try:
            stint_groups = f1_session.laps.groupby(['Driver', 'Stint'])
            stints_to_create = []
            for (driver_code, stint_num), stint_laps in stint_groups:
                try:
                    driver_obj = Driver.objects.get(code=driver_code)
                except Driver.DoesNotExist:
                    continue

                compound = str(stint_laps['Compound'].iloc[0]) if 'Compound' in stint_laps.columns else 'UNKNOWN'
                start_lap = int(stint_laps['LapNumber'].min())
                end_lap = int(stint_laps['LapNumber'].max())
                tyre_age = int(stint_laps['TyreLife'].iloc[0]) if pd.notna(stint_laps.get('TyreLife', pd.Series([None])).iloc[0]) else 0

                stints_to_create.append(TyreStint(
                    session=session_obj,
                    driver=driver_obj,
                    stint_number=int(stint_num),
                    compound=compound.upper()[:20],
                    tire_age_at_start=tyre_age,
                    start_lap=start_lap,
                    end_lap=end_lap,
                    total_laps=end_lap - start_lap + 1,
                ))

            TyreStint.objects.bulk_create(stints_to_create, ignore_conflicts=True)
            logger.info(f"Synced {len(stints_to_create)} tyre stints")

        except Exception as e:
            logger.error(f"Failed to sync tyre stints: {e}")

    # Generate Charts (High Value)
    
    # Identify Winner (for comparison)
    try:
        winner_result = RaceResult.objects.filter(session=session_obj, classified_position=1).first()
        winner_code = winner_result.driver.code if winner_result else None
    except Exception as e:
        logger.warning(f"Could not determine winner from DB: {e}")
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

import fastf1
import fastf1.plotting
from matplotlib import pyplot as plt
import os

# Enable FastF1 color scheme
fastf1.plotting.setup_mpl()

def generate_pace_chart(year, event, session_type):
    print(f"Loading data for {year} {event} {session_type}...")
    
    # Load the session
    session = fastf1.get_session(year, event, session_type)
    session.load()

    # Get laps for top 3 finishers
    # (In a real scenario, we'd loop through all drivers or key rivals)
    drivers = session.results['Abbreviation'].iloc[:3].tolist()
    
    fig, ax = plt.subplots(figsize=(10, 6))

    for abr in drivers:
        laps = session.laps.pick_driver(abr).pick_quicklaps()
        # Convert to seconds
        lap_times = laps['LapTime'].dt.total_seconds()
        
        ax.plot(laps['LapNumber'], lap_times, label=abr)

    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Lap Time (s)')
    ax.set_title(f'Pace Comparison: {year} {event}')
    ax.legend()
    
    output_path = 'backend/media/telemetry_charts/demo_pace.png'
    plt.savefig(output_path)
    print(f"SUCCESS: Chart saved to {output_path}")
    return output_path

if __name__ == "__main__":
    try:
        # Testing with 2024 Bahrain GP which is guaranteed to have data
        generate_pace_chart(2024, 'Bahrain', 'R')
    except Exception as e:
        print(f"Error: {e}")

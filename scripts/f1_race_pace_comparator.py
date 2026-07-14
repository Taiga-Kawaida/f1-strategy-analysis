import logging
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import fastf1
import fastf1.plotting

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

cache_dir = Path('cache')
cache_dir.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(cache_dir))

fastf1.plotting.setup_mpl(misc_mpl_mods=False)
plt.style.use('default')

def export_race_pace(
    year: int, 
    location: str, 
    driver1: str, 
    driver2: str, 
    output_dir: str = 'output',
    use_quicklaps: bool = True
) -> None:
    logger.info(f"Processing Race Pace: {year} {location} {driver1} vs {driver2}")
    
    try:
        session = fastf1.get_session(year, location, 'R')
        session.load(telemetry=False, weather=False, messages=False)

        laps_d1 = session.laps.pick_drivers(driver1)
        laps_d2 = session.laps.pick_drivers(driver2)

        if use_quicklaps:
            laps_d1 = laps_d1.pick_quicklaps()
            laps_d2 = laps_d2.pick_quicklaps()
        else:
            laps_d1 = laps_d1.pick_accurate()
            laps_d2 = laps_d2.pick_accurate()

        color1 = fastf1.plotting.get_driver_color(driver1, session=session)
        color2 = fastf1.plotting.get_driver_color(driver2, session=session)

        fig, ax = plt.subplots(figsize=(12, 6))

        clean_d1 = laps_d1.dropna(subset=['LapNumber', 'LapTime'])
        x1 = clean_d1['LapNumber']
        y1 = clean_d1['LapTime'].dt.total_seconds()
        
        ax.plot(x1, y1, marker='o', linestyle='none', color=color1, label=driver1, alpha=0.7)
        z1 = np.polyfit(x1, y1, 2)
        p1 = np.poly1d(z1)
        ax.plot(x1, p1(x1), linestyle='-', color=color1, linewidth=2)

        clean_d2 = laps_d2.dropna(subset=['LapNumber', 'LapTime'])
        x2 = clean_d2['LapNumber']
        y2 = clean_d2['LapTime'].dt.total_seconds()
        
        ax.plot(x2, y2, marker='o', linestyle='none', color=color2, label=driver2, alpha=0.7)
        z2 = np.polyfit(x2, y2, 2)
        p2 = np.poly1d(z2)
        ax.plot(x2, p2(x2), linestyle='-', color=color2, linewidth=2)

        ax.set_xlabel('Lap Number')
        ax.set_ylabel('Lap Time (Seconds)')
        ax.set_title(f"{year} {location} GP - Race Pace Comparison: {driver1} vs {driver2}")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"{year}_{location.replace(' ', '_')}_RacePace_{driver1}_{driver2}.png"
        save_path = out_path / filename
        
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        logger.info(f"Successfully saved Race Pace graph to: {save_path}")
        plt.close(fig)

    except Exception as e:
        logger.error(f"Failed to process race pace. Error: {e}", exc_info=True)

if __name__ == "__main__":
    export_race_pace(2025, 'Silverstone', 'VER', 'NOR')
    export_race_pace(2025, 'Silverstone', 'VER', 'NOR', use_quicklaps=False)
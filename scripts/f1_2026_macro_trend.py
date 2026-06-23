import logging
from pathlib import Path
import matplotlib.pyplot as plt
import fastf1
import fastf1.plotting
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

THROTTLE_THRESHOLD = 2.0

cache_dir = Path('cache')
cache_dir.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(cache_dir))

plt.style.use('default')


def detect_lift_and_coast(telemetry: pd.DataFrame) -> pd.DataFrame:
    brake_off = (telemetry['Brake'] == 0) | (telemetry['Brake'] == False)
    throttle_off = telemetry['Throttle'] < THROTTLE_THRESHOLD
    
    telemetry['LiftAndCoast'] = throttle_off & brake_off
    return telemetry


def export_macro_trend(
    year: int,
    location: str,
    session_type: str,
    driver1: str,
    driver2: str,
    start_lap: int = 2,
    end_lap: int = 20,
    output_dir: str = 'output'
) -> None:
    logger.info(f"Processing Macro Trend: {year} {location} [{session_type}] {driver1} vs {driver2}")
    
    try:
        session = fastf1.get_session(year, location, session_type)
        session.load(telemetry=True, weather=False, messages=False)

        d1_laps = session.laps.pick_drivers(driver1)
        d2_laps = session.laps.pick_drivers(driver2)

        laps_range = list(range(start_lap, end_lap + 1))
        d1_ratios = []
        d2_ratios = []

        for lap_num in laps_range:
            try:
                d1_lap = d1_laps[d1_laps['LapNumber'] == lap_num].iloc[0]
                d2_lap = d2_laps[d2_laps['LapNumber'] == lap_num].iloc[0]

                d1_tel = d1_lap.get_telemetry().add_distance()
                d2_tel = d2_lap.get_telemetry().add_distance()

                d1_tel = detect_lift_and_coast(d1_tel)
                d2_tel = detect_lift_and_coast(d2_tel)

                d1_tel['DeltaDistance'] = d1_tel['Distance'].diff().fillna(0)
                d2_tel['DeltaDistance'] = d2_tel['Distance'].diff().fillna(0)

                d1_lc_dist = d1_tel.loc[d1_tel['LiftAndCoast'], 'DeltaDistance'].sum()
                d2_lc_dist = d2_tel.loc[d2_tel['LiftAndCoast'], 'DeltaDistance'].sum()

                d1_total_dist = d1_tel['Distance'].iloc[-1]
                d2_total_dist = d2_tel['Distance'].iloc[-1]

                d1_ratios.append((d1_lc_dist / d1_total_dist) * 100)
                d2_ratios.append((d2_lc_dist / d2_total_dist) * 100)
            
            except Exception as e:
                logger.warning(f"Skipping Lap {lap_num}: {e}")
                d1_ratios.append(None)
                d2_ratios.append(None)

        fig, ax = plt.subplots(figsize=(12, 6))
        
        color1 = fastf1.plotting.get_driver_color(driver1, session=session)
        color2 = fastf1.plotting.get_driver_color(driver2, session=session)

        ax.plot(laps_range, d1_ratios, marker='o', linewidth=2, color=color1, label=driver1)
        ax.plot(laps_range, d2_ratios, marker='o', linewidth=2, color=color2, label=driver2)

        ax.set_title(f"Lift & Coast Ratio Trend (Lap {start_lap}-{end_lap}) - {year} {location} {session_type} - {driver1} vs {driver2}")
        ax.set_xlabel("Lap Number")
        ax.set_ylabel("Lift & Coast Ratio (%)")
        ax.set_xticks(laps_range)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        filename = f"{year}_{location.replace(' ', '_')}_{session_type}_macro_trend_{driver1}_{driver2}.png"
        save_path = out_path / filename
        
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        logger.info(f"Successfully saved Macro Trend graph to: {save_path}")
        plt.close(fig)

    except Exception as e:
        logger.error(f"Failed to process macro trend. Error: {e}", exc_info=True)


if __name__ == "__main__":
    export_macro_trend(2025, 'Suzuka', 'R', 'VER', 'NOR', start_lap=2, end_lap=20)
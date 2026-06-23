import logging
from pathlib import Path
import matplotlib.pyplot as plt
import fastf1
import fastf1.plotting
import pandas as pd

logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

THROTTLE_THRESHOLD = 2.0

cache_dir = Path('cache')
cache_dir.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(cache_dir))

plt.style.use('default')


def detect_lift_and_coast(telemetry: pd.DataFrame) -> pd.DataFrame:
    """
    Detects Lift & Coast phases based on telemetry thresholds and 
    appends a boolean flag to the DataFrame.
    """
    brake_off = (telemetry['Brake'] == 0) | (telemetry['Brake'] == False)
    throttle_off = telemetry['Throttle'] < THROTTLE_THRESHOLD
    
    telemetry['LiftAndCoast'] = throttle_off & brake_off
    return telemetry


def export_energy_management_poc(
    year: int,
    location: str,
    session_type: str,
    driver1: str,
    driver2: str,
    output_dir: str = 'output'
) -> None:
    """
    Exports a telemetry comparison graph highlighting Lift & Coast zones 
    to demonstrate energy management strategies (PoC for 2026 EV regulations).
    """
    logger.info(f"Processing PoC (Energy Management): {year} {location} [{session_type}] {driver1} vs {driver2}")
    
    try:
        session = fastf1.get_session(year, location, session_type)
        session.load(telemetry=True, weather=False, messages=False)
        
        target_lap = 15

        d1_laps = session.laps.pick_drivers(driver1)
        d2_laps = session.laps.pick_drivers(driver2)

        d1_lap = d1_laps[d1_laps['LapNumber'] == target_lap].iloc[0]
        d2_lap = d2_laps[d2_laps['LapNumber'] == target_lap].iloc[0]

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
        d1_lc_ratio = (d1_lc_dist / d1_total_dist) * 100
        d2_lc_ratio = (d2_lc_dist / d2_total_dist) * 100

        logger.info(f"--- Lap {target_lap} Energy Management Metrics ---")
        logger.info(f"[{driver1}] L&C Distance: {d1_lc_dist:.1f}m ({d1_lc_ratio:.2f}%)")
        logger.info(f"[{driver2}] L&C Distance: {d2_lc_dist:.1f}m ({d2_lc_ratio:.2f}%)")
        logger.info(f"---------------------------------------------")

        fig, axes = plt.subplots(4, 1, figsize=(15, 12), gridspec_kw={'height_ratios': [3, 1, 1, 1.5]}, sharex=True)
        plt.subplots_adjust(hspace=0.1)

        color1 = fastf1.plotting.get_driver_color(driver1, session=session)
        color2 = fastf1.plotting.get_driver_color(driver2, session=session)

        axes[0].plot(d1_tel['Distance'], d1_tel['Speed'], color=color1, label=driver1)
        axes[0].plot(d2_tel['Distance'], d2_tel['Speed'], color=color2, label=driver2)
        axes[0].set_ylabel('Speed\n(km/h)')
        axes[0].legend(loc='lower right')
        axes[0].set_title(f"Energy Management PoC (Lift & Coast) - {year} {location} {session_type} - {driver1} vs {driver2}")

        axes[1].plot(d1_tel['Distance'], d1_tel['Throttle'], color=color1)
        axes[1].plot(d2_tel['Distance'], d2_tel['Throttle'], color=color2)
        axes[1].set_ylabel('Throttle\n(%)')

        axes[2].plot(d1_tel['Distance'], d1_tel['Brake'], color=color1)
        axes[2].plot(d2_tel['Distance'], d2_tel['Brake'], color=color2)
        axes[2].set_ylabel('Brake')

        # Use fill_between for professional-grade telemetry visualization (highlight bands)
        axes[3].fill_between(
            d1_tel['Distance'], 0, 1, 
            where=d1_tel['LiftAndCoast'], 
            color=color1, alpha=0.5, label=f"{driver1} Coasting",
            transform=axes[3].get_xaxis_transform()
        )
        axes[3].fill_between(
            d2_tel['Distance'], 0, 1, 
            where=d2_tel['LiftAndCoast'], 
            color=color2, alpha=0.5, label=f"{driver2} Coasting",
            transform=axes[3].get_xaxis_transform()
        )
        
        axes[3].set_ylabel('Lift & Coast\nZones')
        axes[3].set_xlabel('Distance (m)')
        axes[3].set_ylim(0, 1)
        axes[3].set_yticks([])
        axes[3].legend(loc='upper right')

        for ax in axes:
            ax.grid(True, which='both', linestyle='--', alpha=0.4)
            ax.yaxis.label.set_rotation(0)
            ax.yaxis.set_label_coords(-0.08, 0.4)

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        filename = f"{year}_{location.replace(' ', '_')}_{session_type}_pattern2_energy_poc_{driver1}_{driver2}.png"
        save_path = out_path / filename
        
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        logger.info(f"Successfully saved PoC graph to: {save_path}")
        plt.close(fig)

    except Exception as e:
        logger.error(f"Failed to process PoC data. Error: {e}", exc_info=True)


if __name__ == "__main__":
    export_energy_management_poc(2025, 'Suzuka', 'R', 'VER', 'NOR')
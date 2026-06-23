import logging
from pathlib import Path
import matplotlib.pyplot as plt
import fastf1
import fastf1.plotting

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

cache_dir = Path('cache')
cache_dir.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(cache_dir))

plt.style.use('default')


def export_aero_telemetry_comparison(
    year: int,
    location: str,
    session_type: str,
    driver1: str,
    driver2: str,
    output_dir: str = 'output'
) -> None:
    """
    Compares the fastest laps of two drivers in a specified session and 
    exports a graph visualizing vehicle dynamics and Active Aero (X-Mode) status.

    Args:
        year (int): Championship year (e.g., 2026).
        location (str): Event location (e.g., 'Miami').
        session_type (str): Session identifier ('Q' for Qualifying, 'R' for Race).
        driver1 (str): 3-letter abbreviation for driver 1 (e.g., 'RUS').
        driver2 (str): 3-letter abbreviation for driver 2 (e.g., 'ANT').
        output_dir (str, optional): Directory to save the output image. Defaults to 'output'.
    """
    logger.info(f"Processing: {year} {location} [{session_type}] {driver1} vs {driver2}")
    
    try:
        session = fastf1.get_session(year, location, session_type)
        session.load(telemetry=True, weather=False, messages=False)

        d1_lap = session.laps.pick_drivers(driver1).pick_fastest()
        d2_lap = session.laps.pick_drivers(driver2).pick_fastest()

        d1_tel = d1_lap.get_telemetry().add_distance()
        d2_tel = d2_lap.get_telemetry().add_distance()

        fig, axes = plt.subplots(
            4, 1, 
            figsize=(15, 10), 
            gridspec_kw={'height_ratios': [3, 1, 1, 1]}, 
            sharex=True
        )
        plt.subplots_adjust(hspace=0.1)

        color1 = fastf1.plotting.get_driver_color(driver1, session=session)
        color2 = fastf1.plotting.get_driver_color(driver2, session=session)

        axes[0].plot(d1_tel['Distance'], d1_tel['Speed'], color=color1, label=driver1)
        axes[0].plot(d2_tel['Distance'], d2_tel['Speed'], color=color2, label=driver2)
        axes[0].set_ylabel('Speed\n(km/h)')
        axes[0].legend(loc='lower right')
        axes[0].set_title(f"{year} {location} {session_type} - {driver1} vs {driver2} (Active Aero Analysis)")

        axes[1].plot(d1_tel['Distance'], d1_tel['Throttle'], color=color1)
        axes[1].plot(d2_tel['Distance'], d2_tel['Throttle'], color=color2)
        axes[1].set_ylabel('Throttle\n(%)')

        axes[2].plot(d1_tel['Distance'], d1_tel['Brake'], color=color1)
        axes[2].plot(d2_tel['Distance'], d2_tel['Brake'], color=color2)
        axes[2].set_ylabel('Brake')

        # Dynamically determine the column name for Active Aero to handle API changes
        available_cols = d1_tel.columns
        aero_column = 'DRS'
        for col in ['ActiveAero', 'XMode', 'DRS']:
            if col in available_cols:
                aero_column = col
                break
        
        axes[3].plot(d1_tel['Distance'], d1_tel[aero_column], color=color1)
        axes[3].plot(d2_tel['Distance'], d2_tel[aero_column], color=color2)
        axes[3].set_ylabel('X-Mode\nStatus')
        axes[3].set_xlabel('Distance (m)')

        for ax in axes:
            ax.grid(True, which='both', linestyle='--', alpha=0.4)
            ax.yaxis.label.set_rotation(0)
            ax.yaxis.set_label_coords(-0.08, 0.4)

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"{year}_{location.replace(' ', '_')}_{session_type}_pattern1_aero_{driver1}_{driver2}.png"
        save_path = out_path / filename
        
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        logger.info(f"Successfully saved graph to: {save_path}")
        plt.close(fig)

    except Exception as e:
        logger.error(f"Failed to process data for {driver1} vs {driver2}. Error: {e}", exc_info=True)


if __name__ == "__main__":
    export_aero_telemetry_comparison(2026, 'Australia', 'Q', 'RUS', 'ANT')
    export_aero_telemetry_comparison(2026, 'Australia', 'R', 'RUS', 'ANT')
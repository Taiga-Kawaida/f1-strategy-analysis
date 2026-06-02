import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import os

fastf1.plotting.setup_mpl(misc_mpl_mods=False)

def export_telemetry_comparison(year, location, session_type, driver1, driver2):
    print(f"--- {year} {location} [{session_type}] {driver1} vs {driver2} processing... ---")
    
    try:
        session = fastf1.get_session(year, location, session_type)
        session.load()

        d1_lap = session.laps.pick_drivers(driver1).pick_fastest()
        d2_lap = session.laps.pick_drivers(driver2).pick_fastest()

        d1_tel = d1_lap.get_telemetry().add_distance()
        d2_tel = d2_lap.get_telemetry().add_distance()

        fig, ax = plt.subplots(5, 1, figsize=(15, 12), gridspec_kw={'height_ratios': [3, 1, 1, 1, 1]})
        plt.subplots_adjust(hspace=0.3)

        color1 = fastf1.plotting.get_driver_color(driver1, session=session)
        color2 = fastf1.plotting.get_driver_color(driver2, session=session)

        ax[0].plot(d1_tel['Distance'], d1_tel['Speed'], color=color1, label=driver1)
        ax[0].plot(d2_tel['Distance'], d2_tel['Speed'], color=color2, label=driver2)
        ax[0].set_ylabel('Speed (km/h)')
        ax[0].legend(loc='upper right')
        ax[0].set_title(f"{year} {location} {session_type} - {driver1} vs {driver2}")

        ax[1].plot(d1_tel['Distance'], d1_tel['Throttle'], color=color1)
        ax[1].plot(d2_tel['Distance'], d2_tel['Throttle'], color=color2)
        ax[1].set_ylabel('Throttle %')

        ax[2].plot(d1_tel['Distance'], d1_tel['Brake'], color=color1)
        ax[2].plot(d2_tel['Distance'], d2_tel['Brake'], color=color2)
        ax[2].set_ylabel('Brake')

        ax[3].plot(d1_tel['Distance'], d1_tel['nGear'], color=color1)
        ax[3].plot(d2_tel['Distance'], d2_tel['nGear'], color=color2)
        ax[3].set_ylabel('Gear')
        ax[3].set_ylim(0.5, 8.5)              
        ax[3].set_yticks(range(1, 9))         

        ax[4].plot(d1_tel['Distance'], d1_tel['DRS'], color=color1)
        ax[4].plot(d2_tel['Distance'], d2_tel['DRS'], color=color2)
        ax[4].set_ylabel('DRS')
        ax[4].set_xlabel('Distance (m)')

        os.makedirs('output', exist_ok=True)
        save_path = f"output/{year}_{location.replace(' ', '_')}_{session_type}_{driver1}_{driver2}.png"
        plt.savefig(save_path)
        print(f"✅ Saved: {save_path}")
        plt.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    export_telemetry_comparison(2025, 'Abu Dhabi', 'Q', 'VER', 'NOR')
    export_telemetry_comparison(2025, 'Abu Dhabi', 'R', 'VER', 'NOR')
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# F1の公式カラーとスタイルを設定
fastf1.plotting.setup_mpl(misc_mpl_mods=False)

def export_race_pace(year, location, driver1, driver2):
    print(f"--- {year} {location} [Race Pace] {driver1} vs {driver2} 分析中... ---")
    
    try:
        # セッションのロード
        session = fastf1.get_session(year, location, 'R')
        session.load()

        # ドライバーのラップデータを取得
        laps_d1 = session.laps.pick_drivers(driver1)
        laps_d2 = session.laps.pick_drivers(driver2)

        # 外れ値（ピットイン、SC、VSCなど極端に遅いラップ）を除外
        # QuickLaps（通常のレーシングスピードのラップ）のみを抽出
        laps_d1 = laps_d1.pick_quicklaps()
        laps_d2 = laps_d2.pick_quicklaps()

        # チームカラーの取得
        color1 = fastf1.plotting.get_driver_color(driver1, session=session)
        color2 = fastf1.plotting.get_driver_color(driver2, session=session)

        # グラフの設定
        fig, ax = plt.subplots(figsize=(12, 6))

        # ドライバー1のプロット
        ax.plot(laps_d1['LapNumber'], laps_d1['LapTime'].dt.total_seconds(), 
                marker='o', linestyle='none', color=color1, label=driver1, alpha=0.7)
        # トレンドライン（多項式近似）
        z1 = np.polyfit(laps_d1['LapNumber'], laps_d1['LapTime'].dt.total_seconds(), 2)
        p1 = np.poly1d(z1)
        ax.plot(laps_d1['LapNumber'], p1(laps_d1['LapNumber']), linestyle='-', color=color1, linewidth=2)

        # ドライバー2のプロット
        ax.plot(laps_d2['LapNumber'], laps_d2['LapTime'].dt.total_seconds(), 
                marker='o', linestyle='none', color=color2, label=driver2, alpha=0.7)
        # トレンドライン（多項式近似）
        z2 = np.polyfit(laps_d2['LapNumber'], laps_d2['LapTime'].dt.total_seconds(), 2)
        p2 = np.poly1d(z2)
        ax.plot(laps_d2['LapNumber'], p2(laps_d2['LapNumber']), linestyle='-', color=color2, linewidth=2)

        # グラフの装飾
        ax.set_xlabel('Lap Number')
        ax.set_ylabel('Lap Time (Seconds)')
        ax.set_title(f"{year} {location} GP - Race Pace Comparison: {driver1} vs {driver2}")
        ax.legend()
        plt.grid(True, linestyle='--', alpha=0.5)

        # 保存処理
        os.makedirs('output', exist_ok=True)
        save_path = f"output/{year}_{location}_RacePace_{driver1}_{driver2}.png"
        plt.savefig(save_path)
        print(f"✅ 画像を保存しました: {save_path}")
        plt.close()

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    export_race_pace(2025, 'Monaco', 'VER', 'NOR')
    export_race_pace(2025, 'Suzuka', 'VER', 'NOR')
    export_race_pace(2025, 'Abu Dhabi', 'VER', 'NOR')